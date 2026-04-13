"""
evolution_bridge.py — Yhdistaa evolution_engine.py AgentDir 3.5 pipelineen

Tarkoitus: silta vanhan v1.x EvolutionEnginen ja uuden
WorkflowOrchestrator-pipelinen valilla.

Pipeline-integraatio:
  orchestrator.run() -> ... -> evolution.record() -> maybe_evolve()

Tama moduuli EI muokkaa evolution_engine.py:ta lainkaan.
Se importtaa sen ja kayttaa suoraan.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("agentdir.evolution_bridge")


class EvolutionBridge:
    """
    Silta: EvolutionEngine <-> WorkflowOrchestrator

    Rekisteroi jokaisen tehtavan tuloksen EvolutionEnginelleen,
    joka seuraa onnistumisprosenttia ja ehdottaa prompt-parannuksia.
    """

    def __init__(self, config_path: str = "config.json") -> None:
        self._engine = None
        self._config_path = Path(config_path)
        self._config: dict = {}
        self._load_config()

    def _load_config(self) -> None:
        """Lataa config.json ja alusta EvolutionEngine."""
        if self._config_path.exists():
            try:
                self._config = json.loads(
                    self._config_path.read_text(encoding="utf-8")
                )
            except Exception as e:
                logger.warning("Config luku epaonnistui: %s", e)
                self._config = self._default_config()
        else:
            self._config = self._default_config()

        try:
            from evolution_engine import EvolutionEngine
            self._engine = EvolutionEngine(
                self._config, str(self._config_path)
            )
            logger.info(
                "EvolutionEngine yhdistetty (versio %s)",
                self._engine.get_stats().get("prompt_version", "?"),
            )
        except ImportError:
            logger.warning("evolution_engine.py ei loytynyt — evoluutio pois kaytosta")
        except Exception as e:
            logger.error("EvolutionEngine alustus epaonnistui: %s", e)

    @staticmethod
    def _default_config() -> dict:
        """Oletuskonfiguraatio jos config.json puuttuu."""
        return {
            "evolution": {
                "enabled": True,
                "evaluate_every_n_tasks": 5,
                "min_tasks_before_evolve": 10,
                "success_threshold": 0.7,
            },
            "llm": {
                "endpoint": "http://localhost:11434/v1/chat/completions",
                "model": "gemma4:e4b",
            },
            "prompt_templates": {
                "default": "",
            },
        }

    # ── Pipeline-integraatio ─────────────────────────────────────────────

    def record_task(self, result: dict[str, Any]) -> dict:
        """
        Rekisteroi tehtavan tulos EvolutionEnginelle.
        Kutsutaan orchestrator.run():n lopussa.

        Args:
            result: Orkestroijan palauttama tulos-dict

        Returns:
            dict: Evoluution tilastot (tai tyhja dict)
        """
        if self._engine is None:
            return {}

        task = result.get("task", result.get("summary", "unknown"))
        success = result.get("success", False)
        print_id = result.get("print_id", "")

        try:
            self._engine.record(
                task_id=print_id or "task",
                input_snippet=task[:300],
                success=success,
            )
            return self._engine.get_stats()
        except Exception as e:
            logger.error("Evolution record epaonnistui: %s", e)
            return {}

    def get_stats(self) -> dict:
        """Palauta evoluution nykyiset tilastot."""
        if self._engine is None:
            return {"status": "disabled", "reason": "EvolutionEngine not available"}
        try:
            return self._engine.get_stats()
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    @property
    def is_active(self) -> bool:
        """Onko evoluutio aktiivinen?"""
        return self._engine is not None

    @property
    def current_version(self) -> str:
        """Nykyinen prompt-versio."""
        stats = self.get_stats()
        return stats.get("prompt_version", "v?")
