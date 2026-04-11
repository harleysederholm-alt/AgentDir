"""
AgentDir – kevyt web-UI (FastAPI + Jinja2).
Listaa Inbox/Outbox, näyttää tiedoston sisällön turvallisella polulla.
Valinnainen: ympäristömuuttuja AGENTDIR_UI_SECRET + otsikko X-AgentDir-Key
(tai POST-lomakkeessa kenttä agentdir_key).
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.parse import quote, unquote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logger = logging.getLogger("agentdir.ui")

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"

ALLOWED_FOLDERS = frozenset({"Inbox", "Outbox"})

_config_getter: Callable[[], dict] | None = None


def set_ui_config_getter(fn: Callable[[], dict]) -> None:
    """server.py rekisteröi get_server_config, jotta UI näkee config-hot-reloadin."""
    global _config_getter
    _config_getter = fn


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


def _verify_ui_access(request: Request, form_key: str = "") -> None:
    """Sama kuin require_ui_key; POST-lomakkeelle voi antaa salasanan kentässä agentdir_key."""
    secret = _ui_secret()
    if not secret:
        return
    if request.headers.get("X-AgentDir-Key", "") == secret:
        return
    if request.method == "POST" and form_key == secret:
        return
    raise HTTPException(
        status_code=401,
        detail="Aseta X-AgentDir-Key tai lomakkeen kenttä agentdir_key (POST).",
    )


def _templates() -> Jinja2Templates:
    return Jinja2Templates(directory=str(ROOT / "web" / "templates"))


router = APIRouter(prefix="/ui", tags=["ui"])


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
    if _config_getter is not None:
        try:
            return _config_getter()
        except Exception:
            pass
    p = ROOT / "config.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _safe_file_path(folder: str, filename: str) -> Path:
    return safe_file_in_root(ROOT, folder, filename)


def _max_upload_bytes(cfg: dict) -> int:
    try:
        mb = int(cfg.get("ui", {}).get("max_upload_mb", 10))
    except Exception:
        mb = 10
    return max(1, mb) * 1024 * 1024


def _sanitize_upload_filename(name: str) -> str:
    base = Path(name).name
    base = re.sub(r"[^a-zA-Z0-9._-]+", "_", base).strip("._") or "upload"
    if base.startswith("."):
        base = "upload_" + base.lstrip(".")
    return base[:120]


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


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(require_ui_key)])
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


@router.get(
    "/partials/inbox-outbox",
    response_class=HTMLResponse,
    dependencies=[Depends(require_ui_key)],
    include_in_schema=False,
)
async def ui_inbox_outbox_partial(request: Request):
    """HTMX: Inbox-, Outbox- ja tilakortit ilman sivun täyttä uudelleenlatausta."""
    config = _load_config()
    ctx = {
        "request": request,
        "inbox_files": _list_dir("Inbox"),
        "outbox_files": _list_dir("Outbox"),
        "rag_count": _rag_count(config),
        "evo": _evo_stats(config),
        "ui_secret_set": bool(_ui_secret()),
    }
    return _templates().TemplateResponse(request, "partials/inbox_outbox.html", ctx)


@router.post("/submit", include_in_schema=False)
async def ui_submit_post(
    request: Request,
    text: str = Form(""),
    agentdir_key: str = Form(""),
    file: UploadFile | None = File(None),
):
    _verify_ui_access(request, agentdir_key)
    inbox = ROOT / "Inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    cfg = _load_config()
    max_bytes = _max_upload_bytes(cfg)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    to_write: list[tuple[str, bytes]] = []

    raw_text = (text or "").strip()
    if file is not None and getattr(file, "filename", None):
        data = await file.read()
        if len(data) > max_bytes:
            raise HTTPException(413, "Tiedosto liian suuri (katso config ui.max_upload_mb).")
        fname = _sanitize_upload_filename(file.filename)
        to_write.append((f"ui_{ts}_{fname}", data))

    if raw_text:
        to_write.append((f"ui_{ts}_task.md", f"# Tehtävä (Web-UI)\n\n{raw_text}\n".encode("utf-8")))

    if not to_write:
        raise HTTPException(400, "Anna teksti tai tiedosto.")

    for name, blob in to_write:
        (inbox / name).write_bytes(blob)

    return RedirectResponse(url="/ui/", status_code=303)


def _ctx_file_view(folder: str, filename: str, content: str) -> dict:
    cfg = _load_config()
    return {
        "agent_name": cfg.get("name", "Agent"),
        "agent_role": cfg.get("role", ""),
        "folder": folder,
        "filename": filename,
        "content": content,
    }


@router.get("/inbox/{filename}", response_class=HTMLResponse, dependencies=[Depends(require_ui_key)])
async def ui_inbox_file(request: Request, filename: str):
    fn = unquote(filename)
    if "/" in fn or "\\" in fn or ".." in fn:
        raise HTTPException(400, "Virheellinen nimi")
    path = _safe_file_path("Inbox", fn)
    text = path.read_text(encoding="utf-8", errors="replace")
    body = text[:500_000] + ("\n\n… (katkaistu)" if len(text) > 500_000 else "")
    ctx = {"request": request, **_ctx_file_view("Inbox", fn, body)}
    return _templates().TemplateResponse(request, "file_view.html", ctx)


@router.get("/outbox/{filename}", response_class=HTMLResponse, dependencies=[Depends(require_ui_key)])
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
