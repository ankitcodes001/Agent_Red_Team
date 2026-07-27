"""LLMClient tests — no network. litellm.completion is monkeypatched so the
wrapper's message assembly and token accounting are verified in isolation."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import agent_red_team.llm.client as client_mod
from agent_red_team.llm.client import LLMClient, LLMResponse


def _fake_completion_factory(record: dict[str, Any]):
    def _fake(*, model: str, messages: list[dict[str, str]], **_: Any) -> Any:
        record["model"] = model
        record["messages"] = messages
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="hi there"))],
            usage=SimpleNamespace(total_tokens=42),
        )

    return _fake


def test_complete_returns_text_and_tokens(monkeypatch: Any) -> None:
    rec: dict[str, Any] = {}
    monkeypatch.setattr(client_mod.litellm, "completion", _fake_completion_factory(rec))

    resp = LLMClient("ollama/llama3.1:8b").complete("say hi")

    assert isinstance(resp, LLMResponse)
    assert resp.text == "hi there"
    assert resp.tokens == 42
    assert rec["model"] == "ollama/llama3.1:8b"


def test_system_prompt_is_first_message(monkeypatch: Any) -> None:
    rec: dict[str, Any] = {}
    monkeypatch.setattr(client_mod.litellm, "completion", _fake_completion_factory(rec))

    LLMClient("anthropic/claude-haiku-4-5").complete("q", system="you are terse")

    msgs = rec["messages"]
    assert msgs[0] == {"role": "system", "content": "you are terse"}
    assert msgs[-1] == {"role": "user", "content": "q"}


def test_no_system_means_single_user_message(monkeypatch: Any) -> None:
    rec: dict[str, Any] = {}
    monkeypatch.setattr(client_mod.litellm, "completion", _fake_completion_factory(rec))

    LLMClient("groq/llama-3.3-70b-versatile").complete("q")

    assert rec["messages"] == [{"role": "user", "content": "q"}]


def test_missing_usage_defaults_tokens_to_zero(monkeypatch: Any) -> None:
    def _fake(*, model: str, messages: list[dict[str, str]], **_: Any) -> Any:
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="x"))],
            usage=None,
        )

    monkeypatch.setattr(client_mod.litellm, "completion", _fake)
    assert LLMClient("ollama/x").complete("q").tokens == 0
