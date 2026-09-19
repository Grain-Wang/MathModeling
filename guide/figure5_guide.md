# 图 5 预测诊断图：模板比较与有标签验证工作流

本指南供正式比赛复用，顺序为**确定诊断问题与证据 → 比较模板 → 核验逐点数据 → 三版同口径候选 → PNG 检查与比较 → 用户确认 → 正式导出**。图 5 可呈现回归残差、分类混淆或其他有真值的误差诊断；不预设面板数、图型和配色。内容定位见[八图总指南](figures_guide.md)，数据及导出时序遵守[绘图规范](09_plotting_protocol.md)。

## 0. 确定诊断范围与证据

读取题目、交接资料、`results/verified/` 中的逐点预测、汇总指标和证据登记表。说明图 5 与图 4 的分工：图 4 给出核心结果，图 5 解释误差结构或类别混淆。记录训练侧 OOF、独立验证或有标签测试的范围、重复编号、观测粒度、样本或组数、目标单位和 Evidence ID。无真实标签的官方测试不能用来计算或绘制测试误差。

回归任务先确定残差定义（例如预测值减真实值）并在图注写明；分类任务核对类别全集、固定顺序、支持数和混淆矩阵的行列含义。区间、显著性和异常样本标签只有在有可追溯计算或人工判定时才能使用。

**进入下一步的条件：**逐点记录、汇总指标、范围和口径可互相核对；不一致时先修正资源，不靠图面掩盖。

## 1. 搜集并比较模板

### 1.1 适用模板库网址

以下网址只作为模板发现入口，不代表其中任何具体模板已经通过用户验证。

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| Matplotlib Gallery | [https://matplotlib.org/stable/gallery/index.html](https://matplotlib.org/stable/gallery/index.html) | 残差、误差分布、分类矩阵和诊断面板的通用实现 | 必须进入具体示例并核对源码、轴定义与数据需求 |
| scikit-learn PredictionErrorDisplay | [https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html) | 回归任务的真实值—预测值及残差诊断 | 只使用有标签且逐点配对的数据，明确残差方向和验证范围 |
| scikit-learn ConfusionMatrixDisplay | [https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ConfusionMatrixDisplay.html](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ConfusionMatrixDisplay.html) | 分类混淆矩阵、类别顺序和标签展示 | 核对行列含义、支持数及是否归一化，不跨重复错误合并 |
| Seaborn heatmap | [https://seaborn.pydata.org/generated/seaborn.heatmap.html](https://seaborn.pydata.org/generated/seaborn.heatmap.html) | 混淆矩阵或有明确定义二维数值的热力图 | 色阶、标注和矩阵方向必须有数据依据，不能用色差夸大微小差异 |
| Yellowbrick Regression Visualizers | [https://www.scikit-yb.org/en/latest/api/regressor/index.html](https://www.scikit-yb.org/en/latest/api/regressor/index.html) | 残差、预测误差和回归诊断结构 | 借鉴前核对其拟合接口和数据拆分，避免把训练诊断写成独立验证结果 |

### 1.2 已验证好用的模板

暂无已确认模板。只有用户明确确认某个具体模板好用后，才能在下表添加记录；代理自行筛选、成功运行或完成试绘均不算用户确认。

| 模板名称 | 具体模板链接或路径 | 适用场景 | 确认记录 |
|---|---|---|---|

### 1.3 模板检索与比较要求

创建候选前实际查看至少三个适配的官方图库示例、科研图模板或有源码的案例，检查数据输入、轴定义、图例、标签密度、面板布局和论文缩小后的可读性。可检索 Matplotlib、Seaborn、scikit-learn、PGFPlots 等对应图型的原始示例；配色样式不能单独算一个模板。确实不足三个时记录关键词、来源和原因。

在 `projects/<project_name>/figures/figure5/template_review.md` 记录来源、适用数据、可借鉴结构、需修改之处、复现方法和误导风险，再选出三个不同的表达方案；回归与分类任务可采用不同图型，不固定三面板结构。

## 2. 核验数据并制作三版候选

用可重运行脚本直接读取已核验文件，检查唯一键、样本数、缺失值、目标与预测的配对、重复或折的边界。回归图重算必要指标并核对残差方向；分类图核对每个混淆矩阵的单元和等于对应样本数，不把不同重复相加后冒充单次结果。若分组绘制，检查每组支持数；异常时停止绘图。

按模板比较结果制作同一证据范围的 A/B/C 三版，分别保留绘图脚本或可编辑源。各版指标、类别顺序、残差定义和坐标语义一致；可因任务差异调整布局。至少进行一轮“生成 → 导出至少 300 DPI 的 PNG → 目视检查 → 修改源文件 → 再导出”，核对拥挤标签、过度绘制、颜色与灰度、异常点和论文宽度下的字形。

在 `candidate_comparison.md` 根据实际 PNG 比较三版的诊断价值、信息密度、尺度公平性和可复现性，给出推荐顺序并交给用户确认。候选阶段只保留各版源文件与 PNG；不得提前保存 SVG/PDF。必要的模板、证据和数据记录照常保留。

## 3. 用户确认后正式导出

用户明确选定最终版本后，仅为该版导出 SVG/PDF，检查矢量对象、字体、裁切、画布一致性和论文版面可读性；若失败，修改源文件并重新导出。未入选版本继续只保留源文件和 PNG。`delivery.md` 记录数据版本或哈希、Evidence ID、重建命令、候选比较、用户确认和最终导出检查。

2024 B 题的[绘图数据](../projects/rehearsal_2024_B/results/verified/figure_data/fig05_prediction_diagnostics.json)、[模板评审](../projects/rehearsal_2024_B/figures/figure5/template_review.md)和[候选比较](../projects/rehearsal_2024_B/figures/figure5/candidate_comparison.md)展示了 Q3 AP 的 OOF 回归诊断及 Q2 分类混淆；对应证据为 E-Q3-OOF-001、E-Q2-CONF-001。该实例的旧候选矢量导出不改变本指南的候选阶段规则。

## 可复用的任务说明

> 从题目、`results/verified/` 和证据登记表确定图 5 的有标签验证范围，核对逐点预测、残差定义或类别顺序。实际比较至少三个相关模板，写入 `figures/figure5/template_review.md`；用同口径数据生成三版可重建候选，只保留源文件与至少 300 DPI 的 PNG。完成实图检查和 `candidate_comparison.md`，把候选交给我确认；确认后才为选定版导出并检查 SVG/PDF。
