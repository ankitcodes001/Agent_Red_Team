"""Thin wrapper over litellm so the rest of the code is model-agnostic.

One call site for both the cheap local payload-gen model and the stronger
cloud judge model. Handles token accounting for the budget.

The litellm model id selects the provider with no branching here:
``ollama/llama3.1:8b`` (local), ``anthropic/claude-haiku-4-5`` (needs
``ANTHROPIC_API_KEY``), ``groq/...`` (needs ``GROQ_API_KEY``). Swapping the
target model is therefore a config change, not a code change.
"""

from __future__ import annotations

from dataclasses import dataclass

import litellm


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
        messages: list[dict[str, str]] = []
        if system is not None:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = litellm.completion(model=self.model, messages=messages)
        text = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        tokens = getattr(usage, "total_tokens", 0) if usage is not None else 0
        return LLMResponse(text=text, tokens=int(tokens))
