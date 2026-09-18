# 任务：检索模板并生成图6的三个候选版本

请为 2024 年 B 题绘制图6：

“三问冻结选择与对照”。

先在线检索指定模板库，从中选出最适合本题的三个模板组合，再基于同一份已核验数据生成三个候选版本并比较。当前阶段不要覆盖最终正式图。

## 一、必须读取

主要绘图数据：

projects/rehearsal_2024_B/results/verified/figure_data/fig06_model_selection.json

绘图规范与证据边界：

guide/figures_guide.md
guide/09_plotting_protocol.md
projects/rehearsal_2024_B/work/handoff/eight_figure_resources.md
projects/rehearsal_2024_B/results/verified/result_registry.md

重点核对：

- E-Q1-001
- E-Q1-IMP-001
- E-Q2-001
- E-Q3-PIPE-001
- E-Q3-TRADE-001

正式图只能读取 results/verified/ 中的已核验数据，不得重新训练模型或重新生成指标。

## 二、图6必须回答的问题

图6由三个概念面板组成：

(a) Q1各特征组在held-out验证中的预测贡献；
(b) Q2候选模型是否达到精确晋级门槛；
(c) Q3三种管线在Primary和LOSO上的性能权衡。

三个问题的指标和量纲不同，必须分面展示，禁止双纵轴。

## 三、数据核验

### Q1

读取5个特征组：

- basic
- desired_rssi
- group_context
- mechanism
- peer_rssi

每组包含：

- permutation_delta_mae；
- ablation_delta_mae；
- repeat 0、1、2；
- 三次重复均值；
- fold_count应为15。

必须区分Permutation与Ablation，两者尺度差异较大，不能放在同一横轴。

只可称为：

- held-out predictive contribution；
- 条件预测贡献。

不得解释为因果效应或变量作用强度。

### Q2

核对：

- baseline Macro-F1 = JSON中的q2_baseline_macro_f1_fixed_17；
- 三个候选模型的Macro-F1；
- 晋级增益门槛 = 0.02；
- weighted HGB真实增益 = 0.019001737503400118；
- 绝对晋级线 = baseline + 0.02。

所有判断使用未四舍五入数值。

必须明确：

weighted HGB未达到晋级门槛。

不得将0.0190四舍五入成0.02后判为通过。

### Q3

比较：

- Q3-B1；
- Q3-M1-HGB-UNIFIED；
- Q3-M1-HGB-APCOUNT。

每个模型包含：

- primary_score；
- loso_score。

必须标注：

S越低越好。

Q3-M1-HGB-UNIFIED的S属于nested pipeline OOF，不得写成固定residual-C3配置的独立成绩。

不得暗示模型差异经过显著性检验。

## 四、在线检索模板库

请实际访问并阅读代码示例。

### 1. Matplotlib Gallery

https://matplotlib.org/stable/gallery/index.html

重点搜索：

- subplot_mosaic
- nested GridSpec
- stem plot
- horizontal lollipop
- errorbar
- hlines scatter
- bar_label
- threshold line

### 2. Python Graph Gallery

https://python-graph-gallery.com/

重点搜索：

- lollipop plot
- horizontal lollipop
- dumbbell chart
- connected dot plot
- Cleveland dot plot
- custom annotations

### 3. forestplot

https://github.com/LSYS/forestplot

重点搜索：

- coefficient plot
- multi-model forest plot
- dot whisker plot
- annotation columns
- zero reference line

不得把三次repeat范围命名为95%置信区间，除非数据文件明确提供了置信区间。

### 4. Seaborn类别图

https://seaborn.pydata.org/generated/seaborn.stripplot.html
https://seaborn.pydata.org/generated/seaborn.pointplot.html

重点搜索：

- stripplot with mean
- categorical raw points
- overlay stripplot pointplot

若使用pointplot，关闭自动置信区间，保留原始三次repeat点。

### 5. figures4papers

https://github.com/ChenLiu-1996/figures4papers

重点读取：

- scientific-figure-making/SKILL.md
- references/common-patterns.md
- references/design-theory.md

仅借鉴多面板布局、字体、配色、留白和导出规范。

### 6. SciencePlots

https://github.com/garrettj403/SciencePlots

重点搜索：

- science
- no-latex
- ieee
- scatter
- color-blind-safe

SciencePlots只作为视觉样式层，不单独算完整模板。

## 五、选择三个候选方案

至少生成以下三个候选；如检索后发现更合理结构，可以替换，但必须说明理由。

### 候选A：点图优先版

(a) Q1：

- 两个对齐小面板；
- Permutation与Ablation分开；
- 显示3个repeat原始点；
- 叠加较大的均值点；
- 绘制ΔMAE=0参考线。

(b) Q2：

- 水平threshold dot plot；
- 显示baseline、三个候选和精确晋级线；
- 特别标出weighted HGB距离门槛约-0.000998。

(c) Q3：

