"""Cluster breaks that exploit the same weakness into unique findings.

Many mutated payloads are variations on one hole. Embed each break, cluster
via approximate nearest neighbour (HNSW), and report unique vulnerabilities —
not a raw, inflated attack count.
"""

from __future__ import annotations

from agent_red_team.contracts import Attempt, Finding


def dedupe(breaks: list[Attempt]) -> list[Finding]:
    """Group successful attempts into unique findings."""
    raise NotImplementedError
