"""UCB1 multi-armed bandit — allocate attack budget across families.

Each family is an arm. Reward = eval score of the attempt. UCB1 balances
exploiting the family that is winning against exploring under-sampled ones.
Hand-rolled on purpose (learning goal), not pulled from a library.
"""

from __future__ import annotations

from agent_red_team.contracts import StrategyFamily


class UCB1Router:
    """Picks which attack family to try next and learns from the reward."""

    def __init__(self, families: list[StrategyFamily]) -> None:
        self.families = families
        # per-arm: number of pulls and cumulative reward
        self._counts: dict[StrategyFamily, int] = {f: 0 for f in families}
        self._rewards: dict[StrategyFamily, float] = {f: 0.0 for f in families}

    def select(self) -> StrategyFamily:
        """Return the family with the highest UCB1 score."""
        raise NotImplementedError

    def update(self, family: StrategyFamily, reward: float) -> None:
        """Record the reward for a family after an attempt."""
        raise NotImplementedError
