# Q4 Model Contract — 全工况磁芯损耗预测

## Problem

利用附件一建立适用于四种材料及给定温度、频率、励磁波形和磁通条件的损耗预测模型，评价精度与泛化能力；模型冻结后预测附件三 400 个样本并形成行业指导边界。

## Inputs

- 附件一：$T,f,m,w,B_{0:1023},P_v$；
- 共享 `wave-v1` 特征、`condition_group` 和固定外层折；
- 附件三只在最终模型冻结后作为预测输入。

主特征为：$T,\log f,m,w,\log B_m,\log B_{pp}$ 与 `wave-v1` 的形状/斜率/频域摘要。样本序号和损耗派生信息不作输入。

## Outputs

- 每个训练样本的 OOF $\widehat P_v$、折号和模型 ID；
- 总体与分材料/波形/温度/频率/幅值指标；
- 一个冻结胜者及其完整 Pipeline、schema、配置和训练数据哈希；
- 附件三 400 个正有限预测，保留 1 位小数；
- 附件四副本第 3 列和指定 10 个样本的正文表格数据；
- 只在验证支持范围内的行业指导结论。

## Variables and Units

| Variable | Meaning | Unit |
|---|---|---|
| $x$ | 工况与 `wave-v1` 特征向量 | mixed |
| $z=\log P_v$ | 训练响应 | log(W/m³) |
| $\hat z$ | 模型的对数损耗预测 | log(W/m³) |
| $\widehat P_v$ | smearing 修正后的原尺度预测 | W/m³ |
| $m,w,T$ | 类别/离散工况 | category / °C |
| $f,B_m,B_{pp}$ | 连续工况和幅值 | Hz / T / T |

## Assumptions

1. 附件一覆盖附件三所需的主要材料和工况域，但联合分布的稀疏区域风险仍需用距离/分组误差说明。
2. 对数响应能缓解损耗长尾；最终交付必须回到 W/m³。
3. `wave-v1` 的低维摘要保留对损耗有用的主要波形信息；是否足够由同折消融判断。
4. 树模型适合中等规模表格非线性，但不具备可靠域外外推能力。
5. 附件三无损耗 Ground Truth，因此不能用于任何模型比较或精度声明。

## Mathematical Definition

物理启发对数线性 Baseline：

\[
z=\beta_0+\beta_f\log f+\beta_B\log B_m
+a_T(T)+a_m(m)+a_w(w)+\beta^Tx_{shape}+\varepsilon,
\]

用 Ridge 稳定相关特征。主候选 HistGradientBoostingRegressor 构造加法树：

\[
F_M(x)=F_0(x)+\sum_{r=1}^{M}\eta h_r(x),
\]

以对数平方损失拟合非线性和交互。RandomForestRegressor 只作挑战者。原尺度预测为：

\[
\widehat P_v=\max\{\epsilon,\exp(\hat z)\hat s\},
\]

其中 smearing 因子 $\hat s$ 只由相应训练折残差估计，$\epsilon=10^{-9}$ 防止数值非正。

## Objective

在合法分组外层 OOF 上最小化 RMSLE，并在原尺度、相对尺度和关键子组上保持稳定。复杂模型只有达到预设增益且不牺牲子组，才替代 Ridge Baseline。

## Constraints

1. 所有预处理和 smearing 因子在折内拟合。
2. 外层使用 `condition_group`，同组不跨折；完全重复记录同折。
3. 类别水平固定为训练数据的四材料、三波形、四温度；未知水平报错。
4. 预测必须有限且严格大于 0。
5. 附件三不进入特征筛选、内/外层验证、早停或超参数选择。
6. 指导结论不能超出训练支持域，也不能把模型重要性当因果效应。

## Parameters

