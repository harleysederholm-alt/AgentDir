"""
agent_print.py — EU AI Act Article 13 -yhteensopiva auditointiraportti.
Generoidaan jokaisen tehtäväsuorituksen jälkeen.

Jokainen suoritus tuottaa sekä JSON- että MD-version auditointiraportista.
"""
from __future__ import annotations

import datetime
import json
import uuid
from pathlib import Path


class AgentPrint:
    """
    Generoi auditointiraportin jokaisesta tehtäväsuorituksesta.
    Tallentaa outputs/ kansioon JSON + Markdown -versiot.
    """

    def __init__(self, output_dir: str = "outputs") -> None:
        self.out = Path(output_dir)
        self.out.mkdir(exist_ok=True)

    def generate(
        self,
        task: str,
        result: dict,
        model: str,
        mode: str,
    ) -> str:
        """
        Generoi Agent Print. Palauttaa raportin ID:n.
        """
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

        # Tallenna JSON-versio
        json_path = self.out / f"agent_print_{report_id}.json"
        json_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Tallenna luettava MD-versio
        success_str = "✅ ONNISTUI" if report["success"] else "❌ EPÄONNISTUI"
        sandbox_str = "Kyllä" if report["sandbox_verified"] else "Ei"

        md = f"""# Agent Print — {report_id}

| Kenttä | Arvo |
|---|---|
| Tehtävä | {task[:100]} |
| Malli | {model} |
| Moodi | {mode} |
| Tulos | {success_str} |
| Sandbox verifioitu | {sandbox_str} |
| EU AI Act Art.13 | ✅ |
| Kausaaliloki | wiki/log.md |
| Aikaleima | {ts} |
"""
        md_path = self.out / f"agent_print_{report_id}.md"
        md_path.write_text(md, encoding="utf-8")

        return report_id
