# 任务：用 LaTeX/PGFPlots 绘制图 2——合格训练数据分布图组

请在当前仓库中完成图 2 的数据核验、设计、绘制、编译和导出。

## 1. 必须读取

主要数据：

projects/rehearsal_2024_B/results/verified/figure_data/fig02_training_distributions.json

图形要求：

guide/figures_guide.md
projects/rehearsal_2024_B/work/handoff/eight_figure_resources.md

证据边界：

projects/rehearsal_2024_B/results/verified/result_registry.md

核对证据：

- E-DATA-001
- E-EDA-001

fig02_data_quality.json 只用于核对数据范围，不再作为图 2 主题。

## 2. 图的目标

图 2 最多包含三个概念子图：

(a) Q1 发送时长分布；
(b) Q2 的 17 个联合类别频数；
(c) Q3 的 AP 真实吞吐量和系统真实吞吐量分布。

图中只展示合格训练数据真值，不加入：

- 模型预测；
- 验证指标；
- 模型优劣；
- 官方测试结果；
- 因果结论。

## 3. 数据口径

必须验证：

- Q1：1250 个 AP 行；
- Q2：1250 个 AP 行，17 类，类别频数和为 1250；
- Q3 AP：1250 个 AP 行；
- Q3 系统：482 个完整组；
- 所有单位从 JSON 读取，不得猜测；
- AP 行和系统组必须明确标注为不同观测粒度。

如果样本数、类别数、单位或字段含义不一致，停止绘图并报告。

不得静默删除缺失值、离群值或极端值。

## 4. 子图设计

### Panel (a)：Q1

先检查唯一值数量、偏度、长尾和零值。

选择规则：

- 连续且取值丰富：直方图；
- 强偏态或长尾：直方图或 ECDF；
- 少量离散值：频数图；
- KDE 不得作为唯一表示。

标注：

- n = 1250 AP 行；
- 单位；
- 中位数；
- 必要时标注 IQR 或 P5–P95。

### Panel (b)：Q2

绘制 17 类频数条形图。

要求：

- 保持 JSON 中规定的固定类别顺序；
- 若没有固定顺序，才按频数排序并记录原因；
- 不得合并为“其他”；
- 标注频数，空间允许时同时标注比例；
- 标签长时使用横向条形图；
- 标注 n = 1250 AP 行、17 类。

### Panel (c)：Q3

在同一概念子图中分别展示：

- AP 真实吞吐量：1250 个 AP 行；
- 系统真实吞吐量：482 个完整组。

建议使用两个上下或左右对齐的小轴。

要求：

- 明确标注样本数、单位和观测粒度；
- 如果范围接近，可共享横轴和 bin；
- 如果范围差异过大，使用独立横轴；
- 不得用两个不透明直方图互相遮挡；
- 不得将 AP 频数与系统频数直接比较。

如展示 2 AP／3 AP 分组，只能描述分布差异，不得解释为因果效应。

## 5. 推荐版式

优先选择以下之一：

方案 A：

- 上排：(a) Q1、(b) Q2；
- 下排：(c) Q3 横跨整行。

方案 B：

- 左上：(a) Q1；
- 左下：(c) Q3；
- 右侧：(b) Q2 横向条形图跨两行。

根据类别标签长度和最终可读性选择。

整图适合 A4 论文整页宽度，正文和刻度最终不低于约 7.5 pt。

## 6. 模板参考

正式绘图前至少比较两个相关图表示例，在 `projects/rehearsal_2024_B/figures/figure2/reference_review.md` 记录来源、可借鉴技法、适配性及取舍。可参考：

PGFPlots Gallery：
https://pgfplots.sourceforge.net/gallery.html

关键词：

- histogram
- xbar
- ybar
- nodes near coords
- symbolic y coords
- groupplots
- empirical cumulative distribution

Walmes TikZ：
https://github.com/walmes/Tikz

awesome-latex-drawing：
https://github.com/xinychen/awesome-latex-drawing

只借鉴布局、标注和 PGFPlots 技法，不复制无关内容。

## 7. 数据提取

创建：

