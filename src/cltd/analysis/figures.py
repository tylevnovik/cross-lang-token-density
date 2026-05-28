from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 设置全局样式，使其具有现代感和视觉美感
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 16,
    "font.family": "sans-serif",
})


def plot_paired_ratios_boxplot(df_paired: pd.DataFrame, output_path: Path) -> None:
    """绘制不同编程语言相对于 Python 的 Token 数量比例箱线图 (Clean 变体, cl100k_base 分词器)。"""
    plt.figure(figsize=(10, 6))
    
    # 筛选主分析配置
    df_plot = df_paired[
        (df_paired["variant"] == "clean") & (df_paired["tokenizer"] == "cl100k_base")
    ].copy()
    
    # 排序：按中位数比例从低到高排列
    order = df_plot.groupby("comparison_language")["ratio"].median().sort_values().index

    ax = sns.boxplot(
        data=df_plot,
        x="comparison_language",
        y="ratio",
        order=order,
        palette="viridis",
        showfliers=False,  # 隐藏异常值以提高可读性
        width=0.6,
    )
    
    # 绘制比例为 1.0 的基准线 (Python)
    ax.axhline(1.0, color="red", linestyle="--", linewidth=1.5, label="Python (Baseline = 1.0)")
    
    ax.set_title("Token Count Ratio to Python by Language (Clean & cl100k_base)")
    ax.set_xlabel("Comparison Language")
    ax.set_ylabel("Token Ratio (Comparison / Python)")
    ax.legend()
    
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_ratio_heatmap(df_stats: pd.DataFrame, output_path: Path) -> None:
    """绘制不同分词器与语言的中位数比例热力图 (Clean 变体)。"""
    # 筛选 clean 变体的主分析子集
    df_clean = df_stats[
        (df_stats["subset"] == "six_lang_strict") & (df_stats["variant"] == "clean")
    ].copy()
    
    # 透视表：行是语言，列是分词器，值是中位数比例
    df_pivot = df_clean.pivot(
        index="comparison_language", columns="tokenizer", values="median_ratio"
    )
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        df_pivot,
        annot=True,
        fmt=".2f",
        cmap="YlGnBu",
        cbar_kws={"label": "Median Token Ratio"},
        linewidths=0.5,
        annot_kws={"size": 12},
    )
    
    plt.title("Median Token Ratio to Python by Tokenizer (Clean)")
    plt.xlabel("Tokenizer")
    plt.ylabel("Language")
    
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_raw_clean_delta(df_summary: pd.DataFrame, output_path: Path) -> None:
    """绘制 Raw vs Clean 变体对各语言 Token 密度的影响图。"""
    # 筛选 cl100k_base 分词器
    df_sub = df_summary[df_summary["tokenizer"] == "cl100k_base"].copy()
    
    # 转换为透视表
    df_pivot = df_sub.pivot(index="language", columns="variant", values="median_tokens")
    
    # 计算 Raw 与 Clean 的差值比例 (Raw / Clean)
    df_pivot["raw_to_clean_ratio"] = df_pivot["raw"] / df_pivot["clean"]
    df_pivot = df_pivot.sort_values("raw_to_clean_ratio", ascending=False)
    
    plt.figure(figsize=(9, 5))
    ax = sns.barplot(
        x=df_pivot.index,
        y=df_pivot["raw_to_clean_ratio"],
        palette="magma",
        hue=df_pivot.index,
        legend=False,
    )
    
    ax.axhline(1.0, color="gray", linestyle="-", linewidth=1)
    
    ax.set_title("Comment & Blank Line Token Overhead by Language (Raw / Clean Median)")
    ax.set_xlabel("Language")
    ax.set_ylabel("Overhead Ratio (Raw Tokens / Clean Tokens)")
    ax.set_ylim(0.9, df_pivot["raw_to_clean_ratio"].max() + 0.1)
    
    # 在条形图上方标注具体数值
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(
            f"{height:.2f}x",
            (p.get_x() + p.get_width() / 2.0, height),
            ha="center",
            va="bottom",
            fontsize=10,
            xytext=(0, 3),
            textcoords="offset points",
        )
        
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_task_size_effects(df_paired: pd.DataFrame, output_path: Path) -> None:
    """绘制任务规模（基准 Python 语言的 Token 数量）对 Token 比例的影响散点图。"""
    plt.figure(figsize=(10, 6))
    
    # 筛选 clean 变体和 cl100k_base 分词器
    df_plot = df_paired[
        (df_paired["variant"] == "clean")
        & (df_paired["tokenizer"] == "cl100k_base")
        & (df_paired["comparison_language"] != "typescript")  # 排除 TS 以保持主语言对比清晰
    ].copy()
    
    # 限制 Python token 数量在 1000 以内以便观察主要分布
    df_plot = df_plot[df_plot["baseline_tokens"] <= 1000]
    
    sns.scatterplot(
        data=df_plot,
        x="baseline_tokens",
        y="ratio",
        hue="comparison_language",
        alpha=0.6,
        edgecolor=None,
        palette="Set1",
    )
    
    plt.axhline(1.0, color="black", linestyle="--", linewidth=1.5)
    
    plt.title("Token Ratio Stability across Task Sizes (Python Clean Tokens <= 1000)")
    plt.xlabel("Python (Baseline) Token Count")
    plt.ylabel("Token Ratio (Comparison / Python)")
    plt.legend(title="Language")
    
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_task_category_effects(df_stats: pd.DataFrame, output_path: Path) -> None:
    """绘制不同任务类别下各编程语言相对于 Python 的 Token 比例对比柱状图 (Clean, cl100k_base)。"""
    # 筛选子集：subset 为 category_ 开头，变体为 clean，分词器为 cl100k_base
    df_cat = df_stats[
        df_stats["subset"].str.startswith("category_") 
        & (df_stats["variant"] == "clean") 
        & (df_stats["tokenizer"] == "cl100k_base")
    ].copy()
    
    if df_cat.empty:
        return
        
    # 从 subset 提取出真正的分类名称
    df_cat["category"] = df_cat["subset"].apply(lambda s: s.replace("category_", ""))
    
    plt.figure(figsize=(10, 6))
    
    # 绘制分组柱状图
    ax = sns.barplot(
        data=df_cat,
        x="category",
        y="median_ratio",
        hue="comparison_language",
        palette="Set2"
    )
    
    # 绘制基准线 (Python = 1.0)
    ax.axhline(1.0, color="red", linestyle="--", linewidth=1.5, label="Python (Baseline = 1.0)")
    
    ax.set_title("Median Token Ratio to Python by Task Category (Clean & cl100k_base)")
    ax.set_xlabel("Task Category")
    ax.set_ylabel("Median Token Ratio")
    ax.legend(title="Language")
    
    # 在柱子上方添加数值标注
    for p in ax.patches:
        height = p.get_height()
        if pd.isna(height) or height == 0:
            continue
        ax.annotate(
            f"{height:.2f}",
            (p.get_x() + p.get_width() / 2., height),
            ha='center', va='bottom',
            fontsize=8, xytext=(0, 2),
            textcoords='offset points'
        )
        
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_char_to_token_ratio(df_summary: pd.DataFrame, output_path: Path) -> None:
    """绘制各编程语言的字符-Token比 (Char-to-Token Ratio) 与行-Token比柱状图，评估分词碎片化 (Clean, cl100k_base)。"""
    # 筛选 clean 变体和 cl100k_base 分词器
    df_plot = df_summary[
        (df_summary["variant"] == "clean") & (df_summary["tokenizer"] == "cl100k_base")
    ].copy()
    
    if df_plot.empty:
        return
        
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 按 Char-to-Token Ratio 从小到大排序
    df_plot_sorted1 = df_plot.sort_values("median_char_to_token_ratio", ascending=True)
    sns.barplot(
        data=df_plot_sorted1,
        x="language",
        y="median_char_to_token_ratio",
        palette="viridis",
        hue="language",
        legend=False,
        ax=ax1
    )
    ax1.set_title("Character-to-Token Ratio (Higher = More Compressed)")
    ax1.set_xlabel("Language")
    ax1.set_ylabel("Median Characters per Token")
    
    for p in ax1.patches:
        height = p.get_height()
        if pd.isna(height) or height == 0:
            continue
        ax1.annotate(
            f"{height:.2f}",
            (p.get_x() + p.get_width() / 2., height),
            ha='center', va='bottom',
            fontsize=9, xytext=(0, 2),
            textcoords='offset points'
        )
        
    # 按 Tokens-per-Line 从小到大排序
    df_plot_sorted2 = df_plot.sort_values("median_tokens_per_line", ascending=True)
    sns.barplot(
        data=df_plot_sorted2,
        x="language",
        y="median_tokens_per_line",
        palette="mako",
        hue="language",
        legend=False,
        ax=ax2
    )
    ax2.set_title("Tokens per Line (Tokens / SLOC)")
    ax2.set_xlabel("Language")
    ax2.set_ylabel("Median Tokens per Line")
    
    for p in ax2.patches:
        height = p.get_height()
        if pd.isna(height) or height == 0:
            continue
        ax2.annotate(
            f"{height:.2f}",
            (p.get_x() + p.get_width() / 2., height),
            ha='center', va='bottom',
            fontsize=9, xytext=(0, 2),
            textcoords='offset points'
        )
        
    plt.suptitle("Tokenizer Fragmentation & Density Metrics (Clean & cl100k_base)", y=0.98)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_leetcode_paired_boxplot(df_paired: pd.DataFrame, df_snippets: pd.DataFrame, output_path: Path) -> None:
    """绘制 LeetCode 场景下 C++ 相对于 Python 的 Token 数量比例箱线图（按 Easy/Medium/Hard 难度分组）。"""
    # 筛选 clean 变体和 cl100k_base 分词器
    df_plot = df_paired[
        (df_paired["variant"] == "clean") & (df_paired["tokenizer"] == "cl100k_base")
    ].copy()
    
    if df_plot.empty:
        return
        
    # 关联难度信息
    df_plot_cat = df_plot.merge(
        df_snippets[["equivalence_group_id", "task_category"]].drop_duplicates(),
        on="equivalence_group_id",
        how="inner"
    )
    
    # 过滤可能异常值
    df_plot_cat = df_plot_cat[df_plot_cat["ratio"] <= 3.0]
    
    # 强制排难度的顺序
    order = ["Easy", "Medium", "Hard"]
    
    plt.figure(figsize=(8, 6))
    
    ax = sns.boxplot(
        data=df_plot_cat,
        x="task_category",
        y="ratio",
        order=order,
        palette="coolwarm",
        showfliers=False,  # 隐藏异常值以保持箱线图清晰美观
        width=0.4,
    )
    
    # 绘制基准线 (Python = 1.0)
    ax.axhline(1.0, color="red", linestyle="--", linewidth=1.5, label="Python (Baseline = 1.0)")
    
    # 在箱体上方标注中位数数值
    grouped = df_plot_cat.groupby("task_category")["ratio"].median()
    for i, cat in enumerate(order):
        if cat in grouped:
            median_val = grouped[cat]
            ax.text(
                i, median_val + 0.03, f"{median_val:.2f}x",
                ha="center", va="bottom", color="black", fontweight="bold", fontsize=10
            )
            
    ax.set_title("LeetCode C++ to Python Token Ratio by Difficulty (Clean & cl100k_base)")
    ax.set_xlabel("Problem Difficulty")
    ax.set_ylabel("Token Count Ratio (C++ / Python)")
    ax.set_ylim(0.5, 2.2)
    ax.legend()
    
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


