from cltd.preprocessing.clean import clean_code
from cltd.preprocessing.normalize import normalize_raw_code
from cltd.preprocessing.sloc import count_sloc


def test_normalize_raw_code():
    raw = "def foo():  \r\n    x = 1 \r"
    expected = "def foo():\n    x = 1\n"
    assert normalize_raw_code(raw) == expected


def test_clean_python_comments():
    code = "#!/usr/bin/env python\n# This is a comment\nx = 1  # inline comment\ny = '# not a comment'\n"
    cleaned, status, warnings = clean_code(code, "python")

    assert status == "ok"
    assert "This is a comment" not in cleaned
    assert "inline comment" not in cleaned
    assert "usr/bin/env" not in cleaned
    assert "y = '# not a comment'" in cleaned


def test_clean_javascript_comments():
    code = "// single comment\nconst x = 1;\n/* multiline\ncomment */\nconst url = 'https://example.com/a//b';\n"
    cleaned, status, warnings = clean_code(code, "javascript")

    assert status == "ok"
    assert "single comment" not in cleaned
    assert "multiline" not in cleaned
    assert "const x = 1;" in cleaned
    assert "https://example.com/a//b" in cleaned


def test_clean_c_comments():
    code = "/* comment */\nint x = 1;\n// single comment\n"
    cleaned, status, warnings = clean_code(code, "c")

    assert status == "ok"
    assert "comment" not in cleaned
    assert "int x = 1;" in cleaned


def test_count_sloc():
    code = "x = 1\n\n\ny = 2\n"
    assert count_sloc(code) == 2
