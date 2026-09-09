# CURRENT

## Project

- 项目名称：rehearsal_2024_B
- ACTIVE_PROJECT：projects/rehearsal_2024_B
- 项目状态：ACTIVE
- 题目：2024 年中国研究生数学建模竞赛 B 题《WLAN组网中网络吞吐量建模》
- 类型：往年题模拟
- 题目版本：本地 DOCX SHA-256 C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594

## Current Stage

S3 — 全题 Baseline 闭环。G2 Round 2 已 PASS，S2→S3 已授权；当前只执行冻结的八个 Baseline、训练侧验证、LOSO、报告与 O2 诊断。

## Last Gate

- Gate：G2 / Review Round 2
- Verdict：PASS
- Review File：[reviews/gate_2_review_r2.md](reviews/gate_2_review_r2.md)
- Reviewed Commit：facedf109a9025cb241d9a93074b0467c93143cb
- Review Commit：6504c54782dc33e111800b3166e9e1766cab6549
- Authorization：S2→S3；Next Gate=G3
- Open findings：Critical=0，Major=0，Minor=3，Advisory=1；均不阻断 S3，按审核时限处理

## Approved Artifacts

- G0/R1、G1/R2、G2/R2 均已 PASS。
- S1 数据身份、A01–A06、严格组定义、Q2 17 类顺序和 Q3 两级目标/指标合同继续有效。
- S2 统一方案、三问模型合同、机器实验合同、切分注册表、嵌套上游血缘与测试集治理已获批准。
- Split registry core SHA-256：88B108D181C2EA3A723303DED3D0E64BACEF7FA482F8322712ED97ED020A6C2D。
- 下游固定上游：Q1-B1 Ridge(alpha=1.0) + seq_time_bounded + q1_clip_0_test_dur_v1。

## Current Goal

完成 S3 全题 Baseline、15 个 primary outer folds、13 个 source-blind LOSO、真实入口门禁、feature schema、训练侧导出 dry-run、Baseline 报告和 O2 诊断；若 O2=PROCEED_TO_G3，则形成 G3 审核包并停在 G3 等待审核。

## Current Tasks

1. 实现共享特征引擎、真实 S3 入口和每次运行的 phase manifest。
2. 运行 EXP-S3-Q1-B0/B1、Q2-B0/B1A/B1B、Q3-B0/B1/B2。
3. 完成 repeated grouped OOF、LOSO、实际 Q1 上游 lineage、Q2 稀有类/A03 和 Q3 AP/system 一致性证据。
4. 生成 results/raw/baseline/feature_schema.json 及其他非 CSV 原始结果。
5. 完成 work/06_baseline_report.md 和 work/optimization/o2_baseline_diagnosis.md。
6. 仅在 O2 决策允许时创建 G3 submission。

## Current Process Blockers

- 无技术阻塞。
- G3 尚未审核；S4 不得启动。

## Known Limitations / Risks

- 原始 CSV 由 /projects/**/*.csv 忽略，不进入 Git；远程 Reviewer 需按 manifest 恢复。
- Q2 固定 17 类高度不平衡，部分训练折可能缺类，必须补零概率并如实披露。
- LOSO 场景偏移、A03 的 0|0 和 Q3 零吞吐相对误差仍是强制风险披露项。
- G2 Minor-02 的 ledger 驱动 exactly-once 门禁最迟在 G4/S5 最终入口前完成。
- G2 Minor-03 的唯一全量最终配置规则须在 S4/O3 前冻结。

## Forbidden Now

- S3 内运行 HGB 主候选、扩大模型网格或调参。
- 在 O2 前启动 S4 改进。
- 在 G4 PASS 与 S5 freeze manifest 完整前解析、推理或人工查看任何官方测试 CSV 数值或预测。
- 使用测试预测外观反馈 O2/O3/S4。
- 下游使用非 Q1-B1、非 bounded、训练内或无血缘的 Q1 特征。
- 修改已批准的模型合同、split registry 核心或 Reviewer 文件来迎合结果。
- 将任何 CSV 加入 Git。

## Next Gate

- Gate：G3
- Preconditions：八个 Baseline、15 个 primary folds、13 个 LOSO、O2=PROCEED_TO_G3
- Expected Submission：reviews/gate_3_submission.md
- Requested transition：S3→S4（仅由未来 G3 PASS 授权）

## Last Updated

- 时间：2026-09-09
- 负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
