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


def _pdf_config() -> dict:
    """Lue pdf-osion config.json:sta (cwd tai tämän moduulin hakemisto)."""
    for base in (Path.cwd(), Path(__file__).resolve().parent):
        p = base / "config.json"
        if not p.exists():
            continue
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            sec = raw.get("pdf")
            return sec if isinstance(sec, dict) else {}
        except Exception:
            pass
    return {}


def _read_pdf_ocr(path: Path, opts: dict, total_pages: int) -> str:
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError as e:
        raise RuntimeError(
            "OCR vaatii Python-paketit: pip install -r requirements-ocr.txt tai pip install -e '.[ocr]'. "
            "Järjestelmään tarvitaan myös Tesseract ja Poppler (Windows: asenna ja lisää PATH)."
        ) from e

    max_pages = int(opts.get("ocr_max_pages", 30))
    lang = str(opts.get("ocr_lang", "fin+eng"))
    dpi = int(opts.get("ocr_dpi", 200))
    last_page = min(max_pages, total_pages) if total_pages > 0 else max_pages
    if last_page < 1:
        last_page = max_pages

    logger.info("PDF OCR: '%s' (sivuja max %s, dpi=%s, lang=%s)", path.name, last_page, dpi, lang)

    try:
        images = convert_from_path(str(path), dpi=dpi, first_page=1, last_page=last_page)
    except Exception as e:
        raise RuntimeError(
            f"PDF→kuva epäonnistui (tarvitaan Poppler): {e}"
        ) from e

    if not images:
        raise ValueError("OCR: yhtään sivua ei voitu renderöidä PDF:stä.")

    parts: list[str] = []
    n = len(images)
    for i, img in enumerate(images):
        try:
            txt = pytesseract.image_to_string(img, lang=lang)
        except Exception as e:
            logger.warning("OCR sivu %s: %s", i + 1, e)
            txt = ""
        t = (txt or "").strip()
        if t:
            parts.append(f"[Sivu {i + 1}/{n} OCR]\n{t}")

    if not parts:
        raise ValueError(
            "OCR ei tunnistanut tekstiä (tarkista kielet: tesseract --list-langs; config pdf.ocr_lang)."
        )

    return "\n\n".join(parts)


def _read_pdf(path: Path) -> str:
    try:
        import pypdf
    except ImportError:
        raise RuntimeError("PDF-tuki vaatii: pip install pypdf")

    text_parts: list[str] = []
    total_pages = 0
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        total_pages = len(reader.pages)
        logger.info("PDF: %d sivua – '%s'", total_pages, path.name)
        for i, page in enumerate(reader.pages):
            extracted = page.extract_text()
            if extracted:
                text_parts.append(f"[Sivu {i + 1}/{total_pages}]\n{extracted}")

    if text_parts:
        return "\n\n".join(text_parts)

    opts = _pdf_config()
    if opts.get("ocr_enabled"):
        return _read_pdf_ocr(path, opts, total_pages)

    raise ValueError(
        "PDF on tyhjä tai skannattu (ei tekstiä). Ota OCR: config.json → pdf.ocr_enabled ja "
        "asenna riippuvuudet (requirements-ocr.txt, README)."
    )


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
