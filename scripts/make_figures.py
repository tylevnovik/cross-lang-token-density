from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import typer

from cltd.analysis.figures import (
    plot_paired_ratios_boxplot,
    plot_ratio_heatmap,
    plot_raw_clean_delta,
    plot_task_size_effects,
    plot_task_category_effects,
    plot_char_to_token_ratio,
    plot_leetcode_paired_boxplot,
)

app = typer.Typer()


@app.command()
def main(
    dataset: str = "rosetta",
    paired_path: Path | None = None,
    summary_path: Path | None = None,
    sensitivity_path: Path | None = None,
    snippets_path: Path | None = None,
    boxplot_out: Path | None = None,
    heatmap_out: Path | None = None,
    delta_out: Path | None = None,
    effects_out: Path | None = None,
    size_effects_out: Path | None = None,
    char_to_token_out: Path | None = None,
) -> None:
    # 动态设定默认路径
    if dataset == "rosetta":
        paired_path = paired_path or Path("data/results/paired_language_ratios.csv")
        summary_path = summary_path or Path("data/results/summary_by_language.csv")
        sensitivity_path = sensitivity_path or Path("data/results/sensitivity_analysis.csv")
        boxplot_out = boxplot_out or Path("report/figures/boxplot_token_count_by_language.png")
        heatmap_out = heatmap_out or Path("report/figures/ratio_heatmap_by_tokenizer.png")
        delta_out = delta_out or Path("report/figures/raw_clean_delta_by_language.png")
        effects_out = effects_out or Path("report/figures/task_category_effects.png")
        size_effects_out = size_effects_out or Path("report/figures/task_size_effects.png")
        char_to_token_out = char_to_token_out or Path("report/figures/char_to_token_ratio.png")
    elif dataset == "leetcode":
        paired_path = paired_path or Path("data/results/leetcode_paired_language_ratios.csv")
        summary_path = summary_path or Path("data/results/leetcode_summary_by_language.csv")
        sensitivity_path = sensitivity_path or Path("data/results/leetcode_sensitivity_analysis.csv")
        snippets_path = snippets_path or Path("data/interim/leetcode_snippets.jsonl")
        boxplot_out = boxplot_out or Path("report/figures/leetcode_boxplot_by_difficulty.png")
    else:
        typer.echo(f"Error: Unknown dataset '{dataset}'", err=True)
        raise typer.Exit(code=1)

    # Check inputs
    inputs = [paired_path, summary_path, sensitivity_path]
    for p in inputs:
        if not p.exists():
            typer.echo(f"Error: required file {p} does not exist", err=True)
            raise typer.Exit(code=1)

    typer.echo(f"Loading {dataset} data files for plotting...")
    df_paired = pd.read_csv(paired_path)
    df_summary = pd.read_csv(summary_path)
    df_stats = pd.read_csv(sensitivity_path)

    if dataset == "rosetta":
        # 1. Boxplot
        typer.echo(f"Plotting boxplot -> {boxplot_out} ...")
        plot_paired_ratios_boxplot(df_paired, boxplot_out)

        # 2. Heatmap
        typer.echo(f"Plotting heatmap -> {heatmap_out} ...")
        plot_ratio_heatmap(df_stats, heatmap_out)

        # 3. Raw-clean Delta
        typer.echo(f"Plotting raw-clean delta -> {delta_out} ...")
        plot_raw_clean_delta(df_summary, delta_out)

        # 4. Size Effects
        typer.echo(f"Plotting size effects -> {size_effects_out} ...")
        plot_task_size_effects(df_paired, size_effects_out)

        # 5. Task Category Effects
        typer.echo(f"Plotting task category effects -> {effects_out} ...")
        plot_task_category_effects(df_stats, effects_out)

        # 6. Char-to-Token Ratio (Fragmentation)
        typer.echo(f"Plotting char-to-token ratio -> {char_to_token_out} ...")
        plot_char_to_token_ratio(df_summary, char_to_token_out)

    elif dataset == "leetcode":
        # 载入 snippets
        snippets_list = []
        with snippets_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    snippets_list.append(json.loads(line))
        df_snippets = pd.DataFrame(snippets_list)
        
        # 1. LeetCode difficulty boxplot
        typer.echo(f"Plotting LeetCode boxplot by difficulty -> {boxplot_out} ...")
        plot_leetcode_paired_boxplot(df_paired, df_snippets, boxplot_out)

    typer.echo("All figures generated successfully.")


if __name__ == "__main__":
    app()


