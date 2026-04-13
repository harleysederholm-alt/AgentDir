"""Vaihe 1 (The Spark): AgentWatcher — Inbox-varaus ja loki."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def _minimal_watcher_config() -> dict:
    return {
        "name": "TestAgent",
        "version": "1.0.0",
        "role": "Testi",
        "language": "fi",
        "llm": {
            "endpoint": "http://127.0.0.1:1/v1/chat/completions",
            "model": "dummy",
            "temperature": 0.1,
            "max_tokens": 64,
            "timeout": 5,
            "fallback_models": [],
        },
        "embedding": {"endpoint": "http://127.0.0.1:1/api/embed", "model": "dummy"},
        "prompt_templates": {"default": "{role}\n{context}\n{content}", "code": "{role}\n{context}\n{content}"},
        "watchdog": {
            "supported_extensions": [".txt", ".md"],
            "debounce_seconds": 0,
            "ignore_patterns": [".*", "~*", "*.tmp", "*.swp"],
        },
        "rag": {"enabled": False, "n_results": 1, "max_context_chars": 100},
        "sandbox": {"enabled": False},
        "swarm": {"enabled": False},
        "evolution": {"enabled": False},
        "a2a": {"enabled": False, "port": 8080, "cors_origins": ["*"], "api_token": ""},
        "pdf": {"ocr_enabled": False},
    }


@pytest.fixture
def watcher_importable_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Tyhjä agenttihakemisto + config, jotta watcher.py voidaan importata."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "Inbox").mkdir()
    (tmp_path / "Outbox").mkdir()
    (tmp_path / "memory").mkdir()
    (tmp_path / "config.json").write_text(json.dumps(_minimal_watcher_config()), encoding="utf-8")
    for mod in ("watcher", "config_manager", "hooks"):
        sys.modules.pop(mod, None)
    import watcher  # noqa: PLC0415

    return tmp_path


def test_agent_watcher_try_claim_renames_md(watcher_importable_env: Path):
    from watcher import AgentWatcher

    inbox = watcher_importable_env / "Inbox"
    src = inbox / "tehtava.md"
    src.write_text("# Hello", encoding="utf-8")
    w = AgentWatcher(inbox)
    claimed = w.try_claim_file(src)
    assert claimed is not None
    assert claimed.name == "tehtava.processing.md"
    assert claimed.read_text(encoding="utf-8") == "# Hello"
    assert not src.exists()


def test_agent_watcher_already_processing_returns_same_path(watcher_importable_env: Path):
    from watcher import AgentWatcher

    inbox = watcher_importable_env / "Inbox"
    f = inbox / "x.processing.md"
    f.write_text("k", encoding="utf-8")
    w = AgentWatcher(inbox)
    out = w.try_claim_file(f)
    assert out == f.resolve()


def test_agent_watcher_log_new_task(caplog, watcher_importable_env: Path):
    from watcher import AgentWatcher

    caplog.set_level(logging.INFO, logger="agentdir.watcher")
    AgentWatcher(watcher_importable_env / "Inbox").log_new_task("foo.md")
    assert any("Uusi tehtävä havaittu: foo.md" in r.message for r in caplog.records)


def test_inbox_source_display_name_strips_processing(watcher_importable_env: Path):
    from watcher import _inbox_source_display_name

    p = watcher_importable_env / "Inbox" / "job.processing.md"
    assert _inbox_source_display_name(p) == "job.md"
