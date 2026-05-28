# 实验复现指南 (Reproducibility)

## 1. 运行环境配置

本研究所使用的软件和硬件依赖如下：

- **操作系统**：Windows (已通过 Windows 兼容性兼容处理)
- **Python 版本**：>= 3.12 (经 CPython 3.13 验证通过)
- **依赖管理器**：`uv` (由 `pyproject.toml` 和 `uv.lock` 统一锁定)

## 2. 复现命令行步骤

在一个干净的克隆仓库中，依次在命令行中执行以下命令以完成全部实验数据采集、清洗、统计分析和图表生成：

```bash
# 1. 安装项目及开发依赖，自动在虚拟环境中配置包
uv sync

# 2. 采集并提取 Rosetta Code 数据 (使用非 cone 模式的 sparse-checkout 排除不合规字符文件)
uv run python scripts/fetch_rosettacode.py

# 3. 运行代码清洗预处理 (生成 raw, clean, canonical 三种变体)
uv run python scripts/preprocess.py

# 4. 计算 Token 计数统计 (支持 cl100k_base 和 o200k_base 编码)
uv run python scripts/tokenize_data.py

# 5. 运行成对统计分析与敏感性分析统计
uv run python scripts/analyze.py

# 6. 生成报告所需的四张主图表
uv run python scripts/make_figures.py
```

或者（如果在 Windows/Linux 环境中配置了 `make` 工具），可以直接运行一键别名：

```bash
make reproduce
```

## 3. 预期输出产物对照表

运行上述命令后，将产生以下核心结果文件：

- 数据文件：
  - [code_variants.parquet](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/data/processed/code_variants.parquet)
  - [token_counts.parquet](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/data/processed/token_counts.parquet)
  - [equivalence_groups.csv](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/data/processed/equivalence_groups.csv)
- 统计检验与分析结果：
  - [summary_by_language.csv](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/data/results/summary_by_language.csv)
  - [stat_tests.csv](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/data/results/stat_tests.csv)
  - [sensitivity_analysis.csv](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/data/results/sensitivity_analysis.csv)
- 核心可视化图表（位于 `report/figures/`）：
  - `boxplot_token_count_by_language.png`
  - `ratio_heatmap_by_tokenizer.png`
  - `raw_clean_delta_by_language.png`
  - `task_category_effects.png`
