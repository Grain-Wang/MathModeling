# Gate 3 Submission — 全题 Baseline 闭环

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_C`
- Gate: `G3`
- Stage: `S3 — 全题 Baseline 闭环`
- Review Round: `1`
- Implementation Commit: `0d36ef8c16f3214b16d8580333f2925aaff45191`
- Reviewed Commit: 调用 Reviewer 时传入本提交推送后的 `git rev-parse HEAD` 完整 SHA
- Prepared at: 2026-09-07 +08:00

Reviewer 必须审核远程固定完整 SHA，不得改用随后变化的 branch HEAD；审核结论请新增为 `reviews/gate_3_review.md`，不得修改代码、结果、本文或 `CURRENT.md`。

## Submitted Deliverables

- `src/s3_common.py`
- `src/build_features.py`
- `src/run_q1.py` 至 `src/run_q5.py`
- `src/run_s3_baselines.py`
- `src/verify_s3_outputs.py`
- `src/test_s3_synthetic.py`
- `experiments/baseline/`
- `results/raw/baseline/`
- `results/raw/s3/`
- `work/06_baseline_report.md`
- `logs/experiments.md`
- `logs/decisions.md`
- `logs/ai_usage.md`
- `CURRENT.md`

模型与评价依据仍为 G2 通过的 `work/models/`、`work/04_solution_plan.md`、`work/05_experiment_plan.md` 和 `experiments/s2_frozen_config.json`。

## Execution Evidence

统一复现命令：

```powershell
conda run --no-capture-output -n math_modeling python src/run_s3_baselines.py --config experiments/s2_frozen_config.json --verify-data-rebuild
conda run --no-capture-output -n math_modeling python src/verify_s3_outputs.py --config experiments/s2_frozen_config.json
```

8 份 `results/raw/baseline/<EXP-ID>/run_manifest.json` 均记录：

- `status=PASS`、`exit_code=0`；
- `git_commit=0d36ef8c16f3214b16d8580333f2925aaff45191`；
- `conda_environment=math_modeling`；
- `implementation_git_dirty_at_finish=false`；
- 实际命令、种子、时间、运行时、软件版本、输入和输出 SHA-256。

`stdout.log` 为追加式审计日志，包含提交前诊断运行；权威运行段是与最新 `run_manifest.json` 起止时间相同的最后一段，旧段特意保留而未清除。

特征构建第二次运行确认三项字节级哈希一致。独立验证报告 `results/raw/s3/verification_report.json` 为 PASS，重算了 Q1–Q4 核心指标、Q5 Pareto 成员和候选级谱系。

## Coverage Claims

1. `EXP-S3-DATA-001`：12,400 行 wave-v1、身份字段、4,323 个 `condition_group` 和固定 5 折均已生成；同组跨折为 0。
2. `EXP-Q1-BASE-001`：12,400 条 shape-only Logistic OOF；Macro-F1=1.000。
3. `EXP-Q2-BASE-001`：1,067 条材料1正弦波 Steinmetz OOF；RMSLE=0.3607，并提交分温度和留一温度结果。
4. `EXP-Q3-DESC-001`：48 个因素单元全部非空，共同支持诊断已生成。
5. `EXP-Q3-BASE-001`：12,400 条加性效应 OOF；log-RMSE=0.3434。
6. `EXP-Q4-NULL-001`：两种训练折中位数参照均已生成。
7. `EXP-Q4-BASE-001`：12,400 条嵌套分组 Ridge OOF；RMSLE=0.2001，优于两个中位数参照。
8. `EXP-Q5-BASE-001`：12,236 个去重后实测工况候选、105 个严格 OOF Pareto 点、折级 Pareto/区域支持、full-fit 参考、观测损耗及冲突诊断均已生成；不是文字替代。

## Leakage and G2 Follow-up Assertions

- 附件二、三没有被加载、拟合、选参、选择或用于 Q5 域/阈值；只在启动完整性检查中重新计算文件哈希。
- Q1 以 `near_shape_group` 分折；Q2–Q5 以 `condition_group` 分折；外层与训练折内选参均断言组交集为空。
- `candidate_oof_lineage.csv` 覆盖 12,236/12,236 个 Q5 候选；每条均绑定验证折和 `q4-ridge-fold-k`，且相应训练组哈希不含该候选组。
- Q5 主 Pareto 只用 `y_pred_oof`；full-fit 仅作参考与差异诊断。
- 已实现重复四分位边界、Pareto 零范围、OOF/full 空交和 Jaccard 双空集分支，并用合成脚本验证关键退化情形。
- 本阶段未执行 500 次 Bootstrap；产物明确标为 S4 pending，并冻结解释为“固定交叉拟合候选表的工况组重采样稳定性”，不是完整模型参数不确定性。

## Known Limitations and Honest Failure Signals

- Q5 OOF/观测 Pareto 区域 Jaccard=0.0962，低于冻结阈值 0.50；`prebootstrap_single_point_eligible_count=0`，因此没有发布唯一推荐。
- Q1 完美 OOF 仍需 S4 不变性和消融压力测试，当前不解释为未知测试集性能。
- Q2 留一温度的最差 RMSLE=0.6262；Q4 低 `Bm` 四分位 RMSLE=0.2575，均已列为针对性改进依据。
- 全部结果仍为 raw，尚未经过 G5 结果核验，不可直接交给论文作为 verified 结论。

## Requested Verdict

请求 `PASS`。若全题真实闭环、基本复核、泄漏控制和运行证据满足 G3，请授权 `S3 → S4`，下一 Gate 为 G4；否则请按 Critical / Major / Minor 给出可复核的 Required Fix 和 Acceptance Criteria。Main Agent 不自行宣布 G3 通过。
