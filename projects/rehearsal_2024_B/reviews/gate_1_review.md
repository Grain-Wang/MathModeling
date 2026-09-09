# Gate 1 Review — 题意拆解与数据审计

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_B`
- Gate: `G1`
- Stage: `S1 — 题意拆解与数据审计`
- Review Round: `1`
- Reviewed Commit: `512e461033c8378f1e591912b4992d8486bde396`
- G0 Review Commit: `0fac4e099cffdafab32af0aa9af9f8969f087dbe`
- Formal Audit Implementation Commit: `f4b8b9f70e049d497edf56a3bdac43669da932a6`
- Verdict: **REVISE**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

## 1. Final Verdict

# **REVISE — 暂不同意进入 S2 / G2**

本轮固定快照已经完成了较高质量的题意拆解和数据审计基础工作：三问的输入时点、事后字段禁用范围、测试集封存、`source_file + test_id` 分组边界、A01–A06 异常处理、RSSI 编码与缺失机制、训练集规模和运行证据均已有明确记录。

但是，当前仍有两项会直接影响 S2 模型合同正确性的 **Major** 问题：

1. **Q3 的题面输出与评价要求没有被完整迁入 S1 需求基线。** S0 项目简报已经记录“每 AP 吞吐量、系统吞吐量、误差 CDF 与 90% 分位精度”，但 S1 的问题分析和需求矩阵只冻结了 185 个逐 AP 吞吐量及 MAE/RMSE/R² 等通用回归指标，缺少系统级吞吐量、题面误差定义、CDF 和 90% 分位模型精度；
2. **“482 个完整 AP 组”和“无训练重复行”的机器证据不够严格。** 审计代码主要依据每个 `test_id` 的行数判断组完整性，未断言每组 AP 身份集合正确、复合行键唯一；同时“训练重复行为 0”实际只统计逐文件内部完全重复，没有完成或明确限定跨文件重复检查。

这两项都可以在 S1 内局部修复，不需要推翻 A01–A06、测试封存或三问主线。因此不判 BLOCK，但在修复前不得进入 S2。

```text
G1 = REVISE
Current Stage remains: S1
S1 -> S2: NOT AUTHORIZED
Next review after fixes: G1 / Review Round 2
```

---

## 2. Review Scope and Limitation

本轮重点读取并交叉核对：

```text
.agents/roles/reviewer_agent.md
.agents/roles/main_agent.md
projects/rehearsal_2024_B/CURRENT.md
projects/rehearsal_2024_B/problem/manifest.md
projects/rehearsal_2024_B/work/00_project_brief.md
projects/rehearsal_2024_B/work/01_problem_analysis.md
projects/rehearsal_2024_B/work/02_data_audit.md
projects/rehearsal_2024_B/work/03_requirement_matrix.md
projects/rehearsal_2024_B/src/s1_data_audit.py
projects/rehearsal_2024_B/results/raw/s1/audit_summary.md
projects/rehearsal_2024_B/results/raw/s1/data_profile.json
projects/rehearsal_2024_B/results/raw/s1/quality_checks.json
projects/rehearsal_2024_B/logs/decisions.md
projects/rehearsal_2024_B/logs/experiments.md
projects/rehearsal_2024_B/reviews/gate_1_submission.md
```

写回前已确认：

```text
main HEAD = 512e461033c8378f1e591912b4992d8486bde396
```

未发生分支漂移。

17 个原始 CSV 按项目策略未进入 Git，因此本 Reviewer 无法在网页端独立重跑原始数据审计。本轮对具体统计量采用 `SUPPORTED_BY_REPO`：依据固定哈希、审计代码、机器可读 JSON、日志和提交谱系判断；对仓库中可直接比较的文档、代码和结果一致性采用 `VERIFIED_FROM_REPO`。无法重跑本身不自动导致失败，本轮 REVISE 来自可直接验证的需求遗漏与审计断言缺口。

---

## 3. Positive Findings

### 3.1 Gate 状态和固定快照一致

**Evidence status: VERIFIED_FROM_REPO**

用户指定 G1，`CURRENT.md` 处于 S1 并等待 G1，`gate_1_submission.md` 也声明 G1 Round 1；G0 已 PASS。没有跳 Gate、错项目或自审通过。

### 3.2 三问的输入时点和数据流总体正确

**Evidence status: VERIFIED_FROM_REPO**

当前已明确：

```text
基本信息 / RSSI / 拓扑
  -> Q1 seq_time
  -> Q2 (MCS,NSS)
  -> Q3 throughput
