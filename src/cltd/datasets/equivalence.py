from __future__ import annotations

from collections import defaultdict

from cltd.schemas import SnippetRecord


def build_coverage(records: list[SnippetRecord]) -> dict[str, set[str]]:
    coverage: dict[str, set[str]] = defaultdict(set)
    for record in records:
        coverage[record.equivalence_group_id].add(record.language)
    return dict(coverage)


def strict_intersection_groups(
    records: list[SnippetRecord], required_languages: set[str]
) -> set[str]:
    coverage = build_coverage(records)
    return {
        group_id
        for group_id, languages in coverage.items()
        if required_languages.issubset(languages)
    }


def classify_task_category(task_name: str) -> str:
    """根据任务名称关键词对 Rosetta Code 任务进行归类。"""
    name_lower = task_name.lower()

    # 1. 数学与数值计算 (Math/Numeric)
    math_keywords = [
        "math", "prime", "fibonacci", "number", "sum", "factorial", "gcd", "lcm",
        "equation", "root", "geometry", "calc", "matrix", "vector", "stat", "probability",
        "random", "arithmetic", "fraction", "logarithm", "trigonometry", "power", "divisors"
    ]
    if any(kw in name_lower for kw in math_keywords):
        return "Math/Numeric"

    # 2. 算法与数据结构 (Algorithms/DS)
    algo_keywords = [
        "sort", "search", "algorithm", "recursive", "permute", "graph", "path", "maze",
        "tree", "list", "stack", "queue", "map", "set", "hash", "binary", "node",
        "sequence", "filter", "combinator", "backtrack", "traverse"
    ]
    if any(kw in name_lower for kw in algo_keywords):
        return "Algorithms/DS"

    # 3. 文本与字符串处理 (Text/String)
    text_keywords = [
        "string", "text", "regex", "char", "word", "parse", "format", "anagram",
        "cipher", "crypt", "print", "display", "output", "input", "match", "replace",
        "xml", "json", "yaml", "csv", "html", "substring"
    ]
    if any(kw in name_lower for kw in text_keywords):
        return "Text/String"

    # 4. 系统与文件I/O (System/IO)
    sys_keywords = [
        "system", "file", "directory", "time", "date", "network", "socket", "http",
        "process", "thread", "env", "shell", "exec", "write", "read", "load", "save",
        "command", "argument", "db", "database", "memory", "alloc"
    ]
    if any(kw in name_lower for kw in sys_keywords):
        return "System/IO"

    return "General/Other"

