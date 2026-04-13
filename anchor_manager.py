"""
anchor_manager.py — Kognitiivisten ankkureiden hallinta
Lukee .agentdir.md -tiedostot ja syöttää kontekstin watcher.py:lle.
Ei korvaa watcher.py:tä — lisää sille kontekstin.
"""
from __future__ import annotations

from pathlib import Path


class AnchorManager:
    """
    Lukee .agentdir.md -tiedostot kansioista ja tuottaa
    strukturoidun kontekstin LLM-promptiin.

    Integrointi: kutsu get_context() watcher.py:stä
    ennen llm_client.py:n kutsua.
    """

    ANCHOR_FILENAME = ".agentdir.md"
    SOVEREIGN_FILENAME = "!_SOVEREIGN.md"

    def get_context(self, folder_path: Path) -> str:
        """
        Kerää ankkurikonteksti tiedostolle:
        1. !_SOVEREIGN.md (juuresta)
        2. .agentdir.md (kansiosta)

        Returns: kontekstiteksti LLM-promptiin lisättäväksi
        """
        parts: list[str] = []

        # Globaali ankkuri projektijuuresta
        sovereign = self._find_sovereign(folder_path)
        if sovereign:
            parts.append(f"## PROJEKTIN GLOBAALIT SÄÄNNÖT\n{sovereign}")

        # Paikallinen ankkuri tästä kansiosta
        local = folder_path / self.ANCHOR_FILENAME
        if local.exists():
            parts.append(f"## TÄMÄN KANSION KONTEKSTI\n{local.read_text(encoding='utf-8')}")

        return "\n\n".join(parts) if parts else ""

    def _find_sovereign(self, start: Path) -> str:
        """Etsii !_SOVEREIGN.md ylöspäin hakemistopuussa."""
        current = start
        for _ in range(5):  # Max 5 tasoa ylös
            candidate = current / self.SOVEREIGN_FILENAME
            if candidate.exists():
                return candidate.read_text(encoding="utf-8")
            current = current.parent
            if current == current.parent:
                break
        return ""

    def create_anchor(self, folder_path: Path, purpose: str) -> Path:
        """Luo .agentdir.md -tiedoston kansioon."""
        anchor = folder_path / self.ANCHOR_FILENAME
        content = f"""# .agentdir.md — {folder_path.name}

## TARKOITUS
{purpose}

## KONTEKSTI
- Tärkeimmät tiedostot: [täytä]
- Riippuu: [täytä]

## OHJEET AGENTILLE
- Sandbox: pakollinen
- Prioriteetti: normaali
- Muutos vaatii: testit

## KIELLETTYÄ TÄSSÄ KANSIOSSA
- [täytä tarvittaessa]
"""
        anchor.write_text(content, encoding="utf-8")
        return anchor
