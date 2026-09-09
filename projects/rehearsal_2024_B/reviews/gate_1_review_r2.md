# Gate 1 Review — Round 2

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_B`
- Gate: `G1`
- Stage: `S1 — 题意拆解与数据审计`
- Review Round: `2`
- Round 1 Reviewed Commit: `512e461033c8378f1e591912b4992d8486bde396`
- Round 1 Review Commit: `e9253ce15a7b296298cf68c61b65357b55f1a1ed`
- Reviewed Commit: `9f0a209f55351aff306aa7ecd6d38486fcf43352`
- Formal Audit Implementation Commit: `affff4fa6ef2d9a5431adac6e7341c993b946f4d`
- Verdict: **PASS**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

## 1. Final Verdict

# **PASS — 同意进入 S2 / G2**

经对固定快照 `9f0a209f55351aff306aa7ecd6d38486fcf43352` 的 G1 Round 2 独立静态复审，Round 1 提出的两项 Major 均已按 Acceptance Criteria 关闭：

1. Q3 已从单一逐 AP 回归任务扩展为完整的两级输出和评价合同，包括 185 个 AP 吞吐量、75 个严格系统组吞吐量、AP/系统两级有符号误差 CDF、`ERROR_90` 和 `accuracy_90`；
2. 数据身份审计已从“只检查组内行数”升级为“预期行数 + 精确 AP ID 集合与次数 + 复合键唯一”的严格检查，同时区分文件内完全重复和跨文件规范化行/组指纹。

当前没有未解决的 Critical 或 Major 问题。题意、数据层级、异常处理、测试集边界、下游 OOF 传递和验证需求已经明确到足以安全开始 S2 总体方案与模型合同设计。

因此正式授权：

```text
G1 = PASS
Current Stage may advance: S1 -> S2
Next Gate: G2
```

本 PASS 只表示题意和数据基础已达到进入方案设计的最低充分标准，不表示任何模型已经被选定、训练或验证，也不授权使用官方测试集进行特征选择、调参或模型选择。

---

## 2. Review Scope and Limitation

本轮重点读取并交叉核对：

```text
.agents/roles/reviewer_agent.md
.agents/roles/main_agent.md
projects/rehearsal_2024_B/CURRENT.md
projects/rehearsal_2024_B/reviews/gate_1_review.md
projects/rehearsal_2024_B/reviews/gate_1_submission_r2.md
projects/rehearsal_2024_B/work/revisions/gate_1_response.md
projects/rehearsal_2024_B/work/01_problem_analysis.md
projects/rehearsal_2024_B/work/02_data_audit.md
projects/rehearsal_2024_B/work/03_requirement_matrix.md
projects/rehearsal_2024_B/src/s1_data_audit.py
projects/rehearsal_2024_B/results/raw/s1/audit_summary.md
projects/rehearsal_2024_B/results/raw/s1/data_profile.json
projects/rehearsal_2024_B/results/raw/s1/quality_checks.json
projects/rehearsal_2024_B/results/raw/s1/identity_checks.json
projects/rehearsal_2024_B/results/raw/s1/q3_target_contract.json
projects/rehearsal_2024_B/logs/decisions.md
projects/rehearsal_2024_B/logs/experiments.md
```

写回前已确认：

```text
main HEAD = 9f0a209f55351aff306aa7ecd6d38486fcf43352
```

未发生分支漂移。

17 个原始 CSV 按项目策略未进入 Git，因此本 Reviewer 无法在网页端独立重跑原始数据审计。对具体数据计数和数值统计，本轮采用 `SUPPORTED_BY_REPO`：依据固定输入哈希、审计代码、机器可读 JSON、运行元数据和日志判断；对文档、代码与结果之间的一致性采用 `VERIFIED_FROM_REPO`。无法重跑本身不构成失败，因为关键断言的逻辑、作用域、计数和失败样例均已进入远程快照。

---

## 3. Round 1 Major Closure

## 3.1 M1-01：Q3 系统吞吐量、CDF 与 90% 精度遗漏

**Status: CLOSED / VERIFIED_FROM_REPO**

Round 2 已明确冻结两级目标：

### AP 级

```text
Key: source_file + test_id + ap_id
Training targets: 1,250
Official Q3 test outputs: 185
Unit: Mbps
```

### 系统级

```text
Key: source_file + test_id
Training targets: 482
Official Q3 test outputs: 75
Unit: Mbps
Aggregation: 同一严格完整组内所有 AP 吞吐量求和
```

其中训练系统组按 AP 数分为 196 个二 AP 组和 286 个三 AP 组；Q3 测试系统组为 40 个二 AP 组和 35 个三 AP 组。机器合同同时确认 AP 目标无缺失，其中 5 个真实值为 0；482 个系统目标均非零，可用于系统级相对误差评价。

两级评价合同已经唯一化：

```text
r_i = (yhat_i - y_i) / y_i
F(x) = count(r_i <= x) / n
ERROR_90 = 升序后第 ceil(0.90*n) 个值（最近秩，不插值）
accuracy_90 = 1 - ERROR_90
```

并已预先规定：

- AP 和系统粒度分别计算，不混合样本；
- 并列值保留，不因结果改变分位数算法；
- `accuracy_90` 不裁剪，可能出现超过 100% 或负值时如实披露；
- 真实吞吐量为 0 的 AP 从相对误差 CDF 和 `ERROR_90` 中排除，并披露数量、单列绝对误差；
- 绝对相对误差 CDF、MAE、RMSE、R²仅作辅助，不能替代题面主指标。

上述内容已同步进入问题分析、数据审计、需求矩阵、决策日志和 `q3_target_contract.json`。需求矩阵现在具有独立的 `R04-AP`、`R04-SYS`、`R04-METRIC-AP` 和 `R04-METRIC-SYS`，因此后续 S2 不会再把 Q3 缩减成单纯的 185 个 AP 回归值。

结论：M1-01 已关闭。

---

## 3.2 M1-02：AP 组身份、复合键与重复范围不足

**Status: CLOSED / SUPPORTED_BY_REPO**

审计实现现在对以下范围分别执行严格身份检查：

- 原始训练；
- A01 隔离后的 eligible 训练；
- 四个官方测试集合计；
- Q3 两个测试集合计；
- 每一个官方测试文件。

严格检查包含：

1. `source_file`、`test_id`、`ap_id` 非空；
2. `ap_id` 满足 `ap_数字` 格式；
3. `(source_file, test_id, ap_id)` 复合键唯一；
4. 二 AP 组恰含 `ap_0`、`ap_1` 各一次；
5. 三 AP 组恰含 `ap_0`、`ap_1`、`ap_2` 各一次；
6. 组内行数同时符合预期。

机器结果记录：

| 范围 | 行数 | 组数 | 严格有效组 | 严格无效组 |
|---|---:|---:|---:|---:|
| 原始训练 | 1,252 | 484 | 482 | 2，均为 A01 |
| eligible 训练 | 1,250 | 482 | 482 | 0 |
| 官方测试 | 336 | 136 | 136 | 0 |
| Q3 测试 | 185 | 75 | 75 | 0 |

eligible 训练和官方测试中的空身份、非法 AP ID、重复复合键均为 0。原始训练仅有 A01 两个不完整组失败，隔离后不存在 AP 身份缺失、重复 AP 或伪完整组。

重复审计也已明确作用域：

- 文件内：按每个训练 CSV 的全部原始列检查完全重复，结果为 0；
- 跨文件：在相同 AP 数分层内，排除 provenance 键和预测占位列，对共同语义字段进行确定性规范化并生成 SHA-256 行指纹和组指纹；
- 二 AP：392 个行指纹、196 个组指纹，均唯一；
- 三 AP：858 个行指纹、286 个组指纹，均唯一；
- 跨文件重复行簇和组簇均为 0。

如果未来派生数据出现等价簇，合同要求整簇绑定到同一验证折，不得静默删除；若考虑删除，还必须报告敏感性。该规则足以支持 S2 的防泄漏切分设计。

正式审计元数据记录实现提交为 `affff4fa6ef2d9a5431adac6e7341c993b946f4d`，运行前工作树为空；17/17 输入文件在审计前后名称、大小与 SHA-256 均通过且未改变。正式审计之后到本次 Reviewed Commit 之间没有修改审计实现，只补充了提交材料、结果身份字段和日志。

结论：M1-02 已关闭。

---

## 4. G1 Checklist

| G1 验收项 | 结果 | Reviewer 判断 |
|---|---|---|
| Q1–Q3 是否逐项解释 | PASS | 三问任务、输出及依赖完整 |
| 输入、输出、变量和约束 | PASS | AP/系统两级键、数量和单位已定义 |
| 小问依赖与输入时点 | PASS | Q1 下游只用 OOF；Q3 的真实 MCS/NSS 特许未外扩 |
| 字段、规模和单位 | PASS WITH MINOR | 主字段清楚；`nav` 单位存在一处文档冲突，见 Minor-01 |
| 缺失、异常和重复 | PASS | A01–A06、严格身份及跨文件重复范围完整 |
| 数据泄漏识别 | PASS | 同组不跨折、事后字段白名单、测试集封存均明确 |
| 测试集边界 | PASS | 只审计结构、非空和身份，不用数值分布选模 |
| 各问数据充分性 | PASS WITH LIMITS | 三问均可开始设计，稀有类和场景外推限制已登记 |
| 需求追踪完整 | PASS | Q3 两级输出和正式指标已单独映射 |
| 可安全开始 S2 | **YES** | 无未解决 Critical/Major |

---

## 5. Issue Classification

### Critical

**None.**

### Major

**None.**

### Minor

#### Minor-01：`nav` 单位在文档与机器 schema 中冲突

**Priority: P2 — S2 开始时修复，不阻断 G1**

`work/02_data_audit.md` 将 `nav` 写为 `μs`，而审计脚本和 `data_profile.json` 将其记录为 `dBm supplied scenario threshold`。该变量的样本值为负数档位，后续又将被用于门限/RSSI关系解释，因此 S2 模型合同不能保留两种单位口径。

处理要求：

1. 在 S2 编写特征与模型合同前回到题目附录核对 `nav` 的业务定义和单位；
2. 统一修正 `work/02_data_audit.md`、字段字典、后续模型合同和论文符号表；
3. 若题面定义与当前机器 schema 不一致，记录一条决策，说明采用口径及影响；
4. 不得仅因变量名联想到传统 WLAN NAV 定时器，就忽视本题字段实际定义和数值范围。

该冲突没有改变本轮组身份、重复检查或 Q3 输出合同，故不阻断 G1；但必须在任何涉及物理解释或特征工程的 G2 合同冻结前关闭。

#### Minor-02：团队实名责任分配仍未完成

**Priority: P2 — 协作开始前补齐**

当前功能角色可支撑技术流程，但最终数据、代码、论文和提交责任仍需由人类队员明确。该事项不影响 S1 科学正确性。

### Advisory

- 在正式比赛设备上完成一次 `environment.yml` clean rebuild；
- 后续所有 Q3 指标实现增加合成测试，覆盖零分母、并列值、90% 最近秩和有符号误差导致异常显示范围的情况；
- 对 Q2 全局标签集和罕见类别缺折规则使用机器配置，而不是只写在 Markdown 中。

---

## 6. S2 Authorization and Mandatory Boundaries

Reviewer 正式授权：

```text
G1 = PASS
S1 -> S2 = AUTHORIZED
Next Gate = G2
```

S2 必须在任何正式训练前完成并冻结：

1. `work/04_solution_plan.md`：形成 Q1→Q2/Q3 的统一技术主线；
2. `work/models/*_model_contract.md`：逐问明确输入白名单、输出、单位、数学定义、Baseline、评价和失败条件；
3. `work/05_experiment_plan.md`：冻结切分清单、随机种子、候选数量、比较顺序和停止条件；
4. `work/optimization/o1_solution_optimization.md`：读取并遵守 `.agents/protocols/optimization_protocol.md`，完成 O1 决策；
5. 将 `source_file + test_id` 作为不可拆分原子组，所有 RSSI 汇总、缺失处理、编码和缩放在训练折内拟合；
6. 将 leave-one-source-file-out 作为强制场景外推压力测试；
7. 冻结 Q2 全局联合标签全集、排序、缺类失败/回退、固定标签集 macro-F1、每类 support 和 A03 保留/排除敏感性；
8. 冻结 Q3 AP/系统两级 signed CDF、`ERROR_90`、`accuracy_90`、零分母和辅助绝对误差实现；
9. 修复并统一 `nav` 单位；
10. 继续封存四个官方测试集，不得使用其数值分布、空白输出或最终预测反向选择方案。

本阶段不得把 `PASS` 解释为可以跳过 G2 直接训练主模型。只有 G2 对方案、模型合同、实验计划和 O1 优化报告给出 PASS 后，才能进入 S3 Baseline 实现。

---

## 7. Review Write-back Boundary

本 Reviewer 只新增本审核文件：

```text
projects/rehearsal_2024_B/reviews/gate_1_review_r2.md
```

未修改 `CURRENT.md`、问题分析、数据审计、审计代码、原始数据或结果。由 Main Agent 拉取本审核后自行更新阶段状态并进入 S2。
