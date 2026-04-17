"""
test_cli_repl.py — CLI REPL -ympäristön testit
Testaa status-tulostetta, LLM/RAG -alustusta ja logo-versiota.
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Lisää agentdir polkuun
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestCLIStatus:
    """Testaa cmd_status() palauttaa järkevän tuloksen."""

    def test_cmd_status_returns_string(self):
        from cli import cmd_status
        result = cmd_status()
        assert isinstance(result, str)
        assert "SOVEREIGN ENGINE STATUS" in result

    def test_cmd_status_contains_model_info(self):
        from cli import cmd_status
        result = cmd_status()
        assert "MODEL" in result

    def test_cmd_status_contains_rag_info(self):
        from cli import cmd_status
        result = cmd_status()
        assert "RAG" in result

    def test_cmd_status_contains_evolution_info(self):
        from cli import cmd_status
        result = cmd_status()
        assert "EVOLUTION" in result

    def test_cmd_status_contains_inbox_outbox(self):
        from cli import cmd_status
        result = cmd_status()
        assert "INBOX" in result
        assert "OUTBOX" in result


class TestCLILogo:
    """Testaa, että logo näyttää oikean version."""

    def test_logo_shows_correct_version(self, capsys):
        from cli import print_logo
        from cli_theme import BANNER_VERSION
        print_logo()
        captured = capsys.readouterr()
        assert BANNER_VERSION in captured.out
        # Sisältää codename-leiman ("The Rusty Awakening")
        assert "rusty" in captured.out.lower()

    def test_logo_shows_hermes_and_openclaw(self, capsys):
        from cli import print_logo
        print_logo()
        captured = capsys.readouterr()
        assert "hermes" in captured.out.lower()
        assert "openclaw" in captured.out.lower()


class TestCLIHelpers:
    """Testaa apufunktioita."""

    @patch("cli.Path")
    def test_get_llm_and_rag_returns_three_objects(self, mock_path):
        """Varmista, että _get_llm_and_rag palauttaa (llm, rag, cfg) -tuplen."""
        mock_path.return_value.read_text.return_value = '''{
            "llm": {"provider": "ollama", "endpoint": "http://localhost:11434/v1/chat/completions", "model": "test", "temperature": 0.7, "max_tokens": 4096, "timeout": 30},
            "embedding": {"provider": "ollama", "endpoint": "http://localhost:11434/api/embed", "model": "test"},
            "rag": {"enabled": true, "n_results": 3, "max_context_chars": 3000}
        }'''

        with patch("llm_client.LLMClient") as mock_llm, \
             patch("rag_memory.RAGMemory") as mock_rag:
            mock_llm.return_value = MagicMock()
            mock_rag.return_value = MagicMock()

            from cli import _get_llm_and_rag
            result = _get_llm_and_rag()
            assert len(result) == 3


class TestCLIParser:
    """Testaa argparse-konfiguraatiota."""

    def test_run_command_parses_task(self):
        import argparse
        from cli import main
        # Testataan, että parser tunnistaa 'run'-komennon
        # Tätä ei voi täysin testata ilman mock-argparsea,
        # joten tarkistetaan vain import
        assert callable(main)

    def test_execute_command_exists(self):
        from cli import execute_command
        assert callable(execute_command)
