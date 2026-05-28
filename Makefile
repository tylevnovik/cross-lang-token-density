.PHONY: test lint fetch-rosetta preprocess tokenize analyze figures report reproduce fetch-leetcode preprocess-leetcode tokenize-leetcode analyze-leetcode figures-leetcode reproduce-leetcode

test:
	uv run pytest -q

lint:
	uv run ruff check src scripts tests

fetch-rosetta:
	uv run python scripts/fetch_rosettacode.py

preprocess:
	uv run python scripts/preprocess.py

tokenize:
	uv run python scripts/tokenize_data.py

analyze:
	uv run python scripts/analyze.py

figures:
	uv run python scripts/make_figures.py

report:
	uv run python scripts/analyze.py
	uv run python scripts/make_figures.py
	uv run python scripts/analyze.py --dataset leetcode
	uv run python scripts/make_figures.py --dataset leetcode

reproduce: fetch-rosetta preprocess tokenize analyze figures

fetch-leetcode:
	uv run python scripts/fetch_leetcode.py

preprocess-leetcode:
	uv run python scripts/preprocess.py --snippets-path data/interim/leetcode_snippets.jsonl --variants-output data/processed/leetcode_variants.parquet --warnings-output data/results/leetcode_preprocess_warnings.csv

tokenize-leetcode:
	uv run python scripts/tokenize_data.py --variants-path data/processed/leetcode_variants.parquet --token-counts-output data/processed/leetcode_token_counts.parquet --summary-output data/results/leetcode_tokenizer_summary.csv

analyze-leetcode:
	uv run python scripts/analyze.py --dataset leetcode

figures-leetcode:
	uv run python scripts/make_figures.py --dataset leetcode

reproduce-leetcode: fetch-leetcode preprocess-leetcode tokenize-leetcode analyze-leetcode figures-leetcode

