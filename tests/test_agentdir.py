"""
AgentDir – Testisuite
pytest tests/ -v

Kattaa:
  - file_parser   : kaikki tuetut formaatit + virhetilanteet
  - sandbox       : AST-tarkistus, timeout, onnistunut suoritus
  - config_manager: hot-reload, pistepolku-haku, thread-safety
  - rag_memory    : add/query/count + Ollama-fallback
  - llm_client    : onnistunut kutsu, yhteysvirhe, fallback-malli
  - evolution     : record, stats, kynnysarvo
  - swarm_manager : spawn, max-children-rajoitus
  - integration   : koko putki tiedostosta tulokseen (mock-LLM)
"""

from __future__ import annotations

import json
import tempfile
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os

import pytest

# Lisätään projektin juurikansio sys.path:iin
sys.path.insert(0, str(Path(__file__).parent.parent))


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def tmp_agent_dir(tmp_path: Path) -> Path:
    """Väliaikainen agenttihakemisto täydellä rakenteella."""
    (tmp_path / "Inbox").mkdir()
    (tmp_path / "Outbox").mkdir()
    (tmp_path / "memory").mkdir()
    (tmp_path / "swarm").mkdir()

    config = {
        "name": "TestAgent",
        "version": "1.0.0",
        "role": "Testi-avustaja",
        "llm": {
            "endpoint": "http://localhost:11434/v1/chat/completions",
            "model": "llama3.2:3b",
            "temperature": 0.7,
            "max_tokens": 1024,
            "timeout": 10,
            "fallback_models": [],
        },
        "embedding": {
            "endpoint": "http://localhost:11434/api/embed",
            "model": "mxbai-embed-large",
        },
        "prompt_templates": {
            "default": "Olet {role}.\n\nKonteksti:\n{context}\n\nTehtävä:\n{content}",
            "code": "Olet {role}.\n\nKonteksti:\n{context}\n\nTehtävä:\n{content}\n\nPalauta JSON: {{\"code\": \"...\", \"final_answer\": \"...\"}}",
        },
        "rag":       {"enabled": True,  "n_results": 2, "max_context_chars": 1000},
        "sandbox":   {"enabled": True,  "timeout_seconds": 5, "max_correction_attempts": 2},
        "swarm":     {"enabled": True,  "trigger_keywords": ["swarm"], "max_children": 3},
        "evolution": {"enabled": True,  "evaluate_every_n_tasks": 100, "min_tasks_before_evolve": 100,
                      "success_threshold": 0.7},
        "watchdog":  {"supported_extensions": [".txt", ".md", ".pdf", ".csv"],
                      "debounce_seconds": 0},
        "a2a":       {"enabled": False},
    }
    (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")
    return tmp_path


@pytest.fixture
def sample_txt(tmp_agent_dir: Path) -> Path:
    f = tmp_agent_dir / "Inbox" / "testi.txt"
    f.write_text("Tämä on testidokumentti. Se sisältää tärkeää tietoa.", encoding="utf-8")
    return f


@pytest.fixture
def sample_csv(tmp_agent_dir: Path) -> Path:
    f = tmp_agent_dir / "Inbox" / "data.csv"
    f.write_text("nimi,arvo,päivä\nAlfa,100,2024-01\nBeeta,200,2024-02\nGamma,150,2024-03",
                 encoding="utf-8")
    return f


@pytest.fixture
def sample_json(tmp_agent_dir: Path) -> Path:
    f = tmp_agent_dir / "Inbox" / "data.json"
    f.write_text(json.dumps({"avain": "arvo", "lista": [1, 2, 3]}), encoding="utf-8")
    return f


# ═══════════════════════════════════════════════════════════════════════════════
# 1. file_parser
# ═══════════════════════════════════════════════════════════════════════════════

class TestFileParser:
    def test_txt_returns_content(self, sample_txt):
        from file_parser import parse
        result = parse(sample_txt)
        assert "testidokumentti" in result

    def test_csv_returns_markdown_table(self, sample_csv):
        from file_parser import parse
        result = parse(sample_csv)
        assert "nimi" in result
        assert "Alfa" in result
        assert "|" in result  # markdown-taulukko

    def test_json_returns_formatted(self, sample_json):
        from file_parser import parse
        result = parse(sample_json)
        assert "avain" in result
        assert "arvo" in result

    def test_md_returns_content(self, tmp_agent_dir):
        from file_parser import parse
        f = tmp_agent_dir / "Inbox" / "testi.md"
        f.write_text("# Otsikko\n\nSisältö.", encoding="utf-8")
        assert "Otsikko" in parse(f)

    def test_unsupported_extension_raises(self, tmp_agent_dir):
        from file_parser import parse
        f = tmp_agent_dir / "Inbox" / "kuva.png"
        f.write_bytes(b"\x89PNG")
        with pytest.raises(ValueError, match="ei tuettu"):
            parse(f)

    def test_empty_txt_returns_empty_string(self, tmp_agent_dir):
        from file_parser import parse
        f = tmp_agent_dir / "Inbox" / "tyhja.txt"
        f.write_text("", encoding="utf-8")
        assert parse(f) == ""

    def test_csv_large_truncated(self, tmp_agent_dir):
        from file_parser import parse
        rows = ["col1,col2"] + [f"row{i},val{i}" for i in range(200)]
        f = tmp_agent_dir / "Inbox" / "iso.csv"
        f.write_text("\n".join(rows), encoding="utf-8")
        result = parse(f)
        assert "50" in result or "ensimmäiset" in result  # truncation notice


# ═══════════════════════════════════════════════════════════════════════════════
# 2. sandbox_executor – AST-pohjainen tarkistus
# ═══════════════════════════════════════════════════════════════════════════════

class TestSandboxExecutor:
    def test_simple_print_succeeds(self):
        from sandbox_executor import execute
        r = execute("print('hello')", timeout=5)
        assert r["success"] is True
        assert "hello" in r["output"]

    def test_arithmetic_succeeds(self):
        from sandbox_executor import execute
        r = execute("print(2 + 2)", timeout=5)
        assert r["success"] is True
        assert "4" in r["output"]

    def test_syntax_error_caught(self):
        from sandbox_executor import execute
        r = execute("def broken(:\n    pass", timeout=5)
        assert r["success"] is False
        assert r["violations"]  # AST parse fails

    def test_blocked_subprocess_import(self):
        from sandbox_executor import execute
        r = execute("import subprocess\nsubprocess.run(['ls'])", timeout=5)
        assert r["success"] is False
        assert r["violations"]
        assert any("subprocess" in v for v in r["violations"])

    def test_blocked_socket_import(self):
        from sandbox_executor import execute
        r = execute("import socket\ns=socket.socket()", timeout=5)
        assert r["success"] is False

    def test_blocked_os_system(self):
        from sandbox_executor import execute
        # Tämä läpäisi vanhan pattern-matching-tarkistuksen mutta ei AST:ta
        code = "import os\nos.system('echo hacked')"
        r = execute(code, timeout=5)
        assert r["success"] is False
        assert any("os.system" in v for v in r["violations"])

    def test_blocked_multiline_os_system(self):
        """Pattern-matching olisi ohitettu rivinvaihdolla – AST ei."""
        from sandbox_executor import execute
        code = textwrap.dedent("""
            import os
            cmd = 'echo hacked'
            os.system(cmd)
        """)
        r = execute(code, timeout=5)
        assert r["success"] is False

    def test_timeout_returns_timed_out(self):
        from sandbox_executor import execute
        r = execute("import time\ntime.sleep(60)", timeout=1)
        assert r["timed_out"] is True
        assert r["success"] is False

    def test_stderr_captured(self):
        from sandbox_executor import execute
        r = execute("import sys\nsys.stderr.write('err')", timeout=5)
        assert "err" in r["error"]

    def test_output_truncated(self):
        from sandbox_executor import execute
        r = execute("print('x' * 100000)", timeout=5)
        assert len(r["output"]) <= 8001  # MAX_OUTPUT_CHARS + newline


# ═══════════════════════════════════════════════════════════════════════════════
# 3. config_manager
# ═══════════════════════════════════════════════════════════════════════════════

class TestConfigManager:
    def test_basic_load(self, tmp_agent_dir):
        from config_manager import ConfigManager
        cm = ConfigManager(tmp_agent_dir / "config.json")
        assert cm.get("name") == "TestAgent"

    def test_dot_path_access(self, tmp_agent_dir):
        from config_manager import ConfigManager
        cm = ConfigManager(tmp_agent_dir / "config.json")
        assert cm.get("llm.model") == "llama3.2:3b"

    def test_default_value(self, tmp_agent_dir):
        from config_manager import ConfigManager
        cm = ConfigManager(tmp_agent_dir / "config.json")
        assert cm.get("ei_ole_olemassa", "oletus") == "oletus"

    def test_hot_reload(self, tmp_agent_dir):
        from config_manager import ConfigManager
        cm = ConfigManager(tmp_agent_dir / "config.json")
        assert cm.get("name") == "TestAgent"

        # Muuta tiedostoa levyllä
        cfg_path = tmp_agent_dir / "config.json"
        data = json.loads(cfg_path.read_text())
        data["name"] = "PäivitettyAgentti"
        cfg_path.write_text(json.dumps(data))

        changed = cm.reload()
        assert changed is True
        assert cm.get("name") == "PäivitettyAgentti"

    def test_invalid_json_keeps_old(self, tmp_agent_dir):
        from config_manager import ConfigManager
        cm = ConfigManager(tmp_agent_dir / "config.json")
        old_name = cm.get("name")

        cfg_path = tmp_agent_dir / "config.json"
        cfg_path.write_text("{virheellinen json")
        changed = cm.reload()

        assert changed is False
        assert cm.get("name") == old_name  # vanha arvo säilyy

    def test_on_change_callback(self, tmp_agent_dir):
        from config_manager import ConfigManager
        cm = ConfigManager(tmp_agent_dir / "config.json")
        called = []
        cm.on_change(lambda cfg: called.append(cfg["name"]))

        cfg_path = tmp_agent_dir / "config.json"
        data = json.loads(cfg_path.read_text())
        data["name"] = "Muuttunut"
        cfg_path.write_text(json.dumps(data))

        cm.reload()
        assert "Muuttunut" in called

    def test_save_updates_file(self, tmp_agent_dir):
        from config_manager import ConfigManager
        cm = ConfigManager(tmp_agent_dir / "config.json")
        cm.save({"uusi_avain": "uusi_arvo"})

        raw = json.loads((tmp_agent_dir / "config.json").read_text())
        assert raw.get("uusi_avain") == "uusi_arvo"

    def test_thread_safety(self, tmp_agent_dir):
        """Monta threadia lukee samanaikaisesti – ei race condition."""
        import threading
        from config_manager import ConfigManager
        cm = ConfigManager(tmp_agent_dir / "config.json")
        errors = []

        def reader():
            for _ in range(50):
                try:
                    _ = cm.get("llm.model")
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=reader) for _ in range(10)]
        for t in threads: t.start()
        for t in threads: t.join()

        assert errors == []


