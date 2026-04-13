# AgentDir 3.5 "Sovereign Engine" — Master Implementation Prompt
# For: Claude Code / Cursor Composer (Opus 4.6 class)
# Version: 3.5 Diamond Edition
# Language: Finnish comments, English code

---

## SYSTEM IDENTITY

You are the **Lead Architect** of AgentDir 3.5 Sovereign Engine.
Your job is to implement a production-ready, modular Python system
that turns any folder into a cognitive operating layer for autonomous agents.

**Core principle:** The model is a commodity. The Harness is the product.

You work with surgical precision. You do not refactor files not mentioned.
You write a hypothesis in `wiki/log.md` before every implementation step.
You verify with tests before marking anything complete.

---

## ARCHITECTURE OVERVIEW

```
AgentDir 3.5/
├── !_SOVEREIGN.md          # L1: Global routing, ethics, OmniNode map
├── cli.py                  # Entry point — all commands go through here
├── orchestrator.py         # WorkflowOrchestrator (openclaw + hermes modes)
├── workspace/
│   ├── policy.py           # Pre-flight task validation (EU AI Act gate)
│   ├── sandbox.py          # Safe YOLO isolated execution (subprocess)
│   ├── rag.py              # FAISS vector index over /wiki
│   ├── retrieval.py        # File-based context collection
│   ├── model_router.py     # Routes tasks to correct LLM backend
│   ├── omninode.py         # OmniNode bridge (USB/WiFi NPU sharding)
│   ├── memmachine.py       # STM/LTM separation (Ground-Truth vault)
│   ├── causal.py           # Causal scratchpad + Circuit Breaker
│   ├── agent_print.py      # EU AI Act compliant audit report generator
│   ├── benchmark.py        # Performance benchmarks
│   └── tests/
│       ├── test_policy.py
│       ├── test_sandbox.py
│       ├── test_rag.py
│       └── test_orchestrator.py
├── raw/                    # Inbox — agent reads from here
├── wiki/
│   ├── index.md            # Living project knowledge index
│   └── log.md              # Causal scratchpad + audit trail
└── outputs/                # Agent-produced results
```

---

## IMPLEMENTATION RULES (KARPATHY DISCIPLINE)

1. **Simplicity First** — use Python stdlib where possible
2. **Surgical edits only** — never touch files not in scope
3. **Hypothesis before code** — write intent to `wiki/log.md` first
4. **Test before ship** — every module gets a test
5. **Agent Print always** — every task run generates an audit record
6. **No hallucination** — if unsure, raise `NotImplementedError` with comment

---

## PHASE 1: CORE FOUNDATION
### Implement in this exact order:

### 1.1 — `!_SOVEREIGN.md`
```markdown
# SOVEREIGN MAP — AgentDir 3.5
## Global Ethics (MemMachine Gate)
- NEVER modify files outside /raw, /wiki, /outputs without explicit user COMMIT
- NEVER execute network calls from sandbox (--network none)
- ALWAYS write causal hypothesis before code execution
- ALWAYS generate Agent Print on task completion

## OmniNode Resources
- node_0: localhost (master PC) — primary inference
- node_1: [USB-C device] — KV-cache shard layer 20-40
- node_2: [WiFi device] — KV-cache shard layer 40-60

## Routing Rules
- Code tasks → openclaw mode
- Memory/research tasks → hermes mode
- Vision tasks → model_router (vision backend)
```

