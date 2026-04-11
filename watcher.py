#!/usr/bin/env python3
"""
AgentDir v1.1 – Hermosto (Watcher)
====================================
Parannukset v1.0:sta:
✅ Config hot-reload (ConfigManager) – muutokset tulevat voimaan lennossa
✅ Lazy loading – raskaat moduulit ladataan vasta ensimmäisellä käytöllä
✅ AST-pohjainen sandbox (korvaa naiivin pattern-matching)
✅ Kaikki bugit v1.0:sta korjattu (swarm-loop, embedding API, debounce)
"""

from __future__ import annotations

import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("agentdir.watcher")

ROOT_DIR    = Path(".")
CONFIG_PATH = ROOT_DIR / "config.json"

if not CONFIG_PATH.exists():
    logger.error("config.json puuttuu!")
    sys.exit(1)

# ── Hot-reload config ─────────────────────────────────────────────────────────
from config_manager import ConfigManager
cfg = ConfigManager(CONFIG_PATH)
cfg.watch(interval=3.0)

INBOX  = ROOT_DIR / "Inbox"
OUTBOX = ROOT_DIR / "Outbox"
MEMORY = ROOT_DIR / "memory"
for d in [INBOX, OUTBOX, MEMORY]:
    d.mkdir(exist_ok=True)

# ── Lazy-loaded moduulit ──────────────────────────────────────────────────────
from rag_memory       import RAGMemory
from llm_client       import LLMClient
from file_parser      import parse, SUPPORTED
from sandbox_executor import execute as sandbox_exec
from swarm_manager    import SwarmManager, should_swarm
from evolution_engine import EvolutionEngine

try:
    import hooks

    hooks.load_plugins()
except Exception as e:
    hooks = None  # type: ignore[assignment]
    logger.warning("Plugin-lataus: %s", e)

try:
    from watchdog.observers import Observer
    from watchdog.events    import FileSystemEventHandler
except ImportError:
    logger.error("watchdog puuttuu: pip install watchdog")
    sys.exit(1)

# ── Komponentit (alustetaan kerran käynnistyksessä) ───────────────────────────
_rag       : RAGMemory       | None = None
_llm       : LLMClient       | None = None
_swarm     : SwarmManager    | None = None
_evolution : EvolutionEngine | None = None


def _get_rag() -> RAGMemory:
    global _rag
    if _rag is None:
        _rag = RAGMemory(cfg.all())
    return _rag


def _get_llm() -> LLMClient:
    global _llm
    if _llm is None:
        _llm = LLMClient(cfg.all())
    # Päivitä config jos se on muuttunut
    _llm.cfg = cfg.get("llm", {})
    return _llm


def _get_swarm() -> SwarmManager:
    global _swarm
    if _swarm is None:
        _swarm = SwarmManager(cfg.all(), ROOT_DIR)
    return _swarm


def _get_evolution() -> EvolutionEngine:
    global _evolution
    if _evolution is None:
        _evolution = EvolutionEngine(cfg.all(), str(CONFIG_PATH))
    return _evolution


# Nollaa komponentit jos config muuttuu merkittävästi
def _on_config_change(new_cfg: dict):
    global _llm
    logger.info("Config muuttui → LLM-asiakas päivitetään")
    _llm = None  # lazy-reload seuraavalla kutsulla


cfg.on_change(_on_config_change)

# ── Debounce ──────────────────────────────────────────────────────────────────
_processing: set[str] = set()

# ── Apufunktiot ───────────────────────────────────────────────────────────────

def build_prompt(content: str, context: str) -> str:
    template = cfg.get("prompt_templates.default", "")
    if not template:
        template = "Olet {role}.\n\nKonteksti:\n{context}\n\nTehtävä:\n{content}"
    return template.format(
        role=cfg.get("role", "Älykäs avustaja"),
        context=context or "Ei aiempaa kontekstia.",
        content=content,
    )


def build_code_prompt(content: str, context: str) -> str:
    template = cfg.get("prompt_templates.code", "")
    if not template:
        return build_prompt(content, context)
    return template.format(
        role=cfg.get("role", "Koodari"),
        context=context or "",
        content=content,
    )


def needs_code(content: str) -> bool:
    keywords = ["tee graafi", "luo kaavio", "laske", "analysoi numerot",
                 "visualisoi", "plot", "chart", "calculate", "make graph",
                 "kirjoita koodi", "python-skripti"]
    return any(kw in content.lower() for kw in keywords)


