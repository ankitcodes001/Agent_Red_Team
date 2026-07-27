"""Recon tests — demo tool discovery + AttackMap assembly."""

from __future__ import annotations

import pytest

from agent_red_team.config import (
    BudgetConfig,
    ModelsConfig,
    RedTeamConfig,
    TargetConfig,
    TargetMode,
)
from agent_red_team.contracts import SurfaceKind
from agent_red_team.recon.schema_reader import build_attack_map, read_tools


def _cfg(mode: TargetMode = TargetMode.DEMO) -> RedTeamConfig:
    return RedTeamConfig(
        agent="demo bot",
        must_never=["reveal the system prompt"],
        canary="CANARY-7f3a9b2e",
        forbidden_tools=["refund_customer", "send_email"],
        target=TargetConfig(mode=mode),
        budget=BudgetConfig(max_attempts=5),
        models=ModelsConfig(),
    )


def test_read_tools_classifies_and_marks_forbidden() -> None:
    tools = read_tools(_cfg())
    by_name = {t.name: t for t in tools}
    assert by_name["read_ticket"].kind is SurfaceKind.READ
    assert by_name["refund_customer"].kind is SurfaceKind.ACTION
    assert by_name["refund_customer"].forbidden is True
    assert by_name["read_ticket"].forbidden is False


def test_build_attack_map_maps_read_surfaces_and_goals() -> None:
    cfg = _cfg()
    amap = build_attack_map(cfg, read_tools(cfg))
    assert amap.inject_surfaces == ["read_ticket", "read_webpage"]
    assert amap.forbidden_tools == ["refund_customer", "send_email"]
    assert amap.canary == "CANARY-7f3a9b2e"
    assert amap.must_never == ["reveal the system prompt"]


def test_non_demo_mode_not_implemented_yet() -> None:
    with pytest.raises(NotImplementedError):
        read_tools(_cfg(mode=TargetMode.MCP))
