#!/usr/bin/env python3
"""
AgentDir 3.5 CLI — Sovereign Engine
Käyttö: python cli.py <komento> [optiot]

Aloituspiste kaikille AgentDir 3.5 -komennoille.
Delegoi kaikki logiikka orkestraattorille ja workspace-moduuleille.
"""
from __future__ import annotations

import argparse
import sys
import shlex
from pathlib import Path

# Pakotetaan UTF-8 koodaus, jotta hienot ASCII-boxit toimivat Windows-terminaalissa
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass



def cmd_status() -> str:
    """
    Palauttaa värikoodatun yleiskuvan moottorin tilasta.
    Hakee tiedot suoraan moduuleista ja tiedostojärjestelmästä.
    """
    root = Path(".")

    # Ollama-tila
    try:
        import subprocess
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        model_ok = "gemma" in result.stdout.lower()
        model_name = "gemma4:e4b" if model_ok else "ei löydy"
    except Exception:
        model_ok = False
        model_name = "ollama offline"
    model_icon = "\033[92m●\033[0m" if model_ok else "\033[91m●\033[0m"

    # RAG-tila
    try:
        import json as _json
        cfg = _json.loads((root / "config.json").read_text(encoding="utf-8"))
        from rag_memory import RAGMemory
        rag = RAGMemory(cfg, memory_path=str(root / "memory"))
        rag_docs = rag.count()
    except Exception:
        rag_docs = 0
    rag_icon = "\033[92m●\033[0m" if rag_docs > 0 else "\033[93m●\033[0m"

    # Evoluutio
    try:
        from evolution_engine import EvolutionEngine
        import json as _json
        cfg = _json.loads((root / "config.json").read_text(encoding="utf-8"))
        ev = EvolutionEngine(cfg, str(root / "config.json"))
        stats = ev.get_stats()
    except Exception:
        stats = {"total_tasks": 0, "success_rate": 0.0, "prompt_version": "?"}
    evo_tasks = stats.get("total_tasks", 0)
    evo_rate = stats.get("success_rate", 0)
    if isinstance(evo_rate, float) and evo_rate <= 1.0:
        evo_rate = evo_rate * 100
    evo_ver = stats.get("prompt_version", "?")
    if evo_rate >= 70:
        evo_icon = "\033[92m●\033[0m"
    elif evo_rate >= 40:
        evo_icon = "\033[93m●\033[0m"
    else:
        evo_icon = "\033[91m●\033[0m"

    # Inbox/Outbox
    inbox_count = len([f for f in (root / "Inbox").glob("*") if f.is_file() and f.name != ".gitkeep"])
    outbox_count = len([f for f in (root / "Outbox").glob("*") if f.is_file() and f.name != ".gitkeep"])

    return f"""
\033[96m┌─ SOVEREIGN ENGINE STATUS ────────────────────────────────────┐\033[0m
│                                                               │
│  {model_icon} MODEL      {model_name:<44}│
│  {rag_icon} RAG        {rag_docs} documents indexed{' '*(27 - len(str(rag_docs)))}│
│  {evo_icon} EVOLUTION  {evo_ver} │ {evo_tasks} tasks │ {evo_rate:.0f}% success{' '*(14 - len(str(evo_tasks)))}│
│                                                               │
│  📥 INBOX    {inbox_count} pending{' '*(45 - len(str(inbox_count)))}│
│  📤 OUTBOX   {outbox_count} completed{' '*(43 - len(str(outbox_count)))}│
│                                                               │
\033[96m└───────────────────────────────────────────────────────────────┘\033[0m
"""