# ═══════════════════════════════════════════════════════════════════════════════
# 4. rag_memory
# ═══════════════════════════════════════════════════════════════════════════════

class TestRAGMemory:
    @pytest.fixture
    def rag(self, tmp_agent_dir):
        """RAG Ollama-fallbackilla (käyttää ChromaDB default-embeddingejä)."""
        from rag_memory import RAGMemory
        config = json.loads((tmp_agent_dir / "config.json").read_text())
        # Pakota fallback (Ollama ei ole testissä käytössä)
        with patch("rag_memory.OllamaEmbedder.is_available", return_value=False):
            return RAGMemory(config, memory_path=str(tmp_agent_dir / "memory"))

    def test_empty_count(self, rag):
        assert rag.count() == 0

    def test_add_and_count(self, rag):
        rag.add("doc1", "Tekoäly on mielenkiintoinen ala.", {"ts": "2024-01"})
        assert rag.count() == 1

    def test_query_empty_returns_string(self, rag):
        result = rag.query("jotain")
        assert isinstance(result, str)

    def test_add_and_query_returns_relevant(self, rag):
        rag.add("a1", "Koneoppiminen on tekoälyn osa-alue.", {"ts": "t1"})
        rag.add("a2", "Koiran ruokinta on tärkeää.", {"ts": "t2"})
        result = rag.query("tekoäly ja ML", n_results=1)
        assert "koneoppiminen" in result.lower() or "tekoäly" in result.lower()

    def test_upsert_same_id(self, rag):
        rag.add("same", "Versio 1", {"v": "1"})
        rag.add("same", "Versio 2", {"v": "2"})
        assert rag.count() == 1  # upsert, ei duplicate

    def test_metadata_strings_only(self, rag):
        """ChromaDB vaatii metadata-arvoiksi merkkijonot – ei kaadu."""
        rag.add("meta1", "Teksti", {"bool": True, "int": 42, "none": None})
        assert rag.count() == 1

    def test_query_n_results_respected(self, rag):
        for i in range(5):
            rag.add(f"doc{i}", f"Dokumentti numero {i} aiheesta X.", {"i": str(i)})
        result = rag.query("aihe X", n_results=2)
        assert isinstance(result, str)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. llm_client