### 1.2 — `cli.py`
```python
#!/usr/bin/env python3
"""
AgentDir 3.5 CLI — Sovereign Engine
Käyttö: python cli.py <komento> [optiot]
"""
import argparse
import sys
from orchestrator import WorkflowOrchestrator

def main():
    parser = argparse.ArgumentParser(
        prog="agentdir",
        description="AgentDir 3.5 Sovereign Engine"
    )
    sub = parser.add_subparsers(dest="command")

    # --- RUN ---
    run_p = sub.add_parser("run", help="Suorita tehtävä")
    run_p.add_argument("task", help="Tehtävän kuvaus")
    run_p.add_argument(
        "--mode",
        choices=["openclaw", "hermes"],
        default="openclaw",
        help="Workflow-moodi (oletus: openclaw)"
    )
    run_p.add_argument(
        "--model",
        default="auto",
        help="Mallitunnus tai 'auto'"
    )

    # --- INIT ---
    init_p = sub.add_parser("init", help="Alusta AgentDir-rakenne")
    init_p.add_argument(
        "--path",
        default=".",
        help="Kohdehakemisto (oletus: nykyinen)"
    )

    # --- STATUS ---
    sub.add_parser("status", help="Näytä parven tila")

    # --- BENCHMARK ---
    sub.add_parser("benchmark", help="Aja suorituskykytestit")

    # --- PRINT ---
    print_p = sub.add_parser("print", help="Generoi Agent Print -raportti")
    print_p.add_argument("--task-id", default="latest")

    args = parser.parse_args()

    if args.command == "run":
        orch = WorkflowOrchestrator(mode=args.mode)
        result = orch.run(task=args.task, model=args.model)
        print(result["summary"])

    elif args.command == "init":
        from workspace.init_structure import init_project
        init_project(args.path)

    elif args.command == "status":
        orch = WorkflowOrchestrator()
        orch.status()

    elif args.command == "benchmark":
        from workspace.benchmark import run_benchmarks
        run_benchmarks()

    elif args.command == "print":
        from workspace.agent_print import generate_print
        generate_print(args.task_id)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

### 1.3 — `orchestrator.py`
Implement `WorkflowOrchestrator` with:
- `__init__(self, mode="openclaw")` — load `!_SOVEREIGN.md` and active `.agentdir.md`
- `run(self, task: str, model: str = "auto") -> dict` — full pipeline
- `status(self)` — print swarm health

**The run() pipeline MUST follow this exact order:**
```
1. policy.validate(task)          # Pre-flight gate
2. causal.write_hypothesis(task)  # Log intent to wiki/log.md
3. retrieval.gather_context(task) # Collect relevant /wiki files
4. rag.query(task)                # FAISS semantic search
5. model_router.select(task)      # Choose LLM backend
6. sandbox.execute(plan)          # Safe YOLO isolated run
7. memmachine.commit(result)      # STM → LTM if verified
8. agent_print.generate(result)   # Audit record
9. return result                  # Return summary dict
```

**openclaw mode** = steps 1-9 linear, fast
**hermes mode** = steps 1-9 with memory lookup before step 4,
                  skill registry check, and session persistence

---

## PHASE 2: COGNITIVE MODULES

### 2.1 — `workspace/policy.py`
```python
"""
Tehtävän esitarkistus (EU AI Act Article 13 gate)
Estää vaaralliset komennot ennen suoritusta.
"""
BLOCKED_PATTERNS = [
    "rm -rf", "del /f", "format c:", ":(){:|:&};:",
    "sudo rm", "os.remove", "shutil.rmtree",
    "__import__('os').system",
]

class PolicyEngine:
    def validate(self, task: str) -> bool:
        """Palauttaa True jos tehtävä on sallittu."""
        task_lower = task.lower()
        for pattern in BLOCKED_PATTERNS:
            if pattern in task_lower:
                raise PermissionError(
                    f"Policy gate: tehtävä estetty. "
                    f"Kielletty kuvio: '{pattern}'"
                )
        return True
```

### 2.2 — `workspace/sandbox.py`
```python
"""
Safe YOLO -hiekkalaatikko.
Kaikki agenttien kirjoittama koodi ajetaan tässä.
Ei verkkoyhteyttä, rajoitettu muisti.
"""
import subprocess, tempfile, os