projects/rehearsal_2024_B/figures/figure2/fig02_training_distributions_extract.py

Python 脚本负责：

- 读取并验证 JSON；
- 计算样本数和描述统计；
- 计算 Q2 类别频数；
- 确定直方图 bin；
- 输出 PGFPlots 可读取的 CSV；
- 输出 LaTeX 数据宏；
- 输出统计摘要。

CSV、LaTeX 数据宏及统计摘要统一放在 `projects/rehearsal_2024_B/figures/figure2/data/`。

不得手工把逐行数据抄进 TEX。

连续变量 bin 优先使用 Freedman–Diaconis 规则，并限制在合理范围，如 12–40。

## 8. LaTeX 绘图

创建：

projects/rehearsal_2024_B/figures/figure2/fig02_training_distributions.tex

使用：

- standalone；
- XeLaTeX；
- ctex；
- TikZ；
- PGFPlots；
- groupplots；
- statistics。

Python 只负责数据处理，最终图必须由 LaTeX/PGFPlots 生成。

字体优先使用本机已有的：

- Noto Sans CJK SC；
- Source Han Sans SC；
- 思源黑体。

不得复制或提交字体文件。

## 9. 视觉规范

- 白色背景；
- 正式、简洁、低饱和；
- Q1 使用蓝色；
- Q2 使用紫色或蓝紫色；
- Q3 AP 与系统使用同色系不同深浅或线型；
- 无渐变、无重阴影、无 3D；
- 不使用彩虹色；
- 不使用双 Y 轴；
- 黑白打印仍能区分；
- 图例不得遮挡数据；
- 不裁剪长尾而不说明；
- 不使用截断坐标轴夸大差异。

## 10. 必须标注

图中应清楚标出：

- Q1：n = 1250 AP 行；
- Q2：n = 1250 AP 行，17 类；
- Q3 AP：n = 1250 AP 行；
- Q3 系统：n = 482 完整组；
- 各变量单位；
- 图中均为合格训练数据真值。

图注中说明：

- Q1、Q2、Q3 AP 使用同一批 1250 个合格训练 AP 行；
- Q3 系统使用 482 个完整组；
- 2 AP／3 AP 差异仅为描述性现象；
- 证据编号为 E-DATA-001、E-EDA-001。

## 11. 输出文件

至少生成：

projects/rehearsal_2024_B/figures/figure2/reference_review.md

projects/rehearsal_2024_B/figures/figure2/fig02_training_distributions_extract.py
projects/rehearsal_2024_B/figures/figure2/fig02_training_distributions.tex
projects/rehearsal_2024_B/figures/figure2/fig02_training_distributions.pdf
projects/rehearsal_2024_B/figures/figure2/fig02_training_distributions.svg
projects/rehearsal_2024_B/figures/figure2/fig02_training_distributions.png
projects/rehearsal_2024_B/figures/figure2/fig02_training_distributions_caption.md
projects/rehearsal_2024_B/figures/figure2/fig02_training_distributions_delivery.md

PDF、SVG 必须保持矢量；PNG 至少 300 DPI。

## 12. 编译与检查

使用 latexmk + XeLaTeX 编译。

至少进行两轮：

编译 → 导出 PNG → 检查 → 修改 → 再编译。

检查：

- 中文是否正常；
- 17 类标签是否全部可读；
- 数值标签是否重叠；
- Q1 bin 是否合理；
- Q3 两种观测粒度是否清晰；
- 单位和样本数是否正确；
- 图例是否遮挡；
- 是否存在长尾裁剪；
- 缩小后是否可读；
- 黑白打印是否可区分；
- 是否误加入模型预测、验证结果或因果措辞。

## 13. 最终报告

完成后汇报：

- 实际字段与单位；
- 四类数据的样本数；
- Q2 类别频数总和；
- 三个 panel 的最终图形类型；
- Q3 是否共享横轴及原因；
- 是否展示 2 AP／3 AP；
- 生成文件列表；
- 编译 warning；
- 两轮视觉修改内容；
- 未解决问题。

不要只给设计建议，实际完成数据提取、LaTeX 绘图、编译、检查和导出。