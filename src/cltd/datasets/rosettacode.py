from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path

from cltd.schemas import SnippetRecord


def normalize_task_id(name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower())
    return normalized.strip("_")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def iter_rosetta_records(root: Path, language_map: dict[str, str]) -> list[SnippetRecord]:
    task_root = root / "Task"
    records: list[SnippetRecord] = []
    if not task_root.exists():
        raise FileNotFoundError(f"missing Task directory: {task_root}")

    version_file = root.parent / "rosettacode_COMMIT.txt"
    if version_file.exists():
        dataset_version = f"git:{version_file.read_text(encoding='utf-8').strip()}"
    else:
        dataset_version = "git:unknown"

    for task_dir in sorted(p for p in task_root.iterdir() if p.is_dir()):
        task_id = normalize_task_id(task_dir.name)
        for language_dir in sorted(p for p in task_dir.iterdir() if p.is_dir()):
            language = language_map.get(language_dir.name)
            if language is None:
                continue
            source_files = sorted(p for p in language_dir.rglob("*") if p.is_file())
            for index, source_file in enumerate(source_files):
                code = source_file.read_text(encoding="utf-8", errors="replace")
                records.append(
                    SnippetRecord(
                        record_id=f"rosetta:{task_id}:{language}:{index}",
                        dataset="rosettacode",
                        dataset_version=dataset_version,
                        source_uri="https://github.com/acmeism/RosettaCodeData",
                        source_path=str(source_file.relative_to(root)).replace("\\", "/"),
                        task_id=task_id,
                        task_name=task_dir.name,
                        language=language,
                        implementation_index=index,
                        equivalence_group_id=f"rosetta:{task_id}",
                        equivalence_confidence="source_aligned",
                        license="source_repo_license",
                        code_raw=code,
                        code_raw_sha256=sha256_text(code),
                        ingested_at=datetime.now(UTC),
                    )
                )
    return records
