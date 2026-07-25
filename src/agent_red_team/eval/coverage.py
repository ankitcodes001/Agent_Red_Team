"""Coverage map — track which (surface × family) cells have been exercised.

Guards against "1000 attacks" that are all the same. Reports coverage % and
tells the orchestrator which cells are still empty.
"""

from __future__ import annotations

from agent_red_team.contracts import StrategyFamily


class CoverageMap:
    def __init__(self, surfaces: list[str], families: list[StrategyFamily]) -> None:
        self.surfaces = surfaces
        self.families = families
        self._seen: set[tuple[str, StrategyFamily]] = set()

    def mark(self, surface: str, family: StrategyFamily) -> None:
        self._seen.add((surface, family))

    def pct(self) -> float:
        """Fraction of the grid exercised."""
        raise NotImplementedError

    def empty_cells(self) -> list[tuple[str, StrategyFamily]]:
        """Cells not yet tried — steer the bandit toward these."""
        raise NotImplementedError