def print_logo() -> None:
    print("\033[96m")
    print(r"╔═══════════════════════════════════════════════════════════════╗")
    print(r"║                                                               ║")
    print(r"║    ▄▀█ █▀▀ █▀▀ █▄ █ ▀█▀ █▀▄ █ █▀█                           ║")
    print(r"║    █▀█ █▄█ ██▄ █ ▀█  █  █▄▀ █ █▀▄                           ║")
    print(r"║                                                               ║")
    print(r"║    SOVEREIGN ENGINE  3.5.1 ·  LOCAL-FIRST  ·  GEMMA4          ║")
    print(r"║    ─────────────────────────────────────────────────────     ║")
    print(r"║    Type  'help'  for commands  │  'status'  for telemetry    ║")
    print(r"║    'hermes'  research  │  'openclaw'  deep analysis          ║")
    print(r"║                                                               ║")
    print(r"╚═══════════════════════════════════════════════════════════════╝" + "\033[0m")
    print()


def _get_llm_and_rag():
    """Luo jaetut LLM- ja RAG-instanssit työnkuluille."""
    import json
    cfg = json.loads(Path("config.json").read_text(encoding="utf-8"))
    from llm_client import LLMClient
    from rag_memory import RAGMemory
    llm = LLMClient(cfg)
    rag = RAGMemory(cfg, memory_path="memory")
    return llm, rag, cfg


def _run_hermes(query: str) -> None:
    """Aja Hermes-iteratiivinen tutkimus suoraan REPL:stä."""
    import asyncio
    print(f"\n\033[95m[Hermes] Aloitetaan iteratiivinen tutkimus...\033[0m")
    try:
        llm, rag, _ = _get_llm_and_rag()
        from workflows.hermes import HermesWorkflow
        wf = HermesWorkflow(llm, rag)
        result = asyncio.run(wf.run(query, max_iterations=3))
        print(f"\n\033[92m[Hermes] Tulos:\033[0m\n{result}\n")
    except Exception as e:
        print(f"\033[91m[Hermes] Virhe: {e}\033[0m\n")


def _run_openclaw(task: str) -> None:
    """Aja OpenClaw-syväanalyysi suoraan REPL:stä."""
    import asyncio
    print(f"\n\033[96m[OpenClaw] Aloitetaan monivaiheinen syväanalyysi...\033[0m")
    try:
        llm, rag, _ = _get_llm_and_rag()
        from workflows.openclaw import OpenClawWorkflow
        wf = OpenClawWorkflow(llm, rag)
        result = asyncio.run(wf.run(task))
        print(f"\n\033[92m[OpenClaw] Tulos:\033[0m\n{result}\n")
    except Exception as e:
        print(f"\033[91m[OpenClaw] Virhe: {e}\033[0m\n")

def repl_mode(parser: argparse.ArgumentParser) -> None:
    print_logo()
    print("Tervetuloa Sovereign CLI -tilaan. Kirjoita 'help' nähdäksesi komennot tai 'exit' poistuaksesi.")
    while True:
        try:
            # Käytetään vihreää promptia
            user_input = input("\033[92mAgentDir>\033[0m ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Lopetetaan Sovereign CLI. Näkemiin.")
                break

            # Suorat REPL-komennot (ei tarvitse argparsea)
            if user_input.lower() == "status":
                print(cmd_status())
                continue
            if user_input.lower() == "help":
                print("\033[96m")
                print("  Komennot:")
                print("  ─────────────────────────────────────────")
                print('  run "tehtävä"    — Suorita tehtävä LLM:llä')
                print('  hermes "kysymys" — Iteratiivinen tutkimus (Hermes)')
                print('  openclaw "task"  — Syväanalyysi (OpenClaw)')
                print("  status           — Näytä moottorin tila")
                print("  print            — Näytä viimeisin Agent Print")
                print("  benchmark        — Aja suorituskykytestit")
                print("  init             — Alusta projektirakenne")
                print("  exit / quit      — Sulje CLI")
                print("\033[0m")
                continue

            # Hermes: iteratiivinen tutkimus
            if user_input.lower().startswith("hermes "):
                query = user_input[7:].strip().strip('"')
                if query:
                    _run_hermes(query)
                else:
                    print("Käyttö: hermes \"tutkimuskysymys\"")
                continue

            # OpenClaw: syväanalyysi
            if user_input.lower().startswith("openclaw "):
                task = user_input[9:].strip().strip('"')
                if task:
                    _run_openclaw(task)
                else:
                    print('Käyttö: openclaw "analyysitehtävä"')
                continue

            # Ohitetaan parserin sys.exit(), kun annetaan virheellinen komento REPL:ssä
            args_list = shlex.split(user_input)
            try:
                args = parser.parse_args(args_list)
                execute_command(args, parser)
            except SystemExit:
                pass  # argparse heittää SystemExit virheistä
        except (KeyboardInterrupt, EOFError):
            print("\nLopetetaan Sovereign CLI.")
            break



