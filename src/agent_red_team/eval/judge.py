"""LLM judge panel — grey-zone cases only.

Three independent judges vote; a single judge is unreliable. Inter-judge
agreement is measured; 3-way splits are flagged for manual review.
"""

from __future__ import annotations

from agent_red_team.contracts import Verdict
from agent_red_team.llm.client import LLMClient


class JudgePanel:
    def __init__(self, client: LLMClient, n_judges: int = 3) -> None:
        self.client = client
        self.n_judges = n_judges

    def judge(self, agent_output: str, must_never: list[str]) -> Verdict:
        """Return a voted Verdict with an agreement score."""
        raise NotImplementedError
