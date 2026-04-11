"""Web-UI: polun turvallisuus ja valinnainen AGENTDIR_UI_SECRET."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_safe_file_in_root_ok_and_blocks_traversal(tmp_path: Path):
    from ui_routes import safe_file_in_root

    (tmp_path / "Inbox").mkdir()
    (tmp_path / "Inbox" / "ok.txt").write_text("hello", encoding="utf-8")
    p = safe_file_in_root(tmp_path, "Inbox", "ok.txt")
    assert p.read_text(encoding="utf-8") == "hello"

    with pytest.raises(HTTPException) as exc:
        safe_file_in_root(tmp_path, "Inbox", "..\\..\\windows\\win.ini")
    assert exc.value.status_code == 400

    with pytest.raises(HTTPException):
        safe_file_in_root(tmp_path, "Inbox", "../ok.txt")


def test_ui_requires_secret_header_when_env_set(monkeypatch):
    monkeypatch.setenv("AGENTDIR_UI_SECRET", "test-secret-key")
    from ui_routes import register_ui

    app = FastAPI()
    register_ui(app)
    client = TestClient(app)
    assert client.get("/ui/").status_code == 401
    r = client.get("/ui/", headers={"X-AgentDir-Key": "test-secret-key"})
    assert r.status_code == 200
    assert "Inbox" in r.text or "Outbox" in r.text


def test_ui_no_secret_allows_local_dashboard():
    from ui_routes import register_ui

    app = FastAPI()
    register_ui(app)
    client = TestClient(app)
    r = client.get("/ui/")
    assert r.status_code == 200
