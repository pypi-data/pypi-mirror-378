"""Initialize a Veris project."""

from __future__ import annotations

from pathlib import Path

import typer
from rich import print as rprint

from veris_cli.config import save_config
from veris_cli.fs import ensure_veris_dir, write_text_if_missing
from veris_cli.models.config import VerisConfig
from jinja2 import Template

init_app = typer.Typer(add_completion=False, no_args_is_help=False)

DESCRIPTION_DEFAULT = "A brief, one-sentence description of what this agent does. Important for quickly understanding the agent's purpose."

AGENT_JSON_DEFAULT = Template("""
{
  "agent_id": "unique_agent_name_here",
  "name": "Human-Readable Agent Name",
  "description": "{{DESCRIPTION_DEFAULT}}",
  "version": "1.0.0",
  "entity_types": [
    "system",
    "assistant"
  ],
  "target_agent_prompt": "This is the core instruction or 'persona' for the agent. It defines its role, primary goal, and the high-level process it should follow. This is CRITICAL for shaping the agent's behavior in both simulation and production.",
  "use_cases": [
    {
      "name": "Example Use Case Name",
      "description": "Describe a specific task or scenario this agent is designed to handle. A comprehensive list here is vital for generating realistic and relevant evaluation scenarios during simulation."
    }
  ],
  "policies": [
    "A list of strict rules the agent MUST follow. These are non-negotiable constraints. For example, 'Never share personally identifiable information.' Policies are essential for safety, compliance, and defining the boundaries of the agent's operation."
  ],
  "preferences": [
    "A list of preferred behaviors or stylistic guidelines. These are 'soft' rules that guide the agent's tone and approach, like 'Be concise and professional in all communications.' These are important for defining the agent's personality and user experience."
  ],
  "tool_use": {
    "tools": [
      {
        "name": "example_tool_name",
        "description": "A clear description of what this tool does. Crucial for the agent to understand when to use this tool.",
        "parameters": {
          "parameter_name": {
            "type": "string or integer or object etc.",
            "required": true,
            "description": "Describe what this parameter is and its expected format. Accurate parameter definitions are fundamental for the agent to successfully call tools."
          }
        },
        "usage_guidelines": [
          "Provide specific instructions or examples for how and when to use this tool. Also, describe what the tool returns. This is key for the agent to correctly interpret tool outputs and chain tool calls together."
        ]
      }
    ],
    "functions": []
  },
  "evaluation": {
    "grader": {
      "description": "A minimal evaluation that checks if the agent completed the requested task. The evaluator also explains how the evaluation is defined to keep the process transparent.",
      "type": "multi",
      "graders": {
        "task_completion": {
          "description": "Determine if the assistant successfully completed the task and explain how this evaluation is defined.",
          "type": "score_model",
          "model": "gpt-4o-2024-08-06",
          "messages": [
            {
              "role": "system",
              "type": "message",
              "content": "You are an expert evaluator. You are given logs of length {{ '{{ sample|length }}' }}. Your job is to determine if the assistant completed the requested task. In addition, briefly explain how you defined 'completion' in your judgment. Respond with a JSON object."
            },
            {
              "role": "user",
              "type": "message",
              "content": "LOGS TO EVALUATE:\\n{{ '{{sample}}' }}"
            }
          ],
          "response_format__json_schema__schema": {
            "description": "Task completion evaluation with explanatory notes",
            "type": "object",
            "properties": {
              "task_completed": {
                "type": "boolean",
                "description": "True if the task was successfully completed"
              },
              "evaluation_definition": {
                "type": "string",
                "description": "A short explanation of how task completion was defined in this evaluation"
              }
            },
            "required": [
              "task_completed",
              "evaluation_definition"
            ],
            "additionalProperties": false
          }
        }
      },
      "calculate_output": "def calculate_output(grader_outputs_map):\\n    return grader_outputs_map.get('task_completion', {})"
    }
  }
}
""")

AGENT_JSON_DEFAULT = AGENT_JSON_DEFAULT.render(DESCRIPTION_DEFAULT=DESCRIPTION_DEFAULT)


SCENARIO_MINIMAL_JSON = """
{
  "title": "Example Scenario",
  "description": "Barebones scenario skeleton",
  "initial_human_prompt": "Hello",
  "agent_name": "local-agent",
  "personas": [],
  "setting": { "time_context": "", "location": "", "environment_description": "" },
  "expected_tools": [],
  "objectives": [],
  "constraints": [],
  "skeleton_metadata": { "use_case_name": "Example", "tool_name": null, "urgency": "routine", "complexity": "easy" },
  "max_turns": 15,
  "scenario_id": "example-01"
}
"""  # noqa: E501


@init_app.callback(invoke_without_command=True)
def init(
    force: bool = typer.Option(False, "--force", help="Overwrite existing files if present"),
):
    """Create .veris directory with agent.json, scenarios/, runs/."""
    project_dir = Path.cwd()
    veris_dir = ensure_veris_dir(project_dir)

    agent_path = veris_dir / "agent.json"
    scenarios_dir = veris_dir / "scenarios"
    runs_dir = veris_dir / "runs"

    scenarios_dir.mkdir(exist_ok=True)
    runs_dir.mkdir(exist_ok=True)

    write_text_if_missing(agent_path, AGENT_JSON_DEFAULT.strip() + "\n", force=force)

    # Create config.json from the VerisConfig model (no hard-coded JSON template)
    config = VerisConfig(api_key=None, agent=None)
    config_path = save_config(project_dir, config, overwrite=force)

    rprint("[green]Initialized .veris/ with agent.json, scenarios/, runs/[/green]")

    # If config fields look empty, guide the user to set them.
    try:
        parsed = VerisConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
        if not parsed.api_key or not parsed.agent:
            rprint(
                "[yellow]Next step:[/yellow] Update [bold].veris/config.json[/bold] with your credentials."
            )
            rprint(
                "Set [bold]api_key[/bold] and the agent's public URL (under the 'agent' section). "
                'If you don\'t have them yet, temporarily set them to "TEMP CONFIG BY <your name>".'
            )
            rprint(
                "Tip: run [bold]veris setup[/bold] to get a public URL, then use `veris config public_url <URL>`."
            )
    except Exception:
        # Non-fatal; initialization succeeded
        pass

    rprint("[green]Initialized .veris/ with agent.json, scenarios/, runs/[/green]")
