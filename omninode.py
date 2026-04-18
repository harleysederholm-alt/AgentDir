"""
omninode.py — OmniNode Swarm router.

Shards LLM tasks across the two canonical AgentDir node classes:

    * **PC node**  — Gemma 4 E4B IT (Thinking) or any Ollama-served
      model on a desktop / workstation. Handles *heavy* cognition:
      full orchestrator pipeline, sandboxed code execution, synthesis.
    * **Mobile node** — Gemma 4 E2B IT (Thinking) on a phone / Pi / USB
      tethered edge device, reachable via WebSocket or mDNS. Handles
      *ingest*: background anchoring, short classification, chat replies.

Task-class routing (``execute_sharded_task(..., task_class=...)``):

    * ``"heavy"``  → prefer a node whose role is ``"pc"`` (desktop E4B).
    * ``"ingest"`` → prefer a node whose role is ``"mobile"`` (phone E2B).
    * ``"auto"``   → first available node (legacy v4.0 behaviour).

If no node matching the requested class is connected, the router falls
back to the first available node so the swarm is never starved on a
partially connected network.

Transports:

    * mDNS / Zeroconf on ``_omninode._tcp.local.`` — LAN discovery.
    * WebSocket — explicit pairing from PWA / mobile over
      ``server.py`` port 8080 (see ``docs/04-Architecture/API_SYMBIOSIS.md``).

TurboQuant (Google Research, arXiv 2504.19874) is on the roadmap for
the server-side inference path. Not plumbed here yet — tracked in
``SYSTEM_STATUS.md`` §3.
"""

import socket
import json
import logging
import threading
import time
import asyncio
from typing import Literal

logger = logging.getLogger("agentdir.omninode")

TaskClass = Literal["heavy", "ingest", "auto"]
NodeRole = Literal["pc", "mobile", "unknown"]


