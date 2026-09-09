# Q1 Model Contract — Sending Opportunity and seq_time

## Problem

回答两部分：

1. 分析网络拓扑、业务、门限和节点间 RSSI 对 AP 发送机会的预测贡献、方向和稳定性；
2. 为 test_set_1_2ap 与 test_set_1_3ap 的 185 个 AP 行预测 seq_time。

发送机会以题面定义的帧序列总时长 seq_time 表征。本合同只允许预测关联解释，不把观测关联写成因果效应。

## Inputs

### Allowed

- test_dur、protocol、pkt_len、pd、ed、nav、eirp；
- AP 数；
- S2 统一 RSSI 单元统计、focal/peer 聚合；
- max-ant RSSI 与 pd/ed 的裕量；
- mean-ant RSSI 与 nav 的裕量；
- desired-to-peer RSSI 差、peer 可听数量和缺失指示。

### Key or stratum only

source_file、test_id、loc_id、bss_id、ap_name、ap_mac、ap_id、sta_mac、sta_id。ap_id/sta_id 只用于把原始 x 后缀对齐为 focal 与 peer，不作为数值或类别特征。

### Forbidden

nss、mcs、per、num_ampdu、ppdu_dur、other_air_time、throughput、所有 predict/error 占位列，以及作为输入的真实 seq_time。

## Outputs

对每个 AP 行输出：

- row key：source_file + test_id + ap_id；
- seq_time_raw，单位 s；
- seq_time_bounded=min(max(seq_time_raw,0),test_dur)，单位 s；
- 模型 ID、配置 ID、repeat/fold 或 final 标记；
- 影响分析所需的 held-out 逐行预测和特征族贡献证据。

官方输出数量为 185。原始 CSV 不被覆盖。

## Variables and Units

| Symbol | Meaning | Unit |
|---|---|---|
| g | 严格完整测试组 | dimensionless |
| i | 组内 focal AP | dimensionless |
| z_ig | 合法统一特征 | mixed |
| s_ig | 真实 seq_time | s |
| shat_ig | 预测 seq_time | s |
| T_ig | test_dur | s |
| rssi | RSSI 序列统计 | dBm |
| pd, ed | CCA 门限 | dBm |
| nav | NAV 门限，不是 NAV 时长 | dBm |
| margin | RSSI 分位数减相应门限 | dB 数值差 |

## Assumptions

1. A01 后 1,250 行、482 组是可用训练总体。
2. 同一组 AP 行不独立，必须作为一个切分原子。
3. RSSI 大尺度统计、门限和流量类型对发送机会包含预测信息，但不足以识别因果效应。
4. 训练折统计可代表相同场景内验证；LOSO 单独度量新 source 场景风险。
5. 物理输出满足 0≤seq_time≤test_dur；bounded 输出用于正式预测，同时保留 raw 结果审计。
6. 训练中恒定的 test_dur、pkt_len、pd、ed 不能支持其经验影响结论。

## Mathematical Definition

统一特征：

$$
z_{ig}=\Phi(x_{ig},\{x_{jg}:j\ne i\})。
$$

Ridge Baseline：

$$
\widehat s_{ig}=\beta_0+\beta^\top z_{ig},
\qquad
\widehat\beta=\arg\min_\beta
\sum_{ig}(s_{ig}-\beta_0-\beta^\top z_{ig})^2
+\alpha\|\beta\|_2^2，
$$

其中 alpha=1。

主候选为加法提升树：

$$
F_m(z)=F_{m-1}(z)+\eta h_m(z),
\qquad
\widehat s^{raw}=F_M(z)。
$$

正式有界输出：

$$
\widehat s^{bounded}
=\min\{\max(\widehat s^{raw},0),T\}。
$$

特征族 j 的 held-out 消融影响定义为：

$$
I_j=MAE_{without\ j}-MAE_{full}。
$$

I_j>0 表示该族在该验证设置下改善预测，不等于因果效应。

## Objective

模型拟合损失：

- Q1-B0：无拟合目标，输出训练折中位数；
- Q1-B1：带 L2 正则的平方损失；
- HGB：squared_error。

模型选择按以下词典序：

