# CURRENT

## Project

- 项目名称：rehearsal_2024_B
- ACTIVE_PROJECT：projects/rehearsal_2024_B
- 项目状态：ACTIVE
- 题目：2024 年中国研究生数学建模竞赛 B 题《WLAN组网中网络吞吐量建模》
- 类型：往年题模拟
- 题目版本：本地 DOCX SHA-256 C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594

## Current Stage

S2 — G2 Review Round 1 修订中。

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
- G2/R1 认可统一三问主线、Baseline、有限候选、主验证、LOSO、nav 单位和 O1 主体；只要求局部修复两项 Major。

## Current Revision

- RF-1：S3 的官方测试 Baseline 推理已删除；唯一释放点冻结为 G4 PASS 后的 S5 freeze manifest 完成后一次最终推理。
- RF-1 machine guard：S2/S3/O2/S4/O3/G4_REVIEW 的 run manifest 若含四个官方测试文件即硬失败。
- RF-2 upstream：Q2/Q3 统一使用 Q1-B1 Ridge(alpha=1.0) 的 seq_time_bounded，postprocess=q1_clip_0_test_dur_v1。
- RF-2 nested lineage：每个 downstream inner-training 内增加第三层 3-fold Q1 OOF；inner-validation 不进入任何相关上游拟合。
- LOSO：held-out source 从预处理、上游/下游拟合与选择中全部排除。
- Minor：按 repeat 先算指标再平均；group bootstrap 保留同组全部 repeat；Q1/Q3 bounded 为主、raw 仅审计；六份人工合同 SHA 已锁。
- 当前只校验预检：PASS；11,568 个 primary nested-upstream 分配、11,568 个 LOSO nested-upstream 分配、409 个 lineage batches；模型拟合和官方测试数值读取均为 0。

## Current Goal

从新的干净修订提交重新生成 S2 合同、split/lineage 与负向门禁证据，逐项响应 RF-1/RF-2，并提交 G2 Review Round 2。

## Current Tasks

1. 登记 G2/R1 REVISE 和修订决策。
2. 创建干净的 G2/R2 合同实现提交。
3. 从该提交正式运行零训练验证器并更新 results/raw/s2。
4. 创建 work/revisions/gate_2_response.md 与 reviews/gate_2_submission_r2.md。
5. 完成全套校验、提交、推送，并停在 S2 等待复审。

## Current Process Blockers

- G2/R1 为 REVISE；在 Round 2 PASS 前，S3 和任何正式模型训练均被门禁阻止。
- 无其他技术阻塞。

## Known Limitations / Risks

- 原始 CSV 由 /projects/**/*.csv 忽略，远程 Reviewer 需按 manifest 恢复。
- 团队成员实名责任分配尚未提供，最终交付前必须补齐。
- environment.yml 尚未完成全新环境 clean rebuild。
- Q2 极稀有类、LOSO 场景偏移及 Q3 有符号指标风险继续按既有合同披露。
- 第三层血缘增加运行量，但固定 Ridge 与有限候选保持计算可行。

## Forbidden Now

- G2 Round 2 PASS 前进入 S3、拟合正式 Baseline、比较模型性能或调参。
- 在 S5 freeze manifest 和 G4 PASS 前解析或推理任何官方测试 CSV 数值。
- 使用测试预测外观反馈 O2/O3/S4。
- 下游使用非 Q1-B1、非 bounded、训练内或无血缘的 Q1 特征。
- 让 outer/downstream-inner/nested-upstream/LOSO 的验证组进入相应拟合。
- 修改 reviews/gate_2_review.md 或创建 reviews/gate_2_review_r2.md。
- 上传任何 CSV。

## Next Gate

- Gate：G2 — Review Round 2
- Verdict：NOT SUBMITTED
- Planned Response：work/revisions/gate_2_response.md
- Planned Submission：reviews/gate_2_submission_r2.md
- Expected Review：reviews/gate_2_review_r2.md
- Requested transition：S2→S3

## Last Updated

- 时间：2026-09-09T14:54:01+08:00
- 负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
