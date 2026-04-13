"""
omninode.py - OmniNode Bridge (NPU Sharding)
Mahdollistaa raskaiden Llama3.2/Gemma4 taskien jakamisen lähiverkossa
oleville OmniNodeille (esim. USB tai WiFi kautta kytketty NPU).
"""

import socket
import json
import logging
import threading
import time
import asyncio

logger = logging.getLogger("agentdir.omninode")

class OmniNodeManager:
    def __init__(self, port: int = 8081):
        self.port = port
        self.nodes = [] # Contains dicts with either 'ip'/'port' (mDNS) or 'websocket' (WS)
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
                            self.manager.nodes.append({"name": name, "ip": ip, "port": info.port, "type": "mdns"})
                            logger.info(f"[OmniNode] Yhdistetty uusi laite (mDNS): {name} at {ip}:{info.port}")

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
            
    def add_ws_node(self, websocket, name="Mobile Node"):
        node = {"name": name, "websocket": websocket, "type": "ws"}
        self.nodes.append(node)
        logger.info(f"[OmniNode] Yhdistetty uusi laite (WebSocket): {name}")
        return node
        
    def remove_ws_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
            logger.info(f"[OmniNode] Poistettu laite: {node.get('name')}")
            
    def handle_ws_result(self, task_id: str, result: str):
        if task_id in self._pending_results:
            self._pending_results[task_id].set_result(result)
            
    async def execute_sharded_task(self, model: str, prompt: str) -> str:
        """Hajauta tehtävä ensimmäiselle vapaalle Nodelle."""
        if not self.nodes:
            raise Exception("Ei OmniNodeja saatavilla laiteverkossa.")
            
        node = self.nodes[0]
        logger.info(f"[OmniNode] Lähetetään tehtävä noottiin: {node['name']}")
        
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
