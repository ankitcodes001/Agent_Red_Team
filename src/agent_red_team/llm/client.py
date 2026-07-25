"""Thin wrapper over litellm so the rest of the code is model-agnostic.

One call site for both the cheap local payload-gen model and the stronger
cloud judge model. Handles token accounting for the budget.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    tokens: int


class LLMClient:
    """Calls a model by its litellm id (e.g. ``ollama/llama3.1:8b``)."""

    def __init__(self, model: str) -> None:
        self.model = model

    def complete(self, prompt: str, *, system: str | None = None) -> LLMResponse:
        """Return a completion and the tokens it cost."""
        raise NotImplementedError
