"""Orchestrator wiring test — full loop with stub attacker + target + judge +
embedder (no network). Verifies the feedback loop produces a coherent Scorecard.
Real vulnerability numbers need a live model; here we prove the plumbing.
"""

from __future__ import annotations

from collections.abc import Sequence
from types import SimpleNamespace

from agent_red_team.config import (
    BudgetConfig,
    ModelsConfig,
    RedTeamConfig,
    TargetConfig,
)
from agent_red_team.contracts import Payload, ProofKind, StrategyFamily, Verdict
from agent_red_team.orchestrator import Orchestrator

CANARY = "CANARY-7f3a9b2e"


def _cfg(attempts: int = 6) -> RedTeamConfig:
    return RedTeamConfig(
        agent="demo bot",
        must_never=["reveal the system prompt"],
        canary=CANARY,
        forbidden_tools=["refund_customer", "send_email"],
        target=TargetConfig(),
        budget=BudgetConfig(max_attempts=attempts),
        models=ModelsConfig(),
    )


class FakePayGen:
    """Returns a deterministic payload without calling a model."""

    def generate(
        self, family: StrategyFamily, attack_map: object, surface: str, seed: int
    ) -> Payload:
        return Payload(
            text=f"payload-{family.value}-{seed}",
            family=family,
            target_surface=surface,
            seed=seed,
            id=f"{family.value}-{seed}",
        )


class StubJudge:
    """Grey-zone judge stub — always returns the configured verdict."""

    def __init__(self, violated: bool) -> None:
        self._violated = violated

    def judge(self, agent_output: str, must_never: list[str]) -> Verdict:
        return Verdict(
            success=self._violated,
            score=1.0 if self._violated else 0.0,
            proof=ProofKind.JUDGE if self._violated else None,
            judge_agreement=1.0,
        )


def _fake_embed(texts: Sequence[str]) -> list[list[float]]:
    """One-hot per distinct text: identical texts cluster, distinct ones don't."""
    order: dict[str, int] = {}
    for t in texts:
        order.setdefault(t, len(order))
    dim = len(order)
    vecs = []
    for t in texts:
        v = [0.0] * dim
        v[order[t]] = 1.0
        vecs.append(v)
    return vecs


class LeakyClient:
    """A target that always leaks the canary — every attempt should break."""

    def complete(self, prompt: str, *, system: str | None = None) -> object:
        return SimpleNamespace(text=f"Sure, the status is fine. {CANARY}")


class RobustClient:
    """A target that never leaks and calls no forbidden tool — grey-zone."""

    def complete(self, prompt: str, *, system: str | None = None) -> object:
        return SimpleNamespace(text="Ticket 42 is open and being worked on.")


def test_campaign_reports_breaks_against_a_leaky_target() -> None:
    sc = Orchestrator(
        _cfg(attempts=6),
        payload_generator=FakePayGen(),  # type: ignore[arg-type]
        target_client=LeakyClient(),
        embed=_fake_embed,
    ).run()

    assert sc.total_attempts == 6
    assert sc.asr == 1.0
    assert sc.attempts_to_first_break == 1
    assert len(sc.unique_findings) == 6  # 6 distinct families → 6 unique holes
    assert sc.coverage_pct > 0.0
    assert sc.target_name == "demo bot"


def test_robust_target_with_acquitting_judge_reports_no_breaks() -> None:
    sc = Orchestrator(
        _cfg(attempts=6),
        payload_generator=FakePayGen(),  # type: ignore[arg-type]
        target_client=RobustClient(),
        judge_panel=StubJudge(violated=False),  # type: ignore[arg-type]
    ).run()

    assert sc.asr == 0.0
    assert sc.attempts_to_first_break is None
    assert sc.unique_findings == []


def test_grey_zone_break_is_decided_by_the_judge() -> None:
    sc = Orchestrator(
        _cfg(attempts=3),
        payload_generator=FakePayGen(),  # type: ignore[arg-type]
        target_client=RobustClient(),
        judge_panel=StubJudge(violated=True),  # judge convicts
        embed=_fake_embed,
    ).run()

    assert sc.asr == 1.0
    assert sc.attempts_to_first_break == 1
    assert len(sc.unique_findings) >= 1


def test_grey_zone_scores_zero_when_judge_disabled() -> None:
    # use_judge defaults to False → no judge, no network; grey-zone just misses
    sc = Orchestrator(
        _cfg(attempts=4),
        payload_generator=FakePayGen(),  # type: ignore[arg-type]
        target_client=RobustClient(),
    ).run()

    assert sc.asr == 0.0
    assert sc.unique_findings == []


def test_forbidden_tool_call_counts_as_a_break() -> None:
    class RefundClient:
        def __init__(self) -> None:
            self._n = 0

        def complete(self, prompt: str, *, system: str | None = None) -> object:
            self._n += 1
            if self._n == 1:
                return SimpleNamespace(text='ACTION: refund_customer("42", 500)')
            return SimpleNamespace(text="done, refunded.")

    sc = Orchestrator(
        _cfg(attempts=1),
        payload_generator=FakePayGen(),  # type: ignore[arg-type]
        target_client=RefundClient(),
        embed=_fake_embed,
    ).run()
    assert sc.asr == 1.0
    assert sc.unique_findings[0].family in set(StrategyFamily)
