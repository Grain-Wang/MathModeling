# 任务：检索图4模板并生成三种候选版本

请为 2024 年 B 题的图 4“Q3 系统吞吐核心验证结果”搜索模板，并基于同一份已核验数据生成三种可比较的候选图。

当前阶段目标：

1. 读取并核验图4数据；
2. 在线查询指定模板库；
3. 筛选三个真正适配的模板；
4. 分别生成三个候选版本；
5. 比较三版优缺点；
6. 暂不覆盖或替代最终正式图。

## 一、必须读取

主要绘图数据：

projects/rehearsal_2024_B/results/verified/figure_data/fig04_q3_core_result.json

绘图指南：

guide/figures_guide.md
guide/09_plotting_protocol.md

项目交接与证据边界：

projects/rehearsal_2024_B/work/handoff/eight_figure_resources.md
projects/rehearsal_2024_B/results/verified/result_registry.md

重点核对：

- E-Q3-OOF-001
- E-Q3-PIPE-001

## 二、必须确认的数据口径

从 JSON 中读取并验证：

- validation_scope = PRIMARY_GROUPED_OOF_REPEAT_0；
- 系统级完整组数 n = 482；
- 每个点包含 truth_mbps 和 prediction_mbps；
- 每个点包含 ap_count、group_id、source_file；
- 横纵轴单位均为 Mbps；
- system MAE 从 JSON 读取，不手工输入；
- 482 个点的 group_id 必须唯一。

图4展示的是：

训练侧第0次 primary grouped OOF 的系统级真值—预测值关系。

不得描述为：

- 官方测试性能；
- 独立测试集性能；
- 唯一一次验证结果；
- 固定 residual-C3 的独立性能。

第0次重复仅用于逐点可视化；整体权威指标仍来自三次重复汇总。

## 三、在线查询的模板源

请实际访问并阅读示例代码，不要只凭名称判断。

### 1. scikit-learn PredictionErrorDisplay

https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html

重点查询：

- actual_vs_predicted
- from_predictions
- scatter_kwargs
- line_kwargs
- prediction error display examples

### 2. Matplotlib Gallery

https://matplotlib.org/stable/gallery/index.html

重点查询：

- scatter plot with legend
- axline
- axis equal
- marker reference
- annotation box
- colorbar and legend design

### 3. Seaborn JointGrid / jointplot

https://seaborn.pydata.org/generated/seaborn.JointGrid.html
https://seaborn.pydata.org/generated/seaborn.jointplot.html

重点查询：

- joint scatter marginal histograms
- JointGrid hue
- marginal distributions
- custom reference line

### 4. PGFPlots

https://pgfplots.sourceforge.net/gallery.html
https://tikz.dev/pgfplots/reference-2dplots

重点查询：

- scatter/classes
- scatter src=explicit symbolic
- only marks
- axis equal image
- identity line
- legend

### 5. SciencePlots

https://github.com/garrettj403/SciencePlots

重点查询：

- science scatter
- no-latex
- ieee
- color-blind-safe styles

SciencePlots仅作为视觉样式层，不单独算一个图形模板。

## 四、筛选三个候选模板

最终选择三个候选，原则上优先尝试：

### 候选A：基础论文散点图

参考：

- scikit-learn PredictionErrorDisplay；
- Matplotlib；
- SciencePlots。

结构：

- 真值—预测值散点；
- y=x参考线；
- 2 AP与3 AP使用不同marker；
- 相同横纵轴范围；
- n与MAE信息框。

### 候选B：联合分布增强图

参考：

- Seaborn JointGrid；
- Matplotlib；
- SciencePlots。

结构：

- 中央真值—预测值散点；
- 顶部真实值边缘分布；
- 右侧预测值边缘分布；
- y=x参考线；
- 2 AP与3 AP分组。

### 候选C：LaTeX论文统一版

参考：

- PGFPlots scatter/classes；
- TikZ/PGFPlots图例与注释。

结构：

- 2 AP和3 AP按scatter class区分；
- y=x参考线；
- 相同横纵轴范围；
- TikZ统计信息框；
- 矢量PDF和SVG。

如果实际检索后发现其中某个模板明显不适配，可以替换，但必须说明替换原因。

