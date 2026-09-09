# CURRENT

## Project

项目名称：rehearsal_2024_B

ACTIVE_PROJECT：projects/rehearsal_2024_B

项目状态：ACTIVE

## Selected Problem

题号与名称：2024 年中国研究生数学建模竞赛 B 题《WLAN组网中网络吞吐量建模》

比赛类型：往年题模拟

题目版本：本地 DOCX SHA-256 C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594

## Current Stage

S2 — 总体方案与模型合同。

G1 Round 2 已 PASS；S1 → S2 已授权。G2 PASS 前不进入 S3 或训练正式 Baseline。

## Last Gate

Gate：G1 / Review Round 2

Verdict：PASS

Review File：[reviews/gate_1_review_r2.md](reviews/gate_1_review_r2.md)

Reviewed Commit：9f0a209f55351aff306aa7ecd6d38486fcf43352

Review Commit：fd6e33b4fa9a7f2de4764ff52272cd62ff52a45b

## Approved Artifacts

- G0/R1 与 G1/R2 均已 PASS。
- S1 的题意、数据层级、A01–A06、严格身份、跨文件重复、测试封存和 Q3 两级指标合同已批准。
- 正式 S1 审计基于干净 commit affff4fa6ef2d9a5431adac6e7341c993b946f4d。
- Reviewer 授权进入 S2，要求在正式训练前完成统一方案、逐问模型合同、实验计划和 O1。

## Current Goal

在不拟合模型、不使用官方测试数值分布的前提下，完成并冻结：

1. Q1→Q2/Q3 的统一技术主线；
2. Q1、Q2、Q3 模型合同；
3. 分组切分、机器配置、评价、候选预算和停止条件；
4. O1 总体方案优化报告；
5. G2 审核包。

## Current Tasks

1. 依据题目附录统一 nav 为 NAV 门限，单位 dBm。
2. 编写 work/04_solution_plan.md 和 work/models/*_model_contract.md。
3. 编写 work/05_experiment_plan.md，并冻结 source_file + test_id 分组、LOSO、Q2 标签及 Q3 指标。
4. 完成 O1 并仅在决策为 PROCEED_TO_G2 时提交 G2。
5. 更新日志、CURRENT 和 reviews/gate_2_submission.md。

## Current Process Blockers

- None。G1 已授权进入 S2。
- G2 尚未审核，因此正式 Baseline 训练和 S3 仍被门禁阻止。

## Known Limitations / Risks

- 原始 CSV 被 Git 忽略；远程 Reviewer 需依赖 manifest、脚本和非 CSV 机器证据。
- 团队成员实名责任分配尚未提供。
- environment.yml 尚未在全新环境 clean rebuild；当前机器导入 smoke=PASS。
- Q2 含极稀有联合类别，普通分组折可能缺类，必须执行固定标签和回退合同。
- 普通 grouped K-fold 共享 source 场景，必须另报 leave-one-source-file-out。
- Q3 题面有符号误差可能产生超过 100% 或为负的 accuracy_90，必须如实报告并使用绝对误差辅助诊断。
- A01–A06 和官方测试分布封存边界继续有效。

## Forbidden Now

- G2 PASS 前进入 S3、训练正式 Baseline、比较模型性能或调参。
- 使用官方测试集数值分布、空白目标或预测结果选择任何方案。
- 覆写原始 DOCX/CSV，或将 CSV 上传远程。
- 让同一 source_file + test_id 组跨折；在全数据上拟合 RSSI 汇总后的可学习预处理。
- Q1 使用事后字段；Q2 使用真实标签；Q3 将真实 MCS/NSS 特许扩展到 PER 等字段。
- Main Agent 创建或修改 reviews/gate_2_review.md。
- 未记录理由地突破候选数量、时间盒和停止条件。

## Next Gate

Gate：G2 — 总体方案与模型合同

Verdict：NOT SUBMITTED

Planned Deliverables：

- work/04_solution_plan.md
- work/models/q1_model_contract.md
- work/models/q2_model_contract.md
- work/models/q3_model_contract.md
- work/05_experiment_plan.md
- work/optimization/o1_solution_optimization.md
- reviews/gate_2_submission.md

Expected Review：reviews/gate_2_review.md

## Last Updated

时间：2026-09-09T11:30:19+08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
