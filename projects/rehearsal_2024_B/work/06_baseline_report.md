# S3 Baseline Report

## 1. Metadata and verdict boundary

- Project: rehearsal_2024_B
- Stage: S3 — 全题 Baseline 闭环
- Authorized by: G2 Round 2 PASS, review commit `6504c54782dc33e111800b3166e9e1766cab6549`
- Formal implementation/run commit: `2222cf5f4e17a6dac832c4e65f9c5a60cd01060d`
- Formal command: `conda run -n math_modeling python projects/rehearsal_2024_B/src/s3_baseline.py`
- Independent validation: `conda run -n math_modeling python projects/rehearsal_2024_B/src/s3_validation.py`
- Result status: PASS for S3 execution and artifact validation
- Gate status: G3 尚未审核；本报告不自行宣布 G3 PASS

本次只运行 G2 授权的八个固定 Baseline。没有运行 HGB、类别权重、参数搜索或官方测试推理。

## 2. Inputs, guard, and reproducibility

真实 S3 入口先校验 run manifest，再调用任何 CSV 数值解析器。

| Item | Formal evidence |
|---|---|
| Training inputs | 13 个 allowlist CSV，逐文件规范相对路径、大小和 SHA-256 匹配 |
| Full identity check | 17/17 文件大小与 SHA-256 匹配；四个官方测试仅做字节哈希 |
| Numeric CSV reads | 13，全部为训练文件 |
| Official-test numeric reads / predictions | 0 / 0 |
| Real-entry negative tests | 四个官方测试文件逐一注入 S3 manifest，全部在解析前拒绝 |
| Eligible population | 1,250 AP 行 / 482 严格完整组 |
| Formal run start | Git 工作区 clean |
| Runtime / model fits / fit warnings | 265.167 s / 327 / 0 |
| Python / sklearn | 3.11.11 / 1.7.1 |
| Threads | 1 |

冻结哈希：

- config SHA-256: `5C2AD614190F64AA67D699F2925808434BED4B8CF8B24B036ABD9AF0B352683A`
- guard SHA-256: `24D5DA851151F41C8285691E563F063EF756A04C5699A5B2F9A6F715DECC8EE3`
- split registry file SHA-256: `B20D719E287D4F4D295D2EC497F13226C7A80C5986B70CA2269E1016BDAA3FF7`
- split registry core SHA-256: `88B108D181C2EA3A723303DED3D0E64BACEF7FA482F8322712ED97ED020A6C2D`
- feature schema SHA-256: `DD9569F8F9707F2B951AD18F75CD109F0E4AC23AA2B7717FA0F98D8FDF669C59`

Ridge 保持合同规定的 `alpha=1.0`，仅把数值求解器固定为确定性 LSQR（`tol=1e-8`, `max_iter=10000`），用于消除高相关派生特征下默认求解器的病态矩阵告警；这不是候选搜索。

## 3. Feature and validation closure

训练侧特征 dry-run 实际生成 312 个固定顺序特征，覆盖：

- 基本配置与 AP 数、protocol；
- focal STA↔AP RSSI 序列的 median/q10/q90/IQR/count/missing；
- peer AP/STA 的置换不变 strongest/weakest/mean/available/missing 聚合；
- PD、ED、NAV 裕量、desired-to-peer 差；
- peer eirp 和业务上下文。

`feature_schema.json` 的每个字段均包含 name、dtype、unit、missing_semantics 和 column_order；2 AP 与 3 AP 的列数、名称和顺序完全一致。身份字段、loc/source 和全部事后字段不进入特征。

验证闭环：

- primary: 3 repeats × 5 frozen grouped outer folds，共 15 折；
- mandatory stress: 13 个 source-blind LOSO；
- 下游训练 Q1 特征：outer/LOSO 训练边界内 3-fold Q1-B1 bounded OOF；
- 验证 Q1 特征：只由完整训练边界拟合的 Q1-B1 推理；
- 实际 lineage: primary 60 + LOSO 52 = 112 batches；
- prediction∩fit=0，held-out∩fit=0；
- upstream identity 全部为 Q1-B1 / seq_time_bounded / q1_clip_0_test_dur_v1；
- group bootstrap: 1,000 次，seed=202412；抽样原始组并保留该组三个 repeat 的全部预测。

