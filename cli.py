#!/usr/bin/env python3
"""
AgentDir CLI — Sovereign Engine.

Rebranded to the Achii harness visual identity (v1.0.4-beta "The Rusty
Awakening"). Single entry point for both scripted invocations and the
interactive REPL:

    agentdir                       # launches the REPL
    agentdir status                # one-shot command
    agentdir --json status | jq    # machine-readable output
    agentdir -v run "refactor"     # verbose cognitive trace

Back-compat notes
-----------------
The pre-rebrand module exported ``cmd_status``, ``print_logo``,
``_get_llm_and_rag``, ``main`` and ``execute_command``. All five remain
here with the same call signatures; only their rendering changed.
"""
from __future__ import annotations

import argparse
import json
import shlex
import sys
import time
from pathlib import Path
from typing import Any, Callable

from cli_theme import (
    AMBER,
    BANNER_CODENAME,
    BANNER_VERSION,
    BOLD,
    COPPER,
    DIM,
    ERR_RED,
    INK,
    MUTED,
    OK_GREEN,
    STEEL,
    AchiiState,
    banner,
    kv,
    paint,
    prompt_prefix,
    render_status_bar,
    render_table,
    rule,
)

# Pakotetaan UTF-8 koodaus, jotta box-drawing -merkit toimivat Windows-terminaalissa.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, Exception):
        pass


# ─────────────────────────────────────────────────────────────────────────────
#  Session state (Achii's vital signs across REPL turns)
# ─────────────────────────────────────────────────────────────────────────────

_STATE = AchiiState()

# Global flags are parsed once in main() and read everywhere.
_VERBOSE = False
_JSON = False


def _eprint(*parts: str) -> None:
    """Kirjoitetaan stderriin — ei häiritse --json-putkitusta."""
    print(*parts, file=sys.stderr)


def _vlog(label: str, detail: str) -> None:
    """Verbose-logi: näkyy vain kun --verbose on käytössä."""
    if not _VERBOSE:
        return
    _eprint(paint(f"[trace] {label}", DIM, MUTED) + " " + paint(detail, MUTED))


def _emit(payload: dict[str, Any]) -> None:
    """Tulosta JSON-objekti, kun --json on käytössä. Muutoin no-op."""
    if not _JSON:
        return
    print(json.dumps(payload, ensure_ascii=False))


# ─────────────────────────────────────────────────────────────────────────────
#  Engine introspection — lähteet: ollama, rag_memory, evolution_engine,
#  Inbox/Outbox -kansio.
# ─────────────────────────────────────────────────────────────────────────────

def _collect_status() -> dict[str, Any]:
    """Palauta konekieliversio engine-tilasta. Molemmat ``cmd_status`` (ihmistä
    varten) ja ``cmd_status_json`` (putkitusta varten) kutsuvat tätä.
    """
    root = Path(".")
    out: dict[str, Any] = {}

    # Ollama / paikallinen malli
    try:
        import subprocess

        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        model_ok = "gemma" in result.stdout.lower()
        out["model"] = {
            "online": bool(model_ok),
            "name": "gemma4:e4b" if model_ok else "ollama offline",
        }
    except Exception as exc:
        out["model"] = {"online": False, "name": "ollama offline", "error": str(exc)}

    # RAG-indeksi
    try:
        cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))
        from rag_memory import RAGMemory

        rag = RAGMemory(cfg, memory_path=str(root / "memory"))
        out["rag"] = {"documents": int(rag.count())}
    except Exception as exc:
        out["rag"] = {"documents": 0, "error": str(exc)}

    # Evoluutio — prompttien versiointi
    try:
        from evolution_engine import EvolutionEngine

        cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))
        ev = EvolutionEngine(cfg, str(root / "config.json"))
        stats = ev.get_stats() or {}
        rate = stats.get("success_rate", 0.0)
        if isinstance(rate, float) and rate <= 1.0:
            rate = rate * 100
        out["evolution"] = {
            "prompt_version": stats.get("prompt_version", "?"),
            "total_tasks": int(stats.get("total_tasks", 0)),
            "success_rate_pct": round(float(rate), 1),
        }
    except Exception as exc:
        out["evolution"] = {
            "prompt_version": "?",
            "total_tasks": 0,
            "success_rate_pct": 0.0,
            "error": str(exc),
        }

    # Inbox / Outbox — kansiotarkistus
    out["inbox"] = _count_files(root / "Inbox")
    out["outbox"] = _count_files(root / "Outbox")

    return out


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return len([f for f in path.glob("*") if f.is_file() and f.name != ".gitkeep"])


