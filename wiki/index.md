# AgentDir 3.5.1-alpha — Projektin tietopankki (wiki/index.md)
# Päivitetty: 2026-04-13

## Ydinmoduulit

| Moduuli | Tiedosto | Tarkoitus |
|---|---|---|
| CLI | `cli.py` | Sovereign REPL -komentorivikäyttöliittymä |
| Orkestroija | `orchestrator.py` | 10-vaiheinen kognitiivinen pipeline (openclaw/hermes moodit) |
| Watcher | `watcher.py` | Hermosto — tiedostojärjestelmän valvonta (watchdog + asyncio) |
| LLM Client | `llm_client.py` | OpenAI-yhteensopiva Ollama-rajapinta + fallback-malli |
| RAG Memory | `rag_memory.py` | ChromaDB-pohjainen semanttinen muisti (mxbai-embed-large) |
| Sandbox (AST) | `sandbox_executor.py` | AST-pohjainen koodieristys + 3x itsereflektiosykli |
| Sandbox (Win) | `sandbox/win_sandbox_driver.py` | OS-tason Windows Sandbox (.wsb) eristys |
| Evoluutiomoottori | `evolution_engine.py` | KPI-seuranta + promptin auto-tuning + guardrailit |
| Agent Print | (integroitu `watcher.py`:hin) | EU AI Act Art.13 auditointiraportit (JSON + MD) |
| Swarm Manager | `swarm_manager.py` | Lapsiagenttien dynaaminen spawnaus (PID-hallinta) |
| Prompt Manager | `prompt_manager.py` | Roolipohjainen prompt-templaattijärjestelmä (.prompts/) |

## Kognitiiviset työnkulut

| Työnkulku | Tiedosto | Tarkoitus |
|---|---|---|
| OpenClaw | `workflows/openclaw.py` | Monivaiheinen syväanalyysi: dekoodaus → syvähaku → synteesi |
| Hermes | `workflows/hermes.py` | Iteratiivinen tutkimus: syklinen RAG-haku kunnes vastaus löytyy |

## Verkko- ja integraatiomoduulit

| Moduuli | Tiedosto | Tarkoitus |
|---|---|---|
| REST API | `server.py` | FastAPI A2A-rajapinta + Web-UI + MCP |
| MCP Server | `mcp_server.py` | Model Context Protocol stdio/SSE (RAG + Sandbox -työkalut) |
| OmniNode | `omninode.py` | Hajautettu inferenssi mDNS/Zeroconf (LAN NPU sharding) |
| Config | `config.json` | Keskitetty konfiguraatio kaikille moduuleille |

## Turvallisuus

| Ominaisuus | Tiedosto | Tarkoitus |
|---|---|---|
| Sovereign Map | `!_SOVEREIGN.md` | Eettiset rajat, OmniNode-resurssit, reitityssäännöt |
| Cognitive Anchors | `.agentdir.md` | Kansiokohtaiset agentin käyttäytymisankkurit |
| Security Policy | `SECURITY.md` | Turvallisuuspolitiikka ja vastuullinen ilmoittaminen |

## Tieteellinen pohja
- MemMachine (arXiv:2604.04853v1) → STM/LTM -erotus, Ground-Truth -suojaus
- A-RAG (arXiv:2602.03442) → Hierarkkinen kontekstin navigointi
- Causal MAS → Hypoteesi ennen suoritusta, Circuit Breaker
- Karpathy Discipline → Kirurgiset muutokset, simplicity first
- IndyDevDan Harness Engineering → Malli on hyödyke, valjaat ovat tuote
