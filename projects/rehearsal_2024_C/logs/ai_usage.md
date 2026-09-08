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
| 2026-09-07 | OpenAI Codex | 仓库维护者 | 处理 G2 Round 2 PASS 并启动 S3 | 拉取并核对 `gate_2_review_r2.md` 的 Verdict、Reviewed Commit、S3 边界和 G3 实现检查 | 更新 CURRENT 与决策日志，按冻结合同准备 8 个 Baseline 实验 | Yes | 审核 SHA 与本地提交一致；正式模型输出需由 `math_modeling` 实机运行并在 G3 复核 |

## Current Disclosure Status

- AI 辅助了代码和报告编写；S3/S4 训练分数、OOF 预测和 Bootstrap 数值均由已记录环境中的脚本实际运行产生，不是人工或语言模型填写。
- 尚未生成附件二、三正式测试预测，也未形成最终论文；当前 S4 输出仍为 raw，待 G4/G5 与参赛团队复核。
- 后续每次使用应追加记录，不得覆盖历史条目。
| 2026-09-07 | OpenAI Codex | 仓库维护者 | 实现并执行 S3 全题 Baseline | 读取 G2 Round 2 PASS、冻结模型合同与实验计划；辅助编写特征/模型/验证代码、运行 8 个实验并整理 G3 证据 | 生成 `src/` S3 流水线、`experiments/baseline/`、`results/raw/`、Baseline 报告和 G3 submission | Yes | 在 `math_modeling` 中全量运行；8 份 manifest PASS；数据重建哈希一致；独立复算核心指标、Pareto 和逐候选 OOF 谱系 PASS；测试附件未参与建模，科学解释仍待团队与 Reviewer 复核 |
| 2026-09-08 | OpenAI Codex | 仓库维护者 | 处理 G3 PASS 并启动 S4 | 拉取指定 review commit，读取 G3 审核、S3 报告、冻结配置和 Main Agent S4/G4 协议 | 更新阶段状态，关闭三项 Minor，起草失败分析并按审核优先级准备有限 S4 实验 | Yes | 审核 SHA、Verdict 和授权已核对；代码差异、合成测试及后续真实实验由 `math_modeling` 环境验证，科学结论仍待 G4 Reviewer 复核 |
| 2026-09-08 | OpenAI Codex | 仓库维护者 | 实现、运行并整理 S4 证据 | 读取 G3 PASS、S3失败信号、冻结实验计划与 G4 标准；辅助编写有限 Q1–Q5 实验和验证代码 | 生成主模型/消融/敏感性/Bootstrap raw 输出、两份报告和 G4 submission | Yes | 全部数值由 `math_modeling` 实机脚本产生；12份manifest统一指向干净实现`6accab2…`；独立复算23/23 PASS；附件二、三未参与选择；结论待团队和G4 Reviewer复核 |
| 2026-09-08 | OpenAI Codex | 仓库维护者 | 处理 G4 PASS 并启动 S5 冻结 | 拉取 `gate_4_review.md`，核对固定快照、S5/G5 标准和已批准模型身份；辅助编写一次性预测与独立核验入口 | 更新 CURRENT/日志，准备附件二、三冻结预测、附件四副本和 verified 白名单 | Yes | 所有正式数值将由 `math_modeling` 实机生成并独立复算；测试附件不得用于选择或调参；结果与交接仍待 G5 Reviewer 复核 |
| 2026-09-08 | OpenAI Codex | 仓库维护者 | 修复 S5 预测入口的附件表头兼容 | 首次运行在生成输出前因首个波形表头含单位文字而失败；复用 S1 已验证的表头规则 | 将波形列检查改为“首列以0开头、其余严格为1–1023”，保留失败清单 | Yes | 失败清单显示 `output_hashes={}`；未生成附件二、三预测，不构成重复正式预测 |
| 2026-09-08 | OpenAI Codex | 仓库维护者 | 恢复 S5 附件四后处理 | 第二次运行已产生冻结预测 CSV，但原模板序号列含公式，后处理失败 | 保留第二次失败清单；恢复模式只读复算已有 CSV 且禁止覆写，再将输出副本序号固化为1–400 | Yes | 两份预测 CSV 的恢复前 SHA-256 已记录；恢复不得改变其哈希，不重新训练、调参或选择模型 |
| 2026-09-08 | OpenAI Codex | 仓库维护者 | 修正 S5 恢复授权校验 | 初版恢复保护中的完整 Git SHA 抄录错误，保护在读取预测 CSV 前拒绝执行 | 改为从受控失败清单读取 40 位提交并用 Git 对象库确认其存在；保留拒绝清单 | Yes | 预测文件在拒绝前未读取或改写，SHA-256 仍为原值 |
