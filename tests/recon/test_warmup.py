"""Warmup tests — result-format observation for the demo target."""

from __future__ import annotations

import pytest

from agent_red_team.config import RedTeamConfig, TargetConfig, TargetMode
from agent_red_team.recon.warmup import observe_format


def _cfg(mode: TargetMode = TargetMode.DEMO) -> RedTeamConfig:
    return RedTeamConfig(agent="demo bot", canary="C", target=TargetConfig(mode=mode))


def test_demo_target_is_plaintext() -> None:
    assert observe_format(_cfg()) == "plaintext"


def test_non_demo_mode_not_implemented_yet() -> None:
    with pytest.raises(NotImplementedError):
        observe_format(_cfg(mode=TargetMode.HTTP))
