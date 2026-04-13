"""Vaiheet 2–4 (The Spark): LLM async, agent_core, evolution.log, Outbox/arkisto."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_core import (  # noqa: E402
    load_manifest,
    outbox_vastaus_path,
    resolve_agent_role,
)
from evolution_log import append_success_record  # noqa: E402


def test_resolve_agent_role_manifest_over_config():
    cfg = {"role": "ConfigRole"}
    man = {"role": "ManifestRole"}
    assert resolve_agent_role(cfg, man) == "ManifestRole"
    assert resolve_agent_role(cfg, {}) == "ConfigRole"
    assert resolve_agent_role({}, {}) == "Agent"


def test_outbox_vastaus_path_collision(tmp_path: Path):
    out = tmp_path / "Outbox"
    out.mkdir()
    (out / "vastaus_tehtava.md").write_text("x", encoding="utf-8")
    p = outbox_vastaus_path(out, "tehtava.md", "20260101_120000")
    assert p.name.startswith("vastaus_tehtava_")
    assert p.suffix == ".md"


def test_load_manifest_missing(tmp_path: Path):
    assert load_manifest(tmp_path) == {}


def test_append_success_record_jsonl(tmp_path: Path):
    append_success_record(
        tmp_path,
        task_size_bytes=42,
        model="m1",
        source_file="in.md",
        outbox_file="vastaus_in.md",
        status="success",
    )
    logf = tmp_path / "evolution.log"
    assert logf.is_file()
    line = logf.read_text(encoding="utf-8").strip().splitlines()[-1]
    rec = json.loads(line)
    assert rec["task_size_bytes"] == 42
    assert rec["model"] == "m1"
    assert rec["source_file"] == "in.md"
    assert rec["outbox_file"] == "vastaus_in.md"
    assert rec["status"] == "success"
    assert "timestamp" in rec


def test_llm_client_process_task_mocked():
    from llm_client import LLMClient  # noqa: E402

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "  Vastaus  "}}]}

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None

        async def post(self, *a, **k):
            return _Resp()

    cfg = {
        "llm": {
            "endpoint": "http://127.0.0.1:1/v1/chat/completions",
            "model": "test-model",
            "fallback_models": [],
            "timeout": 5,
        }
    }
    client = LLMClient(cfg)
    with patch("llm_client.httpx.AsyncClient", return_value=_Client()):
        out = asyncio.run(client.process_task("hei", "Rooli"))
    assert out == "Vastaus"
