# 图 5 预测诊断图：模板比较与有标签验证工作流

本指南供正式比赛复用，顺序为**确定诊断问题与证据 → 比较模板 → 核验逐点数据 → 三版同口径候选 → PNG 检查与比较 → 用户确认 → 正式导出**。图 5 可呈现回归残差、分类混淆或其他有真值的误差诊断；不预设面板数、图型和配色。内容定位见[八图总指南](figures_guide.md)，数据及导出时序遵守[绘图规范](09_plotting_protocol.md)。

## 0. 确定诊断范围与证据

读取题目、交接资料、`results/verified/` 中的逐点预测、汇总指标和证据登记表。说明图 5 与图 4 的分工：图 4 给出核心结果，图 5 解释误差结构或类别混淆。记录训练侧 OOF、独立验证或有标签测试的范围、重复编号、观测粒度、样本或组数、目标单位和 Evidence ID。无真实标签的官方测试不能用来计算或绘制测试误差。

回归任务先确定残差定义（例如预测值减真实值）并在图注写明；分类任务核对类别全集、固定顺序、支持数和混淆矩阵的行列含义。区间、显著性和异常样本标签只有在有可追溯计算或人工判定时才能使用。

**进入下一步的条件：**逐点记录、汇总指标、范围和口径可互相核对；不一致时先修正资源，不靠图面掩盖。

## 1. 搜集并比较模板

### 1.1 适用模板库网址

以下网址只作为模板发现入口，不代表其中任何具体模板已经通过用户验证。