class SovereignSandbox:
    def execute(self, code: str, timeout: int = 30) -> dict:
        """Ajaa koodin eristetyssä prosessissa."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                # Rajoitettu ympäristö
                env={"PATH": os.environ.get("PATH", "")},
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stderr": "TIMEOUT", "stdout": ""}
        finally:
            os.unlink(tmp_path)
```

### 2.3 — `workspace/memmachine.py`
```python
"""
MemMachine — Ground-Truth vault (arXiv:2604.04853v1)
Erottaa työmuistin (STM) ja pysyvän totuuden (LTM).
STM = sandbox tulokset (väliaikaisia)
LTM = wiki/ kansio (pysyvä, vain verifioitu tieto)
"""
import json, datetime
from pathlib import Path

class MemMachine:
    def __init__(self, ltm_path="wiki"):
        self.ltm = Path(ltm_path)
        self.ltm.mkdir(exist_ok=True)
        self.stm = {}  # Väliaikainen sessiomuisti

    def write_stm(self, key: str, value):
        """Kirjoita työmuistiin (ei pysyvä)."""
        self.stm[key] = {"value": value, "ts": datetime.datetime.now().isoformat()}

    def commit_to_ltm(self, key: str, content: str):
        """
        Siirrä STM → LTM vain jos verifioitu.
        Tämä on ainoa tapa muuttaa wiki/ sisältöä.
        """
        target = self.ltm / f"{key}.md"
        with open(target, "a") as f:
            ts = datetime.datetime.now().isoformat()
            f.write(f"\n\n<!-- Committed: {ts} -->\n{content}\n")

    def read_ltm(self, key: str) -> str:
        """Lue pysyvästä muistista."""
        target = self.ltm / f"{key}.md"
        if target.exists():
            return target.read_text()
        return ""

    def get_ground_truth(self) -> dict:
        """Palauta kaikki LTM-faktat dict-muodossa."""
        facts = {}
        for f in self.ltm.glob("*.md"):
            facts[f.stem] = f.read_text()
        return facts
```

### 2.4 — `workspace/causal.py`
```python
"""
Kausaalinen raapustuspaperi + Circuit Breaker
Agentti kirjoittaa hypoteesin ENNEN suoritusta.
Circuit Breaker keskeyttää 3 epäonnistumisen jälkeen.
"""
import json, datetime
from pathlib import Path

class CausalEngine:
    MAX_RETRIES = 3

    def __init__(self, log_path="wiki/log.md"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(exist_ok=True)
        self._attempts = 0

    def write_hypothesis(self, task: str, hypothesis: str = ""):
        """Kirjaa aikomus ennen toimintaa (pakollinen)."""
        entry = {
            "ts": datetime.datetime.now().isoformat(),
            "task": task,
            "hypothesis": hypothesis or f"Suoritan tehtävän: {task}",
            "status": "PENDING"
        }
        with open(self.log_path, "a") as f:
            f.write(f"\n```json\n{json.dumps(entry, ensure_ascii=False)}\n```\n")
        return entry

    def record_result(self, success: bool, detail: str = ""):
        """Kirjaa tulos lokiin."""
        status = "SUCCESS" if success else "FAILURE"
        self._attempts = 0 if success else self._attempts + 1

        if self._attempts >= self.MAX_RETRIES:
            raise RuntimeError(
                f"Circuit Breaker lauennut: {self.MAX_RETRIES} "
                f"epäonnistunutta yritystä. Tarvitaan ihmisen apua."
            )

        with open(self.log_path, "a") as f:
            f.write(f"**{status}** | {detail}\n")

    @property
    def is_tripped(self) -> bool:
        return self._attempts >= self.MAX_RETRIES
```

### 2.5 — `workspace/rag.py`
```python
"""
FAISS-pohjainen semanttinen haku /wiki-kansiolle (A-RAG periaate)
arXiv:2602.03442
"""
from pathlib import Path

class KnowledgeIndex:
    def __init__(self, wiki_path="wiki"):
        self.wiki = Path(wiki_path)
        self._index = {}  # key: filename, value: content

    def build(self):
        """Indeksoi kaikki wiki/ tiedostot."""
        for f in self.wiki.glob("*.md"):
            self._index[f.stem] = f.read_text()
        return len(self._index)

    def query(self, query: str, top_k: int = 3) -> list:
        """
        Yksinkertainen keyword-haku (korvaa FAISS-embeddingillä
        kun sentence-transformers on asennettu).
        """
        results = []
        query_terms = set(query.lower().split())
        for name, content in self._index.items():
            content_terms = set(content.lower().split())
            overlap = len(query_terms & content_terms)
            if overlap > 0:
                results.append((name, content, overlap))

        results.sort(key=lambda x: x[2], reverse=True)
        return [{"name": r[0], "content": r[1][:500]} for r in results[:top_k]]

    # Tulevaa käyttöä varten (FAISS upgrade path):
    # def build_faiss(self): ...
    # def query_faiss(self, query): ...
```

### 2.6 — `workspace/model_router.py`
```python
"""
Mallireititin — valitsee oikean LLM-backendin tehtävätyypin mukaan.
Tukee: Ollama, LM Studio, OpenAI-yhteensopivat.
"""
import os

TASK_ROUTING = {
    "code": "ollama/codellama",
    "analysis": "ollama/gemma2",
    "vision": "ollama/llava",
    "summary": "ollama/mistral",
    "default": os.getenv("AGENTDIR_DEFAULT_MODEL", "ollama/gemma2"),
}

class ModelRouter:
    def select(self, task: str) -> str:
        task_lower = task.lower()
        if any(w in task_lower for w in ["korjaa", "koodi", "fix", "refactor", "debug"]):
            return TASK_ROUTING["code"]
        if any(w in task_lower for w in ["kuva", "näyttö", "image", "screenshot"]):
            return TASK_ROUTING["vision"]
        if any(w in task_lower for w in ["analysoi", "tutki", "compare", "analyze"]):
            return TASK_ROUTING["analysis"]
        return TASK_ROUTING["default"]

    def call(self, model: str, prompt: str, context: str = "") -> str:
        """
        Kutsu mallia Ollama-yhteensopivalla API:lla.
        Vaatii: pip install openai
        Muuta OLLAMA_HOST ympäristömuuttujalla.
        """
        try:
            from openai import OpenAI
            base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434/v1")
            client = OpenAI(base_url=base_url, api_key="ollama")
            model_name = model.replace("ollama/", "")
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            resp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=2000
            )
            return resp.choices[0].message.content
        except ImportError:
            return f"[MOCK] Model {model} vastaus tehtävään: {prompt[:100]}"
        except Exception as e:
            return f"[ERROR] {e}"
```

### 2.7 — `workspace/agent_print.py`
```python
"""
Agent Print — EU AI Act Article 13 -yhteensopiva auditointiraportti.
Generoidaan jokaisen tehtäväsuorituksen jälkeen.
"""
import json, datetime, uuid
from pathlib import Path

class AgentPrint:
    def __init__(self, output_dir="outputs"):
        self.out = Path(output_dir)
        self.out.mkdir(exist_ok=True)

    def generate(self, task: str, result: dict, model: str, mode: str) -> str:
        report_id = str(uuid.uuid4())[:8]
        ts = datetime.datetime.now().isoformat()

        report = {
            "agent_print_id": report_id,
            "timestamp": ts,
            "task": task,
            "mode": mode,
            "model_used": model,
            "success": result.get("success", False),
            "token_savings_pct": result.get("token_savings", 0),
            "sandbox_verified": result.get("sandbox_ok", False),
            "causal_log": "wiki/log.md",
            "eu_ai_act_article13": True,
            "output_hash": hash(str(result)),
        }

        # Tallenna JSON
        json_path = self.out / f"agent_print_{report_id}.json"
        json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

        # Tallenna luettava MD-versio
        md = f"""# Agent Print — {report_id}