独立验证器从 gzip JSONL 重算并通过 21 项全局、12 项 Q1、19 项 Q2 和 31 项 Q3 检查。

## 4. Q1 — seq_time and sending opportunity

### 4.1 Predictive performance

Primary 为每个 repeat 合并 OOF 后的 bounded MAE，再对三次 repeat 取算术平均。

| Model | Primary MAE (s) | 95% group-bootstrap interval | Repeat SD | LOSO MAE (s) | Clip |
|---|---:|---:|---:|---:|---:|
| Q1-B0 median | 11.1226 | [10.7454, 11.5040] | 0.0546 | 11.2860 | 0 |
| Q1-B1 Ridge | **5.5054** | **[5.1977, 5.8370]** | 0.0523 | 7.0266 | 0 |

Q1-B1 相对 Q1-B0 的 primary MAE 降低约 50.5%，三次 repeat 稳定且无物理裁剪，足以作为 Q1 可用底座和 Q2/Q3 固定上游。

### 4.2 Held-out predictive contribution

下表只表示 held-out 预测贡献/条件关联，不解释为因果效应。

| Feature family | Mean ablation ΔMAE (s) | Positive repeats | Mean group-permutation ΔMAE (s) | Positive repeats |
|---|---:|---:|---:|---:|
| Mechanism margins | +0.7480 | 3/3 | +6.0403 | 3/3 |
| Peer RSSI | +0.1696 | 3/3 | +6.7743 | 3/3 |
| Desired RSSI | +0.1109 | 3/3 | +9.3423 | 3/3 |
| Basic | -0.0008 | 0/3 | +0.1209 | 3/3 |
| Group context | -0.0017 | 1/3 | +0.0549 | 3/3 |

机制裕量、peer RSSI 和 desired RSSI 的消融方向在 3/3 repeats 一致。Basic/group-context 的消融与置换证据不一致，不给出强排序。训练中恒定字段也不生成经验影响结论。

### 4.3 Failure modes

- 2 AP MAE=3.2273 s；3 AP MAE=6.5463 s，且三次 repeat 均同向。
- 最差 LOSO 来源为 `training_set_3ap_loc33_nav82.csv`，MAE=9.9464 s。
- 因 G2 已冻结下游上游身份，即使 S4 改进 Q1 自身，也不得替换 Q2/Q3 的 Q1-B1 特征。

## 5. Q2 — fixed joint (NSS,MCS)

| Model | Primary macro-F1 | Accuracy | Log loss | 95% F1 interval | LOSO macro-F1 | LOSO accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Q2-B0 majority | 0.0383 | 0.4832 | 17.8496 | [0.0359, 0.0405] | 0.0383 | 0.4832 |
| Q2-B1A Logistic, no Q1 | **0.3377** | **0.7552** | **1.0042** | [0.3063, 0.3636] | **0.1609** | **0.5112** |
| Q2-B1B Logistic + Q1 OOF | 0.3343 | 0.7544 | 1.0055 | [0.3023, 0.3598] | 0.1580 | 0.5048 |

结论：

1. 两个 Logistic 都显著优于多数类底座，全题分类闭环已形成。
2. Q1 OOF 未带来增益：B1B 比 B1A 的 primary macro-F1 低 0.0033，LOSO 也低 0.0030；S4 不把 Q1 依赖作为主改进。
3. 固定 17 类严重不平衡，support 最低的 `1|6`、`1|7`、`2|2` 各只有 1，`1|4` 与 `1|9` 各 2。B1A 三次 repeat 都未预测 `1|6`、`1|7`、`2|2`，另有部分 repeat 未预测 `1|4`/`1|9`，满足 minority-collapse 诊断。
4. LOSO 相对 primary 明显退化；最差来源 `training_set_2ap_loc2_nav82.csv` 的 macro-F1=0.0303、accuracy=0.2179。
5. A03 的三个 0|0 所在完整组按预注册规则整体从 OOF 评价中排除后，B1A macro-F1=0.3375、accuracy=0.7560，主结论基本不变。主模型拟合仍保留 A03，未改标签。

