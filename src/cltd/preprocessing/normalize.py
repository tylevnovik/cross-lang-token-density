from __future__ import annotations


def normalize_raw_code(code: str) -> str:
    """统一换行符为 \\n，并逐行去除尾随空白，但保留行首的缩进。"""
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in code.split("\n")]
    return "\n".join(lines)