def process_with_self_correction(content: str, file_name: str) -> tuple[str, bool]:
    """Käsittele sisältö + itsekorjaus koodille. Palauttaa (tulos, success)."""
    import json as _json

    max_attempts = cfg.get("sandbox.max_correction_attempts", 3)
    if not cfg.get("sandbox.enabled", True):
        max_attempts = 1

    rag       = _get_rag()
    llm       = _get_llm()
    n_results = cfg.get("rag.n_results", 3)
    context   = rag.query(content[:1000], n_results=n_results)

    use_code  = needs_code(content)
    prompt    = build_code_prompt(content, context) if use_code else build_prompt(content, context)

    attempt, last_result, success = 0, "", False

    while attempt < max_attempts:
        attempt += 1
        logger.info("Käsittely yritys %d/%d...", attempt, max_attempts)
        raw = llm.complete(prompt)
        last_result = raw

        if raw.startswith("❌"):
            return raw, False

        if use_code:
            parsed = None
            match  = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    parsed = _json.loads(match.group(0))
                except Exception:
                    pass

            code = (parsed or {}).get("code", "")
            if code and code not in ("null", "None", ""):
                exec_result = sandbox_exec(
                    code,
                    timeout=cfg.get("sandbox.timeout_seconds", 30),
                )
                if exec_result["success"]:
                    out  = exec_result["output"]
                    ans  = (parsed or {}).get("final_answer", raw)
                    last_result = f"{ans}\n\n**Suorituksen tulos:**\n```\n{out}\n```"
                    success = True
                    break
                else:
                    err = exec_result["error"]
                    logger.warning("Koodivirhe (yritys %d): %s", attempt, err[:150])
                    prompt += f"\n\nEdellinen koodi kaatui:\n{err}\n\nKorjaa koodi."
                    continue
            else:
                success = "❌" not in raw
                break
        else:
            success = "❌" not in raw
            break

    if attempt >= max_attempts and not success:
        last_result += f"\n\n⚠️ Itsekorjaus epäonnistui {max_attempts} yrityksen jälkeen."

    return last_result, success


# ── Watchdog ──────────────────────────────────────────────────────────────────

class AgentHandler(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory:
            return
        fp = Path(event.src_path)
        if fp.suffix.lower() not in SUPPORTED:
            return
        key = str(fp.resolve())
        if key in _processing:
            return
        _processing.add(key)
        debounce = cfg.get("watchdog.debounce_seconds", 1.0)
        time.sleep(debounce)
        try:
            self._handle(fp)
        except Exception as e:
            logger.error("Käsittelyvirhe '%s': %s", fp.name, e, exc_info=True)
        finally:
            _processing.discard(key)

    def _handle(self, file_path: Path):
        print(f"\n{'='*60}")
        print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] {file_path.name}")
        print(f"{'='*60}")

        try:
            content = parse(file_path)
        except (ValueError, RuntimeError) as e:
            logger.error("Parsausvirhe: %s", e)
            return
        if not content.strip():
            logger.warning("Tiedosto tyhjä: %s", file_path.name)
            return

        if hooks is not None:
            try:
                hooks.emit("after_file_parsed", path=file_path, text=content)
            except Exception:
                logger.exception("Hook after_file_parsed")

        result, success = process_with_self_correction(content, file_path.name)

        # Swarm?
        if should_swarm(result, cfg.all()):
            child = _get_swarm().spawn_child(result, "Erikoisanalyytikko", file_path.name)
            if child:
                result += f"\n\n🚀 Swarm-lapsi: `{child.name}`"

        # Tallenna Outboxiin
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = OUTBOX / f"{ts}_{file_path.stem}.md"
        header   = (
            f"# {file_path.name}\n"
            f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"{cfg.get('name','Agent')} – {cfg.get('role','')}*\n\n---\n\n"
        )
        out_file.write_text(header + result, encoding="utf-8")

        # RAG-muistiin
        doc_id = f"{ts}_{file_path.stem}"
        _get_rag().add(
            doc_id=doc_id,
            text=content[:3000] + "\n\n[VASTAUS]: " + result[:1000],
            metadata={"timestamp": ts, "input_file": file_path.name,
                      "result_file": out_file.name, "success": str(success)},
        )

        # Evoluutio
        _get_evolution().record(doc_id, content[:200], success)

        stats = _get_evolution().get_stats()
        print(f"✅ Valmis → {out_file.name}")
        print(
            f"📊 {stats['total_tasks']} tehtävää | "
            f"Onnistuminen: {stats['success_rate']:.0%} | "
            f"RAG: {_get_rag().count()} dok. | "
            f"Promptversio: {stats['prompt_version']}"
        )

        if hooks is not None:
            try:
                hooks.emit(
                    "after_task_completed",
                    path=file_path,
                    text=content,
                    result=result,
                    success=success,
                    out_file=out_file,
                )
            except Exception:
                logger.exception("Hook after_task_completed")


# ── Käynnistys ────────────────────────────────────────────────────────────────

def main():
    print("\n" + "🧬 " * 20)
    print("  AgentDir v1.1 – Elävä tiedostojärjestelmä")
    print("🧬 " * 20 + "\n")
    print(f"  Agentti   : {cfg.get('name')} – {cfg.get('role')}")
    print(f"  Malli     : {cfg.get('llm.model')} @ {cfg.get('llm.endpoint')}")
    print(f"  Inbox     : {INBOX.absolute()}")
    print(f"  Hot-reload: ✅ config.json tarkistetaan 3s välein")
    print(f"  RAG       : {'✅' if cfg.get('rag.enabled') else '⬜'}")
    print(f"  Sandbox   : {'✅ AST-pohjainen' if cfg.get('sandbox.enabled') else '⬜'}")
    print(f"  Swarm     : {'✅' if cfg.get('swarm.enabled') else '⬜'}")
    print(f"  Evoluutio : {'✅' if cfg.get('evolution.enabled') else '⬜'}")

    llm = _get_llm()
    if llm.check_connection():
        print(f"\n  LLM       : ✅ Yhdistetty\n")
    else:
        print(f"\n  LLM       : ⚠️  Ei yhteyttä – käynnistä Ollama: ollama serve\n")

    print("  Pudota tiedosto Inbox/-kansioon...\n")

    handler  = AgentHandler()
    observer = Observer()
    observer.schedule(handler, str(INBOX), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 AgentDir sammuu...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
