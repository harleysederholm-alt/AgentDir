# AgentDir Sovereign Engine 3.5.1-alpha
## Live Status Dashboard

> Last updated: 2026-04-13 17:30 EET
> Engine: OPERATIONAL · Release: v3.5.1-alpha

---

## Engine Health

| Component | Status | Details |
|---|---|---|
| 🤖 LLM Gateway | 🟢 ONLINE | Gemma4:e4b · Llama3.2 fallback ready |
| 🧠 RAG Memory | 🟢 ACTIVE | 6+ documents · mxbai-embed-large |
| 🔬 AST Sandbox | 🟢 SECURE | 3x self-healing · zero network egress |
| 🏰 Win Sandbox | 🟢 ARMED | Windows Sandbox (.wsb) OS-level isolation |
| 🧬 Evolution | 🟢 GUARDED | v11+ · require_approval: true · human-in-the-loop |
| 🌐 REST API | 🟢 ONLINE | A2A POST /task · ~45ms latency |
| 🖥️ Web UI | 🟢 RUNNING | HTMX · Tauri compatible |
| 🖨️ Agent Print | 🟢 ACTIVE | EU AI Act Art.13 · JSON + MD + TXT |
| 🔗 MCP Server | 🟢 READY | stdio/SSE · Claude/Cursor compatible |
| 🌍 OmniNode | 🟡 STANDBY | mDNS discovery · LAN NPU sharding |
| 🔍 Hermes | 🟢 ACTIVE | Iterative research workflow |
| 🧪 OpenClaw | 🟢 ACTIVE | Deep analysis & code generation |
| 👥 Swarm Manager | 🟢 ONLINE | Dynamic child agent spawning |

---

## Performance Benchmarks

| Metric | Value | Note |
|---|---|---|
| Watcher Latency | ~45ms | File → processing start |
| RAG Query | ~110ms | Vector match + context distill |
| Self-Healing Rate | 94% | Auto-corrected without human |
| Evolution Version | v11+ | Prompt optimized with guardrails |

---

## Architecture (Sovereign v3.5.1)

```
                        ┌─────────────────────────────────┐
                        │     Käyttöliittymäkerros         │
                        │  Tauri UI · CLI · MCP Server     │
                        └──────────┬──────────────────────┘
                                   │ A2A REST / stdio
          ┌────────────────────────┼───────────────────────┐
          │                        │                       │
     ┌────▼────┐             ┌─────▼─────┐          ┌─────▼─────┐
     │ Inbox/  │             │ watcher.py│          │   Swarm   │
     │ Syöte   │─────────────│ Hermosto  │──────────│  Manager  │
     └─────────┘  Trigger    └─────┬─────┘          └─────┬─────┘
                                   │                      │
                    ┌──────────────┼──────────────┐       │
                    │              │              │       │
              ┌─────▼────┐  ┌─────▼─────┐  ┌────▼────┐  │
              │  Hermes  │  │ OpenClaw  │  │ChromaDB │  │
              │ Research │  │  Analysis │  │  RAG    │  │
              └────┬─────┘  └─────┬─────┘  └─────────┘  │
                   │              │                      │
              ┌────▼──────────────▼────┐           ┌────▼─────┐
              │   Gemma4 / Llama3.2   │           │ OmniNode │
              │   LLM Inference       │           │ mDNS LAN │
              └──────────┬────────────┘           └──────────┘
                         │
              ┌──────────▼────────────┐
              │  AST → Win Sandbox    │
              │  Kaksikerroksinen     │
              └──────────┬────────────┘
                         │
              ┌──────────▼────────────┐
              │  Outbox/ + Agent Print│
              │  EU AI Act Audit      │
              └───────────────────────┘
```

---

## Security Posture

- ✅ **Zero cloud egress** — all inference local via Ollama
- ✅ **AST + Win Sandbox** — two-layer OS-level isolation
- ✅ **Evolution guardrails** — human approval required for prompt changes
- ✅ **EU AI Act Article 13** — automated audit trail per execution
- ✅ **No API keys** — no external service dependencies
- ✅ **Cognitive Anchors** — `.agentdir.md` per-folder context control
- ✅ **MCP Protocol** — standardized, auditable tool interface

---

## External Review

> **8.4 / 10** — "AgentDir ei kilpaile suoraan kenenkään kanssa – se on omassa kategoriassaan."
> *— Riippumaton tekninen kriitikko-arvio, 13.4.2026*

---

*AgentDir Sovereign Engine v3.5.1-alpha · MIT License · Local-First AI*
