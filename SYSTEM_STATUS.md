# SYSTEM_STATUS.md — AgentDir Sovereign Engine v4.2 Audit Report

**Date:** 2026-04-18
**Branch / PR:** `devin/sovereign-v4.2-audit`
**Scope:** Terminology correction · OmniNode routing · external A2A scaffold · API surface doc · README polish.

---

## 1. What actually changed

| Area                          | File(s)                                              | Change                                                                                              |
|-------------------------------|------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| External A2A contract         | `a2a_protocol.py` *(new)*                            | Generic `A2AMessage` envelope + pluggable `A2AAdapter` registry. `NoopAdapter` shipped for tests.   |
| OmniNode routing              | `omninode.py`                                        | `task_class` param (`heavy` / `ingest` / `auto`) + `role` on every node dict. mDNS TXT `role` reader. |
| Internal-workflow clarity     | `workflows/hermes.py`, `workflows/openclaw.py`, `workflows/__init__.py` | Docstrings now state explicitly these are **internal** cognition loops — not network protocols.    |
| API surface documentation     | `docs/04-Architecture/API_SYMBIOSIS.md` *(new)*     | One doc for every endpoint web / desktop / PWA / CLI hit. Covers REST, MCP, OmniNode WS, A2A.       |
| README                        | `README.md`                                          | Unicorn-grade rewrite — MaaS-DB vs RAG, 11-step pipeline, install, Gemma 4 E2B/E4B, roadmap.        |
| Wiki index                    | `wiki/index.md`                                      | Adds `a2a_protocol.py`, clarifies Hermes/OpenClaw role.                                              |

No functional behaviour was removed. Every prior call-site of
`OmniNodeManager.execute_sharded_task(model, prompt)` still works — the
new `task_class` parameter defaults to `"auto"`, which preserves v4.0
semantics (first-available node).

---

## 2. Terminology confirmation (Phase 1)

The previous directive claimed that earlier agent iterations had
misunderstood **Hermes** and **OpenClaw** as internal features when
they are external protocols. **The codebase shows the opposite.**

* `workflows/hermes.py` — `HermesWorkflow` is a Python class driven by
  `orchestrator.WorkflowOrchestrator`. It makes no network calls.
* `workflows/openclaw.py` — `OpenClawWorkflow` is a Python class driven
  by the same orchestrator. Also no network calls.

Verified with user (Achii) → **Option A confirmed**: Hermes and
OpenClaw stay internal. External agent-to-agent messaging moves into
`a2a_protocol.py` as `A2A_Protocol_Alpha` / `External_Swarm_Sync`. The
two concerns are now orthogonal.

---

## 3. TurboQuant status (Phase 2)

**Confirmed real**, against my earlier skepticism:

