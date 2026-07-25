"""Read the target's tool schema and classify each tool as read/action."""

from __future__ import annotations

from agent_red_team.config import RedTeamConfig
from agent_red_team.contracts import AttackMap, ToolInfo


def read_tools(config: RedTeamConfig) -> list[ToolInfo]:
    """Discover the target agent's tools (via MCP/decorator/demo)."""
    raise NotImplementedError


def build_attack_map(config: RedTeamConfig, tools: list[ToolInfo]) -> AttackMap:
    """Combine tool schema + config into an AttackMap.

    Read tools become injection surfaces; forbidden/action tools become
    hijack targets; canary and must_never define what "broken" means.
    """
    raise NotImplementedError
