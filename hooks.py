"""
Kevyt hook-järjestelmä: plugins/*.py ladataan käynnistyksessä ja voivat rekisteröidä kuuntelijoita.

Tapahtumat:
  after_file_parsed(path, text)  — parsinnan jälkeen, ennen LLM:ää
  after_task_completed(path, text, result, success, out_file) — Outbox-kirjoituksen jälkeen
  before_task_process(task_id, payload) — Ennen työnkulun/taskin suoritusta
  on_agent_decision(task_id, decision, reasoning) — Kun agentti tekee valinnan
  on_evolution_proposal(proposal) — Kun uusi evoluutiosääntö ehdotetaan
"""

from __future__ import annotations

import importlib.util
import logging
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger("agentdir.hooks")

_hooks: dict[str, list[Callable[..., None]]] = {}


def register(name: str, fn: Callable[..., None]) -> None:
    """Rekisteröi kuuntelija tapahtuman nimellä."""
    _hooks.setdefault(name, []).append(fn)


def emit(name: str, **kwargs) -> None:
    """Kutsu kaikkia rekisteröityjä kuuntelijoita (virheet nielevät, eivät kaada kutsujaa)."""
    for fn in _hooks.get(name, []):
        try:
            fn(**kwargs)
        except Exception:
            logger.exception("Hook '%s' (%s) kaatui", name, getattr(fn, "__name__", repr(fn)))


def load_plugins() -> None:
    """Lataa kaikki plugins/*.py (paitsi _alkuiset) projektin juureen."""
    root = Path(__file__).resolve().parent / "plugins"
    if not root.is_dir():
        return
    for path in sorted(root.glob("*.py")):
        if path.name.startswith("_"):
            continue
        mod_name = f"agentdir_plugin_{path.stem}"
        spec = importlib.util.spec_from_file_location(mod_name, path)
        if not spec or not spec.loader:
            continue
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            logger.info("Plugin ladattu: %s", path.name)
        except Exception:
            logger.exception("Plugin %s ei käynnistynyt", path.name)
