# Q3 Model Contract — 磁芯损耗因素与两两交互

## Problem

在控制频率与磁通密度峰值后，分析温度、励磁波形、磁芯材料对损耗的独立关联和两两协同关联，比较影响程度，并给出数据支持域内可能损耗较低的三因素条件。

## Inputs

- 附件一全部 12,400 条记录；
- $P_v,T,w,m,f,B_m$；
- 共享 `condition_group` 和固定折；
- 不使用附件二、三。

## Outputs

- 温度、波形、材料的调整后主效应与统一尺度影响程度；
- $T\times w$、$T\times m$、$w\times m$ 三组两两交互；
- 组 Bootstrap 95% 区间与折间稳定性；
- 数据支持域内低损耗的 $(T,w,m)$ 条件及适用限定；
- 明确的关联性而非因果性表述。

## Variables and Units

| Variable | Role | Unit |
|---|---|---|
| $z=\log P_v$ | 模型响应 | log(W/m³) |
| $T$ | 四水平解释因素 | °C / category |
| $w$ | 三水平解释因素 | category |
| $m$ | 四水平解释因素 | category |
| $\log f$ | 工况控制变量 | log(Hz) |
| $\log B_m$ | 工况控制变量 | log(T) |
| $a,\eta$ | 主效应与两两交互参数 | log-loss contrast |

## Assumptions

1. 观测数据支持调整后关联分析，但不能证明温度、材料或波形的因果效应。
2. 对数损耗能缓解长尾与异方差；残差诊断仍必须执行。
3. 48 个三因素组合都有样本，但 $f/B_m$ 的组间分布可能不平衡，故必须控制工况并限制在共同支持域。
4. 低阶平滑足以先控制 $f/B_m$ 的主要非线性；交互只讨论题目指定的两两项。

## Mathematical Definition

Baseline（无交互）：

\[
z_i=\mu+s_f(\log f_i)+s_B(\log B_{m,i})
+a_T(T_i)+a_w(w_i)+a_m(m_i)+\varepsilon_i.
\]

完整分析模型：

\[
z_i=\mu+s_f(\log f_i)+s_B(\log B_{m,i})
+a_T+a_w+a_m
+\eta_{Tw}+\eta_{Tm}+\eta_{wm}+\varepsilon_i.
\]

$s_f,s_B$ 用 `SplineTransformer(degree=2, n_knots=4)` 的固定基函数；类别使用和为零的 effect coding，交互同样施加可识别约束。若设计矩阵病态，则回退到折内标准化后的 Ridge，正则强度只从预设小网格选择。

因素 $G$ 的预测影响度定义为移除该因素相关主效应及交互、重新拟合后外层 OOF 损失增量：

\[
I_G=\frac{L_{-G}-L_{full}}{L_{full}}.
\]

该量表示预测/关联贡献，不解释为因果贡献。

## Objective

在保持解释结构的前提下最小化外层 OOF log-RMSE，并估计三因素主效应、两两交互和低损耗组合的不确定性。模型简洁性优先于极小的预测增益。

## Constraints

1. 只包含三组两两交互，不加入 $T\times w\times m$ 三阶项。
2. 必须控制 $\log f$ 与 $\log B_m$；不能直接比较未调整组均值并称为独立影响。
3. effect coding 和基函数只在训练折构建设定；未知类别必须报错。
4. 影响程度用统一 OOF 损失增量或标准化对比，不直接比较不同编码的原始系数。
5. 最低损耗条件只在 48 个已观测因素组合和共同 $f/B_m$ 支持内评估。

## Parameters

| Parameter | Frozen value |
|---|---|
| response | `log(core_loss_W_per_m3)` |
| spline degree / knots | 2 / 4 |
| Ridge fallback alpha | `{0, 0.01, 0.1, 1}`，0 表示最小二乘 |
| outer split | `condition_group`，目标 5 折 |
| cluster bootstrap | 500 次，seed `20240921` |
| interaction set | `T×w`, `T×m`, `w×m` only |

## Training / Solving Procedure

1. 生成描述性表：每个因素和 48 个组合的样本数、损耗中位数与四分位数。
2. 检查 48 个组合的 $f/B_m$ 范围和共同支持；无共同支持的区域不做直接调整对比。
3. 在固定外层折拟合无交互 Baseline 和完整两两交互模型，保存 OOF 预测与设计矩阵条件数。
4. 对每个因素分别移除其主效应和相关交互并重新拟合，计算 $I_G$。
5. 以 `condition_group` 为重采样单位执行 500 次 Bootstrap，保存主效应对比、交互对比、$I_G$ 和最低组合分布。
6. 对每个观测行在保持其 $f/B_m$ 的条件下预测 48 种因素组合；只保留训练共同支持中的反事实组合，再对经验工况分布做标准化平均，得到调整后组合损耗。
7. 报告最低调整后组合及区间；若区间重叠，报告候选集合而不是唯一最优。

## Baseline

两层 Baseline：

1. 分层描述统计（中位数、IQR、样本数），明确未控制混杂；
2. 控制 $\log f/\log B_m$、只含三个主效应的加性回归。

完整两两交互模型只有在 OOF 和 Bootstrap 证据支持时才替代加性 Baseline。

## Evaluation

- 拟合充分性：OOF log-RMSE、MAE、残差对拟合值/$f/B_m$；
- 主效应：标准化边际均值对比和 95% 簇 Bootstrap 区间；
- 影响程度：$I_T,I_w,I_m$ 及区间；
- 交互：完整模型相对加性模型的 OOF 增益，以及每组交互对比区间；
- 稳定性：按材料/波形/温度折间方向一致性、峰值口径和重复记录敏感性；
- 最低条件：组合入选频率、区间重叠和共同支持比例。

## Failure Conditions

- 48 个组合中出现空格或共同支持不足却仍做无条件比较；
- 设计矩阵不可识别、条件数过大且 Ridge 回退仍不稳定；
- 完整交互模型 OOF 明显劣于加性 Baseline；
- 主效应或交互方向在折/Bootstrap 中频繁反转；
- 残差仍强依赖 $f/B_m$，说明工况控制不足；
- 把系数、置换贡献或最低组合写成因果结论；
- 删除长尾/重复记录后结论反转而未披露；
- Bootstrap 超过 60 分钟预算。

失败时回退到加性模型或分层描述，缩小结论为“数据中的调整后关联”，不增加三阶交互或黑箱解释器。

## Expected Artifacts

- `results/raw/s3/q3/descriptive_factor_table.csv`
- `results/raw/s3/q3/additive_oof_predictions.csv`
- `results/raw/s3/q3/additive_metrics.json`
- `results/raw/s4/q3/interaction_model_comparison.csv`
- `results/raw/s4/q3/main_effects_bootstrap.csv`
- `results/raw/s4/q3/pairwise_interactions_bootstrap.csv`
- `results/raw/s4/q3/factor_importance.csv`
- `results/raw/s4/q3/minimum_condition_candidates.csv`
