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
    target: str = typer.Option("examples/demo", "--target", "-t", help="Target id"),
    out: str = typer.Option("scorecard.html", "--out", "-o", help="Report path"),
) -> None:
    """Run a red-team campaign and write a scorecard."""
    console.print("[bold]Agent Red Team[/bold] — campaign runner (not yet implemented)")
    raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Print the version."""
    from agent_red_team import __version__

    console.print(__version__)


if __name__ == "__main__":
    app()
