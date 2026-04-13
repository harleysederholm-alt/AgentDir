"""
causal.py — Kausaalinen raapustuspaperi + Circuit Breaker
Perustuu Causal MAS -periaatteeseen.

Agentti PAKOSTA kirjoittaa hypoteesin ENNEN suoritusta.
Circuit Breaker keskeyttää suorituksen 3 peräkkäisen epäonnistumisen jälkeen.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path


class CausalEngine:
    """
    Kausaalimoottori varmistaa, että agentti ajattelee ennen toimintaa.
    Jokainen tehtävä kirjataan wiki/log.md -kausaalilokiin.
    Circuit Breaker estää loputtomat uudelleenyritykset.
    """

    MAX_RETRIES = 3

    def __init__(self, log_path: str = "wiki/log.md") -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(exist_ok=True)
        self._attempts = 0

    def write_hypothesis(self, task: str, hypothesis: str = "") -> dict:
        """
        Kirjaa aikomus lokiin ENNEN suoritusta.
        Tämä vaihe on pakollinen — ohittaminen rikkoo Causal MAS -periaatteen.
        """
        entry = {
            "ts": datetime.datetime.now().isoformat(),
            "task": task,
            "hypothesis": hypothesis or f"Suoritan tehtävän: {task}",
            "status": "PENDING",
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n```json\n{json.dumps(entry, ensure_ascii=False)}\n```\n")
        return entry

    def record_result(self, success: bool, detail: str = "") -> None:
        """
        Kirjaa tehtävän lopputulos lokiin.
        Circuit Breaker laukeaa jos 3 peräkkäistä epäonnistumista.
        """
        status = "SUCCESS" if success else "FAILURE"
        self._attempts = 0 if success else self._attempts + 1

        if self._attempts >= self.MAX_RETRIES:
            error_msg = (
                f"Circuit Breaker lauennut: {self.MAX_RETRIES} "
                f"peräkkäistä epäonnistumista. Tarvitaan ihmisen apua."
            )
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n🔴 **CIRCUIT BREAKER** | {error_msg}\n")
            raise RuntimeError(error_msg)

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"**{status}** | {detail}\n")

    @property
    def is_tripped(self) -> bool:
        """Onko Circuit Breaker lauennut?"""
        return self._attempts >= self.MAX_RETRIES

    def reset(self) -> None:
        """Nollaa Circuit Breaker (vaatii ihmisen luvan)."""
        self._attempts = 0
