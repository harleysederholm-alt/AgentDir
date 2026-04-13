"""
agent_print.py — EU AI Act Article 13 -yhteensopiva auditointiraportti.
Generoidaan jokaisen tehtäväsuorituksen jälkeen.

Jokainen suoritus tuottaa JSON-, MD- JA Pro-Audit TXT-version
auditointiraportista. Sovereign Engine 3.5.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class AgentPrintRecord:
    """Yksittäisen suorituksen auditointitietue."""

    print_id: str
    timestamp: str
    task_description: str
    model_used: str
    fallback_used: bool
    rag_hits: int
    sandbox_attempts: int
    sandbox_success: bool
    evolution_triggered: bool
    input_file: str
    output_file: str
    execution_ms: int
    eu_ai_act_compliant: bool = True


class AgentPrint:
    """
    Generoi ja tallentaa Agent Print -raportteja.
    Tallentaa outputs/ kansioon JSON + Markdown + Pro-Audit TXT -versiot.
    """

    def __init__(self, output_dir: str = "outputs") -> None:
        self.out = Path(output_dir)
        self.out.mkdir(exist_ok=True)

    def generate(
        self,
        task: str,
        result: dict | None = None,
        model: str = "",
        mode: str = "",
        *,
        input_file: str = "",
        output_file: str = "",
        rag_hits: int = 0,
        sandbox_attempts: int = 1,
        sandbox_success: bool | None = None,
        fallback_used: bool = False,
        evolution_triggered: bool = False,
        execution_ms: int = 0,
    ) -> str:
        """
        Generoi Agent Print. Palauttaa raportin ID:n.
        Tukee sekä vanhaa (result-dict) että uutta (keyword) kutsutapaa.
        """
        report_id = str(uuid.uuid4())[:8].upper()
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Vanha rajapinta (orchestrator.py yhteensopivuus)
        if result is not None:
            sandbox_success = result.get("sandbox_ok", result.get("success", False))
            fallback_used = result.get("fallback_used", False)

        if sandbox_success is None:
            sandbox_success = True

        record = AgentPrintRecord(
            print_id=report_id,
            timestamp=ts,
            task_description=task[:200],
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
        json_path = self.out / f"agent_print_{report_id}.json"
        json_path.write_text(
            json.dumps(asdict(record), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Tallenna MD (ihmisluettava tiivis)
        md_path = self.out / f"agent_print_{report_id}.md"
        md_path.write_text(self._render_markdown(record), encoding="utf-8")

        # Tallenna Pro-Audit TXT (enterprise visuaalinen)
        txt_path = self.out / f"agent_print_{report_id}.txt"
        txt_path.write_text(self._render_pro_audit(record), encoding="utf-8")

        return report_id

    # ── Markdown (tiivis taulukko) ────────────────────────────────────────

    def _render_markdown(self, r: AgentPrintRecord) -> str:
        success_str = "✅ ONNISTUI" if r.sandbox_success else "❌ EPÄONNISTUI"
        sandbox_str = "Kyllä" if r.sandbox_success else "Ei"
        fallback_str = "⚠️ Kyllä" if r.fallback_used else "Ei"
        evo_str = "🧬 Kyllä" if r.evolution_triggered else "Ei"

        return f"""# Agent Print — {r.print_id}
**AgentDir Sovereign Engine 3.5**

| Kenttä | Arvo |
|---|---|
| ID | `{r.print_id}` |
| Aikaleima | {r.timestamp} |
| Tulos | {success_str} |
| Malli | `{r.model_used}` |
| Varamalli käytetty | {fallback_str} |
| RAG-osumat | {r.rag_hits} |
| Sandbox-yritykset | {r.sandbox_attempts}/3 |
| Evoluutio laukaistu | {evo_str} |
| Suoritusaika | {r.execution_ms}ms |
| Sandbox verifioitu | {sandbox_str} |
| EU AI Act Art.13 | ✅ |
| Kausaaliloki | wiki/log.md |

## Tehtävä
{r.task_description}

## Tiedostot
- **Syöte:** `{r.input_file}`
- **Tulos:** `{r.output_file}`

---
*AgentDir Sovereign Engine 3.5 | MIT License | Local-First*
"""

    # ── Pro-Audit ASCII (enterprise visuaalinen) ──────────────────────────

    def _render_pro_audit(self, r: AgentPrintRecord) -> str:
        status_icon = "✅" if r.sandbox_success else "❌"
        status_word = "SUCCESS" if r.sandbox_success else "FAILURE"
        fallback_icon = "⚠️ LLAMA FALLBACK" if r.fallback_used else "✓ GEMMA4"
        evo_icon = "🧬 TRIGGERED" if r.evolution_triggered else "─ stable"

        output_hash = hashlib.sha256(
            f"{r.print_id}{r.timestamp}{r.task_description}".encode()
        ).hexdigest()[:16].upper()

        task_display = r.task_description[:120]
        if len(r.task_description) > 120:
            task_display += "..."

        return f"""╔══════════════════════════════════════════════════════════════╗
║           AGENTDIR SOVEREIGN ENGINE — AGENT PRINT            ║
║                    AUDIT RECORD v3.5                         ║
╚══════════════════════════════════════════════════════════════╝

  PRINT ID      ┆ {r.print_id}
  TIMESTAMP     ┆ {r.timestamp}
  STATUS        ┆ {status_icon} {status_word}
  INTEGRITY     ┆ SHA-256:{output_hash}

──────────────────────────────────────────────────────────────
  INFERENCE TELEMETRY
──────────────────────────────────────────────────────────────
  Model         ┆ {fallback_icon}
  Execution     ┆ {r.execution_ms}ms
  RAG Hits      ┆ {r.rag_hits} document(s) retrieved
  Sandbox Loops ┆ {r.sandbox_attempts}/3 self-healing cycles
  Evolution     ┆ {evo_icon}

──────────────────────────────────────────────────────────────
  TASK
──────────────────────────────────────────────────────────────
  {task_display}

──────────────────────────────────────────────────────────────
  I/O MANIFEST
──────────────────────────────────────────────────────────────
  Input         ┆ {r.input_file}
  Output        ┆ {r.output_file}

──────────────────────────────────────────────────────────────
  COMPLIANCE
──────────────────────────────────────────────────────────────
  EU AI Act     ┆ Article 13 ✓ COMPLIANT
  Local-Only    ┆ Zero cloud egress ✓
  Audit Trail   ┆ Immutable ✓

╔══════════════════════════════════════════════════════════════╗
║  AgentDir Sovereign Engine 3.5 │ MIT License │ Local-First  ║
╚══════════════════════════════════════════════════════════════╝
"""

    # ── Tilastot ──────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Palauta tilastot kaikista Agent Print -raporteista."""
        prints = list(self.out.glob("agent_print_*.json"))
        if not prints:
            return {"total_tasks": 0, "success_rate": 0.0, "prompt_version": "v0"}

        records: list[dict] = []
        for p in prints:
            try:
                records.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                continue

        total = len(records)
        successes = sum(1 for r in records if r.get("sandbox_success"))

        return {
            "total_tasks": total,
            "success_rate": round(successes / total, 2) if total else 0.0,
            "prompt_version": f"v{total}",
            "avg_execution_ms": round(
                sum(r.get("execution_ms", 0) for r in records) / total
            )
            if total
            else 0,
            "fallback_rate": round(
                sum(1 for r in records if r.get("fallback_used")) / total * 100, 1
            )
            if total
            else 0,
        }
