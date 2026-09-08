# S5 Result Freeze — 结果核验与冻结

## 1. Freeze Status

- Active Project：`projects/rehearsal_2024_C`
- Stage：`S5 — 结果核验、冻结与交接`
- Freeze ID：`S5-FREEZE-2024C-V1`
- Status：`FROZEN_PENDING_G5`
- G4 Review：`PASS`
- G4 Reviewed Commit：`2309b1e361701be9818544fa18740cd8f5694f2e`
- G4 Review Commit：`82504cc9343b437181e66520aee74c56e863d87a`
- S5 Verification：84/84 PASS，47 个白名单文件晋级

本文件冻结进入绘图和论文的模型、结果、证据边界与复现入口。G5 通过前不得称为“最终提交已批准”；但绘图和写作人员可以只读使用 `results/verified/`。

## 2. Frozen Model Set

### Q1 波形分类

- 模型：`wave-v1` 形状特征 + StandardScaler + 多项 Logistic；
- 超参数：`C=0.1`，`class_weight=None`，`max_iter=2000`；
- 类别编码：1=正弦波，2=三角波，3=梯形波；
- 模型 SHA-256：`1DAEB3B97CA30B28A8E1D6748347B79D2B4DDFF1844969172774C3CC8000810F`；
- 选择理由：分组 OOF Macro-F1=1.000，且相位/幅值压力和留一材料最低 Macro-F1 均为1.000；不增加无收益复杂度。

### Q2 温度修正 Steinmetz

令

\[
z=\frac{T-25}{65},
\]

冻结全量参数形式为

\[
\widehat P_v
=s\,k_{25} f^{\alpha}B_m^{\beta}
\exp(\gamma_1z+\gamma_2z^2),
\]

其中 `k_25=0.190476333889`、`alpha=1.64624946552`、`beta=2.51385006268`、`gamma_1=-1.27664996144`、`gamma_2=0.511759560615`、smearing `s=1.0208733625`。参数的机器可读来源为 `results/verified/q2/quadratic_temperature_parameters.csv`。

### Q3 三因素调整后关联

- 模型：控制 `log(f)` 与 `log(B_m)` 后，材料、温度、波形主效应及三组预定义两两交互的 effect-coded spline Ridge；
- 全量拟合 `alpha=0.01`；
- OOF log-RMSE：0.326667；
- 500/500 次 `condition_group` 簇 Bootstrap 有效；
- 解释边界：只能写“调整后关联”，不能写因果效应。

### Q4 全工况损耗预测

- 最终模型：对数损耗上的 HistGradientBoostingRegressor；
- 特征变体：`amplitude_and_condition`；
- 数值特征：18 个工况与幅值摘要；类别特征为材料、波形、温度；
- 超参数：`learning_rate=0.1`、`max_leaf_nodes=15`、`min_samples_leaf=20`、`l2_regularization=1.0`、`max_iter=500`、`random_state=20240920`；
- smearing：1.0012201264981795；
- 模型 SHA-256：`B284879E38401A301DF02FAF564A4CD482623816E9704DCDADFA8E25DF71AABD`；
- 分组 OOF RMSLE：0.070941。

### Q5 双目标权衡

- 决策域：附件一中满足主频率域的实测工况点；
- 损耗目标：Q4 严格 OOF 预测；传输磁能代理：`f × B_m`；
- 主结果：118 个 OOF Pareto 点、27 个折支持区域、42 个 Bootstrap 稳定区域；
- 冻结限制：模型区域与观测区域 Jaccard=0.39535<0.50，`unique_recommendation_authorized=false`；
- 允许输出 Pareto 权衡、端点、稳定区域和临时膝点；禁止唯一最优工况。

## 3. Official Prediction Freeze

### 附件二

- 80/80 样本完成；
- 正弦波20、三角波44、梯形波16；
- 预测 CSV SHA-256：`3CDFF53B66547E757DCED07A4D13FE492F8EA33B1F72116A789233ED8F0C5DA7`；
- 正式路径：`results/verified/q1/attachment2_predictions.csv`。

指定样本编码：

| ID | 1 | 5 | 15 | 25 | 35 | 45 | 55 | 65 | 75 | 80 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 编码 | 2 | 2 | 1 | 2 | 3 | 3 | 2 | 2 | 2 | 1 |

