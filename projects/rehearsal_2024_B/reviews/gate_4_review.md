# Gate 4 Review — 主模型改进与证据构建

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_B`
- Gate: `G4`
- Stage: `S4 — 主模型改进与证据构建`
- Review Round: `1`
- Reviewed Commit: `b9922fd7752af80fb9ffa1d3ae7118192e0abd20`
- Formal Implementation / Run Commit: `329566748d594e877b57f99cfdddf6796a584d81`
- Prior G3 Review Commit: `a5433257bf94ab651a53b86244d8a86edc72f9e4`
- Verdict: **PASS**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

# 1. Final Verdict

# **PASS — 同意进入 S5 / G5**

经对固定快照 `b9922fd7752af80fb9ffa1d3ae7118192e0abd20` 的独立 G4 审核，当前 S4 已达到停止性能扩张、进入结果核验与冻结阶段的最低充分标准：

1. 改进方向严格来自 S3/O2 的真实失败信号，仅执行 Q2 长尾分类与 Q3 吞吐量非线性/物理残差两个方向；
2. 候选、网格、权重公式、AP-count 对照和时间盒均未越过 G3 授权边界；
3. Q2 即使距离阈值仅约 `0.000998`，仍按完整精度判定失败并回退 `Q2-B1A`，没有事后放宽标准；
4. Q3 的嵌套选择流程相对 `Q3-B1` 将 primary selection score 从 `0.804609` 降至 `0.550330`，相对改善 `31.60%`，三个 repeat 均改善并通过两级偏差护栏；
5. 15 个 primary outer folds、13 个 source-blind LOSO、实际 Q1 nested lineage、AP→system 严格求和和零分母规则均有逐行证据；
6. 正式运行从 clean implementation commit 启动，记录 `1,751` 次拟合、`0` warnings、`0/0` 次官方测试数值读取/预测；
7. 独立产物验证报告 `74/74` 检查通过，并保存 validator、输入产物和输出的 SHA-256；
8. 负结果、最差来源、稀有类别、A03 边界以及 unified/AP-count 的 primary—LOSO 取舍均被保留；
9. O3 已关闭所有 S4 候选路线，决策为 `FREEZE_CANDIDATE`，最终候选栈唯一。

本轮未发现未解决的 Critical 或 Major 问题。因此正式授权：

```text
G4 = PASS
Current Stage may advance: S4 -> S5
Next Gate: G5
```

**重要边界：** 本 PASS 只授权进入 S5 构建 freeze manifest、最终模型、正式验证与证据登记；它本身不等于立即授权读取或推理官方测试集。只有 S5 的完整冻结对象和真实 exactly-once release ledger 均通过机器门禁后，才允许执行一次最终测试推理。

---

# 2. Review Scope and Evidence Status

本轮按照 `.agents/roles/reviewer_agent.md`、`.agents/roles/main_agent.md` 和 `.agents/protocols/optimization_protocol.md`，重点核查：

```text
projects/rehearsal_2024_B/CURRENT.md
projects/rehearsal_2024_B/reviews/gate_4_submission.md
projects/rehearsal_2024_B/work/07_failure_analysis.md
projects/rehearsal_2024_B/work/08_main_model_report.md
projects/rehearsal_2024_B/work/09_evidence_report.md
projects/rehearsal_2024_B/work/optimization/o3_freeze_decision.md
projects/rehearsal_2024_B/configs/s4_candidate_plan.json
projects/rehearsal_2024_B/experiments/main/
projects/rehearsal_2024_B/experiments/comparison/
projects/rehearsal_2024_B/experiments/ablation/
projects/rehearsal_2024_B/experiments/sensitivity/
projects/rehearsal_2024_B/experiments/robustness/
projects/rehearsal_2024_B/src/s4_io.py
projects/rehearsal_2024_B/src/s4_selection.py
projects/rehearsal_2024_B/src/s4_main.py
projects/rehearsal_2024_B/src/s4_validation.py
projects/rehearsal_2024_B/results/raw/main/
projects/rehearsal_2024_B/results/raw/baseline/
projects/rehearsal_2024_B/logs/experiments.md
projects/rehearsal_2024_B/logs/decisions.md
```

写回前已再次确认：

```text
main HEAD = b9922fd7752af80fb9ffa1d3ae7118192e0abd20
```

分支未发生漂移，且被审核快照中不存在 `reviews/gate_4_review.md`。

证据状态：

- 文档、配置、代码、JSON 指标、提交谱系和静态一致性：`VERIFIED_FROM_REPO`；
- gzip JSONL 的逐行内容：由仓库内 validator 解压并复算，网页端没有在本地重新执行 Conda，记为 `SUPPORTED_BY_REPO`；
- 原始 17 个 CSV 未进入 Git，网页端没有独立重跑正式模型；本地运行事实由输入哈希、run manifest、源代码、结果文件与 validation manifest 共同支持，记为 `SUPPORTED_BY_REPO`。

本 Reviewer 没有声称在网页端重新训练模型。

---

# 3. Gate、阶段与快照谱系

## 3.1 状态一致

`CURRENT.md`、用户指定 Gate 和 `gate_4_submission.md` 均指向：

```text
Active Project: projects/rehearsal_2024_B
Current Stage: S4
Gate: G4
Requested transition: S4 -> S5
```

G3 已由 review commit `a5433257bf94ab651a53b86244d8a86edc72f9e4` 正式 PASS，没有跳 Gate。

## 3.2 正式实现与结果可追溯

正式实现和运行来自：

```text
329566748d594e877b57f99cfdddf6796a584d81
```

G4 submission commit 是其直接后继，主要加入正式结果、配置登记、分析报告、O3 和提交文件。正式生成源在运行后未发生改变。

正式运行记录：

```text
runtime_seconds = 4791.800
model_fit_count = 1751
warning_count = 0
eligible_rows/groups = 1250 / 482
outer_folds = 15
LOSO_splits = 13
official_test_numeric_reads/predictions = 0 / 0
```

---

# 4. 改进合理性与候选边界

## 4.1 改进由 Baseline 失败驱动

S3/O2 的主要失败为：

- Q2 fixed-17 联合类别严重不均衡、稀有类别预测坍缩和 source-blind 退化；
- Q3 在 3 AP 和新 source 上尾部误差大，线性 Ridge 与物理 eta 存在 primary—LOSO 取舍。

S4 没有重新打开 Q1，也没有引入深度模型、GNN、外部预训练模型或独立 system head，而只执行：

```text
Q2: 4 个固定 HGB 配置
    + 条件触发的 1 种固定权重公式
    + 1 次相同配置的 Q1 依赖消融

