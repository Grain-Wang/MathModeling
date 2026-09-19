# 图 6 基线、消融与模型选择比较图：模板比较和精确口径工作流

本指南供正式比赛复用，顺序为**核对比较问题与证据 → 比较模板 → 重算指标和门槛 → 三版同口径候选 → PNG 检查与比较 → 用户确认 → 正式导出**。图 6 按赛题选择基线、消融、特征组贡献、候选模型或验证范围的比较，不固定柱状图、误差棒或面板数量。内容定位见[八图总指南](figures_guide.md)，数据及导出时序遵守[绘图规范](09_plotting_protocol.md)。

## 0. 锁定比较口径

读取题目、交接资料、`results/verified/` 的实验汇总与原始重复记录、模型选择规则及证据登记表。逐项写明指标方向和单位、基线与候选定义、训练或验证范围、折数与重复次数、阈值及 Evidence ID。只比较同一指标和同一验证口径；量纲或统计单位不同的结果分面展示。

若存在精确晋级门槛，用未四舍五入的原值计算增益与是否过门槛，图上显示的短数字不得改变结论。消融差异和置换重要性只说明在该实验设置下的变化，不直接声称因果贡献。嵌套选模管线的整体 OOF 表现不能改写为某个固定配置的独立成绩。

## 1. 搜集并比较模板

### 1.1 适用模板库网址

以下网址只作为模板发现入口，不代表其中任何具体模板已经通过用户验证。

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| Matplotlib Gallery | [https://matplotlib.org/stable/gallery/index.html](https://matplotlib.org/stable/gallery/index.html) | 点图、条形图、误差表示、阈值线和分面比较 | 进入具体示例核对源码与尺度，样式变化不能单独算模板 |
| Python Graph Gallery | [https://python-graph-gallery.com/](https://python-graph-gallery.com/) | 哑铃、棒棒糖、排序条形、分组点图和多面板比较 | 选择有完整代码且能承载相同指标口径的具体示例 |
| forestplot | [https://github.com/LSYS/forestplot](https://github.com/LSYS/forestplot) | 带区间的模型、消融或特征组横向比较 | 只有真实区间数据时才使用区间；均值或范围不得冒充置信区间 |
| Seaborn stripplot | [https://seaborn.pydata.org/generated/seaborn.stripplot.html](https://seaborn.pydata.org/generated/seaborn.stripplot.html) | 展示少量重复、折或实验点及其离散程度 | 需要原始重复记录，避免重叠、抖动和样本量造成误读 |
| Seaborn pointplot | [https://seaborn.pydata.org/generated/seaborn.pointplot.html](https://seaborn.pydata.org/generated/seaborn.pointplot.html) | 分组点估计、基线和区间比较 | 必须明确估计量与区间算法；没有区间数据时关闭推断性区间 |
| figures4papers | [https://github.com/ChenLiu-1996/figures4papers](https://github.com/ChenLiu-1996/figures4papers) | 论文多面板组织、标注层级和结果叙事参考 | 仅作布局参考；具体图型仍须有可运行源码和当前数据支持 |

### 1.2 已验证好用的模板

暂无已确认模板。只有用户明确确认某个具体模板好用后，才能在下表添加记录；代理自行筛选、成功运行或完成试绘均不算用户确认。

| 模板名称 | 具体模板链接或路径 | 适用场景 | 确认记录 |
|---|---|---|---|

### 1.3 模板检索与比较要求

在制作图形前实际查看至少三个相关官方图库示例、科研图模板或有源码的案例，比较点图、区间图、哑铃图、条形图或分面布局如何表达本题的指标方向、基线、重复值及阈值。来源可按图型从 Matplotlib、Seaborn、PGFPlots 或专业绘图工具中选择；样式表不单独算完整模板。确实不足三个时记录检索范围和原因。

在 `projects/<project_name>/figures/figure6/template_review.md` 记录来源、结构适配性、可复现方法、需改造之处、坐标风险和论文可读性，并选出三种有实质结构差异的方案。

## 2. 重算数据并制作三版候选

使用可重运行脚本读取已核验记录，检查候选全集、模型名称、指标方向、重复或折数、缺失值和阈值。重算适用的增益、均值和选择结果，并与结果登记表核对。重复原始点存在时可直接绘制；只有范围时标为范围；只有均值时只绘制均值。没有标准误或置信区间数据时不补造误差棒，不把三次重复范围称作 95% 置信区间，也不添加未执行的显著性检验。

制作 A/B/C 三版，各版采用相同数据、指标和门槛口径，保留独立绘图源。至少进行一轮“生成 → 导出至少 300 DPI 的 PNG → 目视检查 → 修正源文件 → 再导出”；检查轴向、阈值线、关键模型、数值舍入、灰度和论文宽度下的字号。不同量纲的面板可各有坐标轴，不用双轴制造可比性。

在 `candidate_comparison.md` 根据实际 PNG 比较三版对核心选择问题的表达、尺度公平性、拥挤程度和复现成本，给出推荐顺序并交给用户确认。候选阶段仅保留源文件和 PNG；模板、数据与比较记录照常保存。

## 3. 用户确认后正式导出

用户明确选定最终版后，仅为该版导出 SVG/PDF，并检查矢量对象、字体、裁切、PNG 与矢量画布的一致性及论文版面可读性。未入选候选保留源文件和 PNG。`delivery.md` 记录输入版本、Evidence ID、重算命令、门槛判断、用户确认和最终导出检查。

2024 B 题的[绘图数据](../projects/rehearsal_2024_B/results/verified/figure_data/fig06_model_selection.json)、[模板评审](../projects/rehearsal_2024_B/figures/figure6/template_review.md)和[候选比较](../projects/rehearsal_2024_B/figures/figure6/candidate_comparison.md)分别展示 Q1 特征组、Q2 精确晋级门槛与 Q3 验证范围权衡；证据包括 E-Q1-001、E-Q1-IMP-001、E-Q2-001、E-Q3-PIPE-001、E-Q3-TRADE-001。具体模型与数值不是其他赛题的预设；该实例既有的候选矢量文件属于历史交付。

## 可复用的任务说明

> 读取题目、`results/verified/`、模型选择规则和证据登记表，核对图 6 的基线、消融、重复值、指标方向与精确门槛。绘图前比较至少三个相关模板并写入 `figures/figure6/template_review.md`。从同一份已核验数据制作 A/B/C 三版可重建候选，只保留各版源文件和至少 300 DPI 的 PNG；按实际图面完成比较并交给我确认。确认最终版后才为选定版导出 SVG/PDF，不添加没有数据支持的误差棒或显著性。
