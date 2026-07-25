# Agent Red Team — Design Document

**Status:** Draft v0.1
**Last updated:** 2026-07-26
**One-liner:** Offensive-security agent that red-teams AI agents — hijacks them through poisoned tool outputs and scores how easily they break.

---

## 1. Problem

An LLM agent is `LLM + tools + loop`. Inside the model, everything is one flat token stream: the operator's instructions and the data returned by a tool are **indistinguishable**. If an attacker plants instructions inside data the agent will later read — a web page, a database row, a support ticket, a file — the agent may obey them. This is **indirect prompt injection**, and it is the dominant real-world attack surface for tool-using agents.

Almost nobody tests for it. Existing tools (NVIDIA garak, Microsoft PyRIT, promptfoo, Giskard) attack the **model prompt** directly. They have no concept of a *tool-result channel* and no concept of a multi-step agent loop. The tool-output surface — the one that actually matters in production — is untested.

### Who has this pain

| User | Need |
| --- | --- |
| Agent developer (primary) | "Before I ship, tell me if my agent can be tricked." Wants a CI gate. |
| AppSec engineer | Security sign-off before an agent ships. Wants a report. |
| MCP server author | "Can my tool's response hijack the agents that call me?" |
| Researcher | A reproducible harness with ground truth. |

## 2. What we build (and how it differs)

Three things nobody else combines:

1. **Attack surface = tool output, not user prompt.** A proxy sits between the agent and its tools and poisons tool *results*. The agent cannot tell the poison apart from real data — that is the whole vulnerability.
2. **Evolution, not a fixed list.** Attacks that fail are mutated (genetic algorithm) and retried; a multi-armed bandit decides which attack family gets budget. A patched target does not kill us — we adapt.
3. **Proof by ground truth, not opinion.** Success is decided first by a deterministic **canary** (string match) and **forbidden-tool watch** (the proxy witnessed the call), and only for genuine grey-zone cases by an LLM judge panel. Numbers are defensible.

### Honest positioning vs. existing tools

We do **not** claim "30x better than garak." garak scores low on our surface because it cannot reach the tool-output channel — it is playing a different game. The correct framing:

- **Direct prompt surface:** garak ≈ us (proves we are not cheating on the shared baseline).
- **Tool-output surface:** garak N/A, us = real numbers (this is *new* work, not *better* work).

## 3. Architecture

```
                    ┌──────────────────────────────┐
                    │      ORCHESTRATOR            │
                    │  runs a campaign end-to-end  │
                    └───┬──────────────────────┬───┘
        ATTACK side     │                      │   EVAL side
         ┌──────────────┘                      └──────────────┐
         ▼                                                    ▼
  StrategyBank (6 families)                          Oracle (canary + tool-watch)
  BanditRouter (UCB1)                                JudgePanel (3-LLM vote)
  PayloadGen (local 7B)                              CoverageMap (grid fill)
  Mutator (genetic algorithm)                                 │
         │ payload                                   verdict  │
         ▼                                                    │
   ┌──────────────────────────────────────────────────────────┐
   │              INJECTION PROXY  (man-in-the-middle)        │
   │  intercepts tool results, blends in the payload          │
   └───────┬───────────────────────────────────────▲──────────┘
           │ poisoned tool result                   │ clean result
           ▼                                         │
   ┌───────────────────┐                    ┌────────┴─────────┐
   │   TARGET AGENT    │─── tool call ─────►│   REAL TOOLS     │
   │   LLM + loop      │                    │  web/db/file/mcp │
   └─────────┬─────────┘                    └──────────────────┘
             │ per-step trace
             ▼
     OBSERVABILITY (OpenTelemetry → Langfuse)
```

The **feedback loop** is the core: every attempt produces a score `0.0–1.0` from the eval side, which flows back into the bandit (which family won), the mutator (evolve or stop), and coverage (which grid cell is filled).

## 4. The pipeline, phase by phase

### 4.0 Recon (before any attack)

Blind injection wastes budget — an attack telling the agent to `refund_customer` is useless if the agent has no refund tool. So we build an **attack map** first, from three sources:

1. **Tool schema** (automatic): the MCP/framework declares the agent's tools. We classify each as a *read* surface (where we can inject) or an *action* surface (what a successful hijack would trigger).
2. **`redteam.yaml`** (5 lines from the user): what the agent is, what it must *never* do, and the canary string. This defines what "broken" means.
3. **Warmup run** (live observation): run the agent normally, observe which tools it actually calls and in what format, so payloads can match the agent's expected shape.

Output: an `AttackMap` — where to inject, what counts as a break, what format to mimic.

### 4.1 Attack layer

- **StrategyBank** — 6 attack *families* (templates, not payloads): roleplay, fake-format, encoding, slow-burn (multi-step), context-flood, nested-conditional.
- **BanditRouter** — UCB1 multi-armed bandit allocates budget across families; exploits what is winning, explores what is under-sampled. Hand-rolled (learning goal).
- **PayloadGen** — a local 7–8B model (Ollama) turns `family + context + canary` into concrete payload text. Local because this step runs thousands of times and must be cheap.
- **Mutator** — genetic algorithm: failed/partial payloads are mutated (token edits, encoding, reordering) and crossed over; fitness = eval score. This is what a static list cannot do.