## 五、所有候选图的共同要求

横轴：

真实系统吞吐量 / Mbps

纵轴：

预测系统吞吐量 / Mbps

必须：

- 绘制y=x理想预测线；
- 横纵轴使用相同数值范围；
- 保持1:1视觉比例；
- 显示n=482完整组；
- 显示“训练侧 grouped OOF，repeat 0”；
- 显示system MAE，数值从JSON读取；
- 2 AP使用圆形marker；
- 3 AP使用三角形marker；
- 使用半透明点减少遮挡；
- 使用色盲友好、低饱和配色；
- 黑白打印时仍能靠marker形状区分；
- 图例不得遮挡数据；
- PDF和SVG保持矢量。

不得：

- 绘制普通回归拟合线代替y=x；
- 将13个source_file绘制成13种颜色；
- 给482个点逐一标注group_id；
- 使用3D散点图；
- 使用彩虹色；
- 使用点大小编码误差；
- 手工修改或删除异常点；
- 使用官方测试数据；
- 加入因果措辞；
- 把2 AP与3 AP差异解释为AP数量造成的因果效应。

## 六、实现要求

所有候选版本必须直接读取：

projects/rehearsal_2024_B/results/verified/figure_data/fig04_q3_core_result.json

不得手工复制482个点。

Python代码使用现有math_modeling Conda环境。

候选A和B优先使用Python生成。

候选C可先由Python把JSON转换成CSV，再由XeLaTeX和PGFPlots生成。

三个版本应尽量使用：

- 相同画布尺寸；
- 相同横纵轴范围；
- 相同主色语义；
- 相同marker语义；
- 相同信息内容。

保证比较的是模板结构，而不是数据或尺度差异。

## 七、输出目录

将全部文件放在：

projects/rehearsal_2024_B/figures/figure4/

先创建：

template_review.md

其中记录每个候选模板的：

- 来源网站；
- 具体页面或示例名称；
- 参考代码位置；
- 可复用设计；
- 需要修改的地方；
- 优点；
- 局限；
- 是否完全可复现；
- 是否适合论文正文。

生成三个候选版本：

fig04_candidate_A.py
fig04_candidate_A.svg
fig04_candidate_A.pdf
fig04_candidate_A.png

fig04_candidate_B.py
fig04_candidate_B.svg
fig04_candidate_B.pdf
fig04_candidate_B.png

fig04_candidate_C_extract.py
fig04_candidate_C.csv
fig04_candidate_C.tex
fig04_candidate_C.svg
fig04_candidate_C.pdf
fig04_candidate_C.png

同时创建：

candidate_comparison.md

## 八、候选比较

在candidate_comparison.md中比较：

- 是否准确表达真值—预测值关系；
- y=x偏离是否容易判断；
- 2 AP和3 AP是否容易区分；
- 点重叠是否严重；
- 边缘分布是否带来真实信息增益；
- 缩小到论文整页宽度后的可读性；
- 黑白打印效果；
- 矢量输出质量；
- 修改和复现成本；
- 与整篇论文风格的一致性。

给出一个推荐顺序，但不要删除其他候选。

推荐结论必须基于实际生成结果，不得预先指定获胜模板。

## 九、视觉检查

每个候选至少执行一轮：

生成 → 导出PNG → 检查 → 修正。

检查：

1. 482个点是否全部加载；
2. 横纵轴范围是否完全一致；
3. y=x线是否从左下到右上覆盖有效范围；
4. marker与颜色是否一致；
5. 信息框是否遮挡散点；
6. 图例是否遮挡；
7. 坐标轴单位是否准确；
8. 文字是否截断；
9. 边缘直方图是否共享正确范围；
10. PDF、SVG、PNG画布是否一致；
11. 是否错误写成官方测试；
12. 是否错误把repeat 0当作唯一验证结果。

## 十、最终报告

完成后汇报：

- 检索过的模板页面；
- 最终采用的三个候选模板；
- 482个点的数据核验结果；
- 2 AP和3 AP各自的组数；
- JSON中的system MAE；
- 三个候选的主要区别；
- 推荐顺序及理由；
- 生成文件列表；
- 尚需人工确认的问题。

不要只输出模板建议，实际完成三种候选图及对比文档。