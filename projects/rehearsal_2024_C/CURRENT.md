# CURRENT

## Project

项目名称：`rehearsal_2024_C`

ACTIVE_PROJECT：`projects/rehearsal_2024_C`

## Selected Problem

题号与名称：2024 年中国研究生数学建模竞赛 C 题《数据驱动下磁性元件的磁芯损耗建模》

比赛类型：往年题模拟

## Current Stage

S3 — 全题 Baseline 闭环

## Last Gate

Gate：G2 / Review Round 2

Verdict：`PASS`

Review File：[`reviews/gate_2_review_r2.md`](reviews/gate_2_review_r2.md)

Reviewed Commit：`7041a8273df63b612590bb7a9b53b02984ff7f26`

## Approved Artifacts

- `work/01_problem_analysis.md`
- `work/02_data_audit.md`
- `work/03_requirement_matrix.md`
- `work/04_solution_plan.md`
- `work/05_experiment_plan.md`
- `work/models/`
- `experiments/s2_frozen_config.json`
- `work/revisions/gate_2_response.md`
- `results/raw/s1/`

## Current Goal

在冻结 `s2-r2-v1` 合同下实际完成 8 个 S3 数据/Baseline 实验，使 Q1–Q5 形成可运行、可复算的最小闭环并提交 G3。

## Current Tasks

1. 实现共享特征、稳定行/波形身份、`condition_group`、固定折和合同哈希复算。
2. 实现并运行 Q1 Logistic、Q2 Steinmetz、Q3 描述/加性、Q4 中位数/Ridge Baseline。
3. 以 Q4 严格 OOF 预测实现 Q5 实测工况点 Pareto、full-fit 参考和基础诊断。
4. 保存实验配置、命令、日志、运行时间、逐样本输出和基本验证。
5. 完成 `work/06_baseline_report.md` 与 `reviews/gate_3_submission.md`，推送固定 SHA 等待 G3。

## G3 Mandatory Implementation Checks

- 逐候选验证 OOF 模型未使用其 `condition_group` 拟合或调参。
- Q5 同时输出折级区域、full/OOF 差和观测损耗诊断，不只展示全局 OOF 膝点。
- 固定 OOF 表的 Bootstrap 只解释为候选表工况组重采样稳定性。
- 显式处理 Pareto 零范围、OOF/full 空交、Jaccard 空集和重复四分位边界。
- S3 启动时复算全部 `sha256_utf8_lf` 合同哈希并写入 `run_manifest.json`。

## Known Blockers

- `None`。G2 Round 2 已 PASS，可以执行 S3。

## Forbidden Now

- 在 8 个 Baseline 闭环前运行 S4 HGB、RandomForest 或无界调参。
- 使用附件二、附件三参与特征选择、调参、模型选择或 Q5 域/阈值制定。
- 修改 `s2-r2-v1` 冻结指标、搜索空间或 Q5 稳定门槛来迎合结果。
- 把 `results/raw/` 写成已核验论文证据，或在 G3 前写入 `results/verified/`。
- 覆写题目 DOCX、四个原始 XLSX 或 Reviewer 审核文件。

## Next Gate

G3 — 全题 Baseline 闭环审核

Verdict：`NOT SUBMITTED`

## Last Updated

时间：2026-09-07 +08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
