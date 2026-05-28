import pytest

from cltd.tokenizers.registry import get_tokenizer


def test_empty_string_token_count():
    tokenizer = get_tokenizer("cl100k_base")
    assert tokenizer.count("") == 0


def test_idempotence():
    tokenizer = get_tokenizer("cl100k_base")
    text = "def hello(): print('hello')"
    c1 = tokenizer.count(text)
    c2 = tokenizer.count(text)
    assert c1 == c2
    assert c1 > 0


def test_unknown_tokenizer_raises_error():
    with pytest.raises(ValueError, match="Unknown tokenizer"):
        get_tokenizer("nonexistent_tokenizer")


def test_o200k_base_supported():
    tokenizer = get_tokenizer("o200k_base")
    assert tokenizer.provider == "openai"
    assert tokenizer.name == "o200k_base"
    assert tokenizer.count("hello") > 0
