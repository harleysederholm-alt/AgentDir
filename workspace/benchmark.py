"""
benchmark.py — AgentDir 3.5 suorituskykytestit
Token-säästöt, viive, läpäisyprosentti.
"""
from __future__ import annotations

import json
import time
from pathlib import Path


def run_benchmarks() -> dict:
    """Aja kaikki benchmark-testit ja tallenna tulokset."""
    results: dict[str, object] = {}
    print("[BENCHMARK] AgentDir 3.5 Benchmark Suite\n")

    # Testi 1: Policy-portin nopeus (1000 tarkistusta)
    from workspace.policy import PolicyEngine

    p = PolicyEngine()
    t0 = time.perf_counter()
    for _ in range(1000):
        try:
            p.validate("analysoi tiedosto ja tee raportti")
        except Exception:
            pass
    results["policy_1000_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    print(f"  Policy gate (1000x): {results['policy_1000_ms']}ms")

    # Testi 2: Sandbox perussuoritus
    from workspace.sandbox import SovereignSandbox

    sb = SovereignSandbox()
    t0 = time.perf_counter()
    r = sb.execute("x = sum(range(1000)); print(x)")
    results["sandbox_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    results["sandbox_ok"] = r["success"]
    print(f"  Sandbox suoritus: {results['sandbox_ms']}ms | OK={r['success']}")

    # Testi 3: RAG-haku (100 dokumenttia)
    from workspace.rag import KnowledgeIndex

    idx = KnowledgeIndex()
    idx._index = {f"doc_{i}": f"sisältö aiheesta tekoäly {i} " * 20 for i in range(100)}
    t0 = time.perf_counter()
    idx.query("tekoäly 42")
    results["rag_100docs_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    print(f"  RAG-haku (100 dok): {results['rag_100docs_ms']}ms")

    # Testi 4: MemMachine STM kirjoitus/luku
    from workspace.memmachine import MemMachine

    mm = MemMachine()
    t0 = time.perf_counter()
    for i in range(100):
        mm.write_stm(f"key_{i}", f"value_{i}")
    for i in range(100):
        mm.read_stm(f"key_{i}")
    results["memmachine_100_rw_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    print(f"  MemMachine (100 r/w): {results['memmachine_100_rw_ms']}ms")

    # Tallenna tulokset
    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/benchmarks.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n[OK] Tulokset tallennettu: outputs/benchmarks.json")
    return results
