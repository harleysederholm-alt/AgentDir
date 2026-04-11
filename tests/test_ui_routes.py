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


def test_ui_submit_writes_task_to_inbox(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("AGENTDIR_UI_SECRET", raising=False)
    (tmp_path / "Inbox").mkdir(parents=True)
    (tmp_path / "Outbox").mkdir(parents=True)
    (tmp_path / "memory").mkdir(parents=True)
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")

    import ui_routes

    monkeypatch.setattr(ui_routes, "ROOT", tmp_path)

    from ui_routes import register_ui

    app = FastAPI()
    register_ui(app)
    client = TestClient(app)
    r = client.post("/ui/submit", data={"text": "Tehtävä testistä"}, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers.get("location", "").endswith("/ui/")
    matches = list((tmp_path / "Inbox").glob("ui_*_task.md"))
    assert len(matches) == 1
    assert "Tehtävä testistä" in matches[0].read_text(encoding="utf-8")


def test_ui_submit_requires_form_key_when_secret_set(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AGENTDIR_UI_SECRET", "sekret")
    (tmp_path / "Inbox").mkdir(parents=True)
    (tmp_path / "Outbox").mkdir(parents=True)
    (tmp_path / "memory").mkdir(parents=True)
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")

    import ui_routes

    monkeypatch.setattr(ui_routes, "ROOT", tmp_path)

    from ui_routes import register_ui

    app = FastAPI()
    register_ui(app)
    client = TestClient(app)
    bad = client.post("/ui/submit", data={"text": "x"}, follow_redirects=False)
    assert bad.status_code == 401
    ok = client.post(
        "/ui/submit",
        data={"text": "x", "agentdir_key": "sekret"},
        follow_redirects=False,
    )
    assert ok.status_code == 303


def test_ui_partials_inbox_outbox(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("AGENTDIR_UI_SECRET", raising=False)
    (tmp_path / "Inbox").mkdir(parents=True)
    (tmp_path / "Outbox").mkdir(parents=True)
    (tmp_path / "memory").mkdir(parents=True)
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "Inbox" / "a.txt").write_text("x", encoding="utf-8")

    import shutil

    src_tpl = Path(__file__).resolve().parent.parent / "web" / "templates"
    dst_tpl = tmp_path / "web" / "templates"
    shutil.copytree(src_tpl, dst_tpl, dirs_exist_ok=True)

    import ui_routes

    monkeypatch.setattr(ui_routes, "ROOT", tmp_path)

    from ui_routes import register_ui

    app = FastAPI()
    register_ui(app)
    client = TestClient(app)
    r = client.get("/ui/partials/inbox-outbox")
    assert r.status_code == 200
    assert "Inbox" in r.text
    assert "a.txt" in r.text
