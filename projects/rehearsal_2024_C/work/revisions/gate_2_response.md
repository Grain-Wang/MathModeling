# G2 Round 2 Revision Response

## Review Metadata

- Gate: `G2`
- Response Round: `2`
- Round 1 Review: [`reviews/gate_2_review.md`](../../reviews/gate_2_review.md)
- Round 1 Reviewed Commit: `2e9517df11b5e0ef861572ca508d8d61d56511f7`
- Round 1 Verdict: `REVISE`
- Reviewer Commit Pulled: `4edfcd05b685d4d4df5fdba8a46a1186671747e8`
- Stage remains: `S2 — 总体方案与模型合同`

本响应不自行宣布 G2 通过。用户已确认采用“实测工况点 + 严格 OOF 主 Pareto + 验证折区域诊断 + 500 次工况组 Bootstrap”的修订方向；本轮没有实现或运行 S3。

## M2-01 Response — 闭合 Q5 决策变量与 Q4 输入

### Selected Option

采用 Reviewer 推荐的方案 A：Q5 候选正式定义为带有完整来源和波形身份的“实测工况点”。不建立额外五变量损耗代理，也不再把 $(T,f,w,B_m,m)$ 写成足以唯一决定 Q4 损耗的完整决策向量。

### Fix

每个候选保存：

- `row_id=file|sheet|excel_row`、来源文件 SHA-256、工作表、Excel 行号和重复来源映射；
- 原始 1,024 点波形的规范化 SHA-256；
- Q4 实际使用的全部 `wave-v1` 输入特征和 feature schema SHA-256；
- `condition_group`、`oof_fold`、Q4 模型/Pipeline/config 哈希；
- $T,f,w,B_m,m$、严格 OOF/全量预测和 $E=fB_m$。

波形签名算法固定为：float64 little-endian，`-0.0` 规范为 `+0.0` 后对连续字节做 SHA-256。来源定位可恢复完整波形，特征快照可重建 Q4 输入。

单点结论必须写为“该实测波形轮廓下的推荐工况”。五因素只按稳定区域、频率/$B_m$ 区间或候选集合汇总，不外推为同类波形均具有相同损耗。

### Evidence Files

- [`work/04_solution_plan.md`](../04_solution_plan.md) §6
- [`work/models/q5_model_contract.md`](../models/q5_model_contract.md) 的 Inputs、Variables、Mathematical Definition、Outputs、Constraints 和 Expected Artifacts
- [`work/05_experiment_plan.md`](../05_experiment_plan.md) §3、§9.1
- [`experiments/s2_frozen_config.json`](../../experiments/s2_frozen_config.json) `models.q5.candidate_*`

### Acceptance Criteria Mapping

| Reviewer criterion | Round 2 closure |
|---|---|
| 决策向量包含全部目标输入或有唯一聚合规则 | 实测工况点包含来源、波形签名、完整 Q4 特征和模型身份；五因素只作汇总 |
| 输出候选可完整复算 Q4 预测 | 候选索引、Q4 特征快照、schema/Pipeline/config 哈希和来源定位均为必需字段 |
| 五因素报告不隐藏波形差异 | 单点强制绑定波形轮廓；五因素只报告稳定区域/区间 |
| 四份主文件与配置一致 | 总体方案、Q5 合同、实验计划和冻结 JSON 均使用 `observed_operating_point_v1` |

### Residual Risk

附件一只能代表已观测联合支持域，不能给出连续空间全局最优；合同已将连续扩展设为关闭，未来若需要必须另建合同并重新过 Gate。

## M2-02 Response — 严格 OOF Q5 稳定性

### Selected Option

采用 Reviewer 方式 3 为主，并加入方式 1 的验证折区域诊断：每个实测候选的主损耗只使用唯一留出其 `condition_group` 的 Q4 OOF 预测；全量模型只作最终重拟合参考。不会再让训练过该候选的其他折模型投票。

### Frozen Procedure

1. 用逐行 `y_pred_oof` 构造全局主 Pareto、端点和膝点。
2. 每个外层模型只评价自己的验证折候选，形成折级 OOF Pareto。
3. 用不读取损耗的 `q5-region-v1` 聚合：材料×波形×温度×全局频率四分位×全局 $B_m$ 四分位；区域至少出现在 `ceil(0.60*K)` 个验证折 Pareto。
4. 对严格 OOF 候选表做 500 次 `condition_group` 簇 Bootstrap，seed `20240922`；区域至少 400 次有效出现且条件 Pareto 入选率 `≥0.50`。
5. 单点必须同时属于 OOF 与 full-fit Pareto；其 OOF 绝对对数残差和 full/OOF 绝对对数差均不得超过材料×波形参照层 P90，参照层 `n<100` 时回退全局。
6. 增加模型预测 Pareto 与观测损耗 Pareto 诊断；稳定区域 Jaccard `<0.50` 时降级。
7. 任一门槛失败，只报告稳定区域和两个端点，不给唯一推荐。

