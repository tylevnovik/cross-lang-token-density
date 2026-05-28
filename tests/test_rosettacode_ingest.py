from pathlib import Path

from cltd.datasets.rosettacode import iter_rosetta_records, normalize_task_id


def test_normalize_task_id():
    assert normalize_task_id("Fibonacci sequence") == "fibonacci_sequence"


def test_iter_rosetta_records_reads_language_directories():
    root = Path("tests/fixtures/rosetta_sample")
    records = iter_rosetta_records(root, {"Python": "python", "Java": "java"})

    assert {r.language for r in records} == {"python", "java"}
    assert {r.task_id for r in records} == {"fibonacci_sequence"}