#### 回归残差、拟合偏差与影响点

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| scikit-learn PredictionErrorDisplay | [https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html) | 真实值—预测值、残差—预测值和基础回归误差诊断 | 只使用有标签且逐点配对的数据，明确残差方向、验证范围和参考线 |
| statsmodels | [https://github.com/statsmodels/statsmodels](https://github.com/statsmodels/statsmodels) | Q-Q、残差、影响点、杠杆值、时间序列残差相关和统计模型诊断 | 诊断前提依赖具体模型；不能把 OLS 假设检验模板直接套到任意黑盒模型 |
| lmdiag | [https://github.com/dynobo/lmdiag](https://github.com/dynobo/lmdiag) | 类似 R `plot(lm)` 的残差—拟合、Q-Q、Scale-Location 和 Residuals-Leverage 四图组 | 主要面向线性回归及兼容模型；必须核对模型对象、Cook 距离和杠杆值定义，不能用于不适配模型 |
| Yellowbrick Regression Visualizers | [https://github.com/DistrictDataLabs/yellowbrick](https://github.com/DistrictDataLabs/yellowbrick) | Residuals、Prediction Error、Alpha Selection 和回归诊断结构 | 核对其拟合接口、训练/验证拆分与版本；不要把训练诊断写成独立验证结果 |
| Matplotlib Gallery | [https://matplotlib.org/stable/gallery/index.html](https://matplotlib.org/stable/gallery/index.html) | 自定义残差分布、误差随时间/分组变化和多面板布局 | 必须进入具体示例核对源码、轴定义和数据需求；通用样式不单独算诊断模板 |

#### 分类混淆、阈值与判别能力

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| scikit-learn 分类显示器 | [ConfusionMatrixDisplay](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ConfusionMatrixDisplay.html)、[RocCurveDisplay](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.RocCurveDisplay.html)、[PrecisionRecallDisplay](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PrecisionRecallDisplay.html)、[CalibrationDisplay](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibrationDisplay.html) | 混淆矩阵、ROC、PR 和可靠性图的官方实现 | ROC/PR/校准需要预测分数或概率；类别不平衡时不能只给 ROC，归一化混淆矩阵需同时报告支持数 |
| scikit-plots | [https://github.com/scikit-plots/scikit-plots](https://github.com/scikit-plots/scikit-plots) | 分类器评估面板、混淆矩阵、ROC、PR、校准、学习曲线等组合 | 先核对当前版本 API 和所需输入；组合面板不能省略验证范围、阈值和类别顺序 |
| Yellowbrick Classification Visualizers | [https://github.com/DistrictDataLabs/yellowbrick](https://github.com/DistrictDataLabs/yellowbrick) | Class Prediction Error、Confusion Matrix、ROC-AUC、PR、阈值与分类报告图 | 适合快速比较诊断结构；论文最终图仍需固定类别全集、阈值和数据拆分 |
| Seaborn heatmap | [https://seaborn.pydata.org/generated/seaborn.heatmap.html](https://seaborn.pydata.org/generated/seaborn.heatmap.html) | 混淆矩阵、分组误差矩阵或有明确定义的二维诊断量 | 色阶、标注、矩阵方向和归一化口径必须有数据依据，不能用色差夸大微小差异 |

#### 概率校准与预测不确定性

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| Uncertainty Toolbox | [https://github.com/uncertainty-toolbox/uncertainty-toolbox](https://github.com/uncertainty-toolbox/uncertainty-toolbox) | 回归预测区间、校准曲线、区间覆盖、锐度和误差—不确定性诊断 | 当前重点是回归不确定性；必须有预测均值、尺度/区间与真实值，区间覆盖不能由点预测臆造 |
| Calzone | [https://github.com/DIDSR/calzone](https://github.com/DIDSR/calzone) | 概率分类的可靠性图、校准指标、Bootstrap 区间与多分类校准 | 只有模型输出概率且校准样本范围明确时使用；分箱方式、置信区间和患病率/基率调整需写清 |

#### 时间序列预测诊断

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| utilsforecast | [https://github.com/Nixtla/utilsforecast](https://github.com/Nixtla/utilsforecast) | 多序列真实值—预测值、预测区间、分组评估和统一时间轴可视化 | 保留训练/验证切分、预测起点、频率、季节性与序列 ID；随机抽取序列时须记录选择规则 |
| statsmodels 时间序列图形 | [https://github.com/statsmodels/statsmodels](https://github.com/statsmodels/statsmodels) | 残差 ACF/PACF、预测图、QQ 和时序模型诊断 | 只绘制实际计算的残差及置信界；不能把时间相关性图解释成因果关系 |

### 1.2 已验证好用的模板

暂无已确认模板。只有用户明确确认某个具体模板好用后，才能在下表添加记录；代理自行筛选、成功运行或完成试绘均不算用户确认。

| 模板名称 | 具体模板链接或路径 | 适用场景 | 确认记录 |
|---|---|---|---|

### 1.3 按诊断问题选择模板类型

创建候选前先明确要查找的失效模式，再进入相应模板库：

- **回归的总体偏差与异方差：**优先真实值—预测值、残差—拟合值和分组残差；需要经典线性模型假设检查时再使用 statsmodels/lmdiag。
- **异常点、杠杆值和高影响样本：**只有能够计算相应统计量并核对模型假设时才使用影响图；普通大残差不能自动称为高影响点。
- **分类的错分结构：**使用混淆矩阵或 Class Prediction Error；固定类别顺序，同时展示原始计数或支持数，避免只给归一化色块。
- **阈值与类别不平衡：**有预测概率时比较 ROC、PR、阈值曲线；正类稀少时 PR 通常比单独 ROC 更能显示失效，但两者指标口径须一致。
- **概率可信度：**分类用 CalibrationDisplay/Calzone，回归区间用 Uncertainty Toolbox；概率分箱、区间覆盖和置信水平必须可追溯。
- **时间序列预测：**使用真实值—预测值—区间及残差随时间/滞后图；不能把随机打乱的普通回归诊断直接套到时序验证。
- **无真实标签的数据：**不得制作图 5；可改为输入分布检查或部署监控，但不能称作预测误差诊断。

图 5 只保留能解释错误结构的面板。若某面板只是重复图 4 的主结果或重复汇总指标，应删除；图型越多不代表诊断越完整。

### 1.4 模板检索与比较要求

创建候选前实际查看至少三个适配的官方图库示例、科研图模板或有源码的案例，检查数据输入、轴定义、图例、标签密度、面板布局和论文缩小后的可读性。配色样式不能单独算一个模板；确实不足三个时记录关键词、来源和原因。

在 `projects/<project_name>/figures/figure5/template_review.md` 记录来源、具体示例路径、版本和许可证、适用数据、可借鉴结构、需修改之处、复现方法和误导风险，再选出三个不同的表达方案。回归、分类、概率校准和时间序列任务应从各自对应类型选择，不固定三面板结构。

## 2. 核验数据并制作三版候选

用可重运行脚本直接读取已核验文件，检查唯一键、样本数、缺失值、目标与预测的配对、重复或折的边界。回归图重算必要指标并核对残差方向；分类图核对每个混淆矩阵的单元和等于对应样本数，不把不同重复相加后冒充单次结果。若分组绘制，检查每组支持数；异常时停止绘图。

按模板比较结果制作同一证据范围的 A/B/C 三版，分别保留绘图脚本或可编辑源。各版指标、类别顺序、残差定义和坐标语义一致；可因任务差异调整布局。至少进行一轮“生成 → 导出至少 300 DPI 的 PNG → 目视检查 → 修改源文件 → 再导出”，核对拥挤标签、过度绘制、颜色与灰度、异常点和论文宽度下的字形。

在 `candidate_comparison.md` 根据实际 PNG 比较三版的诊断价值、信息密度、尺度公平性和可复现性，给出推荐顺序并交给用户确认。候选阶段只保留各版源文件与 PNG；不得提前保存 SVG/PDF。必要的模板、证据和数据记录照常保留。

## 3. 用户确认后正式导出

用户明确选定最终版本后，仅为该版导出 SVG/PDF，检查矢量对象、字体、裁切、画布一致性和论文版面可读性；若失败，修改源文件并重新导出。未入选版本继续只保留源文件和 PNG。`delivery.md` 记录数据版本或哈希、Evidence ID、重建命令、候选比较、用户确认和最终导出检查。

2024 B 题的[绘图数据](../projects/rehearsal_2024_B/results/verified/figure_data/fig05_prediction_diagnostics.json)、[模板评审](../projects/rehearsal_2024_B/figures/figure5/template_review.md)和[候选比较](../projects/rehearsal_2024_B/figures/figure5/candidate_comparison.md)展示了 Q3 AP 的 OOF 回归诊断及 Q2 分类混淆；对应证据为 E-Q3-OOF-001、E-Q2-CONF-001。该实例的旧候选矢量导出不改变本指南的候选阶段规则。

## 可复用的任务说明

> 从题目、`results/verified/` 和证据登记表确定图 5 的有标签验证范围，核对逐点预测、残差定义、类别顺序、概率或时间索引。按诊断问题从本指南的回归、分类、校准或时序模板库中实际比较至少三个具体示例，写入 `figures/figure5/template_review.md`；用同口径数据生成三版可重建候选，只保留源文件与至少 300 DPI 的 PNG。完成实图检查和 `candidate_comparison.md`，把候选交给我确认；确认后才为选定版导出并检查 SVG/PDF。