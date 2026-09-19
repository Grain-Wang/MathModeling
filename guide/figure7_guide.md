# 图 7 稳健性与不确定性图：已执行检验的可追溯工作流

本指南供正式比赛复用，顺序为**确定检验范围 → 比较模板 → 核验区间与逐来源数据 → 三版候选 → PNG 检查与比较 → 用户确认 → 正式导出**。根据本题已执行的实验选择参数灵敏度、Bootstrap 摘要、留一来源外推或场景鲁棒性；不预设热力图、箱线图和失效阈值。内容定位见[八图总指南](figures_guide.md)，数据及导出时序遵守[绘图规范](09_plotting_protocol.md)。

## 0. 确定真实执行的检验

读取题目、交接资料、`results/verified/` 的稳健性结果、实验设置和证据登记表。写明基准方案、指标方向与单位、重复/抽样单位、区间方法与置信水平、扰动范围或留出来源、完整来源数和 Evidence ID。区分整体 Primary、来源外推 LOSO 或其他验证口径；不能把它们画成同一次实验的重复点。

若只有 Bootstrap 区间摘要，不重建不存在的原始抽样分布或箱线图；若只有来源级点估计，不添加来源级置信区间。没有实际运行的参数扰动，不画灵敏度曲线。结论反转、最坏来源或约束失效位置必须来自结果记录。

## 1. 搜集并比较模板

### 1.1 适用模板库网址

以下网址只作为模板发现入口，不代表其中任何具体模板已经通过用户验证。

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| Matplotlib Gallery | [https://matplotlib.org/stable/gallery/index.html](https://matplotlib.org/stable/gallery/index.html) | 区间、灵敏度曲线、来源排序和分面稳健性图 | 进入具体示例核对源码、区间定义和坐标方向 |
| Matplotlib subplot mosaic | [https://matplotlib.org/stable/users/explain/axes/mosaic.html](https://matplotlib.org/stable/users/explain/axes/mosaic.html) | 将整体区间、来源外推和场景检验组织为不等宽面板 | 只解决版面组织，不能替代具体统计图模板或新增未执行检验 |
| forestplot | [https://github.com/LSYS/forestplot](https://github.com/LSYS/forestplot) | 点估计、区间、基准线和来源排序 | 必须有真实上下界；只有点估计时不得补造置信区间 |
| Python Graph Gallery | [https://python-graph-gallery.com/](https://python-graph-gallery.com/) | 森林图、区间点图、灵敏度曲线和分组比较 | 选择有完整代码并与当前统计量匹配的具体示例 |
| figures4papers | [https://github.com/ChenLiu-1996/figures4papers](https://github.com/ChenLiu-1996/figures4papers) | 多面板论文图、长标签和叙事层级参考 | 仅作布局参考；具体统计结构必须来自可重建模板与已核验结果 |

### 1.2 已验证好用的模板

暂无已确认模板。只有用户明确确认某个具体模板好用后，才能在下表添加记录；代理自行筛选、成功运行或完成试绘均不算用户确认。

| 模板名称 | 具体模板链接或路径 | 适用场景 | 确认记录 |
|---|---|---|---|

### 1.3 模板检索与比较要求

制作图形前实际查看至少三个对应检验类型的官方图库示例、科研图模板或有源码的案例，核对其区间含义、排序、来源标签、基准线和指标方向。可选森林图、区间点图、来源排序图或分面比较；样式表不能单独算完整模板。确实不足三个时记录检索来源、关键词和原因。

在 `projects/<project_name>/figures/figure7/template_review.md` 记录来源、可借鉴结构、适用的数据层级、改造量、误读风险、可复现方法和缩小后的可读性，选出三种表达差异明确的候选方案。

## 2. 核验数据并制作三版候选

用可重运行脚本读取已核验结果，检查区间上下界、点估计、来源全集、指标方向与聚合值；重算可由现有数据重算的摘要，并与登记表核对。来源名称需要缩写时，另存 `source_label_mapping.csv`，保留一一对应关系，图中不遗漏困难来源。原始重复值与区间摘要、整体指标与逐来源点估计分别处理，不把不同统计量拼成伪分布。

制作 A/B/C 三版，各版使用同一验证范围、指标和来源全集，保留独立脚本或可编辑源。至少执行一轮“生成 → 导出至少 300 DPI 的 PNG → 检查 → 修正源文件 → 再导出”；检查区间端点、排序、零线或聚合参考线、难读的长标签、灰度和论文宽度下的可读性。

在 `candidate_comparison.md` 根据实际 PNG 比较三版对不确定性、外推差异和最坏来源的表达，说明过度拥挤或尺度误导，并给出推荐顺序供用户确认。候选阶段仅保留各版源文件与 PNG；模板、数据和比较记录照常保存。

## 3. 用户确认后正式导出

用户明确选定最终版后，仅为该版导出 SVG/PDF，检查矢量对象、字体、裁切、完整来源标签和论文版面可读性；未入选候选继续只保留源文件和 PNG。`delivery.md` 记录数据版本、Evidence ID、验证口径、来源映射、用户确认和正式导出检查。

2024 B 题的[绘图数据](../projects/rehearsal_2024_B/results/verified/figure_data/fig07_robustness_uncertainty.json)、[模板评审](../projects/rehearsal_2024_B/figures/figure7/template_review.md)和[候选比较](../projects/rehearsal_2024_B/figures/figure7/candidate_comparison.md)展示了 Bootstrap 汇总区间、整体 Primary/LOSO 和 13 个留出来源；证据包括 E-Q3-UNC-001、E-Q3-LOSO-001、E-Q3-TRADE-001。该实例不提供所有原始 Bootstrap 抽样，也不代表其他赛题必须绘制相同面板；既有候选矢量导出属于历史交付。

## 可复用的任务说明

> 读取题目、`results/verified/` 和证据登记表，列出图 7 实际执行的扰动、区间估计或来源外推检验及其统计口径。绘图前比较至少三个模板并写入 `figures/figure7/template_review.md`。核验区间、来源全集与指标方向，以同口径数据生成 A/B/C 三版可重建候选，只保留源文件和至少 300 DPI 的 PNG；完成实图比较并交给我确认。确认最终版后才为选定版导出 SVG/PDF，不编造原始分布、来源级区间或未执行的灵敏度试验。
