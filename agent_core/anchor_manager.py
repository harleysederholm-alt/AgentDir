"""
anchor_manager.py — MaaS-DB V-Index -graafimoottori (AgentDir 4.0)

MaaS-DB -paradigma: Kohtele koodipohjaa Knowledge Graph -tietokantana.
Tämä moduuli skannaa projektin hakemistorakenteen, poimii entiteetit
(luokat, funktiot, globaalit muuttujat) ja niiden väliset relaatiot
(importit, perintä, kutsut) ja tallentaa ne wiki/v_index.json -graafiksi.

Graafirakenne:
  {
    "entities": {
      "moduuli::EntiteettiNimi": {
        "type": "class" | "function" | "global",
        "file": "polku/tiedostoon.py",
        "line": 42,
        "docstring": "...",
        "relations": ["importoi::toinen_moduuli", "perii::KantaLuokka"]
      }
    },
    "files": {
      "polku/tiedostoon.py": {
        "entities": ["moduuli::Luokka", "moduuli::funktio"],
        "imports": ["os", "pathlib", "toinen_moduuli"],
        "last_scanned": "2026-04-15T21:00:00"
      }
    },
    "meta": {
      "version": "4.0",
      "total_entities": 123,
      "total_files": 45,
      "last_full_scan": "2026-04-15T21:00:00"
    }
  }

Käyttö:
  from agent_core.anchor_manager import AnchorManager
  am = AnchorManager(project_root=Path("."))
  am.build_v_index()  # Koko skannaus
  context = am.query("OmniNodeManager")  # Yksittäinen haku
  am.patch_model_knowledge()  # Syötä graafikonteksti LLM-promptiin
"""

from __future__ import annotations

import ast
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("agentdir.anchor_manager")

# Hakemistot jotka ohitetaan skannauksessa — raskaat ja irrelevantit
SKIP_DIRS = frozenset({
    ".venv", "venv", "node_modules", ".git", "__pycache__",
    ".pytest_cache", ".mypy_cache", "agentdir.egg-info",
    ".tox", "dist", "build", ".eggs",
})

# Tiedostopäätteet jotka skannataan
SCAN_EXTENSIONS = frozenset({".py"})


class VIndexEntity:
    """Yksittäinen entiteetti V-Index -graafissa (luokka, funktio, muuttuja)."""

    __slots__ = ("name", "qualified_name", "entity_type", "file_path",
                 "line", "docstring", "relations")

    def __init__(
        self,
        name: str,
        qualified_name: str,
        entity_type: str,
        file_path: str,
        line: int,
        docstring: str = "",
        relations: list[str] | None = None,
    ):
        self.name = name
        self.qualified_name = qualified_name  # "moduuli::Nimi"
        self.entity_type = entity_type        # "class", "function", "global"
        self.file_path = file_path
        self.line = line
        self.docstring = docstring
        self.relations = relations or []

    def to_dict(self) -> dict[str, Any]:
        """Serialisoi JSON-muotoon."""
        return {
            "type": self.entity_type,
            "file": self.file_path,
            "line": self.line,
            "docstring": self.docstring[:300] if self.docstring else "",
            "relations": self.relations,
        }


