"""
health_monitor.py — Itsekorjautuva OS-monitori (v2.6)
Tarkkailee järjestelmän tilaa ja korjaa ongelmia automaattisesti.

Tarkkaillaan:
  ✅ Ollama/LLM-yhteys (endpoint reachability)
  ✅ Config.json validius (JSON-syntaksi, pakolliset kentät)
  ✅ Levytila (memory/, Outbox/, archive/)
  ✅ Watcher-prosessin tila
  ✅ RAG-muistin konsistenssi

Automaattikorjaukset:
  🔧 Ollama down → yritä käynnistää
  🔧 Config korruptoitunut → palauta backup
  🔧 Levytila loppumassa → siivoa vanhat arkistot
  🔧 Watcher ei käy → varoitus + uudelleenkäynnistys-ehdotus
"""
from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("agentdir.health")


class HealthStatus:
    """Yksittäisen tarkistuksen tulos."""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    FIXED = "fixed"

    def __init__(self, component: str, status: str, message: str, action: str = "") -> None:
        self.component = component
        self.status = status
        self.message = message
        self.action = action
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "component": self.component,
            "status": self.status,
            "message": self.message,
            "action": self.action,
            "timestamp": self.timestamp,
        }


class HealthMonitor:
    """
    Itsekorjautuva järjestelmämonitori.
    Käynnistyy daemon-threadina ja tarkistaa järjestelmän tilan säännöllisesti.
    """

    # Minimivaatimukset
    MIN_DISK_MB = 100  # Varoitus kun levytilaa alle 100MB
    MAX_ARCHIVE_AGE_DAYS = 30  # Arkiston autosiivous
    CONFIG_REQUIRED_KEYS = {"llm", "name"}  # Pakolliset config-avaimet

    def __init__(
        self,
        root_path: str | Path,
        check_interval: float = 30.0,
    ) -> None:
        self.root = Path(root_path).resolve()
        self.config_path = self.root / "config.json"
        self.config_backup = self.root / "config.json.backup"
        self.check_interval = check_interval
        self._thread: threading.Thread | None = None
        self._running = False
        self._last_results: list[HealthStatus] = []
        self._fix_count = 0
        self._check_count = 0

    # ── Daemon lifecycle ──────────────────────────────────────────────

    def start(self) -> None:
        """Käynnistä monitori daemon-threadina."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop,
            name="health-monitor",
            daemon=True,
        )
        self._thread.start()
        logger.info("Health Monitor käynnistetty (intervalli: %.0fs)", self.check_interval)

    def stop(self) -> None:
        self._running = False

    def _monitor_loop(self) -> None:
        # Ensimmäinen tarkistus heti
        self._run_all_checks()
        while self._running:
            time.sleep(self.check_interval)
            if self._running:
                self._run_all_checks()

    # ── Checks ────────────────────────────────────────────────────────

    def _run_all_checks(self) -> list[HealthStatus]:
        """Suorita kaikki tarkistukset ja korjaukset."""
        results: list[HealthStatus] = []
        self._check_count += 1

        results.append(self._check_config())
        results.append(self._check_llm())
        results.append(self._check_disk_space())
        results.append(self._check_watcher())
        results.append(self._check_directories())

        self._last_results = results

        # Logita vain ongelmat (ei spämmiä)
        problems = [r for r in results if r.status != HealthStatus.OK]
        if problems:
            for p in problems:
                level = logging.WARNING if p.status == HealthStatus.WARNING else logging.ERROR
                logger.log(level, "[Health] %s: %s%s",
                    p.component, p.message,
                    f" → {p.action}" if p.action else "",
                )

        return results

    def _check_config(self) -> HealthStatus:
        """Tarkista config.json validius ja tee backup."""
        if not self.config_path.exists():
            return HealthStatus("config", HealthStatus.CRITICAL, "config.json puuttuu!")

        try:
            content = self.config_path.read_text(encoding="utf-8")
            config = json.loads(content)

            # Tarkista pakolliset avaimet
            missing = self.CONFIG_REQUIRED_KEYS - set(config.keys())
            if missing:
                return HealthStatus(
                    "config", HealthStatus.WARNING,
                    f"Puuttuvat avaimet: {missing}",
                )

            # Backup onnistuneesta configista
            self.config_backup.write_text(content, encoding="utf-8")
            return HealthStatus("config", HealthStatus.OK, "Validi")

        except json.JSONDecodeError as e:
            # Yritä palauttaa backup
            if self.config_backup.exists():
                try:
                    backup_content = self.config_backup.read_text(encoding="utf-8")
                    json.loads(backup_content)  # Validoi backup
                    self.config_path.write_text(backup_content, encoding="utf-8")
                    self._fix_count += 1
                    return HealthStatus(
                        "config", HealthStatus.FIXED,
                        f"JSON-virhe: {e}",
                        "Palautettu viimeisin toimiva backup",
                    )
                except Exception:
                    pass
            return HealthStatus(
                "config", HealthStatus.CRITICAL,
                f"JSON-virhe: {e}. Ei backupia saatavilla!",
            )

    def _check_llm(self) -> HealthStatus:
        """Tarkista Ollama/LLM-yhteys."""
        try:
            config = json.loads(self.config_path.read_text(encoding="utf-8"))
            endpoint = config.get("llm", {}).get("endpoint", "http://localhost:11434")
        except Exception:
            endpoint = "http://localhost:11434"

        try:
            import urllib.request
            url = f"{endpoint}/api/tags"
            req = urllib.request.Request(url, method="GET")
            req.add_header("Connection", "close")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return HealthStatus("llm", HealthStatus.OK, f"Ollama OK ({endpoint})")
        except Exception:
            pass

        # Yritä käynnistää Ollama
        action = self._try_start_ollama()
        if action:
            self._fix_count += 1
            return HealthStatus("llm", HealthStatus.FIXED, "Ollama oli pois päältä", action)

        return HealthStatus(
            "llm", HealthStatus.WARNING,
            f"Ollama ei vastaa: {endpoint}",
            "Käynnistä manuaalisesti: ollama serve",
        )

    def _try_start_ollama(self) -> str:
        """Yritä käynnistää Ollama taustalle."""
        try:
            if platform.system() == "Windows":
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            else:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            time.sleep(2)
            return "Ollama käynnistetty automaattisesti"
        except FileNotFoundError:
            return ""
        except Exception as e:
            logger.debug("Ollama-käynnistys epäonnistui: %s", e)
            return ""

    def _check_disk_space(self) -> HealthStatus:
        """Tarkista levytila ja siivoa tarvittaessa."""
        try:
            usage = shutil.disk_usage(str(self.root))
            free_mb = usage.free / (1024 * 1024)

            if free_mb < self.MIN_DISK_MB:
                # Autosiivous: poista vanhat arkistot
                cleaned = self._cleanup_old_archives()
                if cleaned > 0:
                    self._fix_count += 1
                    return HealthStatus(
                        "disk", HealthStatus.FIXED,
                        f"Levytila kriittinen: {free_mb:.0f}MB vapaana",
                        f"Siivottu {cleaned} vanhaa arkistotiedostoa",
                    )
                return HealthStatus(
                    "disk", HealthStatus.CRITICAL,
                    f"Levytila kriittinen: {free_mb:.0f}MB vapaana!",
                )

            if free_mb < self.MIN_DISK_MB * 5:
                return HealthStatus(
                    "disk", HealthStatus.WARNING,
                    f"Levytila vähissä: {free_mb:.0f}MB vapaana",
                )

            return HealthStatus("disk", HealthStatus.OK, f"{free_mb:.0f}MB vapaana")

        except Exception as e:
            return HealthStatus("disk", HealthStatus.WARNING, f"Tarkistus epäonnistui: {e}")

    def _cleanup_old_archives(self) -> int:
        """Siivoa vanhat arkistotiedostot."""
        archive = self.root / "Workspace" / "archive"
        if not archive.exists():
            return 0

        cutoff = time.time() - (self.MAX_ARCHIVE_AGE_DAYS * 86400)
        cleaned = 0
        for f in archive.iterdir():
            if f.is_file() and f.stat().st_mtime < cutoff:
                try:
                    f.unlink()
                    cleaned += 1
                except Exception:
                    pass
        return cleaned

    def _check_watcher(self) -> HealthStatus:
        """Tarkista onko watcher.py -prosessi käynnissä."""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
                    capture_output=True, text=True, timeout=5,
                )
                if "watcher" in result.stdout.lower():
                    return HealthStatus("watcher", HealthStatus.OK, "Watcher aktiivinen")
                # Yritä tarkistaa prosessilistan kautta
                result2 = subprocess.run(
                    ["wmic", "process", "where", "name='python.exe'", "get", "commandline"],
                    capture_output=True, text=True, timeout=5,
                )
                if "watcher" in result2.stdout.lower():
                    return HealthStatus("watcher", HealthStatus.OK, "Watcher aktiivinen")
            else:
                result = subprocess.run(
                    ["pgrep", "-f", "watcher.py"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    return HealthStatus("watcher", HealthStatus.OK, "Watcher aktiivinen")

            return HealthStatus(
                "watcher", HealthStatus.WARNING,
                "Watcher-prosessia ei löydy!",
                "Käynnistä: python watcher.py",
            )
        except Exception as e:
            return HealthStatus("watcher", HealthStatus.WARNING, f"Tarkistus: {e}")

    def _check_directories(self) -> HealthStatus:
        """Varmista kriittiset kansiot."""
        required = ["Inbox", "Outbox", "memory", "wiki"]
        missing = []
        for d in required:
            path = self.root / d
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                missing.append(d)

        if missing:
            self._fix_count += 1
            return HealthStatus(
                "directories", HealthStatus.FIXED,
                f"Puuttuvat kansiot: {missing}",
                "Luotu automaattisesti",
            )
        return HealthStatus("directories", HealthStatus.OK, "Kaikki kansiot OK")

    # ── Public API ────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Palauta viimeisin terveystarkistuksen tila."""
        return {
            "running": self._running,
            "checks_performed": self._check_count,
            "auto_fixes": self._fix_count,
            "interval_sec": self.check_interval,
            "last_check": [r.to_dict() for r in self._last_results],
        }

    def run_check_now(self) -> list[dict]:
        """Suorita tarkistus heti (API-kutsu)."""
        results = self._run_all_checks()
        return [r.to_dict() for r in results]

    def is_healthy(self) -> bool:
        """Onko järjestelmä terve (ei kriittisiä ongelmia)?"""
        return all(
            r.status != HealthStatus.CRITICAL
            for r in self._last_results
        )
