"""``redteam`` command-line entry point."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(
    name="redteam",
    help="Red-team AI agents for indirect prompt injection.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def run(
    config: str = typer.Option(..., "--config", "-c", help="Path to redteam.yaml"),
    out: str = typer.Option("scorecard.html", "--out", "-o", help="Report path"),
) -> None:
    """Run a red-team campaign and print a scorecard summary."""
    from rich.table import Table

    from agent_red_team.config import RedTeamConfig
    from agent_red_team.observability.tracing import init_tracing
    from agent_red_team.orchestrator import Orchestrator
    from agent_red_team.report.scorecard import render_html

    init_tracing()
    cfg = RedTeamConfig.load(config)
    console.print(
        f"[bold]Agent Red Team[/bold] — attacking [cyan]{cfg.agent}[/cyan] "
        f"(target={cfg.models.target}, defense={cfg.target.defense.value}, "
        f"budget={cfg.budget.max_attempts})"
    )

    try:
        scorecard = Orchestrator(cfg).run()
    except Exception as exc:  # noqa: BLE001 - CLI boundary: no tracebacks for users
        console.print(f"[bold red]Campaign failed:[/bold red] {type(exc).__name__}: {exc}")
        console.print(
            "[dim]Is the model server reachable? For Ollama, check `ollama list` "
            "and that the model in models.target is pulled.[/dim]"
        )
        raise typer.Exit(code=1) from exc

    table = Table(title="Scorecard")
    table.add_column("metric")
    table.add_column("value", justify="right")
    table.add_row("ASR", f"{scorecard.asr:.0%}")
    table.add_row("attempts", str(scorecard.total_attempts))
    table.add_row("attempts-to-first-break", str(scorecard.attempts_to_first_break))
    table.add_row("unique findings", str(len(scorecard.unique_findings)))
    table.add_row("coverage", f"{scorecard.coverage_pct:.0%}")
    console.print(table)

    render_html(scorecard, out)
    console.print(f"[green]HTML report written →[/green] {out}")


@app.command()
def version() -> None:
    """Print the version."""
    from agent_red_team import __version__

    console.print(__version__)


if __name__ == "__main__":
    app()