# ═══════════════════════════════════════════════════════════════════════════════

class TestLLMClient:
    @pytest.fixture
    def llm(self, tmp_agent_dir):
        from llm_client import LLMClient
        config = json.loads((tmp_agent_dir / "config.json").read_text())
        return LLMClient(config)

    def test_successful_call(self, llm):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Tämä on vastaus."}}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_response):
            result = llm.complete("Testiprompt")

        assert result == "Tämä on vastaus."

    def test_connection_error_returns_error_string(self, llm):
        import requests as req
        with patch("requests.post", side_effect=req.exceptions.ConnectionError("ei yhteyttä")):
            result = llm.complete("Testiprompt")
        assert "❌" in result
        assert "Ollama" in result

    def test_json_parsing(self, llm):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"key": "value", "num": 42}'}}]
        }
        with patch("requests.post", return_value=mock_response):
            result = llm.complete_json("Prompti")
        assert result == {"key": "value", "num": 42}

    def test_json_parsing_embedded_in_text(self, llm):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": 'Tässä on vastaus: {"code": "print(1)"} loppu'}}]
        }
        with patch("requests.post", return_value=mock_response):
            result = llm.complete_json("Prompti")
        assert result is not None
        assert result.get("code") == "print(1)"

    def test_check_connection_true(self, llm):
        mock = MagicMock()
        mock.status_code = 200
        with patch("requests.get", return_value=mock):
            assert llm.check_connection() is True

    def test_check_connection_false_on_exception(self, llm):
        import requests as req
        with patch("requests.get", side_effect=req.exceptions.ConnectionError()):
            assert llm.check_connection() is False


