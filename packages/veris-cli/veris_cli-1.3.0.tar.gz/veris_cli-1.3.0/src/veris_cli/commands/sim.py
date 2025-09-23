"""Simulation commands."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Annotated

import typer
import httpx
from rich import print as rprint
from rich.live import Live
from rich.text import Text

from veris_cli.config import load_config
from veris_cli.loaders import load_scenarios
from veris_cli.run_models import RunStatus
from veris_cli.runner import SimulationRunner
from veris_cli.runs import RunsStore
from veris_cli.errors import UpstreamServiceError, ConfigurationError

sim_app = typer.Typer(add_completion=False, no_args_is_help=False)


def _select_scenarios(
    scenarios: list[dict],
    ids: list[str] | None = None,
    use_cases: list[str] | None = None,
) -> list[dict]:
    """Select scenarios."""
    selected = scenarios
    if use_cases:
        use_set = set(use_cases)
        selected = [
            s for s in selected if s.get("skeleton_metadata", {}).get("use_case_name") in use_set
        ]
    if ids:
        id_set = set(ids)
        selected = [s for s in selected if s.get("scenario_id") in id_set]
    return selected


def _colorize_status(text: str) -> str:
    """Add Rich markup colors to status keywords in a status string."""
    mapping = {
        "pending": "yellow",
        "running": "cyan",
        "completed": "green",
        "failed": "red",
    }

    def _repl(match: re.Match[str]) -> str:
        word = match.group(0)
        color = mapping.get(word.lower())
        return f"[{color}]{word}[/]" if color else word

    return re.sub(
        r"\b(pending|running|completed|failed)\b",
        _repl,
        text,
        flags=re.IGNORECASE,
    )


@sim_app.command("launch")
def launch(
    agent: Annotated[
        Path | None,
        typer.Option("--agent", help="Path to agent.json"),
    ] = None,
    scenarios: Annotated[
        list[str] | None,
        typer.Option("--scenarios", help="Scenario IDs to run"),
    ] = None,
    use_cases: Annotated[
        list[str] | None,
        typer.Option("--use-cases", help="Filter by use_case_name"),
    ] = None,
    watch: Annotated[
        bool,
        typer.Option(
            "--watch",
            help="Continuously poll status until simulations and evals complete",
        ),
    ] = False,
):
    """Launch a simulation."""
    project_dir = Path.cwd()
    veris_dir = project_dir / ".veris"
    scenarios_dir = veris_dir / "scenarios"

    all_scenarios = load_scenarios(scenarios_dir)
    selected_scenarios = _select_scenarios(all_scenarios, scenarios, use_cases)

    if not selected_scenarios:
        rprint("[red]No scenarios selected[/red]")
        raise typer.Exit(code=1)

    store = RunsStore(project_dir)
    runner = SimulationRunner(store)

    # Load agent configuration from .veris/config.json, if available
    cfg = load_config(project_dir)
    agent_payload = None
    if getattr(cfg, "agent", None) is None:
        # Provide actionable guidance if no agent connection configured
        raise ConfigurationError(
            message=(
                "Agent endpoint is not configured in .veris/config.json (missing 'agent' block)."
            ),
            hint=(
                "Run 'veris setup ...' to detect your public URL automatically, or set it manually "
                "with 'veris config public_url https://<your-ngrok>.ngrok.io'."
            ),
            file_path=str(veris_dir / "config.json"),
            command_suggestion="veris setup  # or: veris config public_url https://...",
        )
    else:
        # Validate MCP is reachable and responding (2xx/3xx). Try base URL first, then fallback to /docs.
        base_url = cfg.agent.mcp_url.rstrip("/")
        try:
            resp = httpx.get(base_url, timeout=3.0, follow_redirects=True)
            if resp.status_code >= 400:
                # Fallback to a commonly-available route to detect FastAPI startup
                docs_url = f"{base_url}/docs"
                resp2 = httpx.get(docs_url, timeout=3.0, follow_redirects=True)
                if resp2.status_code >= 400:
                    raise ConfigurationError(
                        message="Configured agent endpoint is not responding successfully.",
                        hint=(
                            f"Tried: {base_url} (status {resp.status_code}) and {docs_url} (status {resp2.status_code}). "
                            "Ensure your FastAPI app is running and the tunnel URL is correct."
                        ),
                        file_path=str(veris_dir / "config.json"),
                        command_suggestion="veris setup  # or: veris config public_url https://...",
                    )
        except httpx.RequestError as exc:
            raise ConfigurationError(
                message="Unable to reach configured agent MCP URL.",
                hint=(
                    f"Tried: {base_url}. Ensure your FastAPI app is running and ngrok tunnel is active. "
                    "Run 'veris setup ...' or set a working public URL."
                ),
                file_path=str(veris_dir / "config.json"),
                command_suggestion="veris setup  # or: veris config public_url https://...",
            ) from exc

        # Convert Pydantic model to plain dict for payload
        agent_payload = cfg.agent.model_dump()  # type: ignore[assignment]

    run = runner.launch(selected_scenarios, agent=agent_payload)

    print("Run file: ", veris_dir.joinpath("runs", run.run_id + ".json"))

    if watch:
        try:
            with Live("", refresh_per_second=4, transient=False) as live:
                while True:
                    time.sleep(2.0)
                    try:
                        run = runner.poll_once(run)
                    except UpstreamServiceError as e:
                        rprint(f"[red]{str(e)}[/red]")
                        raise typer.Exit(code=1)
                    base = runner.format_status(run)
                    colored = _colorize_status(base)
                    header = "[cyan]Watching run status. Press Ctrl+C to stop.[/cyan]"
                    live.update(Text.from_markup(header + "\n" + colored))
                    # Done when all evals have reached a terminal state
                    all_evals_terminal = all(
                        getattr(sim, "evaluation_status", None)
                        in (
                            RunStatus.completed,
                            RunStatus.failed,
                        )
                        for sim in run.simulations
                    )
                    if all_evals_terminal:
                        live.update(
                            Text.from_markup(
                                header
                                + "\n"
                                + colored
                                + "\n[green]All simulations and evaluations are complete.[/green]"
                            )
                        )
                        break
        except KeyboardInterrupt:
            rprint(
                "[yellow]Stopped watching. Check later with: "
                f"veris sim status --run {run.run_id}[/yellow]"
            )
    else:
        rprint(runner.format_status(run))


@sim_app.command("status")
def status(
    run_id: str = typer.Option(..., "--run", help="Run ID"),
):
    """Get the status of a simulation."""
    store = RunsStore(Path.cwd())
    runner = SimulationRunner(store)
    run = store.load_run(run_id)
    try:
        run = runner.poll_once(run)
    except UpstreamServiceError as e:
        rprint(f"[red]{str(e)}[/red]")
        raise typer.Exit(code=1)
    rprint(runner.format_status(run))


@sim_app.command("results")
def results(
    run_id: Annotated[str, typer.Option("--run", help="Run ID")],
    json_out: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
):
    """Print evaluation_results for all sessions in the run."""
    store = RunsStore(Path.cwd())
    run = store.load_run(run_id)

    simulations = [
        {
            "scenario_id": sim.scenario_id,
            "simulation_id": sim.simulation_id,
            "eval_id": sim.eval_id,
            "evaluation_results": sim.evaluation_results or {},
        }
        for sim in run.simulations
    ]

    if json_out:
        import json as _json

        rprint(
            _json.dumps(
                {"run_id": run.run_id, "simulations": simulations},
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    # Default human-readable output
    rprint(f"[bold]Run[/bold] {run.run_id}")
    for item in simulations:
        scen = item["scenario_id"]
        sid = item["simulation_id"]
        rprint(f"- [cyan]{scen}[/cyan] ({sid})")
        rprint(item["evaluation_results"])  # prints dict or empty


@sim_app.command("kill")
def kill(simulation_id: str):
    """Kill a simulation."""
    from veris_cli.api import ApiClient

    api = ApiClient()
    api.kill_simulation(simulation_id)
    rprint(f"[yellow]Requested kill for simulation {simulation_id}[/yellow]")


@sim_app.command("eval-kill")
def eval_kill(eval_id: str):
    """Kill an evaluation."""
    from veris_cli.api import ApiClient

    api = ApiClient()
    api.kill_evaluation(eval_id)
    rprint(f"[yellow]Requested kill for evaluation {eval_id}[/yellow]")
