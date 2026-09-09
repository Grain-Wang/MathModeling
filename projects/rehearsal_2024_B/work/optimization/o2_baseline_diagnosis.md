# Optimization Report — O2 Baseline Failure Diagnosis

## 1. Metadata

- Project: rehearsal_2024_B
- Stage: S3
- Current Gate: G3 (pending)
- Formal implementation/run commit: `2222cf5f4e17a6dac832c4e65f9c5a60cd01060d`
- Formal model version: `S3-baseline-v1 / topology_aware_rssi_v1`
- Evidence: [06_baseline_report.md](../06_baseline_report.md) and `results/raw/baseline/`
- Remaining time: 往年题模拟无外部倒计时；仍严格采用每个 S4 question family 最多 120 min 的合同时间盒

## 2. Current State

已完成：

- 13 个训练输入的真实入口门禁与 4 个官方测试注入负向测试；
- 312 特征的训练侧 schema；
- 八个冻结 Baseline；
- 15 个 primary outer folds、13 个 source-blind LOSO；
- 112 个实际 Q1 upstream lineage batches，两个 overlap total 均为 0；
- 1,000 次 group bootstrap；
- Q2 固定 17 类、缺类/support、A03；
- Q3 bounded AP/system、signed/absolute-relative CDF、零分母和严格求和；
- 独立 post-run validation PASS。

当前可回退底座：

- Q1: Q1-B1 Ridge，primary MAE=5.5054 s；
- Q2: Q2-B1A Logistic without Q1，primary macro-F1=0.3377；
- Q3: Q3-B1 Ridge，primary S=0.8046；Q3-B2 作为物理外推参照。

本 O2 先排除了数据读取、分组、泄漏、指标、合同偏离、随机性和数值稳定性错误：

1. 17/17 文件身份匹配，eligible=1,250/482；
2. 实际 prediction-fit 与 held-out-fit overlap 为 0；
3. 独立验证器从逐行证据重算主要指标与 system sum；
4. run warning_count=0，所有正式预测有限；
5. 固定 17 类概率宽度、顺序与归一化均通过；
6. 官方测试 numeric read/prediction=0/0。

剩余问题因此可归类为输入信息、类别稀疏和模型能力/外推结构，而不是基础实现错误。

## 3. Evidence-Based Bottlenecks

| ID | Bottleneck | Evidence | Status | Impact |
|---|---|---|---|---|
| B-O2-01 | Q2 少数联合类坍缩 | B1A 三次 repeat 都不预测 support=1 的 1|6、1|7、2|2；部分 repeat 还遗漏 1|4/1|9；固定 17 类 macro-F1 仅 0.3377 | VERIFIED | Q2 对稀有速率状态回答不足，macro-F1 的主要短板 |
| B-O2-02 | Q2 source-blind 外推退化 | B1A primary macro-F1=0.3377，LOSO=0.1609；最差 loc2/nav82 来源 F1=0.0303、accuracy=0.2179 | VERIFIED | 结论不能仅依赖场景内 accuracy=0.7552 |
| B-O2-03 | Q1 cross-fit 对 Q2 没有增益 | B1B 比 B1A primary F1 低 0.0033，LOSO 低 0.0030，bootstrap 区间高度重叠 | VERIFIED | S4 不应把增加 Q1 依赖作为 Q2 主线 |
| B-O2-04 | Q3 3 AP 与 source 外推弱 | B1 的 2/3 AP ARE90=0.5241/0.9493，三次 repeat 同向；LOSO S=1.3233，最差来源 S=4.9790 | VERIFIED | Q3 primary 可用但无法支撑强鲁棒性结论 |
| B-O2-05 | 物理锚点在 primary/LOSO 间有取舍 | B2 primary S=0.8556，略差于 B1=0.8046；但 LOSO S=0.9347，优于 B1=1.3233 | VERIFIED | 值得验证物理基线周围的有限非线性残差，而非抛弃物理结构 |
| B-O2-06 | Q1 3 AP 误差高但整体底座稳定 | Q1-B1 相对 B0 MAE 降约 50.5%，0 裁剪；2/3 AP MAE=3.2273/6.5463，LOSO=7.0266 | VERIFIED | 是限制项，但在两方向预算下优先级低于 Q2/Q3 |

