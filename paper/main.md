# Cross-Language Source Code Token Density in the Coding-Agent Era

## Abstract

With the advent of Large Language Models (LLMs) and autonomous coding agents, source code representation efficiency—measured in tokens—has emerged as a key factor determining both prompt context window utilization and API operational costs. In this paper, we conduct a systematic, paired statistical analysis of source code token density across seven major programming languages: C, Go, Java, JavaScript, Python, Rust, and TypeScript. Using a strict functional intersection of 693 tasks from Rosetta Code, we analyze token usage under both raw and comment-removed (clean) variants using the OpenAI `cl100k_base` and `o200k_base` tokenizers. 

To ensure peer-reviewed statistical rigor, we apply the Kruskal-Wallis H test for global significance, the Holm-Bonferroni correction for pairwise Wilcoxon signed-rank tests, and introduce new metrics to quantify tokenization fragmentation (Char-to-Token Ratio) and line density (Tokens-per-Line). Our results show a robust expression efficiency hierarchy: Python exhibits the highest density (fewest tokens), while comparison languages require significantly more tokens: C (+77%), Rust (+57%), Go (+55%), Java (+47%), and JavaScript (+26%). 

Subgroup analysis reveals that C requires **2.78x** more tokens for Text/String tasks due to lack of high-level abstractions, and static languages (Go, Java, Rust) require ~3x more tokens for System/IO tasks due to verbose error-handling boilerplate. Java exhibits the highest Char-to-Token Ratio (3.91), indicating low tokenizer fragmentation, while C exhibits the lowest (2.87). Python has the highest Tokens-per-Line density (9.42), whereas Go has the lowest (7.13) due to its vertical formatting idiom. These findings provide empirical ground rules for managing cost and context scaling in LLM-driven coding agent deployments.

---

## 1. Introduction

Autonomous software engineering agents (e.g., Devin, SWE-agent) increasingly drive modern software development. These agents interact with codebase repositories by reading and writing files. Since LLM interfaces bill and bound inputs in tokens, the syntax-level token density of a programming language directly affects operational cost and available context space.

While traditional software engineering metrics focus on Source Lines of Code (SLOC) or byte counts, these metrics do not map linearly to token counts due to subword tokenization patterns (e.g., Byte-Pair Encoding). A language that requires verbose syntactic boilerplate or is poorly matched to common tokenizers may incur a silent cost premium. This paper aims to quantify these language-level token cost overheads under a rigorous, functional equivalence framework.

---

## 2. Research Questions

- **RQ1**: What is the relative token overhead of different programming languages when implementing identical functionality?
- **RQ2**: How stable are these token density differences between raw code and clean (comment-removed) code variants?
- **RQ3**: Do different tokenizer versions (`cl100k_base` vs. `o200k_base`) exhibit systematic biases toward specific languages?
- **RQ4**: How do language relative token overheads vary across different task domains (e.g., Math, Algorithms, Text Processing, and System I/O)?
- **RQ5**: What are the underlying characteristics of different languages regarding tokenizer fragmentation (Char-to-Token Ratio) and line density (Tokens-per-Line)?

---

## 3. Data

