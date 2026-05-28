# 功能等价性判定标准

## 置信度级别 (Confidence Levels)

- `source_aligned`: 同一上游任务页面或基准问题下的实现；无需额外的人工审核。
- `test_aligned`: 针对各语言实现执行了相同的单元测试或输入/输出契约（I/O contract）校验。
- `human_reviewed`: 经过人工审查，确认各语言的代码片段具有可比的算法意图。
- `weak_candidate`: 通过搜索或关键词匹配生成的候选配对；默认在主要研究结论中予以排除。

## 主要分析纳入标准 (Primary Analysis Inclusion)

主要成对分析仅纳入满足以下条件的等价性组：

1. 对于所有要求的编程语言（如核心六语言），均有至少一个实现记录。
2. 属于 `source_aligned`、`test_aligned` 或 `human_reviewed` 置信度级别。
3. 未被标记为解析器失败、无法读取的生成产物或非代码的说明性文本。

## 敏感性分析 (Sensitivity Analysis)

通过以下方式运行敏感性分析，以评估结论的稳健性：

1. 排除多文件实现的项目。
2. 仅保留每种语言有且仅有一个实现的等价性组。
3. 分别对比原始变体 (raw) 和清洗后变体 (clean) 的表现。
4. 分别运行六语言严格交集（不含 TypeScript）和七语言交集（包含 TypeScript）的数据口径。
