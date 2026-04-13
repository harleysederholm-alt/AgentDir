# AgentDir Sovereign Engine — Phase 2 Implementation Prompt
# ============================================================
# Käytä tätä kun lisäät .agentdir.md ankkurit ja Agent Print
# OLEMASSA OLEVAAN toimivaan projektiin.
# 
# TÄRKEÄÄ: Nämä ominaisuudet EIVÄT ole vielä repossa.
# Tämä on uusi lisäys — ei korvaus.

---

## TEHTÄVÄ

Lisää AgentDir Sovereign Engine -projektiin kaksi uutta ominaisuutta
häiritsemättä olemassa olevia toimivia komponentteja:

1. **Kansion kognitiiviset ankkurit** (.agentdir.md järjestelmä)
2. **Agent Print -raportointi** (EU AI Act -yhteensopiva)

---

## KONTEKSTI: MITÄ ON JO OLEMASSA

```python
# watcher.py — TOIMII, älä muuta ydinlogiikkaa
# Herää < 50ms kun tiedosto putoaa Inbox/
# Kutsuu llm_client.py:tä promptin kanssa
# Kirjoittaa tuloksen Outbox/

# llm_client.py — TOIMII
# Gemma4:e4b ensisijainen, Llama3.2:3b fallback
# Ollama-integraatio

# ChromaDB RAG — TOIMII
# mxbai-embed-large embeddings
# Semanttinen muisti
```

---

## VAIHE 1: .agentdir.md ANKKURIJÄRJESTELMÄ

### Mitä lisätään

**Uusi tiedosto:** `anchor_manager.py`

```python
"""
anchor_manager.py — Kognitiivisten ankkureiden hallinta
Lukee .agentdir.md -tiedostot ja syöttää kontekstin watcher.py:lle.
Ei korvaa watcher.py:tä — lisää sille kontekstin.
"""
from pathlib import Path
import re

class AnchorManager:
    """
    Lukee .agentdir.md -tiedostot kansioista ja tuottaa
    strukturoidun kontekstin LLM-promptiin.
    
    Integrointi: kutsu get_context() watcher.py:stä
    ennen llm_client.py:n kutsua.
    """
    
    ANCHOR_FILENAME = ".agentdir.md"
    SOVEREIGN_FILENAME = "!_SOVEREIGN.md"
    
    def get_context(self, folder_path: Path) -> str:
        """
        Kerää ankkurikonteksti tiedostolle:
        1. !_SOVEREIGN.md (juuresta)
        2. .agentdir.md (kansiosta)
        
        Returns: kontekstiteksti LLM-promptiin lisättäväksi
        """
        parts = []
        
        # Globaali ankkuri projektijuuresta
        sovereign = self._find_sovereign(folder_path)
        if sovereign:
            parts.append(f"## PROJEKTIN GLOBAALIT SÄÄNNÖT\n{sovereign}")
        
        # Paikallinen ankkuri tästä kansiosta
        local = folder_path / self.ANCHOR_FILENAME
        if local.exists():
            parts.append(f"## TÄMÄN KANSION KONTEKSTI\n{local.read_text()}")
        
        return "\n\n".join(parts) if parts else ""
    
    def _find_sovereign(self, start: Path) -> str:
        """Etsii !_SOVEREIGN.md ylöspäin hakemistopuussa."""
        current = start
        for _ in range(5):  # Max 5 tasoa ylös
            candidate = current / self.SOVEREIGN_FILENAME
            if candidate.exists():
                return candidate.read_text()
            current = current.parent
            if current == current.parent:
                break
        return ""
    
    def create_anchor(self, folder_path: Path, purpose: str) -> Path:
        """Luo .agentdir.md -tiedoston kansioon."""
        anchor = folder_path / self.ANCHOR_FILENAME
        content = f"""# .agentdir.md — {folder_path.name}

## TARKOITUS
{purpose}

## KONTEKSTI
- Tärkeimmät tiedostot: [täytä]
- Riippuu: [täytä]

## OHJEET AGENTILLE
- Sandbox: pakollinen
- Prioriteetti: normaali
- Muutos vaatii: testit

## KIELLETTYÄ TÄSSÄ KANSIOSSA
- [täytä tarvittaessa]
"""
        anchor.write_text(content, encoding="utf-8")
        return anchor
```

### Integrointi watcher.py:hyn

```python
# LISÄÄ watcher.py:hyn (älä muuta olemassa olevaa logiikkaa)
# Löydä kohta jossa prompt rakennetaan llm_client.py:lle

# ENNEN (olemassa oleva koodi):
prompt = build_prompt(file_content, task)

# JÄLKEEN (lisätään ankkurikonteksti):
from anchor_manager import AnchorManager
anchor_ctx = AnchorManager().get_context(inbox_folder)
prompt = build_prompt(file_content, task, anchor_context=anchor_ctx)

# Varmista että build_prompt() hyväksyy anchor_context parametrin
# tai lisää se suoraan promptin alkuun:
if anchor_ctx:
    prompt = f"{anchor_ctx}\n\n---\n\n{prompt}"
```