Q3: 4 个 direct HGB
    + 4 个 physics-residual HGB
    + 1 次 AP-count split 对照
```

这符合“Baseline → 失败模式 → 有限改进 → 证据 → 停止”的优化协议。

## 4.2 候选预算和参数未漂移

HGB 共同参数保持：

```text
learning_rate = 0.05
max_iter = 200
min_samples_leaf = 20
early_stopping = false
random_state = 202409
```

只组合：

```text
max_leaf_nodes in {7, 15}
l2_regularization in {0, 1}
```

Q2 权重仅使用一次：

```text
sqrt(N / (17 * n_k)), cap = 5
```

没有第二种权重、阈值调节、类别合并、重采样或扩大网格。

---

# 5. 对比公平性与泄漏审计

## 5.1 相同数据和外层验证

Baseline 与 S4 候选共享：

- 1,250 个 eligible AP 行；
- 482 个严格完整组；
- `source_file + test_id` 不可拆分原子；
- 3 repeats × 5 outer grouped folds；
- 13 个 source-blind LOSO；
- 相同基础特征 schema 和 bounded 主评价口径；
- 相同 Q2 fixed-17 与 Q3 AP/system 指标。

## 5.2 嵌套模型选择

Q2/Q3 的候选参数仅在各 outer-training 边界内通过 inner validation 选择。Q3 的下游 inner selection 继续使用第三层 Q1 cross-fitting。

实际 Q1 lineage：

```text
Total batches = 448
Primary = 240
LOSO = 208
prediction groups ∩ upstream fit groups = 0
downstream validation / held-out groups ∩ upstream fit groups = 0
upstream identity = Q1-B1 / bounded / v1
```

## 5.3 官方测试集未进入选择

S4 入口顺序为：

```text
G3 authorization
-> phase manifest guard
-> training allowlist / canonical path / size / SHA-256
-> approved contract and Baseline snapshot
-> only then numerical training CSV parsing
```

四个官方测试文件注入 S4 manifest 的负向测试均在 parser 前被拒绝。正式运行只数值读取 13 个训练 CSV；官方测试只做字节身份核验。

---

# 6. Q2 审核

## 6.1 结果

| Model | Primary fixed-17 Macro-F1 | Gain vs Q2-B1A | Accuracy | LOSO Macro-F1 | Promotion |
|---|---:|---:|---:|---:|---|
| Q2-B1A Logistic | 0.337654 | — | 0.755200 | 0.1609 | final rollback |
| Q2-M1-HGB | 0.351390 | +0.013736 | 0.786133 | 0.155544 | FAIL |
| Q2-M1W-HGB-WEIGHTED | 0.356656 | +0.019002 | 0.785067 | 0.167729 | FAIL |
| Q2-M1-Q1-ABLATION | 0.350026 | +0.012372 | 0.789600 | 0.152789 | diagnostic only |

## 6.2 Reviewer 判断

冻结晋级条件是：

```text
Macro-F1 absolute gain >= 0.02
AND at least 2/3 repeats improve
AND accuracy drop <= 0.01
```

无权重和加权 HGB 虽通过 repeat 与 accuracy 条件，但 Macro-F1 增益分别只有 `0.0137358442` 和 `0.0190017375`。项目没有把后者四舍五入成 `0.02`，也没有为了保留更复杂模型而修改阈值。

因此：

```text
Q2 final = Q2-B1A
```

这是合格的负结果处理，而不是 S4 失败。稀有类与 LOSO 风险仍然明确保留。

---

# 7. Q3 审核

## 7.1 结果

| Model | Primary S | Relative gain vs Q3-B1 | AP/System ARE90 | AP/System median bias | LOSO S | Decision |
|---|---:|---:|---:|---:|---:|---|
| Q3-B1 Ridge | 0.804609 | — | 0.804609 / 0.348122 | -0.007799 / +0.011741 | 1.3233 | rollback |
| Q3-M1-HGB-UNIFIED | **0.550330** | **31.60%** | 0.550330 / 0.189701 | -0.006036 / -0.001447 | 0.729921 | selected pipeline |
| Q3-M1-HGB-APCOUNT | 0.573131 | 28.77% | 0.573131 / 0.179872 | -0.006072 / -0.002581 | **0.685496** | comparison only |

统一候选：

- 三个 repeat 均优于 Q3-B1；
- AP 与 system 偏差护栏均通过；
- primary selection-score group-bootstrap 区间为 `[0.50902, 0.60766]`；
- bounded AP 预测有限且非负；
- system 预测由 bounded AP 严格求和；
- 独立验证重建 system 结果通过。

AP-count split 的 LOSO 和 system ARE90 更好，但 primary S 更差。项目按冻结 primary 规则保留 unified，没有在结果出现后把选择目标改成 LOSO。

## 7.2 适用范围

统一模型整体 LOSO S 从 Q3-B1 的 `1.3233` 降至 `0.729921`，但最差 held-out source 仍为：

```text
S = 2.159764
```

因此只允许声明 aggregate primary/LOSO 改善，不允许声明每个来源、每个 3 AP 场景均鲁棒。

---

# 8. 消融、敏感性、鲁棒性和错误分析

本阶段已形成与当前结论相关的证据：

- Q2 无 Q1 / 有 Q1：加入 Q1 不改善 HGB；
- Q2 无权重 / 固定权重：权重小幅改善但未达晋级阈值；
- Q3 direct / physics-residual：在冻结八候选中执行嵌套比较；
- Q3 unified / AP-count split：仅执行一次条件对照；
- A03：明确只是 frozen OOF 上的 whole-group evaluation-exclusion diagnostic，不声称删组重训鲁棒性；
- source-blind LOSO：13 个来源完整报告，未省略最差来源；
- failure cases：保存 Q2 高 log-loss 行、Q3 高 AP 相对误差行和高 system 相对误差组，各 20 条。

失败案例只作诊断，没有触发额外模型或阈值。

---

# 9. 结果复算与 Provenance

`post_run_validation.json` 报告：

```text
Global checks = 25 PASS
Selection checks = 14 PASS
Q2 checks = 16 PASS
Q3 checks = 19 PASS
Total = 74 / 74 PASS
```

验证覆盖：

- artifact hashes；
- 正式运行 commit 祖先关系与生成源码未漂移；
- 候选预算和 selection trace 数量；
- Q2 固定 17 维概率、归一化、覆盖和指标复算；
- Q3 AP/system 覆盖、指标复算、零值计数和严格求和；
- 实际上游 lineage；
- Bootstrap 次数；
- Q2/Q3 promotion 与 final candidate 一致；
- `results/verified/` 未被提前写入。

`validation_manifest.json` 进一步保存 validator SHA、执行命令、Git 状态、22 个输入产物哈希和验证输出哈希。

---

# 10. O3 审核

O3 决策为：

```text
FREEZE_CANDIDATE
```

唯一候选栈：

| Question | Frozen candidate |
|---|---|
| Q1 | Q1-B1 Ridge(alpha=1.0, solver=lsqr), bounded v1 |
| Q2 | Q2-B1A LogisticRegression(C=1.0), no Q1 |
| Q3 | Q3 unified HGB selection pipeline；全数据配置规则选择 physics-residual Q3-C3 |

所有授权预算已耗尽，Q2 正确回退，Q3 唯一候选已形成，没有未关闭的 S4 路线。继续扩大模型空间的预期收益不足以抵消选择偏差、时间和证据成本。

O3 满足 G4 的停止条件。

---

# 11. Issue Classification

```text
Critical: 0
Major:    0
Minor:    3
Advisory: 2
```

## 11.1 Critical

**None.**

未发现测试泄漏、结果伪造、核心模型数学错误、题意偏离、严重不公平比较或无法追溯结果。

## 11.2 Major

**None.**

当前核心结论足以支持进入 S5。以下事项必须在结果登记和论文交接中处理，但不需要重做 S4。

---

## 11.3 Minor-01：必须区分“嵌套选择流程表现”与“最终固定配置”

**Priority: P2 — S5 结果登记时处理**

`Q3-M1-HGB-UNIFIED` 的 outer OOF 结果来自每个 outer-training 内独立执行候选选择。`q3_selection.json` 显示，primary 各折实际选择的候选并不全部是 `physics-residual-C3`，其中也出现 residual-C2、residual-C1 和 direct 系列配置。

因此：

```text
S = 0.550330
```

应解释为：

> 不按 AP-count 分模、并在每个训练边界内执行冻结 direct/residual HGB 选择规则的嵌套模型选择流程的 outer OOF 表现。

而：

```text
physics-residual Q3-C3
```

是使用全部 primary inner evidence 按预注册规则得到的最终全数据部署配置。

当前证据**不能把 `0.550330` 无条件写成“固定 residual-C3 在 outer CV 上的直接分数”**，也不能把全部 31.60% 增益归因于 residual 结构本身。

### S5 Acceptance

在 `results/verified/` 和 writing handoff 中至少建立两个不同 Evidence ID：

1. `Q3_NESTED_SELECTION_PIPELINE_PERFORMANCE`：记录 `S=0.550330`、外层 OOF、逐折候选变化和 bootstrap；
2. `Q3_FINAL_FULL_DATA_CONFIGURATION`：记录最终 `physics-residual-C3` 的配置选择规则、45 条 primary inner records 和配置哈希。

推荐论文表述：

> 嵌套选择的统一 HGB 管线将 primary S 降至 0.5503；按全部训练侧内层证据冻结后，最终全量配置为 physics-residual C3。

若未来一定要声称“固定 residual-C3 本身获得 0.5503”，则需要重新构造不泄漏的固定配置评价证据并重新接受相应审核；当前 S5 不应为了更强措辞重新打开模型选择。

---

## 11.4 Minor-02：S5 应独立重算最终配置与 promotion，而不仅复用生产评价函数

**Priority: P2 — G5 前完成**

当前 validator 已经从逐行产物重算 Q2/Q3 指标和 system sum，证据总体充分。但它仍复用生产侧 `evaluate_q2/evaluate_q3`，且对 final candidate 的检查主要是“与 promotion JSON 一致”，并没有完全从 selection traces 独立重建：

- Q2 四配置词典序与全量 C3 选择；
- Q2 `+0.0190017375 < +0.02` 的最终回退；
- Q3 八候选词典序与全量 residual-C3 选择；
- unified/split promotion、repeat count、bias limits 和最终 unified 选择。

这不是当前结果不可信的证据，但 G5 的 verified 层应更独立。

### S5 Acceptance

最终核验脚本应直接读取：

```text
q2_selection.json
q3_selection.json
q2/q3 OOF predictions
S3 Baseline metrics
s4_candidate_plan.json
```

并重新计算上述选择与 promotion，生成机器可读 PASS/FAIL 和 Evidence ID。

---

## 11.5 Minor-03：HGB 实际预处理与 S2 文字合同的缩放措辞不完全一致

**Priority: P2 — G5 前统一模型规格**

S2 人工合同曾写“StandardScaler 仅用于 Ridge/LogisticRegression”，但 S4 HGB 复用了 `make_pipeline()`，该 Pipeline 对数值列也执行 fold-local StandardScaler。

该差异：

- 没有使用验证或测试统计；
- 所有 HGB 候选一致；
- 对树的单调仿射特征缩放通常不改变其基本信息；
- 不构成泄漏或不公平比较。

因此不阻断 G4。但 S5 的最终模型说明必须忠实于代码：要么明确记录 HGB 的实际 fold-local imputation + scaling Pipeline，要么在改变代码时重做受影响结果；不能让论文和冻结模型规格互相冲突。

---

## 11.6 Advisory-01：不要把 group-bootstrap 区间解释为完整模型重训不确定性

当前 1,000 次 Bootstrap 是对已经产生的 OOF 预测按原始组重采样，并保留三个 repeat。它支持样本组重采样下的指标稳定性，但没有在每次 Bootstrap 中重新训练和重新选参。

建议继续使用：

```text
95% group-bootstrap uncertainty interval
```

不要写成覆盖全部训练、选参和部署不确定性的严格置信区间。

## 11.7 Advisory-02：unified 与 AP-count split 的差异属于一次受控模型比较

两者使用同一 outer 证据进行最终取舍，因此不应把 `0.550330` 对 `0.573131` 的差异包装成独立确认性检验或显著性结论。当前按冻结 primary 规则选 unified 是正确的；论文中应把 split 作为取舍分析，而不是第二个“验证集”。

---

# 12. G4 Checklist

| G4 验收项 | Reviewer 结论 |
|---|---|
| 改进来自真实 Baseline 失败 | PASS |
| 只选择 1—2 个高价值方向 | PASS |
| 候选和参数预算受控 | PASS |
| 相同 population / split / metrics | PASS |
| 嵌套选择与 Q1 lineage | PASS |
| 官方测试未用于选择 | PASS |
| Q2 负结果如实回退 | PASS |
| Q3 提升具有实际意义 | PASS |
| 消融、敏感性和 LOSO | PASS WITH CLAIM LIMITS |
| 错误案例与最差来源披露 | PASS |
| 运行与结果可复核 | PASS |
| 未挑最好 seed / 未省略 LOSO | PASS |
| O3=`FREEZE_CANDIDATE` | PASS |
| 可停止扩张并进入 S5 | **YES** |

---

# 13. S5 Authorization and Hard Boundaries

Reviewer 授权主 Agent进入 S5，完成结果核验、模型冻结、一次性测试释放和交接，但必须遵守以下顺序。

## 13.1 先构建完整 Freeze Manifest

至少冻结：

```text
selection_closed = true
Q1/Q2/Q3 model IDs
完整 estimator 参数
训练输入 SHA-256
S3/S4 feature schema SHA-256
Q1/Q3 postprocess versions
Q2 fixed 17-label order SHA-256
split / config / source commit SHA-256
output schema 与行序规则 SHA-256
Q3 pipeline-level evidence 与 final C3 config 的不同身份
```

## 13.2 再实现真实 exactly-once Ledger

正式 release guard 不得只相信调用方手填：

```text
prior_release_count = 0
```

必须从实际 ledger / release state 推导，并至少验证：

- 不存在历史成功 release；
- freeze manifest 文件真实存在且哈希匹配；
- G4 review 为 PASS；
- 四个官方测试文件身份匹配；
- 输出目录尚未存在冲突版本；
- 推理成功后写入不可重复的 release ID、时间、输入/模型/输出哈希；
- 失败重试与成功重复释放有明确区分；
- 第二次正式释放会硬失败。

## 13.3 最终模型与官方测试推理

只有 13.1 和 13.2 均 PASS 后，才允许：

1. 使用全部 eligible 训练数据拟合唯一冻结栈；
2. 保存模型、Pipeline、类别顺序、特征列序和哈希；
3. 执行一次官方测试推理与导出；
4. 不因预测范围、类别比例或人工观感回到 O2/O3/S4 修改模型。

## 13.4 Verified Evidence

G5 前应把可用于绘图和论文的结果放入 `results/verified/`，并为每个核心结论登记 Evidence ID、来源文件、生成 commit、核验脚本和允许/禁止措辞。

特别是 Q3 必须区分：

- 嵌套选择流程的 OOF 性能；
- 最终全量 residual-C3 配置；
- 官方测试无标签预测；
- source-blind 限制。

---

# 14. Final Authorization

```text
Critical = 0
Major = 0

G4 = PASS
S4 -> S5 = AUTHORIZED
Next Gate = G5
```

当前应停止性能扩张。S5 不得新增模型、网格、权重、阈值或 AP-count 结构；如果冻结对象发生影响核心结果的变化，必须记录影响并回到相应 Gate 重新审核。
