# S4 Failure Analysis

## 1. Scope and evidence boundary

- Project: `rehearsal_2024_B`
- Stage: S4 — 主模型改进与证据构建
- Authorized by: G3 Round 1 PASS, review commit `a5433257bf94ab651a53b86244d8a86edc72f9e4`
- Formal implementation/run commit: `329566748d594e877b57f99cfdddf6796a584d81`
- Formal population: 1,250 AP rows / 482 complete system groups
- Validation: 15 grouped primary outer folds and 13 source-blind LOSO splits
- Evidence: `results/raw/main/`; independent artifact validation status=PASS

本报告只分析 G3 授权的 Q2/Q3 候选。Q1-B1 保持冻结，不新增 Q1 模型；四个官方测试文件只做身份哈希，数值读取和预测均为 0。

## 2. Q2 failure analysis

### 2.1 Promotion result

| Model | Role | Primary fixed-17 macro-F1 | Gain vs Q2-B1A | Joint accuracy | LOSO macro-F1 | Promotion |
|---|---|---:|---:|---:|---:|---|
| Q2-B1A Logistic | frozen baseline / rollback | 0.337654 | — | 0.755200 | 0.1609 | retained |
| Q2-M1-HGB | unweighted candidate | 0.351390 | +0.013736 | 0.786133 | 0.155544 | FAIL |
| Q2-M1W-HGB-WEIGHTED | one authorized weighting run | 0.356656 | +0.019002 | 0.785067 | 0.167729 | FAIL |
| Q2-M1-Q1-ABLATION | dependency ablation only | 0.350026 | +0.012372 | 0.789600 | 0.152789 | ineligible |

冻结门槛要求 macro-F1 至少绝对提高 0.02、至少 2/3 repeats 改善且 accuracy 降幅不超过 0.01。两个可晋级 HGB 的 repeat 与 accuracy 条件均通过，但 macro-F1 均未达到 +0.02；加权版本只差约 0.000998，也不能事后放宽阈值。因此 Q2 必须回退 `Q2-B1A`。

### 2.2 Minority collapse remains the limiting failure

无权重 HGB 的完整 primary OOF 仍触发预注册 minority-collapse 条件，因此唯一一次 `sqrt(N/(K*n_k))`, cap=5 权重实验合法触发。加权后的各 repeat 缺失预测类别为：

- repeat 0: `1|4`, `1|6`, `1|9`；
- repeat 1: `1|0`, `2|2`；
- repeat 2: 无缺失预测类别。

权重改善了平均 fixed-17 macro-F1，但波动增大：三次 repeat 的 macro-F1 SD 为 0.02139，无权重版本为 0.01353。加权 macro-F1 的 95% group-bootstrap interval 为 `[0.33335, 0.37529]`。support=1–2 的类别即使在某个 repeat 被命中，也不足以形成强可学习性结论。

### 2.3 Q1 dependency does not explain the gap

同一选定 HGB 配置加入实际 nested Q1-B1 预测后，primary macro-F1 从 0.351390 变为 0.350026，LOSO 从 0.155544 变为 0.152789。该消融不支持增加 Q1 依赖，且其角色从未具备晋级资格。

### 2.4 Source and strata risk

加权 HGB 的 LOSO overall macro-F1=0.167729，仍远低于 primary=0.356656。最差来源包括：

| Held-out source | LOSO macro-F1 | Joint accuracy | Log loss |
|---|---:|---:|---:|
| `training_set_2ap_loc0_nav82.csv` | 0.051571 | 0.780488 | 0.675565 |
| `training_set_2ap_loc2_nav82.csv` | 0.057000 | 0.269231 | 4.854641 |
| `training_set_2ap_loc0_nav86.csv` | 0.057315 | 0.950000 | 0.137725 |
| `training_set_3ap_loc30_nav86.csv` | 0.073965 | 0.908333 | 0.551524 |
| `training_set_3ap_loc33_nav82.csv` | 0.084968 | 0.279279 | 2.517541 |

高 accuracy 与低 fixed-17 macro-F1 可以同时出现，说明多数类命中不能替代稀有类覆盖。primary 分层中，加权候选的 2 AP/3 AP macro-F1 分别为 0.37712/0.32850；UDP/TCP 分别为 0.33352/0.36649。不能声称分类器已经解决跨场景或长尾问题。

## 3. Q3 failure analysis

### 3.1 Promotion and architecture decision