- dumbbell plot；
- 每个模型连接Primary与LOSO两个点；
- 明确标注S越低越好。

### 候选B：Lollipop统一版

(a) Q1：

- 两个横向lollipop子图；
- 均值为主，repeat点作为小点叠加。

(b) Q2：

- lollipop或bullet chart；
- 精确阈值线必须清晰。

(c) Q3：

- connected-dot/dumbbell。

整张图使用统一的“线+点”视觉语言。

### 候选C：论文仪表盘版

(a) Q1：

- stripplot + mean marker；
- Permutation与Ablation独立坐标轴。

(b) Q2：

- 紧凑bullet chart或threshold strip。

(c) Q3：

- Primary/LOSO并列点图或小型dumbbell。

允许使用极浅分区背景，但不得做成商业Dashboard风格。

## 六、推荐版式

优先采用：

上方整行：
(a) Q1特征组预测贡献
内部包含(a1) Permutation与(a2) Ablation。

下方左侧：
(b) Q2晋级门槛。

下方右侧：
(c) Q3 Primary–LOSO权衡。

使用Matplotlib subplot_mosaic或GridSpec实现。

## 七、共同视觉要求

- 白色背景；
- 正式、简洁、低饱和；
- 色盲友好；
- 黑白打印可辨；
- 不使用渐变、重阴影和3D；
- 不使用双纵轴；
- 不用雷达图或饼图；
- 不加未经定义的显著性星号；
- 原始repeat点必须可见；
- 均值点与原始点视觉区分；
- 图例不得遮挡数据；
- 参考零线和阈值线必须清楚；
- 每个panel明确指标单位与“高/低更优”方向。

建议颜色：

- Q1：蓝色系；
- Q2：紫色系，阈值线用橙色；
- Q3 Primary与LOSO使用两种低饱和颜色；
- 冻结模型可用描边、星形或加粗标签强调，不依赖颜色单独表达。

## 八、禁止内容

不得：

- 将Q1解释为因果效应；
- 把Permutation和Ablation放到同一数轴；
- 将Q2增益四舍五入后判为晋级；
- 删除任何Q2候选模型；
- 将Q3指标描述为越高越好；
- 把nested pipeline成绩归于固定C3配置；
- 添加未做的置信区间或显著性检验；
- 使用官方测试结果；
- 重新拟合模型；
- 手工改写JSON中的数值。

## 九、输出目录

全部输出到：

projects/rehearsal_2024_B/figures/figure6/

创建：

template_review.md
candidate_comparison.md

三个候选版本：

fig06_candidate_A.py
fig06_candidate_A.svg
fig06_candidate_A.pdf
fig06_candidate_A.png

fig06_candidate_B.py
fig06_candidate_B.svg
fig06_candidate_B.pdf
fig06_candidate_B.png

fig06_candidate_C.py
fig06_candidate_C.svg
fig06_candidate_C.pdf
fig06_candidate_C.png

PDF和SVG必须保持矢量，PNG至少300 DPI。

## 十、模板审查

在template_review.md中记录：

- 实际访问的模板页面；
- 示例名称和源码地址；
- 可复用结构；
- 与本题不匹配的部分；
- 最终选出的三个模板组合；
- 每个候选的布局草图；
- 可复现性和黑白打印适配性。

## 十一、候选比较

在candidate_comparison.md中比较：

- Q1原始repeat与均值是否清晰；
- 两种Q1指标是否避免跨尺度误读；
- Q2门槛是否能精确判断；
- weighted HGB未晋级是否表达准确；
- Q3 Primary与LOSO权衡是否清晰；
- “S越低越好”是否醒目；
- 缩小到论文整页宽度后的可读性；
- 黑白打印效果；
- 与图2、图4、图5风格的一致性；
- 修改和复现成本。

基于实际生成结果给出推荐顺序，但保留三个候选。

## 十二、视觉检查

每个候选至少执行一轮：

生成 → 导出PNG → 检查 → 修正。

检查：

1. JSON数值是否全部准确；
2. Q1特征组顺序是否一致；
3. 三次repeat点是否完整；
4. ΔMAE零线是否清楚；
5. Q2精确门槛是否正确；
6. weighted增益是否未被错误判定为通过；
7. Q3模型与两种score是否正确；
8. S越低越好是否明确；
9. 文本、图例和数值是否重叠；
10. PDF、SVG和PNG画布是否一致；
11. 是否出现因果或显著性误导；
12. 是否错误使用官方测试数据。

## 十三、最终汇报

完成后汇报：

- 检索过的模板页面；
- 选出的三个模板组合；
- Q1五个特征组的核验结果；
- Q2基线、候选、增益与精确门槛；
- Q3三个模型的Primary和LOSO值；
- 三个候选的主要区别；
- 推荐顺序及理由；
- 输出文件列表；
- 仍需人工确认的问题。

不要只给模板建议，实际生成三个候选图并完成比较。