class OmniNodeManager:
    def __init__(self, port: int = 8081):
        self.port = port
        self.nodes = []  # dicts: 'ip'/'port' (mDNS) or 'websocket' (WS); all carry 'role'.
        self.running = False
        self._pending_results = {}
        
    def start_discovery(self):
        """Käynnistä Zeroconf-pohjainen laite-etsintä (mDNS)."""
        try:
            from zeroconf import Zeroconf, ServiceBrowser
            
            class NodeListener:
                def __init__(self, manager):
                    self.manager = manager
                    
                def add_service(self, zc, type_, name):
                    info = zc.get_service_info(type_, name)
                    if info:
                        ip = socket.inet_ntoa(info.addresses[0]) if info.addresses else None
                        if ip and not any(n.get("ip") == ip for n in self.manager.nodes):
                            # mDNS TXT record may advertise role=pc|mobile; default to "pc"
                            # because LAN-announced peers are usually desktops / workstations.
                            role_bytes = (info.properties or {}).get(b"role", b"pc")
                            role = role_bytes.decode(errors="ignore") or "pc"
                            if role not in ("pc", "mobile"):
                                role = "unknown"
                            self.manager.nodes.append({
                                "name": name,
                                "ip": ip,
                                "port": info.port,
                                "type": "mdns",
                                "role": role,
                            })
                            logger.info(
                                f"[OmniNode] Yhdistetty uusi laite (mDNS, role={role}): "
                                f"{name} at {ip}:{info.port}"
                            )

                def remove_service(self, zc, type_, name):
                    self.manager.nodes = [n for n in self.manager.nodes if n.get("name") != name]

                def update_service(self, *args):
                    pass
            
            self.zc = Zeroconf()
            self.browser = ServiceBrowser(self.zc, "_omninode._tcp.local.", NodeListener(self))
            self.running = True
            logger.info("OmniNode verkkohaku aktivoitu.")
        except ImportError:
            logger.warning("zeroconf-kirjasto uupuu, OmniNode discovery poistettu käytöstä.")
            
    def stop(self):
        if hasattr(self, 'zc'):
            self.zc.close()
            self.running = False
            
    def add_ws_node(
        self,
        websocket,
        name: str = "Mobile Node",
        role: NodeRole = "mobile",
    ):
        """Register a WebSocket-connected node.

        ``role`` determines which task classes the router prefers for this
        node. Default ``"mobile"`` matches the historical behaviour (PWA
        phones pairing in). Pass ``"pc"`` for a desktop peer paired over
        WebSocket instead of mDNS.
        """
        node = {"name": name, "websocket": websocket, "type": "ws", "role": role}
        self.nodes.append(node)
        logger.info(f"[OmniNode] Yhdistetty uusi laite (WebSocket, role={role}): {name}")
        return node
        
    def remove_ws_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
            logger.info(f"[OmniNode] Poistettu laite: {node.get('name')}")
            
    def handle_ws_result(self, task_id: str, result: str):
        if task_id in self._pending_results:
            self._pending_results[task_id].set_result(result)
            
    def _select_node(self, task_class: TaskClass) -> dict:
        """Pick a node whose role matches ``task_class``; fall back to first.

        Routing table::

            heavy  → pc       (Gemma 4 E4B on desktop / workstation)
            ingest → mobile   (Gemma 4 E2B on phone / Pi / tethered edge)
            auto   → first available node

        Falls back to the first connected node if no role match is found.
        """
        if not self.nodes:
            raise Exception("Ei OmniNodeja saatavilla laiteverkossa.")

        preferred_role: NodeRole | None
        if task_class == "heavy":
            preferred_role = "pc"
        elif task_class == "ingest":
            preferred_role = "mobile"
        else:
            preferred_role = None

        if preferred_role is not None:
            for n in self.nodes:
                if n.get("role") == preferred_role:
                    return n

        fallback = self.nodes[0]
        if preferred_role is not None:
            logger.info(
                "[OmniNode] task_class=%s haluaa role=%s, mutta sopivaa nodea ei löytynyt — "
                "fallback '%s' (role=%s)",
                task_class,
                preferred_role,
                fallback.get("name"),
                fallback.get("role", "unknown"),
            )
        return fallback

    async def execute_sharded_task(
        self,
        model: str,
        prompt: str,
        task_class: TaskClass = "auto",
    ) -> str:
        """Offload a task to a suitable OmniNode.

        ``task_class`` steers the router:
            * ``"heavy"``  — desktop PC (Gemma 4 E4B, full pipeline).
            * ``"ingest"`` — mobile phone (Gemma 4 E2B, background anchor).
            * ``"auto"``   — first available node.
        """
        node = self._select_node(task_class)
        logger.info(
            "[OmniNode] task_class=%s → node=%s (role=%s, transport=%s)",
            task_class,
            node.get("name"),
            node.get("role", "unknown"),
            node.get("type"),
        )
        
        if node["type"] == "ws":
            # Lähetä WebSocket
            import uuid
            task_id = str(uuid.uuid4())
            loop = asyncio.get_running_loop()
            future = loop.create_future()
            self._pending_results[task_id] = future
            
            try:
                await node["websocket"].send_json({
                    "type": "compute_request",
                    "task_id": task_id,
                    "model": model,
                    "prompt": prompt
                })
                # Odotetaan 60s
                result = await asyncio.wait_for(future, timeout=60.0)
                return result
            except Exception as e:
                logger.error(f"[OmniNode] {node['name']} WS yhteysvirhe: {e}")
                raise
            finally:
                self._pending_results.pop(task_id, None)
                
        else:
            # mDNS (REST) - fallback asyncio -> sync
            import requests
            url = f"http://{node['ip']}:{node['port']}/v1/completions"
            def _post():
                resp = requests.post(url, json={"model": model, "prompt": prompt}, timeout=60)
                resp.raise_for_status()
                return resp.json().get("response", "")
            try:
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(None, _post)
            except Exception as e:
                logger.error(f"[OmniNode] {node['name']} mDNS yhteysvirhe: {e}")
                raise

global_omni_manager = OmniNodeManager()
