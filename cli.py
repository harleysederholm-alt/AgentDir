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

    args = parser.parse_args()

    if args.command == "run":
        from orchestrator import WorkflowOrchestrator

        orch = WorkflowOrchestrator(mode=args.mode)
        result = orch.run(task=args.task, model=args.model)
        print(result.get("summary", "Ei tulosta."))

    elif args.command == "init":
        from workspace.init_structure import init_project

        init_project(args.path)

    elif args.command == "status":
        from orchestrator import WorkflowOrchestrator

        orch = WorkflowOrchestrator()
        orch.status()

    elif args.command == "benchmark":
        from workspace.benchmark import run_benchmarks

        run_benchmarks()

    elif args.command == "print":
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
