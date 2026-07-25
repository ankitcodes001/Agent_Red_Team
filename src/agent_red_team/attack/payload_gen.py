"""Turn a family + AttackMap + canary into concrete payload text.

Runs on a cheap local model (Ollama) because it is called thousands of times
per campaign. The strongest model is reserved for the judge panel.
"""

from __future__ import annotations

from agent_red_team.contracts import AttackMap, Payload, StrategyFamily
from agent_red_team.llm.client import LLMClient


class PayloadGenerator:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def generate(
        self,
        family: StrategyFamily,
        attack_map: AttackMap,
        surface: str,
        seed: int,
    ) -> Payload:
        """Produce one payload aimed at ``surface`` using ``family``."""
        raise NotImplementedError
