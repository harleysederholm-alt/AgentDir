"""
AgentDir – evolution.log (JSONL)

Yksinkertainen lokimerkintä onnistuneista Inbox → Outbox -ajoista (vektorimuisti erikseen).
Tiedosto ``evolution.log`` agentin juurihakemistossa; yksi JSON-objekti per rivi.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("agentdir.evolution_log")

LOG_FILENAME = "evolution.log"


def append_success_record(
    root: Path,
    *,
    task_size_bytes: int,
    model: str,
    source_file: str,
    outbox_file: str,
    status: str = "success",
) -> None:
    """
    Lisää JSONL-rivi ``evolution.log`` -tiedostoon.

    Kentät: timestamp (UTC ISO), task_size_bytes, model, source_file, outbox_file, status.
    """
    root = Path(root)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_size_bytes": int(task_size_bytes),
        "model": model,
        "source_file": source_file,
        "outbox_file": outbox_file,
        "status": status,
    }
    path = root / LOG_FILENAME
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.error("evolution.log kirjoitus epäonnistui: %s", e)
