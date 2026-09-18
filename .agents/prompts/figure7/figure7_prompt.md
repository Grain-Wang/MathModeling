# 任务：检索模板并生成图7的三个候选版本

请为2024年B题绘制图7：

“Q3不确定性与来源外推边界”。

先在线检索指定模板库，从中选择最适合的三个模板组合，再基于同一份已核验数据生成三个候选版本并比较。不要覆盖最终正式图。

## 一、必须读取

主要数据：

projects/rehearsal_2024_B/results/verified/figure_data/fig07_robustness_uncertainty.json

规范和证据：

guide/figures_guide.md
guide/09_plotting_protocol.md
projects/rehearsal_2024_B/work/handoff/eight_figure_resources.md
projects/rehearsal_2024_B/results/verified/result_registry.md

重点核对：

- E-Q3-UNC-001
- E-Q3-LOSO-001
- E-Q3-TRADE-001

只能读取results/verified/中的已核验结果，不重新训练、预测、选参或计算官方测试性能。

## 二、数据核验

从JSON验证：

- unified_primary_score约为0.5503296083；
- unified_loso_score约为0.7299206147；
- apcount_loso_score约为0.6854962538；
- Bootstrap重复次数为1000；
- Bootstrap置信水平为0.95；
- Primary S区间约为[0.5090197, 0.6076595]；
- Primary S中位数约为0.5505282；
- System ARE90区间约为[0.1725020, 0.2064804]；
- System ARE90中位数约为0.1884475；
- unified_loso_by_source必须包含13个来源；
- 最差来源必须是training_set_3ap_loc33_nav82.csv；
- 最差来源S约为2.159764。

若数量、字段或证据不一致，停止绘图并报告。

## 三、证据边界

必须明确：

- Bootstrap是固定OOF结果的完整组重采样；
- 不包含重新训练或重新选择超参数；
- LOSO用于描述来源外推差异；
- 不能声称每个来源都稳健；
- S越低越好；
- AP-count与Unified比较是受控比较，不是独立确认性检验。

JSON只有Bootstrap区间摘要，没有1000个原始replicate。

禁止自行模拟replicate、绘制伪Bootstrap直方图、KDE或小提琴图。

## 四、在线检索模板库

### 1. Matplotlib

https://matplotlib.org/stable/gallery/index.html
https://matplotlib.org/stable/users/explain/axes/mosaic.html

搜索：

- subplot_mosaic
- nested GridSpec
- horizontal errorbar
- hlines scatter
- barh
- axvline
- annotation box

### 2. forestplot

https://github.com/LSYS/forestplot

搜索：

- forestplot confidence interval
- dot whisker plot
- annotation columns
- estimate lower upper

### 3. Python Graph Gallery

https://python-graph-gallery.com/

搜索：

- horizontal lollipop
- highlight a group in lollipop
- sorted lollipop
- Cleveland dot plot

### 4. figures4papers

https://github.com/ChenLiu-1996/figures4papers

重点读取：

- scientific-figure-making/SKILL.md
- references/common-patterns.md
- references/design-theory.md
- references/api.md

### 5. SciencePlots

https://github.com/garrettj403/SciencePlots

仅作为样式层，搜索：

- science
- no-latex
- ieee
- muted
- color-blind-safe

## 五、图中必须包含的内容

### Panel A：Bootstrap不确定区间

分别展示：

- Primary selection score S；
- System ARE90。

优先使用两个对齐的小坐标轴，避免把不同含义的指标放进双轴图。

每个小图：

- 横轴从0开始；
- 显示lower、median、upper；
- 使用点+水平区间；
- 标注95% group-bootstrap interval；
- 标注n_boot=1000；
- 标注fixed OOF group resampling。

### Panel B：整体范围对照

展示：

- Unified Primary S；
- Unified LOSO S；
- AP-count LOSO S。

使用水平dot plot、lollipop或bullet-style point plot。

必须：

- 从0起始；
- 明确S越低越好；
- 明确Primary和LOSO是不同验证范围；
- 不添加不存在的区间或显著性标记。

### Panel C：13个来源LOSO

使用排序后的水平lollipop、Cleveland dot plot或barh。

必须：

