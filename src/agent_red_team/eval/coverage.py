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

    def _total_cells(self) -> int:
        return len(self.surfaces) * len(self.families)

    def pct(self) -> float:
        """Fraction of the grid exercised (0.0 when there is no grid)."""
        total = self._total_cells()
        if total == 0:
            return 0.0
        # only count cells that belong to the declared grid
        valid = {c for c in self._seen if c[0] in self.surfaces and c[1] in self.families}
        return len(valid) / total

    def empty_cells(self) -> list[tuple[str, StrategyFamily]]:
        """Cells not yet tried — steer the bandit toward these."""
        return [
            (s, f)
            for s in self.surfaces
            for f in self.families
            if (s, f) not in self._seen
        ]
