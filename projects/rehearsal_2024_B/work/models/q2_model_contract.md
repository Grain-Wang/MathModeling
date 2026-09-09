# Q2 Model Contract — Most-used Joint (NSS,MCS)

## Problem

根据测试基本信息、节点间 RSSI、门限以及 Q1 发送机会信息，为 test_set_2_2ap 和 test_set_2_3ap 的每个 AP 行预测测试中采用次数最多的联合 (NSS,MCS)。

输出是一个联合类别，不允许两个独立分类器随意组合出训练中未观察的状态。

## Inputs

### Allowed

- Q1 合同中的基本信息、拓扑感知 RSSI 与门限裕量特征；
- AP 数和 protocol；
- 固定 Q1-B1 Ridge(alpha=1.0) 产生的 seq_time_bounded：训练行为严格 OOF，验证/最终推理行为 inference；postprocess=q1_clip_0_test_dur_v1；
- Q1 发送机会特征族贡献，仅用于解释，不把验证标签统计编码为特征。

### Key or stratum only

source_file、test_id、loc_id、bss_id、名称、MAC、ap_id、sta_id。身份字段只用于分组、对齐、分层和审计。

### Forbidden

- 真实 nss、mcs 及其派生 PHY Rate；
- per、num_ampdu、ppdu_dur、other_air_time、真实 seq_time、throughput；
- Q1 训练内拟合预测；
- 官方测试数值分布和所有输出占位列。

## Outputs

每个 AP 行输出：

- source_file + test_id + ap_id；
- predict_nss、predict_mcs；
- joint_label；
- 对固定 17 类对齐的概率向量；
- 模型/配置/repeat/fold 标识；
- 该折缺失训练类别列表。

官方输出数量为 151；joint_label 必须属于冻结标签集。

## Variables and Units

| Symbol | Meaning | Unit |
|---|---|---|
| z_ig | 统一合法输入特征 | mixed |
| shat_ig_OOF | Q1 交叉拟合发送时长预测 | s |
| c_ig | 真实联合类别 (NSS,MCS) | categorical |
| C | 固定 17 类全集 | set |
| p_k | 属于第 k 类的概率 | dimensionless |
| nss | 空间流数 | count/class |
| mcs | 调制编码阶数 | index |
| nav | NAV 门限 | dBm |

## Assumptions

1. 采用最多次数的 (NSS,MCS) 能作为题面要求的单一联合标签。
2. 标签空间只由批准的 eligible 训练数据冻结，不从测试集推断。
3. 稀有类在某些训练折缺失是可预期限制，不得动态缩小评价标签集来美化结果。
4. Q1 发送机会预测可能提供额外信息，但只有 cross-fitted 值合法。
5. 0|0 可能是失败状态或哨兵，业务语义未知，故主分析保留并做 A03 敏感性。
6. 新 source 场景可能有标签分布偏移，LOSO 结果必须独立报告。

## Mathematical Definition

固定标签集：

$$
\mathcal C=\{
0|0,
1|0,1|4,1|5,1|6,1|7,1|9,
2|2,2|3,2|4,2|5,2|6,2|7,2|8,2|9,2|10,2|11
\}。
$$

多项 Logistic Baseline：

$$
P(c=k\mid z)
=\frac{\exp(\beta_k^\top z)}
{\sum_{\ell\in\mathcal C}\exp(\beta_\ell^\top z)}。
$$

主候选 HGB 输出当前训练折可学习类别的概率。导出前重索引：

$$
\widetilde P(c=k)=
\begin{cases}
P(c=k),&k\text{ 出现在训练折};\\
0,&k\text{ 未出现在训练折}.
\end{cases}
$$

预测为：

$$
\widehat c=\arg\max_{k\in\mathcal C}\widetilde P(c=k)。
$$

因此不会产生未观察的 NSS/MCS 组合。

## Objective

训练目标：

- Q2-B0：训练折多数类；
- Q2-B1：无权重 multinomial log loss + L2；
- HGB：multiclass log loss。

模型选择词典序：

1. 最大化固定 17 类、zero_division=0 的 grouped OOF macro-F1；
2. 差异小于 0.002 时，最大化 joint exact-match accuracy；
3. 再相同时，最小化按 1e-15 裁剪概率后的 multiclass log loss；
4. 最后选更简单模型。

不以单独 NSS accuracy 或 MCS accuracy 代替联合任务。

## Constraints

- 原子组 source_file + test_id 不跨任何外层/内层折；
- 全部预处理只在训练折拟合；
- 概率列顺序永久等于机器配置中的 17 类顺序；
- 缺失训练类概率为 0，并披露；
- 未见联合标签使流程硬失败，不能临时加类；
- 预测必须落在固定集合；
- Q1 输入必须具有 Q1-B1、seq_time_bounded、q1_clip_0_test_dur_v1 和 fit-group hash 血缘；
- A03 敏感性按包含异常行的完整组排除，避免拆组；
- S2/S3/O2/S4/O3/G4_REVIEW 的输入 manifest 不得含官方测试文件；
- 官方测试只允许在 G4 PASS 后的 S5 freeze manifest 完整时一次最终推理，且不参与标签、阈值、类别权重、模型或后处理选择。