| Model | Primary S | Gain vs Q3-B1 | AP/System ARE90 | AP/System median bias | LOSO S | Promotion |
|---|---:|---:|---:|---:|---:|---|
| Q3-B1 Ridge | baseline / rollback | 0.804609 | 0.804609 / 0.348122 | -0.007799 / +0.011741 | 1.3233 | baseline |
| Q3-M1-HGB-UNIFIED | physics-residual unified | **0.550330** | **31.60%** | 0.550330 / 0.189701 | -0.006036 / -0.001447 | 0.729921 | PASS, selected |
| Q3-M1-HGB-APCOUNT | one split comparison | 0.573131 | 28.77% | 0.573131 / 0.179872 | -0.006072 / -0.002581 | **0.685496** | PASS, not selected |

两个候选均在 3/3 repeats 改善并通过 AP/system bias guard。按冻结的 primary selection score 选择统一模型；不得用结果出现后的 LOSO 偏好改写选择规则。AP-count split 在 system ARE90 和 LOSO 上略优，但 primary AP ARE90 较差且训练池更小，因此停止并回退统一结构。

统一候选的 selection-score 95% group-bootstrap interval 为 `[0.50902, 0.60766]`，三次 repeat SD=0.01078。其 AP/system MAE 为 15.2028/18.8935；bounded AP 负值裁剪比例为 0.000533。

### 3.2 Source-blind risk remains material

统一模型虽把 LOSO S 从 Q3-B1 的 1.3233 降到 0.729921，但场景差异仍大，不能写成所有来源上的一致鲁棒提升。

| Held-out source | LOSO S | AP MAE | System ARE90 | AP/System median bias |
|---|---:|---:|---:|---:|
| `training_set_3ap_loc33_nav82.csv` | 2.159764 | 22.2974 | 0.670180 | +0.1680 / +0.2650 |
| `training_set_3ap_loc32_nav86.csv` | 1.441823 | 27.7249 | 0.251096 | +0.0211 / +0.0997 |
| `training_set_3ap_loc32_nav82.csv` | 1.264260 | 24.2306 | 0.391380 | -0.0822 / -0.0185 |
| `training_set_3ap_loc30_nav86.csv` | 0.982309 | 30.2600 | 0.487920 | +0.1717 / +0.2182 |

primary 分层也显示主要难点来自 3 AP：统一候选的 2 AP/3 AP ARE90 为 0.22335/0.68678；`loc33` 平均 ARE90=1.09218，明显高于 `loc0`=0.13367。NAV=-88 分层为 0.78654，但该分层与来源/位置结构相关，不能解释为单变量因果效应。

### 3.3 Physical and arithmetic constraints

- 最终结构是 `physics_residual`，以折内 Q3-B1 物理/Ridge 回退为锚；
- system prediction 始终由同组 bounded AP prediction 严格求和，没有独立 system head；
- 5 个真实 AP throughput=0 的样本从相对误差分母排除并单列绝对误差；
- 全部预测有限且 bounded AP 非负；独立验证器重建 system sum 并通过。

## 4. A03 evaluation-exclusion diagnostic

A03 只从 primary OOF 评价中整体排除 3 个预注册 group；模型拟合仍保留这些组，没有执行删组重训练，因此不能称为训练鲁棒性实验。

- Q2 weighted macro-F1: 0.356656 → 0.356602；
- Q3 unified S: 0.550330 → 0.541867；
- 排除后不改变 Q2 回退或 Q3 晋级/选择结论。

## 5. Stored failure evidence and stop decision

`failure_cases.json` 保存：

- Q2 weighted 最高 row log-loss 的 20 行；
- Q3 unified 最高 AP 相对误差的 20 行；
- Q3 unified 最高 system 相对误差的 20 个完整组。

这些记录仅用于失败定位，`selection_role=diagnostic_only_no_new_candidate_authorization`。G3 授权的 Q2 四点网格、唯一权重公式、Q1 依赖消融、Q3 八候选和唯一 AP-count 对照均已耗尽；不因失败案例新增模型、网格、权重或阈值。

## 6. Conclusion

- Q2: 有小幅提升但未达冻结阈值，保留 `Q2-B1A`；长尾和 source-blind 退化是未解决风险。
- Q3: `Q3-M1-HGB-UNIFIED` 达到晋级条件并显著改善 primary/LOSO overall，但特定 3 AP 来源仍存在大误差。
- A03: 只支持“结论对评价子集排除不敏感”，不支持删组训练鲁棒性。
- 当前证据足以停止 S4 候选探索并进入 O3 冻结判断，不足以宣称所有稀有类别或所有来源均已解决。
