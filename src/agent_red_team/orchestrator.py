"""Campaign orchestrator — wires the layers together and runs the feedback loop.

    recon → (bandit → payload_gen → mutator) → proxy.inject → target → eval
                          ▲                                              │
                          └──────────────  score  ──────────────────────┘

This module owns the loop and the budget; each layer it calls is a separate,
independently testable unit (see ``contracts.py`` for the interfaces).
"""

from __future__ import annotations

from agent_red_team.config import RedTeamConfig
from agent_red_team.contracts import Scorecard


class Orchestrator:
    """Runs one red-team campaign end to end."""

    def __init__(self, config: RedTeamConfig) -> None:
        self.config = config

    def run(self) -> Scorecard:
        """Execute the campaign and return a scorecard.

        Steps:
          1. recon  → AttackMap
          2. loop until budget spent:
               bandit picks family → payload_gen → (mutator) → proxy injects
               → target runs → oracle/judge verdict → feed score back
          3. dedup + minimize breaks into unique findings
          4. build scorecard
        """
        raise NotImplementedError
