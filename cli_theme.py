"""
cli_theme.py — Sovereign Engine CLI visual identity.

Pidetään puhtaana: ei ulkoisia riippuvuuksia. Raaka ANSI, box-drawing -merkit,
ja Achii-brändin mukaiset värit (kupari / teräs / amber). Moduuli ei tuota
sivuvaikutuksia ilman, että sitä kutsutaan — CLI-koodi voi tuoda tämän turvallisesti.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence


# ─────────────────────────────────────────────────────────────────────────────
#  ANSI-primitiivit
# ─────────────────────────────────────────────────────────────────────────────
#  Truecolor (24-bit). Jos terminaali ei tue, värit putoavat harmaaksi tekstiksi
#  eikä CLI mene rikki. Kaikki koodit peilaavat landing- ja mobile-tokeneita.

RESET = "\x1b[0m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"
ITALIC = "\x1b[3m"
UNDERLINE = "\x1b[4m"

# Brand palette (truecolor)
COPPER = "\x1b[38;2;211;84;0m"      # #D35400 — primary output, highlights
AMBER = "\x1b[38;2;243;156;18m"     # #F39C12 — active state, Achii's eyes
STEEL = "\x1b[38;2;96;125;139m"     # #607D8B — metadata, paths
PANEL = "\x1b[38;2;44;62;80m"       # #2C3E50 — oxidized panel edges
INK = "\x1b[38;2;230;230;230m"      # soft off-white body text
MUTED = "\x1b[38;2;132;132;132m"    # dim metadata
OK_GREEN = "\x1b[38;2;97;163;113m"  # success
WARN_AMBER = AMBER
ERR_RED = "\x1b[38;2;192;72;72m"

# Background (used sparingly for status chip)
BG_COPPER = "\x1b[48;2;211;84;0m"
BG_PANEL = "\x1b[48;2;15;15;15m"

# Box-drawing characters — same glyphs as the landing-page panels.
BOX = {
    "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
    "h":  "─", "v":  "│",
    "lt": "├", "rt": "┤",
    "tt": "┬", "bt": "┴",
    "cross": "┼",
    "thick_h": "━",
}


def supports_color() -> bool:
    """Palauttaa True, jos stdout näyttää ANSI-koodit oikein.

    Kunnioitetaan NO_COLOR-standardia (https://no-color.org) ja piilotetaan
    värit, jos output ei ole TTY (esim. putkitus jq:lle).
    """
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("AGENTDIR_FORCE_COLOR") == "1":
        return True
    return sys.stdout.isatty()


def paint(text: str, *codes: str) -> str:
    """Kääri teksti ANSI-koodeihin vain jos terminaali tukee väriä."""
    if not codes or not supports_color():
        return text
    return "".join(codes) + text + RESET


# ─────────────────────────────────────────────────────────────────────────────
#  ASCII-logo (figlet "slant" -tyyli — sama kuin direktiivissä määrätty)
# ─────────────────────────────────────────────────────────────────────────────

BANNER_VERSION = "1.0.4-beta"
BANNER_CODENAME = "The Rusty Awakening"

_BANNER_ART = [
    r"    ___                      __   ____  _      ",
    r"   /   | ____ ____  ____  __/ /_ / __ \(_)____ ",
    r"  / /| |/ __ `/ _ \/ __ \/ / __// / / / / ___/ ",
    r" / ___ / /_/ /  __/ / / / / /_ / /_/ / / /     ",
    r"/_/  |_\__, /\___/_/ /_/_/\__/_____/_/_/       ",
    r"      /____/                                   ",
]


def banner(version: str = BANNER_VERSION, codename: str = BANNER_CODENAME) -> str:
    """Palauttaa monirivisen käynnistysbannerin merkkijonona.

    Rivinvaihto lopussa on tarkoituksellinen — kutsuja voi kirjoittaa
    suoraan sys.stdout.write() tai print() kumpaakin.
    """
    parts: list[str] = [""]
    for line in _BANNER_ART:
        parts.append(paint(line, BOLD, COPPER))
    tagline = (
        f"ENGINEERING LOCAL HARNESS  "
        f"v{version}  ·  {codename}"
    )
    parts.append(paint(tagline, DIM, STEEL))
    parts.append(
        paint(
            "kirjoita  help  tai  /status  alkuun  ·  /attach <tiedosto>  ·  /clean  ·  exit",
            DIM,
            MUTED,
        )
    )
    parts.append("")
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
#  TUI-tilapalkki
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AchiiState:
    """Achiin elinmerkit, joita alapalkki näyttää jokaisen komennon alla."""

    achii: str = "AWAKE"             # AWAKE · THINKING · IDLE
    harness: str = "ENGAGED"         # ENGAGED · DISENGAGED
    inference_ms: int = 0            # viimeisin inference-latenssi (ms)
    tokens_per_s: float = 0.0        # viimeisin token velocity
    entropy: float = 0.0             # 0.0–1.0; korkea = harkitseva, matala = deterministinen
    egress_bytes: int = 0            # ulkopilveen ajetut tavut tässä sessiossa


def render_status_bar(state: AchiiState, width: int = 78) -> str:
    """Kliininen alapalkki REPL-kierroksen lopuksi.

    Mallirivi:
    ── ACHII: AWAKE │ HARNESS: ENGAGED │ latency 2.5 s │ tok/s 31.0 │ egress 0 B ──
    """
    achii_icon = "●" if state.achii == "AWAKE" else "○"
    cells = [
        f"{paint(achii_icon, AMBER)} ACHII: {paint(state.achii, BOLD, AMBER)}",
        f"HARNESS: {paint(state.harness, BOLD, COPPER)}",
        f"latency {paint(f'{state.inference_ms / 1000:.2f} s', INK)}",
        f"tok/s {paint(f'{state.tokens_per_s:.1f}', INK)}",
        f"entropy {paint(f'{state.entropy:.2f}', INK)}",
        f"egress {paint(f'{state.egress_bytes} B', OK_GREEN if state.egress_bytes == 0 else ERR_RED)}",
    ]
    joined = paint(" │ ", DIM, STEEL).join(cells)
    rule = paint(BOX["h"] * 2, DIM, STEEL)
    return f"{rule} {joined} {rule}"


# ─────────────────────────────────────────────────────────────────────────────
#  Taulukot (ei emoji-koristeita, vain box-drawing)
# ─────────────────────────────────────────────────────────────────────────────

def _strip_ansi(s: str) -> str:
    """Laskee näkyvän leveyden — jättää ANSI-koodit huomioimatta."""
    out: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\x1b" and i + 1 < len(s) and s[i + 1] == "[":
            # SGR-sekvenssi loppuu m-kirjaimeen
            j = s.find("m", i)
            if j == -1:
                break
            i = j + 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def render_table(
    headers: Sequence[str],
    rows: Iterable[Sequence[str]],
    header_color: str = COPPER,
    row_color: str = INK,
    meta_color: str = STEEL,
) -> str:
    """Piirrä kliininen taulukko box-drawing -merkeillä.

    Ei värikkäitä emojeita. Headerit kuparin värillä, solut INK,
    erottimet steelillä.
    """
    rows_list = [list(r) for r in rows]
    cols = len(headers)
    widths = [len(_strip_ansi(h)) for h in headers]
    for row in rows_list:
        for i in range(cols):
            cell = row[i] if i < len(row) else ""
            widths[i] = max(widths[i], len(_strip_ansi(cell)))

    def _rule(left: str, mid: str, right: str) -> str:
        seg = mid.join(BOX["h"] * (w + 2) for w in widths)
        return paint(f"{left}{seg}{right}", DIM, meta_color)

    top = _rule(BOX["tl"], BOX["tt"], BOX["tr"])
    sep = _rule(BOX["lt"], BOX["cross"], BOX["rt"])
    bot = _rule(BOX["bl"], BOX["bt"], BOX["br"])
    vbar = paint(BOX["v"], DIM, meta_color)

    def _fmt_row(cells: Sequence[str], color: str) -> str:
        out = [vbar]
        for i, cell in enumerate(cells):
            pad = widths[i] - len(_strip_ansi(cell))
            out.append(" " + paint(cell, color) + " " * pad + " ")
            out.append(vbar)
        return "".join(out)

    lines = [top, _fmt_row(list(headers), f"{BOLD}{header_color}"), sep]
    for row in rows_list:
        padded = list(row) + [""] * (cols - len(row))
        lines.append(_fmt_row(padded, row_color))
    lines.append(bot)
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  Sävelliaset (prompt, title, kvs-lista)
# ─────────────────────────────────────────────────────────────────────────────

def rule(title: str | None = None, width: int = 78) -> str:
    """Vaakaviiva valinnaisella otsikolla — käytetään osioiden välissä."""
    if not title:
        return paint(BOX["h"] * width, DIM, STEEL)
    label = f" {title} "
    remaining = max(0, width - len(label) - 2)
    left = BOX["h"] * 2
    right = BOX["h"] * remaining
    return (
        paint(left, DIM, STEEL)
        + paint(label, BOLD, COPPER)
        + paint(right, DIM, STEEL)
    )


def kv(items: Sequence[tuple[str, str]], key_color: str = STEEL, val_color: str = INK) -> str:
    """Kliininen avain–arvo-lista, ei taulukoksi asti."""
    if not items:
        return ""
    key_w = max(len(_strip_ansi(k)) for k, _ in items)
    lines = []
    for k, v in items:
        k_padded = k + " " * (key_w - len(_strip_ansi(k)))
        lines.append(f"  {paint(k_padded, key_color)}  {paint(v, val_color)}")
    return "\n".join(lines)


def prompt_prefix(state: AchiiState) -> str:
    """REPL-prompt. Käyttää kuparia, kun HARNESS on engaged, muuten steel."""
    color = COPPER if state.harness == "ENGAGED" else STEEL
    return paint("agentdir", BOLD, color) + paint(" › ", DIM, STEEL)


__all__ = [
    "RESET",
    "BOLD",
    "DIM",
    "COPPER",
    "AMBER",
    "STEEL",
    "PANEL",
    "INK",
    "MUTED",
    "OK_GREEN",
    "ERR_RED",
    "BOX",
    "BANNER_VERSION",
    "BANNER_CODENAME",
    "AchiiState",
    "banner",
    "kv",
    "paint",
    "prompt_prefix",
    "render_status_bar",
    "render_table",
    "rule",
    "supports_color",
]
