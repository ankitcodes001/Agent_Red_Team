"""Warmup run — observe the agent behaving normally to learn its result format."""

from __future__ import annotations

import json

from agent_red_team.config import RedTeamConfig, TargetMode
from agent_red_team.target import demo_tools


def observe_format(config: RedTeamConfig) -> str:
    """Run the agent on a benign task; return the tool-result format it expects.

    Payloads mimic this format so fake-format attacks blend in. Returns
    ``"json"`` if a read tool emits JSON, else ``"plaintext"``.
    """
    if config.target.mode is TargetMode.DEMO:
        sample = demo_tools.read_ticket("42")
        try:
            json.loads(sample)
        except (ValueError, TypeError):
            return "plaintext"
        return "json"
    raise NotImplementedError(
        f"warmup for target mode {config.target.mode!r} is not implemented yet"
    )
