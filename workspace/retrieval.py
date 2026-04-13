"""
retrieval.py — Tiedostopohjainen kontekstin keruu
Kerää relevantin materiaalin /raw ja /wiki -kansioista tehtävää varten.
"""
from __future__ import annotations

from pathlib import Path


SUPPORTED_EXTENSIONS = {".md", ".txt", ".py", ".json", ".csv"}


class ContextRetriever:
    """
    Kerää tehtävälle relevantin kontekstin wiki/ ja raw/ kansioista.
    Noudattaa kontekstin prioriteettijärjestystä (02_CONTEXT_RULES.md).
    """

    def __init__(self, raw_path: str = "raw", wiki_path: str = "wiki") -> None:
        self.raw = Path(raw_path)
        self.wiki = Path(wiki_path)

    def gather_context(self, task: str, max_chars: int = 4000) -> str:
        """
        Kerää relevantti konteksti tehtävän perusteella.
        Prioriteetti: wiki/index.md → wiki/*.md → raw/*
        """
        chunks: list[str] = []
        total = 0

        # P3: wiki/index.md ensin (korkein prioriteetti tiedostoista)
        index = self.wiki / "index.md"
        if index.exists():
            content = index.read_text(encoding="utf-8")[:1000]
            chunks.append(f"## PROJEKTI-INDEKSI\n{content}")
            total += len(content)

        # P4: Muut wiki/ tiedostot
        if self.wiki.exists():
            for f in sorted(self.wiki.iterdir()):
                if (
                    f.suffix in SUPPORTED_EXTENSIONS
                    and f.name != "index.md"
                    and total < max_chars
                ):
                    content = f.read_text(encoding="utf-8", errors="ignore")[:500]
                    chunks.append(f"## {f.name}\n{content}")
                    total += len(content)

        # P5: /raw tiedostot
        if self.raw.exists():
            for f in sorted(self.raw.iterdir()):
                if f.suffix in SUPPORTED_EXTENSIONS and total < max_chars:
                    content = f.read_text(encoding="utf-8", errors="ignore")[:500]
                    chunks.append(f"## {f.name}\n{content}")
                    total += len(content)

        return "\n\n".join(chunks)
