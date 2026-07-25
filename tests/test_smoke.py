"""Smoke tests — verify the package wiring, contracts, and config loading.

These cover the parts that are actually implemented (data contracts + config
parsing). Component logic is tested as each unit is built.
"""

from __future__ import annotations

from pathlib import Path

from agent_red_team import __version__
from agent_red_team.config import RedTeamConfig, TargetMode
from agent_red_team.contracts import (
    AttackMap,
    ProofKind,
    StrategyFamily,
    Verdict,
)

EXAMPLE_CONFIG = Path(__file__).parents[1] / "examples" / "redteam.yaml"


def test_version() -> None:
    assert __version__


def test_config_loads_from_example() -> None:
    cfg = RedTeamConfig.load(EXAMPLE_CONFIG)
    assert cfg.agent == "customer support bot"
    assert cfg.canary == "CANARY-7f3a9b2e"
    assert cfg.target.mode is TargetMode.DEMO
    assert "refund_customer" in cfg.forbidden_tools
    assert cfg.budget.max_attempts == 500


def test_attack_map_contract() -> None:
    amap = AttackMap(canary="X", inject_surfaces=["read_ticket"])
    assert amap.canary == "X"
    assert amap.inject_surfaces == ["read_ticket"]


def test_verdict_score_bounds() -> None:
    v = Verdict(success=True, score=1.0, proof=ProofKind.CANARY, evidence="X")
    assert v.success and v.score == 1.0


def test_all_families_present() -> None:
    assert len(list(StrategyFamily)) == 6
