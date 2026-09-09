# CURRENT

## Project

- 项目名称：rehearsal_2024_B
- ACTIVE_PROJECT：projects/rehearsal_2024_B
- 项目状态：ACTIVE
- 题目：2024 年中国研究生数学建模竞赛 B 题《WLAN组网中网络吞吐量建模》
- 类型：往年题模拟
- 题目版本：本地 DOCX SHA-256 C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594

## Current Stage

S2 — 总体方案与模型合同已完成，等待 G2 Reviewer 判定。

S2→S3：NOT AUTHORIZED。G2 PASS 前不进入 S3，不拟合正式 Baseline。

## Last Gate

- Gate：G1 / Review Round 2
- Verdict：PASS
- Review File：[reviews/gate_1_review_r2.md](reviews/gate_1_review_r2.md)
- Reviewed Commit：9f0a209f55351aff306aa7ecd6d38486fcf43352
- Review Commit：fd6e33b4fa9a7f2de4764ff52272cd62ff52a45b

## Approved Artifacts

- G0/R1 与 G1/R2 均已 PASS。
- S1 的题意、数据层级、A01–A06、严格身份、跨文件重复、测试封存和 Q3 两级目标/指标合同已批准。
- 正式 S1 审计来自干净提交 affff4fa6ef2d9a5431adac6e7341c993b946f4d。
- Reviewer 已授权进入 S2，并要求在正式训练前完成统一方案、逐问合同、实验计划、强制 LOSO、固定 Q2 标签/缺类行为、固定 Q3 指标与 O1。

## S2 Evidence

- 统一方案：[work/04_solution_plan.md](work/04_solution_plan.md)
- 三问合同：work/models/q1_model_contract.md、q2_model_contract.md、q3_model_contract.md
- 实验计划：[work/05_experiment_plan.md](work/05_experiment_plan.md)
- 可机读合同：[configs/s2_experiment_plan.json](configs/s2_experiment_plan.json)
- O1：[work/optimization/o1_solution_optimization.md](work/optimization/o1_solution_optimization.md)，Decision=PROCEED_TO_G2
- 正式合同校验提交：6b88cd1eb6a4776b12b77b859f01d7b8cfaf9a39
- 校验结论：PASS；输入前后哈希不变；model_fit_count=0；official_test_numeric_read_count=0
- 训练候选：1,250 个 AP 行、482 个严格 source_file+test_id 组
- 冻结切分：15 个外层折、1,446 个外层分配、5,784 个嵌套内层分配、13 个 LOSO
- Q2：固定 17 个联合标签；Q3 合成指标测试：PASS
- Split registry core SHA-256：E1DE3911D78140DB8F3A3342F7982959EB28FBA85DCFB3AF09AE990BBAC5D704

## Current Goal

提交 G2 审核包并等待 Reviewer 对 S2→S3 给出 PASS / REVISE / BLOCK。当前不实施模型训练。

## Current Tasks

1. 将完整 S2/G2 审核快照推送至 origin/main。
2. 向 Reviewer 提供最终 origin/main 完整 SHA。
3. 停在 S2，等待 reviews/gate_2_review.md。

## Current Process Blockers

- G2 尚未审核；这是进入 S3 和正式 Baseline 训练的唯一当前门禁。
- 其余 S2 必要产物与 O1 均已完成，无技术阻塞。

## Known Limitations / Risks

- 原始 CSV 由 /projects/**/*.csv 忽略；远程 Reviewer 需依赖 manifest、恢复说明、脚本和非 CSV 机器证据。
- 团队成员实名责任分配尚未提供，最终交付前必须补齐。
- environment.yml 尚未在全新环境 clean rebuild；当前 math_modeling 环境的已记录导入 smoke=PASS。
- Q2 含极稀有联合类；固定标签、缺类零概率、support 披露、A03 敏感性和条件权重规则已冻结。
- 普通 grouped K-fold 共享 source 场景；13 折 LOSO 必须单独报告。
- Q3 题面有符号 ERROR_90 可能产生负数或超过 100% 的 accuracy_90；必须原样报告，并以绝对误差辅助诊断。
- A01–A06 与官方测试集分布封存边界继续有效。

## Forbidden Now

- G2 PASS 前进入 S3、拟合正式 Baseline、比较模型性能或调参。
- 使用官方测试集数值分布、空白目标或预测结果选择方案。
- 覆写原始 DOCX/CSV，或将任何 CSV 上传远程。
- 让同一 source_file+test_id 跨折，或在全数据上拟合可学习预处理。
- Q1 使用事后字段；Q2 使用真实 Q1/Q2 目标；Q3 将真实 MCS/NSS 的题面许可扩展到 PER 等字段。
- 临时扩大候选数量、时间盒或指标定义。
- Main Agent 创建或修改 reviews/gate_2_review.md。

## Next Gate

- Gate：G2 — 总体方案与模型合同
- Verdict：PENDING REVIEW
- Submission：[reviews/gate_2_submission.md](reviews/gate_2_submission.md)
- Expected Review：reviews/gate_2_review.md
- Requested transition：S2→S3

## Last Updated

- 时间：2026-09-09T11:51:36+08:00
- 负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