### 附件三

- 400/400 样本完成，全部预测正且有限；
- 预测范围：535.4564–2,315,612.5707 W/m³；
- 预测 CSV SHA-256：`1C16A4B46788906F6C15EAD2E72112F45F1F021C09512199541D6442C56D8290`；
- 正式路径：`results/verified/q4/attachment3_predictions.csv`。

指定样本预测（W/m³，1位小数）：

| ID | 16 | 76 | 98 | 126 | 168 | 230 | 271 | 338 | 348 | 379 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 预测 | 1060.2 | 1582245.4 | 12081.2 | 1730.0 | 93658.3 | 69929.5 | 1785363.6 | 13398.8 | 903120.2 | 1396.5 |

附件四已在副本中填入：

`results/verified/submission/附件四（Excel表）.xlsx`

原始附件四未被改动，其 SHA-256 仍为 `D8FDFFDF63839F7B40D5DD87BE6923AF04AD1D52180072A47C5B4DF70832C1C8`。

## 4. Verification and Provenance

权威入口：

- 证据登记：`results/verified/result_registry.md`；
- 独立验证：`results/verified/verification_report.json`；
- raw→verified 一对一哈希：`results/verified/provenance.json`；
- 模型冻结：`results/verified/model_freeze.json`；
- 测试预测摘要：`results/verified/prediction_summary.json`。

验证覆盖：

1. 五个官方输入的 SHA-256 与冻结配置一致；
2. G4 PASS 与 Reviewed Commit 一致；
3. S4 独立复算 23/23 PASS；
4. Q1/Q4 模型哈希与批准清单一致；
5. 附件二、三 ID、字段、特征和波形指纹完整；
6. Q1 标签、编码和三类概率逐行复算一致；
7. Q4 对数预测、原尺度预测和1位小数值逐行复算一致；
8. 附件四 80+400 个映射、表头、ID 和空白区正确；
9. 原始附件未改动；
10. 每个晋级文件与 raw 来源 SHA-256 完全一致。

## 5. Controlled Recovery Record

附件二/三预测 CSV 首次生成于提交 `c4d7121caf028df40788037fe5666ca63e2aa108`。模板序号列使用公式，导致附件四后处理失败；恢复流程只读复算已有 CSV 并验证恢复前后哈希不变，没有重写预测。相关失败和恢复清单保存在：

- `results/raw/s5/runs/EXP-S5-PRED-001/failed_manifest_pre_output.json`；
- `results/raw/s5/runs/EXP-S5-PRED-001/failed_manifest_after_prediction_csvs.json`；
- `results/raw/s5/runs/EXP-S5-PRED-001/failed_manifest_recovery_guard.json`；
- `results/raw/s5/runs/EXP-S5-PRED-001/run_manifest.json`。

## 6. Reproduction

从项目目录执行安全复验：

```powershell
cd projects/rehearsal_2024_C
conda run --no-capture-output -n math_modeling python src/verify_s5_outputs.py --config experiments/s2_frozen_config.json
```

当前 raw 预测已冻结，通常不得再次调用生成器。只有在明确授权重建、确认冻结附件与模型哈希一致并将现有结果归档后，才可使用 `run_s5_predictions.py`。

## 7. Frozen Limitations

1. 附件二、三没有公开真值，不能用正式预测构造外部测试精度。
2. Q1 的完美 OOF 不能表述为未知测试集100%正确。
3. Q2 在50°C局部误差略有劣化。
4. Q3 的共同矩形支持仅14.24%，且13/40两两对比未达0.90符号稳定度。
5. Q4 留一材料/温度压力明显弱于插值 OOF；不得声称任意新材料、新温度均可靠。
6. Q5 主 Jaccard 门槛失败，不得给出唯一推荐。
7. 正式图片尚未绘制；见 `work/handoff/figure_handoff.md` 的 Skill 与缺失配色指南约束。

## 8. Change Control

G5 前禁止修改冻结模型、参数、预测 CSV、附件四副本或 verified 证据。若 Reviewer 要求修复：

1. 先记录 Required Fix；
2. 明确哪些 Evidence ID 失效；
3. 不得在原文件上无痕替换数值；
4. 重新运行验证并更新 registry、provenance、两份 handoff；
5. 重新提交 G5。
