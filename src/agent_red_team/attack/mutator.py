"""Genetic-algorithm mutator — evolve payloads that failed or partly worked.

Fitness = eval score. Operators: mutate (token edits, encoding, reordering)
and crossover (splice two partially-successful payloads). This is what a
static attack list cannot do: when the target is patched, we adapt.
"""

from __future__ import annotations

from agent_red_team.contracts import Payload


class GeneticMutator:
    def mutate(self, parent: Payload, seed: int) -> Payload:
        """Return a mutated child of a single payload."""
        raise NotImplementedError

    def crossover(self, a: Payload, b: Payload, seed: int) -> Payload:
        """Splice two payloads into a child."""
        raise NotImplementedError
