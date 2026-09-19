# 图 2 数据结构与关键分布图组：可复用绘图工作流

本指南供正式比赛复用。固定顺序为 **确定问题与证据 → 比较图表示例 → 核验并提取绘图数据 → 选择图型与工具 → 生成 PNG 候选 → 至少两轮视觉检查 → 用户确认 → 正式导出与交付记录**。图 2 可为一张图或不超过三个概念子图；具体变量、图型、布局、分箱和配色均由本题数据决定。内容边界见 [八图总指南](figures_guide.md)，数据来源和工具选择遵守 [绘图规范](09_plotting_protocol.md)。

## 0. 确定问题、数据范围和工具

1. 读取题目、项目交接说明、`results/verified/` 绘图数据及结果登记表。写清图 2 要让读者理解的样本结构、目标分布或类别不平衡，以及每个结论的证据文件或 Evidence ID。
2. 核对训练、验证或测试范围和标签是否存在；分清行、组、时间窗等观测粒度。数据处理前后对比单独用可追溯对照表呈现：按实际处理步骤列出问题与处理依据、处理前后样本/组数及关键质量指标，并说明保留、修复或隔离数量；不适用的指标不强行填写。只有图能进一步揭示缺失模式、异常规则重叠、样本流向或关键分布变化等独立信息时，才在图 2 的三个主题限额内纳入前后对照图；数量和质量指标对照仍以表格为主。
3. 绘图前记录本次工具和理由。优先采用“Python 核验/提取 → LaTeX/PGFPlots 绘制 → `latexmk` 调用 XeLaTeX”；赛题或用户指定其他方案时，可用 Python/Matplotlib、R、MATLAB 等脚本直接绘图，但须达到同样的数据、可重建和导出门槛。有适用 skill 时按绘图规范选用；用户已明确指定工具时无需重复确认。

**进入下一步的条件：**变量、单位、样本范围、观测粒度和证据可逐项核对；不清楚时先查数据与建模记录，不靠图形猜测。

## 1. 绘图前比较至少两个相关示例

### 1.1 适用模板库网址

以下网址只作为模板发现入口，不代表其中任何具体模板已经通过用户验证。

