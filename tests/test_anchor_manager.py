"""
tests/test_anchor_manager.py — Testit kognitiiviselle ankkurijärjestelmälle.
"""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from anchor_manager import AnchorManager


def test_reads_local_anchor(tmp_path):
    """Lukee .agentdir.md paikallisesta kansiosta."""
    anchor = tmp_path / ".agentdir.md"
    anchor.write_text("## TARKOITUS\nTestikansio", encoding="utf-8")

    mgr = AnchorManager()
    ctx = mgr.get_context(tmp_path)
    assert "Testikansio" in ctx


def test_empty_without_anchor(tmp_path):
    """Palauttaa tyhjän jos ankkuria ei ole."""
    mgr = AnchorManager()
    ctx = mgr.get_context(tmp_path)
    assert ctx == ""


def test_creates_anchor(tmp_path):
    """Luo .agentdir.md kansioon."""
    mgr = AnchorManager()
    path = mgr.create_anchor(tmp_path, "Testikansion tarkoitus")
    assert path.exists()
    assert "Testikansion tarkoitus" in path.read_text(encoding="utf-8")


def test_finds_sovereign_from_subfolder(tmp_path):
    """Löytää !_SOVEREIGN.md ylöspäin hakemistopuussa."""
    sovereign = tmp_path / "!_SOVEREIGN.md"
    sovereign.write_text("Sovereign säännöt tässä", encoding="utf-8")

    sub = tmp_path / "sub" / "deep"
    sub.mkdir(parents=True)

    mgr = AnchorManager()
    ctx = mgr.get_context(sub)
    assert "Sovereign säännöt tässä" in ctx


def test_combines_sovereign_and_local(tmp_path):
    """Yhdistää globaalin ja paikallisen kontekstin."""
    sovereign = tmp_path / "!_SOVEREIGN.md"
    sovereign.write_text("Globaali sääntö", encoding="utf-8")

    local = tmp_path / ".agentdir.md"
    local.write_text("Paikallinen ohje", encoding="utf-8")

    mgr = AnchorManager()
    ctx = mgr.get_context(tmp_path)
    assert "Globaali sääntö" in ctx
    assert "Paikallinen ohje" in ctx