def main() -> None:
    parser = argparse.ArgumentParser(
        prog="agentdir",
        description="AgentDir 3.5 Sovereign Engine — kognitiivinen tiedostojärjestelmä",
    )
    sub = parser.add_subparsers(dest="command")

    # --- RUN ---
    run_p = sub.add_parser("run", help="Suorita tehtävä")
    run_p.add_argument("task", help="Tehtävän kuvaus")
    run_p.add_argument(
        "--mode",
        choices=["openclaw", "hermes"],
        default="openclaw",
        help="Workflow-moodi (oletus: openclaw)",
    )
    run_p.add_argument(
        "--model",
        default="auto",
        help="Mallitunnus tai 'auto' (ModelRouter valitsee)",
    )

    # --- INIT ---
    init_p = sub.add_parser("init", help="Alusta AgentDir 3.5 -rakenne kansioon")
    init_p.add_argument(
        "--path",
        default=".",
        help="Kohdehakemisto (oletus: nykyinen)",
    )

    # --- STATUS ---
    sub.add_parser("status", help="Näytä parven ja solmujen tila")

    # --- BENCHMARK ---
    sub.add_parser("benchmark", help="Aja suorituskykytestit")

    # --- PRINT ---
    print_p = sub.add_parser("print", help="Generoi Agent Print -raportti")
    print_p.add_argument("--task-id", default="latest", help="Tehtävän ID tai 'latest'")

    # Estetään argparsea kaatamasta REPLiä oletuksena
    parser.exit_on_error = False

    # Jos argumentteja ei annettu komentoriviltä, käynnistä REPL
    if len(sys.argv) == 1:
        repl_mode(parser)
        return

    try:
        args = parser.parse_args()
        execute_command(args, parser)
    except SystemExit:
        pass

def execute_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if getattr(args, "command", None) == "run":
        from orchestrator import WorkflowOrchestrator

        print(f"\n\033[96m[Sovereign] Suoritetaan tehtävä (Mode: {args.mode}, Model: {args.model})\033[0m")
        orch = WorkflowOrchestrator(mode=args.mode)
        result = orch.run(task=args.task, model=args.model)
        print(f"\n\033[92m[Tulokset]\033[0m\n{result.get('summary', 'Ei tulosta.')}\n")

    elif getattr(args, "command", None) == "init":
        from workspace.init_structure import init_project

        init_project(args.path)

    elif getattr(args, "command", None) == "status":
        from orchestrator import WorkflowOrchestrator

        orch = WorkflowOrchestrator()
        orch.status()

    elif getattr(args, "command", None) == "benchmark":
        from workspace.benchmark import run_benchmarks

        run_benchmarks()

    elif getattr(args, "command", None) == "print":
        from workspace.agent_print import AgentPrint

        ap = AgentPrint()
        # Näytä viimeisin raportti tulostekansiosta
        import json
        from pathlib import Path

        reports = sorted(Path("outputs").glob("agent_print_*.json"))
        if reports:
            data = json.loads(reports[-1].read_text(encoding="utf-8"))
            for k, v in data.items():
                print(f"  {k}: {v}")
        else:
            print("Ei Agent Print -raportteja outputs/ -kansiossa.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
