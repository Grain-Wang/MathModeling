# Writing Handoff — 论文技术写作交接

## 1. Authority and Scope

- 只引用：`results/verified/`
- 数字索引：`results/verified/result_registry.md`
- 模型身份：`results/verified/model_freeze.json`
- 数字来源：`results/verified/provenance.json`
- 当前状态：G5 已 PASS，S6 技术一致性与提交准备进行中；不得写成 G6 已通过或最终文件已可提交

论文技术主线：

```text
附件一只读审计
→ wave-v1 统一特征与分组外层折
→ Q1 形状分类
→ Q2 可解释温度修正
→ Q3 控制连续工况后的三因素调整关联
→ Q4 跨工况 HGB 损耗预测
→ Q4 严格 OOF 供给 Q5 双目标 Pareto
→ 附件二/三一次性冻结预测
→ 84 项独立核验与 47 文件 verified 白名单
```

## 2. Data and Validation Language

训练集共12,400条记录，覆盖四种材料、四档温度和三类波形，每条含1,024点单周期磁通密度序列。附件二含80条分类测试样本，附件三含400条损耗预测样本；两者均无公开目标真值。

统一使用工况组隔离的外层 OOF。论文中统一写：

- “分组 OOF”或“外层分组交叉验证”；
- 不写“随机划分测试集”；
- 附件二/三只称“冻结预测”，不称“外部测试精度”；
- 所有损耗单位统一为 W/m³；
- `fB_m` 单位写为 Hz·T，并说明它只是题目规定的传输磁能代理。

数据审计图表来源：`results/verified/data/`。

## 3. Q1 — 励磁波形分类

### Model

`wave-v1` 的30个相位/尺度稳健形状特征，经 StandardScaler 后输入多项 Logistic；不使用温度、频率、材料或损耗作为主分类输入。

\[
p_k(x)=\frac{\exp(w_k^Tx+b_k)}{\sum_{r=1}^{3}\exp(w_r^Tx+b_r)},
\qquad
\hat c=\arg\max_kp_k(x).
\]

超参数：`C=0.1`、`class_weight=None`。类别编码：1=正弦波、2=三角波、3=梯形波。

### Verified answer

- 12,400条分组 OOF 的 Macro-F1、Accuracy、Balanced Accuracy 均为1.000；
- 三项相位/幅值变换预测一致率为1.000；
- 留一材料最低 Macro-F1=1.000；
- 附件二：正弦20、三角44、梯形16。

指定样本：

| 样本 | 1 | 5 | 15 | 25 | 35 | 45 | 55 | 65 | 75 | 80 |
|---:|---|---|---|---|---|---|---|---|---|---|
| 类别 | 三角 | 三角 | 正弦 | 三角 | 梯形 | 梯形 | 三角 | 三角 | 三角 | 正弦 |
| 编码 | 2 | 2 | 1 | 2 | 3 | 3 | 2 | 2 | 2 | 1 |

### Evidence

- E001：`results/verified/q1/oof_metrics.json`
- E002：`results/verified/q1/invariance_metrics.csv`
- E003：`results/verified/q1/attachment2_predictions.csv`

### Required caveat

“训练分组 OOF 中未观察到分类错误”不等于“附件二100%正确”。不得把附件二预测概率解释为已校准的真实置信度。

## 4. Q2 — 温度修正 Steinmetz

### Model

在材料1、正弦波子集上，以25°C为锚点：

\[
z=\frac{T-25}{65},\qquad
\widehat P_v
=s\,k_{25}f^\alpha B_m^\beta
\exp(\gamma_1z+\gamma_2z^2).
\]

全量冻结参数：

| 参数 | 数值 |
|---|---:|
| `k_25` | 0.190476333889 |
| `alpha` | 1.64624946552 |
| `beta` | 2.51385006268 |
| `gamma_1` | -1.27664996144 |
| `gamma_2` | 0.511759560615 |
| smearing `s` | 1.0208733625 |

### Verified answer