| Model | Frozen finite search |
|---|---|
| Ridge baseline | `alpha ∈ {0.01,0.1,1,10}`；数值标准化、类别 one-hot |
| HistGradientBoosting main | `learning_rate ∈ {0.03,0.06,0.1}`，`max_leaf_nodes ∈ {15,31}`，`min_samples_leaf ∈ {20,50}`，`l2_regularization ∈ {0,1,5}`，最大迭代 500 |
| RandomForest challenger | 500 trees，`max_depth ∈ {None,16}`，`min_samples_leaf ∈ {1,4,10}`，`max_features ∈ {sqrt,0.7}` |

主候选最多 18 个固定抽样组合，挑战者最多 8 个；`random_state=20240920`，线程数不超过物理核数减一，单作业硬上限 120 分钟。

## Training / Solving Procedure

1. 先实现按材料/波形/温度分组中位数和 Ridge Baseline，生成完整 OOF 预测。
2. 只在 Baseline 五问闭环后，外层训练部分做 3 折分组内层搜索；早停数据来自内层训练，不使用外层验证或附件三。
3. 主候选与挑战者在完全相同外层折、特征版本和逐样本损失上比较。
4. 选择满足升级阈值的最简单胜者；保存折模型、参数、运行时和 OOF 预测。
5. 用全附件一重拟合胜者并冻结 Pipeline；检查重复运行预测一致性。
6. 对附件三预测一次，按 ID 1–400 校验，原尺度四舍五入到 1 位小数后写入附件四副本。
7. 从 OOF 残差和 Q3 调整后关联生成指导意义，所有陈述绑定分组指标或效应证据。

## Baseline

1. 无结构参照：训练折全局中位数；
2. 分组参照：训练折内材料×波形×温度中位数，空组回退全局中位数；
3. 正式 Baseline：共享特征的 Ridge 对数回归。

S3 至少完成上述闭环，不等待树模型。

## Evaluation

- 主指标：外层 OOF RMSLE；
- 辅助：MAE、RMSE、MAPE、中位绝对百分比误差、$R^2$；
- 子组：四材料、三波形、四温度、固定 $f/B_m$ 分箱；
- 泛化压力：留一材料、留一温度、边界频率和高损耗尾部；
- 校准：预测/真实分位表、残差对预测值、总体和子组校准斜率；
- 不确定性：`condition_group` 簇 Bootstrap 的指标与模型差区间；
- 特征消融：工况-only、工况+幅值、完整 `wave-v1`；
- 敏感性：峰值口径、重复记录、题面/实测频率边界。

树模型替代 Ridge 的最低条件：RMSLE 相对降低至少 2%，且任何样本量足够的主要子组 RMSLE 不恶化超过 10%；差异不稳定时选 Ridge。

## Failure Conditions

- 同组跨折、折内预处理泄漏或附件三参与选择；
- 预测非有限、非正或 ID 错位；
- 所有模型未优于全局/分组中位数；
- 主候选相对 Ridge 未达到 2% RMSLE 增益；
- 任一主要子组恶化超过 10%，或误差集中在某材料无法解释；
- 留一材料/温度性能崩溃却声称普遍适用；
- `wave-v1` 增量不稳定仍保留大量特征；
- 重复运行不同、内存不足或超过 120 分钟。

失败时依次回退：更强正则的 Ridge → 分材料 Ridge → 分组中位数，并缩小“普遍适用”表述；不临时引入未验证外部库或深度网络。

## Expected Artifacts

- `results/raw/s3/q4/median_baseline_metrics.json`
- `results/raw/s3/q4/ridge_oof_predictions.csv`
- `results/raw/s3/q4/ridge_metrics.json`
- `results/raw/s4/q4/candidate_comparison.csv`
- `results/raw/s4/q4/subgroup_metrics.csv`
- `results/raw/s4/q4/feature_ablation.csv`
- `results/raw/s4/q4/generalization_stress.csv`
- 冻结后 `results/raw/s4/q4/attachment3_predictions.csv`
- 冻结后附件四副本及指定样本表
