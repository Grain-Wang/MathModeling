# Gate 2 Review — 总体方案与模型合同

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_B`
- Gate: `G2`
- Stage: `S2 — 总体方案与模型合同`
- Review Round: `1`
- Reviewed Commit: `5bf0126d03ad0ce81cdd2c6c594a35c68d0f0ebb`
- Prior G1 Review Commit: `fd6e33b4fa9a7f2de4764ff52272cd62ff52a45b`
- Formal Contract-Validation Commit: `6b88cd1eb6a4776b12b77b859f01d7b8cfaf9a39`
- Verdict: **REVISE**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

## 1. Final Verdict

# **REVISE — 暂不同意进入 S3 / G3**

本次固定快照已经形成较完整的 S2 方案底座：三问沿“信道与门限特征 → Q1 发送机会 → Q2 速率状态 → Q3 AP/系统吞吐量”统一衔接；Q1–Q3 的模型合同、Baseline、有限候选、评价指标、异常敏感性、场景外推和停止条件均已定义；O1 优化报告完成候选比较，并给出 `PROCEED_TO_G2`；机器配置和 split registry 也已生成。

但是，当前仍有两项会直接影响 S3/S4 证据可信度的 **Major** 问题：

1. **官方测试集释放时点在实验计划内部冲突。** `work/05_experiment_plan.md` 的 S3 Phase P1 明确安排“在 O2 和 S4 之前对官方测试执行一次 Baseline 推理”，这与同文件的测试集封存边界、机器配置、总体方案以及 G1 已冻结的“模型和全部选择规则冻结后才进行最终推理”相冲突；
2. **Q1 预测作为 Q2/Q3 输入时，下游模型选择所需的嵌套 cross-fitting 尚未被唯一化。** 当前 registry 只冻结 outer fold 和一层 inner fold。若下游 inner-CV 直接复用 outer-train 上预先生成的 Q1 OOF 特征，inner-validation 组的 Q1 标签可能进入用于生成 inner-training 特征的上游拟合，从而污染下游超参数选择。文档虽写明要在 `inner-training` 重新拟合 Q1 cross-fit，但缺少第二层组分配、上游模型身份、raw/bounded 版本和可审计血缘规则。

这两项均可在 S2 内局部修复，不需要推翻三问主线、特征体系、候选模型或 O1 结论。因此不判 `BLOCK`，但修复并复审前不得启动正式 S3 Baseline。

```text
G2 = REVISE
Current Stage remains: S2
S2 -> S3: NOT AUTHORIZED
Next review after fixes: G2 / Review Round 2
```

---

## 2. Review Scope and Limitation

本轮重点读取并交叉核对：

```text
.agents/roles/reviewer_agent.md
.agents/roles/main_agent.md
.agents/protocols/optimization_protocol.md
projects/rehearsal_2024_B/CURRENT.md
projects/rehearsal_2024_B/reviews/gate_1_review_r2.md
projects/rehearsal_2024_B/reviews/gate_2_submission.md
projects/rehearsal_2024_B/work/01_problem_analysis.md
projects/rehearsal_2024_B/work/02_data_audit.md
projects/rehearsal_2024_B/work/03_requirement_matrix.md
projects/rehearsal_2024_B/work/04_solution_plan.md
projects/rehearsal_2024_B/work/05_experiment_plan.md
projects/rehearsal_2024_B/work/models/q1_model_contract.md
projects/rehearsal_2024_B/work/models/q2_model_contract.md
projects/rehearsal_2024_B/work/models/q3_model_contract.md
projects/rehearsal_2024_B/work/optimization/o1_solution_optimization.md
projects/rehearsal_2024_B/configs/s2_experiment_plan.json
projects/rehearsal_2024_B/src/s2_contract_validation.py
projects/rehearsal_2024_B/results/raw/s2/contract_validation.json
projects/rehearsal_2024_B/results/raw/s2/contract_summary.md
projects/rehearsal_2024_B/results/raw/s2/split_registry.json
projects/rehearsal_2024_B/logs/decisions.md
projects/rehearsal_2024_B/logs/experiments.md
```

写回前已确认：

```text
main HEAD = 5bf0126d03ad0ce81cdd2c6c594a35c68d0f0ebb
```

未发生分支漂移。

本 Reviewer 没有在网页端执行本地 Conda 命令，也没有原始 17 个 CSV 可供重跑。因此：

- 文档、配置、代码与远程结果文件之间的静态一致性使用 `VERIFIED_FROM_REPO`；
- split 数量、哈希和本地运行结果使用 `SUPPORTED_BY_REPO`；
- 本轮两项 Major 均来自仓库中可直接确认的合同冲突或实现规格缺口，不依赖重新训练模型。

---

## 3. Positive Findings

### 3.1 Gate 状态、项目和前序授权一致

**Evidence status: VERIFIED_FROM_REPO**

- 当前唯一活动项目是 `projects/rehearsal_2024_B`；
- G1 Round 2 已 PASS；
- `CURRENT.md`、`gate_2_submission.md` 和用户指定 Gate 均指向 S2/G2；
- 当前没有提前宣称 G2 通过，也没有提交模型分数或官方测试预测。

### 3.2 总体方案形成了真正的三问主线

**Evidence status: VERIFIED_FROM_REPO**

方案不是三个孤立算法，而是：

```text
原始 WLAN 场景与 RSSI
  -> 严格身份和组内拓扑
  -> 折内 RSSI / 门限 / SINR 代理特征
  -> Q1 seq_time
  -> Q2 (NSS,MCS)
  -> Q3 AP throughput
  -> 严格组内求和得到 system throughput
