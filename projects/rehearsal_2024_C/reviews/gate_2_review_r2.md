# Gate 2 Review — Round 2

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_C`
- Gate: `G2`
- Stage: `S2 — 总体方案与模型合同`
- Review Round: `2`
- Round 1 Reviewed Commit: `2e9517df11b5e0ef861572ca508d8d61d56511f7`
- Round 1 Review Commit: `4edfcd05b685d4d4df5fdba8a46a1186671747e8`
- Reviewed Commit: `7041a8273df63b612590bb7a9b53b02984ff7f26`
- Verdict: **PASS**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

## 1. Final Verdict

# **PASS — 同意进入 S3 / G3**

经对固定快照 `7041a8273df63b612590bb7a9b53b02984ff7f26` 的 G2 Round 2 独立静态复审，Round 1 提出的两项 Major 问题已经关闭：

1. Q5 决策对象已经从不闭合的抽象五元组，修订为包含来源、完整波形身份、全部 Q4 输入特征及模型/config/schema 哈希的可复算“实测工况点”；
2. Q5 主 Pareto 和稳定性证据已经改为严格 OOF 路线，训练过候选 `condition_group` 的模型不再具有折外稳定投票权，并增加了全量/OOF 冲突拒绝、折级区域支持、簇 Bootstrap 和观测损耗 Pareto 诊断。

当前没有未解决的 Critical 或 Major 问题。总体方案可以落地，Q1–Q5 模型合同已经明确到足以安全开始实现，Baseline、验证规则、升级门槛和失败回退均已定义。

因此正式授权：

```text
G2 = PASS
Current Stage may advance: S2 -> S3
Next Gate: G3
```

本结论仅适用于上述固定 commit。S3 代码、运行日志和结果必须另行提交 G3 审核，不能把本次对“设计可执行性”的 PASS 解释为模型精度、Pareto 结果或最终论文结论已经通过。

---

## 2. Review Scope and Static-Review Limitation

本轮重点读取和核对：

```text
.agents/roles/reviewer_agent.md
projects/rehearsal_2024_C/CURRENT.md
projects/rehearsal_2024_C/reviews/gate_2_review.md
projects/rehearsal_2024_C/reviews/gate_2_submission_r2.md
projects/rehearsal_2024_C/work/revisions/gate_2_response.md
projects/rehearsal_2024_C/work/04_solution_plan.md
projects/rehearsal_2024_C/work/models/00_shared_data_validation_contract.md
projects/rehearsal_2024_C/work/models/q4_model_contract.md
projects/rehearsal_2024_C/work/models/q5_model_contract.md
projects/rehearsal_2024_C/work/05_experiment_plan.md
projects/rehearsal_2024_C/experiments/s2_frozen_config.json
```

同时比较了 Round 1 Reviewer 写回 commit `4edfcd05...` 与 Round 2 commit `7041a827...`。本轮变更仅涉及 `projects/rehearsal_2024_C/` 内 12 个 S2 修订文件，没有覆盖 Round 1 审核文件，也没有新增 S3 模型代码或模型结果。

写回本审核前再次确认：

```text
main HEAD = 7041a8273df63b612590bb7a9b53b02984ff7f26
```

未发现分支漂移。

本 Reviewer 没有执行尚未实现的 S3 CLI，也没有声称已经验证模型精度、实际运行时间、OOF Pareto 数值或 Bootstrap 结果。本轮结论是对数学定义、模型合同、配置、阶段边界及修订闭环的静态审核。

---

## 3. Round 1 Required Fix Closure

## 3.1 M2-01：Q5 决策变量与 Q4 输入闭合

**Status: CLOSED / VERIFIED_FROM_REPO**

Round 1 的核心冲突是：Q5 对外只声明 `T,f,w,B_m,m`，但实际损耗函数依赖完整波形及 `wave-v1` 形状特征，导致所谓“五因素最优条件”不能唯一复算 Q4 预测。

Round 2 已明确采用“实测工况点口径”。候选正式定义为：

```text
row_id
+ source file SHA-256 / sheet / Excel row
+ duplicate source mapping
+ normalized waveform SHA-256
+ complete 1,024-point waveform recoverability
+ all Q4 input features
+ feature schema / Q4 model / Pipeline / config hashes
+ condition_group / oof_fold
+ T, f, waveform class, B_m, material
```

该修改满足以下要求：

1. **目标函数输入闭合**：完整波形和全部 Q4 特征不再是隐藏变量；
2. **候选可复算**：来源定位、波形签名、特征快照和模型身份均被列为必需产物；
3. **报告口径正确**：五因素只作为汇总，单点必须表述为“该实测波形轮廓下的推荐工况”；
4. **多文件一致**：总体方案、Q5 合同、实验计划和冻结 JSON 均使用 `observed_operating_point_v1`。

因此，M2-01 已关闭。

---

## 3.2 M2-02：Q5 严格 OOF 稳定性

**Status: CLOSED / VERIFIED_FROM_REPO**

Round 1 的问题是：若每个折模型都预测全部训练候选，则同一候选会被多个见过其 `condition_group` 的模型投票，所谓“跨折稳定”可能主要来自训练内预测。

Round 2 已冻结以下严格流程：

1. 每个候选主损耗只接受对应外层留出模型产生的 `y_pred_oof`；
2. 主 Pareto、两个端点和膝点只使用严格 OOF 分数；
3. 全量重拟合模型只产生参考 Pareto和一致性诊断，不参与折外稳定投票；
4. 每个外层模型只在自己的验证折候选上形成折级 OOF Pareto；
5. `q5-region-v1` 至少得到 `ceil(0.60*K)` 个验证折支持；
6. 严格 OOF 候选表按 `condition_group` 进行 500 次簇 Bootstrap，区域至少 400 次有效且条件 Pareto 入选率不低于 0.50；
7. 单点还必须同时进入 OOF/full-fit Pareto，并通过 OOF 残差与 full/OOF 差的材料×波形 P90 门槛；
8. 模型稳定区域与观测损耗 Pareto 区域的 Jaccard 低于 0.50 时强制降级；
9. 5 个折模型的范围仅允许称为“重拟合扰动范围”，不得冒充 95% 置信区间；
10. 任一门槛失败时，只报告稳定区域和端点，不给唯一推荐。

该流程使训练过候选组的模型无法单独把候选推过稳定阈值，并给出了程序可执行的严格 OOF Pareto、冲突拒绝和降级路径。因此，M2-02 已关闭。

---

## 4. Minor / Follow-up Closure

Round 1 中列出的非阻断改进也已得到处理：

| Follow-up | Round 2 status | Reviewer judgment |
|---|---|---|
| 留一材料/温度的类别编码 | schema 已知未见水平与真正 schema 外值分开处理 | CLOSED |
| Q4“主要子组”口径 | 固定为 `n≥100` 且覆盖至少 3 个实际外层折 | CLOSED |
| RMSLE / MAPE / R² 公式 | RMSLE=`log1p`；MAPE 分母下限 1 W/m³；R² 原尺度 | CLOSED |
| Markdown 与机器配置漂移 | JSON 增加完整网格、Q5 门槛和 8 份合同哈希登记 | CLOSED WITH G3 REPRODUCTION CHECK |
| Round 2 提交范围 | 仅修改 ACTIVE_PROJECT，未新增模型结果 | CLOSED |

冻结配置也明确禁止附件二、附件三参与 Q5 候选域、阈值或结论选择，测试集隔离仍然成立。

---

## 5. G2 Checklist

| G2 验收项 | 结果 | Reviewer 判断 |
|---|---|---|
| 全题统一主线 | PASS | 统一数据、特征、折、Baseline、OOF 和 Q4→Q5 链路清楚 |
| 各问自然衔接 | PASS | Q4 是 Q5 唯一损耗预测接口，前后依赖真实 |
| 避免算法堆叠 | PASS | Baseline 优先、候选有限、失败回退明确 |
| 输入、输出、变量和单位完整 | PASS | Q5 隐藏波形变量已显式闭合 |
| 数学定义自洽 | PASS | 严格 OOF 目标、full-fit 参考和诊断角色已区分 |
| 目标函数回答原题 | PASS WITH STATED DOMAIN | 双目标正确，结论限定于实测联合支持域 |
| 所需数据真实存在 | PASS | 均来自附件一、冻结 Q4 及可追溯派生特征 |
| 求解方法可执行 | PASS | 实测点非支配排序、区域聚合和簇 Bootstrap 可实现 |
| Baseline 清楚 | PASS | Q1–Q5 均有最小可运行路线 |
| Evaluation 能判断好坏 | PASS | OOF、子组、压力测试、冲突和稳定性门槛完整 |
| Failure Conditions 明确 | PASS | 身份、折外性、双 Pareto、P90、区域和敏感性均有阻断 |
| 最后一问有真实路线 | PASS | 不依赖 GA/PSO，也不需要合成未观测波形 |
| 资源与时间可承受 | PASS | CPU-first；Q5 复用 Q4 OOF，不新增模型拟合 |
| 可以安全开始实现 | **YES** | 允许进入 S3 Baseline 闭环 |

---

## 6. Issue Classification

### Critical

**None.**

未发现模型答错题、目标方向错误、关键数据不存在、严重泄漏被允许、最后一问无可执行路径或方案资源不可承受等问题。

### Major

**None.**

Round 1 的 M2-01、M2-02 均已按 Acceptance Criteria 关闭。

### Minor / G3 Implementation Checks

以下事项不阻断 G2，但必须在 G3 的真实代码和产物中核验：

1. **OOF lineage assertion**：逐候选证明生成 `y_pred_oof` 的模型未使用其 `condition_group` 进行拟合或调参，不能只依赖文件命名。
2. **跨折分数可比性**：不同外层模型的 OOF 分数可能存在校准差异；须如合同所定同时提交折级区域、full/OOF 差和观测损耗诊断，不得只展示全局 OOF 膝点。
3. **Bootstrap 解释边界**：若 Bootstrap 复用固定 OOF 预测而不重新拟合模型，应将其解释为“交叉拟合候选表的工况组重采样稳定性”，不能扩大为完整模型参数不确定性的置信区间。
4. **退化边界处理**：代码需显式处理 Pareto 单目标零范围、OOF/full 交集为空、Jaccard 两侧空集和重复四分位边界；触发时按合同降级，不得临时更换阈值。
5. **配置与合同哈希复算**：S3 启动时应由脚本重新计算 `sha256_utf8_lf`，并在 `run_manifest.json` 中保存，而不能只沿用 S2 文档中的自报 PASS。

这些是实现阶段的证据要求，不需要在进入 S3 前继续修改模型路线。

---

## 7. Authorization and S3 Boundaries

Reviewer 正式授权：

```text
G2 = PASS
S2 -> S3 = AUTHORIZED
Next Gate = G3
```

S3 应优先完成冻结实验计划中的 8 个 Baseline / 数据实验：

```text
EXP-S3-DATA-001
EXP-Q1-BASE-001
EXP-Q2-BASE-001
EXP-Q3-DESC-001
EXP-Q3-BASE-001
EXP-Q4-NULL-001
EXP-Q4-BASE-001
EXP-Q5-BASE-001
```

授权边界如下：

- 可以实现 `build_features.py`、`run_q1.py` 至 `run_q5.py` 的 Baseline 接口；
- 必须先形成 Q1–Q5 最小闭环，再进入 S4 候选扩张；
- Q5 Baseline 主损耗必须来自严格 OOF，不得恢复使用全量模型或见过候选组的折模型作为主分数；
- 若分组互斥、OOF 覆盖、候选身份或可复算断言失败，应停止相应实验并记录 FAIL；
- 附件二、附件三仍不得参与特征选择、调参、模型选择或 Q5 门槛制定；
- S3 期间不得因看到结果而修改冻结指标、搜索空间或 Q5 稳定门槛；确需修改时必须记录影响并重新走 Gate；
- `results/raw/` 仍不是 `results/verified/`，不得提前提供给论文作为核验结论。

G3 审核将重点检查：所有小问是否有真实输出、代码是否实现本次批准合同、折外证据是否真实、运行命令与日志是否完整、结果是否可复算，以及 Q5 是否严格遵守 Round 2 修订后的 OOF 规则。

---

## 8. Reviewer Statement

本次审核依据远程固定快照：

`7041a8273df63b612590bb7a9b53b02984ff7f26`

进行独立静态复审。写回前已确认 `main` 分支未漂移。本 Reviewer 未执行未来 S3 模型代码，也未验证尚不存在的模型分数或优化结果。

**最终结论：PASS。允许进入 S3 / G3。**
