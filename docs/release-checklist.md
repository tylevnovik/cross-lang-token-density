# 发布检查清单 (Release Checklist)

在进行版本封包和发布前，必须对照本清单逐项校验质量门槛：

- [ ] **自动化测试通过**：
  - 运行 `uv run pytest -q` 无错误。
  - 运行 `uv run ruff check src scripts tests` 无错误或未解决警告。
- [ ] **一键复现成功**：
  - 在干净的虚拟或全新拉取的目录下，使用 `make reproduce`（或命令行集）能从头到尾无阻塞执行完毕。
- [ ] **数据源合规性**：
  - 数据源 commit 成功固定记录在 `data/raw/rosettacode_COMMIT.txt` 中。
  - 所有排除的文件均通过 `git sparse-checkout` 的机制过滤，排除原因归档。
- [ ] **日志完整性**：
  - 所有阶段的关键操作均已被记录在 `research_log/runs/agent_runs.jsonl` 文件中。
- [ ] **分析指标复核**：
  - 主分析结论采用 `six_lang_strict`（六语言严格交集）对齐口径，剔除孤立任务样本。
  - 每项检验包含样本量（N）、中位数比例、置信区间及 Cliff's delta 效应量。
- [ ] **发布文档完备**：
  - `README.md` 包含项目背景、安装命令、复现步骤及研究摘要。
  - `report/report_zh.md` 技术报告中的图表引用路径正确，数据均与最新统计输出对齐。
  - `paper/main.md` 英文论文草稿无遗留 TODO。
