from datetime import UTC, datetime

from cltd.schemas import CodeVariantRecord, SnippetRecord, TokenCountRecord


def test_snippet_record_accepts_minimal_valid_record():
    record = SnippetRecord(
        record_id="rosetta:fib:python:0",
        dataset="rosettacode",
        dataset_version="git:abc123",
        source_uri="https://github.com/acmeism/RosettaCodeData",
        source_path="Task/Fibonacci sequence/Python/example.py",
        task_id="fibonacci_sequence",
        task_name="Fibonacci sequence",
        language="python",
        equivalence_group_id="rosetta:fibonacci_sequence",
        equivalence_confidence="source_aligned",
        code_raw="print('hello')\n",
        code_raw_sha256="abc",
        ingested_at=datetime(2026, 5, 26, tzinfo=UTC),
    )

    assert record.language == "python"


def test_code_variant_rejects_negative_counts():
    try:
        CodeVariantRecord(
            variant_id="x",
            record_id="r",
            variant="clean",
            code="",
            char_count=-1,
            byte_count=0,
            sloc=0,
            cleaner="test",
            cleaner_status="ok",
        )
    except ValueError as exc:
        assert "greater than or equal to 0" in str(exc)
    else:
        raise AssertionError("negative char_count should fail validation")


def test_token_count_rejects_negative_tokens():
    try:
        TokenCountRecord(
            token_count_id="x",
            variant_id="v",
            tokenizer_provider="openai",
            tokenizer_name="o200k_base",
            tokenizer_package="tiktoken",
            tokenizer_package_version="0.7.0",
            token_count=-1,
            counted_at=datetime(2026, 5, 26, tzinfo=UTC),
        )
    except ValueError as exc:
        assert "greater than or equal to 0" in str(exc)
    else:
        raise AssertionError("negative token_count should fail validation")
