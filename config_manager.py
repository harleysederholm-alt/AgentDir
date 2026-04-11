"""
AgentDir – Config Manager
Hot-reload: muutokset config.json:iin tulevat voimaan ilman uudelleenkäynnistystä.
Lazy loading: raskaat moduulit (RAG, Evolution) ladataan vasta kun tarvitaan.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("agentdir.config")


class ConfigManager:
    """
    Thread-safe konfiguraatiohallinta hot-reload-tuella.

    Käyttö:
        cfg = ConfigManager("config.json")
        cfg.get("llm.model")          # pistepoluilla
        cfg.get("swarm.enabled", False)
        cfg.watch()                    # käynnistä tausta-watcher
    """

    def __init__(self, path: str | Path = "config.json"):
        self._path   = Path(path)
        self._lock   = threading.RLock()
        self._data   : dict = {}
        self._mtime  : float = 0.0
        self._callbacks: list = []   # kutsutaan muutoksesta
        self._load()

    # ── Lataus ────────────────────────────────────────────────────────────────

    def _load(self) -> bool:
        """Lataa config levyltä. Palauttaa True jos muuttui."""
        try:
            mtime = self._path.stat().st_mtime
            if mtime == self._mtime:
                return False
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            with self._lock:
                self._data  = raw
                self._mtime = mtime
            logger.info("Config ladattu: %s", self._path)
            return True
        except FileNotFoundError:
            logger.error("config.json ei löydy: %s", self._path)
            raise
        except json.JSONDecodeError as e:
            logger.error("config.json JSON-virhe: %s – käytetään vanhaa versiota", e)
            return False

    def reload(self) -> bool:
        """Pakota uudelleenlataus. Palauttaa True jos muuttui."""
        changed = self._load()
        if changed:
            for cb in self._callbacks:
                try:
                    cb(self._data)
                except Exception as e:
                    logger.warning("Config-callback virhe: %s", e)
        return changed

    def on_change(self, callback):
        """Rekisteröi callback jota kutsutaan kun config muuttuu."""
        self._callbacks.append(callback)

    def watch(self, interval: float = 2.0):
        """Käynnistä tausta-threadi joka tarkistaa muutoksia."""
        def _watcher():
            while True:
                try:
                    self.reload()
                except Exception:
                    pass
                time.sleep(interval)

        t = threading.Thread(target=_watcher, daemon=True, name="config-watcher")
        t.start()
        logger.info("Config hot-reload käynnissä (tarkistus %.1fs välein)", interval)

    # ── Lukeminen ─────────────────────────────────────────────────────────────

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Hae arvo pistepolulla. Esim:
            cfg.get("llm.model")
            cfg.get("swarm.enabled", False)
        """
        with self._lock:
            parts = key_path.split(".")
            node  = self._data
            for part in parts:
                if not isinstance(node, dict):
                    return default
                node = node.get(part, default if part == parts[-1] else {})
            return node

    def all(self) -> dict:
        """Palauttaa koko configin kopiona."""
        with self._lock:
            return dict(self._data)

    def save(self, updates: dict):
        """Päivitä ja tallenna config levylle (evoluutio käyttää tätä)."""
        with self._lock:
            self._data.update(updates)
            self._path.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        logger.info("Config tallennettu")

    # dict-like access
    def __getitem__(self, key: str) -> Any:
        with self._lock:
            return self._data[key]

    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._data
