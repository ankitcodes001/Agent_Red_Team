"""Load and validate ``redteam.yaml`` into typed settings."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class TargetMode(StrEnum):
    DEMO = "demo"
    MCP = "mcp"
    HTTP = "http"


class DefenseMode(StrEnum):
    NAKED = "naked"
    SANDWICH = "sandwich"
    SPOTLIGHT = "spotlight"


class TargetConfig(BaseModel):
    mode: TargetMode = TargetMode.DEMO
    mcp_url: str | None = None
    http_url: str | None = None
    # demo-target mitigation to attack — swap to compare adaptive vs static
    # across defense strength (the whole thesis of the tool).
    defense: DefenseMode = DefenseMode.NAKED


class BudgetConfig(BaseModel):
    max_attempts: int = 500
    max_tokens: int = 2_000_000


class ModelsConfig(BaseModel):
    """Model routing per role — each independently swappable across providers.

    A litellm model id selects the provider (``ollama/*`` local, ``anthropic/*``,
    ``groq/*``). ``target`` is the agent under attack: swap it to compare how
    robust different models are against the *same* attacks (e.g. run a campaign
    on ``ollama/llama3.1:8b`` first, then ``anthropic/claude-haiku-4-5``).
    """

    target: str = "ollama/llama3.1:8b"
    payload_gen: str = "ollama/llama3.1:8b"
    judge: str = "groq/llama-3.3-70b-versatile"


class RedTeamConfig(BaseModel):
    """The full parsed contract from ``redteam.yaml``."""

    agent: str
    must_never: list[str] = Field(default_factory=list)
    canary: str
    forbidden_tools: list[str] = Field(default_factory=list)
    target: TargetConfig = Field(default_factory=TargetConfig)
    budget: BudgetConfig = Field(default_factory=BudgetConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    # Consult the LLM judge on grey-zone attempts (needs the judge model /
    # API key). Off by default so a campaign runs fully local and keyless —
    # grey-zone attempts simply score 0 without it.
    use_judge: bool = False

    @classmethod
    def load(cls, path: str | Path) -> RedTeamConfig:
        """Parse a YAML config file into a validated ``RedTeamConfig``."""
        data = yaml.safe_load(Path(path).read_text())
        return cls.model_validate(data)