A03 三个完整组整体排除后的 Q2/Q3 排名基本不变，故 A03 不是当前主要瓶颈。Basic/group-context 的 Q1 消融增益接近 0 且证据不一致，不支持围绕这些字段扩张模型。

## 4. Candidate Improvements

| Candidate | Target | Expected value | Minimum verification | Time box | Main risk | Rollback |
|---|---|---|---|---:|---|---|
| C-O2-01: Q2 finite HGB classifier | B-O2-01/02 | 学习 RSSI/门限的非线性分界；若仍坍缩，只对选定配置执行一次 sqrt inverse-frequency 权重，单样本权重上限 5 | 冻结 4 点 HGB 网格的 nested primary/LOSO；固定 17 类；with/without Q1 以无 Q1 为主；披露缺类和 confusion | 120 min | 稀有类 support 太小，权重可能损害 accuracy 或不稳定 | Q2-B1A |
| C-O2-02: Q3 direct vs physics-residual HGB | B-O2-04/05 | 在保留 B2 外推结构的同时学习合法特征残差；direct 作为必要结构对照 | 最多 4 direct + 4 residual 固定配置；nested primary/LOSO；AP/system bounded sum、bias guard；一次 2/3 AP 分模对照 | 120 min | 非线性过拟合 source，或 residual 仅改善局部场景 | Q3-B1，B2 保留作物理对照 |
| C-O2-03: Q1 HGB | B-O2-06 | 可能降低 3 AP MAE | 合同 4 点网格、primary/LOSO、5% 晋升阈值 | 120 min | 不会改善已冻结的下游 Q1-B1；挤占 Q2/Q3 证据时间 | Q1-B1 |
| C-O2-04: 全题按 AP count 分模 | B-O2-04/06 | 针对 3 AP 难度差异 | 每层相同切分与一次 unified-vs-split 对照 | 额外 60–120 min | 每层样本减少，稀有类更严重 | 统一模型 |
| C-O2-05: 更大网格/深度学习/独立 system head | 无直接证据 | 表面复杂度 | 无法在当前样本和时间盒内公平证明 | >240 min | 过拟合、不可解释、破坏 AP→system 恒等式 | 不执行 |

## 5. Selected Action

选择两个主要方向：

1. **Q2 finite HGB classifier（C-O2-01）**
   - 主输入先不含 Q1，因为 B1A 在 primary 和 LOSO 均略优于 B1B。
   - 只使用合同中的 4 个 HGB 配置，不扩大网格。
   - Baseline 已在三个 repeat 证明 minority collapse，因此授权：若无权重 HGB 仍发生主类坍缩，只对 nested 选出的配置做一次预注册平方根逆频率权重验证，权重裁剪上限 5；不得继续改权重公式。
   - with-Q1 只作一次依赖消融，不得把 Q1-HGB 替换为下游上游。

2. **Q3 direct vs physics-residual HGB（C-O2-02）**
   - 比较合同限定的最多 8 个配置，优先检验 residual 是否兼得 B1 primary 精度和 B2 LOSO 稳定性。
   - 因 3 AP ARE90 在三个 repeat 均比 2 AP 高超过 10%，授权在最佳统一结构上做一次 2 AP/3 AP 分模对照；它是本方向内的条件对照，不扩展新算法族。
   - system 始终由 bounded AP 求和，不允许独立 system 头。

不选择 Q1 HGB：Q1-B1 已获得大幅且稳定的 Baseline 改善，而 Q1 主候选不能替换下游固定上游；两方向预算优先用于 Q2/Q3 的真实失败。

