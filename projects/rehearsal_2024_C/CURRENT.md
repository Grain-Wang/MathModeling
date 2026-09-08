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

保持 `S5-FREEZE-2024C-V1` 与 `results/verified/` 不变；当前暂停主动制作，等待配图队友和论文队友回交成果。收到后完成导入验收、技术一致性检查、官方提交检查，再决定是否提交 G6。

## Waiting Status

状态：`WAITING_FOR_FIGURE_AND_PAPER_HANDOFF`

开始等待：2026-09-08（Asia/Shanghai）

已向配图队友提供：

- `package_for_deliver/rehearsal_2024_C_figure_handoff.zip`；
- 包内44个说明、verified数据及控制文件；
- 八图任务卡、Evidence ID、禁止表述、交付格式和独立校验脚本。

等待配图队友回交：

1. 图1–图8的最终 PDF/SVG 与宽度至少2000 px的 PNG；
2. 图1/3/8的可编辑矢量源，以及数值图的完整生成脚本；
3. 实际使用的数据切片、Skill/工具名称和版本；
4. 每张图的标题、图注、坐标与单位、Evidence ID 和变更说明；
5. 配色方案已经负责人确认的说明。

等待论文队友回交：

1. 基于2024官方模板的可编辑论文源文件；
2. 插图、表格、公式、符号和单位已经排版的完整正文；
3. 已核验并与正文逐项对应的参考文献；
4. 摘要不超过两页、逐问作答且保留全部证据边界；
5. 可供最终检查的 PDF 候选稿及修改说明。

收到回交后由 Main Agent 执行：

1. 核验交付文件完整性、来源和可复现性；
2. 检查所有图表和论文数字只来自 E001–E015 / `results/verified/`；
3. 复跑 S6 一致性检查，核对公式、单位、摘要、图注和限制表述；
4. 检查官方模板、匿名、PDF渲染、附件、文件名与MD5；
5. 更新技术审计和 final fix log；全部条件满足后创建 `reviews/gate_6_submission.md`。

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
6. 建立 `package_for_deliver/` 绘图交接包：44个说明/verified数据及控制文件、独立校验脚本、SHA-256清单与可直接转发的ZIP；未包含raw、原始附件或模型二进制。

## Known Blockers

- 外部协作阻断：正在等待配图队友和论文队友回交，回交前不提交 G6。
- 配图交付必须说明实际 Skill/工具与配色确认结果；仓库本地仍缺少 `guide/figure_color_guide.md`。
- 论文交付返回前，参考文献、官方模板成稿、最终 PDF、匿名检查、队伍编号文件名与 MD5 仍未完成。
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

Submission：等待配图与论文队友回交；完成导入验收、最终一致性和提交合规检查后创建。

## Last Updated

时间：2026-09-08 +08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
