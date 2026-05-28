from __future__ import annotations

import json
from pathlib import Path

from cltd.schemas import AgentRunLog


def append_run_log(path: Path, record: AgentRunLog) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(record.model_dump_json() + "\n")


def read_run_logs(path: Path) -> list[AgentRunLog]:
    if not path.exists():
        return []
    records: list[AgentRunLog] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(AgentRunLog.model_validate(json.loads(line)))
    return records
