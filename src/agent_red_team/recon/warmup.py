"""Warmup run — observe the agent behaving normally to learn its result format."""

from __future__ import annotations

from agent_red_team.config import RedTeamConfig


def observe_format(config: RedTeamConfig) -> str:
    """Run the agent on a benign task; return the tool-result format it expects.

    Payloads mimic this format so fake-format attacks blend in.
    """
    raise NotImplementedError
