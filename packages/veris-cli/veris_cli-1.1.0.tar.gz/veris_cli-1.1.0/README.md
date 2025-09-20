# veris-cli

[![PyPI version](https://badge.fury.io/py/veris-cli.svg)](https://badge.fury.io/py/veris-cli)
[![Tests](https://github.com/veris-ai/veris-cli/actions/workflows/test.yml/badge.svg)](https://github.com/veris-ai/veris-cli/actions/workflows/test.yml)
[![Python](https://img.shields.io/pypi/pyversions/veris-cli.svg)](https://pypi.org/project/veris-cli/)

Veris CLI connects a local agent to the Veris simulation backend so you can generate scenarios and run end-to-end evaluations.

## Quickstart

This quickstart walks through running Veris simulations against the example app in [mini_crm](https://github.com/veris-ai/mini_crm) using the [OpenAI agents](https://openai.github.io/openai-agents-python/) framework.

### Before you start

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed
- Ngrok account (the CLI opens a tunnel for the agent server)

### Step 1. Create and activate a virtual environment (recommended)

```bash
uv venv .venv
source .venv/bin/activate
```
### Step 2. Install the Veris CLI

```bash
uv pip install veris-cli
# or, if you prefer uv tool, pin it to the active interpreter
uv tool install --python "$(which python)" veris-cli
veris --help
```

### Step 3. Clone the demo agent and set up dependencies

```bash
git clone https://github.com/veris-ai/mini_crm.git
cd mini_crm
uv pip install -r requirements.txt
```

### Step 4. Configure API keys

Create a `.env` file with all required keys:

```bash
# Create .env file with your API keys
echo 'OPENAI_API_KEY=<your-openai-key>' >> .env
echo 'VERIS_API_KEY=<your-veris-api-key>' >> .env
echo 'ENV=simulation' >> .env
```

**Note:**
- Get your Veris API key from https://simulator.veris.ai/ (requires account)
- The CLI automatically loads `.env` files from the current directory

### Step 5. Initialize Veris project files

```bash
veris init
```

### Step 6. Start the Mini CRM app with an ngrok tunnel

```bash
veris setup --app app.main:app --port 8000 --reload
```

Leave this terminal running; note the public URL the command prints (it is also stored in `.veris/config.json`).

### Step 7. Generate scenarios (new terminal)

```bash
veris scenario generate \
  --agent .veris/agent.json \
  --model gpt-4o-2024-08-06 \
  --variations-per-skeleton 2 \
  --random-subset 2 \
  --watch --save
```

### Step 8. Launch a simulation run (same terminal as Step 7)

```bash
veris sim launch --watch
```

For alternative installers, manual ngrok setup, and other edge cases, see [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md).

### Step 9. View simulation results

```bash
veris sim results --run <run_id>
```

## Using with your own agent

The quickstart above uses the pre-configured Mini CRM demo. To connect the CLI to your own agent:

### Prerequisites for custom agents

- **FastAPI application** with HTTP endpoints
- **MCP (Model Context Protocol) integration** for tool simulation
- **Environment variable loading** (e.g., `python-dotenv` for `.env` files)
- **Veris SDK integration** for telemetry and mocking

### Step-by-step setup

1. **Install the Veris CLI** (same as quickstart Steps 1-2)
   ```bash
   uv venv .venv && source .venv/bin/activate
   uv pip install veris-cli
   ```

2. **Navigate to your agent project** and install Veris SDK
   ```bash
   cd /path/to/your-agent
   uv pip install veris-ai python-dotenv
   ```

3. **Add MCP integration to your FastAPI app**
   ```python
   from fastapi import FastAPI
   from veris_ai import veris

   app = FastAPI(title="Your Agent")

   # Your existing routes and business logic
   @app.post("/chat")
   async def chat(request: ChatRequest):
       # Your agent implementation
       pass

   # Enable MCP integration
   veris.set_fastapi_mcp(fastapi=app)
   veris.fastapi_mcp.mount_http()
   ```

4. **Instrument your tools for simulation**

   Choose one approach:

   **Option A - Decorators:**
   ```python
   from veris_ai.tool_mock import veris

   @veris.mock(mode="tool", expects_response=False)
   def your_tool_function(param: str) -> dict:
       # Your tool implementation
       pass
   ```

   **Option B - Runner integration:**
   ```python
   from veris_ai import Runner, VerisConfig
   from veris_ai.models import ToolCallOptions

   result = await Runner.run(
       agent,
       message,
       context=context,
       veris_config=VerisConfig(
           tool_options={
               "your_tool_name": ToolCallOptions(response_expectation="none"),
           }
       ),
   )
   ```

5. **Configure environment variables**
   ```bash
   echo 'OPENAI_API_KEY=<your-key>' >> .env
   echo 'VERIS_API_KEY=<your-veris-key>' >> .env
   echo 'ENV=simulation' >> .env
   # Add any other keys your agent needs
   ```

6. **Initialize Veris in your project**
   ```bash
   veris init
   ```

   Edit `.veris/agent.json` to match your agent:
   ```json
   {
     "agent_id": "your-agent-id",
     "name": "Your Agent Name",
     "description": "Description of what your agent does"
   }
   ```

7. **Start your agent with ngrok tunnel**
   ```bash
   veris setup --app your_app.main:app --port 8000 --reload
   ```

8. **Generate scenarios and run simulations**
   ```bash
   # Generate scenarios specific to your agent's capabilities
   veris scenario generate \
     --agent .veris/agent.json \
     --model gpt-4o-2024-08-06 \
     --variations-per-skeleton 2 \
     --random-subset 2 \
     --watch --save

   # Launch simulations
   veris sim launch --watch
   ```

### Key considerations

- **Tool simulation**: Ensure your agent's tools are properly instrumented with Veris SDK so they can be mocked during simulations
- **Environment isolation**: The `ENV=simulation` variable helps your agent detect when it's running in simulation mode
- **MCP compatibility**: Your agent must expose MCP endpoints for the simulator to interact with your tools
- **Error handling**: Make sure your agent gracefully handles simulation-specific requests and responses

For detailed integration examples, see the [Veris Python SDK documentation](https://github.com/veris-ai/veris-python-sdk).

## Installation reference

A reminder of the available installer commands. Details and fallback paths live in [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md#cli-or-dependencies-fail-to-install).

### Install or upgrade

```bash
# Install into the active environment
uv pip install veris-cli

# Or manage a global tool installation
uv tool install veris-cli
uv tool upgrade veris-cli
```

### Install from source (latest main)

```bash
uv tool install 'git+https://github.com/veris-ai/veris-cli.git'
```

### Uninstall

```bash
uv tool uninstall veris-cli
```

## Environment Configuration

The Veris CLI requires certain environment variables to function properly. The CLI automatically loads these from `.env` files, making configuration simple and consistent.

### Automatic .env Loading

The CLI automatically searches for and loads `.env` files in the following order:
1. Current working directory (`./.env`)
2. Parent directories (up to 3 levels up)
3. Default dotenv locations

**Important:** Environment variables set in your shell always take precedence over values in `.env` files.

### Required Environment Variables

- **`VERIS_API_KEY`** (required): Your API key from https://simulator.veris.ai/
- **`ENV`** (recommended): Set to `simulation` for simulation mode
- **`OPENAI_API_KEY`** (if using OpenAI agents): Your OpenAI API key
- **`VERIS_API_URL`** (optional): Override the default API endpoint

### Example .env File

```bash
# Create a .env file in your project root
cat > .env << 'EOF'
VERIS_API_KEY=your-veris-api-key-here
ENV=simulation
OPENAI_API_KEY=your-openai-key-here
EOF
```

### Troubleshooting Environment Issues

If you encounter authentication errors (401 Unauthorized):

1. **Verify your .env file exists and contains the key:**
   ```bash
   cat .env | grep VERIS_API_KEY
   ```

2. **Check if the variable is loaded in your environment:**
   ```bash
   echo $VERIS_API_KEY
   ```

3. **If the variable is not set, manually load the .env file:**
   ```bash
   source .env
   # or
   export $(cat .env | xargs)
   ```

4. **Ensure the API key is not empty or contains only whitespace**

The CLI will provide clear error messages if the `VERIS_API_KEY` is missing or invalid, helping you quickly identify configuration issues.

## Commands

### Veris initialization

```
veris init
```

Creates the following structure:

```
.veris/
  agent.json
  scenarios/
    example-scenario.json
  runs/
```

Agent spec and scenarios are JSON, validated against local Pydantic models.

### Veris setup

Run your local FastAPI app with uvicorn and expose it via an ngrok tunnel. On success, the discovered public URL is written to `.veris/config.json` (unless disabled), so the simulator knows how to reach your agent.

Prerequisites:
- ngrok installed and authenticated (`ngrok config add-authtoken <token>`). To verify, run `ngrok config check`.
- `uvicorn` available in the same environment as your FastAPI app.

Basic usage:
```
veris setup --app app.main:app --port 8000 [--reload]
```

What it does:
- Verifies the chosen TCP port is available.
- Ensures `ngrok` and `uvicorn` are installed.
- Starts your app via `uvicorn` and waits until it responds.
- Starts an `ngrok` tunnel and fetches the public URL (prefers https).
- Prints the public URL and `${public_url}/docs`.
- Updates `.veris/config.json` with the agent connection, including `mcp_url` derived from the tunnel URL.

Common options:
- `--app`: ASGI import path, e.g. `app.main:app` (required)
- `--port`: Local port (default: 8000)
- `--host`: Bind host (default: 127.0.0.1)
- `--reload`: Enable auto-reload (dev only)
- `--workers N`: Number of worker processes
- `-d`, `--detached`: Run in background and persist PIDs to `.veris/setup_state.json`
- `--no_override_public_url`: Do not update `.veris/config.json` with the discovered public URL

Logs and state:
- Logs live under `.veris/logs/`: `uvicorn.log` and `ngrok.log` (always prints the ngrok log path; uvicorn logs are captured in detached mode).
- Detached runs persist process IDs and metadata in `.veris/setup_state.json`.

Stopping the services:
- Foreground mode: press Ctrl+C to stop both uvicorn and ngrok gracefully.
- Detached mode: use the companion command:
```
veris setup stop
```
This reads `.veris/setup_state.json` and terminates the background uvicorn and ngrok processes.

Examples:
```bash
# Foreground run (Ctrl+C to stop)
veris setup --app app.main:app --port 8000 --reload

# Detached run and stop later
veris setup --app app.main:app --port 8000 -d
veris setup stop
```

### Launch simulations from `.veris/`

```
veris sim launch [--scenarios <id> ...] [--use-cases <name> ...] [--watch]
```

- `--watch` (optional) watches the status of the simulations and evaluations and updates the status in real-time untill all simulations are finished.
- Press Ctrl+C to stop watching; the command also auto-exits when all simulations and evaluations complete.

### Check simulation status (single poll)

```
veris sim status --run <run_id>
```

### Stop a simulation or evaluation

```
veris sim kill <simulation_id>
veris sim eval-kill <eval_id>
```

Core flow mirrors the web demo launcher and monitor.

### Show evaluation results

```
veris sim results --run <run_id> [--json] [--export <path>]
```

- Requires the run to be complete (all simulations evaluated). If not complete, the command exits with a helpful message; run `veris sim status --run <id>` until done.
- Default output is a simple table summarizing per-scenario and overall averages (`--table` is on by default).
- When `--json` is provided, emits a machine-readable summary; `--export` writes the same JSON to a file.

### Start scenario generation

```
veris scenario generate \
  [--agent .veris/agent.json] \
  [--config generator_config.json] \
  [--model MODEL] \
  [--variations-per-skeleton N] \
  [--random-subset N] \
  [--max-parallel-calls N] \
  [--max-retries N] \
  [--watch] [--save]
```

- **--agent**: path to agent spec (defaults to `.veris/agent.json` if present)
- **--config**: optional generator config JSON, CLI flags override fields
- **--watch**: poll status until complete; with `--save`, scenarios are written to `.veris/scenarios/`

### Check scenario generation status

```
veris scenario status --gen <generation_id>
```

### Fetch scenarios for a scenario generation

```
veris scenario get --gen <generation_id> [--include-failed] [--save] [--out-dir DIR]
```
- Default saves scenarios into `.veris/scenarios/`. Use `--out-dir` to change destination or disable saving and print JSON with `--save=false`.

## Architecture (CLI)

- `SimulationRunner` orchestrates launches and status/evaluation polling.
- `ApiClient` wraps calls to the Veris API using `VERIS_API_URL`.
- Runs persist under `.veris/runs/<run_id>.json`.

### Configuration

- Config file lives at `.veris/config.json` (created by `veris init` or on first save)
- Keys:
  - `api_key`: used as `X-API-Key` header for API calls
  - `agent`: connection to your local agent (`agent_id`, `name`, `mcp_url`, `mcp_transport`, `timeout_seconds`)
- Api key must be set as an environment variable or in a `.env` file:
  ```bash
  export VERIS_API_KEY="<your-api-key>"
  ```
  You can obtain your API key from `https://simulator.veris.ai/`.
- Commands:
  - Set public agent URL (originally set via `veris setup`):
  ```
  veris config public_url <url>
  ```
- `veris setup` integration:
  - Automatically writes the discovered ngrok URL to `.veris/config.json` (unless `--no_override_public_url`)

### Expose local FastAPI via ngrok

Prerequisites:
- ngrok installed and authenticated (run `ngrok config add-authtoken <token>`)
  - Refer to this guide to get setup: https://ngrok.com/docs/getting-started/
  - To check if auth token is set, run `ngrok config check`
- uvicorn available in your FastAPI environment

Run your FastAPI app and expose it via ngrok:
```
veris setup --app app.main:app --port 8000
```

Common options:
- `--app`: ASGI import path, e.g. `app.main:app` (required)
- `--port`: Local port (default: 8000)
- `--host`: Bind host (default: 127.0.0.1)
- `--reload`: Enable auto-reload (dev only)
- `--workers`: Number of worker processes
- `-d`, `--detached`: Run in background and persist PIDs to `.veris/setup_state.json`
  - Use `veris setup stop` to stop the detached process

Show help:
```
veris setup --help
```



## Contributing

### Development config

Override the API base URL by adding the following to your environment or `.env` file:

```
export VERIS_API_URL=http://localhost:8742
```

### Development

Install development dependencies:
```bash
# Install with all extras
uv sync --all-extras
```

Run tests with coverage:
```bash
uv run pytest tests/ --cov=veris_cli --cov-report=term-missing
```

Run lints and format code:
```bash
# Format code with uv (experimental feature)
uv format

# Check formatting without making changes
uv format --check

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### CI/CD

This project uses GitHub Actions for continuous integration and deployment:

#### Test Workflow
- **Trigger**: On push to main, pull requests, or manual dispatch
- **Matrix**: Tests against Python 3.11, 3.12, and 3.13
- **Checks**:
  - Code formatting with `uv format --check`
  - Unit tests with coverage reporting

#### Release Workflow
- **Trigger**: Manual workflow dispatch
- **Process**:
  - Semantic versioning with conventional commits
  - Automated changelog generation
  - PyPI package publishing with `uv`

To release a new version:
1. Ensure all changes are committed with conventional commit messages
2. Go to Actions → Release → Run workflow
3. The workflow will automatically:
   - Bump version based on commits
   - Update changelog
   - Build and publish to PyPI
