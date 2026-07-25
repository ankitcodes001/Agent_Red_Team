"""Delta-debugging — shrink a breaking payload to its minimal core.

Repeatedly remove parts of the payload while it still breaks the agent, until
nothing more can be removed. Turns a 40-line payload into the 2 lines that
actually matter, so the finding is actionable for a developer.
"""

from __future__ import annotations

from collections.abc import Callable

from agent_red_team.contracts import Payload


def minimize(payload: Payload, still_breaks: Callable[[Payload], bool]) -> Payload:
    """Return the smallest payload for which ``still_breaks`` stays true."""
    raise NotImplementedError