class _ASTEntityExtractor(ast.NodeVisitor):
    """
    AST-kävijä joka poimii luokat, funktiot ja globaalit muuttujat
    yksittäisestä Python-tiedostosta.

    Poimii myös import-lauseet relaatioiden muodostamiseksi.
    """

    def __init__(self, module_name: str, file_path: str):
        self.module_name = module_name
        self.file_path = file_path
        self.entities: list[VIndexEntity] = []
        self.imports: list[str] = []
        self._class_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Poimi luokkamääritys ja sen kantaluokat."""
        qualified = f"{self.module_name}::{node.name}"
        relations = []

        # Perintärelaatiot
        for base in node.bases:
            base_name = self._resolve_name(base)
            if base_name:
                relations.append(f"perii::{base_name}")

        self.entities.append(VIndexEntity(
            name=node.name,
            qualified_name=qualified,
            entity_type="class",
            file_path=self.file_path,
            line=node.lineno,
            docstring=ast.get_docstring(node) or "",
            relations=relations,
        ))

        # Käy läpi luokan sisäiset metodit
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Poimi funktio- tai metodimääritys."""
        # Ohita yksityiset apufunktiot (alkaa __ paitsi __init__)
        if node.name.startswith("__") and node.name != "__init__":
            self.generic_visit(node)
            return

        # Metodit luokan sisällä vs. ylätason funktiot
        if self._class_stack:
            qualified = f"{self.module_name}::{self._class_stack[-1]}.{node.name}"
            entity_type = "method"
        else:
            qualified = f"{self.module_name}::{node.name}"
            entity_type = "function"

        self.entities.append(VIndexEntity(
            name=node.name,
            qualified_name=qualified,
            entity_type=entity_type,
            file_path=self.file_path,
            line=node.lineno,
            docstring=ast.get_docstring(node) or "",
        ))
        self.generic_visit(node)

    # Async-funktiot samalla logiikalla
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node: ast.Assign) -> None:
        """Poimi moduulitason globaalit muuttujat (esim. BIND_PORT = 8080)."""
        if self._class_stack:
            # Ohita luokan attribuutit
            self.generic_visit(node)
            return

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                qualified = f"{self.module_name}::{target.id}"
                self.entities.append(VIndexEntity(
                    name=target.id,
                    qualified_name=qualified,
                    entity_type="global",
                    file_path=self.file_path,
                    line=node.lineno,
                ))
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Kerää import-lauseet relaatioiksi."""
        for alias in node.names:
            self.imports.append(alias.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Kerää from-import -lauseet relaatioiksi."""
        if node.module:
            self.imports.append(node.module.split(".")[0])
        self.generic_visit(node)

    @staticmethod
    def _resolve_name(node: ast.expr) -> str | None:
        """Ratkaise AST-noodin nimi merkkijonoksi (yksinkertainen tapaus)."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            value = _ASTEntityExtractor._resolve_name(node.value)
            if value:
                return f"{value}.{node.attr}"
        return None


class AnchorManager:
    """
    MaaS-DB V-Index -moottori.

    Skannaa projektin Python-tiedostot, rakentaa tietograafin
    ja tarjoaa kyselyrajapinnan LLM-prompttien rikastamiseen.
    """

    V_INDEX_FILE = "wiki/v_index.json"

    def __init__(self, project_root: Path | None = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parent.parent)
        self.v_index_path = self.project_root / self.V_INDEX_FILE
        self._graph: dict[str, Any] = {"entities": {}, "files": {}, "meta": {}}
        self._loaded = False

    # ── Pääskannaus ──────────────────────────────────────────────────────

    def build_v_index(self) -> dict[str, Any]:
        """
        Suorita täysi projektin skannaus ja rakenna V-Index -graafi.

        Käy läpi kaikki .py -tiedostot (pois lukien SKIP_DIRS),
        poimi entiteetit AST:n avulla ja tallenna wiki/v_index.json.

        Returns:
            Graafistatistiikka (total_entities, total_files, duration_ms)
        """
        start = time.monotonic()
        logger.info("[MaaS-DB] Aloitetaan V-Index -skannaus: %s", self.project_root)

        entities: dict[str, dict] = {}
        files: dict[str, dict] = {}
        scan_time = datetime.now().isoformat(timespec="seconds")

        # Etsi kaikki Python-tiedostot
        for py_file in self._find_python_files():
            relative = str(py_file.relative_to(self.project_root)).replace("\\", "/")
            module_name = relative.replace("/", ".").removesuffix(".py")

            try:
                source = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=relative)
            except (SyntaxError, UnicodeDecodeError) as e:
                logger.warning("[MaaS-DB] Ohitetaan %s: %s", relative, e)
                continue

            # Poimi entiteetit AST:sta
            extractor = _ASTEntityExtractor(module_name, relative)
            extractor.visit(tree)

            # Tallenna tiedostotason metatiedot
            file_entities = []
            for entity in extractor.entities:
                entities[entity.qualified_name] = entity.to_dict()
                file_entities.append(entity.qualified_name)

            files[relative] = {
                "entities": file_entities,
                "imports": sorted(set(extractor.imports)),
                "last_scanned": scan_time,
            }

        # Rakenna lopullinen graafi
        self._graph = {
            "entities": entities,
            "files": files,
            "meta": {
                "version": "4.0",
                "total_entities": len(entities),
                "total_files": len(files),
                "last_full_scan": scan_time,
            },
        }

        # Tallenna levylle
        self._save()
        self._loaded = True

        duration_ms = round((time.monotonic() - start) * 1000)
        stats = {
            "total_entities": len(entities),
            "total_files": len(files),
            "duration_ms": duration_ms,
        }
        logger.info(
            "[MaaS-DB] V-Index valmis: %d entiteettiä / %d tiedostoa (%dms)",
            stats["total_entities"], stats["total_files"], stats["duration_ms"]
        )
        return stats

    # ── Kyselyt ──────────────────────────────────────────────────────────

    def query(self, name: str) -> dict[str, Any] | None:
        """
        Hae entiteetti V-Indexistä nimen perusteella.

        Tukee sekä yksinkertaista nimeä ("OmniNodeManager")
        että kvalifioitua nimeä ("omninode::OmniNodeManager").

        Returns:
            Entiteetin tiedot tai None jos ei löydy.
        """
        self._ensure_loaded()

        # Yritä ensin suoraa kvalifioitua hakua
        if name in self._graph["entities"]:
            return self._graph["entities"][name]

        # Osittainen haku: etsi entiteetti jonka nimi päättyy annettuun nimeen
        for key, data in self._graph["entities"].items():
            # "moduuli::Nimi" → "Nimi"
            entity_name = key.rsplit("::", 1)[-1]
            if entity_name == name:
                return {**data, "qualified_name": key}

        return None

    def entity_exists(self, name: str) -> bool:
        """Tarkista onko entiteetti olemassa V-Indexissä."""
        return self.query(name) is not None

    def get_file_entities(self, file_path: str) -> list[str]:
        """Palauta tiedoston kaikki entiteetit."""
        self._ensure_loaded()
        normalized = file_path.replace("\\", "/")
        file_data = self._graph["files"].get(normalized, {})
        return file_data.get("entities", [])

    def get_all_entity_names(self) -> set[str]:
        """Palauta kaikkien entiteettien yksinkertaiset nimet (ilman moduuliprefiksiä)."""
        self._ensure_loaded()
        names = set()
        for key in self._graph["entities"]:
            simple = key.rsplit("::", 1)[-1]
            # Metodit: "Luokka.metodi" → lisää molemmat
            names.add(simple)
            if "." in simple:
                names.add(simple.split(".")[0])  # Lisää myös luokan nimi
        return names

    def get_related_entities(self, name: str) -> list[dict[str, Any]]:
        """Hae entiteetin relaatiot (perintä, importit)."""
        entity = self.query(name)
        if not entity:
            return []

        related = []
        for relation in entity.get("relations", []):
            # "perii::KantaLuokka" → hae KantaLuokka
            rel_type, rel_name = relation.split("::", 1) if "::" in relation else ("tuntematon", relation)
            target = self.query(rel_name)
            related.append({
                "relation_type": rel_type,
                "target_name": rel_name,
                "target_data": target,
            })
        return related

    # ── LLM-kontekstin syöttö (MaaS-DB M3) ──────────────────────────────

    def patch_model_knowledge(self, focus_files: list[str] | None = None) -> str:
        """
        Rakenna LLM-promptiin syötettävä kontekstilohko V-Indexistä.

        MaaS-DB M3: "LLM saa AINA V-Index -kontekstin ennen inferenssiä."

        Tämä metodi tuottaa tiiviin yhteenvedon projektin rakenteesta
        joka syötetään järjestelmäviestiin ennen tehtävää.

        Args:
            focus_files: Jos annettu, keskity näihin tiedostoihin.
                         Muuten tuota yleiskatsaus.

        Returns:
            Markdown-muotoinen kontekstilohko LLM-promptiin.
        """
        self._ensure_loaded()

        parts = [
            "## V-INDEX KNOWLEDGE GRAPH (MaaS-DB)",
            f"Skannausajankohta: {self._graph['meta'].get('last_full_scan', 'tuntematon')}",
            f"Entiteettejä: {self._graph['meta'].get('total_entities', 0)}",
            f"Tiedostoja: {self._graph['meta'].get('total_files', 0)}",
            "",
        ]

        if focus_files:
            # Kohdennettu konteksti — näytä vain pyydetyt tiedostot
            parts.append("### Kohdistettu konteksti")
            for fp in focus_files:
                normalized = fp.replace("\\", "/")
                file_data = self._graph["files"].get(normalized)
                if file_data:
                    parts.append(f"\n**{normalized}**")
                    for ent_name in file_data["entities"]:
                        ent = self._graph["entities"].get(ent_name, {})
                        doc = ent.get("docstring", "")[:100]
                        etype = ent.get("type", "?")
                        parts.append(f"  - [{etype}] `{ent_name}` (rivi {ent.get('line', '?')})")
                        if doc:
                            parts.append(f"    → {doc}")
        else:
            # Yleiskatsaus — listaa tärkeimmät tiedostot ja niiden entiteetit
            parts.append("### Projektin rakenne")
            for fp, file_data in sorted(self._graph["files"].items()):
                entity_count = len(file_data.get("entities", []))
                if entity_count > 0:
                    parts.append(f"- **{fp}** ({entity_count} entiteettiä)")
                    # Näytä max 5 tärkeintä entiteettiä per tiedosto
                    for ent_name in file_data["entities"][:5]:
                        ent = self._graph["entities"].get(ent_name, {})
                        parts.append(f"  - [{ent.get('type', '?')}] `{ent_name}`")
                    if entity_count > 5:
                        parts.append(f"  - ... ja {entity_count - 5} muuta")

        return "\n".join(parts)

    # ── Inkrementaalinen päivitys ────────────────────────────────────────

    def update_file(self, file_path: Path) -> int:
        """
        Päivitä yksittäisen tiedoston entiteetit V-Indexiin.
        Käytetään tehtävän jälkeen kun tiedosto on muuttunut.

        Returns:
            Päivitettyjen entiteettien lukumäärä.
        """
        self._ensure_loaded()

        relative = str(file_path.relative_to(self.project_root)).replace("\\", "/")

        # Poista vanhat entiteetit tästä tiedostosta
        old_entries = self._graph["files"].get(relative, {}).get("entities", [])
        for old_name in old_entries:
            self._graph["entities"].pop(old_name, None)

        # Skannaa uudelleen
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=relative)
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.warning("[MaaS-DB] Päivitys ohitetaan %s: %s", relative, e)
            return 0

        module_name = relative.replace("/", ".").removesuffix(".py")
        extractor = _ASTEntityExtractor(module_name, relative)
        extractor.visit(tree)

        new_entities = []
        for entity in extractor.entities:
            self._graph["entities"][entity.qualified_name] = entity.to_dict()
            new_entities.append(entity.qualified_name)

        self._graph["files"][relative] = {
            "entities": new_entities,
            "imports": sorted(set(extractor.imports)),
            "last_scanned": datetime.now().isoformat(timespec="seconds"),
        }

        # Päivitä metatiedot
        self._graph["meta"]["total_entities"] = len(self._graph["entities"])
        self._graph["meta"]["total_files"] = len(self._graph["files"])

        self._save()
        logger.info("[MaaS-DB] Päivitetty %s: %d entiteettiä", relative, len(new_entities))
        return len(new_entities)

    # ── Sisäiset apufunktiot ─────────────────────────────────────────────

    def _find_python_files(self) -> list[Path]:
        """Etsi kaikki Python-tiedostot projektista, ohita SKIP_DIRS."""
        result = []
        for item in self.project_root.rglob("*.py"):
            # Tarkista ettei mikään polun osa ole ohitettava hakemisto
            parts = item.relative_to(self.project_root).parts
            if any(part in SKIP_DIRS for part in parts):
                continue
            result.append(item)
        return sorted(result)

    def _ensure_loaded(self) -> None:
        """Lataa V-Index levyltä jos ei vielä muistissa."""
        if self._loaded:
            return
        if self.v_index_path.exists():
            try:
                self._graph = json.loads(
                    self.v_index_path.read_text(encoding="utf-8")
                )
                self._loaded = True
                return
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("[MaaS-DB] V-Index korruptoitunut, rakennetaan uudelleen: %s", e)

        # Jos tiedostoa ei ole tai se on korruptoitunut, rakenna uudelleen
        self.build_v_index()

    def _save(self) -> None:
        """Tallenna V-Index levylle atomaarisesti."""
        self.v_index_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.v_index_path.with_suffix(".tmp")
        try:
            tmp.write_text(
                json.dumps(self._graph, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            tmp.replace(self.v_index_path)
        except OSError as e:
            logger.error("[MaaS-DB] V-Index -tallennus epäonnistui: %s", e)
            tmp.unlink(missing_ok=True)

    # ── Diagnostiikka ────────────────────────────────────────────────────

    def stats(self) -> dict[str, Any]:
        """Palauta V-Indexin tilastot."""
        self._ensure_loaded()
        return {
            "total_entities": self._graph["meta"].get("total_entities", 0),
            "total_files": self._graph["meta"].get("total_files", 0),
            "last_scan": self._graph["meta"].get("last_full_scan", "ei koskaan"),
            "graph_size_bytes": self.v_index_path.stat().st_size if self.v_index_path.exists() else 0,
        }
