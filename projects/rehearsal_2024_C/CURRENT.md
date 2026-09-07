# CURRENT

## Project

项目名称：`rehearsal_2024_C`

ACTIVE_PROJECT：`projects/rehearsal_2024_C`

## Selected Problem

题号与名称：2024 年中国研究生数学建模竞赛 C 题《数据驱动下磁性元件的磁芯损耗建模》

比赛类型：往年题模拟

## Current Stage

S3 — 全题 Baseline 闭环（已完成，等待 G3 审核）

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

S3 新产物尚待 G3 审核，不列为 approved。

## Current Goal

保持 S3 冻结状态，将实现提交 `0d36ef8c16f3214b16d8580333f2925aaff45191` 上产生的 8 个 Baseline 真实结果、复算报告和 G3 提交单推送给 Reviewer；在 G3 明确 PASS 前不进入 S4。

## Completed S3 Tasks

1. 生成 12,400 行 wave-v1 特征、稳定身份、近形状/工况组和固定 5 折；第二次重建哈希一致。
2. 完成 Q1 Logistic、Q2 Steinmetz、Q3 描述/加性、Q4 中位数/Ridge 共 7 个问题实验。
3. 完成 Q5 严格 OOF 实测工况 Pareto、fold-region、full/OOF 差和观测损耗诊断。
4. 8 份 run manifest 全部 PASS，均记录 `math_modeling`、固定实现 SHA、命令、种子、时间和输入输出哈希。
5. 独立复算 `results/raw/s3/verification_report.json` PASS；完成 `work/06_baseline_report.md` 和 `reviews/gate_3_submission.md`。

## Known Blockers

- 进入 S4 的唯一流程阻断：G3 尚未返回 PASS。
- Q5 模型/观测 Pareto 区域 Jaccard 为 0.0962，冻结门槛为 0.50；这是需要 S4 改进和稳健性核验的实证失败信号，当前禁止唯一推荐。

## Forbidden Now

- 在 G3 PASS 前运行 S4 HGB、RandomForest、交互扩展、500 次 Bootstrap 或大规模候选比较。
- 使用附件二、附件三参与特征选择、调参、模型选择或 Q5 域/阈值制定。
- 修改 `s2-r2-v1` 冻结指标、搜索空间或 Q5 门槛来迎合 S3 结果。
- 把 `results/raw/` 当作 verified 论文证据，或在 G3/G5 前写入 `results/verified/`。
- 在 Q5 Jaccard/Bootstrap 等门槛未通过时给出唯一推荐工况。
- 覆写题目 DOCX、四个原始 XLSX 或任何 Reviewer 审核文件。

## Next Gate

G3 — 全题 Baseline 闭环审核

Verdict：`SUBMITTED / PENDING REVIEW`

Submission：[`reviews/gate_3_submission.md`](reviews/gate_3_submission.md)

## Last Updated

时间：2026-09-07 +08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充