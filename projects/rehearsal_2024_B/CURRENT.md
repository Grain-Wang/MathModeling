# CURRENT

## Project

- 项目名称：rehearsal_2024_B
- ACTIVE_PROJECT：projects/rehearsal_2024_B
- 项目状态：ACTIVE
- 题目：2024 年中国研究生数学建模竞赛 B 题《WLAN 组网中网络吞吐量建模》
- 类型：往年题模拟
- 题目版本：本地 DOCX SHA-256 `C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594`

## Current Stage

S3 — 全题 Baseline 闭环已完成。O2=`PROCEED_TO_G3`，G3 提交包已形成；当前停在 G3 等待 Reviewer 审核，S4 尚未获授权。

## Last Gate

- Gate：G2 / Review Round 2
- Verdict：PASS
- Review File：[reviews/gate_2_review_r2.md](reviews/gate_2_review_r2.md)
- Reviewed Commit：`facedf109a9025cb241d9a93074b0467c93143cb`
- Review Commit：`6504c54782dc33e111800b3166e9e1766cab6549`
- Authorization：S2→S3；Next Gate=G3
- Open findings：Critical=0，Major=0，Minor=3，Advisory=1；均不阻塞 S3，按审核时限处理

## S3 Formal Snapshot

- Formal implementation/run commit：`2222cf5f4e17a6dac832c4e65f9c5a60cd01060d`
- Eligible：1,250 AP 行 / 482 严格完整组
- Validation：15 个 primary outer folds / 13 个 source-blind LOSO
- Feature schema：312 个固定顺序特征，2 AP/3 AP 对齐
- Baselines：Q1-B0/B1、Q2-B0/B1A/B1B、Q3-B0/B1/B2，合计 327 fits
- Actual upstream lineage：112 batches，prediction-fit 与 held-out-fit overlap 均为 0
- Formal run：PASS，warning_count=0
- Independent validation：PASS（global 21 / Q1 12 / Q2 19 / Q3 31）
- Official test numeric reads / predictions：0 / 0
- O2：[work/optimization/o2_baseline_diagnosis.md](work/optimization/o2_baseline_diagnosis.md)，决策=`PROCEED_TO_G3`
- G3 submission：[reviews/gate_3_submission.md](reviews/gate_3_submission.md)

## Current Goal

将完整 S3/G3 审核快照推送到远程，然后停在 G3 等待独立审核。未经 G3 PASS，不执行任何 S4 模型改进。

## Current Tasks

1. 完成 S3 结果、报告、日志和 G3 submission 的提交前一致性校验。
2. 将 G3 审核包提交为固定本地 commit。
3. 获得用户推送授权后发布到 `origin/main`。
4. 等待 Reviewer 对固定提交给出 G3 verdict。

## Current Process Blockers

- G3 尚未审核；S4 不得启动。
- 远程发布需要用户明确推送授权。

## Known Limitations / Risks

- Q2 固定 17 类高度不平衡，support 1–2 的类别仍发生预测坍缩；LOSO macro-F1 明显低于 primary。
- Q3 的 3 AP 与 source-blind 外推弱于 2 AP/场景内；Ridge 与物理 eta 存在 primary—LOSO 取舍。
- Q1 的 3 AP MAE 高于 2 AP，但 Q1-B1 仍是唯一冻结的下游上游和回退版本。
- A03 敏感性仅是完整组 OOF 评价排除，不是另一次删组重拟合。
- 原始 CSV 由 `/projects/**/*.csv` 忽略，不进入 Git；远程 Reviewer 需按 manifest 恢复。
- G2 Minor-02 的 ledger 驱动 exactly-once 门禁最迟在 G4/S5 最终入口前完成。
- G2 Minor-03 的唯一全量最终配置规则须在 S4/O3 冻结。

## Forbidden Now

- 在 G3 PASS 前启动 S4、运行 HGB、类别权重、条件分模或任何新候选。
- 扩大 O2 已限定的两个方向、网格或时间盒。
- 在 G4 PASS 与 S5 freeze manifest 完整前解析、推理或人工查看任何官方测试 CSV 数值或预测。
- 使用测试预测外观反馈 O2/O3/S4。
- 修改已批准合同、split registry 核心、正式 Baseline 快照或 Reviewer 文件来迎合结果。
- 将任何 CSV 加入 Git，或将未经 G5 核验的结果迁入 `results/verified/`。

## Next Gate

- Gate：G3
- Status：PENDING REVIEW
- Submission：[reviews/gate_3_submission.md](reviews/gate_3_submission.md)
- Preconditions：八个 Baseline、15 primary folds、13 LOSO、真实 lineage、训练侧 dry-run、O2=`PROCEED_TO_G3`（均已满足）
- Requested transition：S3→S4（仅由未来 G3 PASS 授权）

## Last Updated

- 时间：2026-09-09
- 负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