```

并规定 Q1 预测若进入 Q2/Q3，训练阶段必须使用折外预测，不能使用训练内拟合值。Q3 可使用题面明确许可的真实 MCS/NSS，但该许可没有被扩张到 PER、真实 seq_time、num_ampdu、ppdu_dur 或 other_air_time。

这是本题最重要的标签泄漏边界之一，当前方向正确。

### 3.3 测试集封存纪律较强

**Evidence status: SUPPORTED_BY_REPO**

审计脚本对测试集只输出 schema、dtype、缺失/非空计数和组大小，不输出 RSSI 或其他数值分布；测试集没有被用于异常阈值、特征选择、调参或模型选择。测试集 1 中非空的 MCS/NSS/PER 与空白的 seq_time/throughput，以及测试集 2 中空白的 MCS/NSS 均被明确区分。

### 3.4 A01–A06 均有可执行处理边界

**Evidence status: SUPPORTED_BY_REPO**

- A01：隔离两个不完整组，共 2 行，原件不改；
- A02：三个全空 RSSI 列保留缺失，不伪造反向链路；
- A03：三条 `(NSS,MCS)=(0,0)` 暂保留，S2 做保留/排除敏感性；
- A04：schema alias 和输出占位列只在派生层规范化；
- A05：两个超大 `other_air_time` 只作字段级无效，不无依据删除目标行；
- A06：内容 `loc4` 与文件名 token 冲突被保留为 UNKNOWN。

这些处理没有静默改写原始 CSV，并且已进入决策日志和机器证据。

### 3.5 字段、单位、规模与 RSSI 解析风险覆盖较完整

**Evidence status: SUPPORTED_BY_REPO**

当前已记录 17 个文件的 schema、训练 1,252 行、A01 后 1,250 行、测试 336 行、RSSI 列表/标量/缺失/非法文本类型、列表长度变化、常量字段、Q2 类别不平衡、Q3 零吞吐量以及 `num_ppdu`/`num_ampdu` 等口径差异。

### 3.6 当前没有提前进行模型选择

**Evidence status: VERIFIED_FROM_REPO**

S1 只提交问题分析、数据审计、需求矩阵、审计代码和结果；没有提交正式模型结果、测试预测或 S2 模型合同。阶段边界得到遵守。

---

## 4. Issue Classification

## 4.1 Critical

**None.**

当前没有发现整题方向错误、决定性数据缺失、已发生测试泄漏、原件被改写或整个问题需要退回 S0 重建的证据。

---

## 4.2 Major

### M1-01：Q3 的系统级吞吐量、CDF 与 90% 分位精度要求在 S1 中丢失

**Priority: P0 — 立即修复**  
**Evidence status: CONFLICT**

`work/00_project_brief.md` 对 Q3 的冻结范围写明：

```text
每 AP 吞吐量、系统吞吐量、误差 CDF 与 90% 分位精度
```

同时该文件的风险 R12 也指出，需要明确题面误差定义、90% CDF 精度和系统聚合口径。

但当前：

- `work/01_problem_analysis.md` §5 只把 Q3 输出定义为测试集 1 的 185 个逐 AP throughput；
- 其评价只列 MAE、RMSE、R² 和带 epsilon 的相对误差候选；
- `work/03_requirement_matrix.md` 的 R04 同样只映射 185 个逐 AP throughput 和通用回归指标；
- 没有独立要求系统/网络总吞吐量输出；
- 没有冻结题面 `error`、CDF、`ERROR_90` 或模型精度的定义；
- 没有分别定义 AP 级与系统级精度评价。

这不是可以完全留到 S2 再考虑的模型细节，而是 S1 必须明确的“题目究竟要求输出和评价什么”。若直接进入 S2，后续模型合同可能只优化逐 AP 回归，遗漏题目要求的系统级结果和正式精度口径。

#### Required Fix M1-01

1. 从题目正文中提取并记录 Q3 的完整原始要求，明确区分：
   - 每 AP 吞吐量；
   - 每个完整测试组的系统/网络吞吐量；
   - AP 级预测误差 CDF；
   - 系统级预测误差 CDF；
   - 90% 分位误差和相应模型精度定义。
2. 明确系统吞吐量如何由组内 AP 构成。如果题面未直接给公式，必须把采用的聚合规则标记为假设并给出单位和可验证性，不能静默默认。
3. 明确训练和测试的输出粒度与数量：逐 AP 输出和按 `source_file + test_id` 聚合的系统输出必须分别登记。
4. 冻结题面误差公式、绝对值方向、CDF 构造、分位数插值规则以及真实吞吐量为 0 时的处理；MAE/RMSE/R²可以作为辅助指标，但不能替代题面要求的精度指标。
5. 将上述内容同步进入：

```text
work/01_problem_analysis.md
work/02_data_audit.md
work/03_requirement_matrix.md
logs/decisions.md
```

必要时让审计代码生成训练系统级目标的可构造性、完整组数量和零系统吞吐量数量，但不得开始拟合模型。

#### Acceptance Criteria M1-01

复审时必须满足：

- Q3 不再只等价于“185 个逐 AP 回归值”；
- AP 级与系统级输出、单位、样本键和样本数均明确；
- 题面 CDF/90% 分位精度有唯一、可执行的公式合同；
- 零分母与分位数并列/插值处理不留到看到结果后决定；
- 需求矩阵中存在独立条目覆盖系统吞吐量和两级精度评价；
- 后续 S2 可以据此编写不会漏答 Q3 的模型合同。

---

### M1-02：AP 组完整性、复合行键和重复检查证据不足

**Priority: P1 — 本 Gate 通过前修复**  
**Evidence status: NOT_VERIFIED / SCOPE CONFLICT**

当前审计把 `source_file + test_id` 作为切分原子，这是正确方向；但机器检查主要通过“组内行数等于 2 或 3”判定完整性：

```python
frame.groupby("test_id").size()
```

以及在 A01 隔离后再次检查每组行数。代码没有看到以下强制断言：

- `(source_file, test_id, ap_id)` 复合行键唯一；
- `test_id`、`ap_id` 非空且格式合法；
- 每个 2 AP 组恰好包含 `ap_0, ap_1` 各一次；
- 每个 3 AP 组恰好包含 `ap_0, ap_1, ap_2` 各一次；
- 不存在“重复某个 AP、缺少另一个 AP，但总行数仍正确”的伪完整组。

这会影响后续组内拓扑特征、逐 AP 标签对齐、系统吞吐量聚合和最终预测导出。仅检查行数不足以证明“482 个完整 AP 组”。

此外，`training_exact_duplicate_rows` 的实现为逐个训练文件分别执行 `frame.duplicated()` 后求和；它证明的是“各文件内部没有完全重复行”，并不能直接支持不加限定的“整个训练集无重复行”。跨文件是否存在完全相同或近似相同的观测尚未被报告，而后续验证分组可能因此过于乐观。

#### Required Fix M1-02

1. 在审计脚本中增加复合身份断言：

```text
(source_file, test_id, ap_id)
```

必须唯一且非空。
2. 对原始训练、A01 后 eligible 训练以及四个测试集逐组验证精确 AP ID 集合，不得只比较行数。
3. 输出机器可读的：
   - 复合键重复数和示例；
   - 缺失/非法 AP ID 数和示例；
   - AP ID 集合不匹配组数和示例；
   - 通过严格身份检查后的训练/测试组数。
4. 将重复审计的范围说清楚：
   - 文件内完全重复；
   - 跨文件规范化后的完全重复或等价记录。

   至少应对可对齐的训练字段生成稳定内容指纹并报告跨文件重复；若认为相同内容在不同 source 场景不应合并，也必须保留重复组标识供 S2 防泄漏或敏感性判断。
5. 重新运行 S1 审计，确认原始 17 个 CSV 的前后 SHA-256 不变，并更新 JSON、审计报告和实验日志。

#### Acceptance Criteria M1-02

复审时必须满足：

- 每个 eligible 训练组和测试组都通过“行数 + AP 身份集合 + 复合键唯一”三重检查；
- A01 两个异常组被清晰排除，其他组不存在 AP 身份缺失或重复；
- “重复行为 0”等结论明确说明作用域，且存在跨文件重复检查或可执行的重复分组策略；
- 新的机器证据可让 Reviewer 在没有 CSV 的情况下判断断言逻辑和计数；
- 任何新发现的重复或身份异常均进入决策日志，不能静默处理。

---

## 4.3 Minor / S2 Early Requirements

以下问题不单独阻断 G1，但应在完成上述 Major 后，于 S2 初期冻结。

### Minor-01：Q2 稀有联合类别的验证合同

训练中 `(NSS,MCS)=(2,2)` 只有 1 条，`(0,0)` 只有 3 条。分组交叉验证时，某些折的训练部分可能不含特定联合类别；若直接计算默认 macro-F1，指标含义和模型输出类别集合可能随折变化。

S2 应预先固定：

- 联合标签全集和排序；
- 缺失训练类别时的失败/回退规则；
- macro-F1 是否对全局固定标签集计算；
- 每类 support 和可学习性披露；
- A03 保留/排除敏感性。

### Minor-02：场景外推不能只作为可选美化实验

`source_file + test_id` 分组能防止同一测试的 AP 行跨折，但普通 grouped K-fold 仍会让相同 source 场景同时出现在训练和验证。S2 应把 leave-one-source-file-out 设为强制压力测试之一，并明确其与主插值指标的不同用途；不能只在主结果不好看时才决定是否报告。

### Minor-03：团队实名与环境 clean rebuild

团队实名责任分配和全新环境重建仍缺失。两者不影响当前 S1 科学正确性，但应分别在最终协作前和正式比赛前完成。

---

## 5. G1 Checklist

| G1 验收项 | 当前结果 | Reviewer 判断 |
|---|---|---|
| 三问均被识别 | PASS WITH Q3 OMISSION | Q1、Q2完整；Q3缺系统级输出与正式精度要求 |
| 每问输入、输出、约束和目标明确 | REVISE | Q3输出粒度和评价合同不完整 |
| 小问依赖关系正确 | PASS | Q1 OOF 与 Q3真实MCS/NSS边界正确 |
| 字段、单位、范围、规模明确 | PASS | 主要字段和RSSI结构已覆盖 |
| 缺失和异常检查 | PASS WITH LIMITS | A01–A06充分，但身份完整性断言不足 |
| 重复检查 | REVISE | 只充分证明逐文件内部重复；跨文件范围不清 |
| 标签/个体/场景泄漏识别 | PASS | 组边界和事后字段白名单较强 |
| 测试集封存 | PASS | 没有数值分布驱动的选择证据 |
| 数据足以支持各问 | PASS WITH Q3 CHECK | 逐AP任务可支持；系统级目标构造尚未正式审计 |
| 需求追踪完整 | REVISE | Q3系统吞吐量与CDF/90%分位未映射 |
| 可安全开始 S2 | **NO** | 两项 Major 修复后复审 |

---

## 6. Required Fix Summary

本轮只要求聚焦两项，不要求扩张模型或提前进入 S2：

```text
RF-1  恢复并冻结 Q3 的系统吞吐量、AP/系统两级误差 CDF 与 90% 分位精度要求。
RF-2  补齐复合行键、精确 AP ID 集合及跨文件重复范围的机器审计。
```

建议至少更新：

```text
projects/rehearsal_2024_B/work/01_problem_analysis.md
projects/rehearsal_2024_B/work/02_data_audit.md
projects/rehearsal_2024_B/work/03_requirement_matrix.md
projects/rehearsal_2024_B/src/s1_data_audit.py
projects/rehearsal_2024_B/results/raw/s1/
projects/rehearsal_2024_B/logs/decisions.md
projects/rehearsal_2024_B/logs/experiments.md
projects/rehearsal_2024_B/CURRENT.md
projects/rehearsal_2024_B/work/revisions/gate_1_response.md
projects/rehearsal_2024_B/reviews/gate_1_submission_r2.md
```

修复期间不得拟合正式模型、使用测试分布选择规则或改变原始 CSV。

---

## 7. Re-review Requirements

下一轮请提供新的远程固定完整 SHA，并使用：

```text
Gate: G1
Review Round: 2
Response: work/revisions/gate_1_response.md
Submission: reviews/gate_1_submission_r2.md
Expected Review: reviews/gate_1_review_r2.md
```

`gate_1_response.md` 应逐条映射 M1-01、M1-02 的 Required Fix 和 Acceptance Criteria，并列出新机器证据文件及关键计数。

---

## 8. Authorization

```text
G1 = REVISE
Remain at S1
S1 -> S2 = NOT AUTHORIZED
```

当前路线可以保留；A01–A06、测试封存、逐问白名单和分组验证方向不需要推翻。完成两项局部修订并通过 Round 2 后，项目即可继续申请进入 S2。