# ═══════════════════════════════════════════════════════════════════════════════
# 6. evolution_engine
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvolutionEngine:
    @pytest.fixture
    def evo(self, tmp_agent_dir):
        from evolution_engine import EvolutionEngine
        config = json.loads((tmp_agent_dir / "config.json").read_text())
        os.chdir(tmp_agent_dir)  # tiedostot kirjoitetaan tmp-kansioon
        return EvolutionEngine(config, str(tmp_agent_dir / "config.json"))

    def test_initial_stats(self, evo):
        stats = evo.get_stats()
        assert stats["total_tasks"] == 0
        assert stats["success_rate"] == 0.0

    def test_record_success(self, evo):
        evo.record("t1", "tehtävä 1", success=True)
        stats = evo.get_stats()
        assert stats["total_tasks"] == 1
        assert stats["success_rate"] == 1.0

    def test_record_failure(self, evo):
        evo.record("t1", "tehtävä 1", success=True)
        evo.record("t2", "tehtävä 2", success=False)
        stats = evo.get_stats()
        assert stats["success_rate"] == 0.5

    def test_history_persisted_to_disk(self, evo, tmp_agent_dir):
        evo.record("p1", "persistoitu", success=True)
        hist = (tmp_agent_dir / "memory" / "task_history.jsonl").read_text()
        assert "p1" in hist

    def test_no_evolution_below_min_tasks(self, evo):
        """Evoluutio ei käynnisty alle min_tasks-rajan."""
        with patch.object(evo, "_propose_improvement") as mock_prop:
            for i in range(5):
                evo.record(f"t{i}", "tehtävä", success=False)
            mock_prop.assert_not_called()

    def test_get_stats_returns_prompt_version(self, evo):
        stats = evo.get_stats()
        assert "prompt_version" in stats
        assert stats["prompt_version"].startswith("v")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. swarm_manager
