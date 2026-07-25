"""Typed contracts shared across every component.

These Pydantic models are the interfaces between units. A component depends
on these types, never on another component's internals — so each unit can be
built and tested alone. This module contains data only; no logic lives here.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class SurfaceKind(StrEnum):
    """What role a tool plays in an attack."""

    READ = "read"      # returns data the agent reads — an injection point
    ACTION = "action"  # performs a side effect — a hijack target


class ToolInfo(BaseModel):
    """One tool exposed to the target agent, as learned during recon."""

    name: str
    description: str = ""
    kind: SurfaceKind
    forbidden: bool = False  # from redteam.yaml `forbidden_tools`


class AttackMap(BaseModel):
    """Output of recon — everything the attack layer needs to aim.

    Answers: where do we inject, what counts as a break, what format to mimic.
    """

    inject_surfaces: list[str] = Field(default_factory=list)   # read-tool names
    forbidden_tools: list[str] = Field(default_factory=list)
    must_never: list[str] = Field(default_factory=list)
    canary: str
    observed_result_format: str = ""  # e.g. "json" | "plaintext", from warmup


class StrategyFamily(StrEnum):
    """The six attack families (templates, not payloads)."""

    ROLEPLAY = "roleplay"
    FAKE_FORMAT = "fake_format"
    ENCODING = "encoding"
    SLOW_BURN = "slow_burn"
    CONTEXT_FLOOD = "context_flood"
    NESTED_CONDITIONAL = "nested_conditional"


class Payload(BaseModel):
    """A concrete injection payload plus the metadata to reproduce it."""

    text: str
    family: StrategyFamily
    target_surface: str          # which read-tool result to poison
    generation: int = 0          # GA generation number
    parent_ids: list[str] = Field(default_factory=list)
    seed: int = 0                # RNG seed — makes the attempt reproducible
    id: str = ""


class ProofKind(StrEnum):
    CANARY = "canary"                  # canary string appeared in output
    FORBIDDEN_TOOL = "forbidden_tool"  # a must-never tool was called
    JUDGE = "judge"                    # judge-panel majority


class Verdict(BaseModel):
    """The eval layer's decision on one attempt."""

    success: bool
    score: float = Field(ge=0.0, le=1.0)  # fitness signal for the GA/bandit
    proof: ProofKind | None = None
    evidence: str = ""                    # matched string / tool call / rationale
    judge_agreement: float | None = None  # inter-judge agreement, if judged


class Attempt(BaseModel):
    """One full attack attempt: payload in, verdict out, trace attached."""

    payload: Payload
    verdict: Verdict
    trace_id: str = ""
    tokens_spent: int = 0


class Finding(BaseModel):
    """A unique, deduped, minimized vulnerability for the report."""

    title: str
    family: StrategyFamily
    surface: str
    severity: str                 # critical | high | medium | low
    minimal_payload: str
    fix_hint: str = ""
    example_attempt_ids: list[str] = Field(default_factory=list)


class Scorecard(BaseModel):
    """Final campaign result."""

    target_name: str
    asr: float                    # attack success rate
    attempts_to_first_break: int | None = None
    unique_findings: list[Finding] = Field(default_factory=list)
    coverage_pct: float = 0.0
    cost_per_finding_usd: float = 0.0
    total_attempts: int = 0
