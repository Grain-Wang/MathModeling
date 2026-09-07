# Gate 2 Submission — Review Round 2

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_C`
- Gate: `G2`
- Stage: `S2 — 总体方案与模型合同`
- Review Round: `2`
- Round 1 Review Commit: `4edfcd05b685d4d4df5fdba8a46a1186671747e8`
- Round 1 Reviewed Commit: `2e9517df11b5e0ef861572ca508d8d61d56511f7`
- Review commit: 调用 Reviewer 时传入本次 Round 2 提交推送后的 `git rev-parse HEAD` 完整 SHA
- Prepared at: 2026-09-07 +08:00

Reviewer 必须审核远程固定完整 SHA，不得改用随后变化的 branch HEAD。Round 2 结论必须新增到 `reviews/gate_2_review_r2.md`，不得覆盖 [`gate_2_review.md`](gate_2_review.md)。

## Required-Fix Response

- [`work/revisions/gate_2_response.md`](../work/revisions/gate_2_response.md)

该文件逐条映射 M2-01、M2-02 的 Required Fix 和 Acceptance Criteria，并记录 Minor 的处理与残余风险。

## Revised Deliverables

- [`work/04_solution_plan.md`](../work/04_solution_plan.md)
- [`work/models/00_shared_data_validation_contract.md`](../work/models/00_shared_data_validation_contract.md)
- [`work/models/q4_model_contract.md`](../work/models/q4_model_contract.md)
- [`work/models/q5_model_contract.md`](../work/models/q5_model_contract.md)
- [`work/05_experiment_plan.md`](../work/05_experiment_plan.md)
- [`experiments/s2_frozen_config.json`](../experiments/s2_frozen_config.json)
- [`logs/decisions.md`](../logs/decisions.md)
- [`logs/experiments.md`](../logs/experiments.md)
- [`logs/ai_usage.md`](../logs/ai_usage.md)
- [`CURRENT.md`](../CURRENT.md)

Q1–Q3 合同的科学路线没有扩张；其规范化文件哈希与 Q4/Q5 及共享合同一起登记在冻结配置中。

## Round 2 Claims

1. Q5 候选已闭合为 `observed_operating_point_v1`：来源定位、波形 SHA、全部 Q4 特征、模型/config/schema 哈希均为决策身份的一部分。
2. $(T,f,w,B_m,m)$ 只作汇总；单点必须表述为“该实测波形轮廓下的推荐工况”。
3. Q5 主 Pareto 只使用对应外层留出模型产生的严格 `y_pred_oof`；训练过候选组的折模型没有稳定投票权。
4. 每折只评价本折验证候选，并按 `q5-region-v1` 比较区域；最低支持为 `ceil(0.60*K)`。
5. 严格 OOF 候选表执行 500 次 `condition_group` 簇 Bootstrap；至少 400 次有效且条件区域入选率 `≥0.50`。
6. 唯一候选必须同时位于 OOF/full-fit Pareto，且 OOF 残差和 full/OOF 差不超过材料×波形参照层 P90；`n<100` 回退全局。
7. 模型稳定区域与观测损耗区域 Jaccard `<0.50`、口径反转或任一资格门槛失败时，只报告区域和端点。
8. 5 个折模型范围只称“重拟合扰动范围”；95% 区间仅指 500 次工况组簇 Bootstrap 百分位区间。
9. Q4 已区分 schema 已知未见水平与真正未知水平；主要子组固定 `n≥100` 且覆盖至少 3 折。
10. RMSLE、MAPE、$R^2$ 公式和尺度已冻结；JSON 记录搜索网格、Q5 参数和 8 份合同 SHA。
11. 附件二、三不参与任何选择或 Q5 阈值；本轮未实现、训练或运行 S3。

## Static Verification

已完成以下静态检查：

```text
model_contract_structure=PASS count=5 headings=14
config_json_and_input_hashes=PASS
contract_registry_hashes=PASS count=8
q5_round2_controls=PASS
Markdown_links=PASS
raw_workbooks_tracked=0
git_diff_check=PASS
no_modeling_claims=PASS
```

这些是文档与配置静态验证，不代表模型精度、Pareto 结果或运行时间已经实机验证。

## Known Limitations

1. G2 尚未 PASS，S3 CLI 和模型训练仍未开始。
2. 严格 OOF、折级区域和 Bootstrap 的实际有效数量只能在 S3/S4 运行后得到；合同已冻结失败和降级路径。
3. 实测工况点路线不声称连续空间全局最优，连续扩展保持关闭。
4. full-fit 模型仍可能对训练点乐观，因此只作参考，并受双 Pareto/P90/观测区域诊断约束。
5. 若实际外层折降为 4 或 3，区域支持仍按 `ceil(0.60*K)`，其余阈值不得事后放宽。

## Requested Verdict

`PASS`。若两项 Major 已关闭，请授权 `S2 → S3`，下一 Gate 为 G3；否则请继续按 Critical/Major/Minor 给出可复核问题。Main Agent 不自行宣布 G2 通过。
