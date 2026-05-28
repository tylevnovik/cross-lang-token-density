# Cross-Language Source Code Token Density Analysis

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

[简体中文](./README_zh.md) | English


This repository contains a reproducible research pipeline designed to measure and analyze source code token density across eight major programming languages: **C, C++, Go, Java, JavaScript, Python, Rust, and TypeScript**. 

By evaluating how many tokens are required to implement identical functionality, we construct an empirical token-efficiency hierarchy. This is of critical importance in the LLM/Coding-Agent era, where token density directly impacts operational costs and context window utilization.

---

## Key Findings (Abstract)

1. **Rosetta Code Benchmark (Phase 1)**: Using a strict paired intersection of **693 functional tasks**:
   - **Language Hierarchy**: Dynamically typed scripting languages are highly token-efficient. Taking Python as the baseline (1.00), the median paired token count ratios for clean code are:
     $$\text{C (1.77)} > \text{Rust (1.57)} > \text{Go (1.55)} > \text{Java (1.47)} > \text{TypeScript (1.45)} > \text{JavaScript (1.26)}$$
   - **Type Safety Premium**: Adding explicit type definitions in TypeScript incurs a **~15% token premium** over pure JavaScript.
   - **Comment Overhead**: Comment-stripping yields token savings of up to **21% in C** and **16% in JavaScript** without changing syntax structure.
2. **LeetCode Generalization (Phase 2)**: Using **3,681 paired tasks** from `kamyu104/LeetCode-Solutions`:
   - **Overall Overhead**: C++ requires **1.20x** more tokens than Python, showing substantial efficiency improvements over C (1.77x) due to STL and container abstractions.
   - **Difficulty Escalation Effect**: C++ relative token overhead grows monotonically as task complexity increases: **Easy (1.11x) $\rightarrow$ Medium (1.19x) $\rightarrow$ Hard (1.28x)**. Global Kruskal-Wallis H test is extremely significant ($p = 1.53 \times 10^{-42}$), demonstrating that logic complexity scales relative structural boilerplate.
3. **Tokenizer Invariance**: These ratios remain robustly stable across tokenizer iterations (`cl100k_base` vs. `o200k_base`).

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

Execute the full pipeline end-to-end to replicate data ingestion, cleaning, tokenization, analysis, and plotting.

#### Rosetta Code Pipeline (Phase 1)
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

#### LeetCode Pipeline (Phase 2)
```bash
# Using Makefile
make reproduce-leetcode

# Or using raw CLI steps
uv run python scripts/fetch_leetcode.py
uv run python scripts/preprocess.py --snippets-path data/interim/leetcode_snippets.jsonl --variants-output data/processed/leetcode_variants.parquet --warnings-output data/results/leetcode_preprocess_warnings.csv
uv run python scripts/tokenize_data.py --variants-path data/processed/leetcode_variants.parquet --token-counts-output data/processed/leetcode_token_counts.parquet --summary-output data/results/leetcode_tokenizer_summary.csv
uv run python scripts/analyze.py --dataset leetcode
uv run python scripts/make_figures.py --dataset leetcode
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

