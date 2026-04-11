"""A2A: API-avain ja CORS (dynaaminen middleware)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _minimal_config() -> dict:
    return {
        "name": "TestAgent",
        "version": "1.0.0",
        "role": "Test",
        "llm": {
            "endpoint": "http://127.0.0.1:1/v1/chat/completions",
            "model": "dummy",
            "temperature": 0.1,
            "max_tokens": 10,
            "timeout": 1,
            "fallback_models": [],
        },
        "embedding": {"endpoint": "http://127.0.0.1:1/api/embed", "model": "dummy"},
        "prompt_templates": {"default": "x {context} {content}", "code": "x"},
        "rag": {"enabled": False, "n_results": 1, "max_context_chars": 100},
        "sandbox": {"enabled": False},
        "swarm": {"enabled": False},
        "evolution": {"enabled": False},
        "a2a": {
            "enabled": True,
            "port": 8080,
            "mdns_enabled": False,
            "rate_limit_per_minute": 100,
            "cors_origins": ["*"],
            "api_token": "",
        },
    }


def _write_layout(tmp: Path, cfg: dict) -> None:
    (tmp / "Inbox").mkdir(parents=True, exist_ok=True)
    (tmp / "Outbox").mkdir(parents=True, exist_ok=True)
    (tmp / "memory").mkdir(parents=True, exist_ok=True)
    (tmp / "config.json").write_text(json.dumps(cfg), encoding="utf-8")


@pytest.fixture
def server_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AGENTDIR_API_SECRET", raising=False)
    _write_layout(tmp_path, _minimal_config())
    sys.modules.pop("server", None)
    import server  # noqa: PLC0415

    return server.app


def test_post_task_without_api_token_when_not_configured(server_app):
    client = TestClient(server_app)
    r = client.post("/task", json={"task": "Hei", "from": "tester"})
    assert r.status_code == 200
    assert r.json().get("status") == "accepted"
    inbox_files = list((Path.cwd() / "Inbox").glob("*.md"))
    assert len(inbox_files) >= 1


def test_post_task_requires_header_when_agendir_api_secret(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENTDIR_API_SECRET", "only-me")
    _write_layout(tmp_path, _minimal_config())
    sys.modules.pop("server", None)
    import server  # noqa: PLC0415

    client = TestClient(server.app)
    bad = client.post("/task", json={"task": "x", "from": "y"})
    assert bad.status_code == 401
    ok = client.post(
        "/task",
        json={"task": "x", "from": "y"},
        headers={"X-AgentDir-Api-Key": "only-me"},
    )
    assert ok.status_code == 200


def test_cors_acao_on_get_status(server_app):
    client = TestClient(server_app)
    r = client.get("/status", headers={"Origin": "http://localhost:5173"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") in ("*", "http://localhost:5173")