```

Q1 预测进入下游时明确要求使用 OOF/推理预测，Q3 使用真实 MCS/NSS 的题面特许没有扩张到 PER、真实 seq_time 或其他事后字段。三问输入时点和标签边界总体正确。

### 3.3 模型合同覆盖了 Baseline、有限候选和失败条件

**Evidence status: VERIFIED_FROM_REPO**

- Q1：中位数 Baseline、Ridge Baseline、有限 HGB 候选，并包含物理边界、影响排序、消融和方向检查；
- Q2：固定 17 类联合标签、联合 exact accuracy / fixed-label macro-F1 / balanced accuracy、缺类概率对齐和 A03 敏感性；
- Q3：经验中位数、Ridge、机理效率基线以及有限 direct/residual HGB 候选；AP 和系统两级指标均沿用 G1 冻结合同；
- 三问均设置了复杂模型晋升门槛、偏差/子组门槛和失败回退，不存在无边界算法堆叠。

### 3.4 主验证和场景外推方向合理

**Evidence status: SUPPORTED_BY_REPO**

当前计划冻结：

```text
3 repeats × 5 outer GroupKFold
3 inner folds
13 leave-one-source-file-out stress folds
atomic group = source_file + test_id
```

并规定同组 AP 行不跨折、预处理只在训练折拟合、模型比较共享同一切分。LOSO 被设为强制压力测试，而不是只报告好看的插值结果。

### 3.5 O1 优化协议主体合格

**Evidence status: VERIFIED_FROM_REPO**

O1 报告比较了：

- Baseline backbone；
- 有限 HGB 改进；
- 2/3 AP 分模条件分支；
- 原始序列深度模型；
- 外部预训练模型。

报告从收益、风险、资源、验证和回退角度选择了“先完成全题 Baseline，再由 O2 决定最多两个改进方向”，并给出 `PROCEED_TO_G2`。深度序列和外部模型被正确推迟，没有为了先进性突破时间预算。

### 3.6 `nav` 单位冲突已关闭

**Evidence status: VERIFIED_FROM_REPO**

G1 Minor 中的 `nav` 单位冲突已回到题面附录核对并统一为 dBm 门限，不再保留 μs / dBm 双重口径。

---

## 4. Issue Classification

## 4.1 Critical

**None.**

未发现答错赛题、核心变量不可获得、已经发生测试标签泄漏、模型目标与题目相反或方案无法在现有资源下完成等根本问题。

---

## 4.2 Major

### M2-01：官方测试集被安排在模型与选择规则冻结前运行

**Priority: P0 — 立即修复**  
**Evidence status: CONFLICT**

`work/05_experiment_plan.md` 的 S3 Phase P1 明确安排：

```text
9. 对官方测试执行一次 Baseline 推理，只校验行数/键/有限值，不把预测反馈到 O2；
10. 执行 O2。
```

这意味着官方测试推理发生在：

- O2 之前；
- S4 候选比较之前；
- 最终模型、后处理和选择规则冻结之前。

但同一提交中的其他材料又规定：

- 官方测试只用于 final inference/export；
- 模型和全部选择规则冻结后才可进行一次正式推理；
- 测试集不能用于规则、阈值、超参数或模型选择；
- S2 当前没有运行官方测试预测。

因此当前合同内部存在直接冲突。

即使官方测试没有 ground truth，提前生成预测仍可能通过范围、类别分布、极端值、物理直觉或人工观察形成适应性反馈，并影响 O2/S4 的模型、特征、裁剪和回退选择。仅写“不反馈到 O2”不足以建立可审计隔离。

#### Required Fix M2-01

1. 从 S3 Phase P1 中删除全部官方测试推理。
2. 用以下任一种不接触官方测试数值的方式完成导出流程验证：
   - 合成 schema fixture；
   - 从训练集构造只用于接口测试的 mock 表；
   - 对 outer-validation / LOSO 输出执行行数、键、有限值和格式 dry-run。
3. 唯一化官方测试释放点，建议定义为：

```text
G4 PASS 后 / S5 模型与后处理完全冻结后
-> 一次性官方测试推理
-> 只作最终导出，不再回到 O2/O3/S4 选择
```

如项目协议选择其他时点，也必须晚于最终模型、特征 schema、裁剪、类别映射和输出格式冻结，并有 Gate 授权。
4. 同步修订：

```text
work/05_experiment_plan.md
work/04_solution_plan.md（如有相关时点描述）
work/models/q1_model_contract.md
work/models/q2_model_contract.md
work/models/q3_model_contract.md
configs/s2_experiment_plan.json
logs/decisions.md
reviews/gate_2_submission_r2.md
```

5. 在机器合同中增加可复核规则：S3/S4 run manifest 的输入白名单不得包含四个官方测试文件；正式释放前若检测到测试输入，应硬失败。

#### Acceptance Criteria M2-01

复审时必须满足：

- S3 和 O2/O3 前不存在任何官方测试推理步骤；
- 所有文档和机器配置对“final inference only”的定义一致；
- 导出 dry-run 使用合成数据或训练侧验证输出，而不是官方测试数值；
- 官方测试的一次性释放 Gate、冻结对象和禁止反馈规则均明确；
- 机器合同能够检测测试文件是否被提前加载。

---

### M2-02：下游 inner-CV 中的 Q1 特征血缘没有被唯一化，存在嵌套泄漏风险

**Priority: P0 — 立即修复**  
**Evidence status: NOT_VERIFIED / UNDER-SPECIFIED**

当前 Q2/Q3 合同正确要求：

- outer-train 行使用 Q1 cross-fitted `seq_time`；
- outer-validation 使用仅由 outer-train 拟合的 Q1 模型预测；
- Q2/Q3 的 HGB 候选在 inner folds 中选择；
- 所有 Q1 cross-fit 应在 `inner-training` 内重新拟合。

但是，当前 `split_registry.json` 和 `s2_contract_validation.py` 只冻结：

```text
outer split
+ outer-train 内的一层 inner split
```

没有冻结或生成“下游某个 inner-training 内部用于产生 Q1 OOF 特征”的下一层 grouped split，也没有记录逐预测的上游 fit-group 血缘。

这会产生一个具体风险。设某个 outer-train 被分为 A、B、C 三个 downstream inner folds，在评价 C 时：

- 下游 inner-training 是 A+B；
- 下游 inner-validation 是 C。

若直接复用在整个 A+B+C 上预先生成的 Q1 OOF 特征，则 A 或 B 的 Q1 预测模型可能使用过 C 的真实 `seq_time`。这样，C 的上游标签虽然没有直接作为 Q2/Q3 标签参与拟合，却通过 A/B 的训练特征进入下游模型，污染 C 上的超参数选择。

如果改为在 A+B 上训练一个 Q1 模型并对 A+B 产生训练内预测，又违反“禁止 in-sample Q1 特征”的合同。因此必须显式规定嵌套 cross-fitting，而不能留给实现阶段自由解释。

此外，当前合同还没有唯一化：

- 下游使用哪个 Q1 estimator（固定 Ridge、outer-train 内选出的 Q1 胜者，还是全局 OOF 后选出的胜者）；
- 使用 `seq_time_raw` 还是 `[0,test_dur]` 裁剪后的 `seq_time_bounded`；
- 上游模型选择是否会与下游使用同一 outer OOF 结果发生双重选择；
- LOSO 中的上游/下游候选是否完全不接触被留出的 source。

这些差异会改变实验结果和泄漏性质，属于模型合同必须在 S3 前冻结的内容。

#### Required Fix M2-02

主 Agent 应选择并冻结一条可执行路线。推荐最小修复方案如下：

1. **冻结 S3 上游特征版本**：
   - 指定 Q1 estimator ID，例如固定 `Q1-B1 Ridge`；
   - 指定 downstream 使用 raw 或 bounded 预测；
   - 指定裁剪发生在何时、是否进入评价与下游特征；
   - 保存 `upstream_model_id`、`prediction_variant` 和 fit-group hash。
2. **对 S4 下游模型选择实现真正的嵌套 cross-fitting**。对每个：

```text
outer_repeat
outer_fold
downstream_inner_fold
```

必须：

- 只在 downstream inner-training groups 内再生成 Q1 OOF 训练特征；
- Q1 用完整 downstream inner-training 拟合后预测 downstream inner-validation；
- downstream inner-validation 的任何组及其真实 seq_time 不得进入用于生成 downstream inner-training 特征的 Q1 拟合；
- 所有拆分使用 `source_file + test_id` 原子组。
3. 若不希望增加下一层 cross-fit，可采用更简单但必须明确的替代方案：
   - 下游候选选择阶段完全不使用 Q1 特征；或
   - 将“含 Q1 特征的整个下游管线”固定为不调参 Baseline，不在同一数据上做 inner-CV 选择。
4. 对 LOSO 明确：留出 source 的任何行、标签和上游拟合均不得进入模型选择；若使用固定全局配置，必须说明该配置是在何种不接触当前 held-out source 的流程中冻结。
5. 更新机器配置和验证器，至少输出并断言：
   - 每个 downstream inner fold 的 nested upstream split；
   - 每条 Q1 特征对应的 upstream training-group hash；
   - upstream train 与 downstream inner-validation 的组交集为 0；
   - upstream prediction 对 downstream training 行为 OOF；
   - estimator ID、raw/bounded 版本和后处理版本一致。
6. 同步修订：

```text
work/04_solution_plan.md
work/05_experiment_plan.md
work/models/q1_model_contract.md
work/models/q2_model_contract.md
work/models/q3_model_contract.md
configs/s2_experiment_plan.json
src/s2_contract_validation.py
results/raw/s2/split_registry.json
results/raw/s2/contract_validation.json
results/raw/s2/contract_summary.md
logs/decisions.md
```

#### Acceptance Criteria M2-02

复审时必须满足：

- downstream 使用的 Q1 estimator、预测版本和裁剪规则唯一明确；
- S3 固定 Baseline 和 S4 候选选择的上游特征生成流程分别明确；
- 对每个 downstream inner-validation group，可以从机器证据证明它没有出现在任何用于生成 downstream inner-training Q1 特征的上游拟合中；
- 下游训练行使用的 Q1 特征不是训练内预测；
- LOSO 保持 source-blind；
- 相同候选之间使用相同的预注册 nested splits；
- contract validator 能在构造有泄漏的合成血缘时失败，而不是只验证 outer/inner 行数。

---

## 4.3 Minor / S3 Early Requirements

以下事项不单独阻断 G2，但建议随 Round 2 一并唯一化。

### Minor-01：重复 CV 的指标聚合与不确定性单位需明确

当前每个原始组在 3 个 repeat 中会产生 3 次 OOF 预测。应冻结：

- 主点估计是先逐 repeat 计算再平均，还是先对同一组 3 次预测聚合后计算；
- bootstrap 抽样单位是原始 `source_file + test_id`，而不是把 3 次重复预测当成独立样本；
- 折间波动、repeat 间波动和 group bootstrap 区间应分别命名，不应混称统计独立的 95% 置信区间。

### Minor-02：Q1/Q3 的 raw 与 bounded 指标口径需统一

Q1 和 Q3 都准备保存 raw 与 bounded 输出，但当前模型晋升指标没有在所有位置明确使用哪一版。应明确：

- 主 OOF 指标使用 raw 还是 bounded；
- 物理裁剪是模型组成部分还是只作导出保护；
- 下游和系统聚合使用哪一版；
- 报告中两版如何并列，避免事后选择更好结果。

该项可与 M2-02 一起关闭。

### Minor-03：机器验证应覆盖合同文件本身

当前 `contract_validation.json` 主要验证配置、split 和合成指标，但没有看到对三份模型合同和实验计划内容版本的强绑定。建议在 Round 2 配置中登记：

```text
q1_model_contract.md SHA-256
q2_model_contract.md SHA-256
q3_model_contract.md SHA-256
04_solution_plan.md SHA-256
05_experiment_plan.md SHA-256
optimization report SHA-256
```

S3 启动时先复算这些哈希，防止实现配置与人类合同悄然漂移。

### Advisory-01：特征 schema 可在 S3 开始前生成机器清单

建议将最终派生特征名称、dtype、单位、缺失语义和列顺序输出成 `feature_schema.json`。这会显著降低 2 AP/3 AP 对齐、模型保存和最终测试推理中的工程风险，但不是本次 Gate 的独立阻断项。

---

## 5. G2 Checklist

| G2 验收项 | 当前结果 | Reviewer 判断 |
|---|---|---|
| 全题统一主线 | PASS | 三问自然衔接，不是孤立算法堆叠 |
| 输入、输出、变量和单位 | PASS WITH FIX | 主合同清楚；downstream 上游预测版本需唯一化 |
| 数学定义与题目一致 | PASS | Q1/Q2/Q3 目标和 G1 指标合同保持一致 |
| 数据真实存在 | PASS WITH REPO LIMIT | 依据 G1 审计与哈希证据支持 |
| Baseline 明确 | PASS | 三问均有可执行低复杂度 Baseline |
| 候选与预算有限 | PASS | 16 个有界候选，无无界搜索 |
| 验证设计 | REVISE | 下游 inner-CV 的 nested upstream lineage 未闭合 |
| 测试集治理 | REVISE | S3 Phase P1 提前运行官方测试，与冻结合同冲突 |
| Failure Conditions | PASS | 晋升、回退和停止条件总体明确 |
| 最后一问可执行 | PASS | Q3 AP/系统预测与评价路径完整 |
| O1 优化协议 | PASS | 报告完整，决策为 PROCEED_TO_G2 |
| 可安全进入 S3 | **NO** | 两项 Major 修复后复审 |

---

## 6. Required Fix Summary

本轮只要求聚焦两项核心修复，不要求扩展模型族：

```text
RF-1  删除 S3/O2/O3 前的官方测试 Baseline 推理，冻结唯一正式释放点并增加输入白名单硬检查。

