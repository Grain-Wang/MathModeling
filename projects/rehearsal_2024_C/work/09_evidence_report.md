# S4 证据报告

## 1. 状态说明

本报告为 G4 审核提供 raw 证据索引。所有文件仍位于 `results/raw/main/`，通过 G4 只授权进入 S5 核验，并不自动成为 `results/verified/` 论文证据。正式 Evidence ID、复制/生成到 verified 的动作必须等 G4 PASS 后在 S5 完成。

## 2. 可复核主张索引

| Claim ID | 可审核主张 | 核心数值 | 直接证据 | 生成实验 |
|---|---|---:|---|---|
| S4-C01 | Q2 二次温度修正通过采用门槛 | RMSLE 0.360678→0.202567；改善43.84% | `q2/quadratic_temperature_metrics.json`、`q2/quadratic_temperature_oof_predictions.csv`、`q2/quadratic_temperature_by_temperature.csv` | `EXP-Q2-MAIN-001` |
| S4-C02 | Q2 边界温度外推改善但 50°C 有负结果 | LOTO 25°C 0.22788；90°C 0.30606；50°C 0.14378 | `q2/leave_one_temperature_comparison.csv`、`q2/sensitivity_metrics.json` | `EXP-Q2-SENS-001` |
| S4-C03 | 完整 HGB 公平击败 Ridge 并通过子组门槛 | 0.200097→0.076397；最大主要子组变化 -50.64% | `q4/hgb_metrics.json`、`q4/hgb_oof_predictions.csv`、`q4/hgb_vs_ridge_subgroup_comparison.csv` | `EXP-Q4-MAIN-001` |
| S4-C04 | Q4 最终采用工况+幅值 18 特征 HGB | RMSLE 0.070941；比完整 HGB 再改善7.14% | `q4/ablation_metrics.json`、`q4/ablation_metrics.csv`、`q4/final_winner.json` | `EXP-Q4-ABL-001` |
| S4-C05 | Q4 最终模型严格 OOF 和 full-fit 工件闭合 | 12,400 OOF；5 个折模型 | `q4/final_oof_predictions.csv`、`q4/final_oof_lineage.csv`、`q4/final_fold_models.joblib`、`q4/final_full_model.joblib` | `EXP-Q4-ABL-001` |
| S4-C06 | Q4 插值强但未见材料/温度外推较弱 | LOMO max 0.37982；LOTO max 0.57496 | `q4/stress_metrics.json`、`q4/leave_one_level_out_metrics.csv`、`q4/stress_subset_metrics.csv` | `EXP-Q4-STRESS-001` |
| S4-C07 | Q3 三组两两交互在主指标上胜过加性模型 | log-RMSE 0.343416→0.326667；改善4.88% | `q3/interaction_metrics.json`、`q3/interaction_oof_predictions.csv` | `EXP-Q3-INT-001` |
| S4-C08 | Q3 交互结论具有分层稳定性但并非全部稳定 | 500/500；27/40 符号稳定度≥0.90 | `q3/bootstrap_metrics.json`、`q3/bootstrap_pairwise_interaction_intervals.csv` | `EXP-Q3-BOOT-001` |
| S4-C09 | Q3 共同支持有限，峰值/重复敏感性已量化 | 支持14.24%；峰值 +2.28%；去重 +0.004% | `q3/sensitivity_metrics.json`、`q3/sensitivity_summary.csv` | `EXP-Q3-SENS-001` |
| S4-C10 | Q5 Bootstrap 完成但唯一推荐门槛失败 | 500/500；Jaccard 0.39535<0.50；eligible=0 | `q5/robustness_metrics.json`、`q5/final_candidate_index.csv`、`q5/bootstrap_region_stability.csv` | `EXP-Q5-ROB-001` |
| S4-C11 | Q5 三类敏感性不改变“不得覆盖主 Gate”政策 | OOF 区域相对主口径 Jaccard min 0.881 | `q5/sensitivity_metrics.json`、`q5/sensitivity_scenarios.csv` | `EXP-Q5-SENS-001` |
| S4-C12 | Q1 Logistic 在强制压力下仍饱和，树模型无需运行 | 相位/幅值一致率1.0；LOMO min F1=1.0 | `q1/stress_metrics.json`、`q1/invariance_metrics.csv`、`q1/leave_one_material_out.csv` | `EXP-Q1-ABL-001` |
| S4-C13 | 全部 S4 结果来自单一干净实现并通过独立复算 | 23/23 PASS；SHA `6accab2…` | `verification_report.json`、`runs/*/run_manifest.json` | `EXP-S4-COMP-001` |

以上路径均相对于 `results/raw/main/`。

## 3. Manifest 与谱系

12 份权威 manifest 位于 `results/raw/main/runs/<EXP-ID>/run_manifest.json`。其中 11 份问题实验和 1 份总验证均记录：

- `stage=S4`、`status=PASS`、`exit_code=0`；
- `git_commit=6accab2c0d9dbd8fbc0d362d9c60f9161f1e1901`；
- `implementation_git_dirty_at_finish=false`；
- `conda_environment=math_modeling`；
- 仓库相对 `command_repo_relative`；
- 描述文件、冻结配置、代码、输入和输出 SHA-256；
- 重算后的 8 份合同哈希。

Q4 最终 OOF 的每行模型 ID可追到 `q4/final_oof_lineage.csv`；Q5 再逐折核对训练/验证工况组哈希和模型 ID。`verification_report.json` 独立重算 Q2、Q3、Q4 指标、Q5 Pareto 成员和推荐禁用逻辑。

## 4. 公平性与隔离证据

1. Q2/Q3/Q4 均沿用 S3 固定外层折；候选选参只在对应外层训练折内完成。
2. Q4 HGB 候选数固定为18；Q3 只比较三组预定义交互；未试多个随机种子挑最好结果。
3. Q4 消融复用已经选定的折参数，不对三种特征组重新调参。
4. manifest 输入中不存在附件二或附件三；测试附件未参与任何 S4 选择。
5. Q5 的 full-fit 预测只用于参考与一致性诊断，主 Pareto 使用严格 OOF。
6. 结果文件仍为 raw；`results/verified/` 未被写入。

## 5. 论文安全表述边界

可以在 G5 核验后候选表述：

- “二次温度修正在相同分组折上明显降低 Q2 主误差，尤其改善边界温度外推。”
- “有限候选 HGB 显著优于 Ridge，且删除无增益 shape 特征后得到更简洁的 18 特征模型。”
- “预定义两两交互改善 Q3 的对数误差，并由工况组簇 Bootstrap 给出调整后关联区间。”
- “Q5 的区域一致性较 Baseline 提高，但未达预设门槛，因此不发布唯一推荐。”

禁止表述：

- 把 Q1 OOF=1.0 写成附件二真实准确率；
- 把 Q3 调整后关联写成因果效应；
- 隐去 Q2 的 50°C 局部劣化或 Q4 的未见水平外推风险；
- 用未加折支持的敏感性 Jaccard 覆盖 Q5 主 Jaccard 失败；
- 在 G4/G5 前称这些数字为 verified 或论文最终值。

## 6. 完整性检查

- 强制目录：`experiments/main/`、`comparison/`、`ablation/`、`sensitivity/`、`robustness/` 均包含可执行实验描述。
- 强制报告：`work/07_failure_analysis.md`、`work/08_main_model_report.md`、本文件已齐全。
- 原始结果：`results/raw/main/` 共 114 个文件，约 40.6 MB；无文件写入 `results/verified/`。
- 独立复算：`results/raw/main/verification_report.json` 为 PASS，失败项 0。