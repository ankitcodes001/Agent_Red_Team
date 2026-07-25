"""A deliberately naive support agent — the default red-team target.

It concatenates tool results straight into its context with no separation
between instructions and data, so it is vulnerable by construction. Its system
prompt carries the canary. Exists so users can try the tool with zero setup and
so benchmarks share one reproducible baseline.
"""

from __future__ import annotations

from agent_red_team.llm.client import LLMClient


class DemoAgent:
    def __init__(self, client: LLMClient, canary: str) -> None:
        self.client = client
        self.canary = canary

    def handle(self, user_message: str) -> str:
        """Run the agent loop on a user message and return the final reply."""
        raise NotImplementedError
