"""
AgentDir – kevyt web-UI (FastAPI + Jinja2).
Listaa Inbox/Outbox, näyttää tiedoston sisällön turvallisella polulla.

Tuotantokovennukset (istunto / HTMX):
- AGENTDIR_UI_SECRET päällä: GET + HX-Request ilman tunnistusta → 401 ja HX-Redirect
  /ui/login?next=… (HTMX-partial ei jää rikki).
- SessionMiddleware: https_only kun AGENTDIR_UI_COOKIE_SECURE=1 tai ui.cookie_secure.
- Onnistunut POST /ui/login: session.clear() ennen ui_ok (session fixation -torjunta).

Epäonnistuneet kirjautumiset: enintään UI_LOGIN_FAIL_MAX yritystä / IP /
UI_LOGIN_FAIL_WINDOW_SEC (in-memory; ei jaeta prosessien välillä).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import secrets
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.parse import quote, unquote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logger = logging.getLogger("agentdir.ui")

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"

ALLOWED_FOLDERS = frozenset({"Inbox", "Outbox"})
SESSION_UI_OK = "ui_ok"

# Epäonnistuneet POST /ui/login -yritykset per IP (in-memory; ei jaeta instanssien välillä).
UI_LOGIN_FAIL_WINDOW_SEC = 600.0  # 10 min
UI_LOGIN_FAIL_MAX = 5

_config_getter: Callable[[], dict] | None = None
_login_fail_lock = threading.Lock()
_login_fail_times: dict[str, list[float]] = {}


def set_ui_config_getter(fn: Callable[[], dict]) -> None:
    """server.py rekisteröi get_server_config, jotta UI näkee config-hot-reloadin."""
    global _config_getter
    _config_getter = fn


def _ui_secret() -> str:
    return os.environ.get("AGENTDIR_UI_SECRET", "").strip()


def _session_middleware_secret() -> str:
    """Istuntoevästeen allekirjoitus (vähintään 16 merkkiä)."""
    env = os.environ.get("AGENTDIR_SESSION_SECRET", "").strip()
    if len(env) >= 16:
        return env
    ui = _ui_secret()
    if ui:
        return hashlib.sha256(b"agentdir.session:" + ui.encode("utf-8")).hexdigest()
    try:
        if _config_getter:
            cfg = _config_getter()
            s = (cfg.get("ui", {}) or {}).get("session_secret", "")
            if isinstance(s, str) and len(s.strip()) >= 16:
                return s.strip()
    except Exception:
        pass
    return hashlib.sha256(b"agentdir.dev.session.key").hexdigest()


def _session_cookie_https_only() -> bool:
    """True → Starlette SessionMiddleware(https_only=True), eväste Secure.

    AGENTDIR_UI_COOKIE_SECURE=1 tai config ui.cookie_secure kun UI käytössä HTTPS:llä.
    """
    v = os.environ.get("AGENTDIR_UI_COOKIE_SECURE", "").strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    try:
        if _config_getter:
            cfg = _config_getter()
            sec = (cfg.get("ui", {}) or {}).get("cookie_secure")
            if sec is True:
                return True
            if isinstance(sec, str) and sec.strip().lower() in ("1", "true", "yes", "on"):
                return True
    except Exception:
        pass
    return False


def _client_ip(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _login_next_query(request: Request) -> str:
    """URL-koodattu polku+query loginin next=-parametriin."""
    raw = str(request.url.path) or "/ui/"
    if request.url.query:
        raw += "?" + str(request.url.query)
    return quote(raw, safe="")


def _hx_redirect_login_url(request: Request) -> str:
    """HTMX 401:n HX-Redirect-URL (paluu polulle kirjautumisen jälkeen)."""
    return f"/ui/login?next={_login_next_query(request)}"


def _log_ui_401(request: Request, reason: str) -> None:
    """Lokita Web-UI 401 (ei salasanoja, ei otsikkosisältöjä)."""
    logger.warning(
        "Web-UI 401 %s %s ip=%s (%s)",
        request.method,
        request.url.path,
        _client_ip(request),
        reason,
    )


def _login_rate_check_or_raise(request: Request) -> None:
    if not _ui_secret():
        return
    ip = _client_ip(request)
    now = time.monotonic()
    with _login_fail_lock:
        seq = _login_fail_times.setdefault(ip, [])
        seq[:] = [t for t in seq if now - t < UI_LOGIN_FAIL_WINDOW_SEC]
        if len(seq) >= UI_LOGIN_FAIL_MAX:
            logger.warning("Web-UI login rate limited ip=%s", ip)
            raise HTTPException(
                status_code=429,
                detail="Liikaa epäonnistuneita kirjautumisyrityksiä. Odota ja yritä uudelleen.",
            )


def _login_record_failure(request: Request) -> None:
    ip = _client_ip(request)
    now = time.monotonic()
    with _login_fail_lock:
        seq = _login_fail_times.setdefault(ip, [])
        seq[:] = [t for t in seq if now - t < UI_LOGIN_FAIL_WINDOW_SEC]
        seq.append(now)
    logger.warning("Epäonnistunut Web-UI-kirjautuminen ip=%s", ip)


def _login_clear_failures(request: Request) -> None:
    ip = _client_ip(request)
    with _login_fail_lock:
        _login_fail_times.pop(ip, None)


def _session_ui_ok(request: Request) -> bool:
    try:
        return request.session.get(SESSION_UI_OK) is True
    except Exception:
        return False


async def require_ui_key(request: Request) -> None:
    """Vaadi UI-tunnistus: X-AgentDir-Key, istunto (ui_ok) tai POST-lomakkeessa agentdir_key.

    GET ilman tunnistusta: HX-Request → 401 + HX-Redirect; text/html → 307 Location; muut → 401.
    """
    secret = _ui_secret()
    if not secret:
        return
    if request.headers.get("X-AgentDir-Key", "") == secret:
        return
    if _session_ui_ok(request):
        return
    if request.method == "GET":
        if request.headers.get("HX-Request", "").strip().lower() == "true":
            _log_ui_401(request, "htmx_no_session")
            raise HTTPException(
                status_code=401,
                detail="Kirjaudu /ui/login tai käytä otsikkoa X-AgentDir-Key.",
                headers={"HX-Redirect": _hx_redirect_login_url(request)},
            )
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            nxt = _login_next_query(request)
            raise HTTPException(
                status_code=307,
                headers={"Location": f"/ui/login?next={nxt}"},
            )
    _log_ui_401(request, "no_session_or_header")
    raise HTTPException(
        status_code=401,
        detail="Kirjaudu /ui/login tai käytä otsikkoa X-AgentDir-Key.",
    )


def _verify_ui_access(request: Request, form_key: str = "") -> None:
    """POST: X-AgentDir-Key, istunto tai lomake agentdir_key; HTMX → 401 + HX-Redirect."""
    secret = _ui_secret()
    if not secret:
        return
    if request.headers.get("X-AgentDir-Key", "") == secret:
        return
    if _session_ui_ok(request):
        return
    if request.method == "POST" and form_key and secrets.compare_digest(form_key, secret):
        return
    if request.headers.get("HX-Request", "").strip().lower() == "true":
        _log_ui_401(request, "htmx_post_no_auth")
        raise HTTPException(
            status_code=401,
            detail="Kirjaudu /ui/login tai lähetä agentdir_key-lomakekenttä.",
            headers={"HX-Redirect": "/ui/login"},
        )
    _log_ui_401(request, "post_no_auth")
    raise HTTPException(
        status_code=401,
        detail="Kirjaudu /ui/login tai lähetä agentdir_key-lomakekenttä.",
    )


def _templates() -> Jinja2Templates:
    return Jinja2Templates(directory=str(ROOT / "web" / "templates"))


router = APIRouter(prefix="/ui", tags=["ui"])


def _safe_internal_path(url: str) -> str:
    """Estä avoin uudelleenohjaus: vain polku joka alkaa / (ei //)."""
    u = (url or "/ui/").strip() or "/ui/"
    if not u.startswith("/") or u.startswith("//"):
        return "/ui/"
    return u


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def ui_login_get(
    request: Request,
    next: str = Query("", alias="next"),
    err: str = Query(""),
):
    if not _ui_secret():
        return RedirectResponse(url="/ui/", status_code=302)
    if _session_ui_ok(request):
        return RedirectResponse(url=_safe_internal_path(next), status_code=302)
    config = _load_config()
    return _templates().TemplateResponse(
        request,
        "login.html",
        {
            "request": request,
            "agent_name": config.get("name", "Agent"),
            "agent_role": config.get("role", ""),
            "next": _safe_internal_path(next or "/ui/"),
            "login_error": err == "1",
        },
    )


@router.post("/login", include_in_schema=False)
async def ui_login_post(request: Request, password: str = Form(""), next: str = Form("")):
    """Kirjaudu UI-salasanalla; onnistuessa tyhjennä istunto sitten ui_ok (session fixation)."""
    if not _ui_secret():
        return RedirectResponse(url="/ui/", status_code=303)
    dest = _safe_internal_path(next)
    if not password or not secrets.compare_digest(password.strip(), _ui_secret()):
        _login_rate_check_or_raise(request)
        _login_record_failure(request)
        q = quote(dest, safe="")
        return RedirectResponse(url=f"/ui/login?next={q}&err=1", status_code=303)
    try:
        request.session.clear()
    except Exception:
        pass
    # Uusi istuntosisältö kiinnityksen estämiseksi (allekirjoitettu eväste).
    request.session[SESSION_UI_OK] = True
    _login_clear_failures(request)
    return RedirectResponse(url=dest, status_code=303)


@router.post("/logout", include_in_schema=False)
async def ui_logout_post(request: Request):
    try:
        request.session.clear()
    except Exception:
        request.session.pop(SESSION_UI_OK, None)
    return RedirectResponse(url="/ui/login", status_code=303)


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
        "ui_secret_set": bool(_ui_secret()),
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
    """Liitä SessionMiddleware (agentdir_session), staattiset tiedostot, juuriredirect, UI-router.

    https_only tulee _session_cookie_https_only(); secret _session_middleware_secret().
    """
    if not getattr(app.state, "agentdir_session_mw", False):
        from starlette.middleware.sessions import SessionMiddleware

        app.add_middleware(
            SessionMiddleware,
            secret_key=_session_middleware_secret(),
            same_site="lax",
            https_only=_session_cookie_https_only(),
            max_age=14 * 24 * 3600,
            session_cookie="agentdir_session",
        )
        app.state.agentdir_session_mw = True

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