RF-2  唯一化 Q1 -> Q2/Q3 的 estimator、raw/bounded 版本和 nested cross-fitting 血缘，防止下游 inner-CV 泄漏。
```

建议至少更新：

```text
projects/rehearsal_2024_B/work/04_solution_plan.md
projects/rehearsal_2024_B/work/05_experiment_plan.md
projects/rehearsal_2024_B/work/models/q1_model_contract.md
projects/rehearsal_2024_B/work/models/q2_model_contract.md
projects/rehearsal_2024_B/work/models/q3_model_contract.md
projects/rehearsal_2024_B/configs/s2_experiment_plan.json
projects/rehearsal_2024_B/src/s2_contract_validation.py
projects/rehearsal_2024_B/results/raw/s2/
projects/rehearsal_2024_B/logs/decisions.md
projects/rehearsal_2024_B/logs/experiments.md
projects/rehearsal_2024_B/CURRENT.md
projects/rehearsal_2024_B/work/revisions/gate_2_response.md
projects/rehearsal_2024_B/reviews/gate_2_submission_r2.md
```

修订期间不得启动正式 S3 模型训练，不得读取官方测试数值进行推理，也不得改变 G1 已冻结的题意、A01–A06 和评价合同来迎合预期结果。

---

## 7. Next Review

下一轮建议使用：

```text
Gate: G2
Review Round: 2
Response: work/revisions/gate_2_response.md
Submission: reviews/gate_2_submission_r2.md
Expected Review: reviews/gate_2_review_r2.md
```

主 Agent 应逐项映射本文件的 RF-1 / RF-2 与 Acceptance Criteria，并提供新的固定完整 SHA。

---

## 8. Reviewer Boundary

本次审核只新增本文，没有修改：

- `CURRENT.md`；
- 总体方案或模型合同；
- 配置和 split registry；
- 代码；
- 日志；
- 原始数据；
- `results/raw/` 或 `results/verified/`。

由 Main Agent 拉取审核意见、保持 S2，并完成修订后重新提交固定 SHA。
