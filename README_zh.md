# 跨编程语言源代码 Token 密度对比分析研究

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

[English](./README.md) | 简体中文

本仓库包含一个完整且可复现的研究流水线，用于评估和分析以下八种主流编程语言在代码表达效率上的 Token 密度差异：**C, C++, Go, Java, JavaScript, Python, Rust 和 TypeScript**。

通过评估在实现相同算法或功能时不同语言所需的 Token 数量，我们构建了一个实证性质的 “Token 表达效率层级”。这在大语言模型（LLM）与智能编码代理（Coding Agent）协同开发的时代具有重要的实际意义，因为代码的 Token 密度直接决定了 API 调用成本与上下文窗口的有效利用率。

---

## 核心发现 (Abstract)

1. **Rosetta Code 基准 (Phase 1)**：基于 **693 个** 严格等价的任务实现：
   - **语言表达力层级**：动态类型的脚本语言具有最高的 Token 表达效率。以 Python 为基准（1.00），各语言在清洗后代码变体（Clean Code）下的中位 Token 比例为：
     $$\text{C (1.77)} > \text{Rust (1.57)} > \text{Go (1.55)} > \text{Java (1.47)} > \text{TypeScript (1.45)} > \text{JavaScript (1.26)}$$
   - **类型标注成本**：TypeScript 相比 JavaScript 引入了 **~15% 的额外 Token 开销**，这正是显式类型安全所支付的物理成本。
   - **非语义冗余空间**：去除注释与 Shebang 可以在 C 中平均节省 **21%** 的 Token 开销，在 JavaScript 中节省 **16%**。
2. **LeetCode 实证泛化 (Phase 2)**：基于 `kamyu104/LeetCode-Solutions` 提取的 **3,681 个** 严格成对的算法实现：
   - **整体开销**：C++ 相对于 Python 的 Token 消耗中位数比例为 **1.20x**，这相比 Rosetta Code 中的 C 语言（1.77x）有显著的精简，验证了现代 C++ 标准库及高级数据结构抽象的表达优势。
   - **算法难度递增效应**：C++ 相对于 Python 的 Token 开销随着题目难度的增加而单调上升：**简单 (1.11x) $\rightarrow$ 中等 (1.19x) $\rightarrow$ 困难 (1.28x)**。跨难度组的全局 **Kruskal-Wallis H 检验** 极其显著（$p = 1.53 \times 10^{-42}$），证实了越是复杂的算法逻辑，C++ 所不得不编写的 boilerplate（如节点结构体声明、显式指针释放等）被放大的程度越严重。
3. **分词表平移稳定性**：这些语言间的相对比例在不同的 Tiktoken 分词表（如 `cl100k_base` 与 `o200k_base`）中保持极高的单调性与数值一致性。

---

## 项目结构

```text
cross-lang-token-density/
├── README.md              # 英文自述文件
├── README_zh.md           # 中文自述文件
├── pyproject.toml
├── Makefile               # 一键复现控制指令
├── configs/               # 配置文件目录（语言配置、分词器配置、预处理配置）
├── data/
│   ├── raw/               # 原始数据集挂载点（Rosetta Code 与 LeetCode 镜像）
│   ├── interim/           # 中间 JSONL 临时数据集
│   ├── processed/         # 变体代码及 Token 计数 Parquet 数据库
│   └── results/           # 导出的 CSV 统计报表与检验输出
├── docs/                  # 方法论、数据字典与发布检查清单
├── paper/                 # 英文学术论文草稿 (main.md & references.bib)
├── report/                # 中文技术报告及自动渲染的实验图表
├── scripts/               # 命令行运行工具脚本
├── src/cltd/              # 核心工具库
└── tests/                 # 完整的单元测试套件
```

---

## 快速开始

### 1. 依赖安装

本研究流水线需要 **Python 3.12+** 环境以及 Python 包管理工具 [**uv**](https://github.com/astral-sh/uv)。在项目根目录下，运行以下指令完成依赖的同步与可编辑模式包的构建：

```bash
uv sync
```

### 2. 实验复现

我们提供了简单完整的流水线复现机制，用于拉取原始数据集、执行代码清洗、运行分词计数、生成检验报告并渲染图谱。

#### Rosetta Code 实验流水线复现 (Phase 1)
```bash
# 使用 Makefile 一键复现
make reproduce

# 或手动运行 CLI 工具
uv run python scripts/fetch_rosettacode.py
uv run python scripts/preprocess.py
uv run python scripts/tokenize_data.py
uv run python scripts/analyze.py
uv run python scripts/make_figures.py
```

#### LeetCode 实验流水线复现 (Phase 2)
```bash
# 使用 Makefile 一键复现
make reproduce-leetcode

# 或手动运行 CLI 工具
uv run python scripts/fetch_leetcode.py
uv run python scripts/preprocess.py --snippets-path data/interim/leetcode_snippets.jsonl --variants-output data/processed/leetcode_variants.parquet --warnings-output data/results/leetcode_preprocess_warnings.csv
uv run python scripts/tokenize_data.py --variants-path data/processed/leetcode_variants.parquet --token-counts-output data/processed/leetcode_token_counts.parquet --summary-output data/results/leetcode_tokenizer_summary.csv
uv run python scripts/analyze.py --dataset leetcode
uv run python scripts/make_figures.py --dataset leetcode
```

### 3. 单元测试

项目包含完整的单元测试，用来验证数据清洗、分词映射、题号对准等逻辑：

```bash
uv run pytest -v
```

---

## 相关技术文档

- **方法论设计书**：[docs/methodology.md](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/docs/methodology.md)
- **数据字典定义**：[docs/data-dictionary.md](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/docs/data-dictionary.md)
- **中文技术报告 (CN)**：[report/report_zh.md](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/report/report_zh.md)
- **英文学术论文 (EN)**：[paper/main.md](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/paper/main.md)

---

## 开源许可证

本项目核心代码与工具链遵循 MIT 协议开源，详见 `LICENSE` 文件。在 `data/raw/` 中拉取和引用的外部数据集仍遵循其各自上游仓库的数据许可证许可。