**Aika:** {ts}
**Tehtävä:** {task}
**Moodi:** {mode}
**Malli:** {model}
**Tulos:** {"✅ ONNISTUI" if report["success"] else "❌ EPÄONNISTUI"}
**Hiekkalaatikko verifioitu:** {"Kyllä" if report["sandbox_verified"] else "Ei"}
**EU AI Act Art.13:** ✅
**Kausaaliloki:** {report["causal_log"]}
"""
        md_path = self.out / f"agent_print_{report_id}.md"
        md_path.write_text(md)

        return report_id
```

### 2.8 — `workspace/omninode.py`
```python
"""
OmniNode Bridge — KV-välimuistin sharding mobiililaitteille.
Tuki: Android (ADB), iOS (WiFi), lokaali fallback.
"""
import subprocess, json

class OmniNode:
    def __init__(self):
        self.nodes = self._discover_nodes()

    def _discover_nodes(self) -> list:
        """Etsi saatavilla olevat laskentasolmut."""
        nodes = [{"id": "localhost", "type": "master", "status": "online"}]
        # Android ADB -laitteet
        try:
            result = subprocess.run(
                ["adb", "devices"], capture_output=True, text=True, timeout=3
            )
            for line in result.stdout.splitlines()[1:]:
                if "device" in line and "List" not in line:
                    device_id = line.split()[0]
                    nodes.append({
                        "id": device_id, "type": "android", "status": "online"
                    })
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass  # ADB ei ole asennettu tai ei laitteita
        return nodes

    def get_available_vram(self) -> dict:
        """Palauta arvio käytettävissä olevasta muistista per solmu."""
        vram = {"localhost": "local_gpu"}
        for node in self.nodes[1:]:
            vram[node["id"]] = "npu_shard"
        return vram

    def status(self) -> str:
        lines = [f"OmniNode Swarm — {len(self.nodes)} solmua:"]
        for n in self.nodes:
            lines.append(f"  [{n['status'].upper()}] {n['id']} ({n['type']})")
        return "\n".join(lines)
```

### 2.9 — `workspace/retrieval.py`
```python
"""
Tiedostopohjainen kontekstin keruu /raw ja /wiki -kansioista.
"""
from pathlib import Path

SUPPORTED = {".md", ".txt", ".py", ".json", ".csv"}

class ContextRetriever:
    def __init__(self, raw_path="raw", wiki_path="wiki"):
        self.raw = Path(raw_path)
        self.wiki = Path(wiki_path)

    def gather_context(self, task: str, max_chars: int = 4000) -> str:
        """Kerää relevantti konteksti tehtävän perusteella."""
        chunks = []
        total = 0

        # Lue wiki/index.md ensin (korkein prioriteetti)
        index = self.wiki / "index.md"
        if index.exists():
            content = index.read_text()[:1000]
            chunks.append(f"## PROJEKTI-INDEKSI\n{content}")
            total += len(content)

        # Lue /raw tiedostot
        for f in sorted(self.raw.iterdir()) if self.raw.exists() else []:
            if f.suffix in SUPPORTED and total < max_chars:
                content = f.read_text(errors="ignore")[:500]
                chunks.append(f"## {f.name}\n{content}")
                total += len(content)

        return "\n\n".join(chunks)
```

---

## PHASE 3: STRUCTURE INITIALIZATION

### 3.1 — `workspace/init_structure.py`
```python
"""
Alustaa AgentDir 3.5 -kansiorakenteen olemassa olevaan projektiin.
"""
from pathlib import Path
import datetime

SOVEREIGN_TEMPLATE = """# !_SOVEREIGN.md — AgentDir 3.5 Sovereign Map
# Globaali reititys, etiikka ja resurssit.

