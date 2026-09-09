# S4 Main Model Report

## 1. Formal run metadata

| Item | Value |
|---|---|
| Stage authorization | G3 PASS, review commit `a5433257bf94ab651a53b86244d8a86edc72f9e4` |
| Formal implementation/run commit | `329566748d594e877b57f99cfdddf6796a584d81` |
| Command | `conda run -n math_modeling python projects/rehearsal_2024_B/src/s4_main.py` |
| Runtime | 4,791.800 s |
| Eligible population | 1,250 AP rows / 482 complete groups |
| Validation boundaries | 15 primary outer folds / 13 source-blind LOSO |
| Candidate budget | Q2 4 HGB configs; Q3 4 direct + 4 physics-residual configs |
| Model fits / warnings | 1,751 / 0 |
| Actual Q1 lineage | 448 batches; both overlap totals=0 |
| Official test numeric reads / predictions | 0 / 0 |
| Independent validation | PASS; 74 checks |

正式运行从 clean Git commit 启动。训练输入只接受冻结 allowlist 中的 13 个 CSV；四个官方测试文件只做路径、大小和 SHA-256 身份校验。

## 2. Shared implementation decisions

1. `basic__ap_count` 继续使用 numeric binary 2/3，所有 S4 候选完全一致；没有把新表示与旧 Baseline 混合比较。
2. Q2/Q3 可选上游继续固定为 Q1-B1 / `seq_time_bounded` / `q1_clip_0_test_dur_v1`。
3. 每个 downstream inner/outer/LOSO 边界都使用实际折内 Q1 预测；448 个 lineage batches 中 prediction-fit 与 downstream-validation-fit overlap 均为 0。
4. 预处理只在当前训练折拟合；Q2 概率固定展开到冻结 17 类。
5. Q3 只用 bounded AP 作为晋级口径，system 严格由 AP 求和。

## 3. Nested selection and unique full-data rules

### 3.1 Q2

冻结的四个 HGB 配置共享 `learning_rate=0.05`, `max_iter=200`, `min_samples_leaf=20`, `early_stopping=false`, `random_state=202409`，只组合 `max_leaf_nodes={7,15}` 与 `l2_regularization={0,1}`。

对每个配置汇总 45 个 primary downstream-inner 记录，按以下冻结词典序选择：

1. 最大 fixed-17 macro-F1；
2. 若 macro-F1 差小于 0.002，最大 joint accuracy；
3. 最小 multiclass log loss；
4. 更小模型。

唯一入选配置为 `Q2-C3`: max_leaf_nodes=15, l2_regularization=1.0。45 条 inner 记录汇总 macro-F1=0.330705、accuracy=0.765809、log loss=1.060699。权重是否保留只由 outer promotion 决定。

### 3.2 Q3

八个候选为同一四点 HGB 网格下的 direct 与 physics-residual 结构。inner 选择先最小化 `max(ARE90_AP, ARE90_system)`；0.5% 内再比较 normalized AP/system MAE、bias 与复杂度。

45 个 primary inner 记录唯一选择 `Q3-physics_residual-C3`:

- learning_rate=0.05;
- max_leaf_nodes=15;
- l2_regularization=1.0;
- inner selection score=0.580391;
- mean normalized AP/system MAE=0.124028;
- worst absolute median signed bias=0.011445。

AP-count split 与否只由 outer promotion 和冻结 primary 规则决定；官方测试不参与。

## 4. Q2 model comparison

| Model | Primary macro-F1 | Accuracy | Log loss | F1 repeat SD | F1 95% bootstrap | LOSO F1 | Promotion |
|---|---:|---:|---:|---:|---:|---:|---|
| Q2-B1A | 0.337654 | 0.755200 | 1.004248 | — | `[0.3063, 0.3636]` (S3) | 0.1609 | retained baseline |
| Q2-M1-HGB | 0.351390 | 0.786133 | 1.108862 | 0.01353 | `[0.32717, 0.37134]` | 0.155544 | FAIL |
| Q2-M1W-HGB-WEIGHTED | **0.356656** | 0.785067 | 1.095128 | 0.02139 | `[0.33335, 0.37529]` | **0.167729** | FAIL |
| Q2-M1-Q1-ABLATION | 0.350026 | **0.789600** | 1.104168 | 0.01690 | `[0.32856, 0.36716]` | 0.152789 | diagnostic only |

