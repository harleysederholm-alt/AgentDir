"""
memmachine.py — Ground-Truth vault (arXiv:2604.04853v1)
Erottaa tiukasti työmuistin (STM) ja pysyvän totuuden (LTM).

STM = sandbox-tulokset ja session-data (väliaikaisia, katoaa)
LTM = wiki/ kansio (pysyvä, vain verifioitu tieto commitoidaan)

Pysyvän tiedon muokkaaminen vaatii AINA verifioinnin.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path


class MemMachine:
    """
    MemMachine erottaa lyhytkestoisen (STM) ja pitkäkestoisen (LTM) muistin.
    LTM on Ground-Truth -holvi johon kirjoitetaan vain verifioidut tulokset.
    """

    def __init__(self, ltm_path: str = "wiki") -> None:
        self.ltm = Path(ltm_path)
        self.ltm.mkdir(exist_ok=True)
        self.stm: dict[str, dict] = {}  # Väliaikainen sessiomuisti

    def write_stm(self, key: str, value: object) -> None:
        """Kirjoita työmuistiin (ei pysyvä — katoaa session päättyessä)."""
        self.stm[key] = {
            "value": value,
            "ts": datetime.datetime.now().isoformat(),
        }

    def read_stm(self, key: str) -> object | None:
        """Lue työmuistista. Palauttaa None jos avain ei löydy."""
        entry = self.stm.get(key)
        return entry["value"] if entry else None

    def commit_to_ltm(self, key: str, content: str) -> Path:
        """
        Siirrä tieto STM → LTM vain verifioituna.
        Tämä on AINOA tapa muuttaa wiki/ sisältöä ohjelmallisesti.

        Palauttaa kohdetiedoston polun.
        """
        target = self.ltm / f"{key}.md"
        ts = datetime.datetime.now().isoformat()
        with open(target, "a", encoding="utf-8") as f:
            f.write(f"\n\n<!-- Committed: {ts} -->\n{content}\n")
        return target

    def read_ltm(self, key: str) -> str:
        """Lue pysyvästä muistista. Palauttaa tyhjän merkkijonon jos ei löydy."""
        target = self.ltm / f"{key}.md"
        if target.exists():
            return target.read_text(encoding="utf-8")
        return ""

    def get_ground_truth(self) -> dict[str, str]:
        """Palauta kaikki LTM-faktat dict-muodossa {tiedostonimi: sisältö}."""
        facts: dict[str, str] = {}
        for f in self.ltm.glob("*.md"):
            facts[f.stem] = f.read_text(encoding="utf-8")
        return facts

    def stm_snapshot(self) -> str:
        """Diagnostiikka: palauta STM:n nykytila JSON-muodossa."""
        return json.dumps(self.stm, indent=2, ensure_ascii=False, default=str)