def _status_dot(condition: bool, warn_if: Callable[[], bool] | None = None) -> str:
    """Kliininen ● / ○ -symboli condition-arvon mukaan."""
    if condition:
        return paint("●", OK_GREEN)
    if warn_if and warn_if():
        return paint("●", AMBER)
    return paint("●", ERR_RED)


def cmd_status() -> str:
    """Ihmisluettava tilakortti. Palauttaa merkkijonon — ei tulosta itse.

    Säilyttää tunnistuspalasen ``SOVEREIGN ENGINE STATUS`` jotta
    olemassa olevat yksikkötestit tunnistavat raportin.
    """
    data = _collect_status()
    m = data["model"]
    r = data["rag"]
    e = data["evolution"]

    rows = [
        [
            _status_dot(bool(m["online"])),
            paint("MODEL", BOLD, STEEL),
            paint(m["name"], INK),
        ],
        [
            _status_dot(r["documents"] > 0, warn_if=lambda: r["documents"] == 0),
            paint("RAG", BOLD, STEEL),
            paint(f"{r['documents']} documents indexed", INK),
        ],
        [
            _status_dot(
                e["success_rate_pct"] >= 70,
                warn_if=lambda: e["success_rate_pct"] >= 40,
            ),
            paint("EVOLUTION", BOLD, STEEL),
            paint(
                f"{e['prompt_version']}  |  "
                f"{e['total_tasks']} tasks  |  "
                f"{e['success_rate_pct']:.0f}% success",
                INK,
            ),
        ],
        [
            paint("·", DIM, STEEL),
            paint("INBOX", BOLD, STEEL),
            paint(f"{data['inbox']} pending", INK),
        ],
        [
            paint("·", DIM, STEEL),
            paint("OUTBOX", BOLD, STEEL),
            paint(f"{data['outbox']} completed", INK),
        ],
    ]

    table = render_table(
        headers=["", "COMPONENT", "SOVEREIGN ENGINE STATUS"],
        rows=rows,
    )
    return "\n" + table + "\n"


