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
"""

from __future__ import annotations

import json
import logging
import socket
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("agentdir.server")

# Lataa config
_config_path = Path("config.json")
_config: dict = json.loads(_config_path.read_text(encoding="utf-8")) if _config_path.exists() else {}
_a2a_cfg = _config.get("a2a", {})
PORT = _a2a_cfg.get("port", 8080)
RATE_LIMIT = _a2a_cfg.get("rate_limit_per_minute", 60)

try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    raise RuntimeError("FastAPI puuttuu: pip install fastapi uvicorn[standard]")

app = FastAPI(title="AgentDir A2A", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiting ─────────────────────────────────────────────────────────────

_request_counts: dict[str, list[float]] = defaultdict(list)

def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    window = 60.0
    _request_counts[client_ip] = [t for t in _request_counts[client_ip] if now - t < window]
    if len(_request_counts[client_ip]) >= RATE_LIMIT:
        return False
    _request_counts[client_ip].append(now)
    return True


# ── Endpointit ────────────────────────────────────────────────────────────────

@app.get("/status")
async def status():
    return {
        "name": _config.get("name"),
        "role": _config.get("role"),
        "version": _config.get("version"),
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
        ev = EvolutionEngine(_config)
        return ev.get_stats()
    except Exception as e:
        return {"error": str(e)}


@app.post("/task")
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

    # Tallenna tehtävä Inboxiin (watcher poimii sen)
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


@app.post("/rag/query")
async def rag_query(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        n = int(data.get("n_results", 3))
    except Exception:
        raise HTTPException(400, "Virheellinen pyyntö")

    try:
        from rag_memory import RAGMemory
        rag = RAGMemory(_config)
        result = rag.query(query, n_results=n)
        return {"query": query, "result": result}
    except Exception as e:
        raise HTTPException(500, str(e))


# ── mDNS rekisteröinti ────────────────────────────────────────────────────────

def _register_mdns():
    if not _a2a_cfg.get("mdns_enabled", True):
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
            f"{_config.get('name', 'Agent')}._agentdir._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=PORT,
            properties={
                b"role": _config.get("role", "").encode(),
                b"version": _config.get("version", "1.0.0").encode(),
                b"swarm": b"true" if _config.get("swarm", {}).get("enabled") else b"false",
            },
        )
        zc.register_service(info)
        logger.info("🌐 mDNS rekisteröity: %s:%d", local_ip, PORT)

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
                    found.append({
                        "name": name.split(".")[0],
                        "role": info.properties.get(b"role", b"").decode(errors="ignore"),
                        "ip": socket.inet_ntoa(info.addresses[0]) if info.addresses else "?",
                        "port": info.port,
                    })
            def remove_service(self, *a): pass
            def update_service(self, *a): pass

        zc = Zeroconf()
        ServiceBrowser(zc, "_agentdir._tcp.local.", _Listener())
        time.sleep(2)
        zc.close()
        return {"agents": found, "count": len(found)}

    except ImportError:
        return {"agents": [], "error": "zeroconf ei asennettu"}
    except Exception as e:
        return {"agents": [], "error": str(e)}


# ── Käynnistys ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    threading.Thread(target=_register_mdns, daemon=True).start()
    print(f"🌐 A2A-serveri käynnissä → http://0.0.0.0:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