1. 最小 repeated grouped OOF MAE；
2. MAE 相同到 0.1% 内时，最小 RMSE；
3. 再相同时，参数更少、训练更快的模型。

影响分析目标是给出特征族重要性、方向和稳定性，而不是最大化表面重要性数值。

## Constraints

- group=source_file + test_id 永不跨折；
- 所有插补、编码、缩放和模型选择仅用当前训练折；
- 官方测试数值不参与任何选择；
- 输出键必须唯一、非空并保持源行顺序；
- A02 不构造虚假反向链路；
- 不把 loc_id/source_file 当预测特征；
- HGB early_stopping=false，避免内部随机行切分；
- 任何 Q1 预测进入 Q2/Q3 时，训练样本必须使用 cross-fitted 值。

## Parameters

参数来自 configs/s2_experiment_plan.json：

- outer seeds：202409、202410、202411；
- outer：5-fold GroupKFold；
- inner：3-fold GroupKFold；
- Ridge alpha=1.0；
- HGB max_iter=200、min_samples_leaf=20、learning_rate=0.05；
- max_leaf_nodes ∈ {7,15}；
- l2_regularization ∈ {0,1}；
- early_stopping=false；
- HGB 配置最多 4 个，不得临时扩网格。

## Training / Solving Procedure

1. 校验输入哈希、A01 排除和严格身份。
2. 读取冻结 outer/inner split_registry。
3. 每个外层折仅用 outer-train 拟合预处理。
4. S3 先运行 Q1-B0 与 Q1-B1，不调参。
5. O2 若授权 HGB，再在 outer-train 的固定 inner folds 选择 4 个配置之一。
6. 用选择后的配置拟合 outer-train，预测 outer-validation。
7. 合并全部 OOF 预测，计算总体、重复、折和分层指标。
8. 为下游保存严格 cross-fitted Q1 预测。
9. 模型全部冻结后才可用所有 eligible 训练行重拟合并对 test_set_1 一次推理。
10. 导出前验证 185 行、键、顺序、有限值和物理边界。

## Baseline

### Q1-B0

DummyRegressor(strategy=median)，判断复杂管道是否至少优于无信息常数。

### Q1-B1

Ridge(alpha=1.0)，使用完整共享特征，作为快速、透明和可诊断的结构 Baseline。

HGB 只有在相对 Q1-B1 有稳定增益时才晋升。

## Evaluation

Primary：

- grouped OOF MAE，单位 s；
- 每个 repeat 单独报告和合并报告。

Secondary：

- RMSE、R²；
- raw 与 bounded 指标及裁剪比例；
- AP 数、loc、nav、protocol 分层；
- 13-fold LOSO 同口径与相对退化；
- 按组 bootstrap 95% 区间。

Influence：

- feature-family ablation delta MAE；
- held-out whole-group permutation；
- 折间排名相关与方向符号；
- 样本支持和不可识别常量字段声明。

## Failure Conditions

任一发生则阻止晋升或触发回退：

1. 身份、哈希、切分交集或特征白名单断言失败；
2. 正式输出不是 185 行或键不唯一；
3. 出现非有限预测；
4. HGB 相对 Q1-B1 的 MAE 改善不足 5%，或三个 repeat 中不足两个改善；
5. HGB LOSO 相对退化比 Q1-B1 多 10 个百分点以上；
6. bounded 裁剪比例超过 10%，提示模型未学习物理范围；
7. 影响方向在三个 repeat 中不足两个一致，或重要性排名不稳定；
8. 任一事后字段或测试分布进入特征/选择。

失败回退顺序：HGB → Q1-B1 → Q1-B0。影响证据不稳定时仍可保留预测模型，但必须降低解释强度。

## Expected Artifacts

S3/S4 预期产生：

- experiments/baseline/q1_baseline.json
- results/raw/baseline/q1_oof_predictions.jsonl 或非 CSV 等价格式
- results/raw/baseline/q1_metrics.json
- results/raw/baseline/q1_crossfit_for_downstream.jsonl
- results/raw/main/q1_candidate_metrics.json
- results/raw/main/q1_feature_family_importance.json
- work/06_baseline_report.md 中 Q1 章节
- logs/experiments.md 对应运行记录

上述路径是合同，不表示文件或结果已经产生。