#### 综合科研图来源

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| academic-figure | [https://github.com/SciToolsmith/academic-figure](https://github.com/SciToolsmith/academic-figure) | 多面板、处理前后、配对比较、不确定性和分布变化 | 区分可检索图鉴案例与确有开放源码的模板，先核对开放状态及源路径 |
| cnsplots | [https://github.com/faridrashidi/cnsplots](https://github.com/faridrashidi/cnsplots) | Violin、ridge、slope、heatmap、UpSet 和 multipanel | raincloud 只在找到对应可运行源码时采用，不按名称推断已有实现 |
| The Python Graph Gallery | [https://github.com/holtzy/The-Python-Graph-Gallery](https://github.com/holtzy/The-Python-Graph-Gallery) | Python 数据分布、分组比较及多面板示例 | 优先查看 `src/notebooks/` 下可修改的 Notebook，并核对输入数据与依赖 |
| R Graph Gallery | [https://github.com/holtzy/R-graph-gallery](https://github.com/holtzy/R-graph-gallery) | R 数据分布、质量比较和组合图示例 | 只在 Python 来源没有合适结构时使用；迁移时重新核验统计计算与轴语义 |
| RAWGraphs Charts | [https://github.com/rawgraphs/rawgraphs-charts](https://github.com/rawgraphs/rawgraphs-charts) | 样本流向、高维结构、Alluvial、Sankey、Parallel Coordinates 和 Ridgeline | 只有数据结构确有需要时使用，并核对具体 chart 源码及输入格式 |

#### 数据质量与分布专用来源

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| missingno | [https://github.com/ResidentMario/missingno](https://github.com/ResidentMario/missingno) | 缺失矩阵、完整率柱状图、缺失相关热力图和缺失模式树状图 | heatmap 表达缺失指示之间的相关性，不是变量值相关性 |
| UpSetPlot | [https://github.com/jnothman/UpSetPlot](https://github.com/jnothman/UpSetPlot) | 多字段共同缺失、异常规则重叠或删除原因组合 | 需要逐行集合归属，不能从边际计数臆造交集 |
| PyComplexHeatmap | [https://github.com/DingWB/PyComplexHeatmap](https://github.com/DingWB/PyComplexHeatmap) | 多指标质量热力图、聚类树和多层注释 | 先确认指标方向、样本顺序和注释数据 |
| ggdist | [https://github.com/mjskay/ggdist](https://github.com/mjskay/ggdist) | R 端 raincloud、half-eye、区间及分布不确定性 | 密度形状需要相应的逐点或抽样数据 |
| ggalluvial | [https://github.com/corybrunson/ggalluvial](https://github.com/corybrunson/ggalluvial) | 原始数据到保留、修复、插值、去重或删除的样本流向 | 需要可追溯阶段归属及流量守恒 |
| joypy | [https://github.com/leotac/joypy](https://github.com/leotac/joypy) | 多组、多阶段或多时点的 ridgeline 分布 | 标注组别和各组样本数，避免密度面积造成规模误读 |
| sweetviz | [https://github.com/fbdesignpro/sweetviz](https://github.com/fbdesignpro/sweetviz) | 内部探索和定位值得进一步核验的变量 | 不直接截取自动报告作为论文最终图 |

### 1.2 已验证好用的模板

暂无已确认模板。只有用户明确确认某个具体模板好用后，才能在下表添加记录；代理自行筛选、成功运行或完成试绘均不算用户确认。

| 模板名称 | 具体模板链接或路径 | 适用场景 | 确认记录 |
|---|---|---|---|

### 1.3 模板检索与比较要求

先根据本题的观测粒度与证据缺口确定检索方向，再选与当前统计任务直接相关的仓库；不要求逐一使用上述来源，也不一次性克隆全部仓库。实际查看至少两个相关示例或官方技术文档，核对示例源码而不只看预览。PGFPlots 可继续参考其 Gallery 与官方手册。

必要时使用以下搜索词，并按题目字段补充限定词：

- before after data cleaning matplotlib
- missing data matrix upset plot
- raincloud plot python
- data quality heatmap python
- preprocessing alluvial diagram
- before after distribution comparison
- data cleaning multipanel figure
- outlier treatment visualization

在 projects/<project_name>/figures/figure2/reference_review.md 中，逐个记录实际比较的示例页面和源码路径、所查看的版本、许可证、运行依赖、所需字段与数据粒度、可借鉴的布局或代码、改造量、适配性及采用或放弃的理由。仅在选中示例确需本机运行时获取该示例源码或 Notebook；许可证或依赖不明时先核实，不把截图充当可重建模板。比较完成后才确定本题图型与布局；只借鉴表达技法，不复制无关数据、固定配色或未经核验的结论。没有合适示例时，记录检索过程和自行设计的理由。

## 2. 脚本核验与生成绘图输入

编写可重运行的提取脚本，直接读取已核验数据；先检查字段含义、单位、样本数、唯一键、分组完整性、固定类别顺序及频数合计。如有跨粒度汇总，核对每组成员与汇总值。字段、单位或数量不符时停止绘图并报告；缺失、零值、离群值与极端值不得静默删除。

先计算唯一值数量、范围、分位数、偏度、零值和类别支持数，再决定图型。连续变量可用直方图或 ECDF；少量离散取值用频数图；类别较多时优先考虑可读的横向条形图，并保留有证据支持的固定顺序。直方图优先以 Freedman–Diaconis 规则估计分箱，再按样本量和最终版面检查是否需要调整；记录最终边界与数量，不将 KDE 作为唯一分布表示。

脚本输出可供绘图后端读取的 CSV/数据表、必要的 LaTeX 数据宏及统计摘要，保存在 `figure2/data/`。TeX 或绘图脚本不得手抄逐行数据；数据变化时重跑提取和绘图。不同单位或观测粒度分别标注，若共用坐标轴会误导读者，应使用独立轴或分面；不直接比较不同样本基数的频数。

## 3. 绘制与双轮验收

PGFPlots 路径使用 `standalone`、XeLaTeX、`ctex`、TikZ/PGFPlots；按需使用 `groupplots` 和统计库。本机选用可用中文字体，不复制字体文件。其他脚本后端同样保留可编辑源代码。颜色只辅助区分语义，关键组另用文字、线型或纹理识别；不使用双 Y 轴或无说明的坐标裁切。

至少执行两轮“编译或运行 → 导出 PNG → 查看 → 修正 → 再导出检查”。逐项检查中文和类别标签、数值标注、坐标及单位、样本数、图例、长尾和零值、跨粒度说明、缩至论文尺寸后的字号（约 7.5 pt 以上），并检查灰度版本。不得把训练分布写成模型性能、官方无标签测试误差或因果发现。

用户确认最终版本前，在单图目录仅保留绘图源、数据和至少 300 DPI 的 PNG；若 PGFPlots 编译必须先产生 PDF 才能转成 PNG，将该中间文件放在临时构建目录，转换后不留在单图目录。将候选 PNG 交给用户确认后，才为选定版本导出 PDF/SVG。检查矢量性、字体、长标签和裁切，并处理编译警告；整体栅格化时修正源文件后重新导出。未通过正式导出检查的图不能标为最终图。

## 4. 交付目录与记录

图 2 的正式文件统一放在 `projects/<project_name>/figures/figure2/`，例如：

~~~text
figure2/
├── reference_review.md       # 两个以上示例的源码、许可、依赖与适配性比较
├── <stem>_extract.py          # 数据核验和提取脚本，语言可按工具调整
├── data/                      # 脚本生成的 CSV/宏、统计摘要及必要日志
├── <stem>.tex                 # PGFPlots 源；换用其他后端则保存相应脚本
├── <stem>.png                 # 候选阶段至少 300 DPI 的检查图
├── <stem>.pdf                 # 用户确认后仅为最终版生成
├── <stem>.svg                 # 用户确认后仅为最终版生成
├── <stem>_caption.md          # 数据范围、观察粒度和证据编号
└── <stem>_delivery.md         # 重建命令、哈希和两轮检查记录
~~~

交付记录写明：数据文件与 SHA-256、字段和单位、样本/组数、类别频数合计、分箱及轴尺度理由、所用工具、参考示例取舍、两轮视觉修改、用户最终版确认、编译警告、正式导出后的矢量/分辨率检查及未解决问题。图注须说清数据范围、图的主要发现和 Evidence ID；若展示分层差异，只作描述性解释。

演练项目中的实例可用于核对流程；其中的题目字段、样本数和配色不作为其他赛题的预设。

## 可复用的任务说明

> 读取本题题目、交接说明、results/verified/ 和证据登记表，确定图 2 要表达的数据结构与关键分布。按本指南的任务—来源映射，只检索当前统计问题相关的示例；比较至少两个具体示例的页面、源码、许可证、依赖及数据要求，写入 figures/figure2/reference_review.md，不批量克隆仓库。用脚本核验字段、单位、样本与分组，生成可重建的绘图输入；按数据选图型，优先用 PGFPlots，或说明采用的其他脚本后端。至少进行两轮 PNG 视觉检查；候选阶段只保留源代码、数据摘要、PNG、图注和交付记录，交给我确认最终版本后再为选定版导出并检查 PDF/SVG。数据质量与处理前后指标对比另用可追溯表格呈现；只有图能回答独立问题时才补充可视化。