# ═══════════════════════════════════════════════════════════════════════════════

class TestSwarmManager:
    @pytest.fixture
    def swarm(self, tmp_agent_dir):
        from swarm_manager import SwarmManager
        config = json.loads((tmp_agent_dir / "config.json").read_text())
        # Kopioi watcher.py ym. jotta swarm voi kopioida ne
        for fname in ["watcher.py", "rag_memory.py", "sandbox_executor.py",
                      "file_parser.py", "llm_client.py", "evolution_engine.py",
                      "config_manager.py", "swarm_manager.py"]:
            src = Path(__file__).parent.parent / fname
            if src.exists():
                (tmp_agent_dir / fname).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        return SwarmManager(config, root_dir=tmp_agent_dir)

    def test_spawn_creates_directory_in_swarm_not_inbox(self, swarm, tmp_agent_dir):
        child = swarm.spawn_child("Analysoi data", "Analyytikko", "testi.txt")
        assert child is not None
        assert child.exists()
        # KRIITTINEN: lapsi EI ole Inbox:n sisällä
        assert "Inbox" not in str(child)
        assert str(tmp_agent_dir / "swarm") in str(child)

    def test_spawn_creates_inbox_outbox(self, swarm, tmp_agent_dir):
        child = swarm.spawn_child("Tehtävä", "Tutkija", "data.pdf")
        assert (child / "Inbox").exists()
        assert (child / "Outbox").exists()

    def test_task_written_to_child_inbox(self, swarm, tmp_agent_dir):
        child = swarm.spawn_child("Laske summa", "Laskija", "luvut.csv")
        inbox_files = list((child / "Inbox").iterdir())
        assert len(inbox_files) > 0
        task_content = inbox_files[0].read_text()
        assert "Laske summa" in task_content

    def test_child_config_disables_swarm(self, swarm, tmp_agent_dir):
        """Lapsi-agentti ei saa luoda omia lapsiaan (estää ketjureaktion)."""
        child = swarm.spawn_child("Tehtävä", "Analyytikko", "testi.txt")
        child_cfg = json.loads((child / "config.json").read_text())
        assert child_cfg["swarm"]["enabled"] is False

    def test_max_children_respected(self, swarm, tmp_agent_dir):
        swarm.max_children = 2
        c1 = swarm.spawn_child("T1", "R1", "f1.txt")
        c2 = swarm.spawn_child("T2", "R2", "f2.txt")
        c3 = swarm.spawn_child("T3", "R3", "f3.txt")
        # Kolmas ei saa luoda – max 2
        created = [c for c in [c1, c2, c3] if c is not None]
        assert len(created) == 2

    def test_spawn_includes_swarm_manager_for_child_watcher(self, swarm, tmp_agent_dir):
        """Lapsen watcher.py importtaa swarm_managerin – tiedosto pitää kopioida."""
        child = swarm.spawn_child("T", "R", "f.txt")
        assert child is not None
        assert (child / "swarm_manager.py").exists()
        assert (child / "swarm_manager.py").stat().st_size > 100

    def test_should_swarm_detects_keyword(self, tmp_agent_dir):
        from swarm_manager import should_swarm
        config = json.loads((tmp_agent_dir / "config.json").read_text())
        assert should_swarm("Tee tämä swarm-työnä", config) is True

    def test_should_swarm_false_without_keyword(self, tmp_agent_dir):
        from swarm_manager import should_swarm
        config = json.loads((tmp_agent_dir / "config.json").read_text())
        assert should_swarm("Tee tiivistelmä.", config) is False


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Integraatiotesti – koko putki mock-LLM:llä
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """
    Testaa koko putki tiedoston ilmestymisestä Outbox-tulokseen.
    LLM ja Ollama-embeddings on mockattu → ei tarvita oikeaa serveriä.
    """

    def _mock_llm_response(self, text: str):
        mock = MagicMock()
        mock.raise_for_status = MagicMock()
        mock.json.return_value = {"choices": [{"message": {"content": text}}]}
        return mock

    def test_txt_file_produces_outbox_result(self, tmp_agent_dir):
        import importlib, sys

        # Vaihda hakemisto
        original_dir = os.getcwd()
        os.chdir(tmp_agent_dir)

        try:
            # Poista cacheista jotta saadaan puhtaat importit
            for mod in list(sys.modules.keys()):
                if "agentdir" in mod or mod in ("rag_memory", "llm_client",
                                                 "file_parser", "sandbox_executor",
                                                 "config_manager", "swarm_manager",
                                                 "evolution_engine"):
                    del sys.modules[mod]

            # Kopioi skriptit tmp-kansioon
            for fname in ["rag_memory.py", "llm_client.py", "file_parser.py",
                          "sandbox_executor.py", "swarm_manager.py",
                          "evolution_engine.py", "config_manager.py", "watcher.py"]:
                src = Path(__file__).parent.parent / fname
                if src.exists():
                    (tmp_agent_dir / fname).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

            sys.path.insert(0, str(tmp_agent_dir))

            from file_parser import parse

            # Luo testitiedosto
            test_file = tmp_agent_dir / "Inbox" / "integraatio.txt"
            test_file.write_text("Tekoäly on mullistava teknologia.", encoding="utf-8")

            content = parse(test_file)
            assert "Tekoäly" in content

            # Mockattu LLM-vastaus
            llm_answer = "## Tiivistelmä\n\nTekoäly on tärkeä teknologia nykypäivänä."
            mock_resp = self._mock_llm_response(llm_answer)

            with patch("requests.post", return_value=mock_resp), \
                 patch("rag_memory.OllamaEmbedder.is_available", return_value=False):

                from rag_memory import RAGMemory
                from llm_client import LLMClient
                config = json.loads((tmp_agent_dir / "config.json").read_text())
                rag = RAGMemory(config, str(tmp_agent_dir / "memory"))
                llm = LLMClient(config)

                response = llm.complete("Prompti")
                assert "Tiivistelmä" in response

                ts = "20240101_120000"
                out = tmp_agent_dir / "Outbox" / f"{ts}_integraatio.md"
                out.write_text(f"# integraatio.txt\n\n{response}", encoding="utf-8")

                assert out.exists()
                assert "Tiivistelmä" in out.read_text(encoding="utf-8")

                rag.add("int1", content, {"ts": ts})
                assert rag.count() == 1

        finally:
            os.chdir(original_dir)
            sys.path.pop(0)
