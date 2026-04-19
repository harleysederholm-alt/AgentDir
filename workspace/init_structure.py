"""
init_structure.py — Alustaa AgentDir 3.5 -kansiorakenteen
Käyttö: python cli.py init [--path .]
"""
from __future__ import annotations

import datetime
from pathlib import Path


SOVEREIGN_TEMPLATE = """# !_SOVEREIGN.md — AgentDir 3.5 Sovereign Map
# Globaali reititys, etiikka ja resurssit.

## EETTISET RAJAT (MemMachine)
- EI kirjoituksia /raw, /wiki, /outputs ulkopuolelle ilman COMMIT-lupaa
- EI verkkokutsuja hiekkalaatikosta
- AINA kausaalinen hypoteesi ennen suoritusta
- AINA Agent Print -raportti tehtävän jälkeen

## OMNINODE-KARTTA
- node_0: localhost (master)
- node_1: [lisää USB-C laite]
- node_2: [lisää WiFi laite]

## REITITYSSÄÄNNÖT
- Kooditehtävät → omninode
- Muisti/tutkimus → sovereign
- Visio → vision-backend
"""

AGENTDIR_TEMPLATE = """# .agentdir.md — Paikallinen kognitiivinen ankkuri
# Tämä kansio on osa AgentDir 3.5 Sovereign Swarmiä.

## TÄMÄN KANSION TARKOITUS
[Kirjoita tähän kansion tehtävä]

## PAIKALLINEN KONTEKSTI
- Tärkeimmät tiedostot: [listaa]
- Riippuvuudet: [listaa]

## AGENTTIOHJEET
- Prioriteetti: normaali
- Sandbox: pakollinen
- LTM-commit: vaaditaan verifiointi
"""


def init_project(path: str = ".") -> None:
    """Alusta AgentDir 3.5 -kansiorakenne kohdehakemistoon."""
    root = Path(path)

    # Kansiorakenne
    for d in ["raw", "wiki", "outputs", "workspace/tests"]:
        (root / d).mkdir(parents=True, exist_ok=True)

    # Päätiedostot (ei ylikirjoiteta olemassa olevia)
    sovereign = root / "!_SOVEREIGN.md"
    if not sovereign.exists():
        sovereign.write_text(SOVEREIGN_TEMPLATE, encoding="utf-8")

    anchor = root / ".agentdir.md"
    if not anchor.exists():
        anchor.write_text(AGENTDIR_TEMPLATE, encoding="utf-8")

    # Wiki-indeksi
    index = root / "wiki" / "index.md"
    if not index.exists():
        index.write_text(
            f"# Projektin tietopankki\nLuotu: {datetime.datetime.now().isoformat()}\n",
            encoding="utf-8",
        )

    # Kausaaliloki
    log = root / "wiki" / "log.md"
    if not log.exists():
        log.write_text("# Kausaaliloki\n\n", encoding="utf-8")

    print(f"✅ AgentDir 3.5 alustettu: {root.resolve()}")
    print("   Seuraava askel: python cli.py run 'tehtäväsi'")
