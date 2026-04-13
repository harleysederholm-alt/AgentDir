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

logger = logging.getLogger("agentdir.omninode")

class OmniNodeManager:
    def __init__(self, port: int = 8081):
        self.port = port
        self.nodes = []
        self.running = False
        
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
                        if ip and ip not in [n["ip"] for n in self.manager.nodes]:
                            self.manager.nodes.append({"name": name, "ip": ip, "port": info.port})
                            logger.info(f"[OmniNode] Yhdistetty uusi laite: {name} at {ip}:{info.port}")

                def remove_service(self, zc, type_, name):
                    self.manager.nodes = [n for n in self.manager.nodes if n["name"] != name]

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
            
    def execute_sharded_task(self, model: str, prompt: str) -> str:
        """Hajauta tehtävä ensimmäiselle vapaalle Nodelle."""
        if not self.nodes:
            raise Exception("Ei OmniNodeja saatavilla laiteverkossa.")
            
        import requests
        node = self.nodes[0]
        url = f"http://{node['ip']}:{node['port']}/v1/completions"
        try:
            logger.info(f"[OmniNode] Lähetetään tehtävä noottiin: {node['name']}")
            resp = requests.post(url, json={"model": model, "prompt": prompt}, timeout=60)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            logger.error(f"[OmniNode] {node['name']} yhteysvirhe: {e}")
            raise
