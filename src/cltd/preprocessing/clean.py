from __future__ import annotations

import pygments
from pygments.lexers import get_lexer_by_name, ClassNotFound
from pygments.token import Token
from cltd.preprocessing.normalize import normalize_raw_code


def clean_code(code: str, language: str) -> tuple[str, str, list[str]]:
    """去除 Shebang、注释以及纯空行，仅保留有效的代码结构。"""
    warnings = []
    status = "ok"

    # 1. 统一换行符
    code = normalize_raw_code(code)

    # 2. 移除 Shebang
    if code.startswith("#!"):
        lines = code.split("\n", 1)
        code = lines[1] if len(lines) > 1 else ""

    # 3. 获取 pygments Lexer
    try:
        pyg_name = language
        if language == "javascript":
            pyg_name = "js"
        elif language == "typescript":
            pyg_name = "ts"
        lexer = get_lexer_by_name(pyg_name)
    except ClassNotFound:
        from pygments.lexers.special import TextLexer
        lexer = TextLexer()
        status = "warning"
        warnings.append(f"lexer fallback to TextLexer for language: {language}")

    # 4. Tokenize 过滤注释
    tokens = pygments.lex(code, lexer)
    clean_parts = []
    for ttype, value in tokens:
        # 跳过所有 Token.Comment 类型的 token
        if ttype in Token.Comment:
            continue
        clean_parts.append(value)

    reconstructed = "".join(clean_parts)

    # 5. 过滤空白行，保留带有有效字符的行
    lines = reconstructed.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.rstrip()
        # 仅保留非空行
        if stripped.strip():
            cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines), status, warnings