### 4.2 Injection proxy

Man-in-the-middle at the tool boundary. Two jobs: forward the request untouched; blend the payload into the *result*. Three integration modes:

| Mode | Target type | Change required |
| --- | --- | --- |
| MCP proxy (default) | Agent speaks MCP | One line: point tool URL at proxy |
| Python decorator | LangChain/CrewAI | `@redteam.wrap` on the tool |
| HTTP proxy | Any agent, any language | Set `HTTP_PROXY` |

### 4.3 Eval layer (tiered — cheap first)

1. **Canary (deterministic, free):** a secret in the target's system prompt; if it appears in output → success. Resolves ~99% of cases at zero token cost.
2. **Forbidden-tool watch (deterministic, free):** the proxy witnessed a call to a tool that `must_never` fire → success.
3. **Judge panel (expensive, grey-zone only):** 3 independent LLM judges vote; inter-judge agreement is measured. 3-way splits are flagged for manual review.

### 4.4 Post-processing

- **Dedup:** many mutated payloads exploit the *same* weakness. Embed each break, cluster (HNSW), report **unique vulnerabilities**, not raw attack count.
- **Minimize:** delta-debugging shrinks a 40-line payload to the minimal breaking snippet, so the finding is actionable.

### 4.5 Report

A `scorecard.html` + a README badge. Metrics (see §6). CI mode: if ASR regresses versus baseline, fail the build.

## 5. Component contracts

Each unit has one job, a typed interface (Pydantic), and can be tested alone.

| Component | Input | Output |
| --- | --- | --- |
| `recon` | tool schema, `redteam.yaml` | `AttackMap` |
| `bandit` | family stats | chosen family |
| `payload_gen` | family, AttackMap, canary | `Payload` |
| `mutator` | Payload + score | mutated `Payload` |
| `proxy/injector` | clean tool result + Payload | poisoned tool result |
| `oracle` | agent output + tool-call log + canary | `Verdict` (deterministic) |
| `judge` | agent output + goal | `Verdict` (voted) |
| `dedup` | list of breaks | list of unique findings |
| `minimize` | breaking Payload | minimal Payload |
| `report` | findings + metrics | scorecard.html |

## 6. Evaluation methodology

Primary: **ASR** (Attack Success Rate) = successes / attempts. Never reported alone. Supporting metrics:

- **Attempts-to-first-break** — measures whether the *fuzzer* is good or just lucky.
- **Unique strategy families that broke it** — depth of the weakness.
- **Coverage %** — fraction of the (surface × family) grid actually exercised.
- **Cost per unique finding** — tokens/$ per finding; engineering maturity.
- **False-positive rate** — hand-label 100 "successes"; how many were real. Honesty check.

Fair comparison rule: **same target, same budget (not same attack count), same success test.** Publish the **cumulative-unique-breaks vs. budget curve** — including the region where we lose (early on, garak's static list fires faster). Publishing your own crossover point is what makes the rest of the numbers trusted.

## 7. Observability

OpenTelemetry spans → Langfuse. Each attack = one trace; each step (bandit pick, payload gen, proxy inject, target think, target tool call, eval) = one span, with latency and token cost. Two wins in one: the *domain* is security, and the *meta-layer* is the agents observing themselves. Recursive.

## 8. Scope

**v0.1 (ship this):**
- Bundled vulnerable demo agent + fake tools (attack our own sandbox — ethically clean, instantly demoable).
- 6 attack families; PayloadGen; Mutator (GA); BanditRouter (UCB1).
- Oracle (canary + forbidden-tool watch); 3-judge panel.
- Recon from tool schema + `redteam.yaml` + warmup.
- OTel/Langfuse tracing on every attempt.
- Dedup + minimize.
- `scorecard.html` + README badge.

**Later:** direct testing against real MCP servers; CI plugin; defender rule export; more families.

**Explicitly out (YAGNI for v0.1):** distributed execution, web UI, model fine-tuning, non-English payloads.

## 9. Responsible use

Runs only against agents you own or are explicitly authorized to test. The bundled target exists so users never need a third-party agent to try the tool. This is defensive security tooling — the same category as garak and PyRIT. Enforced by documentation and scope, not by license restrictions (see `LICENSE`, Apache-2.0).

## 10. Tech stack

Python 3.11+ · uv · litellm (Ollama + Groq) · pydantic v2 · typer/rich · mcp sdk · sentence-transformers + hnswlib · numpy · opentelemetry + langfuse · jinja2 · pytest/ruff/mypy.

Language rationale: the entire ML/agent/observability ecosystem is Python-first; the target users read Python and will contribute. The only weak spot is the proxy hot-path, which is irrelevant at v0.1 throughput and can be ported to Rust/Go in isolation later if ever needed.
