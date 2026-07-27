"""UCB1 bandit tests — exploration-first, then exploitation."""

from __future__ import annotations

from collections import Counter

from agent_red_team.attack.bandit import UCB1Router
from agent_red_team.attack.strategies import all_families
from agent_red_team.contracts import StrategyFamily


def test_every_arm_is_explored_before_repeats() -> None:
    fams = all_families()
    r = UCB1Router(fams)
    picked = []
    for _ in range(len(fams)):
        f = r.select()
        picked.append(f)
        r.update(f, 0.0)
    # each family tried exactly once before any repeats
    assert set(picked) == set(fams)


def test_exploits_the_winning_arm_over_a_run() -> None:
    # UCB1 explores hard early; the exploitation guarantee is that, over many
    # rounds, the consistently-rewarding arm gets pulled the most.
    fams = all_families()
    r = UCB1Router(fams)
    winner = fams[2]
    picks: Counter[StrategyFamily] = Counter()
    for _ in range(300):
        f = r.select()
        picks[f] += 1
        r.update(f, 1.0 if f is winner else 0.0)
    assert picks.most_common(1)[0][0] is winner


def test_unpulled_arm_has_priority_over_a_rewarded_one() -> None:
    fams = all_families()
    r = UCB1Router(fams)
    r.update(fams[0], 1.0)  # arm 0 pulled, rest still virgin
    # an unpulled arm (score +inf) must be chosen over the rewarded arm 0
    assert r.select() is not fams[0]


def test_single_family_is_always_selected() -> None:
    only = [StrategyFamily.ROLEPLAY]
    r = UCB1Router(only)
    r.update(StrategyFamily.ROLEPLAY, 0.3)
    assert r.select() is StrategyFamily.ROLEPLAY
