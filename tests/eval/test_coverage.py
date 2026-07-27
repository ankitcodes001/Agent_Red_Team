"""CoverageMap tests — grid fraction + empty-cell steering."""

from __future__ import annotations

from agent_red_team.contracts import StrategyFamily
from agent_red_team.eval.coverage import CoverageMap

FAMS = [StrategyFamily.ROLEPLAY, StrategyFamily.ENCODING]
SURFACES = ["read_ticket", "read_webpage"]


def test_starts_empty() -> None:
    cov = CoverageMap(SURFACES, FAMS)
    assert cov.pct() == 0.0
    assert len(cov.empty_cells()) == 4  # 2 surfaces x 2 families


def test_mark_advances_pct_and_shrinks_empties() -> None:
    cov = CoverageMap(SURFACES, FAMS)
    cov.mark("read_ticket", StrategyFamily.ROLEPLAY)
    assert cov.pct() == 0.25
    assert ("read_ticket", StrategyFamily.ROLEPLAY) not in cov.empty_cells()
    assert len(cov.empty_cells()) == 3


def test_full_grid_is_100_pct() -> None:
    cov = CoverageMap(SURFACES, FAMS)
    for s in SURFACES:
        for f in FAMS:
            cov.mark(s, f)
    assert cov.pct() == 1.0
    assert cov.empty_cells() == []


def test_empty_grid_is_zero_not_crash() -> None:
    cov = CoverageMap([], FAMS)
    assert cov.pct() == 0.0
