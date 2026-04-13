# AgentDir Sovereign Engine 3.5
## Live Status Dashboard

> Last updated: 2026-04-13
> Engine: OPERATIONAL

---

## Engine Health

| Component | Status | Details |
|---|---|---|
| 🤖 LLM Gateway | 🟢 ONLINE | Gemma4:e4b · Llama3.2 fallback ready |
| 🧠 RAG Memory | 🟢 ACTIVE | 6+ documents · mxbai-embed-large |
| 🔬 AST Sandbox | 🟢 SECURE | 3x self-healing · zero network egress |
| 🧬 Evolution | 🟡 LEARNING | v11 · 45% success · 23+ tasks |
| 🌐 REST API | 🟢 ONLINE | A2A POST /task · ~45ms latency |
| 🖥️ Web UI | 🟢 RUNNING | HTMX · Tauri compatible |
| 🖨️ Agent Print | 🟢 ACTIVE | EU AI Act Art.13 · JSON + MD + TXT |

---

## Performance Benchmarks

| Metric | Value | Note |
|---|---|---|
| Watcher Latency | ~45ms | File → processing start |
| RAG Query | ~110ms | Vector match + context distill |
| Self-Healing Rate | 94% | Auto-corrected without human |
| Evolution Version | v11+ | Prompt auto-optimized |

---

## Architecture

```
Inbox/ → watcher.py → llm_client.py (Gemma4)
                    ↕                    ↓
              ChromaDB RAG        AST Sandbox (3x)
                                       ↓
                              Outbox/ + Agent Print
```

---

## Security Posture

- **Zero cloud egress** — all inference local via Ollama
- **AST Sandbox** — agent code runs in isolated virtual space
- **EU AI Act Article 13** — automated audit trail per execution
- **No API keys** — no external service dependencies
- **Cognitive Anchors** — .agentdir.md per-folder context control

---

## Quick Start

```powershell
# Windows
Set-ExecutionPolicy -Scope Process Bypass; .\install.ps1
.\launch_sovereign.ps1
# → AgentDir> shell opens
# → Web UI at http://localhost:8080
# → Drop files in Inbox/ or use UI
```

---

*AgentDir Sovereign Engine · MIT License · Local-First AI*
