# Q2 Model Contract — 含温度的 Steinmetz 修正

## Problem

在附件一材料1、正弦波条件下，量化传统 Steinmetz 方程随温度变化的误差，并构造显式包含温度的修正方程，与传统方程做同折、同指标比较。

## Inputs

- 附件一中 `material=材料1` 且 `waveform=正弦波` 的 1,067 条记录；
- $T$、$f$、统一口径 $B_m=\max|B_j|$、响应 $P_v$；
- 共享 `condition_group` 和固定外层折。

## Outputs

- 传统 Steinmetz 参数 $k,\alpha,\beta$；
- 温度修正参数 $k,\alpha,\beta,\gamma_1,\gamma_2$；
- 两模型逐样本 OOF 预测、总体/分温度误差、残差与参数稳定性；
- 修正是否更好的成对证据与适用边界。

## Variables and Units

| Variable | Meaning | Unit |
|---|---|---|
| $T$ | 温度 | °C |
| $\tau=(T-25)/65$ | 归一化温度 | dimensionless |
| $f$ | 频率 | Hz |
| $B_m$ | 磁通密度峰值 `max(abs(B))` | T |
| $P_v$ | 磁芯损耗密度 | W/m³ |
| $k,\alpha,\beta$ | Steinmetz 参数 | $k$ 含相应量纲，指数无量纲 |
| $\gamma_1,\gamma_2$ | 温度修正参数 | dimensionless |

## Assumptions

1. 在材料1正弦波子集内，幂律是可解释 Baseline。
2. 温度影响可先由低自由度平滑乘性因子近似。
3. 记录均为正值，可进行对数拟合；对数目标强调相对而非绝对误差。
4. 残差可能异方差，因此结论以 OOF 预测和簇 Bootstrap 为主，不只依赖训练内标准误。
5. 只有四个离散温度，不能据此声称在 25–90°C 内任意温度连续外推都已验证。

## Mathematical Definition

传统方程：

\[
P_v=k f^{\alpha}B_m^{\beta},\qquad
\log P_v=\log k+\alpha\log f+\beta\log B_m+\varepsilon.
\]

主温度修正：

\[
P_v=k f^{\alpha}B_m^{\beta}
\exp(\gamma_1\tau+\gamma_2\tau^2),
\]

\[
\log P_v=\log k+\alpha\log f+\beta\log B_m
+\gamma_1\tau+\gamma_2\tau^2+\varepsilon.
\]

在 25°C 时 $\tau=0$，修正因子为 1，便于解释。若主修正触发失败条件，唯一允许的升级候选是在 S4 加入 $\tau\log f$ 和 $\tau\log B_m$ 两项；不得继续无界增加高阶项。

## Objective

通过最小化训练折上的对数平方误差估计参数；模型选择以外层 OOF RMSLE 最小为主，并检查原尺度误差与分温度稳定性。

## Constraints

1. 只使用材料1、正弦波数据；$f,B_m,P_v$ 必须为正。
2. Baseline 和修正模型使用完全相同的外层折、样本和预测后处理。
3. $B_m$ 主口径全题一致；`B_pp/2` 只作敏感性。
4. 反变换后预测必须有限且大于 0；smearing 偏差修正只能在训练折残差上估计。
5. 不根据附件三表现改变温度函数或指标。

## Parameters

| Item | Frozen setting |
|---|---|
| 外层验证 | `condition_group` GroupKFold，目标 5 折 |
| 温度压力测试 | Leave-one-temperature-level-out，4 次 |
| 拟合 | 含截距的线性最小二乘；不做逐步显著性筛选 |
| Bootstrap | 500 次 `condition_group` 簇重采样，seed `20240921` |
| 主峰值口径 | `max(abs(B))` |
| 敏感峰值口径 | `B_pp/2` |

## Training / Solving Procedure

1. 按固定条件筛选 1,067 条数据，核验四个温度均有样本。
2. 对每个外层折分别拟合传统方程与温度修正方程。
3. 只用相应训练折估计对数反变换的 smearing 因子，生成验证折原尺度预测。
4. 汇总逐样本 OOF 误差和分温度残差；做同样本成对比较。
5. 运行四次留一温度压力测试，明确这是温度层外推而非主随机泛化分数。
6. 若修正达到进入条件，用全子集重拟合并冻结方程；否则按 Failure Conditions 处理。

## Baseline

传统三参数 Steinmetz 方程 $P_v=k f^\alpha B_m^\beta$，对数线性最小二乘估计。另记录按训练折中位数预测作为无结构参照，但不替代传统方程比较。

## Evaluation

- 主指标：OOF RMSLE；
- 辅助：MAE、RMSE、MAPE、中位绝对百分比误差、$R^2$；
- 分温度：四个温度分别报告同一指标和残差中位数；
- 比较：簇 Bootstrap 的“修正−传统”成对指标差 95% 区间；
- 诊断：残差对 $f$、$B_m$、$T$，参数折间稳定性；
- 敏感性：`max(abs(B))` 与 `B_pp/2` 口径、保留/去除完全重复记录。

“修正更好”的最低证据为：总体 OOF RMSLE 下降，且至少 3/4 温度层 RMSLE 不劣化；若 Bootstrap 区间跨 0，必须表述为改善不确定。

## Failure Conditions

- 任一输入非正、非有限或折泄漏；
- 参数不可识别、数值病态或符号/量级极不稳定；
- 反变换产生非有限/非正预测；
- 修正模型总体 RMSLE 不下降，或两个以上温度层明显劣化；
- 修正增益只存在训练内而不在 OOF；
- 峰值口径改变后结论反转；
- 留一温度误差不可接受，仍声称连续温度泛化；
- 运行超出 15 分钟预算。

失败时保留传统 SE Baseline，最多评估预先定义的两个温度交互项；仍失败则诚实报告“该低阶温度修正未稳定改善”，不得继续数据驱动地堆高阶项。

## Expected Artifacts

- `results/raw/s3/q2/steinmetz_baseline_parameters.csv`
- `results/raw/s3/q2/baseline_oof_predictions.csv`
- `results/raw/s3/q2/baseline_metrics.json`
- `results/raw/s4/q2/temperature_corrected_parameters.csv`
- `results/raw/s4/q2/model_comparison.csv`
- `results/raw/s4/q2/residual_by_temperature.csv`
- `results/raw/s4/q2/peak_definition_sensitivity.csv`
