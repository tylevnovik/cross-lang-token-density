from __future__ import annotations

import numpy as np
import pandas as pd


def build_paired_ratios(
    df_snippets: pd.DataFrame,
    df_variants: pd.DataFrame,
    df_counts: pd.DataFrame,
    baseline_lang: str = "python",
) -> pd.DataFrame:
    """构造成对分析数据表，计算对比语言与基准语言 (Python) 的 token 比例及对数比例。"""
    # 1. 合并 token 计数与变体信息
    df_tokens = df_counts.merge(
        df_variants[["variant_id", "record_id", "variant"]],
        on="variant_id",
        how="inner",
    )

    # 2. 合并片段原始信息（语言，任务ID，等价组，实现索引）
    df_full = df_tokens.merge(
        df_snippets[["record_id", "language", "task_id", "equivalence_group_id", "implementation_index"]],
        on="record_id",
        how="inner",
    )

    # 3. 提取基准语言 (baseline) 和对比语言 (comparison)
    df_base = df_full[df_full["language"] == baseline_lang].copy()
    df_comp = df_full[df_full["language"] != baseline_lang].copy()

    # 4. 按等价组、变体、分词器、实现索引进行内联结
    df_paired = df_base.merge(
        df_comp,
        on=["equivalence_group_id", "variant", "tokenizer_name", "implementation_index"],
        suffixes=("_baseline", "_comparison"),
    )

    # 5. 计算比例与对数比例 (处理 0 的极端情况)
    # 避免除以 0
    df_paired = df_paired[
        (df_paired["token_count_baseline"] > 0) & (df_paired["token_count_comparison"] > 0)
    ].copy()
    
    df_paired["ratio"] = (
        df_paired["token_count_comparison"] / df_paired["token_count_baseline"]
    )
    df_paired["log_ratio"] = np.log(df_paired["ratio"])

    # 6. 整理输出列
    df_result = df_paired[
        [
            "equivalence_group_id",
            "task_id_baseline",
            "variant",
            "tokenizer_name",
            "language_baseline",
            "language_comparison",
            "token_count_baseline",
            "token_count_comparison",
            "ratio",
            "log_ratio",
        ]
    ].copy()

    df_result.rename(
        columns={
            "task_id_baseline": "task_id",
            "tokenizer_name": "tokenizer",
            "language_baseline": "baseline_language",
            "language_comparison": "comparison_language",
            "token_count_baseline": "baseline_tokens",
            "token_count_comparison": "comparison_tokens",
        },
        inplace=True,
    )

    return df_result
