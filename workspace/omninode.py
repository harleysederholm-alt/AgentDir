"""
omninode.py — OmniNode v2: Real KV-cache sharding
Hajautettu laskenta USB-C ja WiFi -laitteiden yli.

Arkkitehtuuri:
  Master (localhost) ajaa mallin kerrokset 0-19
  USB-C  laite ajaa shardeja 20-39 (matala latenssi)
  WiFi   laite ajaa shardeja 40-59 (korkea kapasiteetti)

Protokolla:
  1. Discovery — etsi solmut (ADB, mDNS, staattinen config)
  2. Handshake — kysy solmun resursseja (RAM, NPU, akku)
  3. Assign — kohdenna KV-kerrokset solmuille
  4. Health — tarkkaile solmujen tilaa ja reblalansoi
"""
from __future__ import annotations

import json
import logging
import socket
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("agentdir.omninode")


@dataclass
class NodeCapabilities:
    """Solmun resurssit ja kyvykkyydet."""
    ram_mb: int = 0
    npu_available: bool = False
    battery_pct: int = 100
    max_layers: int = 20
    latency_ms: float = 0.0


@dataclass
class ComputeNode:
    """Yksi laskentasolmu parvessa."""
    id: str
    type: str  # "master", "usb", "wifi", "static"
    host: str  # IP tai hostname
    port: int = 5001
    status: str = "offline"  # "online", "offline", "busy", "error"
    capabilities: NodeCapabilities = field(default_factory=NodeCapabilities)
    assigned_layers: tuple[int, int] = (0, 0)  # (start, end) kerrokset
    last_heartbeat: float = 0.0


