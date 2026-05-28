from __future__ import annotations

import csv
import json
from pathlib import Path

import typer
import yaml

from cltd.datasets.equivalence import build_coverage, strict_intersection_groups, classify_task_category
from cltd.schemas import SnippetRecord

app = typer.Typer()


def load_languages_config(path: Path) -> tuple[set[str], set[str]]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = set(config["primary_intersection"]["required_languages"])
    optional = set(config["primary_intersection"]["optional_languages"])
    return required, optional


@app.command()
def main(
    snippets_path: Path = Path("data/interim/rosettacode_snippets.jsonl"),
    languages_config: Path = Path("configs/languages.yaml"),
    groups_output: Path = Path("data/processed/equivalence_groups.csv"),
    coverage_output: Path = Path("data/results/coverage_by_language.csv"),
    intersection_output: Path = Path("data/results/strict_intersection_tasks.csv"),
) -> None:
    required_langs, optional_langs = load_languages_config(languages_config)
    
    # Read snippets
    records: list[SnippetRecord] = []
    if not snippets_path.exists():
        typer.echo(f"Error: snippets file not found at {snippets_path}", err=True)
        raise typer.Exit(code=1)
        
    with snippets_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(SnippetRecord.model_validate(json.loads(line)))

    # Build coverage
    coverage = build_coverage(records)
    strict_groups = strict_intersection_groups(records, required_langs)
    
    # 1. Write equivalence_groups.csv
    groups_output.parent.mkdir(parents=True, exist_ok=True)
    # We want unique groups by ID, but also map task_id and task_name.
    # Grouping records by equivalence_group_id to get stable task_id and task_name
    group_info = {}
    for r in records:
        if r.equivalence_group_id not in group_info:
            group_info[r.equivalence_group_id] = {
                "task_id": r.task_id,
                "task_name": r.task_name,
            }

    with groups_output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "equivalence_group_id",
            "task_id",
            "task_name",
            "task_category",
            "languages_present",
            "required_language_count",
            "has_required_intersection",
            "has_optional_typescript",
        ])
        for group_id, langs in sorted(coverage.items()):
            info = group_info[group_id]
            langs_present_str = ",".join(sorted(langs))
            req_count = len(langs.intersection(required_langs))
            has_req = req_count == len(required_langs)
            has_ts = "typescript" in langs
            cat = classify_task_category(info["task_name"])
            writer.writerow([
                group_id,
                info["task_id"],
                info["task_name"],
                cat,
                langs_present_str,
                req_count,
                str(has_req).lower(),
                str(has_ts).lower(),
            ])
            
    # 2. Write coverage_by_language.csv
    coverage_output.parent.mkdir(parents=True, exist_ok=True)
    lang_counts = {}
    for langs in coverage.values():
        for lang in langs:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            
    with coverage_output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["language", "task_count"])
        for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([lang, count])

    # 3. Write strict_intersection_tasks.csv
    intersection_output.parent.mkdir(parents=True, exist_ok=True)
    with intersection_output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["equivalence_group_id", "task_name"])
        for group_id in sorted(strict_groups):
            writer.writerow([group_id, group_info[group_id]["task_name"]])

    typer.echo(f"Total equivalence groups: {len(coverage)}")
    typer.echo(f"Strict intersection groups ({', '.join(required_langs)}): {len(strict_groups)}")
    
    if len(strict_groups) < 100:
        typer.echo(
            f"WARNING: Strict intersection task count ({len(strict_groups)}) is under 100! "
            "This may introduce research risks.",
            err=True
        )


if __name__ == "__main__":
    app()
