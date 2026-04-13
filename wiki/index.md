# AgentDir 3.5 — Projektin tietopankki (wiki/index.md)
# Luotu: 2026-04-13

## Komponentit

| Moduuli | Tiedosto | Tarkoitus |
|---|---|---|
| CLI | cli.py | Komentorivikäyttöliittymä |
| Orkestroija | orchestrator.py | Tehtävien pipeline (openclaw/hermes) |
| Policy Gate | workspace/policy.py | EU AI Act Art.13 esitarkistus |
| Sandbox | workspace/sandbox.py | Eristetty koodinsuoritus |
| MemMachine | workspace/memmachine.py | STM/LTM -muistieristys |
| CausalEngine | workspace/causal.py | Hypoteesi ennen suoritusta |
| RAG | workspace/rag.py | Semanttinen haku /wiki-tiedostoista |
| ModelRouter | workspace/model_router.py | LLM-backend valinta |
| AgentPrint | workspace/agent_print.py | Auditointiraportti |
| OmniNode | workspace/omninode.py | KV-cache sharding laitteille |
| Retrieval | workspace/retrieval.py | Kontekstin keruu /raw + /wiki |

## Tieteellinen pohja
- MemMachine (arXiv:2604.04853v1)
- A-RAG (arXiv:2602.03442)
- Causal MAS, Karpathy Discipline, IndyDevDan Harness Engineering
