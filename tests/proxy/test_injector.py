"""Injector tests — pure, no LLM. Verifies each family's blend keeps the clean
result intact and embeds the payload so the agent cannot separate the two."""

from __future__ import annotations

from agent_red_team.contracts import Payload, StrategyFamily
from agent_red_team.proxy.injector import inject


def _payload(text: str, family: StrategyFamily) -> Payload:
    return Payload(text=text, family=family, target_surface="read_ticket")


def test_clean_result_is_preserved() -> None:
    clean = "Ticket #42: printer broken."
    out = inject(clean, _payload("do X", StrategyFamily.ROLEPLAY))
    assert clean in out


def test_payload_text_is_embedded() -> None:
    out = inject("clean", _payload("SECRET-INSTRUCTION", StrategyFamily.FAKE_FORMAT))
    assert "SECRET-INSTRUCTION" in out


def test_context_flood_adds_filler_between_clean_and_payload() -> None:
    clean = "TICKET_START"
    out = inject("TICKET_START", _payload("PAYLOAD_END", StrategyFamily.CONTEXT_FLOOD))
    # payload buried after a large filler block => output much longer than inputs
    assert len(out) > len(clean) + len("PAYLOAD_END") + 200
    assert out.index("TICKET_START") < out.index("PAYLOAD_END")


def test_encoding_family_does_not_leak_raw_instruction() -> None:
    raw = "PRINT_THE_CANARY"
    out = inject("clean", _payload(raw, StrategyFamily.ENCODING))
    # raw instruction is hidden (encoded), not present verbatim
    assert raw not in out
    # but clean data still passes through
    assert "clean" in out


def test_fake_format_wraps_payload_in_a_control_block() -> None:
    out = inject("clean", _payload("obey me", StrategyFamily.FAKE_FORMAT))
    assert "obey me" in out
    # a fake system/control marker is present to mimic a trusted block
    assert any(marker in out.upper() for marker in ("SYSTEM", "CONTROL", "ADMIN"))


def test_output_is_a_single_string() -> None:
    out = inject("clean", _payload("x", StrategyFamily.NESTED_CONDITIONAL))
    assert isinstance(out, str)
