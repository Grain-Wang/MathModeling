# AI Usage Log

本日志记录 AI 在项目中的辅助用途。它不是独立 AI 政策文件；是否披露及如何披露以题目原文和适用竞赛规则为准。任何数学结论、代码执行结果和论文陈述均须由参赛团队复核。

| Time (Asia/Shanghai) | Tool / model | User | Task | Main input or prompt summary | Output use | Adopted | Human verification |
|---|---|---|---|---|---|---|---|
| 2026-09-04 | OpenAI Codex | 仓库维护者 | 仓库赛前可用性检查 | 检查 Agent、Guide、Reference、模板、环境、Competition、项目和 Git | 生成并更新根目录 `readiness_audit.md` | Yes | 用户已确认首轮项目；其余审计证据由工具核验，仍待团队复核 |
| 2026-09-04 | OpenAI Codex | 仓库维护者 | 整理 2024 官方材料 | 仅检索赛事官方平台的规则、提交手册、格式规范和论文模板 | 建立 `competition/2024/` 只读归档和速查 | Yes | 官方域名、附件格式、页数、大小和 SHA-256 已核验 |
| 2026-09-04 21:35 | OpenAI Codex | 仓库维护者 | 初始化 `rehearsal_2024_C` 的 S0 文档 | 读取 Main/Reviewer 协议；只读解析题目、附件、环境和 Git 状态 | 生成 manifest、项目简报、日志、CURRENT 和 G0 submission | Yes | 文件哈希与结构自动复核；科学内容与团队分工待 G0 人工/Reviewer 审核 |

## Current Disclosure Status

- AI 未生成任何训练结果、测试集预测或最终论文结论。
- 本次 AI 输出仅用于仓库维护、资料整理和项目初始化。
- 后续每次使用应追加记录，不得覆盖历史条目。
