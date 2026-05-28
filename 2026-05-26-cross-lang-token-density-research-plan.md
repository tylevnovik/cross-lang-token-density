# 跨语言 Token 密度研究 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` task-by-task 执行本计划。所有步骤使用 checkbox 追踪，所有 agent 参与必须写入研究日志。

**Goal:** 建立一个可复现的数据采集、清洗、token 统计、统计分析与论文写作流水线，用于研究同一功能在不同编程语言中的源代码 token 效率差异，并系统记录 coding agent 参与科研项目的过程。

**Architecture:** 项目采用“数据源适配器 -> 规范化记录 -> 预处理变体 -> tokenizer registry -> 成对统计分析 -> 报告/论文产物”的流水线。agent 不是只做辅助编码，而是作为研究流程中的可审计执行者，每次数据采集、清洗、判断、失败和人工介入都记录到机器可读日志与人工可读反思日志中。

**Tech Stack:** Python 3.12, `uv`, PowerShell-compatible CLI commands, optional `Makefile` aliases, `pytest`, `ruff`, `mypy`, `pandas`, `polars` 或 `duckdb`, `tiktoken`, `pygments`, `scipy`, `statsmodels`, `seaborn`, `matplotlib`, `plotly`, `pydantic`, `typer`, `rich`, JSONL/CSV/Parquet。

---

## 0. 研究范围与版本边界

### 0.1 第一版研究问题

- RQ1：在同一任务、同一 tokenizer 下，不同编程语言的源代码 token 数有多大差异？
- RQ2：这种差异在 raw code、clean code、canonical formatted code 三种代码变体中是否稳定？
- RQ3：不同 tokenizer 对不同语言的 tokenization 是否存在系统性偏好？
- RQ4：在 coding agent 深度参与数据采集、清洗和分析时，如何记录过程，使研究可复现、可审计、可写入论文方法论？

### 0.2 第一版假设

- H1：动态语言 Python / JavaScript 的中位 token count 低于 Java / Go / Rust，但差异大小依赖任务类型。
- H2：TypeScript 与 JavaScript 应分开统计；类型标注会带来可观但不一定压倒性的 token 成本。
- H3：raw code 与 clean code 的语言排序可能不同，说明注释文化和示例风格会影响 token 成本。
- H4：tokenizer 差异不会改变全部结论，但会影响部分语言之间的相对倍率。

### 0.3 第一版语言集合

默认核心集合：

- Python
- JavaScript
- TypeScript
- Java
- Go
- Rust
- C

如果 Rosetta Code 中 TypeScript 覆盖不足，则 Phase 1 报告保留 TypeScript 的描述性统计，不把它纳入“七语言严格交集”；同时输出“六语言严格交集”作为主统计口径。

### 0.4 第一版数据源边界

- Phase 1 必做：Rosetta Code GitHub mirror。
- Phase 2 选做但计划内：开源 LeetCode 题解仓库。
- Phase 3 选做但计划内：GitHub 功能配对项目。

第一篇可投稿短论文或 arXiv v1 以 Phase 1 为主，Phase 2/3 作为扩展实验或后续版本，不阻塞第一版产出。

---

## 1. 目标产物

- 开源研究仓库：`cross-lang-token-density/`
- 可复现实验命令：以 PowerShell 下的 `uv run python scripts/...` 直接命令为准；`make reproduce` 作为安装了 `make` 时的快捷别名。
- 公开数据集：
  - `data/processed/snippets.parquet`
  - `data/processed/token_counts.parquet`
  - `data/processed/equivalence_groups.csv`
  - `data/processed/agent_research_runs.jsonl`
- 统计结果：
  - `data/results/summary_by_language.csv`
  - `data/results/paired_language_ratios.csv`
  - `data/results/tokenizer_language_matrix.csv`
  - `data/results/stat_tests.csv`
- 图表：
  - `report/figures/boxplot_token_count_by_language.png`
  - `report/figures/ratio_heatmap_by_tokenizer.png`
  - `report/figures/raw_clean_delta_by_language.png`
  - `report/figures/task_category_effects.png`
- 中文技术报告：`report/report_zh.md`
- 英文论文草稿：`paper/main.tex` 或 `paper/main.md`
- agent 自省材料：
  - `research_log/runs/*.jsonl`
  - `research_log/reflections/*.md`
  - `docs/decision-log.md`

---

## 2. 项目文件结构

在未来研究仓库 `cross-lang-token-density/` 中创建以下结构：

```text
cross-lang-token-density/
├── README.md
├── pyproject.toml
├── Makefile
├── .gitignore
├── configs/
│   ├── languages.yaml
│   ├── tokenizers.yaml
│   ├── datasets.yaml
│   └── preprocessing.yaml
├── data/
│   ├── raw/
│   │   ├── rosettacode/
│   │   ├── leetcode/
│   │   └── github_projects/
│   ├── interim/
│   ├── processed/
│   └── results/
├── docs/
│   ├── methodology.md
│   ├── equivalence-criteria.md
│   ├── data-dictionary.md
│   └── decision-log.md
├── prompts/
│   ├── data_collection_agent.md
│   ├── equivalence_review_agent.md
│   ├── analysis_agent.md
│   └── reflection_template.md
├── research_log/
│   ├── runs/
│   └── reflections/
├── report/
│   ├── report_zh.md
│   └── figures/
├── paper/
│   ├── main.md
│   └── references.bib
├── scripts/
│   ├── fetch_rosettacode.py
│   ├── fetch_leetcode.py
│   ├── fetch_github_candidates.py
│   ├── preprocess.py
│   ├── tokenize.py
│   ├── analyze.py
│   ├── make_figures.py
│   └── log_reflection.py
├── src/
│   └── cltd/
│       ├── __init__.py
│       ├── schemas.py
│       ├── paths.py
│       ├── datasets/
│       │   ├── rosettacode.py
│       │   ├── leetcode.py
│       │   └── github_projects.py
│       ├── preprocessing/
│       │   ├── normalize.py
│       │   ├── clean.py
│       │   └── sloc.py
│       ├── tokenizers/
│       │   ├── registry.py
│       │   ├── openai_tiktoken.py
│       │   └── provider_api.py
│       ├── analysis/
│       │   ├── paired.py
│       │   ├── statistics.py
│       │   └── figures.py
│       └── agent_logging/
│           ├── run_log.py
│           └── reflection.py
└── tests/
    ├── fixtures/
    ├── test_schemas.py
    ├── test_rosettacode_ingest.py
    ├── test_preprocess.py
    ├── test_tokenize.py
    ├── test_statistics.py
    └── test_agent_logging.py
```

