from __future__ import annotations


def count_sloc(code: str) -> int:
    """统计代码的物理行数 (SLOC)，空行不计入。"""
    lines = code.split("\n")
    return sum(1 for line in lines if line.strip())
