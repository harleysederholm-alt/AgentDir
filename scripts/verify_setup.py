#!/usr/bin/env python3
"""
Paikallinen tarkistus: Python-paketit, config.json-mallit vs. ollama list, LLM-yhteys.
Aja projektin juuresta: python verify_setup.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def ollama_models() -> set[str]:
    try:
        out = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        print("FAIL: ollama-komentoa ei löydy PATH:sta.")
        return set()
    except subprocess.TimeoutExpired:
        print("FAIL: ollama list aikakatkaistiin.")
        return set()
    if out.returncode != 0:
        print("FAIL: ollama list epäonnistui:", out.stderr or out.stdout)
        return set()
    names: set[str] = set()
    for line in out.stdout.splitlines()[1:]:
        parts = line.split()
        if parts:
            names.add(parts[0].strip())
    return names


def model_installed(name: str, installed: set[str]) -> bool:
    if name in installed:
        return True
    base = name.split(":")[0]
    for i in installed:
        if i == name or (":" in name and i == name):
            return True
        if i.startswith(base + ":"):
            return True
    return False


def collect_required_models(cfg: dict) -> list[str]:
    req: list[str] = []
    llm = cfg.get("llm", {}).get("model")
    if llm:
        req.append(llm)
    emb = cfg.get("embedding", {}).get("model")
    if emb:
        req.append(emb)
    fb = cfg.get("embedding", {}).get("fallback")
    if fb:
        req.append(fb)
    for m in cfg.get("llm", {}).get("fallback_models") or []:
        if m and m not in req:
            req.append(m)
    return req


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
    print("AgentDir verify_setup\n" + "-" * 40)
    cfg_path = ROOT / "config.json"
    if not cfg_path.exists():
        print("FAIL: config.json puuttuu.")
        return 1
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    installed = ollama_models()
    if not installed:
        return 1

    for m in collect_required_models(cfg):
        if model_installed(m, installed):
            print(f"Malli '{m}': löytyy")
        else:
            print(f"WARN: mallia '{m}' ei löydy ollama list -tulosteesta – aja: ollama pull {m}")

    try:
        sys.path.insert(0, str(ROOT))
        from llm_client import LLMClient

        llm = LLMClient(cfg)
        ok = llm.check_connection()
        print(f"LLM endpoint: {'OK' if ok else 'FAIL'}")
        if not ok:
            return 1
    except Exception as e:
        print("FAIL: LLMClient:", e)
        return 1

    try:
        from rag_memory import OllamaEmbedder

        emb = cfg.get("embedding", {})
        oe = OllamaEmbedder(emb.get("endpoint", ""), emb.get("model", ""))
        if oe.is_available():
            print(f"Embedding ({emb.get('model')}): OK")
        else:
            print(f"WARN: Ollama-embedding ei vastaa – RAG käyttää ChromaDB-fallbackia.")
    except Exception as e:
        print("WARN: embedding-tarkistus:", e)

    print("-" * 40)
    print("OK: perustarkistukset läpäisty.")
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)
    raise SystemExit(main())
