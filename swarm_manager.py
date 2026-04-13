"""
AgentDir – Swarm Manager
Luo ja hallinnoi lapsi-agenttikansioita.

KRIITTINEN KORJAUS alkuperäiseen:
- Lapsi-kansiot luodaan swarm/-hakemistoon, EI Inbox/-kansion sisään
- Tämä estää watcherin rekursiivisen loop-ongelman
- Lapsi-agenteilla on oma watcher.py (käynnistetään subprocess:lla)
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("agentdir.swarm")

SWARM_DIR = Path("swarm")


def should_swarm(result: str, config: dict) -> bool:
    """Tarkista tarvitaanko swarmia LLM:n vastauksen perusteella."""
    if not config.get("swarm", {}).get("enabled", False):
        return False
    keywords = config.get("swarm", {}).get("trigger_keywords", [])
    result_lower = result.lower()
    return any(kw.lower() in result_lower for kw in keywords)


class SwarmManager:
    def __init__(self, config: dict, root_dir: Path = Path(".")):
        self.config = config
        self.root_dir = root_dir
        self.swarm_dir = root_dir / "swarm"
        self.swarm_dir.mkdir(exist_ok=True)
        self.max_children = config.get("swarm", {}).get("max_children", 5)
        self.active_children: list[subprocess.Popen] = []
        # Lapsikansioiden määrä tässä sessiossa (active_children on vain subprocesseille)
        self._spawned_children = 0

    def spawn_child(self, task: str, child_role: str, parent_file: str) -> Path | None:
        """
        Luo uuden lapsi-agenttikansion swarm/-hakemistoon.
        TÄRKEÄÄ: Ei koskaan Inbox/sisään → estää loopen.
        """
        if self._spawned_children >= self.max_children:
            logger.warning("Swarm: max lapsi-agentteja (%d) saavutettu", self.max_children)
            return None

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        child_name = f"child_{child_role.replace(' ', '_')}_{ts}"
        child_dir = self.swarm_dir / child_name

        # Luo rakenne
        (child_dir / "Inbox").mkdir(parents=True, exist_ok=True)
        (child_dir / "Outbox").mkdir(exist_ok=True)
        (child_dir / "memory").mkdir(exist_ok=True)

        # Luo lapsen config (perii vanhemmalta, mutta eri rooli)
        child_config = dict(self.config)
        child_config["name"] = child_name
        child_config["role"] = child_role
        child_config["swarm"]["enabled"] = False  # lapset eivät luo lapsia
        (child_dir / "config.json").write_text(
            json.dumps(child_config, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Kopioi tarvittavat skriptit
        src_files = [
            "watcher.py",
            "config_manager.py",
            "rag_memory.py",
            "sandbox_executor.py",
            "file_parser.py",
            "llm_client.py",
            "agent_core.py",
            "evolution_log.py",
            "evolution_engine.py",
            "swarm_manager.py",
            "hooks.py",
        ]
        for fname in src_files:
            src = self.root_dir / fname
            if src.exists():
                (child_dir / fname).write_text(
                    src.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )

        manifest = self.root_dir / "manifest.json"
        if manifest.exists():
            (child_dir / "manifest.json").write_text(
                manifest.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

        # Kirjoita tehtävä lapsen Inboxiin
        task_file = child_dir / "Inbox" / f"task_from_{parent_file}.md"
        task_file.write_text(
            f"# Tehtävä vanhemmalta agentilta\n\nAlkuperäinen tiedosto: {parent_file}\n\n{task}",
            encoding="utf-8",
        )

        self._spawned_children += 1
        logger.info("🚀 Swarm: Lapsi-agentti luotu → %s", child_dir)
        return child_dir

    def cleanup_finished(self):
        """Siivoa valmiit lapsi-prosessit."""
        self.active_children = [p for p in self.active_children if p.poll() is None]

    def active_count(self) -> int:
        self.cleanup_finished()
        return len(self.active_children)
