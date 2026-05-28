from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path

from cltd.schemas import SnippetRecord


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def iter_leetcode_records(root: Path, language_map: dict[str, str]) -> list[SnippetRecord]:
    """
    遍历 LeetCode 仓库，解析 Markdown 索引文件，提取 Python 和 C++ 题解的代码并转为 SnippetRecord。
    """
    records: list[SnippetRecord] = []
    
    # 查找所有的 Markdown 索引文件，如 0001-1000.md, 1001-2000.md, 2001-3000.md 等
    md_files = sorted(root.glob("*.md"))
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
            
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 归一化：去掉可能的前导 '|'，然后用 '|' 切分
            parts = [p.strip() for p in line.lstrip("|").split("|")]
            if len(parts) < 6:
                continue
                
            # 第一列（索引 0）必须为纯数字（左填充至四位，例如 "0136"）
            task_id_raw = parts[0]
            if not re.match(r"^\d+$", task_id_raw):
                continue
                
            task_id = task_id_raw.zfill(4)
            
            # 第二列（索引 1）是题目：`[Single Number](https://leetcode.com/problems/single-number/)`
            title_part = parts[1]
            title_match = re.search(r"\[(.*?)\]\((.*?)\)", title_part)
            if not title_match:
                continue
            task_name = title_match.group(1)
            
            # 第六列（索引 5）是 Difficulty: "Easy", "Medium", "Hard"
            difficulty = parts[5]
            
            # 第三列（索引 2）是 Solution 链接，例如：
            # `[C++](./C++/single-number.cpp) [Python](./Python/single-number.py)`
            sol_part = parts[2]
            sol_matches = re.findall(r"\[(.*?)\]\((.*?)\)", sol_part)
            if not sol_matches:
                continue
                
            for lang_name, rel_path in sol_matches:
                lang_id = language_map.get(lang_name)
                if lang_id is None:
                    continue
                    
                # 处理相对路径并剔除前导 "./"
                clean_rel_path = rel_path.lstrip("./").replace("\\", "/")
                # 去除可能的 URL 编码（比如将 %2B 还原成 + 等字符）
                import urllib.parse
                clean_rel_path = urllib.parse.unquote(clean_rel_path)
                
                full_file_path = root / clean_rel_path
                
                if not full_file_path.exists() or not full_file_path.is_file():
                    continue
                    
                try:
                    code_raw = full_file_path.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                    
                records.append(
                    SnippetRecord(
                        record_id=f"leetcode:{task_id}:{lang_id}:0",
                        dataset="leetcode",
                        dataset_version="git_master",
                        source_uri="https://github.com/kamyu104/LeetCode-Solutions",
                        source_path=clean_rel_path,
                        task_id=task_id,
                        task_name=task_name,
                        task_category=difficulty,
                        language=lang_id,
                        implementation_index=0,
                        equivalence_group_id=f"leetcode:{task_id}",
                        equivalence_confidence="source_aligned",
                        license="MIT",
                        code_raw=code_raw,
                        code_raw_sha256=sha256_text(code_raw),
                        ingested_at=datetime.now(UTC),
                    )
                )
                
    return records
