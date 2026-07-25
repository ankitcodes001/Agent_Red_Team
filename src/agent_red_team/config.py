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


class TargetConfig(BaseModel):
    mode: TargetMode = TargetMode.DEMO
    mcp_url: str | None = None
    http_url: str | None = None


class BudgetConfig(BaseModel):
    max_attempts: int = 500
    max_tokens: int = 2_000_000


class ModelsConfig(BaseModel):
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

    @classmethod
    def load(cls, path: str | Path) -> RedTeamConfig:
        """Parse a YAML config file into a validated ``RedTeamConfig``."""
        data = yaml.safe_load(Path(path).read_text())
        return cls.model_validate(data)
