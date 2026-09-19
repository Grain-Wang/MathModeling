# 图 4 核心结果图：模板比较 → 三版候选 → 最终选版

本指南供正式比赛复用，固定顺序为**确定赛题结果与证据 → 阅读并比较模板 → 核验绘图数据 → 用最适配的三个模板制作同口径候选 → PNG 检查与比较 → 用户确认最终版 → 正式导出**。图 4 可以呈现赛题要求的数值、预测核验、方案、路径、布局、排序或时空结果；具体图型、工具和视觉结构由本题结果决定，不能把某次演练的散点图当作通用模板。内容定位见[八图总指南](figures_guide.md)，数据要求见[绘图规范](09_plotting_protocol.md)。

## 0. 确定要回答的问题与证据边界

读取题目、项目交接资料、`results/verified/` 中的绘图数据和结果登记表。写出读者应从图 4 得到的核心答案、观测粒度、数据/验证范围、单位、关键数值、约束和 Evidence ID。预测类结果必须区分训练侧 OOF、独立验证与官方测试；官方测试没有真值时，不得报告其预测误差。若图展示某一次重复的逐点关系，图注须说明它与多次重复汇总指标的关系。图中的箭头、颜色或分组不得引入未证实的因果解释。若另有图 5 误差诊断，图 4 聚焦主结果，图 5 解释失效区间，避免重复同一图。

**进入下一步的条件：**图的目标和每项数值可回指已核验文件；尚未确定题目输出形式时，先核对题目与建模结果，不先选图型。

## 1. 绘图前阅读并比较模板

### 1.1 适用模板库网址

以下网址只作为模板发现入口，不代表其中任何具体模板已经通过用户验证。

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| Matplotlib Gallery | [https://matplotlib.org/stable/gallery/index.html](https://matplotlib.org/stable/gallery/index.html) | 散点、排序、时序、布局及通用结果图 | 进入具体示例并核对源码、坐标和输入数据，不能只看缩略图 |
| scikit-learn PredictionErrorDisplay | [https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html) | 有标签回归任务的真实值—预测值和残差结果 | 只适用于确有逐点真值与预测值的范围，不能用于无标签官方测试 |
| Seaborn JointGrid | [https://seaborn.pydata.org/generated/seaborn.JointGrid.html](https://seaborn.pydata.org/generated/seaborn.JointGrid.html) | 主关系与边际分布的组合结果 | 需要逐点数据；边际分布不能替代对样本范围和单位的说明 |
| Seaborn jointplot | [https://seaborn.pydata.org/generated/seaborn.jointplot.html](https://seaborn.pydata.org/generated/seaborn.jointplot.html) | 快速比较散点、回归、密度或六边形关系结构 | 仅把具体示例作为结构候选，统计设定须按当前数据重新核验 |
| PGFPlots Gallery | [https://pgfplots.sourceforge.net/gallery.html](https://pgfplots.sourceforge.net/gallery.html) | 适合论文 LaTeX 工作流的二维结果图与多面板布局 | 打开具体示例源码后再计入候选，保留数据驱动和可重建性 |
| PGFPlots 2D Plots Reference | [https://tikz.dev/pgfplots/reference-2dplots](https://tikz.dev/pgfplots/reference-2dplots) | 折线、散点、误差表示和坐标轴控制 | 属于实现参考；只有形成适配当前结果的具体结构时才算候选模板 |

### 1.2 已验证好用的模板

暂无已确认模板。只有用户明确确认某个具体模板好用后，才能在下表添加记录；代理自行筛选、成功运行或完成试绘均不算用户确认。

| 模板名称 | 具体模板链接或路径 | 适用场景 | 确认记录 |
|---|---|---|---|

### 1.3 模板检索与比较要求

围绕本题的结果形式，实际查阅至少三个相关模板、官方图库示例或带源代码的科研图；打开示例代码，核查其数据输入、坐标、图例、标注和导出方式。优先找能准确承载本题答案的模板，不能仅凭外观选图。可从绘图库官方 Gallery、PGFPlots、GIS/专业求解软件示例等检索；scikit-learn、Matplotlib、Seaborn、SciencePlots 是预测图的可选参考，不是所有赛题的固定清单。确实没有三个适用的现成模板时，记录检索过程，并将自行设计的结构作为候选之一。

在创建图形前完成 `projects/<project_name>/figures/figure4/template_review.md`：记录来源链接、具体示例与代码位置、可复用设计、所需改造、局限、数据适配性、复现方法和论文正文适用性。选出最适配的三个不同方案；配色样式只作辅助，不能单独算一个结果模板。

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

> 读取本题题目、交接资料和 `results/verified/`，明确图 4 要呈现的核心结果、数据范围、单位和证据。绘图前实际阅读并比较至少三个适配模板或示例代码，完成 `figures/figure4/template_review.md`。用脚本核验数据，从最适配的三个方案制作同口径候选 A/B/C，逐版导出至少 300 DPI 的 PNG 并目视修正；以实际成图完成 `candidate_comparison.md` 和推荐顺序。候选阶段只保留源文件与 PNG，交给我确认最终版后才为选定版导出并检查 PDF/SVG；图型仍由本题结果决定。