---

## 3. 核心数据合同

### 3.1 Snippet 记录

每个代码片段必须包含这些字段：

```json
{
  "record_id": "rosetta:fibonacci_sequence:python:0",
  "dataset": "rosettacode",
  "dataset_version": "git:<commit_sha>",
  "source_uri": "https://github.com/acmeism/RosettaCodeData",
  "source_path": "Task/Fibonacci sequence/Python/fibonacci-sequence.py",
  "task_id": "fibonacci_sequence",
  "task_name": "Fibonacci sequence",
  "task_category": "algorithm",
  "language": "python",
  "language_version": null,
  "implementation_index": 0,
  "equivalence_group_id": "rosetta:fibonacci_sequence",
  "equivalence_confidence": "source_aligned",
  "license": "source_repo_license",
  "code_raw": "def fib(n):\n    ...",
  "code_raw_sha256": "sha256_hex",
  "ingested_at": "2026-05-26T00:00:00Z"
}
```

### 3.2 Code Variant 记录

同一 snippet 输出三种变体：

- `raw`：保留源文件主体，仅统一换行符和尾部空白。
- `clean`：移除注释、shebang、纯空行，保留代码结构。
- `canonical`：在 clean 基础上使用语言标准 formatter 或稳定 formatter 输出；若 formatter 不可用，则标记 `canonical_status=unavailable`，不伪造结果。

```json
{
  "variant_id": "rosetta:fibonacci_sequence:python:0:clean",
  "record_id": "rosetta:fibonacci_sequence:python:0",
  "variant": "clean",
  "code": "def fib(n):\n    ...",
  "char_count": 42,
  "byte_count": 42,
  "sloc": 3,
  "cleaner": "pygments_comment_cleaner_v1",
  "cleaner_status": "ok",
  "cleaner_warnings": []
}
```

### 3.3 Token Count 记录

```json
{
  "token_count_id": "rosetta:fibonacci_sequence:python:0:clean:o200k_base",
  "variant_id": "rosetta:fibonacci_sequence:python:0:clean",
  "tokenizer_provider": "openai",
  "tokenizer_name": "o200k_base",
  "tokenizer_package": "tiktoken",
  "tokenizer_package_version": "pinned_in_lockfile",
  "model_reference": null,
  "token_count": 17,
  "counted_at": "2026-05-26T00:00:00Z"
}
```

### 3.4 Agent Run Log 记录

每次 agent 参与研究都必须写入 JSONL：

```json
{
  "run_id": "20260526-001",
  "timestamp": "2026-05-26T00:00:00Z",
  "phase": "phase1_rosettacode_ingest",
  "actor": "coding_agent",
  "model": "gpt-5",
  "task": "inspect Rosetta Code mirror and implement parser",
  "prompt_hash": "sha256_hex",
  "input_artifacts": ["configs/languages.yaml"],
  "commands": ["python scripts/fetch_rosettacode.py --dry-run"],
  "output_artifacts": ["data/interim/rosettacode_manifest.parquet"],
  "decisions": ["Use strict six-language intersection for primary analysis"],
  "uncertainties": ["TypeScript coverage may be too sparse for Phase 1 paired tests"],
  "human_intervention": "approved language set and strict intersection policy",
  "reflection_path": "research_log/reflections/20260526-001.md"
}
```

---

## 4. Task 1：初始化研究仓库

**Files:**

- Create: `README.md`
- Create: `pyproject.toml`
- Create: `Makefile`
- Create: `.gitignore`
- Create: `configs/languages.yaml`
- Create: `configs/tokenizers.yaml`
- Create: `configs/datasets.yaml`
- Create: `configs/preprocessing.yaml`
- Create: `src/cltd/__init__.py`
- Create: `src/cltd/paths.py`
- Create: `tests/test_project_import.py`

- [ ] **Step 1: 创建仓库目录与基础目录**

Run in PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path cross-lang-token-density | Out-Null
Set-Location cross-lang-token-density
$dirs = @(
  "configs",
  "data/raw",
  "data/interim",
  "data/processed",
  "data/results",
  "docs",
  "prompts",
  "research_log/runs",
  "research_log/reflections",
  "report/figures",
  "paper",
  "scripts",
  "src/cltd",
  "tests/fixtures"
)
$dirs | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }
```

Expected: 目录创建成功。

- [ ] **Step 2: 写入 `pyproject.toml`**

Use:

```toml
[project]
name = "cross-lang-token-density"
version = "0.1.0"
description = "Cross-language source code token density analysis for coding-agent era project selection."
requires-python = ">=3.12"
dependencies = [
  "pandas>=2.2",
  "pyarrow>=16.0",
  "pydantic>=2.7",
  "typer>=0.12",
  "rich>=13.7",
  "pyyaml>=6.0",
  "tiktoken>=0.7",
  "pygments>=2.18",
  "scipy>=1.13",
  "statsmodels>=0.14",
  "matplotlib>=3.9",
  "seaborn>=0.13",
  "plotly>=5.22"
]