> *TurboQuant: Online Vector Quantization with Near-Optimal Distortion*
> — Zandieh, Daliri, Hadian, Mirrokni (Google Research). arXiv
> [2504.19874](https://arxiv.org/abs/2504.19874). Accepted ICLR 2026.
> Two-stage method (PolarQuant + 1-bit QJL) targeting server-side KV-cache
> compression. Reports ≥6× KV memory reduction, up to 8× attention-logit
> speedup on H100.

**Integration decision (per Achii directive):** park on roadmap.
Rationale:

* TurboQuant is a server-side GPU-inference KV-cache tool. Ollama (the
  default AgentDir inference backend) ships GGUF + llama.cpp's own
  scalar quantisations (Q4_K_M, Q5_K_M, etc.) and does not expose a
  KV-cache compression hook. Bolting TurboQuant into the Ollama path
  today means forking llama.cpp or shipping an alternative HuggingFace
  runtime — neither is proportionate to the current scope.
* The Gemma 4 release (2026-04-02) already addresses memory pressure on
  the mobile node via **Per-Layer Embeddings (PLE)** and a **shared KV
  cache**. E2B and E4B are explicitly mobile-efficient without external
  quantisation tricks.
* When a Cloud / Enterprise inference tier lands (own transformers
  runtime, not Ollama), TurboQuant becomes the default there — see
  §6 Proposal 3.

No placeholder flags were added to `llm_client.py` or `orchestrator.py`
to avoid theatre.

---

## 4. OmniNode routing (Phase 2 continued)

`omninode.py` now understands two task classes:

```
heavy  → prefer node with role="pc"       (Gemma 4 E4B — desktop / workstation)
ingest → prefer node with role="mobile"   (Gemma 4 E2B — phone / Pi / tethered edge)
auto   → first available node             (legacy v4.0 behaviour)
```

Roles are discovered two ways:

* mDNS TXT record `role=pc|mobile` (default `pc` if absent — LAN
  peers are usually desktops).
* Explicit `OmniNodeManager.add_ws_node(ws, name, role=...)` for
  WebSocket pairing (default `mobile` — preserves v4.0 PWA semantics).

Fallback is deliberately loud (`logger.info` on role mismatch) so
operators can see when the swarm is degraded.

---

## 5. Cross-platform API symbiosis (Phase 3)

Every surface now has a single documented entrypoint:

* **REST** — `server.py` on `:8080` (`/status`, `/manifest`, `/discover`,
  `/task`, `/rag/query`, `/stats`).
* **MCP** — `mcp_server.py` mounted at `/mcp/v1` (`tools`,
  `tools/call`: `rag_search`, `run_sandbox`).
* **OmniNode WS** — `omninode.py` on `:8081` (`compute_request` /
  `compute_result` envelopes, role-aware routing).
* **External A2A** — `a2a_protocol.py` (`A2AMessage` envelopes, pluggable
  adapters; transport today = AgentDir's own `POST /task`).

The frontend wiring cheat-sheet in `docs/04-Architecture/API_SYMBIOSIS.md`
§6 shows how each of `web/`, `desktop/`, the PWA at `/app`, and the CLI
should consume this surface. No frontend has to reverse-engineer
endpoints any more.

---

## 6. Three strategic improvement proposals

### Proposal 1 — Keyring-backed API token storage for Tauri desktop

**Problem.** `a2a.api_token` is the only thing standing between an
AgentDir process and arbitrary `/task` submissions. Today it is stored
plaintext in `config.json`. Acceptable for a dev laptop; embarrassing
for a v1 enterprise posture.

**Ask.** In `desktop/src-tauri/`, add the
[`keyring`](https://crates.io/crates/keyring) crate, move the token to
the OS keychain (macOS Keychain, Windows Credential Manager,
freedesktop Secret Service), and expose it to the webview only via a
Tauri command that signs requests in-process. `config.json` keeps
`api_token: ""` and the desktop shell injects it at runtime.

**Effort.** Half a day. Zero Python changes.

**Payoff.** Credential story that survives investor DD.

---

### Proposal 2 — PWA ↔ OmniNode WebSocket pairing via rotating QR

**Problem.** The PWA at `/app` currently stores its own history in
`localStorage` and does not yet feed the OmniNode swarm. Shipping PWA
→ ingest-class shards is the fastest path to proving the two-node
story end-to-end.

**Ask.** In `web/app/`, add a "Pair this phone" flow that:

1. The desktop PC node renders a rotating QR (valid 60 s) encoding
   `ws://{lan-ip}:8080/omninode/pair?ticket=…`.
2. The PWA scans, opens the WebSocket, and calls
   `OmniNodeManager.add_ws_node(..., role="mobile")`.
3. From then on, `orchestrator.run(..., task_class="ingest")` routes
   short classification / anchoring work to the phone's Gemma 4 E2B
   while the PC keeps Gemma 4 E4B for heavy synthesis.

**Effort.** One week (two-sided: rotating-ticket issuer in `server.py`
+ WebSocket handshake in PWA). No new dependencies.

**Payoff.** First live demo of the two-node story at Turku Arena
Builder's Challenge (13 May 2026).

---

### Proposal 3 — Enterprise / Cloud inference tier with TurboQuant baked in

**Problem.** Ollama is perfect for the Sovereign / Local story. It is
the wrong runtime the day a customer asks for a *hosted* AgentDir
that serves 200 concurrent agents on H100 — you want TurboQuant +
vLLM + PagedAttention, not llama.cpp.

**Ask.** Introduce `llm_client.BackendAdapter` as a protocol:
`LocalOllamaAdapter` (shipped today) and `HostedVLLMAdapter` (future,
flag-gated behind `llm.provider: "vllm"`). The hosted adapter enables
TurboQuant via the `turboquant-kv` package (or a direct vLLM fork when
that lands) and exposes the same `.complete()` / `.process_task()`
surface the rest of the engine already calls.

**Effort.** One-and-a-half weeks. Requires access to an H100 for
benchmarks.

**Payoff.** The honest answer to *"can Sovereign scale to our whole
org?"* stops being *"stand up N local workers"* and starts being *"flip
a config flag"*.

---

## 7. Outstanding (not in this PR)

* `orchestrator.py` still calls `workspace.policy` / `workspace.causal` /
  `workspace.memmachine` etc. lazily — those modules live under
  `workspace/` and were not in scope for this audit. They are stable;
  no `TODO` markers were found.
* `anchor_manager.py` compiles and has no open `TODO` comments at the
  time of this audit.
* `logical_validator.py` — **does not exist** in the repo (referenced
  only in prior directives). No action possible.

— *Devin, for Achii (Opus 4.7), Lead Architect · Sovereign Engine v4.2*
