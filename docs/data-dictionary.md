# 数据字典

## SnippetRecord (代码片段记录)

`SnippetRecord` 代表某个任务在某种编程语言下的一个源代码实现。

- `record_id`: 稳定的唯一标识符，格式为：`{dataset}:{task_id}:{language}:{implementation_index}`。
- `dataset`: 源数据集标识，如 `rosettacode`。
- `dataset_version`: 数据集版本标记，优选 git commit SHA。
- `source_uri`: 上游仓库或 API 的 URL。
- `source_path`: 上游数据源内部的相对路径。
- `task_id`: 规范化后的任务 ID。
- `task_name`: 易读的任务名称。
- `task_category`: 任务类别之一，包括 `algorithm`, `io`, `text`, `data_structure`, `numeric`, `system`, `unknown`。
- `language`: 来自 `configs/languages.yaml` 的规范化编程语言 ID。
- `language_version`: 编程语言的版本（如果可用）。
- `implementation_index`: 实现索引（如果某种语言对同一个任务有多个实现，从 0 开始递增）。
- `equivalence_group_id`: 用于成对对比的等价性组 ID。
- `equivalence_confidence`: 等价性置信度，取值范围为 `source_aligned`, `test_aligned`, `human_reviewed` 或 `weak_candidate`。
- `license`: 数据源的许可证声明。
- `code_raw`: 原始的源代码字符串。
- `code_raw_sha256`: 原始代码的 SHA-256 哈希值。
- `ingested_at`: 数据采集的 UTC 时间戳。

## CodeVariantRecord (代码变体记录)

`raw`、`clean` 和 `canonical` 变体分别存储，以便分析可以比较预处理对 Token 密度的敏感度。

- `variant_id`: 稳定的唯一变体标识，格式为：`{record_id}:{variant}`。
- `record_id`: 对应的 Snippet 记录 ID。
- `variant`: 变体类型，取值范围为 `raw`、`clean` 或 `canonical`。
- `code`: 变体对应的处理后代码字符串。
- `char_count`: 代码字符数（必须大于或等于 0）。
- `byte_count`: 代码字节数（必须大于或等于 0）。
- `sloc`: 源代码行数（Source Lines of Code，必须大于或等于 0）。
- `cleaner`: 所用清洗器的名称/版本。
- `cleaner_status`: 清洗状态，取值范围为 `ok`、`warning`、`failed` 或 `unavailable`。
- `cleaner_warnings`: 清洗过程中的警告信息列表。

## TokenCountRecord (Token 计数记录)

记录使用特定分词器计算的 Token 计数信息。

- `token_count_id`: 稳定的唯一 Token 计数标识，格式为：`{variant_id}:{tokenizer_name}`。
- `variant_id`: 对应的代码变体记录 ID。
- `tokenizer_provider`: 分词器提供方，如 `openai`。
- `tokenizer_name`: 分词器名称，如 `cl100k_base`、`o200k_base`。
- `tokenizer_package`: 使用的 Python 包名，如 `tiktoken`。
- `tokenizer_package_version`: 运行统计时锁定的包版本。
- `model_reference`: 关联的模型引用（如果适用）。
- `token_count`: 计算得出的 Token 数量（必须大于或等于 0）。
- `counted_at`: 统计计算的 UTC 时间戳。

## AgentRunLog (Agent 运行日志)

记录 Agent 在研究中的每次实质性操作，使科研流程可审计、可复现。

- `run_id`: 运行唯一 ID。
- `timestamp`: 运行开始的 UTC 时间戳。
- `phase`: 研究所处阶段。
- `actor`: 执行者角色，取值范围为 `coding_agent`、`human` 或 `hybrid`。
- `model`: 使用的 AI 模型名称（如果适用）。
- `task`: 本次执行的任务描述。
- `prompt_hash`: 所用 Prompt 的哈希值。
- `input_artifacts`: 输入产物文件路径列表。
- `commands`: 执行的命令列表。
- `output_artifacts`: 生成的输出产物文件路径列表。
- `decisions`: 做出的科研或工程决策列表。
- `uncertainties`: 可能影响数据质量或结论的潜在不确定性。
- `human_intervention`: 人工介入或审核记录。
- `reflection_path`: 对应的反思日志 Markdown 文件路径。
