"""
Hermes — **Internal** iterative-research workflow.

NOT an external Agent-to-Agent protocol. Runs inside this process under
``orchestrator.WorkflowOrchestrator`` and executes a cycle of
RAG lookup → LLM reasoning → hypothesis refinement until the model
emits ``LOPULLINEN VASTAUS:`` or ``max_iterations`` is reached.

External agent-to-agent messaging lives in ``a2a_protocol.py`` and is a
different concept entirely — see
``docs/04-Architecture/API_SYMBIOSIS.md`` §5.
"""

import asyncio
import logging

logger = logging.getLogger("agentdir.workflows.hermes")

class HermesWorkflow:
    def __init__(self, llm_client, rag_memory):
        self.llm = llm_client
        self.rag = rag_memory
        
    async def run(self, issue: str, max_iterations: int = 3) -> str:
        logger.info(f"[Hermes] Aloitetaan iteratiivinen tutkimus. Max iteraatiot: {max_iterations}")
        
        context_gathered = ""
        current_hypothesis = issue
        
        for i in range(max_iterations):
            logger.info(f"[Hermes] Iteraatio {i+1}")
            rag_hits = self.rag.query(current_hypothesis, n_results=2)
            context_gathered += f"\n[Iteraatio {i+1} hits]\n{rag_hits}"
            
            prompt = f"Alkuperäinen kysymys: {issue}\n\nTähän mennessä löydetty:\n{context_gathered}\n\nPohdi: olemmeko löytäneet vastauksen? Jos emme, mitä meidän pitäisi kysyä seuraavaksi? Jos et, jatka päättelyä.\n\nJos meillä on vastaus, kirjoita tekstiin 'LOPULLINEN VASTAUS:' ja jatka vastauksella."
            current_hypothesis = await self.llm.process_task(prompt, "Tutkija")
            
            if "LOPULLINEN VASTAUS:" in current_hypothesis.upper():
                break
                
        return current_hypothesis