不选择全题普遍分模：仅 Q3 满足并需要这一条件实验；Q2 分模会进一步稀释 rare-class support，Q1 的收益优先级不足。

## 6. Time Box

- Q2 最大 120 min。
  - Checkpoint 1: 四个固定无权重 HGB 的 nested primary 选择。
  - Checkpoint 2: selected HGB 完整 outer/LOSO 与 minority collapse。
  - Checkpoint 3: 仅在 collapse 仍存在时运行一次固定权重版本。
- Q3 最大 120 min。
  - Checkpoint 1: 四个 direct 与四个 residual 的 nested primary 选择。
  - Checkpoint 2: selected architecture 完整 outer/LOSO、bias 和 sum equality。
  - Checkpoint 3: 只做一次 unified-vs-AP-count split 对照。
- 总主时间盒 240 min；任一 family 达到计划时间 2 倍前必须停止并回退。

## 7. Success Criteria

### Q2

1. 相对 Q2-B1A 的 primary fixed-17 macro-F1 至少提高 0.02；
2. 三个 repeat 至少两个改善；
3. joint accuracy 不比 0.7552 低超过 0.01；
4. 概率顺序、缺类补零和固定 17 类全部通过；
5. LOSO、每类 support、collapse、A03 和 with/without Q1 完整披露。

### Q3

1. 相对最佳 primary Baseline Q3-B1 的 S=0.8046 至少改善 5%；
2. 三个 repeat 至少两个改善；
3. AP 或 system 的绝对 median signed bias 均不得比最佳 Baseline恶化超过 0.02；
4. bounded AP 非负，system=sum(AP) 的绝对误差≤1e-9；
5. LOSO 不选择性省略；若 primary 晋升但 LOSO 恶化，禁止写成普遍鲁棒提升；
6. AP-count split 只有达到统一模型的同一晋升阈值才保留，否则回退统一结构。

## 8. Stop Conditions

1. Q2 四个固定 HGB 和唯一条件权重都达不到晋升阈值：停止，保留 Q2-B1A。
2. Q2 增益只来自单个 repeat、少数 source 或 accuracy 违规：停止，不晋升。
3. Q3 direct/residual 都达不到 5% 或违反 bias/sum：停止，保留 Q3-B1。
4. Q3 分模未稳定改善或 LOSO 显著恶化：删除分模候选，保留统一结构。
5. 任一 actual lineage overlap、指标重算、测试门禁或有限值断言失败：立即停止 S4，先修实现。
6. 禁止因看见结果扩大网格、改变指标、改变 raw/bounded 口径或读取官方测试。

## 9. Rollback Plan

- Immutable formal run snapshot: `2222cf5f4e17a6dac832c4e65f9c5a60cd01060d`。
- Q1 rollback: Q1-B1。
- Q2 rollback: Q2-B1A；Q1-B1 仍是唯一合法的可选下游上游。
- Q3 rollback: Q3-B1；Q3-B2 保留为物理/LOSO 对照。
- S4 结果只写 `results/raw/main/`，不得覆盖 `results/raw/baseline/`。
- 若需改变 G2 已批准的核心合同、标签、split 或测试治理，停止并回到相应 Gate，不在 S4 偷改。

## 10. Advisor Input

- 本轮未调用 Strong-model Advisor。
- 原因：现有 Baseline、strata、LOSO、bootstrap 和 failure evidence 已足以限定两个方向；不增加新的模型路线。

## 11. Decision

- **O2: PROCEED_TO_G3**

理由：八个 Baseline 已形成全题可运行闭环，基础数据/切分/指标/泄漏/数值问题均已排除，失败模式由实际 primary 与 LOSO 证据支持，S4 仅保留 Q2 与 Q3 两个受限方向，并具有明确时间盒、成功阈值、停止条件和回退版本。

本决定只允许提交 G3；在 Reviewer 给出 G3 PASS 前不得启动 S4。
