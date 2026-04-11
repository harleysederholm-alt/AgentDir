"""
AgentDir – File Parser
Tukee: .txt, .md, .pdf, .csv, .json
Palauttaa aina merkkijonon tai heittää selkeän virheen.
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

logger = logging.getLogger("agentdir.parser")

SUPPORTED = {".txt", ".md", ".pdf", ".csv", ".json"}


def parse(file_path: Path) -> str:
    """
    Parsii tiedoston tekstiksi.
    Palauttaa str tai nostaa ValueError jos formaatti ei tue.
    """
    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED:
        raise ValueError(f"Tiedostotyyppi '{suffix}' ei tuettu. Tuetut: {SUPPORTED}")

    if suffix in (".txt", ".md"):
        return _read_text(file_path)

    if suffix == ".pdf":
        return _read_pdf(file_path)

    if suffix == ".csv":
        return _read_csv(file_path)

    if suffix == ".json":
        return _read_json(file_path)

    raise ValueError(f"Tuntematon tyyppi: {suffix}")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip()


def _read_pdf(path: Path) -> str:
    try:
        import pypdf
    except ImportError:
        raise RuntimeError("PDF-tuki vaatii: pip install pypdf")

    text_parts = []
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        total = len(reader.pages)
        logger.info("PDF: %d sivua – '%s'", total, path.name)
        for i, page in enumerate(reader.pages):
            extracted = page.extract_text()
            if extracted:
                text_parts.append(f"[Sivu {i+1}/{total}]\n{extracted}")

    if not text_parts:
        raise ValueError("PDF on tyhjä tai skannattu (ei tekstiä). Käytä OCR-versiota.")

    return "\n\n".join(text_parts)


def _read_csv(path: Path) -> str:
    """Muuttaa CSV:n markdown-taulukoksi LLM:lle."""
    try:
        rows = []
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)

        if not rows:
            return "(Tyhjä CSV)"

        headers = rows[0]
        data_rows = rows[1:50]  # max 50 riviä kontekstiin

        # Markdown-taulukko
        header_line = "| " + " | ".join(headers) + " |"
        separator = "| " + " | ".join(["---"] * len(headers)) + " |"
        data_lines = ["| " + " | ".join(row) + " |" for row in data_rows]

        summary = f"CSV-tiedosto: {len(rows)-1} riviä, {len(headers)} saraketta\n\n"
        if len(rows) > 51:
            summary += f"*(Näytetään ensimmäiset 50 riviä / {len(rows)-1})*\n\n"

        return summary + "\n".join([header_line, separator] + data_lines)

    except Exception as e:
        raise ValueError(f"CSV-lukuvirhe: {e}")


def _read_json(path: Path) -> str:
    """Muotoiltu JSON merkkijonoksi."""
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except json.JSONDecodeError as e:
        raise ValueError(f"Virheellinen JSON: {e}")
