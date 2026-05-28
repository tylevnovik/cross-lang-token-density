from __future__ import annotations

import importlib.metadata
import tiktoken

from cltd.tokenizers.registry import CodeTokenizer, register_tokenizer


class TiktokenTokenizer(CodeTokenizer):
    """基于 OpenAI tiktoken 的分词器实现。"""

    def __init__(self, encoding_name: str):
        self._name = encoding_name
        self._encoder = tiktoken.get_encoding(encoding_name)
        try:
            self._version = importlib.metadata.version("tiktoken")
        except importlib.metadata.PackageNotFoundError:
            self._version = "0.7.0"

    @property
    def provider(self) -> str:
        return "openai"

    @property
    def name(self) -> str:
        return self._name

    @property
    def package(self) -> str:
        return "tiktoken"

    @property
    def package_version(self) -> str:
        return self._version

    def count(self, text: str) -> int:
        # tiktoken encode 返回 token ids 列表，长度即为 token 数
        return len(self._encoder.encode(text))


# 自动注册支持的分词器
register_tokenizer("cl100k_base", TiktokenTokenizer("cl100k_base"))
register_tokenizer("o200k_base", TiktokenTokenizer("o200k_base"))