### Testit

```python
# tests/test_anchor_manager.py
import pytest
from pathlib import Path
from anchor_manager import AnchorManager

def test_reads_local_anchor(tmp_path):
    """Lukee .agentdir.md paikallisesta kansiosta."""
    anchor = tmp_path / ".agentdir.md"
    anchor.write_text("## TARKOITUS\nTestikansio")
    
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
    assert "Testikansion tarkoitus" in path.read_text()
```

---

## VAIHE 2: AGENT PRINT -RAPORTOINTI

### Mitä lisätään

**Uusi tiedosto:** `agent_print.py`

```python
"""
agent_print.py — EU AI Act Article 13 -yhteensopiva auditointiraportti
Generoidaan jokaisen onnistuneen suorituksen jälkeen.
Integroituu olemassa olevaan Outbox/ -putkeen.
"""
import json
import uuid
import datetime
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class AgentPrintRecord:
    """Yksittäisen suorituksen auditointitietue."""
    print_id: str
    timestamp: str
    task_description: str
    model_used: str          # esim. "gemma4:e4b"
    fallback_used: bool      # käytettiinkö Llama3.2:3b varamalli
    rag_hits: int            # montako ChromaDB-osumaa löytyi
    sandbox_attempts: int    # montako AST-sandbox-yritystä tarvittiin
    sandbox_success: bool
    evolution_triggered: bool  # muuttiko evoluutiomoottori promptia
    input_file: str
    output_file: str
    execution_ms: int
    eu_ai_act_compliant: bool = True

class AgentPrint:
    """
    Generoi ja tallentaa Agent Print -raportteja.
    
    Integrointi: kutsu generate() watcher.py:stä
    kun suoritus on valmis, ennen Outbox/-kirjoitusta.
    """
    
    def __init__(self, output_dir: str = "outputs/prints"):
        self.out = Path(output_dir)
        self.out.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        task: str,
        model: str,
        input_file: str,
        output_file: str,
        rag_hits: int = 0,
        sandbox_attempts: int = 1,
        sandbox_success: bool = True,
        fallback_used: bool = False,
        evolution_triggered: bool = False,
        execution_ms: int = 0,
    ) -> str:
        """
        Generoi Agent Print -raportti.
        Palauttaa print_id:n.
        """
        print_id = str(uuid.uuid4())[:8].upper()
        ts = datetime.datetime.now().isoformat()
        
        record = AgentPrintRecord(
            print_id=print_id,
            timestamp=ts,
            task_description=task[:200],  # Truncate pitkät kuvaukset
            model_used=model,
            fallback_used=fallback_used,
            rag_hits=rag_hits,
            sandbox_attempts=sandbox_attempts,
            sandbox_success=sandbox_success,
            evolution_triggered=evolution_triggered,
            input_file=input_file,
            output_file=output_file,
            execution_ms=execution_ms,
        )
        
        # Tallenna JSON (koneluettava)
        json_path = self.out / f"print_{print_id}.json"
        json_path.write_text(
            json.dumps(asdict(record), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # Tallenna MD (ihmisluettava)
        md_path = self.out / f"print_{print_id}.md"
        md_path.write_text(
            self._render_markdown(record),
            encoding="utf-8"
        )
        
        return print_id
    
    def _render_markdown(self, r: AgentPrintRecord) -> str:
        status = "✅ ONNISTUI" if r.sandbox_success else "❌ EPÄONNISTUI"
        fallback = "⚠️ Kyllä" if r.fallback_used else "Ei"
        evo = "🧬 Kyllä" if r.evolution_triggered else "Ei"
        
        return f"""# Agent Print — {r.print_id}
**AgentDir Sovereign Engine 3.5**

| Kenttä | Arvo |
|---|---|
| ID | `{r.print_id}` |
| Aikaleima | {r.timestamp} |
| Tulos | {status} |
| Malli | `{r.model_used}` |
| Varamalli käytetty | {fallback} |
| RAG-osumat | {r.rag_hits} |
| Sandbox-yritykset | {r.sandbox_attempts}/3 |
| Evoluutio laukaistu | {evo} |
| Suoritusaika | {r.execution_ms}ms |
| EU AI Act Art.13 | ✅ |

## Tehtävä
{r.task_description}

## Tiedostot
- **Syöte:** `{r.input_file}`
- **Tulos:** `{r.output_file}`

---
*AgentDir Sovereign Engine | MIT License*
"""
    
    def get_stats(self) -> dict:
        """Palauta tilastot kaikista Agent Print -raporteista."""
        prints = list(self.out.glob("print_*.json"))
        if not prints:
            return {"total": 0, "success_rate": 0}
        
        records = []
        for p in prints:
            try:
                records.append(json.loads(p.read_text()))
            except Exception:
                continue
        
        total = len(records)
        successes = sum(1 for r in records if r.get("sandbox_success"))
        
        return {
            "total": total,
            "success_rate": round(successes / total * 100, 1) if total else 0,
            "avg_execution_ms": round(
                sum(r.get("execution_ms", 0) for r in records) / total
            ) if total else 0,
            "fallback_rate": round(
                sum(1 for r in records if r.get("fallback_used")) / total * 100, 1
            ) if total else 0,
        }
```

