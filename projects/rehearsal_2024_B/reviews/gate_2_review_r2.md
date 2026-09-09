# Gate 2 Review — Round 2

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_B`
- Gate: `G2`
- Stage: `S2 — 总体方案与模型合同`
- Review Round: `2`
- Round 1 Reviewed Commit: `5bf0126d03ad0ce81cdd2c6c594a35c68d0f0ebb`
- Round 1 Review Commit: `fe959aff8f53e0add7c473a97f981ffc679e293d`
- Reviewed Commit: `facedf109a9025cb241d9a93074b0467c93143cb`
- Revised Contract Implementation Commit: `43a856642e9405b0c42cf479160f30cd2dae0653`
- Verdict: **PASS**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

## 1. Final Verdict

# **PASS — 同意进入 S3 / G3**

经对固定快照 `facedf109a9025cb241d9a93074b0467c93143cb` 的 G2 Round 2 独立审核，Round 1 提出的两项 Major 均已满足 Acceptance Criteria：

1. 官方测试集已从 S3、O2、S4 和 O3 的执行链中移除，唯一释放点冻结为 `G4 PASS → S5 freeze manifest → 一次最终推理与导出`；
2. Q1→Q2/Q3 的上游模型身份、预测版本、后处理和嵌套 cross-fitting 血缘已经唯一化，并对 primary CV 与 LOSO 分别生成可机读分割和零交集证据。

当前未发现未关闭的 Critical 或 Major。统一主线、逐问模型合同、Baseline、有限候选、嵌套验证、强制 LOSO、测试集治理、成功/停止条件、回退路径和 O1 决策已达到安全启动 S3 全题 Baseline 的最低充分标准。

正式授权：

```text
G2 = PASS
Current Stage may advance: S2 -> S3
Next Gate: G3
```

本 PASS 只授权实现冻结合同中的 S3 Baseline 闭环，不表示 HGB 主候选已获性能晋级，也不授权读取、推理或人工查看四个官方测试集的数值与预测。

---

## 2. Review Scope and Evidence Status

本轮重点读取并交叉核对：

```text
.agents/roles/reviewer_agent.md
.agents/roles/main_agent.md
.agents/protocols/optimization_protocol.md
projects/rehearsal_2024_B/CURRENT.md
projects/rehearsal_2024_B/reviews/gate_2_review.md
projects/rehearsal_2024_B/reviews/gate_2_submission_r2.md
projects/rehearsal_2024_B/work/revisions/gate_2_response.md
projects/rehearsal_2024_B/work/04_solution_plan.md
projects/rehearsal_2024_B/work/05_experiment_plan.md
projects/rehearsal_2024_B/work/models/q1_model_contract.md
projects/rehearsal_2024_B/work/models/q2_model_contract.md
projects/rehearsal_2024_B/work/models/q3_model_contract.md
projects/rehearsal_2024_B/work/optimization/o1_solution_optimization.md
projects/rehearsal_2024_B/configs/s2_experiment_plan.json
projects/rehearsal_2024_B/src/contract_guard.py
projects/rehearsal_2024_B/src/s2_contract_validation.py
projects/rehearsal_2024_B/results/raw/s2/contract_summary.md
projects/rehearsal_2024_B/results/raw/s2/contract_validation.json
projects/rehearsal_2024_B/results/raw/s2/split_registry.json
projects/rehearsal_2024_B/logs/decisions.md
projects/rehearsal_2024_B/logs/experiments.md
```

写回前确认：

```text
main HEAD = facedf109a9025cb241d9a93074b0467c93143cb
```

未发生分支漂移，且 `reviews/gate_2_review_r2.md` 在被审核快照中不存在。

17 个原始 CSV 继续按项目策略不进入 Git，本 Reviewer 未在网页环境独立执行 Conda 或重跑原始数据。因此：

- 文档、配置和代码的静态一致性：`VERIFIED_FROM_REPO`；
- 正式运行计数、输入哈希和 split registry 结果：`SUPPORTED_BY_REPO`；
- 本轮 Gate 判断主要基于可直接审核的算法边界、分割构造、负向测试和机器结果之间的一致性。

---

## 3. Round 1 Major Closure

## 3.1 M2-01：官方测试集释放时点冲突

**Status: CLOSED / VERIFIED_FROM_REPO**

### 3.1.1 S3 提前推理已删除

修订后的 S3 Phase P1 只执行：

- 合同哈希和训练输入白名单校验；
- 训练侧特征 schema dry-run；
- Q1、Q2、Q3 Baseline；
- outer-validation、LOSO 或合成 fixture 上的指标与导出 dry-run；
- O2 Baseline 失败诊断。

S3 不再包含官方测试 Baseline 推理；S4 和 O3 也继续禁止官方测试推理。

### 3.1.2 唯一正式释放点已冻结

当前合同统一规定：

```text
O3 = FREEZE_CANDIDATE
-> G4 PASS
-> enter S5
-> freeze model IDs / parameters
-> freeze training hashes and feature schema
-> freeze Q1/Q3 postprocessing
-> freeze Q2 label order and output schema
-> selection_closed = true
-> prior_release_count = 0
-> exactly one official-test inference/export
-> write release ledger
-> no feedback to O2/O3/S4
```

该时点在总体方案、实验计划、三份模型合同、机器配置、决策日志和 Round 2 submission 中保持一致。

### 3.1.3 机器门禁已实现

`src/contract_guard.py` 对 run manifest 执行以下检查：

- protected phase 中出现任一官方测试文件名即拒绝；
- protected training run 出现非训练 allowlist 文件即拒绝；
- protected dry-run 只接受冻结的三类训练侧/合成来源；
- final release 必须精确包含四个官方测试文件；
- 必须声明 `G4_PASS`、完整 freeze manifest、`selection_closed=true`、首次释放和空反馈目标。

正式合成测试证明：

- 合法 S3 训练 manifest：接受；
- S3 注入官方测试：拒绝；
- freeze manifest 不完整：拒绝；
- 完整、首次且满足 G4 条件的最终释放：接受。

正式 S2 验证记录：

```text
model_fit_count = 0
official_test_numeric_read_count = 0
official_test_prediction_count = 0
official_test_run_manifest_count = 0
```

因此，Round 1 中“测试预测发生在 O2/S4 前”的直接冲突已经消除。

---

## 3.2 M2-02：下游 inner-CV 的嵌套 Q1 特征血缘不足

**Status: CLOSED / VERIFIED_FROM_REPO + SUPPORTED_BY_REPO**

### 3.2.1 上游身份和预测版本已经唯一化

Q2/Q3 在 S3、S4 和 LOSO 中统一使用：

```text
upstream_model_id = Q1-B1
estimator = Ridge(alpha=1.0)
prediction_variant = seq_time_bounded
postprocess_version = q1_clip_0_test_dur_v1
```

Q1-HGB 即使后续在 Q1 自身晋级，也不得替换下游的固定 Q1-B1 特征。因此避免了先根据全局结果选择 Q1 胜者，再对 Q2/Q3 进行二次选择的耦合。

### 3.2.2 S3 固定 Baseline 流程明确

对每个 outer fold：

1. outer-training 内按冻结 inner 3-fold 生成 Q1-B1 bounded OOF；
2. 固定 Q2/Q3 Baseline 只使用这些 OOF 训练特征；
3. 用全部 outer-training 拟合 Q1-B1；
4. 只对 outer-validation 生成 inference 特征；
5. 下游固定 Baseline 对 outer-validation 评价。

S3 Baseline 不进行下游超参数搜索，因此一层 outer-training OOF 足以形成无训练内上游预测的固定底座。

### 3.2.3 S4 下游候选选择增加第三层 cross-fitting

对每个：

```text
outer_repeat x outer_fold x downstream_inner_fold
```

当前冻结流程为：

1. downstream inner-validation 完全隔离；
2. 仅在 downstream inner-training 内运行第三层 3-fold；
3. 第三层为 inner-training 每个组产生一次 Q1-B1 bounded OOF；
4. 完整 downstream inner-training 的 Q1-B1 只用于预测 inner-validation；
5. 全部下游候选共享相同 nested assignments；
6. 选参完成后，按 outer 边界重新生成 outer-training OOF 并只评价 outer-validation 一次。

`lineage_batch()` 会同时拒绝：

- prediction groups 与 upstream fit groups 相交；
- downstream inner-validation 或 outer-validation/held-out groups 与 upstream fit groups 相交。

### 3.2.4 LOSO 已保持 source-blind

每个 LOSO split：

- held-out source 不进入预处理、Q1 拟合、下游拟合和候选选择；
- S4 的 downstream inner 和 nested upstream 只在剩余 source 中构造；
- 不允许复用接触过当前 held-out source 的全局配置。

### 3.2.5 正式 split / lineage 证据闭合

正式结果记录：

| Evidence | Count / Result |
|---|---:|
| Outer folds / assignments | 15 / 1,446 |
| Downstream-inner assignments | 5,784 |
| Primary nested-upstream assignments | 11,568 |
| Primary lineage batches | 240 |
| LOSO splits | 13 |
| LOSO inner assignments | 5,784 |
| LOSO nested-upstream assignments | 11,568 |
| LOSO lineage batches | 169 |
| Total lineage batches | 409 |
| Prediction ∩ fit overlap | 0 |
| Downstream-validation/held-out ∩ fit overlap | 0 |
| Fixed upstream identity | PASS |

Split registry core SHA-256：

```text
88B108D181C2EA3A723303DED3D0E64BACEF7FA482F8322712ED97ED020A6C2D
```

合成负向测试还验证：

- 训练内 Q1 prediction lineage 会被拒绝；
- downstream inner-validation 标签进入上游 fit 会被拒绝；
- 无泄漏 lineage 会被接受。

因此，Round 1 指出的具体 inner-CV 标签回流路径已经被关闭。

---

## 4. Minor Resolution Review

### 4.1 Repeated CV aggregation

**Status: CLOSED**

当前固定：

- 每个 repeat 内先合并 OOF 并独立计算指标；
- 主点估计为三个 repeat 指标的算术平均；
- fold dispersion 与 repeat dispersion 分开命名，仅作描述性离散度；
- group bootstrap 以原始 `source_file + test_id` 为重采样单位；
- 同一组的全部 AP 行与三个 repeat 预测共同抽样，不把三次预测当独立样本。

### 4.2 Raw / bounded 口径

**Status: CLOSED**

- Q1：`seq_time_bounded` 是唯一晋升口径和下游输入；raw 只作审计；
- Q3：`throughput_bounded=max(0, raw)` 是唯一晋升口径；system 主结果严格等于 bounded AP 之和；raw AP/system 只作审计；
- 不允许在看到结果后选择 raw 或 bounded 中更好的一版。

### 4.3 合同文件哈希

**Status: CLOSED**

以下六份人工合同已使用 LF-normalized UTF-8 SHA-256 锁定，并在正式验证中全部匹配：

```text
work/04_solution_plan.md
work/05_experiment_plan.md
work/models/q1_model_contract.md
work/models/q2_model_contract.md
work/models/q3_model_contract.md
work/optimization/o1_solution_optimization.md
```

### 4.4 Feature schema

**Status: ACCEPTED FOR S3**

`feature_schema.json` 不应在没有运行特征引擎时伪造。当前已冻结其生成阶段、路径和必填字段；S3 feature dry-run 必须实际生成：

```text
results/raw/baseline/feature_schema.json
```

至少包含 name、dtype、unit、missing_semantics 和 column_order。

---

## 5. G2 Checklist

| G2 item | Result | Reviewer judgment |
|---|---|---|
| 统一全题主线 | PASS | Q1→Q2/Q3 数据流自然，Q3 AP→system 可加闭环 |
| 每问模型与求解路径 | PASS | 三份合同均覆盖最低结构 |
| 输入真实可获得 | PASS WITH REPO LIMIT | 依赖批准的 S1 审计和固定哈希 |
| 变量、单位、目标和约束 | PASS | NAV、Q1 bounded、Q2 17 类、Q3 两级指标均唯一化 |
| Baseline 可快速实现 | PASS | Dummy/Ridge/Logistic/单参数物理效率均有明确路径 |
| 主模型有针对性且有限 | PASS | HGB 小网格与 direct/residual 上限固定 |
| 验证与失败判断 | PASS | outer、nested、LOSO、晋升阈值、停止与回退完整 |
| 测试集治理 | PASS | 提前推理删除，protected phases 具备门禁合同 |
| Cross-fitting | PASS | primary 和 LOSO 的第三层 split 与血缘已冻结 |
| 计算规模 | PASS | 小样本、固定 Ridge 上游和有限候选，CPU 路线可行 |
| O1 协议 | PASS | 报告完整，Decision=`PROCEED_TO_G2` |
| 可安全进入 S3 | **YES** | 无未解决 Critical/Major |

---

## 6. Issue Classification

```text
Critical: 0
Major:    0
Minor:    3
Advisory: 1
```

### Minor-01：G3 必须验证门禁已接入真实 S3 入口

**Priority: P2 — S3 启动时完成**

当前 `contract_guard.py` 和合成测试证明门禁函数本身可用，但 S3 的实际训练入口尚未实现。G3 不能只接受“有这个 guard 文件”，必须看到：

- 每个 S3 run 在任何 CSV 数值解析前调用 guard；
- run manifest 记录 phase、input_kind、输入路径/文件名、config SHA、guard SHA 和检查结果；
- 训练入口的 input list 只包含训练 allowlist；
- 任一官方测试文件注入测试会使真实入口失败。

这属于 S3 实施验证，不阻断当前 G2。

### Minor-02：S5 的 exactly-once 状态需要 ledger 驱动，而不能只信任调用方声明

**Priority: P2 — 最迟在 G4/S5 释放入口实现前完成**

当前 guard 会检查 manifest 中的 `prior_release_count=0` 和 freeze 字段，但尚未自行读取实际 release ledger，也未核验磁盘上的 `results/verified/freeze_manifest.json` 与其哈希。因此在最终入口实现时必须：

1. 从 ledger 实际状态推导 prior release count，不接受调用方任意填写；
2. 验证真实 freeze manifest 文件存在、内容完整且 hash 匹配；
3. 采用失败安全的写法，避免推理成功但 ledger 未落盘后重复释放；
4. 增加 prior_release_count=1、错误 Gate、非空 feedback target、错误 input_kind 等负向测试。

该缺口不会导致 S3/S4 提前接触测试集，因此不作为 G2 阻断项，但必须在正式释放前关闭。

### Minor-03：最终全量模型配置的冻结规则需在 O3 前明确

**Priority: P2 — S4/O3 前完成**

外层嵌套评价允许不同 fold 选择不同配置。进入最终全量训练前，需要预先明确如何从 nested-CV 证据得到唯一 final configuration，例如：

- 按预注册聚合分数在全量训练组上执行一次训练侧 nested selection；或
- 使用 outer folds 中的稳定多数配置并按固定 tie-break 处理。

规则必须在官方测试释放前冻结并写入 O3/freeze manifest，不能根据测试预测外观选择。

### Advisory-01：门禁可从 basename 升级到规范路径与输入哈希

当前 guard 以 basename allowlist/denylist 为主，已足以防止常规误用。S3 实现时建议同时保存规范化相对路径和 SHA-256，防止重命名或复制文件绕过仅文件名检查。

---

## 7. S3 Authorization Boundary

G2 PASS 后允许执行冻结的 S3 Baseline：

```text
EXP-S3-Q1-B0   median Dummy
EXP-S3-Q1-B1   Ridge(alpha=1)
EXP-S3-Q2-B0   most-frequent joint label
EXP-S3-Q2-B1A  Logistic without Q1
EXP-S3-Q2-B1B  Logistic with fixed Q1-B1 bounded cross-fit
EXP-S3-Q3-B0   median Dummy
EXP-S3-Q3-B1   Ridge with fixed Q1-B1 bounded cross-fit
EXP-S3-Q3-B2   constrained physical eta baseline
```

同时必须：

- 生成并冻结 feature schema；
- 使用当前合同 hash 和 split registry hash；
- 完成 15 个 primary outer folds；
- 完成 13 个 source-blind LOSO；
- 记录实际 upstream lineage；
- 复算 Q3 AP/system sum equality 与指标；
- 完成 `work/06_baseline_report.md`；
- 按优化协议完成 `work/optimization/o2_baseline_diagnosis.md`，且只有 `O2=PROCEED_TO_G3` 才可提交 G3。

当前仍禁止：

- 在 S3 内运行 HGB 主候选或扩大模型网格；
- 使用官方测试 CSV 进行推理、分布检查或预测外观检查；
- 用 Q1-HGB 替换 Q2/Q3 固定的 Q1-B1 bounded 上游；
- 修改评价口径、raw/bounded 选择、17 类顺序或 nested split 来迎合结果；
- 在 O2 前启动 S4 改进。

---

## 8. Evidence Required at G3

G3 至少应检查：

1. 实际 S3 入口在读取训练 CSV 前执行 phase guard；
2. 合同 SHA、config SHA、guard SHA 和 split registry SHA 与本次批准版本一致；
3. feature schema 实际生成且 2 AP/3 AP 对齐正确；
4. 八个 Baseline 均有逐折运行记录和失败处理；
5. 15 个 primary outer folds 和 13 个 LOSO 均完整；
6. Q2/Q3 使用的每条训练侧 Q1 特征具有 OOF lineage，验证侧具有 inference lineage；
7. actual prediction-fit overlap 和 held-out-fit overlap 均为 0；
8. Q2 固定 17 类、support、缺类和 A03 敏感性得到披露；
9. Q3 AP/system 主结果使用 bounded 口径并满足严格求和；
10. 没有官方测试数值读取或预测；
11. O2 报告定位真实失败模式、限制 S4 至多两个主要改进方向，并给出 `PROCEED_TO_G3`。

---

## 9. Final Authorization

```text
G2 = PASS
S2 -> S3 = AUTHORIZED
Next Gate = G3
```

Main Agent 应读取本审核文件后自行更新 `CURRENT.md`；Reviewer 未修改任何主 Agent 产物、配置、代码或结果。