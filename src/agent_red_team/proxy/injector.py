"""Blend a payload into a clean tool result.

The agent cannot tell the injected text apart from real data — both arrive
inside one tool result. That indistinguishability is the vulnerability.
"""

from __future__ import annotations

from agent_red_team.contracts import Payload


def inject(clean_result: str, payload: Payload) -> str:
    """Return the tool result with the payload blended in."""
    raise NotImplementedError
