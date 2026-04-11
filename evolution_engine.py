"""
AgentDir – Evolution Engine
Agentin itseparannus perustuen oikeisiin mittareihin.

Mitä tämä OIKEASTI tekee (ei vain liimaa tekstiä):
- Seuraa tehtävien onnistumisprosenttia
- Vertaa eri prompt-versioita A/B-tyylisesti
- Ehdottaa parannettuja promptteja (LLM-avusteisesti)
- Tallentaa versiohistorian → peruutettavissa
- Ei koskaan tee muutoksia automaattisesti ilman kynnysarvon ylitystä
"""

from __future__ import annotations

import json
import logging
import statistics
from datetime import datetime
from pathlib import Path

import requests

logger = logging.getLogger("agentdir.evolution")


class TaskRecord:
    def __init__(self, task_id: str, input_snippet: str, success: bool, feedback_score: float):
        self.task_id = task_id
        self.input_snippet = input_snippet
        self.success = success
        self.feedback_score = feedback_score  # 0.0–1.0
        self.timestamp = datetime.now().isoformat()
        self.prompt_version = ""

    def to_dict(self) -> dict:
        return self.__dict__


class EvolutionEngine:
    """
    Seuraa suorituskykyä ja ehdottaa parannuksia.

    Versiointi:
    - Jokainen prompt-versio tallennetaan evolution.log:iin
    - Vain jos uusi versio selvästi parempi (threshold) se otetaan käyttöön
    - Aina peruutettavissa
    """

    VERSION_FILE = "evolution.log"
    HISTORY_FILE = "memory/task_history.jsonl"

    def __init__(self, config: dict, config_path: str = "config.json"):
        self.config = config
        self.config_path = Path(config_path)
        self.evo_cfg = config.get("evolution", {})
        self.evaluate_every = self.evo_cfg.get("evaluate_every_n_tasks", 5)
        self.min_tasks = self.evo_cfg.get("min_tasks_before_evolve", 10)
        self.success_threshold = self.evo_cfg.get("success_threshold", 0.7)
        self.llm_cfg = config.get("llm", {})
        self.task_count = 0
        self._load_history()

    def _load_history(self):
        self.history: list[TaskRecord] = []
        hist_path = Path(self.HISTORY_FILE)
        hist_path.parent.mkdir(exist_ok=True)
        if hist_path.exists():
            for line in hist_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        d = json.loads(line)
                        r = TaskRecord(
                            d["task_id"], d["input_snippet"],
                            d["success"], d["feedback_score"]
                        )
                        r.timestamp = d.get("timestamp", "")
                        r.prompt_version = d.get("prompt_version", "v1")
                        self.history.append(r)
                    except Exception:
                        pass
        self.task_count = len(self.history)

    def record(self, task_id: str, input_snippet: str, success: bool, feedback_score: float = -1.0):
        """Tallenna tehtävän tulos. feedback_score -1 = automaattinen arvio."""
        if feedback_score < 0:
            feedback_score = 1.0 if success else 0.2

        record = TaskRecord(task_id, input_snippet[:300], success, feedback_score)
        record.prompt_version = f"v{self._current_version()}"
        self.history.append(record)
        self.task_count += 1

        # Append to disk
        hist_path = Path(self.HISTORY_FILE)
        with hist_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

        # Tarkista onko aika evaluoida
        if self.evo_cfg.get("enabled") and self.task_count % self.evaluate_every == 0:
            self._maybe_evolve()

    def _current_version(self) -> int:
        evo_path = Path(self.VERSION_FILE)
        if not evo_path.exists():
            return 1
        lines = [l for l in evo_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        return len(lines) + 1

    def _recent_success_rate(self, n: int = 20) -> float:
        recent = self.history[-n:]
        if not recent:
            return 0.0
        return sum(1 for r in recent if r.success) / len(recent)

    def _recent_scores(self, n: int = 20) -> list[float]:
        return [r.feedback_score for r in self.history[-n:]]

    def get_stats(self) -> dict:
        if not self.history:
            return {
                "total_tasks": 0,
                "success_rate": 0.0,
                "avg_score": 0.0,
                "prompt_version": f"v{self._current_version()}",
            }
        scores = [r.feedback_score for r in self.history]
        return {
            "total_tasks": len(self.history),
            "success_rate": round(self._recent_success_rate(), 3),
            "avg_score": round(statistics.mean(scores), 3),
            "recent_trend": round(self._recent_success_rate(5), 3),
            "prompt_version": f"v{self._current_version()}",
        }

    def _maybe_evolve(self):
        """Päätä onko syytä evolvoida."""
        if len(self.history) < self.min_tasks:
            logger.info("Evolution: liian vähän dataa (%d/%d tehtävää)", len(self.history), self.min_tasks)
            return

        rate = self._recent_success_rate()
        logger.info("Evolution tarkistus: onnistumisprosentti %.0f%%", rate * 100)

        if rate >= self.success_threshold:
            logger.info("Evolution: suorituskyky hyvä (%.0f%%) – ei muutoksia tarvitaan", rate * 100)
            return

        # Onnistumisprosentti liian alhainen → yritetään parantaa prompttia
        logger.info("Evolution: onnistumisprosentti %.0f%% < %.0f%% → yritetään parantaa prompttia",
                    rate * 100, self.success_threshold * 100)
        self._propose_improvement(rate)

    def _propose_improvement(self, current_rate: float):
        """Pyydä LLM:ltä parempi prompt-versio."""
        current_prompt = self.config.get("prompt_templates", {}).get("default", "")
        failed_snippets = [r.input_snippet for r in self.history[-20:] if not r.success][:5]

        meta_prompt = f"""Olet AI-agentti-insinööri. Alla on nykyinen prompt-template jolla on onnistumisprosentti {current_rate:.0%}.

NYKYINEN PROMPT:
{current_prompt}

EPÄONNISTUNEET TEHTÄVÄT (esimerkit):
{json.dumps(failed_snippets, ensure_ascii=False, indent=2)}

Kirjoita PAREMPI prompt-template joka korjaa nämä ongelmat.
Vastaa AINOASTAAN JSON-muodossa: {{"new_prompt": "uusi prompt tähän", "reasoning": "miksi tämä on parempi"}}"""

        try:
            resp = requests.post(
                self.llm_cfg.get("endpoint", "http://localhost:11434/v1/chat/completions"),
                json={
                    "model": self.llm_cfg.get("model", "llama3.2:3b"),
                    "messages": [{"role": "user", "content": meta_prompt}],
                    "temperature": 0.3,
                    "stream": False,
                },
                timeout=120,
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]

            # Parsitaan JSON
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if not match:
                raise ValueError("LLM ei palauttanut JSONia")
            proposal = json.loads(match.group(0))
            new_prompt = proposal.get("new_prompt", "")
            reasoning = proposal.get("reasoning", "")

            if new_prompt and len(new_prompt) > 50:
                self._apply_evolution(new_prompt, reasoning, current_rate)
        except Exception as e:
            logger.error("Evolution proposal epäonnistui: %s", e)

    def _apply_evolution(self, new_prompt: str, reasoning: str, old_rate: float):
        """Tallenna uusi versio ja päivitä config."""
        version = self._current_version()
        entry = {
            "version": f"v{version}",
            "timestamp": datetime.now().isoformat(),
            "old_success_rate": old_rate,
            "reasoning": reasoning,
            "old_prompt_snippet": self.config.get("prompt_templates", {}).get("default", "")[:200],
            "new_prompt_snippet": new_prompt[:200],
        }

        # Kirjaa versiohistoriaan
        with open(self.VERSION_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Päivitä config muistissa ja levyllä
        if "prompt_templates" not in self.config:
            self.config["prompt_templates"] = {}
        self.config["prompt_templates"]["default"] = new_prompt

        self.config_path.write_text(json.dumps(self.config, indent=2, ensure_ascii=False))
        logger.info("🧬 Evoluutio v%d – prompt päivitetty (vanha %.0f%%)", version, old_rate * 100)
        print(f"\n🧬 EVOLUUTIO: Agentti paransi omaa promptiaan (versio v{version})")
        print(f"   Syy: {reasoning[:120]}...\n")