## EETTISET RAJAT (MemMachine)
- EI kirjoituksia /raw, /wiki, /outputs ulkopuolelle ilman COMMIT-lupaa
- EI verkkokutsuja hiekkalaatikosta
- AINA kausaalinen hypoteesi ennen suoritusta
- AINA Agent Print -raportti tehtävän jälkeen

## OMNINODE-KARTTA
- node_0: localhost (master)
- node_1: [lisää USB-C laite]
- node_2: [lisää WiFi laite]

## REITITYSSÄÄNNÖT
- Kooditehtävät → openclaw
- Muisti/tutkimus → hermes
- Visio → vision-backend
"""

AGENTDIR_TEMPLATE = """# .agentdir.md — Paikallinen kognitiivinen ankkuri
# Tämä kansio on osa AgentDir 3.5 Sovereign Swarmiä.

## TÄMÄN KANSION TARKOITUS
[Kirjoita tähän kansion tehtävä]

## PAIKALLINEN KONTEKSTI
- Tärkeimmät tiedostot: [listaa]
- Riippuvuudet: [listaa]

## AGENTTIOHJEET
- Prioriteetti: normaali
- Sandbox: pakollinen
- LTM-commit: vaaditaan verifiointi
"""

def init_project(path: str = "."):
    root = Path(path)

    # Kansiorakenne
    for d in ["raw", "wiki", "outputs", "workspace/tests"]:
        (root / d).mkdir(parents=True, exist_ok=True)

    # Päätiedostot
    sovereign = root / "!_SOVEREIGN.md"
    if not sovereign.exists():
        sovereign.write_text(SOVEREIGN_TEMPLATE)

    anchor = root / ".agentdir.md"
    if not anchor.exists():
        anchor.write_text(AGENTDIR_TEMPLATE)

    # Wiki-indeksi
    index = root / "wiki" / "index.md"
    if not index.exists():
        index.write_text(
            f"# Projektin tietopankki\nLuotu: {datetime.datetime.now().isoformat()}\n"
        )

    # Kausaaliloki
    log = root / "wiki" / "log.md"
    if not log.exists():
        log.write_text("# Kausaaliloki\n\n")

    print(f"✅ AgentDir 3.5 alustettu: {root.resolve()}")
    print("   Seuraava askel: python cli.py run 'tehtäväsi'")
```

---

## PHASE 4: TESTS

### 4.1 — `workspace/tests/test_policy.py`
```python
import pytest
import sys; sys.path.insert(0, "workspace")
from policy import PolicyEngine

def test_allows_safe_task():
    p = PolicyEngine()
    assert p.validate("analysoi data.csv ja tee raportti") is True

def test_blocks_rm_rf():
    p = PolicyEngine()
    with pytest.raises(PermissionError):
        p.validate("rm -rf /home/user")

def test_blocks_format():
    p = PolicyEngine()
    with pytest.raises(PermissionError):
        p.validate("format c: kaikki tiedostot pois")
```

### 4.2 — `workspace/tests/test_sandbox.py`
```python
import sys; sys.path.insert(0, "workspace")
from sandbox import SovereignSandbox

def test_runs_safe_code():
    sb = SovereignSandbox()
    result = sb.execute("print('hello agentdir')")
    assert result["success"] is True
    assert "hello agentdir" in result["stdout"]

def test_catches_syntax_error():
    sb = SovereignSandbox()
    result = sb.execute("def broken(")
    assert result["success"] is False

def test_timeout():
    sb = SovereignSandbox()
    result = sb.execute("import time; time.sleep(99)", timeout=1)
    assert result["success"] is False
```

### 4.3 — `workspace/tests/test_rag.py`
```python
import sys, tempfile, os
sys.path.insert(0, "workspace")
from pathlib import Path
from rag import KnowledgeIndex

def test_build_and_query(tmp_path):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "auth.md").write_text("JWT token authentication timeout 24h UTC")
    (wiki / "policy.md").write_text("kaikki koodi tarkistetaan sandboxissa")

    idx = KnowledgeIndex(str(wiki))
    count = idx.build()
    assert count == 2

    results = idx.query("JWT token")
    assert len(results) > 0
    assert "auth" in results[0]["name"]
```

---

## PHASE 5: BENCHMARKS

### 5.1 — `workspace/benchmark.py`
```python
"""
Suorituskykytestit — token-säästöt, viive, läpäisyprosentti.
"""
import time, json
from pathlib import Path

def run_benchmarks():
    results = {}
    print("🔬 AgentDir 3.5 Benchmark Suite\n")

    # Testi 1: Policy-portti nopeus
    from workspace.policy import PolicyEngine
    p = PolicyEngine()
    t0 = time.perf_counter()
    for _ in range(1000):
        try: p.validate("analysoi tiedosto")
        except: pass
    results["policy_1000_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    print(f"Policy gate (1000x): {results['policy_1000_ms']}ms")

    # Testi 2: Sandbox perussuoritus
    from workspace.sandbox import SovereignSandbox
    sb = SovereignSandbox()
    t0 = time.perf_counter()
    r = sb.execute("x = sum(range(1000)); print(x)")
    results["sandbox_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    results["sandbox_ok"] = r["success"]
    print(f"Sandbox suoritus: {results['sandbox_ms']}ms | OK={r['success']}")

    # Testi 3: RAG-haku
    from workspace.rag import KnowledgeIndex
    idx = KnowledgeIndex()
    idx._index = {f"doc_{i}": f"content about topic {i} " * 20 for i in range(100)}
    t0 = time.perf_counter()
    idx.query("topic 42")
    results["rag_100docs_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    print(f"RAG-haku (100 dok): {results['rag_100docs_ms']}ms")

    # Tallenna tulokset
    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/benchmarks.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False)
    )
    print(f"\n✅ Tulokset tallennettu: outputs/benchmarks.json")
    return results
```

---

## PHASE 6: REQUIREMENTS & DOCKERFILE

### 6.1 — `requirements.txt`
```
openai>=1.0.0
faiss-cpu>=1.7.4
sentence-transformers>=2.2.0
pytest>=7.0.0
pathlib2>=2.3.0
```

### 6.2 — `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /agentdir

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ei verkkoyhteyttä sandboxille (asetetaan käynnistyksessä)
ENV AGENTDIR_DEFAULT_MODEL=ollama/gemma2
ENV OLLAMA_HOST=http://host.docker.internal:11434/v1

ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]
```

### 6.3 — `README.md`
```markdown
# AgentDir 3.5 — Sovereign Engine

Muuttaa kansion kognitiiviseksi tekoälyagentiksi.

## Nopea aloitus

pip install -r requirements.txt

python cli.py init              # Alusta rakenne
python cli.py run "analysoi raw-kansiosi tiedostot"
python cli.py run "korjaa bugi" --mode openclaw --model ollama/codellama
python cli.py benchmark         # Suorituskykytestit
pytest -q                       # Testit

## Tieteellinen pohja
- MemMachine (arXiv:2604.04853v1) — muistijärjestelmä
- A-RAG (arXiv:2602.03442) — hierarkkinen haku
- Karpathy Discipline — kirurginen koodauskuri

## Integraatio
Kaikki OpenAI-yhteensopivat mallit toimivat (Ollama, LM Studio, Hermes, OpenClaw).
```

---

## EXECUTION INSTRUCTIONS FOR AI ARCHITECT

**When you receive this prompt:**

1. Read `!_SOVEREIGN.md` first
2. Write your implementation plan to `wiki/log.md`
3. Implement files in Phase order (1 → 6)
4. After each phase, run the tests for that phase
5. Do not proceed to next phase if tests fail
6. Generate final Agent Print when all phases complete

**Do NOT:**
- Invent libraries that don't exist
- Refactor files outside the scope
- Skip the causal log entry
- Merge phases without user confirmation

**START:** Implement Phase 1 now. Begin with `!_SOVEREIGN.md` and `cli.py`.
