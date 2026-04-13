"""
test_workflows.py — Hermes & OpenClaw -työnkulkujen testit
Mockaa LLM-vastaukset ja testaa logiikka ilman oikeaa mallia.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock


class TestHermesWorkflow:
    """Testaa Hermes-iteratiivinen tutkimus."""

    def _make_workflow(self, llm_responses: list[str]):
        """Luo HermesWorkflow mock-LLM:llä."""
        from workflows.hermes import HermesWorkflow

        mock_llm = MagicMock()
        mock_llm.process_task = AsyncMock(side_effect=llm_responses)

        mock_rag = MagicMock()
        mock_rag.query = MagicMock(return_value="RAG konteksti: tekoäly on...")

        return HermesWorkflow(mock_llm, mock_rag)

    def test_hermes_instantiation(self):
        from workflows.hermes import HermesWorkflow
        wf = HermesWorkflow(MagicMock(), MagicMock())
        assert wf.llm is not None
        assert wf.rag is not None

    def test_hermes_finds_answer_on_first_iteration(self):
        wf = self._make_workflow(["LOPULLINEN VASTAUS: Vastaus on 42"])
        result = asyncio.run(wf.run("Mikä on elämän tarkoitus?", max_iterations=3))
        assert "42" in result
        # LLM kutsuttiin vain kerran koska vastaus löytyi heti
        assert wf.llm.process_task.call_count == 1

    def test_hermes_iterates_until_answer(self):
        wf = self._make_workflow([
            "Tarvitaan lisää tietoa...",
            "Tutkitaan tarkemmin...",
            "LOPULLINEN VASTAUS: Python julkaistiin 1991",
        ])
        result = asyncio.run(wf.run("Milloin Python julkaistiin?", max_iterations=5))
        assert "1991" in result
        assert wf.llm.process_task.call_count == 3

    def test_hermes_respects_max_iterations(self):
        wf = self._make_workflow([
            "Ei vastausta vielä...",
            "Etsitään lisää...",
        ])
        result = asyncio.run(wf.run("Vaikea kysymys", max_iterations=2))
        # Ei löytänyt vastausta mutta palautti jotain
        assert result is not None
        assert wf.llm.process_task.call_count == 2

    def test_hermes_rag_called_each_iteration(self):
        wf = self._make_workflow([
            "Iteraatio 1...",
            "LOPULLINEN VASTAUS: Tulos",
        ])
        asyncio.run(wf.run("Testi", max_iterations=3))
        assert wf.rag.query.call_count == 2


class TestOpenClawWorkflow:
    """Testaa OpenClaw-syväanalyysi."""

    def _make_workflow(self, llm_responses: list[str]):
        from workflows.openclaw import OpenClawWorkflow

        mock_llm = MagicMock()
        mock_llm.process_task = AsyncMock(side_effect=llm_responses)

        mock_rag = MagicMock()
        mock_rag.query = MagicMock(return_value="Syvähaku: arkkitehtuurianalyysi")

        return OpenClawWorkflow(mock_llm, mock_rag)

    def test_openclaw_instantiation(self):
        from workflows.openclaw import OpenClawWorkflow
        wf = OpenClawWorkflow(MagicMock(), MagicMock())
        assert wf.llm is not None
        assert wf.rag is not None

    def test_openclaw_runs_three_phases(self):
        wf = self._make_workflow([
            "Dekoodaus: tarvitaan tieto koheesiosta ja kytkennöistä",  # Phase 1
            "Synteesi: arkkitehtuuri on modulaarinen ja hyvin rakennettu",  # Phase 3
        ])
        result = asyncio.run(wf.run("Analysoi tämän projektin arkkitehtuuri"))
        assert result is not None
        # LLM kutsuttiin 2 kertaa (dekoodaus + synteesi)
        assert wf.llm.process_task.call_count == 2
        # RAG kutsuttiin kerran (syvähaku)
        assert wf.rag.query.call_count == 1

    def test_openclaw_passes_rag_context_to_synthesis(self):
        wf = self._make_workflow([
            "Aliosat: watcher, rag_memory, sandbox",
            "Loppuraportti: kattava analyysi",
        ])
        asyncio.run(wf.run("Testitehtävä"))
        # Tarkista, että synteesikutsu sisältää RAG-kontekstin
        second_call = wf.llm.process_task.call_args_list[1]
        prompt_arg = second_call[0][0]  # Ensimmäinen positioargumentti
        assert "Syvähaku" in prompt_arg or "RAG" in prompt_arg
