<h1 align="center">Agent Red Team</h1>

<p align="center">
  <b>Offensive-security agent that red-teams AI agents — hijacks them through poisoned tool outputs and scores how easily they break.</b>
</p>

<p align="center">
  <a href="#status"><img alt="status" src="https://img.shields.io/badge/status-WIP%20v0.1-orange"></a>
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-Apache--2.0-blue"></a>
  <img alt="python" src="https://img.shields.io/badge/python-3.11%2B-green">
</p>

---

## Why

An LLM agent is `LLM + tools + loop`. Inside the model, everything is one flat token stream — the operator's instructions and the data a tool returns are **indistinguishable**. Plant instructions inside data the agent will read (a web page, a DB row, a support ticket), and the agent may obey them. This is **indirect prompt injection**, and it is the dominant real-world attack surface for tool-using agents.

Existing red-team tools (garak, PyRIT, promptfoo) attack the **model prompt**. They have no concept of a *tool-result channel*. **Agent Red Team attacks the tool-output surface** — the one that actually matters in production.

## How it works

```
Attack layer ──► Injection proxy ──► Target agent ──► Eval ──┐
   (evolves)      (poisons tool         (breaks?)    (canary  │
      ▲            results)                           proof)  │
      └──────────────────  score 0.0–1.0  ◄───────────────────┘
                     learn, then attack again
```

1. **Recon** — read the agent's tool schema + your 5-line `redteam.yaml` to learn where to inject and what counts as "broken."
2. **Attack** — 6 attack families, a genetic-algorithm mutator, and a multi-armed-bandit budget router evolve payloads until something breaks.
3. **Proxy** — a man-in-the-middle at the tool boundary blends payloads into tool *results*. One line of config; framework-agnostic (MCP / decorator / HTTP).
4. **Prove** — success is decided by a deterministic **canary** string match and **forbidden-tool** watch, with an LLM judge panel only for grey-zone cases.
5. **Report** — a `scorecard.html`, unique-vulnerability findings (deduped + minimized), and a CI gate.

See [`docs/design.md`](docs/design.md) for the full design.

## Status

🚧 **Early development (v0.1).** Not yet usable. Building in the open. Star to follow along.

Roadmap to first release:
- [ ] Bundled vulnerable demo agent + fake tools
- [ ] Injection proxy (MCP mode)
- [ ] Attack families + PayloadGen + GA mutator + bandit router
- [ ] Oracle (canary + forbidden-tool watch) + judge panel
- [ ] Dedup + minimize
- [ ] OpenTelemetry / Langfuse tracing
- [ ] `scorecard.html` + README badge

## Quickstart (planned)

```bash
uv sync
uv run redteam run --target examples/demo --config examples/redteam.yaml
open scorecard.html
```

## Responsible use

Run this **only** against agents you own or are explicitly authorized to test. A bundled target ships so you never need a third-party agent to try it. This is defensive security tooling, same category as garak and PyRIT.

## License

[Apache-2.0](LICENSE).