- 传统 Steinmetz OOF RMSLE=0.360678；
- 二次温度修正 OOF RMSLE=0.202567；
- 相对改善43.84%，四档温度中三档不劣化；
- 25°C、90°C 留一温度 RMSLE 分别由0.62624/0.55430降至0.22788/0.30606；
- 50°C局部 OOF RMSLE 由0.12065升至0.12796，必须披露。

### Evidence

- E004：`results/verified/q2/quadratic_temperature_metrics.json`
- 参数：`results/verified/q2/quadratic_temperature_parameters.csv`
- E005：`results/verified/q2/leave_one_temperature_comparison.csv`

### Required caveat

温度修正改善总体及边界温度外推，但不是每一温度都改善；不能写成“各温度均显著优于传统方程”。

## 5. Q3 — 三因素独立及协同影响

### Model

以对数损耗为响应，控制 `log(f)`、`log(B_m)` 的二次样条，并对温度、波形、材料使用效应编码；加入温度×波形、温度×材料、波形×材料三组预定义两两交互。全量 Ridge `alpha=0.01`。

### Verified answer

- 加性模型 OOF log-RMSE=0.343416；
- 两两交互模型 OOF log-RMSE=0.326667，改善4.88%；
- 500/500次工况组簇Bootstrap有效；
- 40个两两对比中27个符号稳定度≥0.90；
- 主效应方向在当前编码与支持域内表现为：材料1/2低于总体、材料3/4高于总体；70/90°C低于总体、25/50°C高于总体；正弦/梯形低于总体、三角高于总体；
- 500次Bootstrap中，调整后最低组合均为 `90°C｜正弦波｜材料1`。

### Evidence

- E006：`results/verified/q3/interaction_metrics.json`
- E007：`results/verified/q3/bootstrap_main_effect_intervals.csv`
- `results/verified/q3/bootstrap_pairwise_interaction_intervals.csv`
- `results/verified/q3/bootstrap_lowest_combination_frequency.csv`

### Required caveat

共同矩形支持仅14.24%。以上是模型调整后的关联和Bootstrap稳定性，不是温度、材料或波形的因果效应；不在共同支持域内不得机械外推。

## 6. Q4 — 全工况磁芯损耗预测

### Model

最终模型在 (log P_v) 上拟合 HistGradientBoostingRegressor，并用训练残差 smearing 返回 W/m³：

\[
F_M(x)=F_0(x)+\sum_{r=1}^{M}\eta h_r(x),
\qquad
\widehat P_v=\max\{10^{-9},\exp(F_M(x))s\}.
\]

最终使用18个工况与幅值摘要，加材料、波形、温度类别特征；删除未带来收益的形状特征。参数见 `results/verified/model_freeze.json`。

### Verified answer

- Ridge OOF RMSLE=0.200097；
- 完整48特征 HGB OOF RMSLE=0.076397；
- 最终18特征 HGB OOF RMSLE=0.070941；
- 最终 OOF：MAE=9,368.96 W/m³、MAPE=5.482%、原尺度 R²=0.99523；
- 低 `B_m` 子集 RMSLE=0.08328；
- 最大留一材料/留一温度 RMSLE 分别为0.37982/0.57496。

附件三共400条冻结预测，全部正有限，范围535.4564–2,315,612.5707 W/m³。指定样本：

| ID | 16 | 76 | 98 | 126 | 168 | 230 | 271 | 338 | 348 | 379 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| W/m³ | 1060.2 | 1582245.4 | 12081.2 | 1730.0 | 93658.3 | 69929.5 | 1785363.6 | 13398.8 | 903120.2 | 1396.5 |

### Evidence

- E008：`results/verified/q4/hgb_metrics.json`、`ablation_metrics.json`
- E009：`results/verified/q4/final_oof_predictions.csv`
- E010：`results/verified/q4/stress_metrics.json`
- E011：`results/verified/q4/attachment3_predictions.csv`

### Required caveat

