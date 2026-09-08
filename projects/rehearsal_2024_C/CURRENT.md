# CURRENT

## Project

项目名称：`rehearsal_2024_C`

ACTIVE_PROJECT：`projects/rehearsal_2024_C`

## Selected Problem

题号与名称：2024 年中国研究生数学建模竞赛 C 题《数据驱动下磁性元件的磁芯损耗建模》

比赛类型：往年题模拟

## Current Stage

S4 — 主模型改进与证据构建（已完成，等待 G4 审核）

## Last Gate

Gate：G3 / Review Round 1

Verdict：`PASS`

Review File：[`reviews/gate_3_review.md`](reviews/gate_3_review.md)

Reviewed Commit：`17cefbfe7bda13fa97f2eb19decc1abd02529597`

Review Commit：`076a7a3070dbd4b10c164b15bd4e02cf460368c4`

## Approved Artifacts

- S0–S3 已批准文档、合同、代码、Baseline 与原始证据；
- `work/06_baseline_report.md`；
- `results/raw/s3/` 和 `results/raw/baseline/`；
- `reviews/gate_3_submission.md`。

S4 的实现、报告和 `results/raw/main/` 尚待 G4 审核，不列为 approved。所有结果仍是 raw，`results/verified/` 未写入。

## Current Goal

保持实现提交 `6accab2c0d9dbd8fbc0d362d9c60f9161f1e1901` 和其上生成的 12 份 S4 run manifest 冻结，将有限改进、同折比较、消融、敏感性、稳健性及独立复算提交 G4；在 G4 PASS 前不进入 S5。

## Completed S4 Tasks

1. 关闭 G3 三项 Minor：日志历史状态标注、两个直接退化断言、仓库相对命令字段。
2. Q2：二次温度修正 OOF RMSLE=0.20257，相对 Steinmetz 改善43.84%；25°C/90°C 留一温度明显改善。
3. Q4：完整 HGB 相对 Ridge 改善61.82%并通过子组门槛；消融后最终冻结 18 特征 `amplitude_and_condition` HGB，OOF RMSLE=0.07094。
4. Q5：最终 Q4 胜者严格 OOF 谱系闭合，500/500 次工况组 Bootstrap 完成；主 Jaccard=0.39535<0.50，唯一推荐继续禁用。
5. Q3：三组两两交互 log-RMSE=0.32667，相对加性改善4.88%；500/500 次簇 Bootstrap 完成。
6. Q1：相位/幅值一致率和留一材料最低 Macro-F1 均为1.0，保留 shape-only Logistic，不运行无收益空间的树模型。
7. 12 份 manifest 均指向 `6accab2…`、环境 `math_modeling`、实现目录洁净；独立复算 23/23 PASS。

## Known Blockers

- 进入 S5 的唯一流程阻断：G4 尚未返回 PASS。
- Q5 主稳定区域与观测区域 Jaccard 未达0.50，是实证限制，不是运行错误；本轮禁止唯一推荐。

## Forbidden Now

- 在 G4 结论前继续扩展模型族、搜索空间、随机种子或修改采用阈值。
- 使用附件二、附件三参与特征选择、调参、模型选择或 Q5 域/阈值制定。
- 把 Q1 OOF=1.0 当成未知测试集准确率，把 Q3 调整关联写成因果，或隐藏 Q2/Q4 外推限制。
- 用未施加折支持的敏感性 Jaccard 覆盖 Q5 主 Jaccard 失败，或给出唯一最优工况。
- 把 `results/raw/` 当作 verified 论文证据，或在 G4/G5 前写入 `results/verified/`。
- 覆写题目 DOCX、四个原始 XLSX 或任何 Reviewer 审核文件。

## Next Gate

G4 — 主模型改进与证据构建审核

Verdict：`SUBMITTED / PENDING REVIEW`

Submission：[`reviews/gate_4_submission.md`](reviews/gate_4_submission.md)

## Last Updated

时间：2026-09-08 +08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充