- 展示全部13个来源；
- 横轴从0开始；
- 完整包含最差S=2.159764；
- 不使用断轴或对数轴；
- 最差来源使用特殊颜色、描边或较大marker；
- 标出Unified aggregate LOSO参考线；
- 可标出Unified Primary参考线；
- 2AP与3AP使用不同marker；
- 不为13个来源使用13种颜色。

如缩写文件名，输出完整名称映射。

## 六、生成三个候选版本

### 候选A：Forest + Lollipop标准版

- Panel A：forest-style interval plot；
- Panel B：三点水平dot plot；
- Panel C：排序lollipop并突出最差来源；
- 使用Matplotlib subplot_mosaic组织版式。

### 候选B：来源外推突出版

- 右侧或下方使用大面积Panel C；
- 左上为Bootstrap区间；
- 左下为Primary/LOSO/AP-count总体对照；
- 强调最差来源和来源间离散性。

### 候选C：统一点线语法版

- 所有panel统一使用点、线段和参考线；
- Bootstrap用dot-whisker；
- 总体对照用lollipop；
- 来源结果用point-forest样式；
- 可参考forestplot的注释列设计。

如在线检索后发现更合理的第三种结构，可以替换，但必须记录理由。

## 七、共同视觉要求

- 正式论文风格；
- 白色背景；
- 低饱和、色盲友好；
- 黑白打印可辨；
- 无渐变、重阴影和3D；
- 所有直接比较坐标从0开始；
- 最差来源不得裁掉；
- 不使用双纵轴；
- 不使用雷达图；
- 不添加显著性星号；
- 不把Bootstrap区间称为完整训练不确定性；
- 不使用官方测试数据。

建议：

- Unified使用蓝色；
- AP-count使用紫色；
- 最差来源使用橙色；
- 其他来源使用中性蓝灰；
- 2AP圆形，3AP三角形；
- 聚合参考线使用不同虚线样式。

## 八、输出目录

输出到：

projects/rehearsal_2024_B/figures/figure7/

创建：

template_review.md
candidate_comparison.md
source_label_mapping.csv

三个候选：

fig07_candidate_A.py
fig07_candidate_A.svg
fig07_candidate_A.pdf
fig07_candidate_A.png

fig07_candidate_B.py
fig07_candidate_B.svg
fig07_candidate_B.pdf
fig07_candidate_B.png

fig07_candidate_C.py
fig07_candidate_C.svg
fig07_candidate_C.pdf
fig07_candidate_C.png

PDF和SVG保持矢量；PNG至少300 DPI。

## 九、模板审查

在template_review.md记录：

- 实际访问的模板页面；
- 示例名称和源码位置；
- 可复用结构；
- 不适配本题的部分；
- 三个候选的组合来源；
- 版式草图；
- 可复现性；
- 黑白打印适配性。

## 十、候选比较

在candidate_comparison.md比较：

- Bootstrap区间是否准确；
- 两种Bootstrap指标是否避免混淆；
- Primary与LOSO差异是否清楚；
- 13个来源是否全部可读；
- 最差来源是否明显且未裁切；
- aggregate LOSO参考线是否有帮助；
- 缩小到论文整页宽度后的可读性；
- 黑白打印效果；
- 与图4、图5、图6的视觉一致性；
- 修改和复现成本。

基于实际结果给出推荐顺序，但保留三个候选。

## 十一、视觉检查

每个候选至少执行一轮：

生成→导出PNG→检查→修正。

检查：

1. 所有JSON数值是否准确；
2. Bootstrap上下界是否正确；
3. n_boot是否为1000；
4. 是否误画了Bootstrap分布；
5. 13个来源是否完整；
6. 最差来源是否为正确文件；
7. 最差S是否完整显示；
8. 所有可比轴是否从0开始；
9. 是否错误使用断轴或对数轴；
10. S越低越好是否清楚；
11. 图例、标签和注释是否重叠；
12. 是否出现逐来源一致鲁棒的错误表述；
13. PDF、SVG、PNG画布是否一致。

## 十二、最终汇报

完成后汇报：

- 检索的模板页面；
- 选出的三个模板组合；
- Bootstrap区间核验结果；
- 13个来源及最差来源核验结果；
- 三个候选主要区别；
- 推荐顺序及理由；
- 输出文件列表；
- 尚需人工确认的问题。

不要只提供模板建议，实际生成三个候选图并完成比较。