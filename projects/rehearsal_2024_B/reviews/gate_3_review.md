# Gate 3 Review — 全题 Baseline 闭环

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_B`
- Gate: `G3`
- Stage: `S3 — 全题 Baseline 闭环`
- Review Round: `1`
- Reviewed Commit: `e352c4233bb6a974e974ab697481b712a9c83d0b`
- Prior G2 Review Commit: `6504c54782dc33e111800b3166e9e1766cab6549`
- Formal Implementation / Run Commit: `2222cf5f4e17a6dac832c4e65f9c5a60cd01060d`
- Verdict: **PASS**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

# 1. Final Verdict

# **PASS — 同意进入 S4 / G4**

经对固定快照 `e352c4233bb6a974e974ab697481b712a9c83d0b` 的独立 G3 审核，当前 S3 已达到“即使后续改进全部失败，仍有一套完整、可运行、可回退的全题 Baseline”的门控要求：

1. Q1、Q2、Q3 的八个冻结 Baseline 均已实际运行，而不是停留在模型合同或伪代码；
2. 15 个 primary grouped outer folds、13 个 source-blind LOSO splits、Q1→Q2/Q3 的实际 OOF / inference 血缘均有机器产物；
3. Q3 已真实输出 AP 级与系统级结果，系统预测严格等于 bounded AP 预测之和；
4. 逐行 gzip JSONL、指标文件、运行清单、特征 schema、Bootstrap、分层诊断和独立复算结果相互一致；
5. 官方测试文件未被数值解析或预测，真实训练入口已接入输入门禁；
6. O2 先排查数据、切分、泄漏、指标、合同偏离和数值问题，再将剩余失败归因于类别稀疏、输入信息与模型/外推能力；
7. S4 仅保留 Q2、Q3 两个证据驱动且受时间盒约束的改进方向，具有成功阈值、停止条件和回退版本；
8. O2 决策为 `PROCEED_TO_G3`。

本轮未发现未解决的 Critical 或 Major 问题。因此正式授权：

```text
G3 = PASS
Current Stage may advance: S3 -> S4
Next Gate: G4
```

本 PASS 仅授权执行 O2 已限定的 S4 改进和证据构建，不表示 HGB、类别权重、AP-count 分模或任何主候选已经获得性能晋级，也不授权读取、推理或人工查看四个官方测试集的数值与预测。

---

# 2. Review Scope and Evidence Status

本轮按 `reviewer_agent.md` 与 `optimization_protocol.md` 重点读取并交叉核对：

```text
.agents/roles/reviewer_agent.md
.agents/roles/main_agent.md
.agents/protocols/optimization_protocol.md
projects/rehearsal_2024_B/CURRENT.md
projects/rehearsal_2024_B/reviews/gate_2_review_r2.md
projects/rehearsal_2024_B/reviews/gate_3_submission.md
projects/rehearsal_2024_B/work/models/q1_model_contract.md
projects/rehearsal_2024_B/work/models/q2_model_contract.md
projects/rehearsal_2024_B/work/models/q3_model_contract.md
projects/rehearsal_2024_B/work/05_experiment_plan.md
projects/rehearsal_2024_B/work/06_baseline_report.md
projects/rehearsal_2024_B/work/optimization/o2_baseline_diagnosis.md
projects/rehearsal_2024_B/src/s3_*.py
projects/rehearsal_2024_B/experiments/baseline/
projects/rehearsal_2024_B/results/raw/baseline/
projects/rehearsal_2024_B/logs/experiments.md
projects/rehearsal_2024_B/logs/decisions.md
```

写回前已确认：

```text
main HEAD = e352c4233bb6a974e974ab697481b712a9c83d0b
```

分支未发生漂移，且被审核快照中不存在 `reviews/gate_3_review.md`。

证据状态说明：

- 文档、代码、JSON 指标、运行清单和提交谱系的静态一致性：`VERIFIED_FROM_REPO`；
- gzip JSONL 中的逐行结果：由仓库内独立验证器读取并复算，网页端当前未直接解压，记为 `SUPPORTED_BY_REPO`；
- 原始 17 个 CSV 按项目策略不进入 Git，网页端未独立运行 Conda，因此原始数据计数和本地执行事实依赖输入哈希、运行元数据、代码和结果链，记为 `SUPPORTED_BY_REPO`。

本 Reviewer 没有声称在网页端重新执行了模型训练。本次 PASS 来自固定提交中足够完整的代码、运行清单、逐行结果哈希、复算报告和静态审查。

---

# 3. Gate、阶段与提交谱系

## 3.1 状态一致

`CURRENT.md`、用户指定 Gate 与 `gate_3_submission.md` 均指向：

```text
Active Project: projects/rehearsal_2024_B
Current Stage: S3
Gate: G3
Requested transition: S3 -> S4
```

G2 Round 2 已由 `6504c54782dc33e111800b3166e9e1766cab6549` 正式 PASS，没有跳 Gate 或由 Main Agent 自行宣布 G3 通过。

## 3.2 正式运行快照可追溯

正式模型实现和运行来自：

```text
2222cf5f4e17a6dac832c4e65f9c5a60cd01060d
```

提交 G3 的固定快照是其直接后继，主要增加正式结果、实验配置、报告、O2 和 submission。正式训练所使用的七个模型/特征/血缘/评价源文件在正式运行后未发生变化；提交阶段仅增强了独立验证器，使其能够验证“正式运行 commit 为当前提交祖先且模型源未漂移”。

这符合“先冻结实现并运行，再提交结果”的证据链要求。

---

# 4. 实际运行与测试集治理

## 4.1 真实入口门禁已接入

`src/s3_io.py` 的实际顺序是：

```text
构造 phase input manifest
-> validate_phase_input_manifest(...)
-> 核对训练 allowlist、规范路径、字节数和 SHA-256
-> 才调用 pd.read_csv
```

这不是只存在一个未调用的 guard 文件。正式 run manifest 记录：

```text
phase = S3
input_kind = training_csv
training inputs = 13
numeric_read_count_at_guard_return = 0
guard status = PASS
```

四个官方测试文件被逐一注入真实 S3 入口的负向用例，全部在数值解析前拒绝。

## 4.2 正式数据访问边界正确

正式运行记录：

```text
training CSV numeric reads = 13
official test hash-only checks = 4
official test numeric reads = 0
official test predictions = 0
```

官方测试只进行字节数与 SHA-256 身份核验，没有进入特征、异常阈值、模型、后处理、O2 或预测外观反馈。

## 4.3 运行环境与随机性已记录

正式运行清单保存：

- Python 3.11.11；
- scikit-learn 1.7.1；
- NumPy / pandas 版本；
- 单线程；
- 固定 outer / inner / LOSO registry；
- config、guard、split registry、feature schema SHA-256；
- 正式运行起止时间与 265.167 秒运行时；
- 327 次模型拟合；
- warning count = 0。

开发期默认 Ridge 求解器产生病态矩阵告警后，项目在正式运行前将求解器固定为确定性 `lsqr`，同时保持 `alpha=1.0`，并明确登记该变化是数值稳定修复而非性能网格搜索。该处理合理。

---

# 5. 特征与切分闭环

## 5.1 共享特征引擎已真实实现

训练侧实际生成 312 个固定顺序特征，覆盖：

- 测试基础配置；
- focal STA↔AP 的 RSSI 分位数、IQR、样本数和缺失信息；
- peer AP / STA 的置换不变聚合；
- PD、ED、NAV 判决裕量；
- desired-to-peer 信号差；
- AP 数、协议与合法组内上下文。

代码未将 `source_file`、`loc_id`、MAC、原始设备名称或目标/事后统计作为模型输入；这些字段只用于身份、对齐、分层和审计。2 AP 与 3 AP 数据产生相同的列数、名称和顺序。

`feature_schema.json` 对每个特征保存：

```text
name
dtype
unit
missing_semantics
column_order
family
```

并由正式 manifest 绑定 SHA-256。

## 5.2 主切分和外推切分完整

正式运行使用：

```text
Primary: 3 repeats x 5 frozen GroupKFold = 15 outer folds
Atomic group: source_file + test_id
Stress: 13 source-blind LOSO splits
```

所有模型和问题共用冻结 registry，同一测试组内 AP 行不跨折。可学习的插补、缩放和编码均位于当前训练折 Pipeline 内。

## 5.3 Q1→Q2/Q3 的实际血缘闭合

S3 实际使用的下游 Q1 特征唯一为：

```text
Q1-B1
Ridge(alpha=1.0)
seq_time_bounded
q1_clip_0_test_dur_v1
```

每个 outer / LOSO 训练边界内：

1. 内层 3 折为下游训练行生成 Q1 OOF；
2. 完整训练边界拟合 Q1-B1，只预测 outer-validation 或 held-out source；
3. 保存预测组、预测哈希、upstream fit-group SHA、作用域、模型和后处理版本；
4. 运行时检查预测组不进入上游拟合，held-out 组也不进入上游拟合。

正式结果：

```text
Primary lineage batches = 60
LOSO lineage batches = 52
Total = 112
prediction ∩ fit = 0
held-out ∩ fit = 0
fixed upstream identity = PASS
```

因此下游 Baseline 没有使用 Q1 训练内预测或真实 `seq_time`。

---

# 6. 八个 Baseline 的实际覆盖

本轮确认实际运行了 G2 授权的全部八个 Baseline：

```text
Q1-B0  median Dummy
Q1-B1  Ridge(alpha=1.0)

