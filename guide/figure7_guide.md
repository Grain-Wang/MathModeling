# 图 7 稳健性与不确定性图：已执行检验的可追溯工作流

本指南供正式比赛复用，顺序为**确定检验范围 → 比较模板 → 核验区间与逐来源数据 → 三版候选 → PNG 检查与比较 → 用户确认 → 正式导出**。根据本题已执行的实验选择参数灵敏度、Bootstrap 摘要、留一来源外推或场景鲁棒性；不预设热力图、箱线图和失效阈值。内容定位见[八图总指南](figures_guide.md)，数据及导出时序遵守[绘图规范](09_plotting_protocol.md)。

## 0. 确定真实执行的检验

读取题目、交接资料、`results/verified/` 的稳健性结果、实验设置和证据登记表。写明基准方案、指标方向与单位、重复/抽样单位、区间方法与置信水平、扰动范围或留出来源、完整来源数和 Evidence ID。区分整体 Primary、来源外推 LOSO 或其他验证口径；不能把它们画成同一次实验的重复点。

若只有 Bootstrap 区间摘要，不重建不存在的原始抽样分布或箱线图；若只有来源级点估计，不添加来源级置信区间。没有实际运行的参数扰动，不画灵敏度曲线。结论反转、最坏来源或约束失效位置必须来自结果记录。

## 1. 搜集并比较模板

### 1.1 适用模板库网址

以下网址只作为模板发现入口，不代表其中任何具体模板已经通过用户验证。

