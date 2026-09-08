# Gate 3 Review — 全题 Baseline 闭环

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_C`
- Gate: `G3`
- Stage: `S3 — 全题 Baseline 闭环`
- Review Round: `1`
- Reviewed Commit: `17cefbfe7bda13fa97f2eb19decc1abd02529597`
- Evidence Commit: `db02f7dfd75b957f20fc65d0b69472e50d87c60e`
- Recorded Implementation Commit: `0d36ef8c16f3214b16d8580333f2925aaff45191`
- Verdict: **PASS**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

## 1. Final Verdict

# **PASS — 同意进入 S4 / G4**

经对固定快照 `17cefbfe7bda13fa97f2eb19decc1abd02529597` 的独立静态审核，当前 S3 已达到 `.agents/roles/main_agent.md` 与 `.agents/roles/reviewer_agent.md` 对 G3 的核心要求：

1. G2 批准的 8 个数据与 Baseline 实验均已真实实现并产生结果；
2. Q1–Q5 均有可运行代码、逐样本或逐候选输出、指标及基本验证；
3. Q4 的严格 OOF 预测已经真实传递到 Q5，最后一问不是文字方案；
4. 数据切分、同组隔离、随机种子、配置、实现提交、环境、输入输出哈希和运行日志均有可追溯证据；
5. 独立验证脚本能够重新计算 Q1–Q4 核心指标和 Q5 严格 OOF Pareto 成员；
6. 未发现附件二、附件三进入特征选择、拟合、调参、模型选择或 Q5 阈值制定；
7. Q5 出现稳定性失败信号时，系统按冻结合同拒绝唯一推荐，而不是放宽阈值或隐藏负结果。

当前不存在未解决的 Critical 或 Major 问题。因此正式授权：

```text
G3 = PASS
Current Stage may advance: S3 -> S4
Next Gate: G4
```

本 PASS 只表示“全题 Baseline 底座已经真实闭环，可以安全开展针对性改进”，不表示当前 Baseline 已达到最终竞赛精度，也不表示 Q5 已获得唯一最优工况，更不表示 `results/raw/` 已成为可直接写入论文的 verified 结果。

---

## 2. Review Scope and Limitation

本轮按 Reviewer 协议重点读取和核对：

```text
.agents/roles/reviewer_agent.md
.agents/roles/main_agent.md
projects/rehearsal_2024_C/CURRENT.md
projects/rehearsal_2024_C/reviews/gate_2_review_r2.md
projects/rehearsal_2024_C/reviews/gate_3_submission.md
projects/rehearsal_2024_C/work/03_requirement_matrix.md
projects/rehearsal_2024_C/work/06_baseline_report.md
projects/rehearsal_2024_C/work/models/
projects/rehearsal_2024_C/experiments/s2_frozen_config.json
projects/rehearsal_2024_C/experiments/baseline/
projects/rehearsal_2024_C/src/
projects/rehearsal_2024_C/results/raw/baseline/
projects/rehearsal_2024_C/results/raw/s3/
projects/rehearsal_2024_C/logs/experiments.md
projects/rehearsal_2024_C/logs/decisions.md
```

审核开始及写回前均确认：

```text
main HEAD = 17cefbfe7bda13fa97f2eb19decc1abd02529597
```

未发现分支漂移。

实验运行清单统一记录实现提交 `0d36ef8c16f3214b16d8580333f2925aaff45191`。该提交是当前审核快照的祖先；实现代码、冻结配置和 Baseline 实验描述在运行后没有发生影响结果的改变。当前最新提交新增的是绘图与配色 Guide，不改变 S3 模型证据。

本 Reviewer 没有在网页端重新执行本地 Conda 实验。以下运行结论来自仓库中的源码、运行清单、日志、逐样本结果、文件哈希和独立复算报告，属于静态、可追溯审核，而不是 Reviewer 实机复现声明。

---

## 3. Evidence Summary

### 3.1 阶段状态与提交对象

**Status: VERIFIED_FROM_REPO**

`CURRENT.md`、`gate_3_submission.md` 与实际目录一致表明：

- G2 Round 2 已 PASS；
- 当前阶段为 S3，等待 G3；
- S3 结果尚未写入 `results/verified/`；
- G3 PASS 前禁止运行 S4 候选或放宽冻结门槛；
- Q5 Jaccard 失败已被登记为真实限制。

没有发现跳 Gate、把 raw 结果冒充 verified，或在审核前自行宣布进入 S4。

### 3.2 实现与实验覆盖

**Status: VERIFIED_FROM_REPO**

仓库中存在实际实现：

```text
src/s3_common.py
src/build_features.py
src/run_q1.py
src/run_q2.py
src/run_q3.py
src/run_q4.py
src/run_q5.py
src/run_s3_baselines.py
src/verify_s3_outputs.py
src/test_s3_synthetic.py
```

`experiments/baseline/` 中存在 8 个冻结实验描述，`results/raw/baseline/` 中存在对应的 8 个运行证据目录：

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

每个目录均有 `config.json`、`metrics.json`、`run_manifest.json` 和 `stdout.log`，主要模型实验还保存逐样本输出、模型文件、折谱系和子组结果。

### 3.3 运行清单与复现链

**Status: VERIFIED_FROM_REPO**

8 份权威 `run_manifest.json` 一致记录：

- `status=PASS`；
- `exit_code=0`；
- `git_commit=0d36ef8c16f3214b16d8580333f2925aaff45191`；
- `implementation_git_dirty_at_finish=false`；
- Conda 环境 `math_modeling`；
- Python 3.11.11、NumPy、pandas、SciPy、scikit-learn、openpyxl 版本；
- 实际命令、种子、起止时间和运行时；
- 冻结合同哈希；
- 输入与输出 SHA-256。

统一入口 `run_s3_baselines.py` 按冻结依赖顺序调用全部 8 个实验，并支持重复构建数据产物。提交材料给出的两条复现命令清楚、可复制。

### 3.4 数据构建、折与泄漏控制

**Status: VERIFIED_FROM_REPO**

数据流水线实际完成：

- 12,400 条训练记录；
- 48 个 Q4 数值特征和 30 个 Q1 shape-only 特征；
- 4,323 个 `condition_group`；
- Q1 与回归任务各 5 个外层折；
- 1 条额外精确重复记录被识别；
- `near_shape_group`、`condition_group` 和精确重复均未跨相应外层折；
- 特征表、折分配与 schema 重建 SHA-256 一致。

源码显示：附件一以只读方式生成特征；附件二、三、四只在启动完整性检查中核验哈希，不进入模型数据表。各任务在外层和需要的内层验证中均对组交集做显式断言。

因此，本次静态审核未发现明显测试集泄漏、全数据预处理泄漏或同组跨折泄漏。

### 3.5 Q1 Baseline

**Status: VERIFIED_FROM_REPO**

Q1 已实现 shape-only 多项逻辑回归：

- 外层 `StratifiedGroupKFold`；
- 内层 3 折分组选参；
- 标准化位于 Pipeline 内；
- 主输入不含温度、频率、材料或损耗；
- 保存 12,400 条 OOF 概率、类别、混淆矩阵、子组指标和模型。

仓库报告与独立复算一致：

```text
OOF Macro-F1 = 1.000
OOF Accuracy = 1.000
OOF Balanced Accuracy = 1.000
```

完美分数本身不构成 G3 问题，因为模型输入确实是波形形状特征且组泄漏检查通过；但它仍需在 S4 接受相位、幅值、不变性和代理字段消融压力，不能直接解释为附件二未知真值上的 100% 性能。

### 3.6 Q2 Baseline

**Status: VERIFIED_FROM_REPO**

Q2 已在材料1、正弦波的 1,067 条记录上实现传统 Steinmetz 对数线性 Baseline，并进行：

- 5 折 `condition_group` OOF；
- 训练折内 smearing 修正；
- 分温度指标；
- 四次留一温度压力测试；
- 折参数与完整模型参数保存。

核心结果与独立复算一致：

```text
OOF RMSLE = 0.360678
MAPE = 32.526%
R²（原尺度） = 0.941175
```

完整拟合参数约为：

```text
k = 0.17584
alpha = 1.61011
beta = 2.49712
```

该 Baseline 已提供温度修正模型的公平比较底座，并真实暴露了留一温度弱点。

### 3.7 Q3 Baseline

**Status: VERIFIED_FROM_REPO**

Q3 已形成两层实际输出：

1. 48 个 `温度×波形×材料` 单元的描述统计及共同支持诊断；
2. 控制 `log(f)` 与 `log(B_m)` 的 effect-coded spline Ridge 加性关联模型。

48 个单元均非空，共同矩形支持为 1,766 行，占 14.24%。加性模型保存 12,400 条 OOF 预测、折系数、谱系和模型；结果为：

```text
OOF log-RMSE = 0.343416
R²（原尺度） = 0.603605
最大有限 Gram 条件数 = 183.45
```

当前输出被正确限定为“调整后关联”，没有声称因果。题目要求的两两协同量化属于已冻结的 S4 强制工作；由于 S3 已提供描述和加性参照，当前足以作为后续交互模型的可信 Baseline，不构成 G3 阻断。

### 3.8 Q4 Baseline

**Status: VERIFIED_FROM_REPO**

Q4 已实现：

1. 外层训练折全局中位数参照；
2. 外层训练折 `材料×波形×温度` 中位数参照；
3. 带折内标准化、预声明类别编码、内层 3 折选参和训练折 smearing 的 Ridge 对数回归。

5 个外层折的训练组与验证组交集均为 0，验证样本合计覆盖 12,400 条。结果与独立复算一致：

```text
全局中位数 RMSLE = 1.900178
分组中位数 RMSLE = 1.831109
Ridge RMSLE = 0.200097
Ridge MAPE = 15.847%
Ridge R²（原尺度） = 0.950734
```

Ridge 明显优于两个最低参照，能够作为 S4 主候选的有效比较底座；低 `B_m` 四分位 RMSLE 0.2575 已被记录为重点失败子组。

### 3.9 Q5 Baseline 与 Q4→Q5 闭环

**Status: VERIFIED_FROM_REPO**

Q5 已真实实现，而非文字替代。其输入来自 Q4 Ridge 的逐行严格 OOF 和 full-fit 参考：

- 名义频率域内候选 12,237 条；
- 折叠一条精确重复后 12,236 个实测工况点；
- 每个候选保留来源、波形身份、全部 Q4 特征、折与模型谱系；
- 每个候选主损耗只使用未见其 `condition_group` 的对应外层模型预测；
- 5 个外层折的组交集均为 0，模型 ID、折 ID 和组哈希断言均通过；
- OOF Pareto、full-fit 参考 Pareto、观测损耗诊断 Pareto、折级 Pareto和区域支持均已实际输出。

实际结果为：

```text
严格 OOF Pareto 点 = 105
full-fit 参考 Pareto 点 = 109
观测损耗诊断 Pareto 点 = 130
双 Pareto 点 = 101
Bootstrap 前达到折支持的区域 = 22
```

关键负结果也被正确执行：

```text
模型/观测 Pareto 区域 Jaccard = 0.096154 < 0.50
Bootstrap 尚未完成
单点推荐资格数 = 0
unique_recommendation_authorized = false
```

这不构成 G3 失败。相反，它证明冻结的失败条件确实发挥作用：当前只保留 Pareto、端点和临时膝点，不把不稳定结果包装成唯一最优工况。

### 3.10 独立基本复核

**Status: SUPPORTED_BY_REPO**

`src/verify_s3_outputs.py` 对当前证据执行了以下检查：

- 8 份 manifest 的状态、实现 SHA、实现洁净性和输出文件哈希；
- 实现提交是证据提交的祖先，且核心实现/冻结配置在运行后未变化；
- Q1 分类指标由逐样本 OOF CSV 重算；
- Q2、Q4 回归指标由逐样本 OOF CSV 重算；
- Q3 log-RMSE 重算；
- Q5 严格 OOF Pareto 成员重新计算；
- Q5 候选级 OOF 谱系完整性检查。

提交的 `verification_report.json` 状态为 PASS，记录 8 份 manifest，并给出与报告一致的核心数值。

---

## 4. G3 Checklist

| G3 验收项 | 结果 | Reviewer 判断 |
|---|---|---|
| 数据处理流程可运行 | PASS | 特征、身份、分组、折和确定性重建均有真实产物 |
| Q1–Q5 均有实际输出 | PASS | 每问均有代码、结果和指标；Q5 有实际 Pareto 表 |
| 最后一问不是文字方案 | PASS | 12,236 候选、105 个严格 OOF Pareto 点及诊断已生成 |
| 前后数据流闭环 | PASS | Q4 严格 OOF 真实进入 Q5 |
| 代码与批准合同基本一致 | PASS | 特征、折、指标、候选身份和失败门槛一致 |
| 输入输出路径明确 | PASS | 报告、manifest 与目录结构一致 |
| 配置和随机性可追溯 | PASS | 冻结 JSON、种子、实现 SHA、环境和合同哈希齐全 |
| 训练/验证方式合理 | PASS | 分组外层 OOF，选参位于外层训练部分 |
| 无明显数据泄漏 | PASS | 同组跨折为 0；测试附件只核验哈希 |
| 结果可基本复核 | PASS | 逐样本输出、文件哈希和独立复算报告齐全 |
| Baseline 足以支撑后续比较 | PASS | Q1/Q2/Q3/Q4/Q5 均有明确参照与失败信号 |
| 失败模式已记录 | PASS | Q1 压力测试、Q2 温度、Q3 支持域、Q4 低 Bm、Q5 Jaccard 均已登记 |
| 运行失败有明确机制 | PASS | 异常抛出、manifest FAIL 路径和多项断言存在 |
| 可安全进入 S4 | **YES** | 允许针对失败模式开展有限改进 |

---

## 5. Issue Classification

### Critical

**None.**

未发现：

- 核心小问完全无输出；
- 附件二、三参与拟合或调参；
- 报告中的核心结果文件不存在；
- 代码与批准方案完全不同；
- 人工填写无法追溯的结果；
- Q5 被文字替代；
- 无意义结果被宣称为最终成功。

### Major

**None.**

当前证据足以确认全题 Baseline 实际闭环，且后续即使主候选未产生提升，已有代码和结果仍可作为完整分析底座。

### Minor

#### Minor-01：`logs/experiments.md` 存在历史模板残留冲突

文件前部仍写有“本日志尚不包含模型训练”，末尾也残留：

```text
已训练模型：None
已选择超参数：None
已生成预测：None
```

但同一文件中已经记录 Q1/Q2/Q3/Q4 Baseline 训练和 OOF 预测。权威 manifest、结果目录、Baseline 报告及当前状态是一致的，因此该问题不推翻核心结果；但日志内部存在 `CONFLICT`。

**建议修复时间：进入 S4 后首次状态提交前，最迟在 G4 submission 前。**

修复时应保留历史含义，不删除旧实验记录；可把旧段改为“截至 S2 的历史状态”或删除仅用于空项目初始化的模板项。

#### Minor-02：合成退化测试的覆盖表述略强于实际测试

`test_s3_synthetic.py` 明确测试了：

- Pareto 支配与并列；
- 重复四分位边界；
- 损耗/能量零范围代表点。

源码中确实实现了 OOF/full 空交和 Jaccard 双空集分支，但当前合成测试没有直接构造这两个分支。Baseline 报告中“代码与合成测试覆盖全部退化情形”的表述略强。

**建议修复时间：G4 submission 前。**

应补充两个小型断言，或把文字改成“代码实现，部分关键分支由合成测试覆盖”。

#### Minor-03：运行清单中的 config 参数记录为本机绝对路径

统一复现命令使用项目相对路径，能够指导跨机器运行；但子实验 manifest 的 `command` 字段包含 Windows 本机绝对配置路径。输入哈希和环境信息仍然充分，因此不阻断复现，但跨机器审计可读性可更好。

**建议修复时间：S4 新实验框架开始前。**

建议在 manifest 中同时记录 `command_repo_relative`，或让命令序列化优先使用相对 `PROJECT_ROOT` 的路径。

### Advisory

- 当前最新审核快照在 S3 证据提交之后又加入了绘图 Guide。该变更未影响模型实现与结果，不构成问题；正式比赛中仍建议 Gate 提交后尽量减少同分支无关提交，以降低审核复杂度。

---

## 6. Mandatory S4 Priorities

本次 PASS 不允许无边界更换算法。S4 必须从 S3 的真实失败信号出发，优先级建议为：

1. **Q2 温度修正**：实现冻结的二次乘性温度修正，与传统 Steinmetz 在完全相同 OOF 折上比较；重点处理 25°C、90°C 留一温度误差。
2. **Q4 主模型与消融**：在相同折和指标下比较 HGB 与 Ridge，只有达到 ≥2% RMSLE 改善且主要子组不恶化超过 10% 才替换；重点检查低 `B_m` 子组。
3. **Q5 稳定性闭环**：消费最终 Q4 胜者的严格 OOF，执行 500 次 `condition_group` 重采样、频率域和峰值口径敏感性；若 Jaccard、双 Pareto或稳定门槛仍失败，继续禁止唯一推荐。
4. **Q3 两两协同**：在加性 Baseline 上实现三组预定义两两交互、共同支持和簇 Bootstrap；必须保持“调整后关联”措辞。
5. **Q1 压力测试**：完美 OOF 分数必须接受相位/幅值不变性、留一材料和特征/辅助字段消融；若 Logistic 已稳定饱和，不得为了形式复杂化强行采用树模型。

Q2 温度修正和 Q3 两两交互是题面核心要求。它们在 S3 已有真实 Baseline，但必须在 G4 前产生实际主结果；不能因 G3 PASS 而跳过。

附件二、附件三仍只能在对应最终模型和预处理完全冻结后按既定单次释放流程使用，不得用于 S4 模型选择。

---

## 7. Authorization for Next Stage

Reviewer 正式授权：

```text
G3 = PASS
S3 -> S4 = AUTHORIZED
Next Gate = G4
```

S4 的正确工作流应为：

```text
S3 失败信号
-> 有限、针对性的模型改进
-> 同折公平比较
-> 消融 / 敏感性 / 鲁棒性 / 不确定性
-> 负结果与回退
-> G4 审核
```

禁止因为进入 S4 而：

- 改动冻结外层折或主指标以追求更好分数；
- 使用附件二、附件三反向选择模型；
- 无限制增加模型族或超参数；
- 隐藏 Q5 Jaccard 失败；
- 将 `results/raw/` 直接升级为 `results/verified/`；
- 在稳定性门槛未满足时输出唯一最优工况。

---

## 8. Reviewer Statement

本审核仅针对固定快照：

```text
17cefbfe7bda13fa97f2eb19decc1abd02529597
```

Reviewer 未声称在网页端重新执行 Conda 代码。结论来自固定仓库快照中的源码、运行清单、日志、逐样本/逐候选结果、文件哈希、模型合同和独立复算报告。

**最终结论：PASS。允许进入 S4 / G4。**
