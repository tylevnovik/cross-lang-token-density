# Cross-Language Source Code Token Density Analysis

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

This repository contains a reproducible research pipeline designed to measure and analyze source code token density across seven major programming languages: **C, Go, Java, JavaScript, Python, Rust, and TypeScript**. 

By evaluating how many tokens are required to implement identical functionality, we construct an empirical token-efficiency hierarchy. This is of critical importance in the LLM/Coding-Agent era, where token density directly impacts operational costs and context window utilization.

---

## Key Findings (Abstract)

Using a strict paired intersection of **693 functional tasks** from Rosetta Code:
1. **Language Hierarchy**: Dynamically typed scripting languages are highly token-efficient. Taking Python as the baseline (1.00), the median paired token count ratios for clean code are:
   $$\text{C (1.77)} > \text{Rust (1.57)} > \text{Go (1.55)} > \text{Java (1.47)} > \text{TypeScript (1.45)} > \text{JavaScript (1.26)}$$
2. **Type Safety Premium**: Adding explicit type definitions in TypeScript incurs a **~15% token premium** over pure JavaScript.
3. **Comment Overhead**: Comment-stripping yields token savings of up to **21% in C** and **16% in JavaScript** without changing syntax structure.
4. **Tokenizer Invariance**: These ratios remain robustly stable across tokenizer iterations (`cl100k_base` vs. `o200k_base`).

---

## Project Structure

```text
cross-lang-token-density/
├── README.md
├── pyproject.toml
├── Makefile
├── configs/               # Configuration files for languages, tokenizers, preprocessing
├── data/
│   ├── raw/               # Pinned raw datasets (Rosetta Code mirrored)
│   ├── interim/           # Temporary JSONL files
│   ├── processed/         # Code variants & Token count Parquet databases
│   └── results/           # CSV statistical tables and test outputs
├── docs/                  # Methodology, release checklists, data dictionary
├── paper/                 # English paper drafts (main.md & references.bib)
├── report/                # Chinese technical reports and generated figures
├── scripts/               # CLI execution scripts
├── src/cltd/              # Project core library
└── tests/                 # Full unit testing suite
```

---

## Getting Started

### 1. Installation

This project requires **Python 3.12+** and [**uv**](https://github.com/astral-sh/uv). Install dependencies and build the package in editable mode:

```bash
uv sync
```

### 2. Reproduction

Execute the full pipeline end-to-end to replicate data ingestion, cleaning, tokenization, analysis, and plotting:

```bash
# Using Makefile
make reproduce

# Or using raw CLI steps
uv run python scripts/fetch_rosettacode.py
uv run python scripts/preprocess.py
uv run python scripts/tokenize_data.py
uv run python scripts/analyze.py
uv run python scripts/make_figures.py
```

### 3. Running Tests

Run the full suite of unit tests to verify logic correctness:

```bash
uv run pytest -v
```

---

## Documents & Reports

- **Methodology**: [docs/methodology.md](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/docs/methodology.md)
- **Data Dictionary**: [docs/data-dictionary.md](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/docs/data-dictionary.md)
- **Technical Report (CN)**: [report/report_zh.md](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/report/report_zh.md)
- **Academic Paper Draft (EN)**: [paper/main.md](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/paper/main.md)

---

## License

This repository is licensed under the MIT License - see the `LICENSE` file for details. Raw data in `data/raw/` remains subject to the licenses of its respective upstream repositories.