class OmniNode:
    """
    OmniNode v2: Hajautettu KV-cache sharding.

    Tukee:
      - USB-C (ADB reverse port forward, matala latenssi)
      - WiFi  (TCP socket, suuri kapasiteetti)
      - Staattinen konfiguraatio (!_SOVEREIGN.md)
      - Automaattinen failover ja rebalansointi
    """

    CONFIG_KEY = "omninode"
    HEARTBEAT_INTERVAL = 10  # sekuntia
    LAYER_TOTAL = 60  # Tyypillinen 7B-mallin kerrosmäärä

    def __init__(self, config_path: str = "config.json") -> None:
        self.nodes: list[ComputeNode] = []
        self._config_path = Path(config_path)
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False

        # Master on aina mukana
        self.nodes.append(ComputeNode(
            id="localhost",
            type="master",
            host="127.0.0.1",
            status="online",
            capabilities=NodeCapabilities(
                ram_mb=self._get_local_ram(),
                max_layers=self.LAYER_TOTAL,
            ),
            assigned_layers=(0, self.LAYER_TOTAL),
        ))

        # Etsi lisäsolmut
        self._discover_all()

    # ── Discovery ────────────────────────────────────────────────────────

    def _discover_all(self) -> None:
        """Etsi kaikki saatavilla olevat solmut."""
        self._discover_adb()
        self._discover_static_config()
        self._discover_mdns()
        self._assign_layers()

    def _discover_adb(self) -> None:
        """Etsi USB-C -laitteet ADB:n kautta."""
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    device_id = parts[0]
                    # Tarkista ettei jo listalla
                    if any(n.id == device_id for n in self.nodes):
                        continue

                    # Kysy laitteen RAM
                    ram = self._get_adb_ram(device_id)

                    node = ComputeNode(
                        id=device_id,
                        type="usb",
                        host=device_id,
                        status="online",
                        capabilities=NodeCapabilities(
                            ram_mb=ram,
                            npu_available=True,
                            max_layers=20,
                            latency_ms=1.0,  # USB-C on nopea
                        ),
                    )
                    self.nodes.append(node)
                    logger.info("USB-C solmu loytyi: %s (RAM %dMB)", device_id, ram)

                    # Aseta ADB port forward KV-cache -shardingille
                    self._setup_adb_forward(device_id)

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass  # ADB ei saatavilla

    def _get_adb_ram(self, device_id: str) -> int:
        """Kysy laitteen RAM ADB:n kautta."""
        try:
            result = subprocess.run(
                ["adb", "-s", device_id, "shell", "cat", "/proc/meminfo"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines():
                if line.startswith("MemTotal"):
                    # "MemTotal:     1234567 kB"
                    kb = int(line.split()[1])
                    return kb // 1024
        except Exception:
            pass
        return 4096  # Oletus 4GB

    def _setup_adb_forward(self, device_id: str) -> bool:
        """Aseta ADB reverse port forward KV-cache -liikenteelle."""
        try:
            subprocess.run(
                ["adb", "-s", device_id, "reverse",
                 "tcp:5001", "tcp:5001"],
                capture_output=True, timeout=5,
            )
            logger.info("ADB port forward asetettu: %s:5001", device_id)
            return True
        except Exception as e:
            logger.warning("ADB forward epaonnistui (%s): %s", device_id, e)
            return False

    def _discover_static_config(self) -> None:
        """Lue staattisesti konfiguroidut solmut."""
        if not self._config_path.exists():
            return
        try:
            config = json.loads(
                self._config_path.read_text(encoding="utf-8")
            )
            static_nodes = config.get(self.CONFIG_KEY, {}).get("nodes", [])
            for n in static_nodes:
                if any(node.id == n.get("id") for node in self.nodes):
                    continue
                node = ComputeNode(
                    id=n["id"],
                    type=n.get("type", "wifi"),
                    host=n.get("host", n["id"]),
                    port=n.get("port", 5001),
                    status="offline",  # Tarkistetaan myohemmin
                    capabilities=NodeCapabilities(
                        ram_mb=n.get("ram_mb", 4096),
                        max_layers=n.get("max_layers", 20),
                    ),
                )
                # Tarkista onko saavutettavissa
                if self._ping_node(node):
                    node.status = "online"
                self.nodes.append(node)
        except Exception as e:
            logger.warning("Staattisten solmujen luku epaonnistui: %s", e)

    def _discover_mdns(self) -> None:
        """Etsi WiFi-solmut mDNS-palveluna (zeroconf)."""
        try:
            from zeroconf import ServiceBrowser, Zeroconf

            class _Listener:
                def __init__(self, parent: OmniNode):
                    self.parent = parent

                def add_service(self, zc, type_, name):
                    info = zc.get_service_info(type_, name)
                    if info and info.addresses:
                        host = socket.inet_ntoa(info.addresses[0])
                        port = info.port or 5001
                        node_id = f"mdns_{name.split('.')[0]}"
                        if not any(n.id == node_id for n in self.parent.nodes):
                            node = ComputeNode(
                                id=node_id,
                                type="wifi",
                                host=host,
                                port=port,
                                status="online",
                                capabilities=NodeCapabilities(
                                    ram_mb=4096, max_layers=20,
                                    latency_ms=5.0,
                                ),
                            )
                            self.parent.nodes.append(node)
                            logger.info("mDNS solmu: %s @ %s:%d", node_id, host, port)

                def remove_service(self, *_):
                    pass

                def update_service(self, *_):
                    pass

            zc = Zeroconf()
            ServiceBrowser(zc, "_agentdir._tcp.local.", _Listener(self))
            time.sleep(2)  # Odota vastauksia
            zc.close()
        except ImportError:
            pass  # zeroconf ei asennettu
        except Exception as e:
            logger.debug("mDNS discovery epaonnistui: %s", e)

    # ── Layer Assignment ─────────────────────────────────────────────────

    def _assign_layers(self) -> None:
        """
        Kohdenna mallin kerrokset solmuille painotetun RAM:n perusteella.

        Master saa aina layers 0-N (alkukerrokset = vähemmän KV-cachea).
        USB-C solmut seuraavaksi (matala latenssi).
        WiFi solmut viimeisenä (korkea latenssi mutta suuri kapasiteetti).
        """
        online = [n for n in self.nodes if n.status == "online"]
        if len(online) <= 1:
            # Vain master — kaikki kerrokset sille
            self.nodes[0].assigned_layers = (0, self.LAYER_TOTAL)
            return

        # Laske kokonais-RAM ja jaa suhteellisesti
        total_ram = sum(n.capabilities.ram_mb for n in online)
        if total_ram == 0:
            return

        layer_cursor = 0
        for node in online:
            share = node.capabilities.ram_mb / total_ram
            layer_count = max(1, int(self.LAYER_TOTAL * share))
            node.assigned_layers = (layer_cursor, layer_cursor + layer_count)
            layer_cursor += layer_count

        # Varmista etta kaikki kerrokset on kohdistettu
        online[-1].assigned_layers = (
            online[-1].assigned_layers[0], self.LAYER_TOTAL
        )

        for node in online:
            logger.info(
                "Kerrokset %d-%d -> %s (%s)",
                node.assigned_layers[0], node.assigned_layers[1],
                node.id, node.type,
            )

    # ── Health Monitoring ────────────────────────────────────────────────

    def start_monitor(self) -> None:
        """Kaynnista taustasäie joka tarkkailee solmujen tilaa."""
        if self._running:
            return
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True
        )
        self._monitor_thread.start()

    def stop_monitor(self) -> None:
        """Pysayta terveystarkkailija."""
        self._running = False

    def _monitor_loop(self) -> None:
        """Tarkista solmujen tila saeannollisesti ja rebalansoi tarvittaessa."""
        while self._running:
            changed = False
            for node in self.nodes:
                if node.type == "master":
                    continue
                was_online = node.status == "online"
                is_online = self._ping_node(node)
                node.status = "online" if is_online else "offline"
                node.last_heartbeat = time.time() if is_online else node.last_heartbeat
                if was_online != is_online:
                    changed = True
                    logger.info(
                        "Solmu %s tila muuttui: %s -> %s",
                        node.id,
                        "online" if was_online else "offline",
                        node.status,
                    )
            if changed:
                self._assign_layers()
            time.sleep(self.HEARTBEAT_INTERVAL)

    def _ping_node(self, node: ComputeNode) -> bool:
        """Tarkista onko solmu saavutettavissa (TCP-yhteys)."""
        try:
            with socket.create_connection(
                (node.host, node.port), timeout=2
            ):
                return True
        except (ConnectionRefusedError, OSError, socket.timeout):
            return False

    # ── KV-cache Sharding API ────────────────────────────────────────────

    def get_shard_plan(self) -> list[dict]:
        """
        Palauta KV-cache sharding -suunnitelma kaikille solmuille.
        Käytetään LLM-inferenssimoottorin konfigurointiin.
        """
        plan = []
        for node in self.nodes:
            if node.status != "online":
                continue
            plan.append({
                "node_id": node.id,
                "type": node.type,
                "host": node.host,
                "port": node.port,
                "layers": list(range(
                    node.assigned_layers[0], node.assigned_layers[1]
                )),
                "ram_mb": node.capabilities.ram_mb,
                "latency_ms": node.capabilities.latency_ms,
            })
        return plan

    def get_node_for_layer(self, layer: int) -> Optional[ComputeNode]:
        """Etsi solmu jolle tietty kerros on kohdistettu."""
        for node in self.nodes:
            if (node.status == "online"
                    and node.assigned_layers[0] <= layer < node.assigned_layers[1]):
                return node
        return self.nodes[0]  # Fallback: master

    # ── Status & Utility ─────────────────────────────────────────────────

    def _get_local_ram(self) -> int:
        """Hae lokaalin koneen RAM megabittiesina."""
        try:
            import psutil
            return int(psutil.virtual_memory().total / (1024 * 1024))
        except ImportError:
            pass
        # Fallback: Windows
        try:
            result = subprocess.run(
                ["wmic", "computersystem", "get", "totalphysicalmemory"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.isdigit():
                    return int(line) // (1024 * 1024)
        except Exception:
            pass
        return 16384  # Oletus 16GB

    def get_available_vram(self) -> dict[str, str]:
        """Palauta arvio käytettävissä olevasta muistista per solmu."""
        vram: dict[str, str] = {}
        for node in self.nodes:
            status = f"{node.capabilities.ram_mb}MB"
            if node.capabilities.npu_available:
                status += "+NPU"
            vram[node.id] = status
        return vram

    def status(self) -> str:
        """Tulosta parven koko tila."""
        online = sum(1 for n in self.nodes if n.status == "online")
        total = len(self.nodes)
        lines = [f"  OmniNode v2 Swarm -- {online}/{total} solmu(a) online:"]
        for n in self.nodes:
            layers = f"L{n.assigned_layers[0]}-{n.assigned_layers[1]}"
            ram = f"{n.capabilities.ram_mb}MB"
            lines.append(
                f"    [{n.status.upper():7s}] {n.id:20s} "
                f"({n.type:6s}) {layers:8s} {ram}"
            )
        return "\n".join(lines)

    def to_dict(self) -> list[dict]:
        """Palauta parven tila dict-listana (serialisoitava)."""
        return [
            {
                "id": n.id,
                "type": n.type,
                "host": n.host,
                "port": n.port,
                "status": n.status,
                "ram_mb": n.capabilities.ram_mb,
                "layers": n.assigned_layers,
                "npu": n.capabilities.npu_available,
            }
            for n in self.nodes
        ]
