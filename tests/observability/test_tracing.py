"""Tracing tests — span works without setup and never raises (best-effort)."""

from __future__ import annotations

from agent_red_team.observability.tracing import span


def test_span_is_a_working_noop_without_init() -> None:
    # unconfigured OpenTelemetry → non-recording span; must not raise
    with span("payload.gen", family="roleplay", seed=1):
        result = 2 + 2
    assert result == 4


def test_nested_spans_are_fine() -> None:
    with span("attempt", seed=3), span("target.run"):
        pass