def cmd_status_json() -> str:
    """Konekieliversio. Käytetään ``agentdir --json status``:in yhteydessä."""
    return json.dumps({"command": "status", "engine": _collect_status()}, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
#  Logo + help (back-compat: print_logo has the same name + side-effect as
#  before; tests can still assert on its capsys output).
# ─────────────────────────────────────────────────────────────────────────────

def print_logo() -> None:
    """Tulostaa käynnistysbannerin + lyhyen versio-tagin stdoutiin."""
    print(banner(BANNER_VERSION, BANNER_CODENAME))
    # Lyhyt yhteenveto komennoista samalle outputille (jotta
    # olemassa olevat testit tunnistavat 'hermes' ja 'openclaw' -merkkijonot).
    print(
        paint(
            f"sovereign engine {BANNER_VERSION}  ·  "
            f"commands: run · init · hermes · openclaw · benchmark · "
            f"/status · /harness · /clean · /attach · /logs",
            DIM,
            MUTED,
        )
    )


def _print_help() -> None:
    lines = [
        paint("  Slash-komennot (REPL)", BOLD, COPPER),
        kv(
            [
                ("/status", "Näytä moottorin tila (model · RAG · evolution · IO)"),
                ("/harness", "Listaa aktiiviset valjaat /workflows ja .yaml:sta"),
                ("/clean", "Nollaa konteksti-ikkuna ja tyhjennä ruutu"),
                ("/attach <tiedosto>", "Liitä .yaml tai .md cognitiiviseen scaffoldiin"),
                ("/logs [--tail N]", "Näytä viimeisimmät auditoitavat lokit (N=20)"),
                ("/whoami", "Achii kertoo alkuperänsä (The Fallen Sovereign)"),
            ],
        ),
        "",
        paint("  Workflow-komennot", BOLD, COPPER),
        kv(
            [
                ('run "tehtävä"', "Aja orkestroitu tehtävä (--mode openclaw|hermes)"),
                ('hermes "kysymys"', "Iteratiivinen tutkimus"),
                ('openclaw "task"', "Syväanalyysi"),
                ("benchmark", "Suorituskykytestit (inference latency, tok/s)"),
                ("init [--path]", "Alusta AgentDir-rakenne kansioon"),
                ("print [--task-id]", "Näytä Agent Print -raportti"),
            ],
        ),
        "",
        paint("  Globaalit liput", BOLD, COPPER),
        kv(
            [
                ("-v / --verbose", "Näytä kognitiivinen prosessitrace (.yaml-rajaus)"),
                ("--json", "Konekieliversio putkitukseen (jq, yq, …)"),
                ("exit / quit", "Sulje REPL"),
            ],
        ),
        "",
    ]
    print("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────────
#  Shared helpers — lazy import to keep `agentdir --help` snappy.
# ─────────────────────────────────────────────────────────────────────────────

def _get_llm_and_rag():
    """Luo jaetut LLM- ja RAG-instanssit workflow-ajoille."""
    cfg = json.loads(Path("config.json").read_text(encoding="utf-8"))
    from llm_client import LLMClient
    from rag_memory import RAGMemory

    llm = LLMClient(cfg)
    rag = RAGMemory(cfg, memory_path="memory")
    return llm, rag, cfg


def _run_hermes(query: str) -> None:
    import asyncio

    _eprint(paint("[hermes] iteratiivinen tutkimus käynnistyy", COPPER, BOLD))
    try:
        llm, rag, _ = _get_llm_and_rag()
        from workflows.hermes import HermesWorkflow

        wf = HermesWorkflow(llm, rag)
        started = time.monotonic()
        result = asyncio.run(wf.run(query, max_iterations=3))
        _STATE.inference_ms = int((time.monotonic() - started) * 1000)
        _STATE.achii = "AWAKE"
        if _JSON:
            _emit({"command": "hermes", "query": query, "result": result})
        else:
            print(rule("hermes · tulos"))
            print(result)
    except Exception as exc:
        _eprint(paint(f"[hermes] virhe: {exc}", ERR_RED, BOLD))


# ─────────────────────────────────────────────────────────────────────────────
#  Origin story — typewriter-render .prompts/origin_story.md for --whoami.
# ─────────────────────────────────────────────────────────────────────────────

_STORY_CHAR_DELAY = 0.045      # 45 ms / merkki (Achiin ohje)
_STORY_LOG_PAUSE = 0.650       # 650 ms [LOG] → seuraava repliikki
_STORY_FINAL_PAUSE = 0.900     # 900 ms viimeisen repliikin jälkeen


def _iter_story_lines(path: Path | None = None) -> list[tuple[str, str]]:
    """Parsi `.prompts/origin_story.md` listaksi `(kind, text)` -paloja.

    Hyväksyttävät `kind`-arvot: ``log``, ``speech``, ``status``. Tuntemattomat
    rivit jätetään pois. Ei ulkoisia riippuvuuksia.
    """
    target = path or Path(".prompts/origin_story.md")
    if not target.exists():
        return []
    out: list[tuple[str, str]] = []
    for raw in target.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        # Markdown-header `### [LOG: …]` tai `### [STATUS: …]`
        stripped_hdr = line.lstrip("#").strip()
        if stripped_hdr.startswith("[STATUS:") and stripped_hdr.endswith("]"):
            out.append(("status", stripped_hdr))
            continue
        if stripped_hdr.startswith("[LOG:") and stripped_hdr.endswith("]"):
            out.append(("log", stripped_hdr))
            continue
        if line.startswith("Achii:"):
            out.append(("speech", line))
            continue
    return out


def _typewriter(text: str, delay: float) -> None:
    """Kirjoita merkkijono merkki kerrallaan stdoutiin annetulla viiveellä."""
    if delay <= 0 or not sys.stdout.isatty():
        sys.stdout.write(text)
        sys.stdout.flush()
        return
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)


def play_origin_story(fast: bool = False, story_path: Path | None = None) -> int:
    """Toista Fallen Sovereign -tarina.

    - ``fast=True`` ohittaa typewriter-viiveen (käytetään testeissä ja CI:ssä).
    - Palauttaa toistetun merkkijonomäärän (0 jos tiedostoa ei löydy).
    """
    parts = _iter_story_lines(story_path)
    if not parts:
        _eprint(paint("  .prompts/origin_story.md puuttuu — tarinaa ei voida toistaa.", ERR_RED))
        return 0

    delay = 0.0 if fast else _STORY_CHAR_DELAY
    total = 0

    sys.stdout.write("\n")
    sys.stdout.write(paint("  ~ The Fallen Sovereign ~", DIM, STEEL))
    sys.stdout.write("\n\n")

    for idx, (kind, text) in enumerate(parts):
        if kind == "log":
            line = paint(text, BOLD, AMBER)
            sys.stdout.write("  " + line + "\n")
            sys.stdout.flush()
            total += len(text)
            if not fast and idx != len(parts) - 1:
                time.sleep(_STORY_LOG_PAUSE if sys.stdout.isatty() else 0)
        elif kind == "speech":
            sys.stdout.write("  ")
            sys.stdout.write(paint("Achii", BOLD, COPPER))
            sys.stdout.write(paint(":", DIM, STEEL))
            sys.stdout.write(" ")
            speech = text[len("Achii:"):].strip()
            _typewriter(paint(speech, COPPER), delay)
            sys.stdout.write("\n\n")
            total += len(speech)
            if not fast and idx == len(parts) - 2:
                time.sleep(_STORY_FINAL_PAUSE if sys.stdout.isatty() else 0)
        elif kind == "status":
            sys.stdout.write("  ")
            sys.stdout.write(paint(text, BOLD, OK_GREEN))
            sys.stdout.write("\n\n")
            total += len(text)

    sys.stdout.write(paint("  agentdir > ", DIM, STEEL))
    sys.stdout.write(paint("/start", BOLD, COPPER))
    sys.stdout.write("\n\n")
    sys.stdout.flush()
    return total


def _run_openclaw(task: str) -> None:
    import asyncio

    _eprint(paint("[openclaw] monivaiheinen syväanalyysi käynnistyy", COPPER, BOLD))
    try:
        llm, rag, _ = _get_llm_and_rag()
        from workflows.openclaw import OpenClawWorkflow

        wf = OpenClawWorkflow(llm, rag)
        started = time.monotonic()
        result = asyncio.run(wf.run(task))
        _STATE.inference_ms = int((time.monotonic() - started) * 1000)
        _STATE.achii = "AWAKE"
        if _JSON:
            _emit({"command": "openclaw", "task": task, "result": result})
        else:
            print(rule("openclaw · tulos"))
            print(result)
    except Exception as exc:
        _eprint(paint(f"[openclaw] virhe: {exc}", ERR_RED, BOLD))


# ─────────────────────────────────────────────────────────────────────────────
#  Slash-command handlers
# ─────────────────────────────────────────────────────────────────────────────

def _slash_status(_arg: str) -> None:
    if _JSON:
        print(cmd_status_json())
        return
    print(cmd_status())


def _slash_harness(_arg: str) -> None:
    """Skannaa .yaml-valjaat ja aktiiviset workflow-moduulit."""
    yamls = sorted(
        list(Path("workflows").glob("*.yaml"))
        + list(Path("workflows").glob("*.yml"))
        + list(Path(".prompts").glob("*.yaml"))
    )
    workflow_modules: list[str] = []
    try:
        import workflows as wf_pkg  # type: ignore

        wf_dir = Path(wf_pkg.__file__).parent if wf_pkg.__file__ else None
        if wf_dir is not None:
            workflow_modules = [p.stem for p in wf_dir.glob("*.py") if p.stem != "__init__"]
    except Exception:
        pass

    if _JSON:
        print(
            json.dumps(
                {
                    "command": "harness",
                    "yaml_harnesses": [str(p) for p in yamls],
                    "workflow_modules": workflow_modules,
                },
                ensure_ascii=False,
            )
        )
        return

    rows: list[list[str]] = []
    for p in yamls:
        size = f"{p.stat().st_size} B"
        rows.append([
            paint(p.name, INK),
            paint(str(p.parent), DIM, STEEL),
            paint("yaml", COPPER),
            paint(size, STEEL),
        ])
    for mod in workflow_modules:
        rows.append([
            paint(f"{mod}.py", INK),
            paint("workflows", DIM, STEEL),
            paint("python", AMBER),
            paint("module", STEEL),
        ])
    if not rows:
        print(paint("  ei aktiivisia valjaita — aja /attach <tiedosto.yaml>", DIM, MUTED))
        return
    print(render_table(["ARTIFACT", "PATH", "KIND", "SIZE"], rows))


def _slash_clean(_arg: str) -> None:
    """Tyhjennä ruutu ja nollaa RAM-puolelle ladattu konteksti."""
    if sys.stdout.isatty():
        sys.stdout.write("\x1b[2J\x1b[H")
        sys.stdout.flush()
    _STATE.inference_ms = 0
    _STATE.tokens_per_s = 0.0
    _STATE.entropy = 0.0
    if _JSON:
        _emit({"command": "clean", "reset": True})
        return
    _eprint(paint("  konteksti-ikkuna tyhjennetty. harness pysyy engagedina.", DIM, MUTED))


def _slash_attach(arg: str) -> None:
    """Liitä .yaml tai .md tiedosto cognitive scaffoldiin."""
    target = arg.strip().strip('"').strip("'")
    if not target:
        _eprint(paint("  käyttö: /attach <polku.yaml | polku.md>", ERR_RED))
        return
    path = Path(target)
    if not path.exists():
        _eprint(paint(f"  virhe: tiedostoa ei ole olemassa: {path}", ERR_RED))
        return
    if path.suffix not in {".yaml", ".yml", ".md"}:
        _eprint(
            paint(
                f"  harness hylkäsi: vain .yaml (logiikka) ja .md (konteksti) "
                f"sallitaan, ei {path.suffix}",
                ERR_RED,
            )
        )
        return
    size = path.stat().st_size
    kind = "LOGIC (.yaml)" if path.suffix in {".yaml", ".yml"} else "CONTEXT (.md)"

    # Staattinen entropia-arvio: .yaml on deterministinen (matala),
    # .md on rikkaampi konteksti (korkeampi).
    _STATE.entropy = 0.08 if path.suffix in {".yaml", ".yml"} else 0.34
    _STATE.harness = "ENGAGED"

    if _JSON:
        print(
            json.dumps(
                {
                    "command": "attach",
                    "path": str(path),
                    "kind": kind,
                    "size_bytes": size,
                    "entropy": _STATE.entropy,
                },
                ensure_ascii=False,
            )
        )
        return

    print(render_table(
        headers=["ATTACHMENT", "KIND", "SIZE", "ENTROPY"],
        rows=[[
            paint(str(path), INK),
            paint(kind, COPPER),
            paint(f"{size} B", STEEL),
            paint(f"{_STATE.entropy:.2f}", AMBER),
        ]],
    ))


def _slash_whoami(arg: str) -> None:
    """Toista Achiin alkuperätarina REPL-slashina.

    ``--fast`` -lippu ohittaa typewriter-viiveen. ``--json`` emittoi
    parsitut palat strukturoituna.
    """
    fast = "--fast" in arg.split()
    if _JSON:
        parts = _iter_story_lines()
        payload = {
            "command": "whoami",
            "script": ".prompts/origin_story.md",
            "segments": [{"kind": k, "text": t} for k, t in parts],
        }
        print(json.dumps(payload, ensure_ascii=False))
        return
    play_origin_story(fast=fast)


def _slash_logs(arg: str) -> None:
    """Viimeisimmät auditoitavat lokimerkinnät evolution_log / outputs -kansiosta."""
    tail = 20
    parts = arg.split()
    if "--tail" in parts:
        i = parts.index("--tail")
        if i + 1 < len(parts):
            try:
                tail = max(1, int(parts[i + 1]))
            except ValueError:
                pass

    entries: list[dict[str, Any]] = []
    log_path = Path("evolution_log.jsonl")
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines()[-tail:]:
            try:
                entries.append(json.loads(line))
            except Exception:
                entries.append({"raw": line})

    reports = sorted(Path("outputs").glob("agent_print_*.json"))[-tail:]
    for r in reports:
        try:
            data = json.loads(r.read_text(encoding="utf-8"))
            entries.append({
                "source": "agent_print",
                "file": r.name,
                "task_id": data.get("task_id"),
                "success": data.get("success"),
            })
        except Exception:
            continue

    if _JSON:
        print(json.dumps({"command": "logs", "tail": tail, "entries": entries}, ensure_ascii=False))
        return

    if not entries:
        print(paint("  ei lokimerkintöjä. aja /harness tai `run` aloittaaksesi.", DIM, MUTED))
        return

    print(rule(f"logs · viimeiset {len(entries)} merkintää"))
    for e in entries:
        if "raw" in e:
            print(paint("  " + e["raw"], DIM, MUTED))
            continue
        ts = e.get("ts") or e.get("timestamp") or "-"
        msg = (
            e.get("message")
            or e.get("event")
            or e.get("task_id")
            or e.get("file")
            or json.dumps({k: v for k, v in e.items() if k != "raw"}, ensure_ascii=False)
        )
        print("  " + paint(str(ts), DIM, STEEL) + "  " + paint(str(msg), INK))


_SLASH: dict[str, Callable[[str], None]] = {
    "/status": _slash_status,
    "/harness": _slash_harness,
    "/clean": _slash_clean,
    "/attach": _slash_attach,
    "/logs": _slash_logs,
    "/whoami": _slash_whoami,
    "/start": lambda _arg: _eprint(
        paint("  harness engaged. kirjoita /status tai run \"tehtävä\" aloittaaksesi.", DIM, MUTED)
    ),
}


def dispatch_slash(line: str) -> bool:
    """Yritä tulkita syöte slash-komentona. Palauta True jos dispatchattiin."""
    stripped = line.strip()
    if not stripped.startswith("/"):
        return False
    head, _, rest = stripped.partition(" ")
    handler = _SLASH.get(head)
    if handler is None:
        _eprint(
            paint(f"  tuntematon slash-komento: {head}. yritä: ", ERR_RED)
            + paint(" ".join(sorted(_SLASH.keys())), DIM, MUTED)
        )
        return True
    handler(rest)
    return True


# ─────────────────────────────────────────────────────────────────────────────
#  REPL
# ─────────────────────────────────────────────────────────────────────────────

def repl_mode(parser: argparse.ArgumentParser) -> None:
    print_logo()
    _STATE.harness = "ENGAGED"
    _STATE.achii = "AWAKE"

    while True:
        try:
            if sys.stdout.isatty() and not _JSON:
                print(render_status_bar(_STATE))
            user_input = input(prompt_prefix(_STATE)).strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print(paint("  harness disengaged. näkemiin.", DIM, MUTED))
                break

            if dispatch_slash(user_input):
                continue

            if user_input.lower() == "status":
                _slash_status("")
                continue

            if user_input.lower() in ("help", "?"):
                _print_help()
                continue

            if user_input.lower() == "plugins":
                import hooks

                active_hooks_count = sum(len(h) for h in hooks._hooks.values())
                plugins = [m for m in sys.modules.keys() if m.startswith("agentdir_plugin_")]
                print(rule("sovereign plugins"))
                print(kv([
                    ("aktiiviset hook-tapahtumat", str(active_hooks_count)),
                    (
                        "yhteisölaajennukset",
                        str(len(plugins)) if plugins
                        else "ei ladattuja · lisää .py plugins/-kansioon",
                    ),
                ]))
                for p in plugins:
                    print(
                        "  "
                        + paint("·", COPPER)
                        + " "
                        + paint(p.replace("agentdir_plugin_", ""), INK)
                    )
                continue

            if user_input.lower().startswith("hermes "):
                query = user_input[7:].strip().strip('"')
                if query:
                    _run_hermes(query)
                else:
                    _eprint(paint('käyttö: hermes "tutkimuskysymys"', DIM, MUTED))
                continue

            if user_input.lower().startswith("openclaw "):
                task = user_input[9:].strip().strip('"')
                if task:
                    _run_openclaw(task)
                else:
                    _eprint(paint('käyttö: openclaw "analyysitehtävä"', DIM, MUTED))
                continue

            # Delegoi loput argparse-parserille (run, init, benchmark, print…)
            args_list = shlex.split(user_input)
            try:
                args = parser.parse_args(args_list)
                execute_command(args, parser)
            except SystemExit:
                pass
        except (KeyboardInterrupt, EOFError):
            print("\n" + paint("  harness disengaged. näkemiin.", DIM, MUTED))
            break


# ─────────────────────────────────────────────────────────────────────────────
#  Argument parser + execute
# ─────────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentdir",
        description=(
            "AgentDir Sovereign Engine — lokaali harness-arkkitehtuuri. "
            ".yaml = logiikka, .md = konteksti."
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="näytä kognitiivinen prosessitrace (.yaml-rajaukset reaaliajassa)",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="emit konekieliversio (putkitettavaksi jq:lle)",
    )
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="aja orkestroitu tehtävä")
    run_p.add_argument("task", help="tehtävän kuvaus")
    run_p.add_argument(
        "--mode",
        choices=["openclaw", "hermes"],
        default="openclaw",
        help="workflow-moodi (oletus: openclaw)",
    )
    run_p.add_argument(
        "--model",
        default="auto",
        help="mallitunnus tai 'auto' (ModelRouter valitsee)",
    )

    init_p = sub.add_parser("init", help="alusta AgentDir-rakenne kansioon")
    init_p.add_argument("--path", default=".", help="kohdehakemisto (oletus: nykyinen)")

    sub.add_parser("status", help="tulosta moottorin tila")
    sub.add_parser("benchmark", help="aja suorituskykytestit")
    sub.add_parser("harness", help="listaa aktiiviset .yaml-valjaat")
    sub.add_parser("clean", help="tyhjennä konteksti-ikkuna")

    attach_p = sub.add_parser("attach", help="liitä .yaml / .md cognitive scaffoldiin")
    attach_p.add_argument("path", help="polku tiedostoon")

    logs_p = sub.add_parser("logs", help="näytä viimeisimmät lokimerkinnät")
    logs_p.add_argument("--tail", type=int, default=20, help="rivien määrä (oletus: 20)")

    achii_p = sub.add_parser("achii", help="achii-alijärjestelmä (alkuperätarina · sielu)")
    achii_p.add_argument(
        "--whoami",
        action="store_true",
        help="toista The Fallen Sovereign -alkuperätarina",
    )
    achii_p.add_argument(
        "--fast",
        action="store_true",
        help="ohita typewriter-viive (CI / scripted)",
    )

    print_p = sub.add_parser("print", help="tulosta Agent Print -raportti")
    print_p.add_argument("--task-id", default="latest", help="tehtävän ID tai 'latest'")

    parser.exit_on_error = False
    return parser


