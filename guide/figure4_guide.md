# 图 4 核心结果图：模板比较 → 三版候选 → 最终选版

本指南供正式比赛复用，固定顺序为**确定赛题结果与证据 → 阅读并比较模板 → 核验绘图数据 → 用最适配的三个模板制作同口径候选 → PNG 检查与比较 → 用户确认最终版 → 正式导出**。图 4 可以呈现赛题要求的数值、预测核验、方案、路径、布局、排序或时空结果；具体图型、工具和视觉结构由本题结果决定，不能把某次演练的散点图当作通用模板。内容定位见[八图总指南](figures_guide.md)，数据要求见[绘图规范](09_plotting_protocol.md)。

## 0. 确定要回答的问题与证据边界

读取题目、项目交接资料、`results/verified/` 中的绘图数据和结果登记表。写出读者应从图 4 得到的核心答案、观测粒度、数据/验证范围、单位、关键数值、约束和 Evidence ID。预测类结果必须区分训练侧 OOF、独立验证与官方测试；官方测试没有真值时，不得报告其预测误差。若图展示某一次重复的逐点关系，图注须说明它与多次重复汇总指标的关系。图中的箭头、颜色或分组不得引入未证实的因果解释。若另有图 5 误差诊断，图 4 聚焦主结果，图 5 解释失效区间，避免重复同一图。

**进入下一步的条件：**图的目标和每项数值可回指已核验文件；尚未确定题目输出形式时，先核对题目与建模结果，不先选图型。

## 1. 绘图前阅读并比较模板

### 1.1 适用模板库网址

以下网址只作为模板发现入口，不代表其中任何具体模板已经通过用户验证。

