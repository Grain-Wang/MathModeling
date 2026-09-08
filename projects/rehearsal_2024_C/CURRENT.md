# CURRENT

## Project

项目名称：`rehearsal_2024_C`

ACTIVE_PROJECT：`projects/rehearsal_2024_C`

## Selected Problem

题号与名称：2024 年中国研究生数学建模竞赛 C 题《数据驱动下磁性元件的磁芯损耗建模》

比赛类型：往年题模拟

## Current Stage

S5 — 结果核验、冻结与交接（进行中）

## Last Gate

Gate：G4 / Review Round 1

Verdict：`PASS`

Review File：[`reviews/gate_4_review.md`](reviews/gate_4_review.md)

Reviewed Commit：`2309b1e361701be9818544fa18740cd8f5694f2e`

Review Commit：`82504cc9343b437181e66520aee74c56e863d87a`

## Approved Artifacts

- S0–S4 的文档、合同、代码、Baseline、主模型与 raw 证据；
- `work/06_baseline_report.md`、`work/07_failure_analysis.md`、`work/08_main_model_report.md`、`work/09_evidence_report.md`；
- `results/raw/s3/`、`results/raw/baseline/`、`results/raw/main/`；
- `reviews/gate_4_submission.md` 及 G4 固定快照。

G4 已授权把明确白名单内、经 S5 独立复算的证据迁入 `results/verified/`；迁入前仍视为 raw。

## Current Goal

冻结 G4 已批准的 Q1 Logistic 与 Q4 18 特征 HGB；只运行一次附件二、三正式预测；独立复算并将白名单证据写入 `results/verified/`；完成结果登记、绘图/写作交接和 G5 提交。

## Completed S4 Tasks

1. 关闭 G3 三项 Minor：日志历史状态标注、两个直接退化断言、仓库相对命令字段。
2. Q2：二次温度修正 OOF RMSLE=0.20257，相对 Steinmetz 改善43.84%；25°C/90°C 留一温度明显改善。
3. Q4：完整 HGB 相对 Ridge 改善61.82%并通过子组门槛；消融后最终冻结 18 特征 `amplitude_and_condition` HGB，OOF RMSLE=0.07094。
4. Q5：最终 Q4 胜者严格 OOF 谱系闭合，500/500 次工况组 Bootstrap 完成；主 Jaccard=0.39535<0.50，唯一推荐继续禁用。
5. Q3：三组两两交互 log-RMSE=0.32667，相对加性改善4.88%；500/500 次簇 Bootstrap 完成。
6. Q1：相位/幅值一致率和留一材料最低 Macro-F1 均为1.0，保留 shape-only Logistic，不运行无收益空间的树模型。
7. 12 份 manifest 均指向 `6accab2…`、环境 `math_modeling`、实现目录洁净；独立复算 23/23 PASS。

## Known Blockers

- 模型冻结与结果核验当前无流程阻断。
- 正式绘图暂缓：`guide/09_plotting_protocol.md` 要求先指定并确认 Skill，但 `.agents/skills/` 当前为空，且其引用的 `guide/figure_color_guide.md` 不存在。
- Q5 主稳定区域与观测区域 Jaccard 未达0.50，是实证限制，不是运行错误；本轮禁止唯一推荐。

## Forbidden Now

- 继续扩展模型族、搜索空间、随机种子或修改已冻结采用阈值。
- 使用附件二、附件三参与特征选择、调参、模型选择或 Q5 域/阈值制定；两附件只允许冻结预测和只读复算。
- 把 Q1 OOF=1.0 当成未知测试集准确率，把 Q3 调整关联写成因果，或隐藏 Q2/Q4 外推限制。
- 用未施加折支持的敏感性 Jaccard 覆盖 Q5 主 Jaccard 失败，或给出唯一最优工况。
- 把 `results/raw/` 当作论文证据；只有通过 S5 独立核验的白名单文件可进入 `results/verified/`。
- 覆写题目 DOCX、四个原始 XLSX 或任何 Reviewer 审核文件。

## Next Gate

G5 — 结果核验、冻结与交接审核

Verdict：`NOT SUBMITTED`

Submission：待生成 `reviews/gate_5_submission.md`

## Last Updated

时间：2026-09-08 +08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