## Parameters

来自 configs/s2_experiment_plan.json：

- outer：3 repeats × 5-fold GroupKFold，seeds 202409–202411；
- inner：3-fold GroupKFold，固定派生 seed；
- Q2-B1：C=1.0、max_iter=2000、class_weight=None；
- HGB：max_iter=200、min_samples_leaf=20、learning_rate=0.05；
- max_leaf_nodes ∈ {7,15}；
- l2_regularization ∈ {0,1}；
- early_stopping=false；
- 主 HGB 最多 4 个配置；
- 条件权重只允许一个：sqrt(N/(K n_k))，再裁剪到最大 5，且须由 O2 少数类坍缩证据触发。

## Training / Solving Procedure

1. 验证输入哈希、A01、严格身份、合同 SHA、phase 白名单和固定 17 类。
2. 读取冻结 outer/downstream-inner/nested-upstream/LOSO registry。
3. S3 在每个 outer fold 运行固定 Q2-B0、Q2-B1，不做下游调参。
4. S3 的 outer-training 使用 inner 3-fold Q1-B1 bounded OOF；outer-validation 使用完整 outer-training 拟合的 Q1-B1 bounded 预测。
5. 比较有/无固定 Q1 特征两条 Baseline 链，禁止训练内 Q1 值。
6. O2 若授权 HGB，对每个 downstream inner fold，只在 inner-training 的 nested-upstream 3-fold 生成 Q1-B1 bounded OOF，并由完整 inner-training 预测 inner-validation，再从 4 个配置选择。
7. 对每个 prediction lineage 断言目标组不在 fit groups，且 downstream inner-validation 不进入生成 inner-training 特征的任何上游拟合。
8. 把 estimator.classes_ 对齐到 17 列，缺类补 0。
9. 保存逐行 OOF 概率、预测、真实标签、support、缺类、切分 ID 和 upstream lineage ID。
10. 每个 repeat 独立计算指标后取算术平均；LOSO 每折只在剩余 source 内执行相同的固定 Baseline或嵌套选择。
11. S3/S4 导出 dry-run 仅用合成 fixture 或训练侧验证输出。
12. 只有 G4 PASS 后进入 S5，且 freeze manifest 固定模型、schema、Q1 后处理、17 类顺序和输出格式，才可用完整 eligible 训练重拟合并对 test_set_2 一次最终推理。
13. 导出前检查 151 行、唯一键、固定标签和概率和为 1；浮点误差容许 1e-10；写 release ledger 后不得反馈选择。

## Baseline

### Q2-B0

DummyClassifier(strategy=most_frequent)。当前训练多数类是 2|11，但每折只从训练部分确定，不能硬编码验证标签。

### Q2-B1

LogisticRegression(C=1.0)，共享折内插补、编码与缩放。它是 HGB 的主要晋升参照。

有/无 Q1 OOF 是预注册依赖消融，不构成无限新模型族。

## Evaluation

Primary：

- 固定 17 类 macro-F1，zero_division=0；
- joint exact-match accuracy。

Secondary：

- balanced accuracy；
- NSS 分量 accuracy、MCS 分量 accuracy；
- multiclass log loss；
- 17×17 confusion matrix；
- 每类 train/validation/OOF support；
- 每折缺失训练类；
- 每个 repeat 独立指标、三者算术平均、fold dispersion 与 repeat dispersion；
- 13-fold source-blind LOSO；
- 按 AP 数、loc、nav、protocol 分层；
- 以原始组为单位并保留同组全部 repeat 预测的 95% group-bootstrap uncertainty interval；
- A03 组保留/排除敏感性；
- 有/无 Q1 OOF 消融。

## Failure Conditions

1. 观察到配置外标签、概率列错序、概率不归一或预测非法；
2. 身份、哈希、切分或特征白名单失败；
3. 使用真实标签、真实 seq_time 或训练内 Q1 预测作为输入；
4. 主 HGB macro-F1 相对 Q2-B1 改善小于 0.02，或三个 repeat 中不足两个改善；
5. HGB joint accuracy 比 Q2-B1 低超过 0.01；
6. 任何一个主类在有训练 support 时仍从不被预测，记为 minority collapse，交 O2 判断一次权重候选；
7. LOSO 相对主 CV 大幅退化但未披露；
8. A03 处理改变却未记录；
9. 输出行数不是 151 或键不唯一。

回退顺序：HGB → Q2-B1 → Q2-B0。稀有类不可学习时如实披露，不通过人工改标签制造性能。

## Expected Artifacts

S3/S4 预期产生：

- experiments/baseline/q2_baseline.json
- results/raw/baseline/q2_oof_predictions.jsonl
- results/raw/baseline/q2_metrics.json
- results/raw/baseline/q2_class_support.json
- results/raw/main/q2_candidate_metrics.json
- results/raw/main/q2_confusion_matrix.json
- results/raw/sensitivity/q2_a03_sensitivity.json
- work/06_baseline_report.md 中 Q2 章节
- logs/experiments.md 对应运行记录

上述路径是合同，不表示结果已经产生。
