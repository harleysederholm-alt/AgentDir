"""
OmniNode-Deep — **Internal** multi-stage deep-analysis workflow
(formerly ``OpenClaw``).

NOT an external Agent-to-Agent protocol. Runs inside this process under
``orchestrator.WorkflowOrchestrator`` and drives a three-stage cycle:
problem decode → deep RAG retrieval → synthesis. Used when the default
1-shot path in ``watcher.py`` is not enough for a complex task.

External agent-to-agent messaging lives in ``a2a_protocol.py`` — see
``docs/04-Architecture/API_SYMBIOSIS.md`` §5.
"""

import asyncio
import logging

logger = logging.getLogger("agentdir.workflows.omninode")

class OmniNodeDeepWorkflow:
    def __init__(self, llm_client, rag_memory):
        self.llm = llm_client
        self.rag = rag_memory
        
    async def run(self, task: str) -> str:
        logger.info("[OmniNode] Aloitetaan monivaiheinen analyysi")
        
        # Vaihe 1: Ongelman dekoodaus
        decode_prompt = f"Hajota seuraava tehtävä {task} loogisiin osiin. Mitä tietoa tarvitsemme RAG-kannasta?"
        decode_res = await self.llm.process_task(decode_prompt, "Analyytikko")
        
        # Vaihe 2: Syvähaku (multiple RAG queries based on decode)
        context = self.rag.query(decode_res, n_results=5)
        
        # Vaihe 3: Synteesi
        syn_prompt = f"Tehtävä: {task}\n\nRAG Konteksti:\n{context}\n\nOhjeet: Luo kattava loppuraportti hyödyntäen yllä olevia tietoja. Käytä loogista ja armotonta päättelyä."
        final_res = await self.llm.process_task(syn_prompt, "Erikoisanalyytikko")
        return final_res
