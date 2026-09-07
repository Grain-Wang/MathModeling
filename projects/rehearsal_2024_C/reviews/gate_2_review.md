# Gate 2 Review

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_C`
- Gate: `G2`
- Stage: `S2 — 总体方案与模型合同`
- Review Round: `1`
- Reviewed Commit: `2e9517df11b5e0ef861572ca508d8d61d56511f7`
- Verdict: **REVISE**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

## 1. Final Verdict

# **REVISE — 暂不同意进入 S3 / G3**

经对固定快照 `2e9517df11b5e0ef861572ca508d8d61d56511f7` 的独立静态审核，当前 S2 已形成较完整、可执行、CPU 可承受的全题方案。Q1–Q4 的模型合同、Baseline、验证路径和失败回退基本达到 G2 要求；统一数据合同、测试集隔离和实验纪律也明显优于一般竞赛方案。

但是，Q5 合同目前存在两项会直接影响“最优条件”可信度的 **Major** 问题：

1. Q5 声明的五个决策变量不能唯一决定其实际调用的 Q4 损耗目标，完整波形及其派生形状特征成为未显式报告的隐藏决策量；
2. 当前“跨 Q4 外层折模型 Pareto 入选频率”并不是严格的折外稳定性证据，因为同一训练候选会被大多数外层折模型用于训练。

这两项问题不要求推翻总体路线，也不否定“实测联合支持域 Pareto”这一保守方案；但若不在实现前修订，S3 会把一个变量未闭合、稳定性可能偏乐观的 Q5 合同直接固化进代码和结果。

因此：

```text
G2 = REVISE
Current Stage remains: S2
S2 -> S3: NOT AUTHORIZED
Next review after fixes: G2 / Review Round 2
```

---

## 2. Review Scope and Static-Review Limitation

本轮读取并核对了：

```text
.agents/roles/reviewer_agent.md
.agents/roles/main_agent.md
guide/06_reviewer_gate_workflow.md
projects/rehearsal_2024_C/CURRENT.md
projects/rehearsal_2024_C/reviews/gate_1_review.md
projects/rehearsal_2024_C/reviews/gate_2_submission.md
projects/rehearsal_2024_C/work/01_problem_analysis.md
projects/rehearsal_2024_C/work/02_data_audit.md
projects/rehearsal_2024_C/work/03_requirement_matrix.md
projects/rehearsal_2024_C/work/04_solution_plan.md
projects/rehearsal_2024_C/work/models/00_shared_data_validation_contract.md
projects/rehearsal_2024_C/work/models/q1_model_contract.md
projects/rehearsal_2024_C/work/models/q2_model_contract.md
projects/rehearsal_2024_C/work/models/q3_model_contract.md
projects/rehearsal_2024_C/work/models/q4_model_contract.md
projects/rehearsal_2024_C/work/models/q5_model_contract.md
projects/rehearsal_2024_C/work/05_experiment_plan.md
projects/rehearsal_2024_C/experiments/s2_frozen_config.json
```

写回前已确认 `main` 仍指向被审核 commit，没有分支漂移。

本 Reviewer 未在本地重新运行未来的 S3 模型代码；这些入口尚未实现，符合 S2 阶段边界。本次判定基于仓库中的数学定义、模型合同、冻结配置和静态验证记录，不声称已经实机验证模型精度或运行时间。

---

## 3. Positive Findings

### 3.1 阶段和流程状态一致

**Status: VERIFIED_FROM_REPO**

`CURRENT.md`、G1 Review 和 G2 Submission 一致表明：

- ACTIVE_PROJECT 为 `projects/rehearsal_2024_C`；
- G1 已 PASS；
- 当前处于 S2，等待 G2；
- G2 PASS 前禁止实现和运行正式 S3 Baseline；
- 当前未宣称已有模型分数、附件预测或最优工况。

没有发现跳 Gate、伪造结果或阶段状态冲突。

### 3.2 全题主线完整且不是算法堆叠

**Status: VERIFIED_FROM_REPO**

总体方案形成了清楚的数据流：

```text
统一只读输入与哈希
→ 统一 wave-v1 / group-v1
→ 五问 Baseline
→ 有限候选与 OOF 证据
→ 冻结 Q1/Q4
→ Q5 联合支持域 Pareto
```

Q1–Q3 为分类、物理修正和因素分析，Q4 是进入 Q5 的唯一损耗预测接口。方案没有强行把前问输出拼接为后问输入，也没有为了复杂度同时堆叠多种树模型。

### 3.3 共享数据与验证合同较强

**Status: VERIFIED_FROM_REPO**

共享合同已经冻结：

- 原始 XLSX 哈希和只读规则；
- 12,400 条训练记录的一一映射；
- `B_m=max(abs(B))` 主口径与 `B_pp/2` 敏感性；
- 完全重复同折；
- 近形状组和工况组；
- 外层最多 5 折、内层 3 折及 5→4→3 回退；
- 学习型预处理只在训练折拟合；
- 附件二、三禁止参与特征选择、调参和模型选择；
- 逐样本 OOF 输出和运行哈希。

这些控制足以显著降低随机行切分、重复记录和测试集调参造成的虚高结果风险。

### 3.4 Q1 合同基本可执行

**Status: SUPPORTED_BY_REPO**

Q1 使用形状特征和逻辑回归作为透明 Baseline，HistGradientBoosting 与 RandomForest 只作为有限挑战者；主指标为 Macro-F1，并有逐类 Recall、留一材料、相位平移和幅值缩放不变性检查。

其输入、编码、附件四写入要求、指定样本和失败条件均明确。当前未发现会阻断实现的数学问题。

### 3.5 Q2 合同具有可解释性和公平比较

**Status: SUPPORTED_BY_REPO**

传统 Steinmetz 方程和二次温度乘性修正使用同一材料1+正弦波子集、同一折和同一指标。温度修正因子在 25°C 锚定为 1，参数可估计；反变换 smearing 只由训练折残差估计。

合同还限定了唯一的温度交互升级，避免看到结果后无界增加高阶项。当前路线足以开始实现。

### 3.6 Q3 正确限制为调整后关联

**Status: SUPPORTED_BY_REPO**

Q3 明确控制 `log f` 与 `log B_m`，使用 effect coding、两两交互、共同支持和簇 Bootstrap；影响程度通过移除因素后的 OOF 损失增量定义，而不是直接比较不同编码系数。

合同禁止把观测关联写成因果，并在区间重叠时输出候选集合而非强行给唯一最低组合，方向合理。

### 3.7 Q4 Baseline、候选和回退门槛完整

**Status: SUPPORTED_BY_REPO**

Q4 依次设置：

1. 全局中位数；
2. 材料×波形×温度分组中位数；
3. Ridge 对数回归；
4. 有限的 HistGradientBoosting 主候选；
5. 条件触发的 RandomForest 挑战者。

树模型只有在 OOF RMSLE 相对 Ridge 改善至少 2%，且主要子组不恶化超过 10% 时才可替代。失败后回退到更简单模型并缩小适用范围。该合同满足“Baseline 可运行、评价可判断、失败可回退”的 G2 要求。

### 3.8 计算预算现实

**Status: SUPPORTED_BY_REPO**

全部路线基于现有 scikit-learn/SciPy 和 CPU，模型候选有限，S3 优先在约 2 小时内完成五问 Baseline，S4 串行候选上限约 8 小时，并设置单作业 120 分钟硬上限。

当前没有把未验证 GPU 当作必要资源，整体可完成性良好。

---

## 4. Issue Classification

## 4.1 Critical

**None.**

未发现：

- 模型回答错题；
- 使用不存在的核心数据；
- 目标函数方向错误；
- 最后一问完全没有可执行路线；
- 复杂度明显无法在比赛时间内实现；
- 已发生测试集泄漏或伪造结果。

总体路线可以保留，不需要回退到 S1。

---

## 4.2 Major

### M2-01：Q5 声明的决策变量与实际损耗函数输入不闭合

**Evidence status: CONFLICT**

Q5 将决策变量写为：

```text
T, f, waveform class, B_m, material
```

但 Q4 的实际预测函数还使用完整 `wave-v1`，包括：

- `B_pp`、`B_rms`；
- 差分斜率和总变差；
- 平台比例和转折；
- FFT 谐波能量；
- 其他由 1,024 点完整波形得到的形状摘要。

Q5 通过“从附件一选择一条实测行并保留完整波形”绕开了合成波形问题，这个工程选择本身合理；但它意味着真正被优化的候选不是单纯的五元组，而是：

```text
(row_id, T, f, waveform class, B_m, material, full waveform/profile)
```

因此，两个拥有相同或近似 `T,f,w,B_m,m` 的候选，只要详细波形不同，就可能得到不同的 Q4 损耗预测。当前输出却主要报告五个因素，不能唯一复现损耗目标；所谓“最优五因素条件”实际依赖一个未显式列出的波形轮廓。

这属于模型合同中的重要变量缺失，而不是单纯写作问题。

#### Required Fix M2-01

主 Agent 必须明确选择并冻结一种口径：

**方案 A：实测工况点口径（推荐，改动较小）**

- 把 Q5 候选正式定义为包含 `row_id` 和完整波形签名/足够波形描述的“实测工况点”；
- Pareto 点、端点和膝点必须保留 `row_id`、`waveform_signature` 及 Q4 实际使用的关键形状特征；
- 单点推荐必须写成“该实测波形轮廓下的推荐工况”，不能宣称五元组本身对所有同类波形都具有同一损耗；
- 若要总结五因素条件，应按因素区间或稳定候选区域聚合，并说明波形内部差异造成的不确定性。

**方案 B：严格五变量口径**

- 另行定义并验证一个只依赖 `T,f,w,B_m,m` 的 Q5 损耗代理；
- 完整 Q4 模型作为验证/审计模型，不允许把未声明的形状特征暗中带入五变量目标。

不得同时模糊使用两种口径。

#### Acceptance Criteria M2-01

复审时必须满足：

1. Q5 的数学决策向量包含所有会改变目标函数的输入，或有唯一、冻结的聚合规则；
2. 任一输出候选能够由保存的字段完整复算 Q4 预测；
3. 报告的“五因素条件”不会隐藏依赖于未报告完整波形的单点差异；
4. `04_solution_plan.md`、`q5_model_contract.md`、`05_experiment_plan.md` 和冻结配置口径一致。

---

### M2-02：Q5“跨折 Pareto 入选频率”不是严格折外稳定性证据

**Evidence status: CONFLICT**

当前 Q5 程序规定：

1. 候选来自附件一训练行；
2. 使用 Q4 全量模型得到主 Pareto；
3. 再使用每个 Q4 外层折模型对所有候选重复预测；
4. 候选在至少 50% 折模型中进入 Pareto，就可作为稳定推荐。

问题在于：对于某个附件一候选，其 `condition_group` 只在一个外层模型中被留出，而在其余大多数外层模型中参与了训练。以 5 折为例，候选通常被 4 个折模型见过、只被 1 个折模型真正留出。

因此，`3/5` 或更高的 Pareto 入选频率完全可能主要来自训练内预测，不能被解释为“跨折外推稳定”。对 HGB/RF 这类可拟合局部结构的模型，这会特别偏向训练点中的低损耗极值。

当前第 6 步虽然检查候选的 OOF 残差，但没有规定：

- OOF 预测与全量模型预测偏差多大时必须拒绝候选；
- 候选在唯一真正留出模型中不进入 Pareto时是否还能被称为稳定；
- 如何避免 4 个训练内折模型压过 1 个折外模型。

此外，仅用 5 个高度相关的折模型计算 2.5%/97.5% 分位，不应被表述成统计意义上的 95% 置信区间；最多只能称为有限重拟合扰动范围，除非增加足够的分组重采样。

#### Required Fix M2-02

主 Agent 必须冻结一个严格的折外 Q5 验证方案。可选择下列任一可执行方式：

**方式 1：折验证候选 Pareto**

- 每个外层模型只评价其对应外层验证折中的候选；
- 仅使用该折的 OOF 损耗预测形成折级 Pareto；
- 跨折比较稳定的因素区域、分箱或条件模式，而不是把同一个训练候选在见过它的模型中反复计票。

**方式 2：重复分组交叉拟合**

- 预先冻结多次 grouped cross-fitting；
- 每个候选的每次稳定性预测都必须来自未训练该候选 `condition_group` 的模型；
- 只有严格 OOF 预测可以计入 Pareto 入选频率。

**方式 3：主 Pareto 使用单次 OOF 分数，并增加明确一致性门槛**

- 实测候选的主损耗分数直接使用对应 OOF 预测；
- 全量模型预测只作为最终重拟合/部署参考；
- 预先规定全量预测与 OOF 预测、局部 OOF 误差之间的拒绝阈值；
- 不把见过候选的折模型投票称为折外稳定性。

无论选择哪一种方式，建议同时增加“模型预测 Pareto vs 实测损耗 Pareto”的诊断比较。实测损耗不能替代题目要求的 Q4 模型目标，但可以用于识别模型选择出的虚假极端点。

#### Acceptance Criteria M2-02

复审时必须满足：

1. 候选不能仅凭训练过其 `condition_group` 的模型投票达到稳定阈值；
2. 至少存在一条明确、程序可执行的严格 OOF Pareto 验证路径；
3. 对全量模型分数与折外分数的明显冲突有预先冻结的拒绝/降级规则；
4. 5 个折模型的范围不得冒充 95% 置信区间；若报告置信区间，须说明重采样单位、次数和构造方法；
5. Q5 Failure Conditions 能阻止训练点过拟合极值被写成唯一推荐。

---

## 4.3 Minor / Follow-up

这些问题不单独阻断 G2，但建议在本轮修订时一并澄清：

1. **Q4 留一材料/留一温度压力测试的类别编码口径。** 合同同时写了“未知水平报错”和“留一材料/温度”。需区分“schema 已知但当前训练折未出现的水平”与真正未知水平，并说明 OneHot/Ordinal 编码如何处理，否则压力测试可能在接口层直接失败。
2. **主要子组的最小样本量尚未冻结。** Q4 的“任一主要子组 RMSLE 不恶化超过 10%”需要在看到结果前定义 `min_n` 或有效组判据，避免事后选择哪些子组算“主要”。
3. **指标公式宜进入冻结合同。** 建议明确 RMSLE 使用 `log1p` 还是 `log`、$R^2$ 在原尺度还是对数尺度计算、MAPE 的分母保护规则。
4. **机器配置与 Markdown 合同的单一事实源。** `s2_frozen_config.json` 当前记录模型名和候选数量，但完整网格仍只在 Markdown 中。至少应记录合同文件 SHA/版本，或把关键搜索网格与 Q5 新验证参数写入 JSON，防止实现阶段两处漂移。
5. **阶段提交范围。** 本次 commit 同时更新了仓库根目录 `readiness_audit.md`。它不影响模型正确性，但后续 Gate 提交建议尽量把赛题阶段成果限制在 ACTIVE_PROJECT，减少无关 diff 对审核快照的干扰。

---

## 5. G2 Checklist

| G2 验收项 | 状态 | Reviewer 判断 |
|---|---|---|
| 全题统一主线 | PASS | 五问关系清楚，Q4→Q5 数据流明确 |
| 避免孤立算法堆叠 | PASS | Baseline 优先、候选有限、不做无依据集成 |
| 数据与单位完整 | PASS WITH Q5 EXCEPTION | 全题大部分完整；Q5 隐藏完整波形输入未闭合 |
| 数学定义自洽 | REVISE | Q1–Q4 基本自洽；Q5 决策向量与实际目标输入冲突 |
| 目标函数回答原题 | PASS WITH LIMIT | 双目标方向正确，但推荐条件口径需修订 |
| 数据真实存在 | PASS | 全部来自附件一或冻结 Q4，不依赖外部核心数据 |
| 求解方法可执行 | PASS | 实测域非支配排序可实现，计算量可控 |
| Baseline 清楚 | PASS | 五问均有可快速完成的 Baseline |
| Evaluation 能判断好坏 | REVISE | Q5 当前跨折稳定性可被训练内投票偏置 |
| Failure Conditions 明确 | PASS WITH FIX | 大部分充分；Q5 缺少全量/OOF 冲突拒绝门槛 |
| 最后一问有真实路线 | PASS | 路线存在，不要求改用 GA/PSO |
| 资源和比赛时间可承受 | PASS | CPU-first、候选有限、有硬预算 |
| 可安全开始 S3 | **NO** | 需先修复两项 Q5 Major |

---

## 6. Required Fixes Summary

本轮只要求聚焦以下两项，不要求重新设计 Q1–Q4：

```text
RF-1  闭合 Q5 决策变量与 Q4 实际输入，消除隐藏完整波形变量。
RF-2  把 Q5 稳定性改为严格 OOF/未见组证据，并冻结全量模型与 OOF 冲突的降级规则。
```

至少需要更新：

```text
work/04_solution_plan.md
work/models/q5_model_contract.md
work/05_experiment_plan.md
experiments/s2_frozen_config.json
logs/decisions.md
work/revisions/gate_2_response.md
CURRENT.md / 新一轮 G2 submission 状态
```

如修订会改变 Q4 输出接口，也应同步更新 `q4_model_contract.md`，但不得借机无关扩张模型族。

---

## 7. Re-review Requirements

复审时请提供新的固定完整 commit SHA，并保持分支冻结。主 Agent 应在：

```text
work/revisions/gate_2_response.md
```

逐条说明：

- M2-01 选择了哪种 Q5 决策口径；
- 哪些字段能完整复算候选的 Q4 损耗；
- M2-02 采用了哪种严格 OOF 稳定性方案；
- 稳定阈值、拒绝阈值、重采样次数和区间名称；
- 修改文件和对应章节；
- 为何修订后不会使用附件二、三参与选择。

第二轮审核文件应新增为：

```text
reviews/gate_2_review_r2.md
```

不得覆盖本文件。

---

## 8. Reviewer Statement

当前 S2 已接近可通过状态。问题集中在 Q5 的数学闭环和验证公平性，而不是总体选题、Q1–Q4 或计算资源。

在两项 Major 修复并通过复审前，不应运行正式 S3 Baseline；否则需要随后返工 Q5 候选表、Pareto 结果、稳定性证据和论文结论。

**最终结论：REVISE。暂不同意 S2 → S3。**
