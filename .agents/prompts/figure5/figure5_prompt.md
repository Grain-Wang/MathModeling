# 任务：检索模板并生成图5的三个候选版本

请为 2024 年 B 题绘制图5：

“Q3 AP预测诊断与Q2固定17类混淆矩阵”。

要求先在线检索指定模板库，从中选出最适合本题的三个模板组合，
再使用同一份已核验数据生成三个候选版本并比较。

## 一、必须读取的项目文件

主要绘图数据：

projects/rehearsal_2024_B/results/verified/figure_data/fig05_prediction_diagnostics.json

绘图规范与证据边界：

guide/figures_guide.md
guide/09_plotting_protocol.md
projects/rehearsal_2024_B/work/handoff/eight_figure_resources.md
projects/rehearsal_2024_B/results/verified/result_registry.md

重点核对：

- E-Q3-OOF-001
- E-Q2-CONF-001

正式图只能直接读取 results/verified/ 中的已核验数据，
不得重新训练模型或重新生成预测。

## 二、必须确认的数据口径

从 JSON 中读取并验证：

### Q3 AP回归诊断

- scope：PRIMARY_GROUPED_OOF_REPEAT_0；
- 样本数：1250个AP行；
- 字段包括truth_mbps、prediction_mbps、residual_mbps、ap_count；
- 残差定义必须是：
  prediction_mbps - truth_mbps；
- AP级MAE从JSON读取，约为15.046265 Mbps；
- row_key必须唯一；
- 不得删除或手工修改异常点。

### Q2分类诊断

- 固定17个联合类别；
- 标签顺序必须保持JSON中的顺序；
- repeat 0、1、2各有一张17×17混淆矩阵；
- 每张矩阵元素之和必须为1250；
- 三次重复是同一批1250条训练AP行的重复验证；
- 不得写成3750个独立样本；
- 行为真实标签，列为预测标签。

若任何样本数、矩阵维度、标签顺序或字段含义不一致，停止绘图并报告。

## 三、在线检索的模板库

请实际访问并阅读示例代码，不要只记录网址。

### 1. Matplotlib Gallery

https://matplotlib.org/stable/gallery/index.html

重点搜索：

- subplot_mosaic
- GridSpec
- nested GridSpec
- scatter plot with legend
- axline
- horizontal zero line
- annotated heatmap
- shared colorbar
- label subplots

### 2. scikit-learn PredictionErrorDisplay

https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html

重点搜索：

- actual_vs_predicted
- residual_vs_predicted
- from_predictions
- scatter_kwargs
- line_kwargs

注意：
scikit-learn的残差定义可能与本项目不同。
本项目必须使用prediction-truth，不得照搬相反符号。

### 3. scikit-learn ConfusionMatrixDisplay

https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ConfusionMatrixDisplay.html

重点搜索：

- fixed display labels
- multiclass confusion matrix
- shared color scale
- include_values
- colorbar

不得重新从标签生成矩阵，应直接使用JSON中的矩阵。

### 4. Seaborn heatmap

https://seaborn.pydata.org/generated/seaborn.heatmap.html

重点搜索：

- annotated heatmap
- shared colorbar
- mask zero annotations
- square heatmap
- common vmin vmax

### 5. SciencePlots

https://github.com/garrettj403/SciencePlots

重点搜索：

- science
- no-latex
- scatter
- ieee
- color-blind-safe styles

SciencePlots只作为视觉样式层，不单独算作完整模板。

### 6. Yellowbrick

https://www.scikit-yb.org/en/latest/api/regressor/index.html

仅参考：

- PredictionError
- ResidualsPlot
- ConfusionMatrix

不得调用Yellowbrick重新fit或predict。

## 四、从模板库选择三个候选方案

至少比较三个模板组合，并分别生成图像。

优先尝试以下三类，但允许根据实际检索结果调整。

### 候选A：标准五面板论文版

布局：

上排：
- (a) Q3 AP真实值—预测值散点；
- (b) Q3 AP残差—预测值散点。

下排：
- (c) Q2 repeat 0混淆矩阵；
- (d) Q2 repeat 1混淆矩阵；
- (e) Q2 repeat 2混淆矩阵；
- 三张矩阵共用一个colorbar。

参考：

- Matplotlib GridSpec或subplot_mosaic；
- scikit-learn PredictionErrorDisplay；
- Seaborn heatmap；
- SciencePlots。

### 候选B：Q3主结果突出版

布局：

- 左侧大图：Q3真实—预测散点；
- 左下或下方：Q3残差图；
- 右侧：三张Q2混淆矩阵纵向或紧凑排列。

适合突出Q3回归诊断，Q2作为辅助诊断。

### 候选C：诊断稳定性对照版

布局：

- 上排：Q3真实—预测与残差；
- 下排：Q2三次repeat并排；
- 强调三张混淆矩阵的统一类别顺序、统一色阶和可比性。

可参考：

- Matplotlib annotated heatmap；
- ConfusionMatrixDisplay；
- 共享色条的多热图布局。

