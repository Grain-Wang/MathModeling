# AI Usage Log

本日志记录 AI 在项目中的辅助用途。它不是独立 AI 政策文件；是否披露及如何披露以题目原文和适用竞赛规则为准。任何数学结论、代码执行结果和论文陈述均须由参赛团队复核。

| Time (Asia/Shanghai) | Tool / model | User | Task | Main input or prompt summary | Output use | Adopted | Human verification |
|---|---|---|---|---|---|---|---|
| 2026-09-04 | OpenAI Codex | 仓库维护者 | 仓库赛前可用性检查 | 检查 Agent、Guide、Reference、模板、环境、Competition、项目和 Git | 生成并更新根目录 `readiness_audit.md` | Yes | 用户已确认首轮项目；其余审计证据由工具核验，仍待团队复核 |
| 2026-09-04 | OpenAI Codex | 仓库维护者 | 整理 2024 官方材料 | 仅检索赛事官方平台的规则、提交手册、格式规范和论文模板 | 建立 `competition/2024/` 只读归档和速查 | Yes | 官方域名、附件格式、页数、大小和 SHA-256 已核验 |
| 2026-09-04 21:35 | OpenAI Codex | 仓库维护者 | 初始化 `rehearsal_2024_C` 的 S0 文档 | 读取 Main/Reviewer 协议；只读解析题目、附件、环境和 Git 状态 | 生成 manifest、项目简报、日志、CURRENT 和 G0 submission | Yes | 文件哈希与结构自动复核；科学内容与团队分工待 G0 人工/Reviewer 审核 |
| 2026-09-07 | OpenAI Codex | 仓库维护者 | 处理远程 G0 审核并进入 S1 | 拉取固定快照的 `gate_0_review.md`，核对 PASS、Reviewed Commit 和授权范围 | 更新 CURRENT、决策日志与 readiness audit，并以独立提交推送 | Yes | Git diff、显式暂存路径和远程 push 结果已核验；两处用户 Guide 改动未纳入提交 |
| 2026-09-07 | OpenAI Codex | 仓库维护者 | S1 题意拆解与数据审计 | 读取题目原文、Main/Reviewer G1 标准；辅助编写只读审计脚本和三份 S1 文档 | 生成 `src/s1_data_audit.py`、`results/raw/s1/`、问题分析、数据审计、需求矩阵和 G1 submission | Yes | 脚本在 `math_modeling` 中全量运行；原件前后哈希一致；154 项检查 0 FAIL/5 WARN；题意与科学判断仍待团队和 G1 Reviewer 复核 |
| 2026-09-07 | OpenAI Codex | 仓库维护者 | 处理 G1 PASS 并设计 S2 方案 | 读取 G1 审核、S2/G2 标准及相关 Reference；辅助定义统一数据流、五问合同、实验队列和机器配置 | 生成总体方案、共享合同、Q1–Q5 合同、实验计划、冻结 JSON 和 G2 submission | Yes | 合同章节、JSON/输入哈希、链接和计划 API 已自动核验；未训练模型；科学选择待团队与 G2 Reviewer 复核 |
| 2026-09-07 | OpenAI Codex | 仓库维护者 | 响应 G2 Round 1 REVISE | 读取固定快照审核意见；用户确认“实测工况点 + 严格 OOF + 折级区域 + 簇 Bootstrap”方向 | 修订 Q4/Q5 合同、总体方案、实验计划、冻结配置并起草 Round 2 响应 | Yes | 5×14 章节、输入/合同哈希、Q5 阈值、链接和 Git 边界均通过静态检查；未实现或运行 S3，科学阈值仍待 G2 Reviewer 复审 |

## Current Disclosure Status

- AI 未生成任何训练结果、测试集预测或最终论文结论。
- 本次 AI 输出用于仓库维护、题意结构化、审计代码辅助、S2 建模方案与实验合同起草；尚未产生模型分数或预测，S1 数值均来自脚本运行产物。
- 后续每次使用应追加记录，不得覆盖历史条目。