主精度来自附件一的分组 OOF。附件三无真值；留一水平压力明显弱于插值 OOF，因此不能宣称对任意新材料或新温度具有同等精度。

## 7. Q5 — 磁芯损耗与传输磁能权衡

### Model

在附件一实测联合可行域中，以 Q4 严格 OOF 损耗最小、`E=fB_m` 最大构造 Pareto 集。全量模型 Pareto只作部署参考，不参与主选择。

### Verified answer

- 去重候选12,236个；
- 主 OOF Pareto点118个；
- 折支持区域27个；
- 500/500次 `condition_group` Bootstrap有效，稳定区域42个；
- 模型/观测区域 Jaccard=0.39535<0.50；
- 单点合格数为0，`unique_recommendation_authorized=false`。

可报告但不得称为唯一推荐的三个代表点：

| 角色 | 材料 | T (°C) | 波形 | f (Hz) | Bm (T) | OOF损耗 (W/m³) | fBm (Hz·T) |
|---|---|---:|---|---:|---:|---:|---:|
| 最小 OOF 损耗端点 | 材料4 | 90 | 正弦 | 89080 | 0.015462 | 544.47 | 1377.36 |
| 临时几何膝点 | 材料1 | 90 | 三角 | 396820 | 0.122978 | 898876.24 | 48799.98 |
| 最大能量端点 | 材料1 | 70 | 三角 | 354610 | 0.218857 | 2747961.76 | 77608.98 |

临时膝点由归一化目标到理想点的几何距离确定，不代表用户偏好。最小损耗端点的部分一致性检查失败，也不能包装成工程推荐。

### Evidence

- E012：`results/verified/q5/final_oof_pareto.csv`
- E013：`results/verified/q5/bootstrap_region_stability.csv`
- E014：`results/verified/q5/robustness_metrics.json`
- 代表点：`results/verified/q5/representative_conditions.json`

### Required caveat

真实工程还缺少磁芯尺寸、饱和、温升、成本等约束。本问只能给数据支持域中的双目标权衡、稳定区域与端点，不能给“全局唯一最优工况”。

## 8. Safe Abstract Numbers

摘要可安全使用：

1. Q1 分组 OOF Macro-F1=1.000，并通过相位/幅值和留一材料压力；
2. Q2 RMSLE从0.3607降至0.2026，改善43.84%；
3. Q3 两两交互较加性模型改善4.88%，500次Bootstrap完成；
4. Q4 最终分组 OOF RMSLE=0.07094，较 Ridge 降低约64.55%；
5. Q5得到118个 OOF Pareto点、27个折支持区域和42个Bootstrap稳定区域，但Jaccard=0.39535未达0.50，因此不提供唯一推荐；
6. 附件二80条和附件三400条冻结预测已完成，但无公开真值。

## 9. Prohibited Claims

不得写：

- “附件二分类准确率100%”；
- “附件三测试集 RMSLE=0.07094”；
- “温度修正对每个温度都更优”；
- “温度/材料/波形导致损耗变化”；
- “HGB可以可靠外推到任意新材料、新温度”；
- “Q5找到全局唯一最优工况”；
- “42个稳定区域说明单点推荐可靠”；
- 任何未登记在 `result_registry.md` 的数值。

## 10. Figures and Tables

- 图表需求、坐标、单位、数据路径和 Skill 门槛：`work/handoff/figure_handoff.md`；
- 附件四正式副本：`results/verified/submission/附件四（Excel表）.xlsx`；
- 图表制作不得读取 raw；
- 正式图片完成后，论文图注必须标 Evidence ID，并在 S6 做数字一致性检查。

## 11. Remaining Work for S6

1. 由用户确认并安装/指定绘图 Skill，补齐缺失配色指南后生成正式图；
2. 按官方模板完成论文正文；
3. 将公式、变量、单位、图表、附件四与 E001–E015 逐项对照；
4. 检查摘要强度、引用、匿名要求和提交文件命名；
5. 运行技术一致性审计并提交 G6。