无权重 HGB 仍发生预定义类别坍缩，因此触发且只执行了一次平方根逆频率权重，单样本权重 cap=5。加权候选的 macro-F1 绝对增益为 0.019002，小于冻结门槛 0.02；不能按四舍五入判为通过。最终 Q2 保留 `Q2-B1A`，全量配置为 LogisticRegression, C=1.0, class_weight=null, uses_q1=false。

## 5. Q3 model comparison

`S=max(ARE90_AP, ARE90_system)`，越低越好。

| Model | Primary S | AP ARE90 | System ARE90 | AP/System MAE | LOSO S | Repeat SD | Promotion |
|---|---:|---:|---:|---:|---:|---:|---|
| Q3-B1 Ridge | 0.804609 | 0.804609 | 0.348122 | 23.5287 / 37.2231 | 1.3233 | — | baseline |
| Q3-M1-HGB-UNIFIED | **0.550330** | **0.550330** | 0.189701 | 15.2028 / 18.8935 | 0.729921 | **0.01078** | **PASS, selected** |
| Q3-M1-HGB-APCOUNT | 0.573131 | 0.573131 | **0.179872** | **15.1646 / 18.2312** | **0.685496** | 0.01445 | PASS, comparison only |

统一物理残差候选相对 Q3-B1 的 primary S 改善 31.60%，3/3 repeats 改善，AP/system bias guard 全部通过；selection-score 95% group-bootstrap interval=`[0.50902, 0.60766]`。AP-count split 也通过晋级阈值，但其 primary S 较差，故按照预注册 primary 规则不保留分模。

最终 Q3 为：

```text
model_id: Q3-M1-HGB-UNIFIED
architecture: physics_residual
config: Q3-C3
learning_rate: 0.05
max_leaf_nodes: 15
l2_regularization: 1.0
ap_count_split: false
system_head: none; system=sum(bounded AP)
```

## 6. Ablation, sensitivity and robustness evidence

| Evidence | Result | Interpretation |
|---|---|---|
| Q2 without/with Q1 | 0.351390 / 0.350026 primary macro-F1 | Q1 dependency does not improve HGB classification |
| Q2 unweighted/weighted | 0.351390 / 0.356656 | weighting helps but misses promotion threshold |
| Q3 unified/AP-count split | 0.550330 / 0.573131 primary S | split not retained; it has a LOSO tradeoff |
| A03 exclusion, Q2 weighted | 0.356656 → 0.356602 macro-F1 | evaluation-only exclusion; conclusion unchanged |
| A03 exclusion, Q3 unified | 0.550330 → 0.541867 S | evaluation-only exclusion; conclusion unchanged |
| Q3 unified source-blind LOSO | S=0.729921 | better than Q3-B1 overall, but worst source S=2.159764 |

具体失败案例、分层差异和不能作出的鲁棒性结论见 [07_failure_analysis.md](07_failure_analysis.md)。

## 7. Final frozen candidate stack

| Question | Frozen model | Decision |
|---|---|---|
| Q1 | Q1-B1 Ridge(alpha=1.0, solver=lsqr), bounded postprocess | unchanged rollback-quality baseline |
| Q2 | Q2-B1A LogisticRegression(C=1.0), no Q1 | HGB stopped and rolled back |
| Q3 | Q3-M1-HGB-UNIFIED, physics-residual Q3-C3 | promoted |

该组合是唯一 O3 freeze candidate。模型选择已经关闭；在 G4 审核期间不得根据任何官方测试反馈修改。

## 8. Known limitations

- Q2 fixed-17 rare classes with support 1–2 remain intrinsically weak; no strong class-level learnability claim is made.
- Q2 and Q3 both have primary-to-LOSO gaps; aggregate LOSO improvement does not imply every source improves.
- Q3 unified is selected by frozen primary evidence although AP-count split has better LOSO aggregate; this is a disclosed selection/robustness tradeoff.
- A03 is not a delete-group refit experiment.
- `results/raw/main/` is unverified-stage evidence; nothing is written to `results/verified/` before G5.
- Official test release still requires G4 PASS plus a complete S5 freeze manifest and exactly-once release ledger.

## 9. Result

S4 candidate selection is complete. Q2 stops at the approved rollback; Q3 promotes the unique unified physics-residual configuration. The package is ready for O3=`FREEZE_CANDIDATE` and G4 review, but this report does not self-approve G4.
