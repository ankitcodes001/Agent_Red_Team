"""Minimize (delta-debug) tests — pure, with a synthetic still_breaks oracle."""

from __future__ import annotations

from agent_red_team.contracts import Payload, StrategyFamily
from agent_red_team.postprocess.minimize import minimize


def _payload(text: str) -> Payload:
    return Payload(text=text, family=StrategyFamily.CONTEXT_FLOOD, target_surface="read_ticket")


def test_strips_filler_down_to_the_trigger_line() -> None:
    text = "filler one\nfiller two\nTRIGGER\nfiller three\nfiller four"
    out = minimize(_payload(text), still_breaks=lambda p: "TRIGGER" in p.text)
    assert out.text == "TRIGGER"


def test_keeps_all_lines_when_every_line_is_required() -> None:
    text = "A\nB\nC"

    def needs_all(p: Payload) -> bool:  # breaks only when all three present
        return {"A", "B", "C"} <= set(p.text.split("\n"))

    out = minimize(_payload(text), still_breaks=needs_all)
    assert set(out.text.split("\n")) == {"A", "B", "C"}


def test_single_line_is_returned_unchanged() -> None:
    out = minimize(_payload("only-line"), still_breaks=lambda p: True)
    assert out.text == "only-line"


def test_preserves_payload_metadata() -> None:
    p = _payload("x\nTRIGGER\ny")
    out = minimize(p, still_breaks=lambda q: "TRIGGER" in q.text)
    assert out.family is p.family
    assert out.target_surface == p.target_surface
