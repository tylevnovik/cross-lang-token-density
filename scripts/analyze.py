from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import scipy.stats as stats
import typer

from cltd.analysis.paired import build_paired_ratios
from cltd.analysis.statistics import bootstrap_median_ci, cliffs_delta, run_paired_test, holm_bonferroni_correction

app = typer.Typer()


@app.command()
def main(
    dataset: str = "rosetta",
    snippets_path: Path | None = None,
    variants_path: Path | None = None,
    token_counts_path: Path | None = None,
    equivalence_groups_path: Path | None = None,
    summary_output: Path | None = None,
    paired_output: Path | None = None,
    stat_tests_output: Path | None = None,
    sensitivity_output: Path | None = None,
) -> None:
    # 动态设定默认路径
    if dataset == "rosetta":
        snippets_path = snippets_path or Path("data/interim/rosettacode_snippets.jsonl")
        variants_path = variants_path or Path("data/processed/code_variants.parquet")
        token_counts_path = token_counts_path or Path("data/processed/token_counts.parquet")
        equivalence_groups_path = equivalence_groups_path or Path("data/processed/equivalence_groups.csv")
        summary_output = summary_output or Path("data/results/summary_by_language.csv")
        paired_output = paired_output or Path("data/results/paired_language_ratios.csv")
        stat_tests_output = stat_tests_output or Path("data/results/stat_tests.csv")
        sensitivity_output = sensitivity_output or Path("data/results/sensitivity_analysis.csv")
    elif dataset == "leetcode":
        snippets_path = snippets_path or Path("data/interim/leetcode_snippets.jsonl")
        variants_path = variants_path or Path("data/processed/leetcode_variants.parquet")
        token_counts_path = token_counts_path or Path("data/processed/leetcode_token_counts.parquet")
        summary_output = summary_output or Path("data/results/leetcode_summary_by_language.csv")
        paired_output = paired_output or Path("data/results/leetcode_paired_language_ratios.csv")
        stat_tests_output = stat_tests_output or Path("data/results/leetcode_stat_tests.csv")
        sensitivity_output = sensitivity_output or Path("data/results/leetcode_sensitivity_analysis.csv")
    else:
        typer.echo(f"Error: Unknown dataset '{dataset}'", err=True)
        raise typer.Exit(code=1)

    # 校验文件存在性
    required_paths = [snippets_path, variants_path, token_counts_path]
    if dataset == "rosetta":
        required_paths.append(equivalence_groups_path)
    for p in required_paths:
        if not p.exists():
            typer.echo(f"Error: required file {p} does not exist", err=True)
            raise typer.Exit(code=1)

    typer.echo(f"Loading {dataset} data files...")
    # 载入 snippets
    snippets_list = []
    with snippets_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                snippets_list.append(json.loads(line))
    df_snippets = pd.DataFrame(snippets_list)

    # 载入 Parquet
    df_variants = pd.read_parquet(variants_path)
    df_counts = pd.read_parquet(token_counts_path)

    # 2. Build paired ratios table
    typer.echo("Building paired ratios table...")
    df_paired = build_paired_ratios(df_snippets, df_variants, df_counts)
    
    paired_output.parent.mkdir(parents=True, exist_ok=True)
    df_paired.to_csv(paired_output, index=False)
    typer.echo(f"Wrote full paired language ratios to {paired_output}")

    # 3. Descriptive Summary
    typer.echo("Computing summary statistics by language...")
    df_tokens_full = df_counts.merge(
        df_variants[["variant_id", "record_id", "variant", "char_count", "sloc"]], on="variant_id", how="inner"
    ).merge(
        df_snippets[["record_id", "language"]], on="record_id", how="inner"
    )
    
    # 避免除以 0
    df_tokens_full["char_to_token_ratio"] = df_tokens_full.apply(
        lambda r: r["char_count"] / r["token_count"] if r["token_count"] > 0 else None, axis=1
    )
    df_tokens_full["tokens_per_line"] = df_tokens_full.apply(
        lambda r: r["token_count"] / r["sloc"] if r["sloc"] > 0 else None, axis=1
    )
    
    summary_list = []
    grouped_desc = df_tokens_full.groupby(["language", "variant", "tokenizer_name"])
    for (lang, var, tok), group in grouped_desc:
        ct_ratios = group["char_to_token_ratio"].dropna()
        tpl_ratios = group["tokens_per_line"].dropna()
        summary_list.append({
            "language": lang,
            "variant": var,
            "tokenizer": tok,
            "mean_tokens": float(group["token_count"].mean()),
            "median_tokens": float(group["token_count"].median()),
            "total_tokens": int(group["token_count"].sum()),
            "n_snippets": len(group),
            "median_char_to_token_ratio": float(ct_ratios.median()) if not ct_ratios.empty else None,
            "median_tokens_per_line": float(tpl_ratios.median()) if not tpl_ratios.empty else None,
        })
    df_summary = pd.DataFrame(summary_list)
    df_summary.to_csv(summary_output, index=False)
    typer.echo(f"Wrote summary by language to {summary_output}")

    # 4. Statistical Tests Helper
    def get_stats_for_df(df_sub: pd.DataFrame, subset_name: str) -> list[dict]:
        records = []
        if df_sub.empty:
            return records
        
        # 先按 (variant, tokenizer) 分组
        grouped_var_tok = df_sub.groupby(["variant", "tokenizer"])
        for (var, tok), group_vt in grouped_var_tok:
            # 运行 Kruskal-Wallis H 检验
            kruskal_groups = []
            comp_langs = group_vt["comparison_language"].unique()
            for cl in comp_langs:
                cl_ratios = group_vt[group_vt["comparison_language"] == cl]["ratio"].to_numpy()
                if len(cl_ratios) > 0:
                    kruskal_groups.append(cl_ratios)
            
            kruskal_p = 1.0
            if len(kruskal_groups) >= 2:
                try:
                    _, kruskal_p_val = stats.kruskal(*kruskal_groups)
                    kruskal_p = float(kruskal_p_val)
                except ValueError:
                    kruskal_p = 1.0
            
            # 对每个 comparison_language 计算成对 Wilcoxon 和 Cliff's delta
            vt_records = []
            grouped_lang = group_vt.groupby("comparison_language")
            for comp_lang, group in grouped_lang:
                x = group["comparison_tokens"].to_numpy()
                y = group["baseline_tokens"].to_numpy()
                ratios = group["ratio"].to_numpy()
                
                n_tasks = len(group)
                median_ratio = float(group["ratio"].median())
                mean_log_ratio = float(group["log_ratio"].mean())
                
                lower_ci, upper_ci = bootstrap_median_ci(ratios)
                p_val = run_paired_test(x, y)
                delta = cliffs_delta(x, y)
                
                vt_records.append({
                    "subset": subset_name,
                    "variant": var,
                    "tokenizer": tok,
                    "comparison_language": comp_lang,
                    "n_tasks": n_tasks,
                    "median_ratio": median_ratio,
                    "mean_log_ratio": mean_log_ratio,
                    "bootstrap_ci_lower": lower_ci,
                    "bootstrap_ci_upper": upper_ci,
                    "wilcoxon_p_value": p_val,
                    "cliffs_delta": delta,
                    "kruskal_p_value": kruskal_p,
                })
            
            # Holm-Bonferroni 修正
            valid_p_vals = []
            valid_indices = []
            for idx, r in enumerate(vt_records):
                p = r["wilcoxon_p_value"]
                if isinstance(p, float):
                    valid_p_vals.append(p)
                    valid_indices.append(idx)
            
            corrected_p_vals = []
            if len(valid_p_vals) > 0:
                corrected_p_vals = holm_bonferroni_correction(valid_p_vals)
            
            for idx, r in enumerate(vt_records):
                r["wilcoxon_p_value_corrected"] = r["wilcoxon_p_value"]
            
            for i, idx in enumerate(valid_indices):
                vt_records[idx]["wilcoxon_p_value_corrected"] = float(corrected_p_vals[i])
                
            records.extend(vt_records)
        return records

    # 针对两个数据集分而治之
    if dataset == "rosetta":
        typer.echo("Running primary statistical tests on 6-language strict intersection...")
        df_groups = pd.read_csv(equivalence_groups_path)
        strict_groups = df_groups[df_groups["has_required_intersection"]]["equivalence_group_id"].unique()
        df_paired_strict = df_paired[df_paired["equivalence_group_id"].isin(strict_groups)].copy()

        primary_records = get_stats_for_df(df_paired_strict, "six_lang_strict")
        
        typer.echo("Running statistical tests grouped by task_category on strict intersection...")
        df_paired_strict_cat = df_paired_strict.merge(
            df_groups[["equivalence_group_id", "task_category"]],
            on="equivalence_group_id",
            how="inner"
        )
        categories = df_paired_strict_cat["task_category"].dropna().unique()
        category_records = []
        for cat in categories:
            df_cat = df_paired_strict_cat[df_paired_strict_cat["task_category"] == cat].copy()
            cat_records = get_stats_for_df(df_cat, f"category_{cat}")
            category_records.extend(cat_records)

        # 写入 stat_tests.csv
        df_stat_tests = pd.DataFrame(primary_records + category_records)
        stat_tests_output.parent.mkdir(parents=True, exist_ok=True)
        df_stat_tests.to_csv(stat_tests_output, index=False)
        typer.echo(f"Wrote primary and category statistical tests to {stat_tests_output}")

        # Sensitivity Analysis
        typer.echo("Running sensitivity analyses...")
        sensitivity_records = []
        sensitivity_records.extend(primary_records)
        sensitivity_records.extend(category_records)

        # TS inclusive
        ts_groups = df_groups[
            df_groups["has_required_intersection"] & df_groups["has_optional_typescript"]
        ]["equivalence_group_id"].unique()
        df_paired_ts = df_paired[df_paired["equivalence_group_id"].isin(ts_groups)].copy()
        ts_records = get_stats_for_df(df_paired_ts, "seven_lang_inclusive")
        sensitivity_records.extend(ts_records)

        # Single implementation
        task_lang_counts = df_snippets.groupby(["equivalence_group_id", "language"])["record_id"].count().reset_index()
        max_impls_per_group = task_lang_counts.groupby("equivalence_group_id")["record_id"].max()
        single_impl_groups = max_impls_per_group[max_impls_per_group == 1].index.unique()
        single_impl_strict_groups = set(strict_groups).intersection(single_impl_groups)
        df_paired_single = df_paired[df_paired["equivalence_group_id"].isin(single_impl_strict_groups)].copy()
        single_records = get_stats_for_df(df_paired_single, "single_implementation_only")
        sensitivity_records.extend(single_records)

        df_sensitivity = pd.DataFrame(sensitivity_records)
        df_sensitivity.to_csv(sensitivity_output, index=False)
        typer.echo(f"Wrote sensitivity analysis summary to {sensitivity_output}")

    elif dataset == "leetcode":
        typer.echo("Running primary statistical tests on LeetCode C++ vs Python...")
        # 总体 C++ vs Python
        primary_records = get_stats_for_df(df_paired, "leetcode_all")
        
        # 关联难度 (task_category)
        df_paired_cat = df_paired.merge(
            df_snippets[["equivalence_group_id", "task_category"]].drop_duplicates(),
            on="equivalence_group_id",
            how="inner"
        )
        
        difficulty_records = []
        difficulties = ["Easy", "Medium", "Hard"]
        for diff in difficulties:
            df_diff = df_paired_cat[df_paired_cat["task_category"] == diff].copy()
            diff_records = get_stats_for_df(df_diff, f"difficulty_{diff}")
            difficulty_records.extend(diff_records)
            
        # 难度全局显著性检验
        kruskal_diff_records = []
        grouped_var_tok = df_paired_cat.groupby(["variant", "tokenizer"])
        for (var, tok), group_vt in grouped_var_tok:
            kruskal_groups = []
            for diff in difficulties:
                diff_ratios = group_vt[group_vt["task_category"] == diff]["ratio"].to_numpy()
                if len(diff_ratios) > 0:
                    kruskal_groups.append(diff_ratios)
            kruskal_p = 1.0
            if len(kruskal_groups) >= 2:
                try:
                    _, kruskal_p_val = stats.kruskal(*kruskal_groups)
                    kruskal_p = float(kruskal_p_val)
                except ValueError:
                    kruskal_p = 1.0
            kruskal_diff_records.append({
                "variant": var,
                "tokenizer": tok,
                "kruskal_p_value_across_difficulty": kruskal_p
            })
        df_kruskal_diff = pd.DataFrame(kruskal_diff_records)
        leetcode_kruskal_out = Path("data/results/leetcode_difficulty_kruskal_tests.csv")
        df_kruskal_diff.to_csv(leetcode_kruskal_out, index=False)
        typer.echo(f"Wrote difficulty Kruskal-Wallis tests to {leetcode_kruskal_out}")

        # 保存 stat_tests.csv
        df_stat_tests = pd.DataFrame(primary_records + difficulty_records)
        stat_tests_output.parent.mkdir(parents=True, exist_ok=True)
        df_stat_tests.to_csv(stat_tests_output, index=False)
        typer.echo(f"Wrote LeetCode statistical tests to {stat_tests_output}")

        # 敏感性分析
        df_stat_tests.to_csv(sensitivity_output, index=False)
        typer.echo(f"Wrote LeetCode sensitivity summary to {sensitivity_output}")


if __name__ == "__main__":
    app()