Q2-B0  most-frequent joint class
Q2-B1A Logistic without Q1
Q2-B1B Logistic with Q1-B1 bounded OOF

Q3-B0  median Dummy
Q3-B1  Ridge with Q1-B1 bounded OOF
Q3-B2  constrained physical eta baseline
```

没有运行 HGB、类别权重、AP-count 分模、扩大参数网格或深度模型。

输出覆盖检查为：

- Q1 每个 model×repeat：1,250 个唯一 AP 行；
- Q2 每个 model×repeat：1,250 个唯一 AP 行和固定 17 维概率；
- Q3 每个 model×repeat：1,250 个 AP 行；
- Q3 每个 model×repeat：482 个系统组；
- LOSO 每个模型覆盖全部 1,250 AP 行 / 482 系统组；
- 所有正式预测有限。

因此全题 Completion 已达到 G3 所要求的 100% 基础闭环。

---

# 7. Q1 审核

## 7.1 预测 Baseline 可用

Primary 结果：

| Model | MAE (s) | R² | LOSO MAE (s) | Clip |
|---|---:|---:|---:|---:|
| Q1-B0 | 11.1226 | -0.0172 | 11.2860 | 0 |
| Q1-B1 | **5.5054** | **0.6738** | **7.0266** | 0 |

Q1-B1 相比无信息中位数 Baseline 的 MAE 降低约 50.5%，三个 repeat 波动较小；95% group-bootstrap uncertainty interval 为 `[5.1977, 5.8370] s`。它已经足以作为 Q1 的可回退模型及冻结的下游上游模型。

## 7.2 发送机会分析有实际证据

Q1 提交了 outer-held-out 特征族消融、whole-group permutation 和 Ridge 系数证据。稳定结果为：

- mechanism margins：消融正增益 3/3 repeats；
- peer RSSI：3/3；
- desired RSSI：3/3；
- basic / group-context 的消融和置换证据不一致，因此没有生成强结论。

报告明确限定为“held-out 预测贡献 / 条件关联”，没有写成因果影响。该表达边界正确。

## 7.3 已识别限制

- 2 AP MAE 约 3.2273 s；3 AP 约 6.5463 s；
- 最差 LOSO 来源 MAE 约 9.9464 s；
- 在 O2 两方向预算下，Q1-HGB 未被优先授权。

这不妨碍 Q1 Baseline 作为完整底座。

---

# 8. Q2 审核

Primary 与 LOSO 结果：

| Model | Primary fixed-17 Macro-F1 | Accuracy | Log loss | LOSO Macro-F1 |
|---|---:|---:|---:|---:|
| Q2-B0 | 0.0383 | 0.4832 | 17.8496 | 0.0383 |
| Q2-B1A | **0.3377** | **0.7552** | **1.0042** | **0.1609** |
| Q2-B1B | 0.3343 | 0.7544 | 1.0055 | 0.1580 |

审核判断：

1. Logistic Baseline 明显优于多数类，Q2 已形成实际可运行底座；
2. Q1 OOF 特征没有带来增益，O2 正确地没有把增加 Q1 依赖作为 Q2 主改进；
3. 固定 17 类、概率列顺序、缺类补零、概率和、每类 support 和混淆证据均已保存；
4. support 为 1–2 的多个类别发生坍缩，且 LOSO 显著弱于 primary，这些负结果被完整披露，没有用总体 accuracy 掩盖；
5. A03 所在三个完整组从 OOF 评价中排除后，主要排名和结论基本不变。

Q2 性能并不代表问题已解决，但 G3 的目标是建立可信 Baseline；当前结果足以支撑 S4 的有限非线性改进。

---

# 9. Q3 审核

## 9.1 AP 与系统两级均已实际实现

Primary 结果：

| Model | S=max(AP ARE90, SYS ARE90) | AP ARE90 | SYS ARE90 | LOSO S |
|---|---:|---:|---:|---:|
| Q3-B0 | 1.4518 | 1.4518 | 0.7419 | 1.5587 |
| Q3-B1 | **0.8046** | **0.8046** | **0.3481** | 1.3233 |
| Q3-B2 | 0.8556 | 0.8556 | 0.3570 | **0.9347** |

Q3-B1 是场景内 primary 最佳 Baseline，Q3-B2 在 source-blind LOSO 上更稳定，形成了真实、可解释的“插值精度—物理外推”取舍。

## 9.2 核心数学合同得到验证

正式产物和独立验证器确认：

- bounded AP 预测均有限且非负；
- 每个 model×repeat 有 1,250 个 AP 和 482 个系统组；
- 系统预测严格等于同组 bounded AP 预测之和；
- 存储值与逐行重算值误差为 0 / 数值容差内通过；
- 5 个真实 throughput=0 的 AP 未加入 epsilon，相对误差计算中正确排除并单列绝对误差；
- AP / system 的 signed CDF、`ERROR_90`、未裁剪 `accuracy_90` 和 absolute-relative-error 诊断均已产生。

因此最后一问不是文字路线，而是已经产生实际基础结果。

## 9.3 已识别失败模式

- Q3-B1 的 2 AP ARE90 约 0.5241，3 AP 约 0.9493，三个 repeat 同向；
- B1 最差 LOSO 来源 S 约 4.9790；
- B2 虽然 primary 稍差，但 LOSO 明显优于 B1。

这些结果足以支持 O2 选择“direct HGB 与 physics-residual HGB 对照”，而不是无依据更换算法。

---

# 10. 独立结果复算与证据完整性

`src/s3_validation.py` 不读取原始 CSV，而是直接读取提交的 gzip JSONL 和 JSON 结果，复算：

- Q1 每个 repeat 的 coverage 和 primary MAE；
- Q2 固定 17 类概率宽度、有限性、归一化、标签顺序、coverage 和 Macro-F1；
- Q3 AP / system coverage、非负与有限性、系统行对齐、truth / prediction 求和恒等式和 selection score；
- 正式运行 commit 谱系、模型源漂移、特征 schema、Bootstrap 数量、实际 lineage 和测试集零访问。

提交的 `post_run_validation.json` 状态为 PASS：

```text
Global checks: 21 / 21
Q1 checks: 12 / 12
Q2 checks: 19 / 19
Q3 checks: 31 / 31
```

这使报告中的主要数字能够从逐行结果重新得到，而不是只依赖人工填写的 Markdown 表格。

---

# 11. O2 优化协议审核

## 11.1 诊断顺序合规

O2 先核查并排除了：

1. 输入文件、eligible 数量和严格身份错误；
2. outer / LOSO 划分及 Q1 上游泄漏；
3. Q2 固定标签与概率实现错误；
4. Q3 指标和系统求和错误；
5. 正式运行告警、非有限值和随机性问题；
6. 官方测试反馈。

之后才将剩余问题归为少数类信息不足、source shift、3 AP 难度和线性/物理模型能力限制。符合 `optimization_protocol.md` 的 O2 诊断顺序。

## 11.2 S4 方向数量和范围受控

O2 只选择两个主要方向：

### Direction 1 — Q2 finite HGB

- 只使用已冻结 4 点 HGB 网格；
- primary 默认不含 Q1；
- with-Q1 只作为一次依赖消融；
- 只有无权重 HGB 仍发生 minority collapse 时，才允许对已选配置执行一次固定平方根逆频率权重，权重上限 5；
- 120 分钟时间盒；
- 回退 Q2-B1A。

### Direction 2 — Q3 direct vs physics-residual HGB

- 最多 4 个 direct + 4 个 residual 配置；
- 使用 G2 冻结 nested cross-fitting；
- primary、LOSO、偏差护栏和 system=sum(AP) 同时检查；
- 只允许一次 2 AP / 3 AP 分模对照；
- 120 分钟时间盒；
- 回退 Q3-B1，保留 B2 为物理对照。

Q1-HGB、全题普遍分模、更大网格、深度模型和独立 system head均未获授权。

## 11.3 成功、停止与回退明确

Q2、Q3 均设置了：

- 明确数值晋级阈值；
- 至少两个 repeat 改善；
- accuracy / bias / LOSO / sum consistency 护栏；
- 候选数量和时间盒；
- 未达标即停止并回退 Baseline；
- 不得因结果扩大网格或读取测试集。

O2 决策为：

```text
PROCEED_TO_G3
```

因此满足 G3 的优化协议门槛。

---

# 12. Issue Classification

```text
Critical: 0
Major:    0
Minor:    3
Advisory: 2
```

## 12.1 Critical

**None.**

未发现漏答核心问题、正式结果不存在、官方测试泄漏、人工填写结果、严重切分错误、模型目标错误或必须退回 S2 重建的证据。

## 12.2 Major

**None.**

当前剩余问题不会使 Baseline 失效，也不阻止在冻结边界内进入 S4。

## 12.3 Minor — P2，S4 早期或 G4 前修复

### Minor-01：AP count 的实现表示与人工合同措辞不完全一致

批准的总体方案将 `protocol 和 AP 数`写为 one-hot；当前实际 `CATEGORICAL_FEATURES` 只包含 protocol，`basic__ap_count` 作为数值特征进入 Pipeline。

由于 AP count 当前只有 2 / 3 两个取值，数值二元表示与单个二元 dummy 具有相同的基本可表达空间，且所有 Baseline 使用同一实现，因此不影响本轮 Baseline 闭环和比较公平性，判为 Minor 而非 Major。

处理要求：

- 不得在 S4 中悄悄改变表示后与旧 Baseline 直接比较；
- 若继续保留 numeric binary，应在 S4 实验元数据和最终模型说明中明确该实现口径，并让所有候选共用；
- 若改为 one-hot，必须在同一切分上重跑受影响的 Baseline，报告差异并保持旧结果可追溯。

### Minor-02：A03 当前是评价子集敏感性，不是删组重拟合敏感性

现有 `a03_sensitivity.json` 明确说明：主模型仍保留 A03，只在 primary OOF 结果上整组排除后重新计算指标。该结果可以回答“这些组是否主导现有评价”，但不能证明“删除这些组重新训练后模型仍稳定”。

处理要求：

- 在论文和 O3 中只能称为 `evaluation-exclusion diagnostic`；
- 若 S4 要把 A03 用作训练鲁棒性证据，应对最终 Q2/Q3 候选增加一次完整组删去后的同切分重拟合；
- 若不做重拟合，则保持当前诚实边界，不得扩大结论。

### Minor-03：独立验证运行自身的 provenance 仍可加强

当前 `post_run_validation.json` 能复算主要指标，但没有同时记录：

- validator 文件 SHA-256；
- validator 执行时的 Git commit 与工作树状态；
- 它所消费的全部 gzip / JSON 输入 SHA 列表；
- validation output 自身的独立 manifest。

正式模型源未发生变化，且验证器只读取产物，因此不影响本次 G3 PASS。G4 前建议为主模型验证建立单独 validation manifest，使“正式运行”和“独立复算”各自都有完整 provenance。

## 12.4 Advisory — P3，可选优化

### Advisory-01：在 S4 failure analysis 中补充具体高误差样本/组

当前 O2 已有 AP-count 和 source 级失败证据。为了提高论文解释力，可再从冻结 OOF 中提取若干最高绝对误差 AP / 系统组，按 RSSI 可见性、协议、NAV、AP 数等归类，但不能据此无限新增模型。

### Advisory-02：Q2 support=1–2 的类别不得作强可学习性结论

即使固定权重 HGB 偶然预测到这些类别，也不能把单个样本上的成功描述为稳定少数类能力。相关结果应与 support、fold coverage 和 LOSO 一起报告。

---

# 13. G3 Checklist

| G3 验收项 | 结果 | Reviewer 判断 |
|---|---|---|
| Q1–Q3 是否都有实际输出 | PASS | 八个 Baseline 均有逐行和指标产物 |
| 最后一问是否真实实现 | PASS | Q3 AP/system、CDF、零分母与严格求和均完成 |
| 前后数据流是否闭环 | PASS | Q1-B1 bounded OOF / inference 实际进入 Q2/Q3 |
| 代码是否遵守批准模型合同 | PASS WITH MINOR | 主体一致；AP-count 编码措辞存在轻微偏差 |
| 数据切分是否合理 | PASS | 15 grouped outer + 13 source-blind LOSO |
| 是否存在明显泄漏 | PASS | 实际 lineage 两类 overlap 均为 0 |
| 测试集治理 | PASS | 正式 numeric read / prediction 均为 0 |
| 随机性和配置是否保存 | PASS | registry、seed、线程、版本和哈希均保存 |
| 结果是否可基本复核 | PASS | 独立验证从逐行产物复算主要指标 |
| Baseline 是否足以回退 | PASS | Q1-B1、Q2-B1A、Q3-B1/B2 均可回退 |
| 失败模式是否记录 | PASS | rare class、LOSO、3 AP 与物理取舍均明确 |
| O2 是否符合优化协议 | PASS | 两个有界方向、阈值、时间盒、停止与回退齐备 |
| O2 决策 | PASS | `PROCEED_TO_G3` |
| 可安全进入 S4 | **YES** | 无 Critical / Major |

---

# 14. S4 Authorization Boundary

G3 PASS 后，只允许实施 O2 已选定的两个方向。

## 14.1 Authorized Direction A — Q2

```text
4 个冻结无权重 HGB 配置
-> nested primary / source-blind LOSO
-> 固定 17 类与同一指标
-> 与 Q2-B1A 公平比较
```

只有无权重 HGB 仍满足预定义 minority-collapse 条件时，才允许：

```text
对已选配置执行 1 次固定 sqrt inverse-frequency weighting
weight cap = 5
```

不得继续更改权重公式、阈值或搜索更多类别处理方法。

## 14.2 Authorized Direction B — Q3

```text
4 direct HGB
+
4 physics-residual HGB
```

使用同一冻结 nested registry、bounded 口径、AP/system selection score、bias guard 和 source-blind LOSO。只允许在最佳统一结构上进行一次预注册 2 AP / 3 AP 分模对照。

系统输出继续严格等于 bounded AP 预测之和，禁止独立 system head。

## 14.3 Explicitly Not Authorized

- Q1-HGB 或其他 Q1 新模型；
- 用 Q1-HGB 替换下游固定 Q1-B1；
- 超出 4 / 4 / 8 的网格；
- 新的深度模型、GNN、外部预训练模型；
- 全题普遍 AP-count 分模；
- 改变 17 类标签、split registry、Q3 指标或 raw/bounded 主口径；
- 在 G4 PASS 和 S5 freeze manifest 前读取/预测官方测试集；
- 把 `results/raw/baseline/` 覆盖或迁入 `results/verified/`。

## 14.4 G4 前仍需完成

S4 应形成并提交：

```text
work/07_failure_analysis.md
work/08_main_model_report.md
work/09_evidence_report.md
experiments/main/
experiments/comparison/
experiments/ablation/
experiments/sensitivity/
experiments/robustness/
results/raw/main/
work/optimization/o3_freeze_decision.md
```

O3 必须确定唯一最终候选、最终全量配置规则和停止决策；只有 `FREEZE_CANDIDATE` 才能提交 G4。

G2 遗留的真实 release-ledger exactly-once 门禁仍须在 G4/S5 正式测试入口前完成，但不是当前 G3 阻断项。

---

# 15. Final Authorization

```text
G3 = PASS
S3 -> S4 = AUTHORIZED
Next Gate = G4
```

Main Agent 可在拉取本审核文件后更新 `CURRENT.md` 并启动上述两个受限 S4 方向。不得把本次 PASS 解释为主候选已经晋级或测试集已经释放。