### Integrointi watcher.py:hyn

```python
# LISÄÄ watcher.py:hyn (olemassa olevan suorituslogiikan loppuun)

from agent_print import AgentPrint
import time

# Olemassa oleva koodi (pseudokoodi — seuraa oikeaa watcher.py:n rakennetta):
# start_time = time.time()
# ... AST sandbox suoritus ...
# ... Outbox-kirjoitus ...
# execution_time = int((time.time() - start_time) * 1000)

# LISÄÄ tämä Outbox-kirjoituksen JÄLKEEN:
printer = AgentPrint()
print_id = printer.generate(
    task=task_description,
    model=used_model,           # llm_client.py:stä
    input_file=str(input_path),
    output_file=str(output_path),
    rag_hits=rag_hit_count,     # ChromaDB:stä
    sandbox_attempts=attempts,  # AST Sandboxista
    sandbox_success=success,
    fallback_used=used_fallback,
    execution_ms=execution_time,
)
# print_id on nyt saatavilla lokitukseen
```

---

## VAIHE 3: TESTIT MOLEMMILLE

```python
# tests/test_agent_print.py
import pytest
from pathlib import Path
from agent_print import AgentPrint

def test_generates_json_and_md(tmp_path):
    """Luo sekä JSON että MD tiedoston."""
    printer = AgentPrint(str(tmp_path / "prints"))
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
    
    assert (tmp_path / "prints" / f"print_{print_id}.json").exists()
    assert (tmp_path / "prints" / f"print_{print_id}.md").exists()

def test_stats_empty(tmp_path):
    """Tyhjä stats ilman raportteja."""
    printer = AgentPrint(str(tmp_path / "prints"))
    stats = printer.get_stats()
    assert stats["total"] == 0

def test_stats_with_records(tmp_path):
    """Stats laskee oikein useista raporteista."""
    printer = AgentPrint(str(tmp_path / "prints"))
    printer.generate("task1", "gemma4:e4b", "in1", "out1", sandbox_success=True)
    printer.generate("task2", "gemma4:e4b", "in2", "out2", sandbox_success=False)
    
    stats = printer.get_stats()
    assert stats["total"] == 2
    assert stats["success_rate"] == 50.0
```

---

## ASENNUS JA TESTAUS

```bash
# Aja testit ennen kuin pusket GitHubiin
cd agentdir
pytest tests/test_anchor_manager.py -v
pytest tests/test_agent_print.py -v

# Tarkista ettei olemassa olevat testit hajoa
pytest -v

# Käynnistä ja testaa manuaalisesti
.\launch_sovereign.ps1
# Pudota tiedosto Inbox/ kansioon
# Tarkista että outputs/prints/ kansioon ilmestyy raportti
```

---

## README-PÄIVITYS

Lisää README.md:hen `Benchmark`-taulukon alle:

```markdown
## 🖨️ Agent Print — Auditointiraportti

Jokainen suoritus generoi automaattisesti EU AI Act Article 13
-yhteensopivan raportin kansioon `outputs/prints/`:

| Kenttä | Kuvaus |
|---|---|
| Malli | Käytetty LLM (Gemma4 / fallback) |
| RAG-osumat | Semanttisen muistin löydöt |
| Sandbox-yritykset | AST self-healing -kierrokset |
| Suoritusaika | End-to-end ms |

Tilastot: `python -c "from agent_print import AgentPrint; print(AgentPrint().get_stats())"`
```

---

## COMMIT-VIESTI (GitHubiin)

```
feat: add cognitive anchors (.agentdir.md) and Agent Print reporting

- anchor_manager.py: reads .agentdir.md and !_SOVEREIGN.md for
  folder-level context injection into LLM prompts
- agent_print.py: EU AI Act Article 13 compliant audit reports
  saved to outputs/prints/ as JSON + Markdown
- Integrates with existing watcher.py pipeline (non-breaking)
- Tests: tests/test_anchor_manager.py, tests/test_agent_print.py

Does not modify: watcher.py core, llm_client.py, ChromaDB setup,
AST sandbox, REST API, Tauri UI, install.ps1, launch_sovereign.ps1
```