#### 参数扫描与全局敏感性

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| Matplotlib Gallery | [https://matplotlib.org/stable/gallery/index.html](https://matplotlib.org/stable/gallery/index.html) | 单参数曲线、双参数热力图、等高线、区间带、来源排序和分面稳健性图 | 进入具体示例核对源码、区间定义和坐标方向；插值表面不能超出实际采样范围 |
| SALib | [https://github.com/SALib/SALib](https://github.com/SALib/SALib) | Sobol、Morris、FAST、Delta 等全局敏感性指标及基础可视化 | 只有实际按相应采样设计运行并完成分析时才使用；一因子扫描不能冒充 Sobol 或 Morris 结果 |
| OpenTURNS | [https://github.com/openturns/openturns](https://github.com/openturns/openturns) | 不确定性传播、可靠性、敏感性、响应面和概率分布分析示例 | 功能范围广，先锁定当前实验的统计对象和方法；示例参数、分布和置信水平必须全部替换为本题结果 |
| The Python Graph Gallery | [https://github.com/holtzy/The-Python-Graph-Gallery](https://github.com/holtzy/The-Python-Graph-Gallery) | 灵敏度曲线、热力图、等高线、区间点图和分组场景比较 | 优先选择有完整代码的具体模板；复杂视觉结构不能替代扰动设计和数据覆盖 |

#### 区间、分布与预测不确定性

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| ArviZ | [https://github.com/arviz-devs/arviz](https://github.com/arviz-devs/arviz) | 后验分布、森林图、ridge、HDI、轨迹、后验预测与 Bayesian 模型比较 | 仅在确有后验样本或 Bayesian 结果时使用；可信区间不能改称频率学置信区间，反之亦然 |
| ggdist | [https://github.com/mjskay/ggdist](https://github.com/mjskay/ggdist) | half-eye、区间、分位点、ridge 和分布不确定性 | 需要原始抽样或可追溯分布数据；只有上下界摘要时使用区间图，不重建伪密度 |
| Uncertainty Toolbox | [https://github.com/uncertainty-toolbox/uncertainty-toolbox](https://github.com/uncertainty-toolbox/uncertainty-toolbox) | 回归预测区间、校准、覆盖率、锐度、误差—不确定性和综合诊断 | 用于预测不确定性而非任意参数扰动；必须有真实值和预测均值/尺度或区间，说明校准范围 |
| forestplot | [https://github.com/LSYS/forestplot](https://github.com/LSYS/forestplot) | Bootstrap/重复实验区间、逐来源效果、场景排序和基准线 | 必须有真实上下界；只有点估计时不补区间，标准差、范围、置信区间和可信区间不得混称 |

#### 多场景、来源外推与稳健权衡

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| academic-figure | [https://github.com/SciToolsmith/academic-figure](https://github.com/SciToolsmith/academic-figure) | 不确定性、多面板、来源比较、配对变化和论文图结构检索 | 区分图鉴案例和开放源码模板；只借鉴与当前检验口径相符的结构，先核对源路径和许可证 |
| figures4papers | [https://github.com/ChenLiu-1996/figures4papers](https://github.com/ChenLiu-1996/figures4papers) | 整体区间、来源外推和场景检验的多面板组织与长标签排版 | 仅作布局参考；不能因为模板有箱线图、误差棒或显著性就补造相应统计量 |
| pymoo | [https://github.com/anyoptimization/pymoo](https://github.com/anyoptimization/pymoo) | 鲁棒性—性能—成本等多目标权衡、Pareto 前沿和平行坐标 | 只有确有多个冲突目标和完整方案集时使用；单参数敏感性不能包装成 Pareto 分析 |
| Matplotlib subplot mosaic | [https://matplotlib.org/stable/users/explain/axes/mosaic.html](https://matplotlib.org/stable/users/explain/axes/mosaic.html) | 将整体区间、来源外推、场景检验和局部放大组织为不等宽面板 | 只解决版面组织，不能替代具体统计模板，也不能新增未执行的检验 |

### 1.2 已验证好用的模板

暂无已确认模板。只有用户明确确认某个具体模板好用后，才能在下表添加记录；代理自行筛选、成功运行或完成试绘均不算用户确认。

| 模板名称 | 具体模板链接或路径 | 适用场景 | 确认记录 |
|---|---|---|---|

### 1.3 按已执行检验选择模板类型

制作图形前先按结果记录确认实际执行了哪一种检验：

- **单参数或少量参数扫描：**使用折线、点线、小多图或二维热力图；标出基准参数、实际采样点、可行区和失效位置，不能用平滑插值掩盖稀疏采样。
- **Sobol、Morris、FAST 等全局敏感性：**使用 SALib/OpenTURNS 对应指标图；必须写清采样设计、样本量、阶数和置信区间方法。
- **Bootstrap 或重复实验只有点估计与上下界：**优先 forestplot/区间点图；没有原始重采样值时不画箱线、小提琴或密度。
- **有完整 Bootstrap、后验或模拟样本：**可比较 ggdist、ArviZ 或分布型小多图；区间类型和分布来源必须准确命名。
- **预测区间与校准：**使用 Uncertainty Toolbox；同时报告覆盖率与区间宽度，不能只展示“包住了多数点”的视觉效果。
- **留一来源、跨地区、跨设备或场景外推：**使用来源排序点图、森林图或分面比较；保留完整来源全集和困难来源，不只展示平均值。
- **性能、资源、风险和鲁棒性共同权衡：**只有生成完整多目标方案集时才使用 pymoo 的 Pareto/平行坐标模板。
- **不同验证口径并列：**整体 Primary、LOSO、场景扰动和不确定区间分面呈现，不把它们当作同一组重复值。

以下模板不能使用：与未执行检验对应的 Sobol/箱线/响应面、把置信区间画成概率密度、用来源级点估计补造来源级区间，以及只展示对方法有利的扰动区间。

### 1.4 模板检索与比较要求

制作图形前实际查看至少三个与当前检验类型对应的官方图库示例、科研图模板或有源码案例，核对其区间含义、排序、来源标签、基准线、采样点和指标方向。样式表不能单独算完整模板；确实不足三个时记录检索来源、关键词和原因。

在 `projects/<project_name>/figures/figure7/template_review.md` 记录来源、具体示例/源码路径、版本和许可证、可借鉴结构、所需的数据层级和统计量、改造量、误读风险、可复现方法和缩小后的可读性，选出三种表达差异明确的候选方案。

## 2. 核验数据并制作三版候选

用可重运行脚本读取已核验结果，检查区间上下界、点估计、来源全集、指标方向与聚合值；重算可由现有数据重算的摘要，并与登记表核对。来源名称需要缩写时，另存 `source_label_mapping.csv`，保留一一对应关系，图中不遗漏困难来源。原始重复值与区间摘要、整体指标与逐来源点估计分别处理，不把不同统计量拼成伪分布。

制作 A/B/C 三版，各版使用同一验证范围、指标和来源全集，保留独立脚本或可编辑源。至少执行一轮“生成 → 导出至少 300 DPI 的 PNG → 检查 → 修正源文件 → 再导出”；检查区间端点、排序、零线或聚合参考线、难读的长标签、灰度和论文宽度下的可读性。

在 `candidate_comparison.md` 根据实际 PNG 比较三版对不确定性、外推差异和最坏来源的表达，说明过度拥挤或尺度误导，并给出推荐顺序供用户确认。候选阶段仅保留各版源文件与 PNG；模板、数据和比较记录照常保存。

## 3. 用户确认后正式导出

用户明确选定最终版后，仅为该版导出 SVG/PDF，检查矢量对象、字体、裁切、完整来源标签和论文版面可读性；未入选候选继续只保留源文件和 PNG。`delivery.md` 记录数据版本、Evidence ID、验证口径、来源映射、用户确认和正式导出检查。

2024 B 题的[绘图数据](../projects/rehearsal_2024_B/results/verified/figure_data/fig07_robustness_uncertainty.json)、[模板评审](../projects/rehearsal_2024_B/figures/figure7/template_review.md)和[候选比较](../projects/rehearsal_2024_B/figures/figure7/candidate_comparison.md)展示了 Bootstrap 汇总区间、整体 Primary/LOSO 和 13 个留出来源；证据包括 E-Q3-UNC-001、E-Q3-LOSO-001、E-Q3-TRADE-001。该实例不提供所有原始 Bootstrap 抽样，也不代表其他赛题必须绘制相同面板；既有候选矢量导出属于历史交付。

## 可复用的任务说明

> 读取题目、`results/verified/` 和证据登记表，列出图 7 实际执行的参数扫描、全局敏感性、区间估计、预测不确定性、来源外推或多目标稳健性检验及其统计口径。按真实检验类型从本指南列出的模板库中实际比较至少三个具体示例，写入 `figures/figure7/template_review.md`。核验区间、来源全集、采样点与指标方向，以同口径数据生成 A/B/C 三版可重建候选，只保留源文件和至少 300 DPI 的 PNG；完成实图比较并交给我确认。确认最终版后才为选定版导出 SVG/PDF，不编造原始分布、来源级区间或未执行的灵敏度试验。