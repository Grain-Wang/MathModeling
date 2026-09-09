# CURRENT

## Project

- 项目名称：rehearsal_2024_B
- ACTIVE_PROJECT：`projects/rehearsal_2024_B`
- 项目状态：ACTIVE
- 题目：2024 年中国研究生数学建模竞赛 B 题，WLAN 组网中网络吞吐量建模
- 类型：往年题模拟
- 题目版本：本地 DOCX SHA-256 `C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594`

## Current Stage

S4 — 主模型改进与证据构建已完成。O3=`FREEZE_CANDIDATE`，G4 submission 已形成；当前停在 G4 等待 Reviewer，不得自行进入 S5。

## Last Gate

- Gate：G3 / Review Round 1
- Verdict：PASS
- Review File：[reviews/gate_3_review.md](reviews/gate_3_review.md)
- Reviewed Commit：`e352c4233bb6a974e974ab697481b712a9c83d0b`
- Review Commit：`a5433257bf94ab651a53b86244d8a86edc72f9e4`
- Authorization：S3→S4；Next Gate=G4
- Findings：Critical=0，Major=0，Minor=3，Advisory=2

## S4 Formal Snapshot

- Formal implementation/run commit：`329566748d594e877b57f99cfdddf6796a584d81`
- Formal status：PASS
- Runtime / model fits / warnings：4,791.800 s / 1,751 / 0
- Population：1,250 AP rows / 482 complete groups
- Validation：15 primary outer folds / 13 source-blind LOSO
- Actual Q1 lineage：448 batches；两个 overlap total 均为 0
- Independent validation：74/74 checks PASS
- Official-test numeric read / prediction：0 / 0

## Frozen Final Candidate

| Question | Frozen model | Status |
|---|---|---|
| Q1 | Q1-B1 Ridge, bounded v1 | unchanged |
| Q2 | Q2-B1A LogisticRegression(C=1.0), no Q1 | HGB 未达 +0.02，回退 |
| Q3 | Q3-M1-HGB-UNIFIED, physics-residual Q3-C3 | promoted |

Q3-C3 参数：learning_rate=0.05，max_leaf_nodes=15，l2_regularization=1.0，`ap_count_split=false`。system 严格等于 bounded AP 预测之和。

## O3 Decision

- Decision：`FREEZE_CANDIDATE`
- Q2：unweighted gain=+0.013736；唯一 weighted gain=+0.019002；均未达 +0.02，停止并回退 Q2-B1A。
- Q3：unified primary S=0.550330，相对 Q3-B1 改善 31.60%，3/3 repeats 改善并通过 bias guards。
- AP-count split：primary S=0.573131、LOSO S=0.685496；按冻结 primary 规则不保留。
- 选择已关闭，不新增候选、网格、权重、阈值或模型族。

## Completed Deliverables

- `work/07_failure_analysis.md`
- `work/08_main_model_report.md`
- `work/09_evidence_report.md`
- `work/optimization/o3_freeze_decision.md`
- `experiments/main/`, `comparison/`, `ablation/`, `sensitivity/`, `robustness/`
- `results/raw/main/`
- `reviews/gate_4_submission.md`

## Known Limitations / Risks

- Q2 support=1–2 类别仍不能形成强可学习性结论，source-blind macro-F1 仍低。
- Q3 aggregate primary/LOSO 改善，但最差 held-out source 的 S=2.159764，不能声称所有来源一致鲁棒。
- AP-count split 的 LOSO aggregate 优于 unified，但冻结 primary 指标选择 unified；该取舍已披露。
- A03 只是 whole-group evaluation-exclusion diagnostic，不是删组重拟合鲁棒性。
- `basic__ap_count` 继续使用所有 S4 候选一致的 numeric binary 2/3。
- G2 遗留的 exactly-once release ledger 必须在 G4 PASS 后、S5 正式测试入口前完成。

## Forbidden Now

- 在 Reviewer 给出 G4 PASS 前进入 S5 或执行官方测试推理。
- 在 G4 PASS 和 S5 freeze manifest 完整前解析、推理或人工查看官方测试 CSV 数值/预测。
- 修改唯一冻结候选、全量配置规则、17 类标签、split registry、Q3 指标、bounded 口径或 AP→system 求和规则。
- 新增 Q1-HGB、第二种类别权重、更多 HGB 网格、AP-count 分模或独立 system head。
- 将任何结果写入 `results/verified/`，或覆盖 `results/raw/baseline/`。
- 修改 Reviewer 文件来迎合结果。

## Next Gate

- Gate：G4
- Status：READY FOR REVIEW / PENDING REVIEWER
- Submission：[reviews/gate_4_submission.md](reviews/gate_4_submission.md)
- Requested transition：S4→S5
- S5 entry condition：未来 G4 review 明确 PASS

## Last Updated

- 时间：2026-09-09
- 负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
