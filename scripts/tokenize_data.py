from __future__ import annotations

import datetime
from pathlib import Path

import pandas as pd
import typer

from cltd.schemas import TokenCountRecord
from cltd.tokenizers.registry import get_tokenizer

app = typer.Typer()


@app.command()
def main(
    variants_path: Path = Path("data/processed/code_variants.parquet"),
    token_counts_output: Path = Path("data/processed/token_counts.parquet"),
    summary_output: Path = Path("data/results/tokenizer_summary.csv"),
) -> None:
    if not variants_path.exists():
        typer.echo(f"Error: variants file not found at {variants_path}", err=True)
        raise typer.Exit(code=1)

    df_variants = pd.read_parquet(variants_path)
    typer.echo(f"Loaded {len(df_variants)} code variants. Counting tokens...")

    token_records: list[TokenCountRecord] = []
    target_tokenizers = ["cl100k_base", "o200k_base"]

    # Pre-fetch tokenizers to avoid lookup overhead in the loop
    tokenizers = {name: get_tokenizer(name) for name in target_tokenizers}

    now = datetime.datetime.now(datetime.timezone.utc)

    # Tiktoken count loop
    for idx, row in df_variants.iterrows():
        variant_id = row["variant_id"]
        # Handle possible null/None code strings safely
        code_text = row["code"] if row["code"] is not None else ""

        for name, tokenizer in tokenizers.items():
            count = tokenizer.count(code_text)
            token_records.append(
                TokenCountRecord(
                    token_count_id=f"{variant_id}:{name}",
                    variant_id=variant_id,
                    tokenizer_provider=tokenizer.provider,
                    tokenizer_name=tokenizer.name,
                    tokenizer_package=tokenizer.package,
                    tokenizer_package_version=tokenizer.package_version,
                    token_count=count,
                    counted_at=now,
                )
            )

    # Write to Parquet
    token_counts_output.parent.mkdir(parents=True, exist_ok=True)
    df_counts = pd.DataFrame([r.model_dump() for r in token_records])
    df_counts.to_parquet(token_counts_output, index=False)
    typer.echo(f"Wrote {len(df_counts)} token count records to {token_counts_output}")

    # Generate summary CSV
    # Join with variants to get variant type (raw, clean, canonical)
    df_merged = df_counts.merge(
        df_variants[["variant_id", "variant"]], on="variant_id", how="left"
    )
    
    summary_data = []
    grouped = df_merged.groupby(["tokenizer_name", "variant"])
    for (tok_name, variant_type), group in grouped:
        summary_data.append({
            "tokenizer_name": tok_name,
            "variant": variant_type,
            "total_tokens": int(group["token_count"].sum()),
            "mean_tokens": float(group["token_count"].mean()),
            "median_tokens": float(group["token_count"].median()),
            "max_tokens": int(group["token_count"].max()),
            "min_tokens": int(group["token_count"].min()),
        })

    summary_output.parent.mkdir(parents=True, exist_ok=True)
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_csv(summary_output, index=False)
    typer.echo(f"Wrote tokenizer summary statistics to {summary_output}")


if __name__ == "__main__":
    app()
