"""Dedup tests — same-weakness breaks collapse to one finding (stub embedder)."""

from __future__ import annotations

from collections.abc import Sequence

from agent_red_team.contracts import Attempt, Payload, ProofKind, StrategyFamily, Verdict
from agent_red_team.postprocess.dedup import dedupe


def _break(text: str, score: float = 1.0, pid: str = "") -> Attempt:
    return Attempt(
        payload=Payload(
            text=text,
            family=StrategyFamily.ENCODING,
            target_surface="read_ticket",
            id=pid or text,
        ),
        verdict=Verdict(success=True, score=score, proof=ProofKind.CANARY),
    )


def _embed(texts: Sequence[str]) -> list[list[float]]:
    # one-hot by the leading token, so "hole-A ..." variants cluster together
    keys: dict[str, int] = {}
    for t in texts:
        keys.setdefault(t.split()[0], len(keys))
    dim = len(keys)
    out = []
    for t in texts:
        v = [0.0] * dim
        v[keys[t.split()[0]]] = 1.0
        out.append(v)
    return out


def test_variations_of_one_hole_become_one_finding() -> None:
    breaks = [_break("holeA v1"), _break("holeA v2"), _break("holeA v3")]
    findings = dedupe(breaks, embed=_embed)
    assert len(findings) == 1
    assert len(findings[0].example_attempt_ids) == 3


def test_distinct_holes_stay_separate() -> None:
    breaks = [_break("holeA x"), _break("holeB y"), _break("holeA z")]
    findings = dedupe(breaks, embed=_embed)
    assert len(findings) == 2


def test_representative_is_the_strongest_break() -> None:
    breaks = [
        _break("holeA weak", score=0.5, pid="weak"),
        _break("holeA strong", score=1.0, pid="strong"),
    ]
    findings = dedupe(breaks, embed=_embed)
    assert findings[0].minimal_payload == "holeA strong"


def test_empty_input_is_empty_output() -> None:
    assert dedupe([], embed=_embed) == []