[dependency-groups]
dev = [
  "pytest>=8.2",
  "ruff>=0.5",
  "mypy>=1.10"
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: 写入 `Makefile`**

Use:

```makefile
.PHONY: test lint fetch-rosetta preprocess tokenize analyze figures report reproduce

test:
	uv run pytest -q

lint:
	uv run ruff check src scripts tests

fetch-rosetta:
	uv run python scripts/fetch_rosettacode.py

preprocess:
	uv run python scripts/preprocess.py

tokenize:
	uv run python scripts/tokenize.py

analyze:
	uv run python scripts/analyze.py

figures:
	uv run python scripts/make_figures.py

report:
	uv run python scripts/analyze.py
	uv run python scripts/make_figures.py

reproduce: fetch-rosetta preprocess tokenize analyze figures
```

- [ ] **Step 4: 写入核心配置**

`configs/languages.yaml`:

```yaml
languages:
  - id: python
    display: Python
    rosetta_names: ["Python"]
    extensions: [".py"]
  - id: javascript
    display: JavaScript
    rosetta_names: ["JavaScript", "ECMAScript"]
    extensions: [".js", ".mjs"]
  - id: typescript
    display: TypeScript
    rosetta_names: ["TypeScript"]
    extensions: [".ts"]
  - id: java
    display: Java
    rosetta_names: ["Java"]
    extensions: [".java"]
  - id: go
    display: Go
    rosetta_names: ["Go"]
    extensions: [".go"]
  - id: rust
    display: Rust
    rosetta_names: ["Rust"]
    extensions: [".rs"]
  - id: c
    display: C
    rosetta_names: ["C"]
    extensions: [".c", ".h"]
primary_intersection:
  required_languages: ["python", "javascript", "java", "go", "rust", "c"]
  optional_languages: ["typescript"]
```

`configs/tokenizers.yaml`:

```yaml
tokenizers:
  - id: cl100k_base
    provider: openai
    package: tiktoken
    local: true
  - id: o200k_base
    provider: openai
    package: tiktoken
    local: true
provider_api_tokenizers:
  enabled_by_default: false
  reason: "Vendor API token counting may incur cost and model availability changes; use for validation sample only."
```

`configs/datasets.yaml`:

```yaml
datasets:
  rosettacode:
    source_uri: "https://github.com/acmeism/RosettaCodeData"
    local_path: "data/raw/rosettacode"
    phase: 1
  leetcode:
    phase: 2
    candidate_repos:
      - "https://github.com/doocs/leetcode"
      - "https://github.com/krahets/LeetCode"
  github_projects:
    phase: 3
    keyword_file: "configs/github_keywords.yaml"
```

`configs/preprocessing.yaml`:

```yaml
variants:
  raw:
    normalize_newlines: true
    strip_trailing_whitespace: true
    remove_shebang: false
    remove_comments: false
    remove_blank_lines: false
  clean:
    normalize_newlines: true
    strip_trailing_whitespace: true
    remove_shebang: true
    remove_comments: true
    remove_blank_lines: true
  canonical:
    base_variant: clean
    formatter_required: false
```

- [ ] **Step 5: 写入 smoke test**

`tests/test_project_import.py`:

```python
def test_import_package():
    import cltd

    assert cltd.__name__ == "cltd"
```

- [ ] **Step 6: 验证**

Run:

```powershell
uv sync
uv run pytest -q
uv run ruff check src scripts tests
```

Expected: `pytest` 通过；`ruff` 没有错误。

验收标准：新仓库能安装依赖、运行测试；Phase 1 的直接复现命令和可选 Makefile 目标都已固定。

---

## 5. Task 2：实现数据 schema 与数据字典

**Files:**

- Create: `src/cltd/schemas.py`
- Create: `docs/data-dictionary.md`
- Test: `tests/test_schemas.py`

- [ ] **Step 1: 写入 Pydantic schema**

Create `src/cltd/schemas.py`:

```python
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


CodeVariant = Literal["raw", "clean", "canonical"]
CleanerStatus = Literal["ok", "warning", "failed", "unavailable"]


class SnippetRecord(BaseModel):
    record_id: str
    dataset: str
    dataset_version: str
    source_uri: str
    source_path: str
    task_id: str
    task_name: str
    task_category: str | None = None
    language: str
    language_version: str | None = None
    implementation_index: int = 0
    equivalence_group_id: str
    equivalence_confidence: str
    license: str | None = None
    code_raw: str
    code_raw_sha256: str
    ingested_at: datetime


class CodeVariantRecord(BaseModel):
    variant_id: str
    record_id: str
    variant: CodeVariant
    code: str
    char_count: int = Field(ge=0)
    byte_count: int = Field(ge=0)
    sloc: int = Field(ge=0)
    cleaner: str
    cleaner_status: CleanerStatus
    cleaner_warnings: list[str] = Field(default_factory=list)


class TokenCountRecord(BaseModel):
    token_count_id: str
    variant_id: str
    tokenizer_provider: str
    tokenizer_name: str
    tokenizer_package: str
    tokenizer_package_version: str
    model_reference: str | None = None
    token_count: int = Field(ge=0)
    counted_at: datetime


class AgentRunLog(BaseModel):
    run_id: str
    timestamp: datetime
    phase: str
    actor: Literal["coding_agent", "human", "hybrid"]
    model: str | None = None
    task: str
    prompt_hash: str | None = None
    input_artifacts: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    output_artifacts: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    human_intervention: str | None = None
    reflection_path: str | None = None
```

- [ ] **Step 2: 写 schema 测试**

Create `tests/test_schemas.py`:

```python
from datetime import UTC, datetime

from cltd.schemas import CodeVariantRecord, SnippetRecord, TokenCountRecord


def test_snippet_record_accepts_minimal_valid_record():
    record = SnippetRecord(
        record_id="rosetta:fib:python:0",
        dataset="rosettacode",
        dataset_version="git:abc123",
        source_uri="https://github.com/acmeism/RosettaCodeData",
        source_path="Task/Fibonacci sequence/Python/example.py",
        task_id="fibonacci_sequence",
        task_name="Fibonacci sequence",
        language="python",
        equivalence_group_id="rosetta:fibonacci_sequence",
        equivalence_confidence="source_aligned",
        code_raw="print('hello')\n",
        code_raw_sha256="abc",
        ingested_at=datetime(2026, 5, 26, tzinfo=UTC),
    )

    assert record.language == "python"


def test_code_variant_rejects_negative_counts():
    try:
        CodeVariantRecord(
            variant_id="x",
            record_id="r",
            variant="clean",
            code="",
            char_count=-1,
            byte_count=0,
            sloc=0,
            cleaner="test",
            cleaner_status="ok",
        )
    except ValueError as exc:
        assert "greater than or equal to 0" in str(exc)
    else:
        raise AssertionError("negative char_count should fail validation")


def test_token_count_rejects_negative_tokens():
    try:
        TokenCountRecord(
            token_count_id="x",
            variant_id="v",
            tokenizer_provider="openai",
            tokenizer_name="o200k_base",
            tokenizer_package="tiktoken",
            tokenizer_package_version="0.7.0",
            token_count=-1,
            counted_at=datetime(2026, 5, 26, tzinfo=UTC),
        )
    except ValueError as exc:
        assert "greater than or equal to 0" in str(exc)
    else:
        raise AssertionError("negative token_count should fail validation")
```

- [ ] **Step 3: 写数据字典**

Create `docs/data-dictionary.md` with these sections:

```markdown
# Data Dictionary

## SnippetRecord

`SnippetRecord` represents one source-code implementation of one task in one language.

- `record_id`: Stable unique id: `{dataset}:{task_id}:{language}:{implementation_index}`.
- `dataset`: Source dataset id, e.g. `rosettacode`.
- `dataset_version`: Dataset version pin, preferably git commit SHA.
- `source_uri`: Upstream repository or API URL.
- `source_path`: Path inside upstream source.
- `task_id`: Normalized task id.
- `task_name`: Human-readable task name.
- `task_category`: One of `algorithm`, `io`, `text`, `data_structure`, `numeric`, `system`, `unknown`.
- `language`: Normalized language id from `configs/languages.yaml`.
- `equivalence_group_id`: Group id for paired comparison.
- `equivalence_confidence`: `source_aligned`, `test_aligned`, `human_reviewed`, or `weak_candidate`.

## CodeVariantRecord

`raw`, `clean`, and `canonical` variants are stored separately so analysis can compare preprocessing sensitivity.

## TokenCountRecord

Token counts must include tokenizer name, package, package version, and count timestamp.

## AgentRunLog

Every material agent action must have a run log. A material action is any step that changes data, code, analysis, interpretation, or paper text.
```

- [ ] **Step 4: 验证**

Run:

```powershell
uv run pytest -q
```

Expected: schema tests pass。

验收标准：所有后续数据文件都能映射到明确 schema，论文方法部分可引用数据字典。

---

## 6. Task 3：建立 agent 辅助科研日志机制

**Files:**

- Create: `prompts/reflection_template.md`
- Create: `prompts/data_collection_agent.md`
- Create: `prompts/equivalence_review_agent.md`
- Create: `prompts/analysis_agent.md`
- Create: `src/cltd/agent_logging/run_log.py`
- Create: `src/cltd/agent_logging/reflection.py`
- Create: `scripts/log_reflection.py`
- Test: `tests/test_agent_logging.py`

- [ ] **Step 1: 写反思模板**

Create `prompts/reflection_template.md`:

```markdown
# Agent Reflection

## Run Metadata

- Run ID:
- Date:
- Phase:
- Model:
- Human operator:

## Task

State the task in one sentence.

## Inputs

List source files, data files, prompts, commands, and assumptions used.

## Actions Taken

List concrete actions, including commands and files changed.

## Decisions

List research or engineering decisions made during the run.

## Uncertainties

List uncertainties that may affect data quality, statistical validity, or interpretation.

## Failures and Recovery

Record errors, failed commands, discarded approaches, and why recovery choice was made.

## Human Intervention

Record what the human approved, corrected, rejected, or clarified.

## Output Artifacts

List generated files and their purpose.

## Next Step

State the next executable step.
```

- [ ] **Step 2: 写 agent 角色 prompt**

Create `prompts/data_collection_agent.md`:

```markdown
# Data Collection Agent

You collect source data for the cross-language token density study.

Rules:
- Preserve upstream provenance: URL, commit SHA, source path, license note.
- Do not silently drop files. Emit an exclusion record with reason.
- Prefer deterministic scripts over manual copy.
- After every material action, write an AgentRunLog and reflection.
- Flag any source whose license or structure is unclear.
```

Create `prompts/equivalence_review_agent.md`:

```markdown
# Equivalence Review Agent

You review whether code snippets are comparable for paired token-density analysis.

Rules:
- Assign confidence: `source_aligned`, `test_aligned`, `human_reviewed`, or `weak_candidate`.
- Do not upgrade confidence without evidence.
- Record whether snippets implement the same task, same IO contract, and comparable algorithmic intent.
- If unsure, keep the snippet but mark it for sensitivity analysis exclusion.
```

Create `prompts/analysis_agent.md`:

```markdown
# Analysis Agent

You run statistical analysis and produce reproducible outputs.

Rules:
- Treat each task as a paired unit.
- Prefer medians, log ratios, bootstrap confidence intervals, and paired tests.
- Never report only aggregate means.
- Record exact commands, package versions, and generated artifacts.
- Separate findings from interpretation.
```

- [ ] **Step 3: 实现日志写入工具**

Create `src/cltd/agent_logging/run_log.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from cltd.schemas import AgentRunLog


def append_run_log(path: Path, record: AgentRunLog) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(record.model_dump_json() + "\n")


def read_run_logs(path: Path) -> list[AgentRunLog]:
    if not path.exists():
        return []
    records: list[AgentRunLog] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(AgentRunLog.model_validate(json.loads(line)))
    return records
```

Create `src/cltd/agent_logging/reflection.py`:

```python
from __future__ import annotations

from pathlib import Path


def write_reflection(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
```

- [ ] **Step 4: 写 CLI**

Create `scripts/log_reflection.py`:

```python
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import typer

from cltd.agent_logging.run_log import append_run_log
from cltd.schemas import AgentRunLog

app = typer.Typer()


@app.command()
def main(
    run_id: str,
    phase: str,
    task: str,
    model: str = "unknown",
    reflection_path: Path | None = None,
    log_path: Path = Path("research_log/runs/agent_runs.jsonl"),
) -> None:
    record = AgentRunLog(
        run_id=run_id,
        timestamp=datetime.now(UTC),
        phase=phase,
        actor="coding_agent",
        model=model,
        task=task,
        reflection_path=str(reflection_path) if reflection_path else None,
    )
    append_run_log(log_path, record)
    typer.echo(f"logged {run_id} -> {log_path}")


if __name__ == "__main__":
    app()
```

- [ ] **Step 5: 写测试**

Create `tests/test_agent_logging.py`:

```python
from datetime import UTC, datetime

from cltd.agent_logging.run_log import append_run_log, read_run_logs
from cltd.schemas import AgentRunLog


def test_append_and_read_run_log(tmp_path):
    path = tmp_path / "runs.jsonl"
    record = AgentRunLog(
        run_id="r1",
        timestamp=datetime(2026, 5, 26, tzinfo=UTC),
        phase="test",
        actor="coding_agent",
        model="gpt-5",
        task="write a test log",
    )

    append_run_log(path, record)
    loaded = read_run_logs(path)

    assert len(loaded) == 1
    assert loaded[0].run_id == "r1"
```

- [ ] **Step 6: 验证**

Run:

```powershell
uv run pytest -q
uv run python scripts/log_reflection.py --run-id 20260526-001 --phase setup --task "initialize logging protocol" --model gpt-5
```

Expected: tests pass; `research_log/runs/agent_runs.jsonl` 出现一条记录。

验收标准：任何 agent 后续动作都有统一日志入口，论文方法论中可展示日志 schema 和示例。

---

## 7. Task 4：实现 Rosetta Code 数据采集

**Files:**

- Create: `src/cltd/datasets/rosettacode.py`
- Create: `scripts/fetch_rosettacode.py`
- Test: `tests/test_rosettacode_ingest.py`
- Create fixtures: `tests/fixtures/rosetta_sample/Task/Fibonacci sequence/Python/example.py`
- Create fixtures: `tests/fixtures/rosetta_sample/Task/Fibonacci sequence/Java/example.java`

- [ ] **Step 1: 写 Rosetta 解析函数**

Create `src/cltd/datasets/rosettacode.py`:

```python
from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path

from cltd.schemas import SnippetRecord


def normalize_task_id(name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower())
    return normalized.strip("_")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def iter_rosetta_records(root: Path, language_map: dict[str, str]) -> list[SnippetRecord]:
    task_root = root / "Task"
    records: list[SnippetRecord] = []
    if not task_root.exists():
        raise FileNotFoundError(f"missing Task directory: {task_root}")

    for task_dir in sorted(p for p in task_root.iterdir() if p.is_dir()):
        task_id = normalize_task_id(task_dir.name)
        for language_dir in sorted(p for p in task_dir.iterdir() if p.is_dir()):
            language = language_map.get(language_dir.name)
            if language is None:
                continue
            source_files = sorted(p for p in language_dir.rglob("*") if p.is_file())
            for index, source_file in enumerate(source_files):
                code = source_file.read_text(encoding="utf-8", errors="replace")
                records.append(
                    SnippetRecord(
                        record_id=f"rosetta:{task_id}:{language}:{index}",
                        dataset="rosettacode",
                        dataset_version="git:unknown",
                        source_uri="https://github.com/acmeism/RosettaCodeData",
                        source_path=str(source_file.relative_to(root)).replace("\\", "/"),
                        task_id=task_id,
                        task_name=task_dir.name,
                        language=language,
                        implementation_index=index,
                        equivalence_group_id=f"rosetta:{task_id}",
                        equivalence_confidence="source_aligned",
                        license="source_repo_license",
                        code_raw=code,
                        code_raw_sha256=sha256_text(code),
                        ingested_at=datetime.now(UTC),
                    )
                )
    return records
```

- [ ] **Step 2: 写采集 CLI**

Create `scripts/fetch_rosettacode.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml

from cltd.datasets.rosettacode import iter_rosetta_records

app = typer.Typer()


def load_language_map(path: Path) -> dict[str, str]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    mapping: dict[str, str] = {}
    for language in config["languages"]:
        for rosetta_name in language["rosetta_names"]:
            mapping[rosetta_name] = language["id"]
    return mapping


@app.command()
def main(
    root: Path = Path("data/raw/rosettacode"),
    languages: Path = Path("configs/languages.yaml"),
    output: Path = Path("data/interim/rosettacode_snippets.jsonl"),
) -> None:
    language_map = load_language_map(languages)
    records = iter_rosetta_records(root, language_map)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")
    typer.echo(f"wrote {len(records)} records to {output}")


if __name__ == "__main__":
    app()
```

- [ ] **Step 3: 写 fixtures 和测试**

Create `tests/test_rosettacode_ingest.py`:

```python
from pathlib import Path

from cltd.datasets.rosettacode import iter_rosetta_records, normalize_task_id


def test_normalize_task_id():
    assert normalize_task_id("Fibonacci sequence") == "fibonacci_sequence"


def test_iter_rosetta_records_reads_language_directories():
    root = Path("tests/fixtures/rosetta_sample")
    records = iter_rosetta_records(root, {"Python": "python", "Java": "java"})

    assert {r.language for r in records} == {"python", "java"}
    assert {r.task_id for r in records} == {"fibonacci_sequence"}
```

Create fixture contents:

`tests/fixtures/rosetta_sample/Task/Fibonacci sequence/Python/example.py`:

```python
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

`tests/fixtures/rosetta_sample/Task/Fibonacci sequence/Java/example.java`:

```java
class Fibonacci {
  static int fib(int n) {
    return n < 2 ? n : fib(n - 1) + fib(n - 2);
  }
}
```

- [ ] **Step 4: 克隆并 pin 数据源**

Run:

```powershell
git clone https://github.com/acmeism/RosettaCodeData data/raw/rosettacode
git -C data/raw/rosettacode rev-parse HEAD > data/raw/rosettacode_COMMIT.txt
```

Expected: `data/raw/rosettacode_COMMIT.txt` 包含 upstream commit SHA。

- [ ] **Step 5: 运行采集**

Run:

```powershell
uv run pytest -q
uv run python scripts/fetch_rosettacode.py
```

Expected: `data/interim/rosettacode_snippets.jsonl` 生成，记录数大于 0。

验收标准：Rosetta Code 原始代码能被稳定解析；每条记录有 provenance、task id、language、source path 和 hash。

---

## 8. Task 5：实现功能等价分组与任务覆盖矩阵

**Files:**

- Create: `src/cltd/datasets/equivalence.py`
- Create: `scripts/build_equivalence_groups.py`
- Create: `docs/equivalence-criteria.md`
- Test: `tests/test_equivalence.py`

- [ ] **Step 1: 写等价标准文档**

Create `docs/equivalence-criteria.md`:

```markdown
# Functional Equivalence Criteria

## Confidence Levels

- `source_aligned`: Same upstream task page or benchmark problem; no additional manual review.
- `test_aligned`: Same tests or IO contract executed against implementations.
- `human_reviewed`: Human inspected snippets and confirmed comparable intent.
- `weak_candidate`: Candidate pair from search or keyword matching; excluded from primary claims.

## Primary Analysis Inclusion

Primary paired analysis includes only equivalence groups that:

1. Have one or more implementation records for every required language.
2. Come from `source_aligned`, `test_aligned`, or `human_reviewed` confidence.
3. Are not marked as parser failure, unreadable generated output, or non-code explanatory text.

## Sensitivity Analysis

Run sensitivity analysis by:

1. Excluding multi-file implementations.
2. Keeping only groups with exactly one implementation per language.
3. Comparing raw and clean variants separately.
4. Running six-language and seven-language intersections separately.
```

- [ ] **Step 2: 实现覆盖矩阵**

Create `src/cltd/datasets/equivalence.py`:

```python
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
```

- [ ] **Step 3: 写测试**

Create `tests/test_equivalence.py`:

```python
from datetime import UTC, datetime

from cltd.datasets.equivalence import strict_intersection_groups
from cltd.schemas import SnippetRecord


def make_record(group: str, language: str) -> SnippetRecord:
    return SnippetRecord(
        record_id=f"{group}:{language}:0",
        dataset="test",
        dataset_version="git:test",
        source_uri="local",
        source_path=f"{language}.txt",
        task_id=group,
        task_name=group,
        language=language,
        equivalence_group_id=group,
        equivalence_confidence="source_aligned",
        code_raw="x",
        code_raw_sha256="sha",
        ingested_at=datetime(2026, 5, 26, tzinfo=UTC),
    )


def test_strict_intersection_groups():
    records = [
        make_record("g1", "python"),
        make_record("g1", "java"),
        make_record("g2", "python"),
    ]

    assert strict_intersection_groups(records, {"python", "java"}) == {"g1"}
```

- [ ] **Step 4: 输出覆盖报告**

Create `scripts/build_equivalence_groups.py` to read `data/interim/rosettacode_snippets.jsonl`, compute:

- `data/processed/equivalence_groups.csv`
- `data/results/coverage_by_language.csv`
- `data/results/strict_intersection_tasks.csv`

The CSV columns:

```text
equivalence_group_id,task_id,task_name,languages_present,required_language_count,has_required_intersection,has_optional_typescript
```

- [ ] **Step 5: 验证**

Run:

```powershell
uv run pytest -q
uv run python scripts/build_equivalence_groups.py
```

Expected: 输出 strict intersection task 数量；如果数量低于 100，记录为研究风险并进入日志。

验收标准：主分析样本不是模糊地“有很多任务”，而是有明确 intersection 口径和可复核 CSV。

---

## 9. Task 6：实现代码预处理与 SLOC 统计

**Files:**

- Create: `src/cltd/preprocessing/normalize.py`
- Create: `src/cltd/preprocessing/clean.py`
- Create: `src/cltd/preprocessing/sloc.py`
- Create: `scripts/preprocess.py`
- Test: `tests/test_preprocess.py`

- [ ] **Step 1: 实现 raw normalization**

Rules:

- Convert `\r\n` and `\r` to `\n`.
- Strip trailing whitespace line by line.
- Preserve indentation.
- Preserve blank lines in raw variant.

- [ ] **Step 2: 实现 clean variant**

Use `pygments` tokenization first:

- Drop tokens under `Token.Comment`.
- Drop shebang line when first line starts with `#!`.
- Drop pure blank lines after comment removal.
- Preserve string literals, including strings that contain `#`, `//`, or `/*`.
- Mark `cleaner_status="warning"` if lexer fallback is used.

- [ ] **Step 3: 实现 SLOC**

Definition:

- `sloc_raw`: count non-empty lines after raw normalization.
- `sloc_clean`: count non-empty lines after clean processing.
- Do not count comment-only lines in clean variant.

- [ ] **Step 4: 写测试用例**

Test cases must cover:

- Python `# comment`
- JavaScript `// comment`
- C/Java/Rust `/* comment */`
- URL string `"https://example.com/a//b"` must remain intact
- Python string `"# not a comment"` must remain intact
- Shebang removal in clean variant

- [ ] **Step 5: 写预处理 CLI**

`scripts/preprocess.py` reads:

- `data/interim/rosettacode_snippets.jsonl`

Writes:

- `data/processed/code_variants.parquet`
- `data/results/preprocess_warnings.csv`

- [ ] **Step 6: 验证**

Run:

```powershell
uv run pytest -q
uv run python scripts/preprocess.py
```

Expected:

- `code_variants.parquet` contains 3 variants per snippet when canonical is available.
- If canonical is unavailable, raw and clean still exist; canonical records have `cleaner_status=unavailable`.

验收标准：clean 逻辑有测试保护；任何清洗失败不会静默污染主结果。

---

## 10. Task 7：实现 tokenizer registry 与 token 统计

**Files:**

- Create: `src/cltd/tokenizers/registry.py`
- Create: `src/cltd/tokenizers/openai_tiktoken.py`
- Create: `scripts/tokenize.py`
- Test: `tests/test_tokenize.py`

- [ ] **Step 1: 实现 tokenizer interface**

Interface:

```python
class CodeTokenizer:
    provider: str
    name: str
    package: str

    def count(self, text: str) -> int:
        ...
```

- [ ] **Step 2: 实现 OpenAI tiktoken tokenizer**

Supported:

- `cl100k_base`
- `o200k_base`

Record:

- tokenizer name
- package name
- package version
- count timestamp

- [ ] **Step 3: 写 token 统计 CLI**

`scripts/tokenize.py` reads:

- `data/processed/code_variants.parquet`

Writes:

- `data/processed/token_counts.parquet`
- `data/results/tokenizer_summary.csv`

- [ ] **Step 4: 写测试**

Tests:

- Empty string token count is 0 or tokenizer-defined count; expected value must be pinned.
- Same input counted twice returns same number.
- Unknown tokenizer id raises clear error.

- [ ] **Step 5: 验证**

Run:

```powershell
uv run pytest -q
uv run python scripts/tokenize.py
```

Expected: 每个 available code variant 都有 `cl100k_base` 和 `o200k_base` token count。

验收标准：所有 token 统计都可追溯到 tokenizer name 和 package version；后续加入 Anthropic/Gemini/DeepSeek 时不改变数据合同。

---

## 11. Task 8：实现成对统计分析

**Files:**

- Create: `src/cltd/analysis/paired.py`
- Create: `src/cltd/analysis/statistics.py`
- Create: `scripts/analyze.py`
- Test: `tests/test_statistics.py`

- [ ] **Step 1: 构造成对分析表**

Input:

- `SnippetRecord`
- `CodeVariantRecord`
- `TokenCountRecord`
- `equivalence_groups.csv`

Output:

- `data/results/paired_language_ratios.csv`

Columns:

```text
equivalence_group_id,task_id,variant,tokenizer,baseline_language,comparison_language,baseline_tokens,comparison_tokens,ratio,log_ratio
```

Default baseline:

- `python`

- [ ] **Step 2: 实现统计指标**

For each `(variant, tokenizer, comparison_language)` compute:

- task count
- median ratio
- mean log ratio
- bootstrap 95% CI for median ratio
- Wilcoxon signed-rank p-value on paired token counts
- Cliff's delta

- [ ] **Step 3: 实现敏感性分析**

Run the same statistics for:

- raw only
- clean only
- canonical only when available
- six-language strict intersection
- seven-language TypeScript-inclusive subset when sample size is sufficient
- single-implementation-per-language groups only

- [ ] **Step 4: 写分析 CLI**

`scripts/analyze.py` writes:

- `data/results/summary_by_language.csv`
- `data/results/paired_language_ratios.csv`
- `data/results/stat_tests.csv`
- `data/results/sensitivity_analysis.csv`

- [ ] **Step 5: 验证**

Run:

```powershell
uv run pytest -q
uv run python scripts/analyze.py
```

Expected:

- Every reported language comparison has `n_tasks`.
- Statistical test table does not report p-values when `n_tasks < 20`; instead writes `insufficient_sample`.

验收标准：论文主结论基于成对任务，不基于混合后均值；所有统计结论带样本量与置信区间。

---

## 12. Task 9：生成图表与第一版中文报告

**Files:**

- Create: `src/cltd/analysis/figures.py`
- Create: `scripts/make_figures.py`
- Create: `report/report_zh.md`

- [ ] **Step 1: 生成主图**

Required figures:

- Boxplot: token count by language, variant, tokenizer.
- Ratio heatmap: median ratio to Python by language and tokenizer.
- Raw-clean delta: comment/blank-line effect by language.
- Task category effects: ratio distribution by task category.

- [ ] **Step 2: 写报告骨架**

`report/report_zh.md` must include:

```markdown
# 跨编程语言源代码 Token 密度对比研究

## 摘要

## 1. 背景与动机

## 2. 研究问题

## 3. 数据与方法

## 4. Agent 辅助科研协议

## 5. 结果

## 6. 讨论

## 7. 威胁与局限

## 8. 结论

## 附录 A：数据字段

## 附录 B：复现实验命令
```

- [ ] **Step 3: 填入可复现实验命令**

Report appendix must include:

```powershell
uv sync
uv run python scripts/fetch_rosettacode.py
uv run python scripts/preprocess.py
uv run python scripts/tokenize.py
uv run python scripts/analyze.py
uv run python scripts/make_figures.py
```

- [ ] **Step 4: 验证**

Run:

```powershell
uv run python scripts/make_figures.py
```

Expected:

- Figures generated in `report/figures/`.
- Report references existing figure paths.

验收标准：Phase 1 结束时即使还没做 LeetCode/GitHub，也能形成一篇完整中文技术报告。

---

## 13. Task 10：撰写英文论文草稿

**Files:**

- Create: `paper/main.md`
- Create: `paper/references.bib`
- Modify: `docs/methodology.md`

- [ ] **Step 1: 写论文主结构**

`paper/main.md`:

```markdown
# Cross-Language Source Code Token Density in the Coding-Agent Era

## Abstract

## 1. Introduction

## 2. Research Questions

## 3. Data

## 4. Method

## 5. Agent-Assisted Research Protocol

## 6. Results

## 7. Discussion

## 8. Threats to Validity

## 9. Conclusion

## Reproducibility Statement

## Ethics and Data Availability
```

- [ ] **Step 2: 论文 framing**

Introduction must emphasize:

- Coding agent context windows and API billing make token cost a practical software engineering metric.
- Existing code benchmarks focus on correctness or generation ability, not language-level expression cost.
- This paper measures static source token density, not full agent session cost.

- [ ] **Step 3: 方法论中写入 agent protocol**

Include:

- agent roles
- run logs
- reflection logs
- human approval points
- artifact hashes
- failures and excluded data

- [ ] **Step 4: 写 validity threats**

Must cover:

- Rosetta Code educational style bias
- equivalent functionality ambiguity
- tokenizer/model version drift
- comment removal errors
- language ecosystem style differences
- single-file vs project-level token cost gap
- coding agent assistance may introduce selection bias

验收标准：英文论文草稿可以直接进入 arXiv v0.1 或继续扩展 Phase 2/3。

---

## 14. Task 11：Phase 2 LeetCode 扩展

**Files:**

- Create: `src/cltd/datasets/leetcode.py`
- Create: `scripts/fetch_leetcode.py`
- Create: `docs/leetcode-source-review.md`
- Test: `tests/test_leetcode_ingest.py`

- [ ] **Step 1: 评估候选仓库**

For each candidate repo record:

- license
- language coverage
- problem count
- directory consistency
- whether same solution approach is identifiable
- whether source files are machine-parseable

Write results to `docs/leetcode-source-review.md`.

- [ ] **Step 2: 只纳入强对齐样本**

Primary LeetCode analysis includes only:

- same problem id
- same high-level algorithm tag if available
- accepted solution or official/community maintained solution
- language implementations not obviously different in asymptotic complexity

- [ ] **Step 3: 输出 LeetCode 单独结果**

Write:

- `data/processed/leetcode_snippets.parquet`
- `data/results/leetcode_summary_by_language.csv`
- `report/figures/leetcode_vs_rosetta_ratios.png`

验收标准：LeetCode 作为外部验证数据源，不覆盖 Rosetta Code 主结果。

---

## 15. Task 12：Phase 3 GitHub 功能配对扩展

**Files:**

- Create: `configs/github_keywords.yaml`
- Create: `src/cltd/datasets/github_projects.py`
- Create: `scripts/fetch_github_candidates.py`
- Create: `docs/github-pairing-review.md`

- [ ] **Step 1: 定义功能关键词**

Start with 10:

```yaml
keywords:
  - json parser
  - markdown to html
  - url shortener
  - todo cli
  - http server
  - csv parser
  - password generator
  - lru cache
  - calculator
  - ini parser
```

- [ ] **Step 2: GitHub Search 初筛**

For each keyword and language:

- collect top candidates by stars
- exclude forks when possible
- record repository URL, license, stars, file path, search query
- do not download private or unclear-license data

- [ ] **Step 3: 人工审核配对**

Each accepted pair must record:

- function description
- included file path
- excluded framework boilerplate reason
- reviewer
- review date
- confidence level

Write review table to `docs/github-pairing-review.md`.

验收标准：GitHub 数据只作为深挖案例或稳健性分析，不让低置信配对污染主结论。

---

## 16. Task 13：复现、发布与版本管理

**Files:**

- Create: `docs/reproducibility.md`
- Create: `docs/release-checklist.md`
- Modify: `README.md`

- [ ] **Step 1: 写复现说明**

`docs/reproducibility.md` must include:

````markdown
# Reproducibility

## Environment

- Python 3.12
- uv
- Operating system used for original run

## Commands

```bash
uv sync
uv run python scripts/fetch_rosettacode.py
uv run python scripts/preprocess.py
uv run python scripts/tokenize.py
uv run python scripts/analyze.py
uv run python scripts/make_figures.py
```

## Data Version Pins

- Rosetta Code commit: recorded in `data/raw/rosettacode_COMMIT.txt`
- Package lock: `uv.lock`
- Tokenizer package versions: recorded in `data/processed/token_counts.parquet`

## Expected Outputs

- `data/results/summary_by_language.csv`
- `data/results/stat_tests.csv`
- `report/figures/*.png`
````

- [ ] **Step 2: 写发布检查清单**

`docs/release-checklist.md`:

```markdown
# Release Checklist

- [ ] `uv run pytest -q` passes.
- [ ] `uv run ruff check src scripts tests` passes.
- [ ] Phase 1 direct reproduction commands finish from a clean checkout.
- [ ] Dataset source commit hashes are recorded.
- [ ] Exclusion reasons are recorded.
- [ ] Agent logs are complete for material actions.
- [ ] Report figures are regenerated.
- [ ] README contains citation, license, and data availability.
- [ ] Paper includes reproducibility statement.
```

- [ ] **Step 3: 创建版本标签**

Run:

```powershell
git tag -a v0.1-rosetta -m "Phase 1 Rosetta Code token density analysis"
```

验收标准：别人能从仓库 README 按命令复现 Phase 1 结果。

---

## 17. 推荐时间线

### Week 1：研究基础设施

- 完成 Task 1-3。
- 产出仓库骨架、schema、agent logging protocol。
- 决策点：确认语言集合和 tokenizer 第一版范围。

### Week 2：Rosetta Code 采集与等价分组

- 完成 Task 4-5。
- 产出 strict intersection 任务列表。
- 决策点：确认 TypeScript 是否进入主统计。

### Week 3：预处理与 token 统计

- 完成 Task 6-7。
- 产出 raw/clean/canonical 变体和 token counts。
- 决策点：检查 cleaner warning 率；如果 warning 率高于 5%，暂停主分析并修清洗器。

### Week 4：统计分析与中文报告

- 完成 Task 8-9。
- 产出 Phase 1 中文技术报告。
- 决策点：确认主发现是否足够支撑 arXiv v0.1。

### Week 5：论文草稿

- 完成 Task 10。
- 产出英文论文草稿。
- 决策点：决定先发 Rosetta-only v0.1，还是等 Phase 2。

### Week 6-7：LeetCode 扩展

- 完成 Task 11。
- 产出外部验证结果。

### Week 8-9：GitHub 深挖案例

- 完成 Task 12。
- 产出真实项目案例分析。

### Week 10：发布

- 完成 Task 13。
- 发布数据、代码、中文报告和论文草稿。

---

## 18. 质量门槛

必须满足：

- `uv run pytest -q` 通过。
- Phase 1 direct reproduction commands 可从干净环境跑完。
- 主分析只用 paired task。
- 每个 tokenizer count 都有 tokenizer name 和 package version。
- 每个数据源都有 source URI、commit/version、license note。
- 每个排除样本都有 exclusion reason。
- 每个 material agent action 都有 run log。
- 报告中明确区分 static source token density 与 full agent session token cost。

暂停条件：

- Rosetta strict intersection 少于 100 个任务。
- cleaner warning/failed 比例高于 5%。
- 任一语言样本中大量记录不是代码而是说明文本。
- token count 出现不可复现差异。
- 主统计结论只依赖均值、没有 paired ratio 或置信区间。

---

## 19. 最小可发表版本定义

最小可发表版本只需要：

- Rosetta Code Phase 1。
- 六语言严格交集。
- raw 与 clean 两个代码变体。
- `cl100k_base` 与 `o200k_base` 两个 tokenizer。
- paired ratio、bootstrap CI、Wilcoxon、Cliff's delta。
- 中文报告。
- 英文论文草稿。
- 完整 agent run log 和 reflection log。

不阻塞 v0.1 的内容：

- LeetCode。
- GitHub 项目配对。
- Anthropic/Gemini/DeepSeek provider API token count。
- Web dashboard。
- 完整 agent session generation cost 实验。

---

## 20. 执行方式建议

推荐采用 Subagent-Driven：

- 每个 Task 派一个 fresh agent 实现。
- 主 agent 做 code review、数据质量 review、统计 sanity check。
- 每个 Task 完成后写一条 agent run log 和一篇 reflection。
- 每周结束写一篇 `research_log/reflections/week-N-summary.md`，总结决策、失败和下一步。

Inline Execution 也可行，但要严格在每个 Task 完成后暂停做验收，避免把数据采集、清洗和结论解释混在一起。
