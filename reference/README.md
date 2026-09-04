# 数学建模方法速查库

本目录用于赛前选型、假设检查和结果验证。使用顺序建议为：先明确问题、数据生成过程与评价标准，再选择最简单可验证的 Baseline；只有当统一验证显示稳定增益时，才升级到更复杂方法。这里的条目不能替代题意分析、官方规则和针对当前数据的实验。

## 目录导航

- [数据处理](data_processing/)：缺失、异常、尺度和泄漏。
- [统计与基础建模](statistics/)：探索、相关、推断、回归与重采样。
- [机器学习](machine_learning/)：降维、聚类和树集成。
- [时间序列](time_series/)：分解、预测与时序验证。
- [优化](optimization/)：连续和离散资源配置。
- [评价与验证](evaluation/)：任务指标与敏感性。
- [建模机制](modeling/)：预留，后续补充微分方程、仿真等主题。
- [可视化](visualization/)：预留，后续补充探索图和论文图规范。

## 按任务类型选型

| 问题特征 | 首选 Baseline | 可考虑的升级 | 必做验证 |
|---|---|---|---|
| 连续变量预测 | 均值/中位数、[线性回归](statistics/linear_regression.md) | [随机森林](machine_learning/random_forest.md)、[梯度提升树](machine_learning/gradient_boosting.md) | 交叉验证、残差与子群误差 |
| 二分类或多分类 | 多数类/规则、简单线性分类器 | 随机森林、梯度提升树 | 分层或分组验证、混淆矩阵、校准 |
| 季节性时间序列 | 季节朴素法、[指数平滑](time_series/exponential_smoothing.md) | [ARIMA/SARIMA](time_series/arima_sarima.md)、分解后建模 | [滚动回测](time_series/time_series_cross_validation.md)、残差和区间覆盖 |
| 多指标结构压缩 | 保留原变量、相关筛查 | [PCA](machine_learning/pca.md) | 载荷稳定性、重构与下游性能 |
| 无监督分群 | 规则分层、[K-Means](machine_learning/kmeans_dbscan.md) | DBSCAN、后续可补层次聚类 | 参数/扰动稳定性、领域解释 |
| 资源分配与指派 | 简单可行策略、连续 LP | [MILP](optimization/linear_mixed_integer_programming.md) | 逐约束复算、松弛界、gap 和敏感性 |
| 两组或多组差异 | 效应差和区间 | [假设检验](statistics/hypothesis_testing.md)、置换或 Bootstrap | 设计假设、多重比较、实际意义 |
| 方案稳健性 | 单因素与离散情景 | [全局敏感性分析](evaluation/sensitivity_analysis.md) | 范围依据、收敛、约束可行性 |

## 数据进入模型前

1. 用[描述性统计与 EDA](statistics/descriptive_statistics.md)确认单位、分布、分组和样本量。
2. 记录[缺失值处理](data_processing/missing_values.md)及[异常值检测](data_processing/outlier_detection.md)规则，保留原值和标记。
3. 对距离、内积或正则化模型选择合适的[特征缩放](data_processing/feature_scaling.md)。
4. 按预测时点、主体或组设计切分，并完成[数据泄漏检查](data_processing/data_leakage.md)。

## 统计推断与关系检查

- [相关性分析](statistics/correlation_analysis.md)：先看关系形状，再选 Pearson、Spearman 或 Kendall；不能据此宣称因果。
- [假设检验](statistics/hypothesis_testing.md)：同时报告效应量、区间和设计假设，不把显著性当重要性。
- [Bootstrap](statistics/bootstrap.md)：重采样单位必须匹配独立、时间或簇结构。

## 预测评价入口

先阅读[常用预测评价指标](evaluation/prediction_metrics.md)。指标应匹配真实代价；保留逐样本、逐折或逐时点预测，报告 Baseline、区间和关键子群结果。时间序列不能用随机 K 折替代滚动回测。

## 常见错误提醒

- 不先做 Baseline，无法判断复杂方法是否带来真实增益。
- 在全数据上填补、缩放、筛选、PCA 或目标编码，造成数据泄漏。
- 反复查看测试集调参、选阈值或挑指标。
- 无依据堆叠算法，只有训练拟合或单次划分结果。
- 用 AHP、熵权或 TOPSIS 代替真实机制，且不检查权重与排序敏感性。
- 用启发式算法掩盖可由 LP、MILP 或网络流精确建模的问题。
- 只报告优化目标，不逐条验证约束、界和参数扰动后的可行性。
- 把相关性、特征重要性或模型解释值写成因果效应。
- 对时间、空间或同一主体重复观测做普通随机切分。
- 只给单一平均指标，忽略不确定性、关键子群和极端场景。

## 使用与维护

- 方法文档采用统一的 13 节结构，先看“适用问题”“不适用”“验证”和“常见误用”。
- 软件接口可能变化，实现前应复核各文档中的官方链接及当前环境版本。
- 新增主题前先更新[覆盖计划](coverage_plan.md)，避免同义文件和过深目录。