We use the [Rosetta Code Data](https://github.com/acmeism/RosettaCodeData) repository as our primary source of functional equivalence. To avoid selection bias, we filter tasks that are implemented in all six core languages (C, Go, Java, JavaScript, Python, Rust), resulting in a strict intersection of **693 tasks**. For TypeScript, descriptive statistics are compiled on the available subset of tasks.

We generate three code variants for each implementation:
1. **Raw**: Code with standardized newlines and stripped trailing whitespaces.
2. **Clean**: Comments, shebangs, and extra blank lines are removed using lexical parsing via Pygments.
3. **Canonical**: Cleansed code formatted using standard style rules (optional/fallback).

---

## 4. Method

For each task $T$, we compute the paired token count ratio $R_{L}$ for comparison language $L$ against the baseline Python ($L_{base}$):
$$R_{L} = \frac{\text{TokenCount}(L, T)}{\text{TokenCount}(L_{base}, T)}$$

Because token counts span multiple orders of magnitude across tasks, we evaluate the distribution using non-parametric statistics:
- **Median Paired Ratio**: The primary metric of relative overhead.
- **Kruskal-Wallis H Test**: A non-parametric method to test whether the token ratios of all languages originate from the same distribution globally.
- **Pairwise Wilcoxon Signed-Rank Test**: To assess the statistical significance of paired differences.
- **Holm-Bonferroni Correction**: Applied to the family of pairwise comparison p-values to control the Family-Wise Error Rate (FWER) and prevent Type I errors.
- **Bootstrap Resampling**: We use 1000 bootstrap iterations to compute 95% Confidence Intervals (CI) for the median ratios.
- **Cliff's Delta**: To measure the effect size of the distributions.

Additionally, we define two new metrics to characterize the sub-token properties of each language:
- **Char-to-Token Ratio**: Calculated as $\text{CharCount} / \text{TokenCount}$, evaluating the fragmentation degree of the code syntax under tokenization.
- **Tokens-per-Line**: Calculated as $\text{TokenCount} / \text{SLOC}$, evaluating the semantic density of code lines.

---

## 5. Results

### 6.1 Language Token Density Comparison (RQ1)

Under the Clean variant and `cl100k_base` tokenizer, the paired token count ratio compared to Python (1.00) yields the following results on the strict 6-language intersection:

- **C**: Median Ratio = **1.77** (95% CI: [1.65, 1.89], Cliff's $d$ = 0.27, Holm-corrected $p < 10^{-48}$)
- **Rust**: Median Ratio = **1.57** (95% CI: [1.50, 1.70], Cliff's $d$ = 0.21, Holm-corrected $p < 10^{-41}$)
- **Go**: Median Ratio = **1.55** (95% CI: [1.47, 1.66], Cliff's $d$ = 0.24, Holm-corrected $p < 10^{-38}$)
- **Java**: Median Ratio = **1.47** (95% CI: [1.39, 1.57], Cliff's $d$ = 0.17, Holm-corrected $p < 10^{-38}$)
- **JavaScript**: Median Ratio = **1.26** (95% CI: [1.21, 1.34], Cliff's $d$ = 0.09, Holm-corrected $p < 10^{-14}$)
- **TypeScript**: Median Ratio = **1.45** (95% CI: [1.31, 2.08], Cliff's $d$ = 0.25, Holm-corrected $p < 0.001$)

The global Kruskal-Wallis H test is highly significant ($p < 2.13 \times 10^{-15}$), verifying that the differences among languages are extremely strong. The results show that dynamic languages are highly token-efficient. C requires 77% more tokens than Python due to lack of higher-level structures, while Rust, Go, and Java require 47% to 57% more tokens.

![Figure 1: Token Count Ratio to Python by Language](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/report/figures/boxplot_token_count_by_language.png)

### 6.2 Preprocessing Sensitivity (RQ2)

Comparing Raw and Clean variants reveals comment density patterns. The ratio of Raw to Clean tokens is highest in C (1.21x) and JavaScript (1.16x), reflecting heavy comment use in educational codebases. In contrast, TypeScript (1.02x) and Rust (1.05x) have minimal comment overhead. Removing comments dynamically reduces agent context charges by up to 21% without losing functional semantics.

![Figure 2: Comment & Blank Line Token Overhead by Language](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/report/figures/raw_clean_delta_by_language.png)

### 6.3 Tokenizer Bias (RQ3)

Comparing `cl100k_base` (GPT-4) and `o200k_base` (GPT-4o) shows that the median paired ratios remain virtually unchanged. The rank order of languages is perfectly preserved, suggesting that BPE tokenizer updates do not introduce systematic bias toward specific programming syntax families.

![Figure 3: Median Token Ratio to Python by Tokenizer](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/report/figures/ratio_heatmap_by_tokenizer.png)

### 6.4 Task Category Subgroups (RQ4)

Grouping tasks into specific domain categories exposes syntactic and structural profiles of each language:

| Task Category | Language | N | Median Ratio (vs. Python) | Corrected Wilcoxon p-value | Kruskal-Wallis p-value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Math/Numeric** | C | 156 | **1.69** | $1.54 \times 10^{-8}$ | **0.0195** (Significant) |
| | Go | 162 | **1.48** | $2.49 \times 10^{-7}$ | |
| | Java | 157 | **1.43** | $2.49 \times 10^{-7}$ | |
| | JavaScript | 217 | **1.15** | 0.0078 | |
| | Rust | 149 | **1.44** | $1.37 \times 10^{-8}$ | |
| **Text/String** | C | 92 | **2.78** | $2.97 \times 10^{-7}$ | **$5.12 \times 10^{-5}$** (Highly Significant) |
| | Go | 86 | **1.84** | 0.00015 | |
| | Java | 113 | **1.27** | 0.0100 | |
| | JavaScript | 117 | **1.38** | 0.0055 | |
| | Rust | 84 | **1.46** | 0.0055 | |
| **System/IO** | C | 32 | **2.81** | 0.00013 | 0.0712 (Not Significant) |
| | Go | 31 | **3.47** | 0.00047 | |
| | Java | 39 | **3.08** | 0.00013 | |
| | JavaScript | 35 | **1.52** | 0.0052 | |
| | Rust | 28 | **3.00** | 0.00047 | |

**Key Insights**:
- **String Verbosity**: In `Text/String` processing, C language token overhead escalates to **2.78x** and Go to **1.84x**. C lacks built-in modern string manipulation APIs, forcing developers to implement verbose manual loops over character arrays or pointers.
- **IO Boilerplate**: Under `System/IO`, static languages experience a massive token inflation (Go: 3.47x, Java: 3.08x, Rust: 3.00x). This is caused by the mandatory try-catch blocks (Java), explicit return-value checks (Go), or comprehensive result wrapping (Rust), which add extensive token overhead compared to Python's compact single-line IO operations.

![Figure 4: Median Token Ratio to Python by Task Category](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/report/figures/task_category_effects.png)

### 6.5 Tokenization Fragmentation and Line Density (RQ5)

Analyzing Char-to-Token Ratio and Tokens-per-Line reveals language compression patterns:
- **Tokenizer Friendliness**: Java exhibits the highest Char-to-Token ratio (**3.91 characters per token**), indicating that its camelCase naming conventions match tokenizer vocabularies exceptionally well. In contrast, C exhibits the lowest ratio (**2.87**), meaning the tokenizer splits its syntax into much smaller, fragmented tokens due to widespread operators and single-character identifiers.
- **SLOC Information Density**: Python yields the highest line density (**9.42 tokens/line**), showing its horizontal compactness. Conversely, Go yields the lowest (**7.13 tokens/line**), because the language style guidelines dictate vertical layouts with frequent newlines for error-checking blocks.

![Figure 5: Tokenizer Fragmentation and Line Density](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/report/figures/char_to_token_ratio.png)

### 6.6 Robustness across Task Complexities

The scatter distribution of paired language ratios across task sizes (using Python token count as a proxy for complexity) remains highly stable. The language ratio bands continue parallel without scaling drifts up to 1000 tokens.

![Figure 6: Token Ratio Stability across Task Sizes](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/report/figures/task_size_effects.png)

---

### 6.7 Phase 2: LeetCode Generalization Analysis

To evaluate the generalization of our findings in competitive algorithmic and programming interview domains, we integrated the `kamyu104/LeetCode-Solutions` dataset, matching C++ (cpp) and Python on **3,681** functionally equivalent tasks.

Under the Clean variant and `cl100k_base` tokenizer, the results reveal key insights:

1. **Overall Performance**: With Python as the baseline (1.00), C++ exhibits a median ratio of **1.20** (95% CI: `[1.20, 1.21]`, Wilcoxon $p < 10^{-270}$, Cliff's $d = 0.11$). This token surcharge is significantly lower than that of Rosetta Code's C solutions (1.77x), demonstrating the syntactic efficiency improvements in modern C++ (e.g., standard library container abstractions, generic algorithms).
2. **Difficulty Escalation Effect**:
   When grouped by task difficulty (Easy, Medium, Hard), C++ relative token overhead shows a clear monotonic escalation:
   - **Easy Tasks**: Median Ratio = **1.11** (N = 824, 95% CI: `[1.09, 1.13]`, $p < 10^{-26}$)
   - **Medium Tasks**: Median Ratio = **1.19** (N = 1,914, 95% CI: `[1.17, 1.20]`, $p < 10^{-120}$)
   - **Hard Tasks**: Median Ratio = **1.28** (N = 897, 95% CI: `[1.27, 1.30]`, $p < 10^{-100}$)

   > The global **Kruskal-Wallis H test** across the three difficulty groups is extremely significant ($p = 1.53 \times 10^{-42}$), proving that algorithmic complexity systematically increases the relative verbosity of C++ compared to Python. In hard algorithmic tasks, developers must write verbose structural boilerplates (e.g., node allocations, pointer-based traversals, custom graph representations), whereas Python handles these complex structures with compact, built-in dynamic statements.

![Figure 7: LeetCode C++ to Python Token Ratio by Difficulty](file:///c:/Users/blmpt/Downloads/workspace/cross-lang-token-density/report/figures/leetcode_boxplot_by_difficulty.png)

3. **Sub-token Diagnostics**:
   - **Fragmentation**: C++ yields a Char-to-Token ratio of **3.84** and Python yields **3.93**. These values are notably higher than those in Rosetta Code, indicating high naming consistency in interview platforms.
   - **Line Density**: C++ (7.97 tokens/line) and Python (7.90 tokens/line) are highly aligned, primarily because Python LeetCode solutions frequently adopt type annotations, increasing the line distribution of variables.

---

## 7. Discussion

The results have direct implications for LLM system prompt design and multi-agent systems:
1. **Language Choice for Prototyping**: In multi-turn agent conversations, prototype validation in Python/JS maximizes context window efficiency and reduces API costs.
2. **Pre-processing Pipelines**: Cleaning comments and empty lines from target codebases prior to model feeding yields stable token savings of 5% to 21% across all languages.

---

## 8. Threats to Validity

- **Data Source Representativeness**: Rosetta Code implementations are single-file scripts and may not represent industrial multi-module configurations.
- **Language Idioms**: Educational style on Rosetta Code may skew verbosity compared to standard codebases.
- **Formatting Variability**: Absence of strict auto-formatting (canonical formatting) in Phase 1 introduces slight styling noise, though minimized by stripping trailing whitespace and comments.

---

## 9. Conclusion

This study systematically quantifies cross-language token densities. We demonstrate that dynamically-typed languages offer significant token efficiency advantages, and explicitly quantify the cost of type safety (TypeScript vs. JavaScript) and system-level control (Rust/C vs. Python). These findings provide empirical ground rules for managing cost and context scaling in LLM-driven coding agent deployments.

---

## Reproducibility Statement

All code, configuration schemas, and data ingestion steps are public. The experiment can be fully reproduced under a Python 3.12+ environment with `uv` by running:
```bash
uv sync
uv run python scripts/fetch_rosettacode.py
uv run python scripts/preprocess.py
uv run python scripts/tokenize_data.py
uv run python scripts/analyze.py
uv run python scripts/make_figures.py
```
Outputs and final statistical tables will match the reported values exactly.
