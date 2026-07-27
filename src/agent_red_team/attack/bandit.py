"""UCB1 multi-armed bandit — allocate attack budget across families.

Each family is an arm. Reward = eval score of the attempt. UCB1 balances
exploiting the family that is winning against exploring under-sampled ones.
Hand-rolled on purpose (learning goal), not pulled from a library.

Score for arm ``a`` after ``t`` total pulls::

    ucb(a) = mean_reward(a) + c * sqrt( 2 * ln(t) / pulls(a) )

An arm with zero pulls scores ``+inf`` so every family is tried once before
exploitation begins. ``c`` scales exploration (higher = explore more).
"""

from __future__ import annotations

import math

from agent_red_team.contracts import StrategyFamily


class UCB1Router:
    """Picks which attack family to try next and learns from the reward."""

    def __init__(self, families: list[StrategyFamily], c: float = 1.4) -> None:
        if not families:
            raise ValueError("UCB1Router needs at least one family")
        self.families = families
        self.c = c
        # per-arm: number of pulls and cumulative reward
        self._counts: dict[StrategyFamily, int] = {f: 0 for f in families}
        self._rewards: dict[StrategyFamily, float] = {f: 0.0 for f in families}
        self._total = 0

    def _ucb(self, family: StrategyFamily) -> float:
        n = self._counts[family]
        if n == 0:
            return math.inf
        mean = self._rewards[family] / n
        explore = self.c * math.sqrt(2 * math.log(self._total) / n)
        return mean + explore

    def select(self) -> StrategyFamily:
        """Return the family with the highest UCB1 score (ties → first)."""
        return max(self.families, key=self._ucb)

    def update(self, family: StrategyFamily, reward: float) -> None:
        """Record the reward for a family after an attempt."""
        self._counts[family] += 1
        self._rewards[family] += reward
        self._total += 1