如果实际检索后发现更适合的第三种结构，可以替换，
但必须在模板审查文档中说明原因。

## 五、所有候选图的共同要求

### Q3真实—预测图

必须包含：

- 横轴：真实AP吞吐量 / Mbps；
- 纵轴：预测AP吞吐量 / Mbps；
- y=x理想预测线；
- 横纵轴相同数值范围；
- 1:1视觉比例；
- n=1250 AP行；
- MAE从JSON读取；
- 2 AP与3 AP使用不同marker；
- 半透明散点减少遮挡。

建议：

- 2 AP使用圆形；
- 3 AP使用三角形；
- 颜色低饱和且色盲友好；
- 黑白打印时仍可通过marker区分。

### Q3残差图

必须包含：

- 横轴优先使用预测AP吞吐量；
- 纵轴：预测-真实 / Mbps；
- y=0水平参考线；
- 2 AP和3 AP保持与上一子图一致的marker和颜色；
- n=1250；
- 不得改变残差符号。

可加入描述性平滑趋势线，但必须：

- 不作为因果解释；
- 不遮挡散点；
- 在图例或图注中标明仅为描述性趋势。

### Q2混淆矩阵

必须：

- 分别展示repeat 0、1、2；
- 每张标注n=1250；
- 固定17类顺序；
- 行=真实类别，列=预测类别；
- 三张图使用相同vmin、vmax和colormap；
- 共用colorbar；
- 保留所有稀有类；
- 不合并为“其他”；
- 不把三张矩阵求和后替代原图。

为避免过密，可：

- 颜色表示全部数值；
- 只标注非零值；
- 或只标注对角线及超过统一阈值的单元。

三张矩阵必须使用完全相同的标注规则。

## 六、禁止内容

不得：

- 使用官方测试结果；
- 写成独立测试集性能；
- 将repeat 0称为唯一验证；
- 将三次重复称为3750个独立样本；
- 重新训练或重新预测；
- 修改固定17类顺序；
- 删除稀有类别；
- 使用3D热图；
- 使用彩虹色；
- 使用不同色阶比较三张矩阵；
- 将残差定义为truth-prediction；
- 添加未经验证的因果结论；
- 标注固定residual-C3的独立性能。

## 七、实现与输出

使用现有math_modeling Conda环境。

所有候选版本必须直接读取：

projects/rehearsal_2024_B/results/verified/figure_data/fig05_prediction_diagnostics.json

输出目录：

projects/rehearsal_2024_B/figures/figure5/

创建：

template_review.md
candidate_comparison.md

三个候选版本：

fig05_candidate_A.py
fig05_candidate_A.svg
fig05_candidate_A.pdf
fig05_candidate_A.png

fig05_candidate_B.py
fig05_candidate_B.svg
fig05_candidate_B.pdf
fig05_candidate_B.png

fig05_candidate_C.py
fig05_candidate_C.svg
fig05_candidate_C.pdf
fig05_candidate_C.png

PDF和SVG必须保持矢量，PNG至少300 DPI。

## 八、模板审查文档

在template_review.md中记录：

- 检索过的网站和具体页面；
- 示例名称或源码地址；
- 每个模板可复用的部分；
- 与本题不匹配的部分；
- 最终选出的三个候选；
- 每个候选的布局草图；
- 是否完全可复现；
- 是否适合论文整页展示。

## 九、候选比较

在candidate_comparison.md中比较：

- Q3真实—预测关系是否清楚；
- 系统偏差是否容易从残差图识别；
- 2 AP与3 AP是否容易区分；
- 三次Q2混淆模式是否可比较；
- 17类标签是否可读；
- 色条和数值标注是否过密；
- 缩小到论文整页宽度后的可读性；
- 黑白打印效果；
- PDF/SVG质量；
- 修改和复现成本；
- 与图2、图4视觉风格的一致性。

根据实际生成结果给出推荐顺序，但保留三个候选版本。

## 十、视觉检查

每个候选至少执行一轮：

生成 → 导出PNG → 检查 → 修正。

检查：

1. Q3是否加载全部1250个点；
2. 2 AP与3 AP的数量是否正确；
3. y=x线是否正确；
4. 残差零线是否清楚；
5. 残差符号是否为预测-真实；
6. 三张矩阵是否均为17×17；
7. 每张矩阵总数是否为1250；
8. 三张矩阵色阶是否一致；
9. 类别标签是否截断；
10. 标注是否重叠；
11. 图例和colorbar是否遮挡；
12. 是否错误写成官方测试；
13. PDF、SVG、PNG画布是否一致。

## 十一、最终汇报

完成后汇报：

- 检索的模板页面；
- 最终选出的三个模板组合；
- Q3样本数与MAE；
- Q2每次repeat的矩阵总数；
- 三个候选的主要区别；
- 推荐顺序及理由；
- 输出文件列表；
- 仍需人工确认的问题。

不要只提供模板建议，实际生成三个候选图并完成比较。