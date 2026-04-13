"""
AgentDir – agentin ydin (manifest + arkistointi).

Yhdistää konfiguraation ja ``manifest.json`` -roolin watcherin ja LLM-putken käyttöön.
Huom: ``memory/`` on RAG-tietokannan hakemisto; älä nimeä tätä moduulia ``memory.py``.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("agentdir.agent_core")


def load_manifest(root: Path) -> dict:
    """Lue ``manifest.json`` agentin juuresta; puuttuva tai virheellinen → tyhjä dict."""
    p = Path(root) / "manifest.json"
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("manifest.json lukeminen epäonnistui: %s", e)
        return {}


def resolve_agent_role(config: dict, manifest: dict) -> str:
    """
    Valitse rooli: manifestin ``role`` jos asetettu, muuten ``config['role']``.

    Käytetään prompttipohjissa (The Spark -putki).
    """
    mr = (manifest or {}).get("role")
    if isinstance(mr, str) and mr.strip():
        return mr.strip()
    cr = config.get("role")
    if isinstance(cr, str) and cr.strip():
        return cr.strip()
    return "Agent"


def manifest_context_for_system_message(manifest: dict) -> str:
    """Rakenna lyhyt manifest-teksti järjestelmäviestin täydennykseen (valinnainen)."""
    if not manifest:
        return ""
    parts: list[str] = []
    desc = manifest.get("description")
    if isinstance(desc, str) and desc.strip():
        parts.append(desc.strip())
    caps = manifest.get("capabilities")
    if isinstance(caps, list) and caps:
        parts.append("Kyvyt: " + ", ".join(str(c) for c in caps))
    return "\n".join(parts)


def archive_inbox_after_success(root: Path, claimed_inbox_path: Path, display_name: str) -> None:
    """
    Siirrä käsitelty Inbox-varaustiedosto ``Workspace/archive/`` -kansioon.

    ``claimed_inbox_path`` on tyypillisesti ``*.processing.*`` -tiedosto watcherissa.
    """
    root = Path(root)
    dest_dir = root / "Workspace" / "archive"
    dest_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_display = display_name.replace("/", "_").replace("\\", "_").replace(":", "_")
    dest = dest_dir / f"{ts}_{safe_display}"
    try:
        shutil.move(str(claimed_inbox_path.resolve()), str(dest))
        logger.info("Arkistoitu: %s → %s", display_name, dest.name)
    except OSError as e:
        logger.warning("Arkistointi epäonnistui (%s): %s", display_name, e)


def outbox_vastaus_path(outbox: Path, display_name: str, ts: str) -> Path:
    """
    Palauta Outbox-polku: ``vastaus_<alkuperäinen_nimi>`` (törmäyksessä mukana aikaleima).

    ``display_name`` esim. ``tehtävä.md`` → ``vastaus_tehtävä.md``.
    """
    outbox = Path(outbox)
    safe = display_name.replace("/", "_").replace("\\", "_").replace(":", "_")
    candidate = outbox / f"vastaus_{safe}"
    if candidate.exists():
        stem = Path(safe).stem
        suf = Path(safe).suffix or ".md"
        candidate = outbox / f"vastaus_{stem}_{ts}{suf}"
    return candidate
