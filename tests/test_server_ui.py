"""Täysi server.app: Web-UI + SessionMiddleware + CORS -järjestys."""

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
        "ui": {"max_upload_mb": 10, "session_secret": "", "cookie_secure": False},
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
    monkeypatch.delenv("AGENTDIR_UI_SECRET", raising=False)
    _write_layout(tmp_path, _minimal_config())
    sys.modules.pop("server", None)
    import server  # noqa: PLC0415

    return server.app


def test_server_status_ok(server_app):
    assert TestClient(server_app).get("/status").status_code == 200


def test_status_public_and_ui_htmx_redirect_when_secret_set(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENTDIR_UI_SECRET", "ui-int")
    _write_layout(tmp_path, _minimal_config())
    sys.modules.pop("server", None)
    import server  # noqa: PLC0415

    client = TestClient(server.app)
    st = client.get("/status")
    assert st.status_code == 200
    r = client.get("/ui/partials/inbox-outbox", headers={"HX-Request": "true"})
    assert r.status_code == 401
    assert r.headers.get("HX-Redirect", "").startswith("/ui/login?next=")
