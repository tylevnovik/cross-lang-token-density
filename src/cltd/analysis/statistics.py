from __future__ import annotations

import numpy as np
import scipy.stats as stats


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    """计算 Cliff's delta 效应量，评估两组独立样本的差异程度。"""
    n1 = len(x)
    n2 = len(y)
    if n1 == 0 or n2 == 0:
        return 0.0
    # 利用 numpy 广播机制快速计算所有成对的符号
    diffs = x[:, None] - y[None, :]
    signs = np.sign(diffs)
    return float(np.sum(signs) / (n1 * n2))


def bootstrap_median_ci(
    ratios: np.ndarray, n_bootstrap: int = 1000, ci_level: float = 0.95, seed: int = 42
) -> tuple[float, float]:
    """使用自助法 (Bootstrap) 计算中位数比例的 95% 置信区间。"""
    n = len(ratios)
    if n < 10:
        return (np.nan, np.nan)
    
    rng = np.random.default_rng(seed)
    boot_medians = []
    for _ in range(n_bootstrap):
        sample = rng.choice(ratios, size=n, replace=True)
        boot_medians.append(np.median(sample))
        
    lower_pct = (1.0 - ci_level) / 2.0
    upper_pct = 1.0 - lower_pct
    
    lower = np.percentile(boot_medians, lower_pct * 100)
    upper = np.percentile(boot_medians, upper_pct * 100)
    return float(lower), float(upper)


def run_paired_test(
    x: np.ndarray, y: np.ndarray
) -> str | float:
    """运行 Wilcoxon 符号秩检验，返回 p 值。如果样本少于 20，返回 'insufficient_sample'。"""
    if len(x) < 20:
        return "insufficient_sample"
    
    # Wilcoxon 检验在所有差值为 0 时会报错，需要防御性处理
    if np.all(x == y):
        return 1.0
        
    try:
        _, p_val = stats.wilcoxon(x, y)
        return float(p_val)
    except ValueError:
        # 如果样本差值全为 0 等异常情况导致无法检验
        return 1.0


def holm_bonferroni_correction(p_values: list[float] | np.ndarray) -> np.ndarray:
    """
    对 p 值应用 Holm-Bonferroni 修正，以控制族错误率 (FWER)。
    """
    p_vals = np.asarray(p_values, dtype=float)
    n = len(p_vals)
    if n == 0:
        return np.array([])
    
    # 记录原始索引并排序
    sorted_indices = np.argsort(p_vals)
    sorted_p = p_vals[sorted_indices]
    
    adjusted_p = np.zeros(n)
    
    # Holm-Bonferroni 递推公式：
    # p_adj = min(1.0, max(p_adj[i-1], p_sorted[i] * (n - i)))
    for i in range(n):
        raw_adj = sorted_p[i] * (n - i)
        if i == 0:
            adjusted_p[i] = min(1.0, raw_adj)
        else:
            adjusted_p[i] = min(1.0, max(adjusted_p[i-1], raw_adj))
            
    # 还原到原始顺序
    final_p = np.zeros(n)
    final_p[sorted_indices] = adjusted_p
    return final_p

