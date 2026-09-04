# ARIMA 与 SARIMA（Autoregressive Integrated Moving Average）

## 1. 适用问题

适用于单变量序列经差分后自相关结构相对稳定的短中期预测。ARIMA 描述非季节自相关，SARIMA 加入季节差分与季节 AR/MA 项；二者应与朴素、季节朴素和指数平滑比较。

## 2. 不适用或需谨慎的情况

结构突变、多重季节、强非线性、长记忆或外生变量主导时，基本 ARIMA 可能不足。短序列上高阶模型难稳定估计；过度差分会增加噪声，自动选阶也不能替代诊断。

## 3. 核心思想

用差分去除随机趋势或季节非平稳，再用过去观测的线性组合和过去冲击描述剩余依赖。指数平滑从状态更新角度建模趋势季节，ARIMA 从自相关角度建模，两者是互补候选。

## 4. 基本数学形式

非季节 ARIMA 可写为

$$
\phi(B)(1-B)^d y_t=c+\theta(B)\varepsilon_t,
$$

其中 $B y_t=y_{t-1}$。SARIMA 再乘季节算子 $\Phi(B^m)(1-B^m)^D$ 与 $\Theta(B^m)$。

## 5. 输入、输出与主要假设

输入为等间隔序列、周期、候选阶数和可选外生变量；输出为参数、点预测与区间。通常要求差分后过程近似平稳，创新项均值为零且无剩余自相关；参数需满足相应稳定与可逆条件。

## 6. 标准建模流程

画序列与季节图；建立朴素 Baseline；根据题意、差分图和单位根诊断选择 $d,D$；用 ACF/PACF 和信息准则提出少量候选；在滚动回测中选阶；检查残差后再生成预测区间。若使用外生变量，应明确它在预测期是否已知或另有可验证的预测来源，否则样本内改进无法部署。

## 7. 评价与验证方式

按目标预测跨度滚动回测；比较 MAE、RMSE、MASE 等；检查残差 ACF 与 Ljung–Box 结果、偏差和异常；评估区间覆盖。信息准则只用于训练窗内候选筛选，不能替代样本外评价。诊断检验的滞后阶应与季节周期和样本量匹配，并同时查看残差图，避免只凭一个 $p$ 值判定白噪声。

## 8. 优点

模型结构清晰，可直接刻画自相关与季节滞后；在规则、线性时间依赖中常能提供有竞争力且易诊断的预测。

## 9. 局限

阶数和差分选择敏感，对突变与非线性适应有限。参数解释依赖变换和差分，长期预测往往趋于简单趋势或水平。预测区间通常依赖创新项和模型结构正确，在异方差或结构变化下可能覆盖不足。

## 10. 华为杯常见用法

用于月度、季度需求和经济指标预测。论文应写明频率、差分阶、季节周期、候选选择规则、滚动回测与残差白噪声检查。

## 11. 常见误用

以 ADF 未拒绝就反复差分；只凭 AIC 选复杂模型；在完整序列定阶后声称做了回测；随机交叉验证；忽略季节朴素 Baseline；残差仍强自相关却直接解释预测。

## 12. Python 实现建议

使用 statsmodels `ARIMA` 或 `SARIMAX`。显式给出 `order`、`seasonal_order` 和趋势项；用 `get_forecast` 获取区间，并在每个回测窗口重新拟合。自动选阶结果仅作候选。

## 13. 权威参考

1. Box, G. E. P., Jenkins, G. M., Reinsel, G. C., Ljung, G. M. *Time Series Analysis: Forecasting and Control*, 5th ed., Wiley, 2015.
2. Hyndman, R. J., Athanasopoulos, G. *Forecasting: Principles and Practice*, ARIMA models：https://otexts.com/fpp3/arima.html，访问日期：2026-09-04。
3. statsmodels Documentation, Time Series Analysis：https://www.statsmodels.org/stable/tsa.html，访问日期：2026-09-04。
