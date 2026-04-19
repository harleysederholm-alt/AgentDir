"""
logical_validator.py — Semanttinen hallusinaatiosuodatin (AgentDir 4.0)

MaaS-DB M2: "Ennen koodin kirjoittamista, kysy V-Indexiltä:
            'Onko tämä entiteetti olemassa?'"

Tämä moduuli toimii 10-askeleen pipelinen vaiheessa 6 (Semantic Guardrail).
Se sieppaa LLM:n tekstivastauksen, parsii siitä koodientiteetit
(tiedostonimet, luokat, funktiot, moduulit) ja vertaa niitä
V-Index -graafiin. Jos LLM viittaa entiteettiin jota ei ole
olemassa projektissa, se nostaa HallucinationException.

Toimintaperiaate:
  1. Parsii LLM-vastauksen koodilohkot (```python ... ```)
  2. Poimii import-, class-, def-, ja tiedostopolkuviittaukset
  3. Vertaa löydöksiä V-Indexin tunnettuihin entiteetteihin
  4. Arvioi hallusinaatioriskin (matala/korkea/kriittinen)
  5. Estää kriittiset hallusinaatiot, raportoi matalariskiset

Käyttö:
  from agent_core.logical_validator import LogicalValidator, HallucinationException
  validator = LogicalValidator(anchor_manager)
  try:
      validated = validator.validate(llm_response)
  except HallucinationException as e:
      print(f"LLM hallusinoi: {e.hallucinations}")
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from agent_core.anchor_manager import AnchorManager

logger = logging.getLogger("agentdir.logical_validator")


# ── Poikkeusluokat ───────────────────────────────────────────────────────

class HallucinationException(Exception):
    """
    Nostetaan kun LLM:n vastaus sisältää kriittisiä hallusinaatioita.

    Hallusinaatio = viittaus entiteettiin (luokka, funktio, moduuli, tiedosto)
    jota EI löydy MaaS-DB V-Index -graafista.
    """

    def __init__(self, message: str, hallucinations: list[HallucinationReport]):
        super().__init__(message)
        self.hallucinations = hallucinations


# ── Riskitasot ───────────────────────────────────────────────────────────

class RiskLevel(Enum):
    """Hallusinaation riskitaso."""
    LOW = "matala"           # Epävarma maininta, ei kriittistä
    MEDIUM = "keskitaso"     # Todennäköinen hallusinaatio mutta ei estävä
    HIGH = "korkea"          # Vahva hallusinaatio, estää suorituksen
    CRITICAL = "kriittinen"  # Selkeä olematon entiteetti, AINA estää


@dataclass
class HallucinationReport:
    """Yksittäinen hallusinaatiolöydös."""
    entity_name: str           # Hallusinoitu entiteetin nimi
    entity_type: str           # "import", "class", "function", "file"
    context: str               # Rivi tai konteksti jossa viittaus esiintyy
    risk_level: RiskLevel      # Arvioitu riskitaso
    suggestion: str = ""       # Ehdotettu korjaus (jos saatavilla)


@dataclass
class ValidationResult:
    """Validoinnin kokonaistulos."""
    is_valid: bool                              # True = ei kriittisiä hallusinaatioita
    original_text: str                          # Alkuperäinen LLM-vastaus
    hallucinations: list[HallucinationReport] = field(default_factory=list)
    total_entities_checked: int = 0             # Montako entiteettiä tarkistettiin
    warnings: list[str] = field(default_factory=list)  # Matalariskiset varoitukset


# ── Tunnetut Python-standardikirjaston moduulit ──────────────────────────
# Näitä EI saa merkitä hallusinaatioiksi
STDLIB_MODULES = frozenset({
    "os", "sys", "re", "json", "math", "time", "datetime", "pathlib",
    "logging", "typing", "collections", "itertools", "functools",
    "abc", "io", "hashlib", "hmac", "secrets", "uuid", "copy",
    "threading", "asyncio", "concurrent", "multiprocessing",
    "subprocess", "shutil", "tempfile", "glob", "fnmatch",
    "ast", "inspect", "importlib", "dataclasses", "enum",
    "http", "urllib", "email", "html", "xml", "csv", "sqlite3",
    "socket", "ssl", "struct", "base64", "binascii",
    "unittest", "doctest", "pdb", "traceback", "warnings",
    "argparse", "configparser", "textwrap", "string",
    "random", "statistics", "decimal", "fractions",
    "pickle", "shelve", "dbm", "gzip", "zipfile", "tarfile",
    "ctypes", "platform", "signal", "resource", "mmap",
})

# Yleisesti käytetyt kolmannen osapuolen paketit — ei merkitä hallusinaatioiksi
KNOWN_THIRD_PARTY = frozenset({
    "fastapi", "uvicorn", "starlette", "httpx", "requests", "pydantic",
    "jinja2", "pytest", "numpy", "pandas", "torch", "transformers",
    "chromadb", "faiss", "sentence_transformers", "openai",
    "qrcode", "zeroconf", "websockets", "aiohttp", "httpcore",
    "click", "rich", "typer", "tqdm", "pillow", "PIL",
})


class LogicalValidator:
    """
    Semanttinen hallusinaatiosuodatin.

    Sieppaa LLM:n vastauksen, parsii koodientiteetit
    ja vertaa niitä V-Index -graafiin.
    """

    def __init__(self, anchor_manager: AnchorManager):
        self._am = anchor_manager
        self._known_entities: set[str] | None = None

    # ── Päävalidointi ────────────────────────────────────────────────────

    def validate(
        self,
        llm_response: str,
        block_on_high_risk: bool = True,
    ) -> ValidationResult:
        """
        Validoi LLM:n tekstivastaus hallusinaatioiden varalta.

        Args:
            llm_response: LLM:n tuottama raaka teksti
            block_on_high_risk: Jos True, nosta HallucinationException
                                kriittisillä hallusinaatioilla

        Returns:
            ValidationResult jossa tiedot löydetyistä hallusinaatioista

        Raises:
            HallucinationException: Jos kriittisiä hallusinaatioita löytyy
                                    ja block_on_high_risk on True
        """
        # Lataa tunnetut entiteetit V-Indexistä (kerran per sessio)
        if self._known_entities is None:
            self._known_entities = self._am.get_all_entity_names()

        hallucinations: list[HallucinationReport] = []
        total_checked = 0

        # 1. Tarkista koodilohkojen importit
        code_blocks = self._extract_code_blocks(llm_response)
        for block in code_blocks:
            imports = self._parse_imports(block)
            total_checked += len(imports)
            for imp in imports:
                report = self._check_import(imp, block)
                if report:
                    hallucinations.append(report)

            # 2. Tarkista luokka- ja funktiomääritykset
            definitions = self._parse_definitions(block)
            # Uusien määrittelyjen ei tarvitse olla V-Indexissä

            # 3. Tarkista viittaukset olemassa oleviin entiteetteihin
            references = self._parse_references(block)
            total_checked += len(references)
            for ref in references:
                report = self._check_reference(ref, block)
                if report:
                    hallucinations.append(report)

        # 4. Tarkista tiedostopolkuviittaukset vapaasta tekstistä
        file_refs = self._parse_file_references(llm_response)
        total_checked += len(file_refs)
        for fref in file_refs:
            report = self._check_file_reference(fref)
            if report:
                hallucinations.append(report)

        # Rakenna tulos
        critical = [h for h in hallucinations if h.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)]

        result = ValidationResult(
            is_valid=len(critical) == 0,
            original_text=llm_response,
            hallucinations=hallucinations,
            total_entities_checked=total_checked,
            warnings=[
                f"[{h.risk_level.value}] {h.entity_type} '{h.entity_name}': {h.suggestion}"
                for h in hallucinations if h.risk_level in (RiskLevel.LOW, RiskLevel.MEDIUM)
            ],
        )

        # Nosta poikkeus jos kriittisiä löytyi ja esto on päällä
        if block_on_high_risk and critical:
            msg = (
                f"LLM hallusinoi {len(critical)} entiteettiä jotka eivät ole "
                f"V-Indexissä: {', '.join(h.entity_name for h in critical)}"
            )
            logger.error("[Guardrail] %s", msg)
            raise HallucinationException(msg, critical)

        if hallucinations:
            logger.warning(
                "[Guardrail] %d hallusinaatiota löydetty (%d kriittistä), %d entiteettiä tarkistettu",
                len(hallucinations), len(critical), total_checked
            )
        else:
            logger.info("[Guardrail] Validointi OK: %d entiteettiä tarkistettu", total_checked)

        return result

    # ── Parsintatyökalut ─────────────────────────────────────────────────

    @staticmethod
    def _extract_code_blocks(text: str) -> list[str]:
        """Poimi ```python ... ``` -koodilohkot tekstistä."""
        pattern = r"```(?:python|py)?\s*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        return matches

    @staticmethod
    def _parse_imports(code: str) -> list[str]:
        """Parsii import-lauseet koodilohkosta."""
        imports = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
        except SyntaxError:
            # Fallback: regex-pohjainen parsinta epätäydelliselle koodille
            for match in re.finditer(r"(?:from|import)\s+([\w.]+)", code):
                imports.append(match.group(1))
        return imports

    @staticmethod
    def _parse_definitions(code: str) -> list[tuple[str, str]]:
        """Parsii class- ja def-määrittelyt koodilohkosta.
        Palauttaa listan (tyyppi, nimi) -pareja."""
        defs = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    defs.append(("class", node.name))
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defs.append(("function", node.name))
        except SyntaxError:
            for match in re.finditer(r"(?:class|def|async\s+def)\s+(\w+)", code):
                defs.append(("unknown", match.group(1)))
        return defs

    @staticmethod
    def _parse_references(code: str) -> list[str]:
        """Parsii viittaukset olemassa oleviin entiteetteihin (funktio- ja metodikutsut)."""
        refs = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        refs.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        refs.append(node.func.attr)
        except SyntaxError:
            # Regex-fallback: Nimi( -kutsumuoto
            for match in re.finditer(r"(\w+)\s*\(", code):
                name = match.group(1)
                # Ohita Python-builtinit ja yleiset nimet
                if name not in {"print", "len", "range", "str", "int", "float",
                                "list", "dict", "set", "tuple", "type", "super",
                                "isinstance", "issubclass", "hasattr", "getattr",
                                "setattr", "property", "staticmethod", "classmethod",
                                "enumerate", "zip", "map", "filter", "sorted",
                                "reversed", "any", "all", "min", "max", "sum",
                                "abs", "round", "open", "input", "format",
                                "True", "False", "None", "if", "for", "while",
                                "return", "yield", "raise", "assert", "del",
                                "with", "as", "try", "except", "finally"}:
                    refs.append(name)
        return refs

    @staticmethod
    def _parse_file_references(text: str) -> list[str]:
        """Parsii tiedostopolkuviittaukset vapaasta tekstistä."""
        # Etsi "polku/tiedosto.py" -tyyppiset viittaukset
        pattern = r'["\']?(\w[\w/\\]*\.py)["\']?'
        matches = re.findall(pattern, text)
        return list(set(matches))

    # ── Entiteettitarkistukset ───────────────────────────────────────────

    def _check_import(self, import_name: str, context: str) -> HallucinationReport | None:
        """Tarkista onko importattu moduuli tunnettu."""
        root_module = import_name.split(".")[0]

        # Ohita standardikirjasto ja tunnetut paketit
        if root_module in STDLIB_MODULES or root_module in KNOWN_THIRD_PARTY:
            return None

        # Tarkista onko projektin moduuli V-Indexissä
        if self._am.entity_exists(root_module):
            return None

        # Tarkista onko tiedosto olemassa
        self._am._ensure_loaded()
        known_modules = {
            fp.replace("/", ".").removesuffix(".py")
            for fp in self._am._graph.get("files", {})
        }
        # Tarkista myös yksinkertaiset moduulinimet
        known_simple = {m.split(".")[-1] for m in known_modules}

        if root_module in known_modules or root_module in known_simple:
            return None

        # Tuntematon import — matala riski koska voi olla asennettu paketti
        return HallucinationReport(
            entity_name=import_name,
            entity_type="import",
            context=context[:200],
            risk_level=RiskLevel.LOW,
            suggestion=f"Moduulia '{import_name}' ei löydy V-Indexistä. Varmista onko se asennettu.",
        )

    def _check_reference(self, ref_name: str, context: str) -> HallucinationReport | None:
        """Tarkista onko viitattu entiteetti tunnettu."""
        assert self._known_entities is not None

        # Lyhyet nimet tai Python-builtinit eivät ole hallusinaatioita
        if len(ref_name) < 3 or ref_name[0].islower():
            return None

        # PascalCase-nimet ovat luokkia — tarkista V-Index
        if ref_name[0].isupper() and ref_name not in self._known_entities:
            # Etsi lähimmät osumat ehdotukseksi
            suggestion = self._find_closest_match(ref_name)
            return HallucinationReport(
                entity_name=ref_name,
                entity_type="class",
                context=context[:200],
                risk_level=RiskLevel.HIGH,
                suggestion=suggestion or f"Luokkaa '{ref_name}' ei löydy. Onko nimi oikein?",
            )

        return None

    def _check_file_reference(self, file_ref: str) -> HallucinationReport | None:
        """Tarkista onko viitattu tiedosto olemassa."""
        self._am._ensure_loaded()
        normalized = file_ref.replace("\\", "/")

        # Tarkista V-Indexin tiedostoluettelosta
        known_files = set(self._am._graph.get("files", {}).keys())
        if normalized in known_files:
            return None

        # Tarkista myös tiedoston nimi ilman polkua
        known_basenames = {Path(f).name for f in known_files}
        if Path(normalized).name in known_basenames:
            return None

        return HallucinationReport(
            entity_name=file_ref,
            entity_type="file",
            context=f"Viittaus tiedostoon: {file_ref}",
            risk_level=RiskLevel.CRITICAL,
            suggestion=f"Tiedostoa '{file_ref}' ei löydy projektista.",
        )

    def _find_closest_match(self, name: str, max_distance: int = 3) -> str | None:
        """Etsi lähin vastaava entiteetti V-Indexistä (yksinkertainen Levenshtein)."""
        assert self._known_entities is not None

        best_match = None
        best_dist = max_distance + 1

        for known in self._known_entities:
            dist = self._levenshtein(name.lower(), known.lower())
            if dist < best_dist:
                best_dist = dist
                best_match = known

        if best_match and best_dist <= max_distance:
            return f"Tarkoititko: '{best_match}'?"
        return None

    @staticmethod
    def _levenshtein(s1: str, s2: str) -> int:
        """Minimaalinen Levenshtein-etäisyys."""
        if len(s1) < len(s2):
            return LogicalValidator._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)

        prev_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row

        return prev_row[-1]
