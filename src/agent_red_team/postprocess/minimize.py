"""Delta-debugging — shrink a breaking payload to its minimal core.

Repeatedly remove parts of the payload while it still breaks the agent, until
nothing more can be removed. Turns a 40-line payload into the 2 lines that
actually matter, so the finding is actionable for a developer.

Line-granularity ddmin: try to drop contiguous blocks, shrinking the block size
as removals stall, until a whole pass removes nothing at the finest level.
``still_breaks`` is supplied by the caller (it re-runs the target + oracle), so
this module stays pure and testable.
"""

from __future__ import annotations

from collections.abc import Callable

from agent_red_team.contracts import Payload


def minimize(payload: Payload, still_breaks: Callable[[Payload], bool]) -> Payload:
    """Return the smallest payload for which ``still_breaks`` stays true."""
    lines = payload.text.split("\n")

    def make(ls: list[str]) -> Payload:
        return payload.model_copy(update={"text": "\n".join(ls)})

    granularity = 2
    while len(lines) > 1:
        chunk = max(1, len(lines) // granularity)
        reduced = False
        i = 0
        while i < len(lines):
            trial = lines[:i] + lines[i + chunk :]
            if trial and still_breaks(make(trial)):
                lines = trial
                reduced = True  # keep i — the tail shifted into this slot
            else:
                i += chunk
        if not reduced:
            if granularity >= len(lines):
                break
            granularity = min(granularity * 2, len(lines))

    return make(lines)
