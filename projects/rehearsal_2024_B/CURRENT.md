# CURRENT

## Project

- 项目名称：rehearsal_2024_B
- ACTIVE_PROJECT：`projects/rehearsal_2024_B`
- 项目状态：ACTIVE
- 题目：2024 年中国研究生数学建模竞赛 B 题，WLAN 组网中网络吞吐量建模
- 类型：往年题模拟
- 题目版本：本地 DOCX SHA-256 `C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594`

## Current Stage

S6 — 技术一致性审计、论文工程与最终提交准备进行中。G5=`PASS`，已授权 S5→S6；G5 的发布后绑定/语义补强已 29/29 PASS，verified-only 配图交接包已经形成。当前可移交配图与论文队友，但正式图、论文源文件、匿名/格式核验和最终 PDF 尚未完成，因此 G6=`NOT READY`。

## Last Gate

- Gate：G5 / Review Round 1
- Verdict：PASS
- Review File：[reviews/gate_5_review.md](reviews/gate_5_review.md)
- Reviewed Commit：`cb1e9276fc5054e7f912b00e54ab0b4292f3d464`
- Review Commit：`3862fee66a3c1ca362202b8d5d9e8b5d7eb2137b`
- Authorization：S5→S6；Next Gate=G6
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

## S5 Formal Snapshot

- S5 implementation commit：`474acb71dfc0bcaa27e6cca908c2243efa65660f`
- Pre-release freeze commit：`473a8ad8bf04cfa7d62511dadbe620f3a6ba8570`
- Freeze manifest SHA-256：`A4AA45A0491C35C1D816164AADABB20998E9984D7521AFDE55D01A8B027E5E6D`
- Independent selection/promotion reconstruction：6/6 PASS
- Release ID：`S5-A4AA45A0491C-20260911T110151+0800`
- Runtime / full-data fits / warnings：29.320 s / 4 / 0
- Training / official-test numeric reads：13 / 4
- Exactly-once successful release count：1；第二次 release guard 硬失败
- Post-release validation：10 项跨产物检查 + 12 项逐文件 schema/order 检查 PASS

## S6 Current Snapshot

- G5 findings：Critical=0，Major=0，Minor=3，Advisory=2。
- Post-release binding/semantic attestation：29/29 PASS；official-test CSV numeric reads=0；model inference=0。
- Figure input snapshot SHA-256：`BE2A9AFEAA836000ACAFCA897B516C8DCFB621CA5B006DFD9008C9D14E44CFA5`。
- Figure handoff ZIP SHA-256：`DAA0F01BDC26722275941E865222EB48481E6B8F9E7E7D70D676004A1F5E411B`。
- Handoff manifest：registry、figure/writing handoff、result freeze、attestation 与配图包均已登记；正式图数据、论文源文件和 PDF 仍为 PENDING。
- Overall：`S6_HANDOFF_READY_G6_NOT_READY`。

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

- S4：`work/07_failure_analysis.md`、`08_main_model_report.md`、`09_evidence_report.md`、`work/optimization/o3_freeze_decision.md`
- `results/verified/freeze_manifest.json` 与 SHA-256 sidecar
- `results/verified/selection_reconstruction.json`、`verified_metrics.json`、`result_registry.md`
- `results/verified/final_release_verification.json` 与四个 `official_*.jsonl`
- `results/raw/final/test_release_ledger.json`、release manifest、3 个模型文件与 4 个输出文件
- `work/10_result_freeze.md`
- `work/handoff/figure_handoff.md`
- `work/handoff/writing_handoff.md`
- `src/s5_validation.py`、`src/s5_release.py`、`configs/s5_output_schema.json`
- `reviews/gate_5_submission.md`
- `results/verified/post_release_binding_attestation.json`、`s6_handoff_manifest.json`
- `work/11_technical_consistency_audit.md`、`work/revisions/gate_5_followup.md`、`final_fix_log.md`
- `package_for_deliver/figure_handoff_2024_B/`
- `package_for_deliver/rehearsal_2024_B_figure_handoff.zip`
- `src/s6_post_release_attestation.py`、`src/s6_figure_package.py`

## Known Limitations / Risks

- Q2 support=1–2 类别仍不能形成强可学习性结论，source-blind macro-F1 仍低。
- Q3 aggregate primary/LOSO 改善，但最差 held-out source 的 S=2.159764，不能声称所有来源一致鲁棒。
- AP-count split 的 LOSO aggregate 优于 unified，但冻结 primary 指标选择 unified；该取舍已披露。
- A03 只是 whole-group evaluation-exclusion diagnostic，不是删组重拟合鲁棒性。
- `basic__ap_count` 继续使用所有 S4 候选一致的 numeric binary 2/3。
- 官方测试输出无标签，只能作为部署结果，不能作为性能证据。
- 本地 CSV 只能声明与 S0 manifest 一致，尚无官方压缩包 URL 与 archive hash。

## Forbidden Now

- 未确认具体 plotting skill 前生成正式图，或让配图/论文引用未登记 Evidence ID 的 raw 数值。
- 正式图、论文源文件和 PDF 尚未回传前提交 G6 或宣称最终交付完成。
- 再次执行官方测试释放；真实 ledger 已有一次成功记录，机器门禁必须继续硬拒绝。
- 修改唯一冻结候选、全量配置规则、17 类标签、split registry、Q3 指标、bounded 口径或 AP→system 求和规则。
- 新增 Q1-HGB、第二种类别权重、更多 HGB 网格、AP-count 分模或独立 system head。
- 根据官方无标签预测的范围、比例或人工观感返回 O2/O3/S4 调模；或修改 Reviewer 文件迎合结果。

## Next Gate

- Gate：G6
- Status：NOT READY / PENDING FIGURE AND PAPER OUTPUTS
- Submission：尚未创建
- Requested transition：S6→FINAL SUBMISSION
- G6 entry condition：正式图与图数据快照、论文源文件、匿名/格式/PDF 检查全部完成，并写入 final-delivery manifest

## Last Updated

- 时间：2026-09-11
- 负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
