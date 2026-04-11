"""
AgentDir – kevyt web-UI (FastAPI + Jinja2).
Listaa Inbox/Outbox, näyttää tiedoston sisällön turvallisella polulla.
Valinnainen: ympäristömuuttuja AGENTDIR_UI_SECRET + otsikko X-AgentDir-Key.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logger = logging.getLogger("agentdir.ui")

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"

ALLOWED_FOLDERS = frozenset({"Inbox", "Outbox"})


def _ui_secret() -> str:
    return os.environ.get("AGENTDIR_UI_SECRET", "").strip()


async def require_ui_key(request: Request) -> None:
    secret = _ui_secret()
    if not secret:
        return
    if request.headers.get("X-AgentDir-Key", "") != secret:
        raise HTTPException(
            status_code=401,
            detail="Aseta otsikko X-AgentDir-Key samaan arvoon kuin AGENTDIR_UI_SECRET.",
        )


def _templates() -> Jinja2Templates:
    return Jinja2Templates(directory=str(ROOT / "web" / "templates"))


router = APIRouter(prefix="/ui", tags=["ui"], dependencies=[Depends(require_ui_key)])


def safe_file_in_root(root: Path, folder: str, filename: str) -> Path:
    """Testattava: yksi tiedosto Inbox/ tai Outbox/ alla (ei path traversal)."""
    if folder not in ALLOWED_FOLDERS:
        raise HTTPException(400, "Virheellinen kansio")
    if not filename or filename in (".", ".."):
        raise HTTPException(400, "Virheellinen tiedostonimi")
    if "/" in filename or "\\" in filename or ".." in filename or filename.startswith("."):
        raise HTTPException(400, "Virheellinen tiedostonimi")
    base = (root / folder).resolve()
    target = (root / folder / filename).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        raise HTTPException(404, "Ei löydy")
    if not target.is_file():
        raise HTTPException(404, "Ei tiedostoa")
    return target


def _load_config() -> dict:
    p = ROOT / "config.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _safe_file_path(folder: str, filename: str) -> Path:
    return safe_file_in_root(ROOT, folder, filename)


def _list_dir(folder: str, limit: int = 200) -> list[dict]:
    d = ROOT / folder
    if not d.is_dir():
        return []
    rows: list[dict] = []
    for p in sorted(d.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if not p.is_file() or p.name == ".gitkeep":
            continue
        st = p.stat()
        rows.append(
            {
                "name": p.name,
                "size": st.st_size,
                "mtime": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "href": f"/ui/{folder.lower()}/{quote(p.name, safe='')}",
            }
        )
        if len(rows) >= limit:
            break
    return rows


def _rag_count(config: dict) -> int:
    try:
        from rag_memory import RAGMemory

        rag = RAGMemory(config, memory_path=str(ROOT / "memory"))
        return rag.count()
    except Exception as e:
        logger.warning("RAG count epäonnistui: %s", e)
        return -1


def _evo_stats(config: dict) -> dict:
    try:
        from evolution_engine import EvolutionEngine

        ev = EvolutionEngine(config, str(ROOT / "config.json"))
        return ev.get_stats()
    except Exception as e:
        logger.warning("Evolution stats epäonnistui: %s", e)
        return {"total_tasks": 0, "success_rate": 0.0, "prompt_version": "?"}


@router.get("/", response_class=HTMLResponse)
async def ui_dashboard(request: Request):
    config = _load_config()
    ctx = {
        "request": request,
        "agent_name": config.get("name", "Agent"),
        "agent_role": config.get("role", ""),
        "inbox_files": _list_dir("Inbox"),
        "outbox_files": _list_dir("Outbox"),
        "rag_count": _rag_count(config),
        "evo": _evo_stats(config),
        "ui_secret_set": bool(_ui_secret()),
    }
    return _templates().TemplateResponse(request, "dashboard.html", ctx)


def _ctx_file_view(folder: str, filename: str, content: str) -> dict:
    cfg = _load_config()
    return {
        "agent_name": cfg.get("name", "Agent"),
        "agent_role": cfg.get("role", ""),
        "folder": folder,
        "filename": filename,
        "content": content,
    }


@router.get("/inbox/{filename}", response_class=HTMLResponse)
async def ui_inbox_file(request: Request, filename: str):
    fn = unquote(filename)
    if "/" in fn or "\\" in fn or ".." in fn:
        raise HTTPException(400, "Virheellinen nimi")
    path = _safe_file_path("Inbox", fn)
    text = path.read_text(encoding="utf-8", errors="replace")
    body = text[:500_000] + ("\n\n… (katkaistu)" if len(text) > 500_000 else "")
    ctx = {"request": request, **_ctx_file_view("Inbox", fn, body)}
    return _templates().TemplateResponse(request, "file_view.html", ctx)


@router.get("/outbox/{filename}", response_class=HTMLResponse)
async def ui_outbox_file(request: Request, filename: str):
    fn = unquote(filename)
    if "/" in fn or "\\" in fn or ".." in fn:
        raise HTTPException(400, "Virheellinen nimi")
    path = _safe_file_path("Outbox", fn)
    text = path.read_text(encoding="utf-8", errors="replace")
    body = text[:500_000] + ("\n\n… (katkaistu)" if len(text) > 500_000 else "")
    ctx = {"request": request, **_ctx_file_view("Outbox", fn, body)}
    return _templates().TemplateResponse(request, "file_view.html", ctx)


def register_ui(app) -> None:
    """Liitä staattiset tiedostot, juuriredirect ja UI-router."""
    static_dir = WEB_DIR / "static"
    if static_dir.is_dir() and not getattr(app.state, "agentdir_static_mounted", False):
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        app.state.agentdir_static_mounted = True

    if not getattr(app.state, "agentdir_ui_registered", False):

        @app.get("/", include_in_schema=False, dependencies=[Depends(require_ui_key)])
        async def root_redirect():
            return RedirectResponse(url="/ui/", status_code=302)

        app.include_router(router)
        app.state.agentdir_ui_registered = True
        logger.info("Web-UI: / ja /ui/ (AGENTDIR_UI_SECRET=%s)", "asetettu" if _ui_secret() else "ei käytössä")
