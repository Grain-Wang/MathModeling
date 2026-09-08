# S6 Technical Consistency Audit

## 1. Audit Status

- Stage: `S6 — 论文技术一致性与提交准备`
- Entry authorization: G5 `PASS`
- G5 review commit: `5078989`
- Reviewed S5 snapshot: `4a14dfd88259c2a5186da1056c3994eccef5e5f7`
- Current verdict: `IN PROGRESS — TECHNICAL DRAFT CONSISTENT, SUBMISSION PACKAGE INCOMPLETE`
- G6 readiness: `NOT READY`

本审计只确认技术 Markdown 底稿与冻结证据的一致性，不把尚未完成的插图、官方模板排版或 PDF 检查标为通过。

## 2. Frozen Evidence Integrity

自动检查命令：

```powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_C/src/check_s6_consistency.py
```

结果：`9/9 PASS`、`0 failed`。

核验范围：

1. G5 对固定 S5 快照给出 PASS 并授权 S6；
2. S5 原独立验证仍为 84/84 PASS；
3. provenance 登记的 47 个 verified 文件与各自 raw 来源 SHA-256 逐一一致；
4. E001–E015 完整且无越界 Evidence ID；
5. Q1/Q4 冻结模型哈希保持不变；
6. Q2–Q5 核心数字与 verified JSON 一致；
7. 附件二 80 条、附件三 400 条及“无公开真值”边界一致；
8. 技术底稿包含必须披露的外推、关联和优化限制；
9. 技术底稿未出现已登记的直接夸大表述。

报告：`results/raw/s6/consistency_report.json`。

首次运行曾因检查器把模型 SHA-256 中的 `E384`、`E970` 片段误识别为 Evidence ID 而失败。该问题没有涉及模型、数字或 verified 文件；修复为带字母数字边界的正则后通过。原报告保留在 `results/raw/s6/failed_consistency_report_evidence_id_regex.json`。

## 3. Requirement-to-Paper Matrix

| 检查项 | 当前状态 | 证据 / 说明 |
|---|---|---|
| 五个小问逐项作答 | PASS for draft | `paper/technical_draft.md` 第4–8节 |
| 模型定义与冻结实现一致 | PASS for draft | 五份模型合同、`model_freeze.json`、E001–E014 |
| 核心数字来自 verified | PASS | 自动检查 `verified_numeric_claims` |
| 附件二/三预测口径 | PASS | 明确无公开真值，不作为精度证据 |
| Q3 表述强度 | PASS | 统一为“调整后关联，不是因果效应” |
| Q4 外推限制 | PASS | 披露最大 LOMO/LOTO RMSLE |
| Q5 唯一推荐限制 | PASS | 披露 Jaccard=0.39535<0.50，不提供唯一最优工况 |
| 摘要数字与正文一致 | PASS for draft | 由同一 verified 值生成并自动查验关键 token |
| 表格数字一致 | PASS for Markdown tables | Q1/Q4 指定样本与 Q5 代表点均来自交接证据 |
| 正式图表 | PENDING | `figures/` 尚无正式图；受 Skill 与配色确认门槛约束 |
| 参考文献 | PENDING | 仅列出待补方法类别，未伪造条目 |
| 官方 Word 模板 | PENDING | 尚未复制并套用 2024 官方 `.doc` 模板 |
| 匿名、字体、公式、页码 | PENDING | 需在最终 Word/PDF 中检查 |
| 最终 PDF 可打开性 | PENDING | 尚未生成最终 PDF |
| 队伍编号文件名与 MD5 | PENDING / N/A UNTIL PROVIDED | 需要队伍编号和最终 PDF 冻结后执行 |

## 4. Official 2024 Submission Boundary

本轮演练采用 `competition/2024/` 的官方只读原件。最终提交件必须：

- 使用官方封面、摘要页与正文顺序；
- 摘要不超过两页；
- 除首页外不得出现身份信息；
- 导出单个、未压缩 PDF；
- 文件名为“赛题编号 + 队伍编号”；
- MD5 冻结后不得改写对应 PDF；
- 附件如上传，按官方要求使用 RAR、控制在 50 MB 内且匿名。

用户此前明确本仓库不设置独立 AI 政策检查项。本项目保留 `logs/ai_usage.md` 作为过程追溯日志，但不将不存在的独立 AI 政策文件作为本轮 G6 前置条件。

## 5. Current Blocking Items

1. 用户尚未确认正式绘图使用的具体 Skill，且 `guide/figure_color_guide.md` 缺失；
2. 图1、图3、图8要求的 Scientific Illustrator 尚未安装；数值图的 Python plotting Skill 也未指定；
3. 参考文献尚未基于实际引用逐项核验；
4. 技术底稿尚未迁入官方 Word 模板；
5. 最终 PDF、匿名检查、打开检查、文件命名与 MD5 尚未完成。

以上均不推翻 G5，也不要求重训模型；但在关闭前不得提交 G6。

## 6. Next Actions

1. 用户确认图1/3/8与数值图的 Skill 和配色方案；
2. 根据 `work/handoff/figure_handoff.md` 生成可复现正式图；
3. 核验并补齐参考文献；
4. 将技术底稿和正式图迁入官方模板副本；
5. 执行逐页、匿名、数字、图表、附件、PDF 与命名检查；
6. 生成最终提交快照和 `reviews/gate_6_submission.md`。
