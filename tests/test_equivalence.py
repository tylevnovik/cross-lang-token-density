from datetime import UTC, datetime

from cltd.datasets.equivalence import strict_intersection_groups
from cltd.schemas import SnippetRecord


def make_record(group: str, language: str) -> SnippetRecord:
    return SnippetRecord(
        record_id=f"{group}:{language}:0",
        dataset="test",
        dataset_version="git:test",
        source_uri="local",
        source_path=f"{language}.txt",
        task_id=group,
        task_name=group,
        language=language,
        equivalence_group_id=group,
        equivalence_confidence="source_aligned",
        code_raw="x",
        code_raw_sha256="sha",
        ingested_at=datetime(2026, 5, 26, tzinfo=UTC),
    )


def test_strict_intersection_groups():
    records = [
        make_record("g1", "python"),
        make_record("g1", "java"),
        make_record("g2", "python"),
    ]

    assert strict_intersection_groups(records, {"python", "java"}) == {"g1"}


def test_classify_task_category():
    from cltd.datasets.equivalence import classify_task_category
    assert classify_task_category("Fibonacci sequence") == "Math/Numeric"
    assert classify_task_category("Binary search") == "Algorithms/DS"
    assert classify_task_category("String matching") == "Text/String"
    assert classify_task_category("HTTP server") == "System/IO"
    assert classify_task_category("Unknown generic task") == "General/Other"

