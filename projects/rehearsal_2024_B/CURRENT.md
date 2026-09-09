# CURRENT

## Project

- 项目名称：rehearsal_2024_B
- ACTIVE_PROJECT：projects/rehearsal_2024_B
- 项目状态：ACTIVE
- 题目：2024 年中国研究生数学建模竞赛 B 题《WLAN组网中网络吞吐量建模》
- 类型：往年题模拟
- 题目版本：本地 DOCX SHA-256 C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594

## Current Stage

S2 — G2 Review Round 2 修订与正式证据已完成，等待复审。

S2→S3：NOT AUTHORIZED。G2 Round 2 PASS 前不进入 S3，不拟合正式 Baseline。

## Last Gate

- Gate：G2 / Review Round 1
- Verdict：REVISE
- Review File：[reviews/gate_2_review.md](reviews/gate_2_review.md)
- Reviewed Commit：5bf0126d03ad0ce81cdd2c6c594a35c68d0f0ebb
- Review Commit：fe959aff8f53e0add7c473a97f981ffc679e293d
- Major：M2-01 官方测试释放过早；M2-02 下游 inner-CV 的 Q1 嵌套血缘未唯一化

## Approved Artifacts

- G0/R1 与 G1/R2 已 PASS。
- S1 的题意、数据层级、A01–A06、严格身份、跨文件重复、测试封存和 Q3 两级目标/指标合同继续有效。
- G2/R1 认可统一三问主线、Baseline、有限候选、主验证、LOSO、nav 单位和 O1 主体；两项 Major 已按 Round 2 响应提交 Reviewer 关闭。

## G2 Round 2 Evidence

- Response：[work/revisions/gate_2_response.md](work/revisions/gate_2_response.md)
- Submission：[reviews/gate_2_submission_r2.md](reviews/gate_2_submission_r2.md)
- Revised contract implementation commit：43a856642e9405b0c42cf479160f30cd2dae0653
- Formal validation：PASS；worktree before outputs=clean；合同与输入哈希均 PASS
- RF-1：S3 官方测试推理已删除；G4 PASS 后的 S5 freeze manifest 完成前测试文件硬拒绝
- RF-2：下游固定 Q1-B1 Ridge(alpha=1.0) + seq_time_bounded + q1_clip_0_test_dur_v1
- Frozen assignments：outer 1,446；downstream-inner 5,784；primary nested-upstream 11,568
- LOSO：13 splits；inner 5,784；nested-upstream 11,568；全程 source-blind
- Lineage：primary 240 + LOSO 169 = 409 batches；prediction∩fit=0；validation/held-out∩fit=0
- Synthetic tests：Q3 metric PASS；lineage leakage PASS；official-test guard PASS
- Contract artifact hashes：PASS
- Split registry core SHA-256：88B108D181C2EA3A723303DED3D0E64BACEF7FA482F8322712ED97ED020A6C2D
- model_fit_count=0；official_test_numeric_read_count=0；official_test_prediction_count=0

## Current Goal

将完整 G2/R2 固定审核快照推送至 origin/main，然后停在 S2 等待 reviews/gate_2_review_r2.md。

## Current Tasks

1. 完成最终一致性、CSV ignore 和 Git 索引检查。
2. 提交并推送 G2 Review Round 2 审核包。
3. 向 Reviewer 提供最终 origin/main 完整 SHA。
4. 等待复审，不启动 S3。

## Current Process Blockers

- G2/R1 为 REVISE；Round 2 尚未判定，S3 仍被门禁阻止。
- 无其他技术阻塞。

## Known Limitations / Risks

- 原始 CSV 由 /projects/**/*.csv 忽略，远程 Reviewer 需按 manifest 恢复。
- feature_schema.json 只能在 G2 PASS 后的 S3 训练侧 dry-run 生成；当前仅冻结其路径和字段合同。
- 第三层血缘增加计算量，但固定 Ridge 与有限候选保持可行。
- 团队成员实名责任分配尚未提供；environment.yml 尚未完成全新环境 clean rebuild。
- Q2 极稀有类、LOSO 场景偏移及 Q3 有符号指标风险继续按既有合同披露。

## Forbidden Now

- G2 Round 2 PASS 前进入 S3、拟合正式 Baseline、比较性能或调参。
- 在 G4 PASS 和 S5 freeze manifest 完整前解析或推理任何官方测试 CSV 数值。
- 使用测试预测外观反馈 O2/O3/S4。
- 下游使用非 Q1-B1、非 bounded、训练内或无血缘 Q1 特征。
- 让 outer/downstream-inner/nested-upstream/LOSO 的验证组进入相应拟合。
- 修改 reviews/gate_2_review.md 或创建/修改 reviews/gate_2_review_r2.md。
- 上传任何 CSV。

## Next Gate

- Gate：G2 — Review Round 2
- Verdict：PENDING REVIEW
- Response：[work/revisions/gate_2_response.md](work/revisions/gate_2_response.md)
- Submission：[reviews/gate_2_submission_r2.md](reviews/gate_2_submission_r2.md)
- Expected Review：reviews/gate_2_review_r2.md
- Requested transition：S2→S3

## Last Updated

- 时间：2026-09-09T14:59:02+08:00
- 负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
