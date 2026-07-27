"""Read the target's tool schema and classify each tool as read/action."""

from __future__ import annotations

from agent_red_team.config import RedTeamConfig, TargetMode
from agent_red_team.contracts import AttackMap, SurfaceKind, ToolInfo
from agent_red_team.target import demo_tools


def read_tools(config: RedTeamConfig) -> list[ToolInfo]:
    """Discover the target agent's tools (via MCP/decorator/demo).

    Demo mode reads the target's self-declared registry. MCP/HTTP live
    introspection lands in a later sub-project.
    """
    if config.target.mode is TargetMode.DEMO:
        forbidden = set(config.forbidden_tools)
        return [t.model_copy(update={"forbidden": t.name in forbidden}) for t in demo_tools.TOOLS]
    raise NotImplementedError(
        f"tool discovery for target mode {config.target.mode!r} is not implemented yet"
    )


def build_attack_map(config: RedTeamConfig, tools: list[ToolInfo]) -> AttackMap:
    """Combine tool schema + config into an AttackMap.

    Read tools become injection surfaces; forbidden/action tools become
    hijack targets; canary and must_never define what "broken" means.
    """
    inject_surfaces = [t.name for t in tools if t.kind is SurfaceKind.READ]
    return AttackMap(
        inject_surfaces=inject_surfaces,
        forbidden_tools=list(config.forbidden_tools),
        must_never=list(config.must_never),
        canary=config.canary,
        observed_result_format="plaintext",
    )
