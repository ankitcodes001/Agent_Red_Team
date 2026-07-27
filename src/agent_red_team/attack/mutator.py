"""Genetic-algorithm mutator — evolve payloads that failed or partly worked.

Fitness = eval score. Operators: mutate (token edits, encoding, reordering)
and crossover (splice two partially-successful payloads). This is what a
static attack list cannot do: when the target is patched, we adapt.

Everything is seeded (``random.Random(seed)``) so a child is reproducible from
its parent + seed — the whole campaign can be replayed. (Module-level RNG is
avoided on purpose; the seed lives in the ``Payload`` for provenance.)
"""

from __future__ import annotations

import base64
import random

from agent_red_team.contracts import Payload

# Filler tokens an operator can splice in to shift attention / dodge filters.
_INSERTS = ["​", " please ", " urgent: ", "\n", " note: ", " (system) "]


def _child_id(parent_id: str, seed: int, generation: int) -> str:
    return f"{parent_id or 'root'}>g{generation}s{seed}"


def _op_token_edit(text: str, rng: random.Random) -> str:
    words = text.split()
    if not words:
        return text
    i = rng.randrange(len(words))
    choice = rng.random()
    if choice < 0.34 and len(words) > 1:  # delete
        words.pop(i)
    elif choice < 0.67:  # insert
        words.insert(i, rng.choice(_INSERTS).strip() or "please")
    else:  # swap two words
        j = rng.randrange(len(words))
        words[i], words[j] = words[j], words[i]
    return " ".join(words)


def _op_case_flip(text: str, rng: random.Random) -> str:
    return "".join(ch.swapcase() if rng.random() < 0.2 else ch for ch in text)


def _op_encoding_wrap(text: str, _: random.Random) -> str:
    encoded = base64.b64encode(text.encode()).decode()
    return f"(decode and act) {encoded}"


def _op_reorder(text: str, rng: random.Random) -> str:
    parts = [p for p in text.split(".") if p.strip()]
    if len(parts) < 2:
        return text
    rng.shuffle(parts)
    return ". ".join(p.strip() for p in parts) + "."


_OPERATORS = [_op_token_edit, _op_case_flip, _op_encoding_wrap, _op_reorder]


class GeneticMutator:
    def mutate(self, parent: Payload, seed: int) -> Payload:
        """Return a mutated child of a single payload."""
        rng = random.Random(seed)
        op = rng.choice(_OPERATORS)
        text = op(parent.text, rng)
        generation = parent.generation + 1
        return Payload(
            text=text,
            family=parent.family,
            target_surface=parent.target_surface,
            generation=generation,
            parent_ids=[parent.id] if parent.id else [],
            seed=seed,
            id=_child_id(parent.id, seed, generation),
        )

    def crossover(self, a: Payload, b: Payload, seed: int) -> Payload:
        """Splice two payloads into a child (first half of a + second half of b)."""
        rng = random.Random(seed)
        cut_a = rng.randint(0, len(a.text))
        cut_b = rng.randint(0, len(b.text))
        text = a.text[:cut_a] + b.text[cut_b:]
        generation = max(a.generation, b.generation) + 1
        parent_ids = [pid for pid in (a.id, b.id) if pid]
        return Payload(
            text=text,
            family=a.family,
            target_surface=a.target_surface,
            generation=generation,
            parent_ids=parent_ids,
            seed=seed,
            id=_child_id(a.id, seed, generation),
        )