#### 数值关系、排序与时间结果

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| Matplotlib Gallery | [https://matplotlib.org/stable/gallery/index.html](https://matplotlib.org/stable/gallery/index.html) | 散点、折线、排序点图、甘特式区间、矩阵及通用结果图 | 进入具体示例并核对源码、坐标和输入数据，不能只看缩略图 |
| scikit-learn PredictionErrorDisplay | [https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html) | 有标签回归任务的真实值—预测值主结果 | 只适用于确有逐点真值与预测值的范围；详细残差结构留给图 5，无标签官方测试不得使用 |
| Seaborn JointGrid / jointplot | [JointGrid](https://seaborn.pydata.org/generated/seaborn.JointGrid.html)、[jointplot](https://seaborn.pydata.org/generated/seaborn.jointplot.html) | 主关系与边际分布的组合结果、六边形密度和分组散点 | 需要逐点数据；边际分布不能替代对样本范围、单位、重复和验证范围的说明 |
| The Python Graph Gallery | [https://github.com/holtzy/The-Python-Graph-Gallery](https://github.com/holtzy/The-Python-Graph-Gallery) | 排名、棒棒糖、哑铃、斜率图、时间序列、小多图和复杂组合结果 | 优先查看有完整 Notebook/源码的具体案例，按当前指标方向和数据粒度重建 |
| PGFPlots Gallery 与 2D Reference | [Gallery](https://pgfplots.sourceforge.net/gallery.html)、[2D Reference](https://tikz.dev/pgfplots/reference-2dplots) | 适合论文 LaTeX 工作流的二维结果、多面板、误差表示和精确坐标控制 | 打开具体示例源码后再计入候选；手册只作实现参考，不能替代数据核验 |

#### 多目标优化与方案权衡

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| pymoo | [https://github.com/anyoptimization/pymoo](https://github.com/anyoptimization/pymoo) | Pareto 前沿、二维/三维散点、平行坐标、Radviz、热力图和多目标决策 | 只在本题确有多个冲突目标和可行解集时使用；标明目标方向、约束、非支配关系和最终推荐解 |
| mooplot | [https://github.com/multi-objective/mooplot](https://github.com/multi-objective/mooplot) | Pareto 前沿、经验达成函数及随机多目标算法结果比较 | 适合有多次随机优化结果的场景；单次最优点不能冒充解集分布或经验达成概率 |

#### 调度、网络与路径结果

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| Plotly.py | [https://github.com/plotly/plotly.py](https://github.com/plotly/plotly.py) | 时间线/Gantt、Sankey、平行坐标、地图和交互式结果原型 | 可用来探索布局；最终论文静态图须固定视角、字体和导出尺寸，不能依赖悬停信息 |
| NetworkX examples | [https://github.com/networkx/networkx](https://github.com/networkx/networkx) | 网络拓扑、流量、中心性、最短路、匹配和节点—边结果 | 节点、边、方向、权重和布局必须来自模型或数据；大网络应筛选主结构并保留图例 |
| OSMnx examples | [https://github.com/gboeing/osmnx-examples](https://github.com/gboeing/osmnx-examples) | 真实道路网络、最短/最快路线、等时圈和城市网络结果 | 仅在有可靠坐标、道路数据和路线计算时使用；保留底图来源、坐标系、网络类型与成本定义 |

#### 空间分布、选址与区域结果

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| GeoPandas | [https://github.com/geopandas/geopandas](https://github.com/geopandas/geopandas) | 分级设色、点线面叠加、空间连接、缓冲区和区域结果图 | 先核对坐标系、空间粒度、分类方法和缺失区域；行政区颜色不能暗示未计算的连续精度 |
| MapAction QGIS Templates | [https://github.com/mapaction/maptemplates-qgis](https://github.com/mapaction/maptemplates-qgis) | 专题地图版式、图例、比例尺、数据来源区和标准化输出 | `.qpt` 只提供版式；真实选址、路线、覆盖和风险层必须由 GIS/Python 根据已核验数据生成，并分别核对底图许可 |

### 1.2 已验证好用的模板

暂无已确认模板。只有用户明确确认某个具体模板好用后，才能在下表添加记录；代理自行筛选、成功运行或完成试绘均不算用户确认。

| 模板名称 | 具体模板链接或路径 | 适用场景 | 确认记录 |
|---|---|---|---|

### 1.3 按核心结果类型选择模板

围绕题目要求的最终输出先判定结果类型，再进入对应模板库：

- **有标签预测的主关系：**可比较 PredictionErrorDisplay、JointGrid 或普通散点/折线；图 4只呈现核心答案，系统残差、混淆和校准留给图 5。
- **排序、评分或方案相对变化：**优先排序点图、棒棒糖、哑铃或斜率图；类别很多时避免拥挤柱状图和雷达图。
- **多目标优化：**优先 pymoo/mooplot 的 Pareto、平行坐标或经验达成结构；必须显示推荐解为何从可行解集中被选出。
- **调度与资源配置：**优先 Gantt/时间线、设备—时间矩阵或资源热力图；条带宽度、起止时间和冲突必须由求解结果直接生成。
- **网络、流量或拓扑方案：**优先 NetworkX；需要真实道路时使用 OSMnx，不能用示意直线冒充地理路径。
- **空间分布、选址、覆盖或区域风险：**优先 GeoPandas/QGIS 模板；保留坐标系、底图来源、比例尺、时间范围和分类口径。
- **高维方案权衡：**可使用平行坐标或小多图，但须提供明确归一化方法，不能用面积或颜色制造不存在的优劣。

图 4 的模板必须让评委直接读出赛题答案。算法收敛曲线、训练损失和误差诊断不能替代核心结果；若某种模板无法承载关键数值、约束或推荐解，应放弃而不是靠图注补救。

### 1.4 模板检索与比较要求

实际查阅至少三个与当前结果类型相关的模板、官方图库示例或带源代码的科研图；打开示例代码，核查其数据输入、坐标、图例、标注和导出方式。优先找能准确承载本题答案的模板，不能仅凭外观选图。确实没有三个适用的现成模板时，记录检索过程，并将自行设计的结构作为候选之一。

在创建图形前完成 `projects/<project_name>/figures/figure4/template_review.md`：记录来源链接、具体示例与代码位置、版本和许可证、可复用设计、所需改造、错误语义风险、数据适配性、复现方法和论文正文适用性。选出最适配的三个不同方案；配色样式只作辅助，不能单独算一个结果模板。

## 2. 核验数据并制作三版候选

用可重运行的脚本直接读取已核验数据；按本题数据类型检查字段、单位、样本或完整组数、唯一键、范围、缺失值和汇总指标。需要由行聚合为组、由预测生成指标或从 JSON 转换 CSV 时，脚本重算并核对结果，异常时停止绘图，不静默筛除离群点或手抄数据。记录输入文件版本或 SHA-256。

按模板比较结果分别生成候选 A、B、C，每版保留绘图源代码或可编辑源。三版使用同一份已核验数据和相同的结果口径；凡直接比较的数值、分组、单位与基准必须一致，适用时采用相同轴范围、画布和视觉语义。不同图型可使用各自合理的布局与坐标，但不能通过裁轴、换指标或遗漏样本制造表面优势。折线、散点、甘特、地图、网络或其他形式都由赛题决定；不预设 A/B/C 各是什么图。

## 3. 逐版 PNG 检查和比较

每个候选至少执行一轮“生成 → 导出 PNG → 目视检查 → 对象或脚本级修正 → 重新导出”。逐项核对数据量、关键数值、单位、图例、坐标和必要基准，检查遮挡、文字截断、颜色与黑白打印、论文最终宽度下的可读性。若有共同坐标或画布，程序检查其一致性；候选 PNG 至少 300 DPI。用户确认前不生成或保留候选 PDF/SVG。若生成 PNG 必须经过其他格式，将中间文件放在临时构建目录；遇到自动裁边或字体故障时修正源文件并重新检查。

在 `candidate_comparison.md` 根据**实际生成的 PNG**比较三版对核心问题的表达、信息增益、尺度公平性、缩小后可读性、灰度效果、编辑/复现成本和全文风格，并给出推荐顺序。保留全部候选及其源文件，将推荐与 PNG 交给用户；只有用户明确确认后才标记最终版。矢量质量在正式导出后检查。

## 4. 交付与实例

所有材料放在 `projects/<project_name>/figures/figure4/`：候选阶段至少包含 `template_review.md`、`candidate_comparison.md`、三版各自的生成脚本或可编辑源与 PNG、必要的数据提取脚本及中间数据。用户确认后仅为选定版导出 PDF/SVG，核查矢量性、字体、裁切和论文宽度；`delivery.md` 记录输入数据、Evidence ID、重建命令、三版检查、用户确认、最终导出检查与尚存限制。不得覆盖其他候选。

2024 B 题的[模板评审](../projects/rehearsal_2024_B/figures/figure4/template_review.md)和[三版实图比较](../projects/rehearsal_2024_B/figures/figure4/candidate_comparison.md)展示了这一流程：三版都从同一份训练侧 OOF 数据生成，比较后推荐正文版本。其散点图、模型名称、样本数、坐标范围、配色和工具组合仅属于该题实例；其他赛题重新按结果选择模板。

## 可复用的任务说明

> 读取本题题目、交接资料和 `results/verified/`，明确图 4 要呈现的核心结果、数据范围、单位和证据。先按结果类型从本指南列出的数值关系、多目标优化、调度网络或空间模板库中实际打开至少三个具体示例，完成 `figures/figure4/template_review.md`。用脚本核验数据，从最适配的三个方案制作同口径候选 A/B/C，逐版导出至少 300 DPI 的 PNG 并目视修正；以实际成图完成 `candidate_comparison.md` 和推荐顺序。候选阶段只保留源文件与 PNG，交给我确认最终版后才为选定版导出并检查 PDF/SVG；图型仍由本题结果决定。