Bootstrap 输出可称“95% condition-group cluster bootstrap percentile interval”。若保留 5 个折模型的全候选预测范围，只能称“refit perturbation range / 重拟合扰动范围”，不作为折外证据，也不称置信区间。

### Evidence Files

- [`work/04_solution_plan.md`](../04_solution_plan.md) §5–§6
- [`work/models/q5_model_contract.md`](../models/q5_model_contract.md) Mathematical Definition、Parameters、Procedure、Evaluation、Failure Conditions
- [`work/05_experiment_plan.md`](../05_experiment_plan.md) `EXP-Q5-BASE-001`、`EXP-Q5-ROB-001`、§9.1
- [`experiments/s2_frozen_config.json`](../../experiments/s2_frozen_config.json) `models.q5`

### Acceptance Criteria Mapping

| Reviewer criterion | Round 2 closure |
|---|---|
| 训练过候选组的模型不能投出稳定票 | 主分数只接受对应严格 OOF；其他折模型范围仅为非推断性诊断 |
| 存在可执行严格 OOF Pareto | 全局 OOF Pareto + 每折仅验证候选 Pareto均已冻结 |
| full 与 OOF 冲突有预定降级 | 双 Pareto、两个材料×波形 P90 和观测区域 Jaccard 0.50 |
| 不把 5 折范围冒充 95% CI | 5 折范围改名重拟合扰动范围；95% 区间只来自 500 次簇 Bootstrap |
| Failure Conditions 阻止过拟合极值 | 双 Pareto、P90、折支持、Bootstrap、观测区域与敏感性任一失败即禁止唯一推荐 |

### Residual Risk

不同外层模型产生的 OOF 分数可能存在折间校准差异，因此合同同时要求折级区域诊断、全量/OOF 差、实际残差与观测 Pareto对照；这些门槛只允许降级，不允许事后放宽。

## Minor / Follow-up Closure

| Reviewer follow-up | Fix |
|---|---|
| Q4 留一材料/温度编码 | schema 外值入口报错；schema 已知但训练折未见的水平用预声明类别和 `OneHotEncoder(handle_unknown="ignore")`，标为已知水平外推 |
| 主要子组最小样本量 | 固定 `n≥100` 且覆盖至少 3 个实际外层折；不足组只描述，不改变 10% 升级门槛 |
| 指标公式 | RMSLE=`log1p`；MAPE 分母下限 `1 W/m³`；$R^2$ 原尺度；集中写入共享合同并同步 JSON |
| Markdown / 配置单一事实源 | JSON 新增 Q1/Q4 完整搜索网格、Q5 参数和 8 份合同的 `sha256_utf8_lf` |
| 阶段提交范围 | Round 2 只修改 ACTIVE_PROJECT；不更新根目录 `readiness_audit.md` 或用户 Guide 文件 |

## Test-Set Isolation

附件二、三继续禁止参与特征选择、调参、模型选择、Q5 候选域、阈值、权重或稳定性判断。Q5 只使用附件一的训练 OOF 证据；配置新增 `use_for_q5_candidate_domain_or_thresholds=false`。

## Validation

Round 2 提交前静态检查结果：

```text
model_contract_structure=PASS count=5 headings=14
config_json_and_input_hashes=PASS count=5
contract_registry_hashes=PASS count=8
q5_round2_controls=PASS
Markdown_links=PASS docs=8
stale_q5_policy_scan=PASS
raw_workbooks_tracked=0
git_diff_check=PASS
active_project_scope=PASS
no_model_training_or_prediction_executed=PASS
```

这些检查只证明文档、配置、哈希和流程口径闭合，不声称模型精度、Pareto、Bootstrap 或实际运行时间已经验证。

## Requested Re-review

请 Reviewer 对新的远程固定完整 SHA 执行 `G2 / Review Round 2`，并将新结论写入 `reviews/gate_2_review_r2.md`，不得覆盖 Round 1 审核文件。只有 Round 2 `PASS` 才允许 S2 → S3。
