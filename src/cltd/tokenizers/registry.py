from __future__ import annotations

import abc


class CodeTokenizer(abc.ABC):
    """分词器基类接口，所有具体分词器需继承此接口。"""

    @property
    @abc.abstractmethod
    def provider(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def package(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def package_version(self) -> str:
        pass

    @abc.abstractmethod
    def count(self, text: str) -> int:
        """输入文本，返回分词后的 token 数量。"""
        pass


_REGISTRY: dict[str, CodeTokenizer] = {}


def register_tokenizer(name: str, tokenizer: CodeTokenizer) -> None:
    _REGISTRY[name] = tokenizer


def get_tokenizer(name: str) -> CodeTokenizer:
    if name not in _REGISTRY:
        raise ValueError(f"Unknown tokenizer: {name}")
    return _REGISTRY[name]


def list_registered_tokenizers() -> list[str]:
    return list(_REGISTRY.keys())
