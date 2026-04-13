"""
tests/test_agent_print.py — Testit Agent Print -raportointijärjestelmälle.
"""
import json
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "workspace"))

from agent_print import AgentPrint


def test_generates_json_md_and_txt(tmp_path):
    """Luo JSON, MD ja Pro-Audit TXT tiedostot."""
    printer = AgentPrint(str(tmp_path))
    print_id = printer.generate(
        task="Analysoi data.csv",
        model="gemma4:e4b",
        input_file="Inbox/data.csv",
        output_file="Outbox/raportti.md",
        rag_hits=3,
        sandbox_attempts=1,
        sandbox_success=True,
        execution_ms=234,
    )

    assert (tmp_path / f"agent_print_{print_id}.json").exists()
    assert (tmp_path / f"agent_print_{print_id}.md").exists()
    assert (tmp_path / f"agent_print_{print_id}.txt").exists()


def test_pro_audit_contains_hash(tmp_path):
    """Pro-Audit TXT sisältää SHA-256 hash."""
    printer = AgentPrint(str(tmp_path))
    print_id = printer.generate(
        task="Testi SHA",
        model="gemma4:e4b",
        input_file="in",
        output_file="out",
        sandbox_success=True,
    )
    txt = (tmp_path / f"agent_print_{print_id}.txt").read_text(encoding="utf-8")
    assert "SHA-256:" in txt
    assert "SOVEREIGN ENGINE" in txt


def test_stats_empty(tmp_path):
    """Tyhjä stats ilman raportteja."""
    printer = AgentPrint(str(tmp_path))
    stats = printer.get_stats()
    assert stats["total_tasks"] == 0


def test_stats_with_records(tmp_path):
    """Stats laskee oikein useista raporteista."""
    printer = AgentPrint(str(tmp_path))
    printer.generate(
        task="task1",
        model="gemma4:e4b",
        input_file="in1",
        output_file="out1",
        sandbox_success=True,
    )
    printer.generate(
        task="task2",
        model="gemma4:e4b",
        input_file="in2",
        output_file="out2",
        sandbox_success=False,
    )

    stats = printer.get_stats()
    assert stats["total_tasks"] == 2
    assert stats["success_rate"] == 0.5


def test_backwards_compat_with_result_dict(tmp_path):
    """Vanha rajapinta (result-dict) toimii yhä."""
    printer = AgentPrint(str(tmp_path))
    result = {"success": True, "sandbox_ok": True, "token_savings": 0}
    print_id = printer.generate(
        task="Vanha kutsu",
        result=result,
        model="ollama/gemma4:e4b",
        mode="openclaw",
    )
    assert print_id
    json_file = tmp_path / f"agent_print_{print_id}.json"
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert data["sandbox_success"] is True
