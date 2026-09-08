# Gate 4 Submission — 主模型改进与证据构建

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_C`
- Gate: `G4`
- Stage: `S4 — 主模型改进与证据构建`
- Review Round: `1`
- Implementation Commit: `6accab2c0d9dbd8fbc0d362d9c60f9161f1e1901`
- Reviewed Commit: 调用 Reviewer 时传入本提交推送后的 `git rev-parse HEAD` 完整 SHA
- Prepared at: 2026-09-08 +08:00

Reviewer 必须审核远程固定完整 SHA，不得改用随后变化的 branch HEAD；审核结论请新增为 `reviews/gate_4_review.md`，不得修改代码、模型、结果、本文或 `CURRENT.md`。

## Submitted Deliverables

- `work/07_failure_analysis.md`
- `work/08_main_model_report.md`
- `work/09_evidence_report.md`
- `src/s4_common.py`
- `src/run_s4.py`
- `src/run_s4_q1.py` 至 `src/run_s4_q5.py`
- `src/verify_s4_outputs.py`
- `experiments/main/`
- `experiments/comparison/`
- `experiments/ablation/`
- `experiments/sensitivity/`
- `experiments/robustness/`
- `results/raw/main/`
- `logs/experiments.md`
- `logs/decisions.md`
- `logs/ai_usage.md`
- `CURRENT.md`

S2 合同、冻结配置和 S3 Baseline 仍是比较依据；本轮没有改动其哈希登记内容。

## Reproduction and Execution Evidence

统一复现命令：

```powershell
conda run --no-capture-output -n math_modeling python src/run_s4.py --config experiments/s2_frozen_config.json
```

独立复算：

```powershell
conda run --no-capture-output -n math_modeling python src/verify_s4_outputs.py --config experiments/s2_frozen_config.json
```

`results/raw/main/runs/` 下 11 个问题实验和 `EXP-S4-COMP-001` 总验证 manifest 全部为 PASS，均记录：

- `git_commit=6accab2c0d9dbd8fbc0d362d9c60f9161f1e1901`；
- `implementation_git_dirty_at_finish=false`；
- `conda_environment=math_modeling`；
- `command_repo_relative`、固定 seed、环境版本、输入/输出 SHA-256 和合同哈希。

`results/raw/main/verification_report.json` 为 PASS，23/23 检查通过，独立复算 Q2/Q3/Q4 主指标、Q4 最终消融胜者、Q5 Pareto 与唯一推荐禁用逻辑。`stdout.log` 为追加式；权威运行段以当前 manifest 起止时间为准。

## Core Results and Adoption Decisions

1. Q2：二次乘性温度修正与 Steinmetz 使用相同 OOF 折；RMSLE 0.360678→0.202567，改善43.84%，3/4 温度不劣化，正式采用。25°C/90°C LOTO 分别从0.62624/0.55430降至0.22788/0.30606；50°C 局部劣化已披露。条件交互未触发。
2. Q4：冻结18候选 HGB 与 Ridge 同折比较，完整 HGB RMSLE=0.076397，相对 Ridge 改善61.82%，最大主要子组变化为 -50.64%，通过2%/10%门槛；RF 未触发。
3. Q4 消融：工况+幅值18特征 RMSLE=0.070941，比完整48特征再改善7.14%；按无增益特征删除规则，最终模型为 `HGB + amplitude_and_condition`。低 `B_m` RMSLE=0.08328。
4. Q3：三组预定义交互 log-RMSE 0.343416→0.326667，改善4.88%；500/500 工况组 Bootstrap 有效，27/40 两两对比符号稳定度≥0.90。只作调整后关联解释。
5. Q1：三项真实波形变换的一致率、留一材料最低 Macro-F1 均为1.0；保留 Logistic，不为形式复杂化运行树模型。辅助字段-only Macro-F1=0.41976。
6. Q5：使用最终 Q4 胜者严格 OOF；118 个 OOF Pareto、27 个折支持区域、42 个 Bootstrap 稳定区域。折支持后模型/观测区域 Jaccard=0.39535<0.50，单点合格数0，唯一推荐未授权。

## Fairness, Leakage and Selection Assertions

- 外层折、主指标、种子、候选上限和门槛均未更改。
- Q2/Q3/Q4 选参只发生在外层训练折内部；所有谱系检查工况组交集为0。
- Q4 消融复用各折已选参数，不对特征组重新调参；预定义三档全部报告。
- 未运行多个随机种子挑最好结果；负结果和条件未触发分支均写入报告。
- 附件二、三没有出现在任何 S4 manifest 输入中，未生成其预测。
- Q5 主损耗只用 strict OOF；full-fit 只作参考。
- `results/verified/` 未写入，所有 S4 证据仍为 raw。

## G3 Minor Closure

1. `logs/experiments.md` 已把旧空模板明确标为“截至 S2 的历史状态”。
2. `test_s3_synthetic.py` 已直接构造并验证 OOF/full 空交与 Jaccard 双空集分支，`math_modeling` 下 PASS。
3. 新 manifest 均含可移植的 `command_repo_relative`，独立验证确认不包含项目绝对路径。

## Known Limitations and Stop Condition

- Q2 的50°C局部指标略差；Q4 留一材料1和留一25°C RMSLE分别达到0.37982和0.57496，表明未见水平外推远弱于插值 OOF。
- Q3 共同矩形支持仅14.24%，且13/40两两对比符号稳定度不足0.90。
- Q5 主 Jaccard 仍失败，任何敏感性正结果都不得覆盖该失败。
- Q1 完美 OOF 不等于未知测试集真值表现。
- 预定义改进、消融、稳健性和负结果均已闭合；除审核 Required Fix 外，建议停止扩大模型矩阵并进入 S5 结果核验。

## Requested Verdict

请求 `PASS`。若 Reviewer 确认改进真实且源于 S3 失败、同折比较公平、消融/敏感性/稳健性证据充分、负结果无隐瞒且复杂度收益合理，请授权 `S4 → S5`，下一 Gate 为 G5；否则请按 Critical / Major / Minor 给出 Required Fix 和可复核 Acceptance Criteria。Main Agent 不自行宣布 G4 通过。