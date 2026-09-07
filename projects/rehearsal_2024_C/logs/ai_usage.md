# AI Usage Log

本日志记录 AI 在项目中的辅助用途。它不是独立 AI 政策文件；是否披露及如何披露以题目原文和适用竞赛规则为准。任何数学结论、代码执行结果和论文陈述均须由参赛团队复核。

| Time (Asia/Shanghai) | Tool / model | User | Task | Main input or prompt summary | Output use | Adopted | Human verification |
|---|---|---|---|---|---|---|---|
| 2026-09-04 | OpenAI Codex | 仓库维护者 | 仓库赛前可用性检查 | 检查 Agent、Guide、Reference、模板、环境、Competition、项目和 Git | 生成并更新根目录 `readiness_audit.md` | Yes | 用户已确认首轮项目；其余审计证据由工具核验，仍待团队复核 |
| 2026-09-04 | OpenAI Codex | 仓库维护者 | 整理 2024 官方材料 | 仅检索赛事官方平台的规则、提交手册、格式规范和论文模板 | 建立 `competition/2024/` 只读归档和速查 | Yes | 官方域名、附件格式、页数、大小和 SHA-256 已核验 |
| 2026-09-04 21:35 | OpenAI Codex | 仓库维护者 | 初始化 `rehearsal_2024_C` 的 S0 文档 | 读取 Main/Reviewer 协议；只读解析题目、附件、环境和 Git 状态 | 生成 manifest、项目简报、日志、CURRENT 和 G0 submission | Yes | 文件哈希与结构自动复核；科学内容与团队分工待 G0 人工/Reviewer 审核 |
| 2026-09-07 | OpenAI Codex | 仓库维护者 | 处理远程 G0 审核并进入 S1 | 拉取固定快照的 `gate_0_review.md`，核对 PASS、Reviewed Commit 和授权范围 | 更新 CURRENT、决策日志与 readiness audit，并以独立提交推送 | Yes | Git diff、显式暂存路径和远程 push 结果已核验；两处用户 Guide 改动未纳入提交 |
| 2026-09-07 | OpenAI Codex | 仓库维护者 | S1 题意拆解与数据审计 | 读取题目原文、Main/Reviewer G1 标准；辅助编写只读审计脚本和三份 S1 文档 | 生成 `src/s1_data_audit.py`、`results/raw/s1/`、问题分析、数据审计、需求矩阵和 G1 submission | Yes | 脚本在 `math_modeling` 中全量运行；原件前后哈希一致；154 项检查 0 FAIL/5 WARN；题意与科学判断仍待团队和 G1 Reviewer 复核 |

## Current Disclosure Status

- AI 未生成任何训练结果、测试集预测或最终论文结论。
- 本次 AI 输出用于仓库维护、题意结构化、审计代码辅助和审计报告起草；数值均来自脚本运行产物，不是语言模型臆测。
- 后续每次使用应追加记录，不得覆盖历史条目。
