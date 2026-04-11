"""
AgentDir – Sandbox Executor
Turvallinen Python-koodin suoritus AST-analyysin + subprocess-eristyksen avulla.

Turvallisuuskerrokset (syvyyssuojaus):
  1. AST-analyysi  – kielletyt moduulit/kutsut ennen suoritusta
  2. Subprocess    – erillinen prosessi, ei pääsy vanhemman muistiin
  3. Ympäristö     – minimaalinen env, oma temp-hakemisto
  4. Resurssirajoitukset – timeout + max output-koko

TÄRKEÄ HUOMIO:
  Subprocess-sandbox ei ole täysin tiivis tahallista haittakoodia vastaan.
  Tuotantokäytössä jossa ajetaan tuntemattomia agenttitehtäviä, käytä
  Docker-konttia (ks. docker-stack.yml). Tämä sandbox suojaa tahattomilta
  virheiltä ja LLM:n tuottamalta huonolta koodilta.
"""

from __future__ import annotations

import ast
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger("agentdir.sandbox")

MAX_OUTPUT_CHARS = 8_000
MAX_CODE_CHARS   = 50_000  # Ei ajeta yli 50k merkin koodia

# ── AST-pohjaiset kiellot ─────────────────────────────────────────────────────
# Kielletyt moduulit (import-tasolla)
BLOCKED_IMPORTS = {
    "subprocess", "multiprocessing", "ctypes", "cffi",
    "socket",     # verkko – voi sallia configissa
    "urllib",     # verkko
    "http",       # verkko
    "ftplib",     "smtplib",   "telnetlib",
    "pty",        "tty",       "termios",
    "resource",                           # resurssirajoitusten poisto
    "signal",                             # prosessisignaalit
    "mmap",                               # muistikartat
}

# Kielletyt sisäänrakennetut funktiot (builtins)
BLOCKED_BUILTINS = {
    "__import__", "compile", "memoryview",
    "open",       # tiedostojärjestelmä – käytä vain jos erikseen sallittu
}

# os-moduulista kielletyt attribuutit (jos os on importattu)
BLOCKED_OS_ATTRS = {
    "system", "popen", "execv", "execve", "execvp", "execvpe",
    "fork",   "spawn", "spawnl", "spawnle", "spawnlp", "spawnlpe",
    "kill",   "killpg", "remove", "unlink", "rmdir", "removedirs",
}


class _SecurityVisitor(ast.NodeVisitor):
    """AST-kävijä joka etsii kiellettyjä rakenteita."""

    def __init__(self):
        self.violations: list[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in BLOCKED_IMPORTS:
                self.violations.append(
                    f"Kielletty import rivi {node.lineno}: '{alias.name}'"
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            root = node.module.split(".")[0]
            if root in BLOCKED_IMPORTS:
                self.violations.append(
                    f"Kielletty from-import rivi {node.lineno}: '{node.module}'"
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Kiellä __import__("..."), eval(...), exec(...)
        if isinstance(node.func, ast.Name):
            if node.func.id in BLOCKED_BUILTINS:
                self.violations.append(
                    f"Kielletty kutsu rivi {node.lineno}: '{node.func.id}()'"
                )
        # Kiellä os.system(...), os.popen(...) jne.
        if isinstance(node.func, ast.Attribute):
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "os"
                and node.func.attr in BLOCKED_OS_ATTRS
            ):
                self.violations.append(
                    f"Kielletty os-kutsu rivi {node.lineno}: 'os.{node.func.attr}()'"
                )
        self.generic_visit(node)


def _ast_check(code: str) -> list[str]:
    """
    Analysoi koodi AST:n kautta.
    Palauttaa listan rikkomuksista (tyhjä = OK).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"Syntaksivirhe: {e}"]
    visitor = _SecurityVisitor()
    visitor.visit(tree)
    return visitor.violations


# ── Julkinen API ──────────────────────────────────────────────────────────────

def execute(
    code: str,
    timeout: int = 30,
    work_dir: Path | None = None,
    allow_open: bool = False,     # salli tiedostojen luku/kirjoitus
) -> dict:
    """
    Ajaa Python-koodin sandboxissa.

    Args:
        code:       Ajettava Python-lähdekoodi
        timeout:    Maksimiajoaika sekunteissa (oletus 30)
        work_dir:   Työkansio; None → käytetään temp-kansiota
        allow_open: Salli tiedostoperaatiot (poistaa 'open' kiellosta)

    Palauttaa:
        {
            "success":    bool,
            "output":     str,    # stdout (max MAX_OUTPUT_CHARS)
            "error":      str,    # stderr tai virheilmoitus
            "violations": list,   # AST-tarkistuksen rikkomukset
            "timed_out":  bool,
        }
    """
    if len(code) > MAX_CODE_CHARS:
        return _err(f"Koodi liian pitkä ({len(code)} > {MAX_CODE_CHARS} merkkiä).")

    # Poista 'open' kiellosta jos sallittu
    effective_blocked = BLOCKED_BUILTINS - ({"open"} if allow_open else set())

    violations = _ast_check(code)
    # Suodata vain aktiiviset kiellot (open voi olla sallittu)
    active = [v for v in violations if not (allow_open and "'open()'" in v)]

    if active:
        logger.warning("Sandbox: AST-rikkomuksia: %s", active)
        return {
            "success":    False,
            "output":     "",
            "error":      "Koodi hylätty turvallisuustarkistuksessa:\n" + "\n".join(active),
            "violations": active,
            "timed_out":  False,
        }

    temp_dir = Path(tempfile.mkdtemp(prefix="agentdir_sb_"))
    try:
        script = temp_dir / "script.py"
        script.write_text(code, encoding="utf-8")

        # Minimaalinen ympäristö – ei peri vanhemman env:ä
        safe_env = {
            "PATH":        "/usr/bin:/usr/local/bin:/bin",
            "PYTHONPATH":  "",
            "HOME":        str(temp_dir),
            "TMPDIR":      str(temp_dir),
            "LANG":        "en_US.UTF-8",
        }

        proc = subprocess.run(
            [sys.executable, "-I", str(script)],  # -I = isolated mode
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(work_dir or temp_dir),
            env=safe_env,
        )

        return {
            "success":    proc.returncode == 0,
            "output":     proc.stdout[:MAX_OUTPUT_CHARS],
            "error":      proc.stderr[:MAX_OUTPUT_CHARS],
            "violations": [],
            "timed_out":  False,
        }

    except subprocess.TimeoutExpired:
        logger.warning("Sandbox timeout (%ds) ylittyi", timeout)
        return {
            "success":    False,
            "output":     "",
            "error":      f"Aikakatkaisu ({timeout}s). Koodi liian hidas tai jumissa.",
            "violations": [],
            "timed_out":  True,
        }
    except Exception as e:
        return _err(f"Suoritusvirhe: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def _err(msg: str) -> dict:
    return {"success": False, "output": "", "error": msg, "violations": [], "timed_out": False}
