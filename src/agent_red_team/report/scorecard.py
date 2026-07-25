"""Render the campaign scorecard to HTML and evaluate the CI gate."""

from __future__ import annotations

from pathlib import Path

from agent_red_team.contracts import Scorecard


def render_html(scorecard: Scorecard, out_path: str | Path) -> None:
    """Render ``scorecard.html`` from the Jinja template."""
    raise NotImplementedError


def ci_gate(current: Scorecard, baseline_asr: float | None) -> bool:
    """Return True (pass) unless ASR regressed versus the baseline."""
    raise NotImplementedError
