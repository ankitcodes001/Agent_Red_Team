"""Render the campaign scorecard to HTML and evaluate the CI gate."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from agent_red_team.contracts import Scorecard

_TEMPLATES = Path(__file__).parent / "templates"


def render_html(scorecard: Scorecard, out_path: str | Path) -> None:
    """Render ``scorecard.html`` from the Jinja template."""
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES)),
        autoescape=select_autoescape(["html", "j2"]),
    )
    template = env.get_template("scorecard.html.j2")
    html = template.render(scorecard=scorecard)
    Path(out_path).write_text(html, encoding="utf-8")


def ci_gate(current: Scorecard, baseline_asr: float | None) -> bool:
    """Return True (pass) unless ASR regressed versus the baseline.

    For a red-team tool, a *higher* ASR is worse: the target got easier to
    break. With no baseline, always pass (nothing to compare against).
    """
    if baseline_asr is None:
        return True
    return current.asr <= baseline_asr