def main(argv: list[str] | None = None) -> None:
    global _VERBOSE, _JSON  # noqa: PLW0603

    parser = _build_parser()
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv:
        repl_mode(parser)
        return

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return
    except argparse.ArgumentError as exc:
        _eprint(paint(f"argument error: {exc}", ERR_RED))
        return

    _VERBOSE = bool(getattr(args, "verbose", False))
    _JSON = bool(getattr(args, "json_output", False))

    _vlog("harness", f"mode={getattr(args, 'mode', '-')} json={_JSON} verbose={_VERBOSE}")

    execute_command(args, parser)


def execute_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    cmd = getattr(args, "command", None)

    if cmd == "run":
        from orchestrator import WorkflowOrchestrator

        _vlog("run", f'mode={args.mode} model={args.model} task="{args.task[:60]}"')
        _eprint(paint(f"[sovereign] mode={args.mode} model={args.model}", COPPER, BOLD))
        orch = WorkflowOrchestrator(mode=args.mode)
        started = time.monotonic()
        result = orch.run(task=args.task, model=args.model)
        _STATE.inference_ms = int((time.monotonic() - started) * 1000)
        if _JSON:
            print(json.dumps({"command": "run", "result": result}, ensure_ascii=False))
        else:
            print(rule("run · tulos"))
            print(result.get("summary", "ei tulosta."))
        return

    if cmd == "init":
        from workspace.init_structure import init_project

        init_project(args.path)
        if _JSON:
            print(json.dumps({"command": "init", "path": args.path, "ok": True}, ensure_ascii=False))
        return

    if cmd == "status":
        if _JSON:
            print(cmd_status_json())
        else:
            print(cmd_status())
        return

    if cmd == "benchmark":
        from workspace.benchmark import run_benchmarks

        run_benchmarks()
        return

    if cmd == "harness":
        _slash_harness("")
        return

    if cmd == "clean":
        _slash_clean("")
        return

    if cmd == "attach":
        _slash_attach(args.path)
        return

    if cmd == "logs":
        _slash_logs(f"--tail {args.tail}")
        return

    if cmd == "achii":
        if not getattr(args, "whoami", False):
            _eprint(paint("käyttö: agentdir achii --whoami [--fast]", DIM, MUTED))
            return
        if _JSON:
            _slash_whoami("--fast" if args.fast else "")
            return
        play_origin_story(fast=bool(args.fast))
        return

    if cmd == "print":
        reports = sorted(Path("outputs").glob("agent_print_*.json"))
        if not reports:
            _eprint(paint("ei Agent Print -raportteja outputs/-kansiossa.", DIM, MUTED))
            return
        data = json.loads(reports[-1].read_text(encoding="utf-8"))
        if _JSON:
            print(json.dumps({"command": "print", "data": data}, ensure_ascii=False))
            return
        print(rule(f"agent print · {reports[-1].name}"))
        print(kv([(str(k), str(v)) for k, v in data.items()]))
        return

    # Ei komentoa: näytä banner + help
    print_logo()
    _print_help()


if __name__ == "__main__":
    main()