## 6. Q3 — AP and system throughput

`S_Q3=max(ARE90_AP, ARE90_system)`，越低越好；primary 全部使用 nonnegative bounded AP，system 严格由 bounded AP 求和。

| Model | Primary S | AP ARE90 | System ARE90 | AP median bias | System median bias | LOSO S | Clip |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q3-B0 median | 1.4518 | 1.4518 | 0.7419 | -0.0055 | -0.0050 | 1.5587 | 0 |
| Q3-B1 Ridge | **0.8046** | **0.8046** | **0.3481** | -0.0078 | +0.0117 | 1.3233 | 0.0011 |
| Q3-B2 physical eta | 0.8556 | 0.8556 | 0.3570 | +0.0173 | +0.0463 | **0.9347** | 0 |

Q3-B1 的 primary S bootstrap 95% interval 为 [0.7169, 0.9101]；Q3-B2 为 [0.7527, 0.9445]。B1 是 primary 最佳 Baseline，但 B2 在 LOSO 上明显更稳，说明物理锚点具有场景外推价值。

强制检查：

- 每个 model×repeat 均有 1,250 AP 与 482 system OOF；
- LOSO 每个模型覆盖 1,250 AP / 482 system；
- 每个 system prediction 与其 bounded AP prediction 之和绝对差为 0；
- 5 个真实 AP throughput=0 的样本未加入 epsilon，从相对误差分母排除并单列绝对误差；
- 482 个 system truth 均为正；
- bounded AP 全部非负且有限。

失败模式：

- Q3-B1 的 2 AP ARE90=0.5241，3 AP ARE90=0.9493；三次 repeat 的 3 AP 均更差，满足预注册的 AP-count 条件对照门槛。
- 最差 LOSO 来源 `training_set_3ap_loc33_nav82.csv`，B1 S=4.9790；物理结构需要作为非线性残差锚点验证。
- A03 完整组排除后 B1 S=0.7876、B2 S=0.8442，不改变 primary 排名。

## 7. Output and dry-run closure

正式原始结果位于 `results/raw/baseline/`，逐行证据使用 gzip JSONL，不使用 CSV：

- `feature_schema.json`
- `run_manifest.json`
- `post_run_validation.json`
- `q1_oof_predictions.jsonl.gz`
- `q1_crossfit_for_downstream.jsonl.gz`
- `q1_actual_upstream_lineage.json`
- `q2_oof_predictions.jsonl.gz`
- `q3_ap_oof_predictions.jsonl.gz`
- `q3_system_oof_predictions.jsonl.gz`
- 三问 metrics、Q3 CDF、support、strata、A03、influence 和 bootstrap JSON。

训练侧 OOF 输出已完成字段、固定标签、有限值、物理边界和 AP→system 导出 dry-run。官方输出行数只保留合同，不生成或查看测试预测。

## 8. Known limitations and handoff to O2

- Q2 稀有类坍缩与 LOSO 分布偏移仍未解决。
- Q3 3 AP 与 source-blind 外推明显弱于场景内 primary；B1/B2 存在“场景内精度—物理外推稳定性”取舍。
- Q1 的 3 AP 误差较高，但当前 Ridge 已形成稳定可回退底座；在最多两个 S4 主要方向约束下，其 HGB 暂不优先。
- A03 敏感性是 OOF 评价完整组排除，不是另一次删组重拟合；因差异极小，当前不授权扩大该实验。
- 所有数字仍属于 `results/raw/`；G3 PASS 前不得进入 S4，G5 核验前不得迁入 `results/verified/`。

O2 失败诊断见 [o2_baseline_diagnosis.md](optimization/o2_baseline_diagnosis.md)。
