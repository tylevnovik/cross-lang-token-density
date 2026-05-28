from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd
import typer

from cltd.preprocessing.clean import clean_code
from cltd.preprocessing.normalize import normalize_raw_code
from cltd.preprocessing.sloc import count_sloc
from cltd.schemas import CodeVariantRecord, SnippetRecord

app = typer.Typer()


@app.command()
def main(
    snippets_path: Path = Path("data/interim/rosettacode_snippets.jsonl"),
    variants_output: Path = Path("data/processed/code_variants.parquet"),
    warnings_output: Path = Path("data/results/preprocess_warnings.csv"),
) -> None:
    if not snippets_path.exists():
        typer.echo(f"Error: snippets file not found at {snippets_path}", err=True)
        raise typer.Exit(code=1)

    snippets: list[SnippetRecord] = []
    with snippets_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                snippets.append(SnippetRecord.model_validate(json.loads(line)))

    variant_records: list[CodeVariantRecord] = []
    warnings_list = []

    typer.echo(f"Processing {len(snippets)} snippets...")

    for snippet in snippets:
        record_id = snippet.record_id
        lang = snippet.language
        raw_code = snippet.code_raw

        # 1. Generate Raw Variant
        normalized_raw = normalize_raw_code(raw_code)
        raw_record = CodeVariantRecord(
            variant_id=f"{record_id}:raw",
            record_id=record_id,
            variant="raw",
            code=normalized_raw,
            char_count=len(normalized_raw),
            byte_count=len(normalized_raw.encode("utf-8")),
            sloc=count_sloc(normalized_raw),
            cleaner="normalize_v1",
            cleaner_status="ok",
            cleaner_warnings=[],
        )
        variant_records.append(raw_record)

        # 2. Generate Clean Variant
        cleaned, status, warnings = clean_code(raw_code, lang)
        clean_record = CodeVariantRecord(
            variant_id=f"{record_id}:clean",
            record_id=record_id,
            variant="clean",
            code=cleaned,
            char_count=len(cleaned),
            byte_count=len(cleaned.encode("utf-8")),
            sloc=count_sloc(cleaned),
            cleaner="pygments_clean_v1",
            cleaner_status=status,
            cleaner_warnings=warnings,
        )
        variant_records.append(clean_record)

        # Record warnings/errors if any
        if status != "ok":
            warnings_list.append({
                "record_id": record_id,
                "language": lang,
                "variant": "clean",
                "cleaner_status": status,
                "warnings": "; ".join(warnings),
            })

        # 3. Generate Canonical Variant (optional/unavailable for Phase 1)
        # As planned: canonical variant copies clean but sets status to unavailable
        canonical_record = CodeVariantRecord(
            variant_id=f"{record_id}:canonical",
            record_id=record_id,
            variant="canonical",
            code=cleaned,
            char_count=len(cleaned),
            byte_count=len(cleaned.encode("utf-8")),
            sloc=count_sloc(cleaned),
            cleaner="formatter_none",
            cleaner_status="unavailable",
            cleaner_warnings=[],
        )
        variant_records.append(canonical_record)

    # Convert to pandas DataFrame and write to Parquet
    variants_output.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([r.model_dump() for r in variant_records])
    df.to_parquet(variants_output, index=False)
    typer.echo(f"Wrote {len(variant_records)} variant records to {variants_output}")

    # Write warnings to CSV
    warnings_output.parent.mkdir(parents=True, exist_ok=True)
    with warnings_output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["record_id", "language", "variant", "cleaner_status", "warnings"]
        )
        writer.writeheader()
        writer.writerows(warnings_list)
    typer.echo(f"Wrote {len(warnings_list)} warning records to {warnings_output}")


if __name__ == "__main__":
    app()
