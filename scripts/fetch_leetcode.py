from __future__ import annotations

from pathlib import Path

import typer
import yaml

from cltd.datasets.leetcode import iter_leetcode_records

app = typer.Typer()


def load_language_map(path: Path) -> dict[str, str]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    mapping: dict[str, str] = {}
    for language in config["languages"]:
        for rosetta_name in language["rosetta_names"]:
            mapping[rosetta_name] = language["id"]
    return mapping


@app.command()
def main(
    root: Path = Path("data/raw/leetcode"),
    languages: Path = Path("configs/languages.yaml"),
    output: Path = Path("data/interim/leetcode_snippets.jsonl"),
) -> None:
    language_map = load_language_map(languages)
    records = iter_leetcode_records(root, language_map)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")
    typer.echo(f"wrote {len(records)} records to {output}")


if __name__ == "__main__":
    app()
