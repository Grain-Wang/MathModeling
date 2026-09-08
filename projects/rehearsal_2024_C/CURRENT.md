# CURRENT

## Project

项目名称：`rehearsal_2024_C`

ACTIVE_PROJECT：`projects/rehearsal_2024_C`

## Selected Problem

题号与名称：2024 年中国研究生数学建模竞赛 C 题《数据驱动下磁性元件的磁芯损耗建模》

比赛类型：往年题模拟

## Current Stage

S6 — 论文技术一致性与提交准备（进行中）

## Last Gate

Gate：G5 / Review Round 1

Verdict：`PASS`

Review File：[`reviews/gate_5_review.md`](reviews/gate_5_review.md)

Reviewed Commit：`4a14dfd88259c2a5186da1056c3994eccef5e5f7`

Review Commit：`5078989`

## Approved Artifacts

- S0–S5 的文档、合同、代码、Baseline、主模型、预测与验证证据；
- `S5-FREEZE-2024C-V1`、84项独立验证、47个 provenance 白名单文件；
- `results/verified/` 的 E001–E015、附件二/三冻结预测及附件四副本；
- `work/10_result_freeze.md`、绘图/写作交接与 G5 固定快照。

G5 已授权基于冻结证据完成论文、图表、技术一致性与提交准备；不授权改变模型、阈值或正式预测。

## Current Goal

保持 `S5-FREEZE-2024C-V1` 与 `results/verified/` 不变，完成正式图表、参考文献、官方模板论文、最终 PDF 与提交一致性检查；全部前置项关闭后提交 G6。

## Completed S4 Tasks

1. 关闭 G3 三项 Minor：日志历史状态标注、两个直接退化断言、仓库相对命令字段。
2. Q2：二次温度修正 OOF RMSLE=0.20257，相对 Steinmetz 改善43.84%；25°C/90°C 留一温度明显改善。
3. Q4：完整 HGB 相对 Ridge 改善61.82%并通过子组门槛；消融后最终冻结 18 特征 `amplitude_and_condition` HGB，OOF RMSLE=0.07094。
4. Q5：最终 Q4 胜者严格 OOF 谱系闭合，500/500 次工况组 Bootstrap 完成；主 Jaccard=0.39535<0.50，唯一推荐继续禁用。
5. Q3：三组两两交互 log-RMSE=0.32667，相对加性改善4.88%；500/500 次簇 Bootstrap 完成。
6. Q1：相位/幅值一致率和留一材料最低 Macro-F1 均为1.0，保留 shape-only Logistic，不运行无收益空间的树模型。
7. 12 份 manifest 均指向 `6accab2…`、环境 `math_modeling`、实现目录洁净；独立复算 23/23 PASS。

## Completed S5 Tasks

1. 冻结 Q1 Logistic 与 Q4 18特征 HGB 的模型文件、参数、特征 schema、输入和模型 SHA-256。
2. 附件二完成80条冻结分类：正弦20、三角44、梯形16；预测 CSV 在受控恢复中未覆写。
3. 附件三完成400条冻结损耗预测，全部正有限；附件四副本的80+400个输出映射通过复算。
4. 原始题目与四个 XLSX 的冻结 SHA-256 保持不变；测试附件未参与特征、调参或模型选择。
5. 独立验证84/84 PASS；47个明确白名单文件由 raw 按同 SHA-256 晋级 `results/verified/`。
6. 建立 E001–E015 结果登记、model freeze、provenance、figure handoff 与 writing handoff。

## Completed S6 Start Tasks

1. 拉取并核对 G5 Round 1 PASS，确认 `S5 -> S6` 已获授权。
2. 建立 `paper/technical_draft.md`，逐问写入模型、公式、结果、Evidence ID 与强制限制。
3. 建立只读 `src/check_s6_consistency.py`；在 `math_modeling` 中检查 G5 授权、47个 provenance 哈希、E001–E015、冻结模型和核心论文数字。
4. 修复 Evidence ID 正则对 SHA-256 片段的误报并保留首次失败报告；当前一致性结果为 9/9 PASS。
5. 建立 `work/11_technical_consistency_audit.md` 和 `work/revisions/final_fix_log.md`，区分技术底稿通过项与 G6 未完成项。

## Known Blockers

- 正式绘图暂缓：`guide/09_plotting_protocol.md` 要求先指定并确认 Skill，但 `.agents/skills/` 当前为空，且其引用的 `guide/figure_color_guide.md` 不存在。
- 图1/3/8要求的 Scientific Illustrator 尚未安装，数值图使用的具体 plotting Skill 尚未指定。
- 参考文献、官方 Word 模板排版、最终 PDF、匿名检查、队伍编号文件名与 MD5 尚未完成。
- Q5 Jaccard=0.39535<0.50 是必须保留的实证限制，不是待“修好”的运行错误。

## Forbidden Now

- 修改冻结模型、数据切分、采用阈值、附件二/三正式预测或 `results/verified/`。
- 从 `results/raw/` 选择论文数字，或让附件二、附件三参与任何重新选模与调参。
- 把 Q1 OOF=1.0 当成未知测试准确率，把 Q3 调整关联写成因果，或隐藏 Q2/Q4 外推限制。
- 用敏感性结果覆盖 Q5 主 Jaccard 失败，或把代表点包装成唯一/全局最优工况。
- 在未确认 Skill 前生成正式图，或把当前 Markdown 技术底稿称为可提交论文。
- 覆写题目 DOCX、四个原始 XLSX、官方模板原件或任何 Reviewer 审核文件。

## Next Gate

G6 — 论文技术一致性与提交准备审核

Verdict：`NOT SUBMITTED / NOT READY`

Submission：待正式图、参考文献、官方模板与最终 PDF 全部完成后创建。

## Last Updated

时间：2026-09-08 +08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
