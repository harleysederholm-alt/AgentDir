"""
AgentDir – A2A Server (Agent-to-Agent)
FastAPI REST API + mDNS automaattirekisteröinti.

Endpointit:
  GET  /status      – Agentin tila
  GET  /manifest    – Julkiset kyvyt (A2A-discovery)
  GET  /discover    – Lista lokaaliverkon agenteista (mDNS)
  POST /task        – Vastaanota tehtävä toiselta agentilta
  POST /rag/query   – Hae tästä agentista semanttisesti
  GET  /stats       – Evolution-tilasto

Konfiguraatio: config_manager.ConfigManager + taustaseuranta (muutokset ilman täyttä uudelleenkäynnistystä).
Kuunneltava portti (a2a.port) luetaan käynnistyksessä; portin vaihto vaatii palvelimen uudelleenkäynnistyksen.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("agentdir.server")

# ── Konfiguraatio (hot-reload) ───────────────────────────────────────────────

_config_path = Path("config.json")


def _read_bind_port() -> int:
    if _config_path.exists():
        try:
            d = json.loads(_config_path.read_text(encoding="utf-8"))
            return int(d.get("a2a", {}).get("port", 8080))
        except Exception:
            pass
    return 8080


BIND_PORT = _read_bind_port()


class _EmptyConfigManager:
    """Kun config.json puuttuu — sama käyttäytyminen kuin aiemmin tyhjällä dictillä."""

    def all(self) -> dict[str, Any]:
        return {}


_server_cfg: Any = None


def _init_config_backend() -> Any:
    global _server_cfg
    if _server_cfg is not None:
        return _server_cfg
    if not _config_path.exists():
        logger.warning("config.json puuttuu → tyhjä konfiguraatio")
        _server_cfg = _EmptyConfigManager()
        return _server_cfg
    from config_manager import ConfigManager

    cm = ConfigManager(_config_path)

    def _on_change(data: dict) -> None:
        try:
            new_port = int(data.get("a2a", {}).get("port", 8080))
            if new_port != BIND_PORT:
                logger.info(
                    "config.json: a2a.port=%s (palvelin kuuntelee %s) — portin muutos vaatii uudelleenkäynnistyksen.",
                    new_port,
                    BIND_PORT,
                )
        except Exception:
            pass

    cm.on_change(_on_change)
    cm.watch(interval=3.0)
    _server_cfg = cm
    return _server_cfg


_init_config_backend()


def get_server_config() -> dict[str, Any]:
    """Tuorein config (thread-safe). Käytä reiteissä tämän sijaan moduulitason _config:ia."""
    return _server_cfg.all()


try:
    from fastapi import Depends, FastAPI, HTTPException, Request
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import Response
    import uvicorn
except ImportError:
    raise RuntimeError("FastAPI puuttuu: pip install fastapi uvicorn[standard]")

app = FastAPI(title="AgentDir A2A", version="1.0.0")


def _a2a_expected_api_token() -> str:
    env = os.environ.get("AGENTDIR_API_SECRET", "").strip()
    if env:
        return env
    return (get_server_config().get("a2a", {}) or {}).get("api_token", "").strip()


def _cors_origins_list() -> list[str]:
    """Lue a2a.cors_origins. API-tokenin kanssa '*' ei ole sallittu (tyhjä lista + varoitus)."""
    raw = get_server_config().get("a2a", {}).get("cors_origins", ["*"])
    if raw is None:
        origins = ["*"]
    elif isinstance(raw, str):
        origins = [raw] if raw.strip() else ["*"]
    elif isinstance(raw, list):
        origins = [str(x) for x in raw if str(x).strip()] or ["*"]
    else:
        origins = ["*"]

    if _a2a_expected_api_token() and any(str(o).strip() == "*" for o in origins):
        logger.warning(
            "A2A API -token on käytössä — a2a.cors_origins ei saa sisältää '*'. "
            "CORS poistettu kunnes lista on eksplisiittinen (esim. [\"https://app.example\"])."
        )
        return []
    return origins


class DynamicCORSMiddleware(BaseHTTPMiddleware):
    """CORS config.json:sta (a2a.cors_origins), päivittyy ilman uudelleenkäynnistystä."""

    async def dispatch(self, request: Request, call_next):
        origins = _cors_origins_list()
        origin = request.headers.get("origin") or ""
        allow_all = "*" in origins
        allowed_origin = "*" if allow_all else (origin if origin in origins else None)

        if request.method == "OPTIONS":
            hdrs: list[tuple[str, str]] = [
                ("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS"),
                (
                    "Access-Control-Allow-Headers",
                    request.headers.get("access-control-request-headers") or "*",
                ),
                ("Access-Control-Max-Age", "600"),
            ]
            if allowed_origin:
                hdrs.append(("Access-Control-Allow-Origin", allowed_origin))
            return Response(status_code=204, headers=hdrs)

        response = await call_next(request)
        if allowed_origin:
            response.headers["Access-Control-Allow-Origin"] = allowed_origin
        return response


app.add_middleware(DynamicCORSMiddleware)


def verify_a2a_api_key(request: Request) -> None:
    """Jos a2a.api_token tai AGENTDIR_API_SECRET on asetettu, vaadi otsikko tai Bearer."""
    expected = _a2a_expected_api_token()
    if not expected:
        return
    got = request.headers.get("X-AgentDir-Api-Key", "").strip()
    if not got:
        auth = request.headers.get("Authorization", "") or ""
        if auth.lower().startswith("bearer "):
            got = auth[7:].strip()
    if got != expected:
        raise HTTPException(
            status_code=401,
            detail="Vaaditaan X-AgentDir-Api-Key tai Authorization: Bearer (a2a.api_token / AGENTDIR_API_SECRET).",
        )

# ── Rate limiting ─────────────────────────────────────────────────────────────

_request_counts: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    window = 60.0
    cfg = get_server_config()
    limit = int(cfg.get("a2a", {}).get("rate_limit_per_minute", 60))
    _request_counts[client_ip] = [t for t in _request_counts[client_ip] if now - t < window]
    if len(_request_counts[client_ip]) >= limit:
        return False
    _request_counts[client_ip].append(now)
    return True


# ── Endpointit ────────────────────────────────────────────────────────────────


@app.get("/status")
async def status():
    """Julkinen valmiustarkistus (ei API-avainta) — Docker healthcheck ja monitorointi."""
    cfg = get_server_config()
    return {
        "name": cfg.get("name"),
        "role": cfg.get("role"),
        "version": cfg.get("version"),
        "status": "online",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/manifest")
async def get_manifest():
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        raise HTTPException(404, "manifest.json puuttuu")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


@app.get("/stats")
async def get_stats():
    try:
        from evolution_engine import EvolutionEngine

        cfg = get_server_config()
        cfg_p = str(_config_path.resolve()) if _config_path.exists() else "config.json"
        ev = EvolutionEngine(cfg, cfg_p)
        return ev.get_stats()
    except Exception as e:
        return {"error": str(e)}


@app.post("/task", dependencies=[Depends(verify_a2a_api_key)])
async def receive_task(request: Request):
    client_ip = request.client.host if request.client else "unknown"

    if not check_rate_limit(client_ip):
        raise HTTPException(429, "Rate limit ylitetty")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(400, "Virheellinen JSON")

    task = data.get("task", "")
    sender = data.get("from", "unknown")
    priority = data.get("priority", "normal")

    if not task:
        raise HTTPException(400, "Kenttä 'task' vaaditaan")

    logger.info("📨 A2A-tehtävä agentilta '%s': %s...", sender, task[:80])

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    inbox_file = Path("Inbox") / f"a2a_{ts}_from_{sender}.md"
    inbox_file.write_text(
        f"# A2A-tehtävä\n\n**Lähettäjä:** {sender}\n**Prioriteetti:** {priority}\n\n---\n\n{task}",
        encoding="utf-8",
    )

    return {
        "status": "accepted",
        "task_id": f"{ts}_from_{sender}",
        "message": "Tehtävä vastaanotettu ja lisätty jonoon",
    }


@app.post("/rag/query", dependencies=[Depends(verify_a2a_api_key)])
async def rag_query(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        n = int(data.get("n_results", 3))
    except Exception:
        raise HTTPException(400, "Virheellinen pyyntö")

    try:
        from rag_memory import RAGMemory

        rag = RAGMemory(get_server_config())
        result = rag.query(query, n_results=n)
        return {"query": query, "result": result}
    except Exception as e:
        raise HTTPException(500, str(e))


# ── mDNS rekisteröinti ────────────────────────────────────────────────────────


def _register_mdns():
    cfg = get_server_config()
    a2a = cfg.get("a2a", {})
    if not a2a.get("mdns_enabled", True):
        return
    try:
        from zeroconf import Zeroconf, ServiceInfo
    except ImportError:
        logger.warning("zeroconf puuttuu → mDNS ei käytössä. pip install zeroconf")
        return

    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        zc = Zeroconf()
        info = ServiceInfo(
            "_agentdir._tcp.local.",
            f"{cfg.get('name', 'Agent')}._agentdir._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=BIND_PORT,
            properties={
                b"role": cfg.get("role", "").encode(),
                b"version": cfg.get("version", "1.0.0").encode(),
                b"swarm": b"true" if cfg.get("swarm", {}).get("enabled") else b"false",
            },
        )
        zc.register_service(info)
        logger.info("🌐 mDNS rekisteröity: %s:%d", local_ip, BIND_PORT)

        while True:
            time.sleep(3600)

    except Exception as e:
        logger.warning("mDNS-rekisteröinti epäonnistui: %s", e)


@app.get("/discover")
async def discover():
    """Etsi lokaaliverkon AgentDir-agentit mDNS:llä."""
    try:
        from zeroconf import Zeroconf, ServiceBrowser

        found = []

        class _Listener:
            def add_service(self, zc, type_, name):
                info = zc.get_service_info(type_, name)
                if info:
                    found.append(
                        {
                            "name": name.split(".")[0],
                            "role": info.properties.get(b"role", b"").decode(errors="ignore"),
                            "ip": socket.inet_ntoa(info.addresses[0]) if info.addresses else "?",
                            "port": info.port,
                        }
                    )

            def remove_service(self, *a):
                pass

            def update_service(self, *a):
                pass

        zc = Zeroconf()
        ServiceBrowser(zc, "_agentdir._tcp.local.", _Listener())
        time.sleep(2)
        zc.close()
        return {"agents": found, "count": len(found)}

    except ImportError:
        return {"agents": [], "error": "zeroconf ei asennettu"}
    except Exception as e:
        return {"agents": [], "error": str(e)}


# ── Web-UI (dashboard: Inbox / Outbox) ────────────────────────────────────────
try:
    from ui_routes import register_ui, set_ui_config_getter

    set_ui_config_getter(get_server_config)
    register_ui(app)
except Exception as e:
    logger.warning("Web-UI ei käynnistynyt: %s", e)


# ── Käynnistys ────────────────────────────────────────────────────────────────


def main() -> None:
    threading.Thread(target=_register_mdns, daemon=True).start()
    print(f"🌐 A2A-serveri käynnissä → http://0.0.0.0:{BIND_PORT}")
    print(f"   Web-UI → http://127.0.0.1:{BIND_PORT}/ui/  (OpenAPI: /docs)")
    print("   config.json päivittyy taustalla (~3 s); portin vaihto vaatii uudelleenkäynnistyksen.")
    uvicorn.run(app, host="0.0.0.0", port=BIND_PORT, log_level="warning")


if __name__ == "__main__":
    main()
