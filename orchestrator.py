"""
orchestrator.py — AgentDir 3.5 WorkflowOrchestrator

Orkestroi koko suoritusputken kahdessa moodissa:
  - openclaw: Nopea lineaarinen suoritus (kooditehtävät)
  - hermes:   Muistirikas suoritus (tutkimus, pitkä konteksti)

Pipeline-järjestys (pakollinen, ei saa ohittaa):
  1. policy.validate()          → Esitarkistusportti
  2. causal.write_hypothesis()  → Kausaaliloki
  3. retrieval.gather_context() → Kontekstin keruu
  4. rag.query()                → Semanttinen haku /wiki
  5. model_router.select()      → Mallin valinta
  6. sandbox.execute()          → Eristetty suoritus
  7. memmachine.commit()        → STM → LTM (jos verifioitu)
  8. agent_print.generate()     → Auditointiraportti
  9. return result              → Palauta yhteenveto
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("agentdir.orchestrator")


class WorkflowOrchestrator:
    """
    Ohjaa tehtävän koko elinkaaren. Ei itse tee laskentaa
    vaan delegoi workspace-moduuleille Karpathy-kurin mukaisesti.
    """

    VALID_MODES = ("openclaw", "hermes")

    def __init__(self, mode: str = "openclaw") -> None:
        if mode not in self.VALID_MODES:
            raise ValueError(f"Tuntematon moodi: {mode}. Sallitut: {self.VALID_MODES}")
        self.mode = mode

        # Alusta komponentit laiskasti
        self._policy = None
        self._causal = None
        self._retrieval = None
        self._rag = None
        self._router = None
        self._sandbox = None
        self._memmachine = None
        self._agent_print = None
        self._omninode = None
        self._evolution = None

    # ── Laiska alustus (importit vasta tarvittaessa) ─────────────────────

    @property
    def policy(self):
        if self._policy is None:
            from workspace.policy import PolicyEngine
            self._policy = PolicyEngine()
        return self._policy

    @property
    def causal(self):
        if self._causal is None:
            from workspace.causal import CausalEngine
            self._causal = CausalEngine()
        return self._causal

    @property
    def retrieval(self):
        if self._retrieval is None:
            from workspace.retrieval import ContextRetriever
            self._retrieval = ContextRetriever()
        return self._retrieval

    @property
    def rag(self):
        if self._rag is None:
            from workspace.rag import KnowledgeIndex
            self._rag = KnowledgeIndex()
            self._rag.build()
        return self._rag

    @property
    def router(self):
        if self._router is None:
            from workspace.model_router import ModelRouter
            self._router = ModelRouter()
        return self._router

    @property
    def sandbox(self):
        if self._sandbox is None:
            from workspace.sandbox import SovereignSandbox
            self._sandbox = SovereignSandbox()
        return self._sandbox

    @property
    def memmachine(self):
        if self._memmachine is None:
            from workspace.memmachine import MemMachine
            self._memmachine = MemMachine()
        return self._memmachine

    @property
    def agent_print(self):
        if self._agent_print is None:
            from workspace.agent_print import AgentPrint
            self._agent_print = AgentPrint()
        return self._agent_print

    @property
    def omninode(self):
        if self._omninode is None:
            from workspace.omninode import OmniNode
            self._omninode = OmniNode()
        return self._omninode

    @property
    def evolution(self):
        if self._evolution is None:
            from workspace.evolution_bridge import EvolutionBridge
            self._evolution = EvolutionBridge()
        return self._evolution

    # ── Pääsuoritusputki ─────────────────────────────────────────────────

    def run(self, task: str, model: str = "auto") -> dict[str, Any]:
        """
        Suorita tehtävä koko pipelinen läpi.
        Palauttaa dict: {success, summary, model, mode, print_id}
        """
        result: dict[str, Any] = {
            "success": False,
            "summary": "",
            "model": "",
            "mode": self.mode,
            "print_id": "",
        }

        # Vaihe 1: Policy Gate (EU AI Act Art. 13)
        try:
            self.policy.validate(task)
        except PermissionError as e:
            result["summary"] = f"[FAIL] Policy gate esti tehtavan: {e}"
            logger.warning("Policy gate esti: %s", e)
            return result

        # Vaihe 2: Kausaalinen hypoteesi ENNEN suoritusta
        self.causal.write_hypothesis(task)

        # Vaihe 3: Kontekstin keruu (/wiki + /raw)
        context = self.retrieval.gather_context(task)

        # Vaihe 4: RAG-haku /wiki tiedostoista
        rag_results = self.rag.query(task)
        if rag_results:
            rag_text = "\n".join(
                f"[{r['name']}] {r['content'][:200]}" for r in rag_results
            )
            context += f"\n\n## RAG-tulokset\n{rag_text}"

        # Hermes-moodi: lisää MemMachine LTM-konteksti
        if self.mode == "hermes":
            ltm_facts = self.memmachine.get_ground_truth()
            if ltm_facts:
                ltm_text = "\n".join(
                    f"[{k}] {v[:200]}" for k, v in ltm_facts.items()
                )
                context += f"\n\n## LTM Ground-Truth\n{ltm_text}"

        # Vaihe 5: Mallin valinta
        selected_model = model if model != "auto" else self.router.select(task)
        result["model"] = selected_model

        # Vaihe 6: Kutsu mallia ja aja sandbox-verifiointi
        llm_response = self.router.call(selected_model, task, context)

        # Tarkista sisältääkö vastaus koodia joka pitäisi ajaa sandboxissa
        sandbox_result = {"success": True, "stdout": "", "stderr": ""}
        if "```python" in llm_response:
            # Poimi koodilohko vastauksesta
            code_start = llm_response.index("```python") + len("```python")
            code_end = llm_response.index("```", code_start)
            code = llm_response[code_start:code_end].strip()
            sandbox_result = self.sandbox.execute(code)

        result["sandbox_ok"] = sandbox_result["success"]

        # Vaihe 7: MemMachine — commitoi LTM:ään jos sandbox onnistui
        if sandbox_result["success"]:
            self.memmachine.write_stm("latest_task", {
                "task": task,
                "response": llm_response[:500],
            })
            # Commitoi vain verifioitu tieto pysyvään muistiin
            if sandbox_result.get("stdout"):
                self.memmachine.commit_to_ltm(
                    "verified_results",
                    f"Tehtävä: {task}\nTulos: {sandbox_result['stdout'][:300]}",
                )

        # Kirjaa kausaalinen tulos
        self.causal.record_result(
            success=sandbox_result["success"],
            detail=f"Malli: {selected_model}, Sandbox: {'OK' if sandbox_result['success'] else 'FAIL'}",
        )

        # Vaihe 8: Agent Print (auditointiraportti)
        result["token_savings"] = 0  # Lasketaan tulevaisuudessa
        print_id = self.agent_print.generate(
            task=task,
            result=result,
            model=selected_model,
            mode=self.mode,
        )
        result["print_id"] = print_id

        # Vaihe 9: Evolution — rekisteroi tulos itseparannusmoottorille
        result["task"] = task
        evo_stats = self.evolution.record_task(result)
        result["evolution"] = evo_stats

        # Vaihe 10: Koosta yhteenveto
        result["success"] = sandbox_result["success"]
        status_icon = "[OK]" if result["success"] else "[FAIL]"
        evo_ver = evo_stats.get("prompt_version", "-")
        result["summary"] = (
            f"{status_icon} Tehtava: {task[:80]}\n"
            f"   Moodi: {self.mode} | Malli: {selected_model}\n"
            f"   Agent Print: {print_id} | Evoluutio: {evo_ver}\n"
            f"   Vastaus: {llm_response[:300]}"
        )

        return result

    # ── Status-komento ───────────────────────────────────────────────────

    def status(self) -> None:
        """Tulosta parven ja järjestelmän tila."""
        print("=" * 50)
        print("  AgentDir 3.5 Sovereign Engine -- Status")
        print("=" * 50)
        print(f"  Moodi: {self.mode}")
        print(f"  Circuit Breaker: {'[TRIPPED]' if self.causal.is_tripped else '[OK]'}")
        print()
        print(self.omninode.status())
        print()

        # RAG-indeksin tila
        rag_stats = self.rag.stats() if hasattr(self.rag, 'stats') else {}
        faiss_str = "FAISS" if rag_stats.get("faiss_active") else "keyword"
        doc_count = rag_stats.get("documents", len(self.rag._index))
        chunk_count = rag_stats.get("chunks", 0)
        print(f"  RAG: {doc_count} dok, {chunk_count} chunkkia [{faiss_str}]")
        print(f"  Sandbox: {self.sandbox.sandbox_type}")
        print()

        # Evolution
        evo = self.evolution.get_stats()
        if self.evolution.is_active:
            print(f"  Evolution: {evo.get('prompt_version', '?')} | "
                  f"onnistumis-% {evo.get('success_rate', 0):.0%} | "
                  f"tehtavia: {evo.get('total_tasks', 0)}")
        else:
            print(f"  Evolution: pois kaytosta")

        # Agent Print -raporttien maara
        from pathlib import Path
        prints = list(Path("outputs").glob("agent_print_*.json"))
        print(f"  Agent Printit: {len(prints)} raporttia")
        print("=" * 50)
