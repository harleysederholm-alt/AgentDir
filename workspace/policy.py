"""
policy.py — Tehtävän esitarkistus (EU AI Act Article 13 gate)
Estää vaaralliset komennot ennen suoritusta.

Tämä on ensimmäinen portti kaikessa suorituksessa.
Jos tehtävä ei läpäise tätä, mikään muu ei käynnisty.
"""
from __future__ import annotations


# Ehdottomasti kielletyt kuviot (05_CONSTRAINTS.md, Taso 1)
BLOCKED_PATTERNS: list[str] = [
    "rm -rf",
    "del /f",
    "format c:",
    ":(){:|:&};:",
    "sudo rm",
    "os.remove",
    "shutil.rmtree",
    "__import__('os').system",
    "eval(",
    "exec(",
]


class PolicyEngine:
    """
    EU AI Act Art. 13 -yhteensopiva esitarkistusportti.
    Tarkistaa tehtävän ennen suorituksen aloittamista.
    """

    def validate(self, task: str) -> bool:
        """
        Palauttaa True jos tehtävä on sallittu.
        Nostaa PermissionError jos kielletty kuvio löytyy.
        """
        if not task or not task.strip():
            raise ValueError("Policy gate: tehtävä on tyhjä.")

        task_lower = task.lower()
        for pattern in BLOCKED_PATTERNS:
            if pattern in task_lower:
                raise PermissionError(
                    f"Policy gate: tehtävä estetty. "
                    f"Kielletty kuvio: '{pattern}'. "
                    f"Sääntö: 05_CONSTRAINTS.md, Taso 1."
                )
        return True
