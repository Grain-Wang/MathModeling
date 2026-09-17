# 图 1 总体技术路线图：Draw.io → Penpot 工作流

本指南供正式比赛复用。它固定**事实核对 → 模板搜集与比较 → Draw.io 可编辑初稿 → 初稿验收 → Penpot 原生美化 → 最终验收与导出**的顺序，不预先指定模板、泳道、阶段数、方向、颜色或画布尺寸。具体图形结构由本次赛题的信息和模板比较结果决定。图 1 的内容要求见 [八图总指南](figures_guide.md)，正式绘图数据遵守 [绘图规范](09_plotting_protocol.md)。

## 0. 准备事实与绘图任务

1. 读取题目、项目的 work/handoff/figure_handoff.md、模型与结果说明，以及 results/verified/ 中的正式结果；为关键数值和结论记录证据文件或 Evidence ID。尚未核验的内容只能标成草案，不能进入最终图。
2. 列出图 1 要回答的问题、需要出现的输入、处理、各子问题、模型、验证、产物和最终输出。另列真实的数据流、计算依赖和时间顺序；不要把流程箭头自动解释为因果关系。
3. 标明必须保留的名称、数字、限制条件，以及不得画出的关系。绘图前按项目绘图规范确认本次使用的 Scientific Illustrator 设计和 Draw.io 绘制 skill，并用一句话说明选择原因。

**进入下一步的条件：**有可逐项核对的节点与连接清单；事实不清楚时先回到题目或结果文件，不靠图形补全。

## 1. 搜罗和比较模板：Draw.io 开始前的必经步骤

在创建 Draw.io 节点、连线或画布之前，先检查 Draw.io 内置模板、公开的可编辑 .drawio / .xml 模板库及项目已有参考图。按本题的内容结构搜集至少三个相关候选；若确实不足三个，记录检索来源、关键词和未找到更多适用模板的原因。可以借鉴模板的分组或连线方式，也可以在比较后选择空白画布。

在 projects/<project_name>/figures/figure1/template_review.md 留下比较表：

| 候选及来源链接 | 与本题节点和依赖的匹配程度 | 可编辑性、连线和缩小后的可读性 | 需要改动的部分 | 采用或放弃的理由 |
| --- | --- | --- | --- | --- |

选择适合本题的**结构参考**，说明哪些部分可借鉴、哪些必须重画。配色灵感与结构模板分开记录；不因为模板好看就改变事实、箭头方向或增加无关节点。模板比较记录完成后，才进入 Draw.io 绘制。

## 2. 在 Draw.io 绘制可编辑初稿

使用 Scientific Illustrator 的 Draw.io 能力，根据节点与连接清单规划阅读顺序、分组和连接线，再逐区域绘制。模板只作为参考，所有文字、节点、箭头、图例和分区仍须适配本题并保持可编辑；不把整张参考图贴成位图。涉及真实数值的曲线、地图或统计图由数据绘图程序生成，图 1 仅表达其在研究流程中的位置。

保存 fig1_overall_workflow.drawio，同时导出 fig1_overall_workflow_drawio.svg 和预览 PNG，供后续对照。图内的每个数字、模型名和依赖应能回指第 0 步的事实清单。

### Gate A：Draw.io 初稿验收

- 重新打开 .drawio，确认节点、文字和连线可编辑，导出的 SVG 完整可读。
- 按事实清单逐项核对名称、数字、箭头方向及数据/验证边界；不存在凭空添加的因果关系。
- 检查阅读顺序、文字截断与重叠、连线穿过节点、无意义交叉线，以及论文版面缩小后的可读性。
- 修正后重新导出，并在交付记录中标记通过 Gate A。未通过时继续修改 Draw.io，不进入 Penpot。

## 3. 在 Penpot 美化并保留原生对象

先检查 Penpot MCP 服务、插件连接和目标文件；新文件先做可逆的读写验证。将 Draw.io 导出图放在独立参考页并锁定；若 SVG 不能直接导入，可用其 PNG 预览作锁定参考。最终 Board 应以 Penpot 原生文本、形状和路径重建，不能以参考位图充当成品。

在不改变 Gate A 内容和箭头语义的前提下，统一栅格、间距、字体层级、分组、线型和色彩。具体版式与配色在看过本题内容和 Draw.io 初稿后确定。保留 Draw.io 源文件，在交付记录中写明 Penpot 文件、页面、Board 的名称和链接。

### Gate B：Penpot 最终验收

至少执行两轮“截图或导出 → 检查 → 修正 → 再检查”。逐项比对 Draw.io 初稿、事实清单与 Penpot Board，确认没有漏项、改名、改数、反向箭头或新增关系；检查文字、节点、线条、图例、证据标识和缩小后的可读性。再检查导出的 SVG/PDF 是否保持矢量、PNG 是否至少为 2×，并在最终论文版面查看一次。若导出接口产生空文件或异常文件，改用其他原生导出方式，并重新验证文件内容。

Penpot 阶段是图 1 的**必经交付门槛**。连接或导出失败时，保留已验收的 Draw.io 初稿、记录阻塞并排障；不能把未完成 Penpot 验收的图标记为最终图。

## 4. 交付目录与记录

图 1 的全部文件放在 projects/<project_name>/figures/figure1/；图 2 至图 8 分别放在同级 figure2/ 至 figure8/。图 1 至少保留：

~~~text
projects/<project_name>/figures/figure1/
├── template_review.md                 # 绘图前完成的模板比较
├── fig1_overall_workflow.drawio       # 可编辑的 Draw.io 初稿
├── fig1_overall_workflow_drawio.svg   # 初稿矢量对照
├── fig1_overall_workflow_drawio.png   # 初稿视觉预览
├── fig1_overall_workflow_penpot.svg   # Penpot 最终矢量图
├── fig1_overall_workflow_penpot.pdf   # 论文使用的矢量图
├── fig1_overall_workflow_penpot.png   # 至少 2× 的预览图
└── delivery.md                        # 证据、Penpot Board 链接、检查与导出记录
~~~

delivery.md 记录事实源和版本、模板比较结论、两次验收结果、Penpot 文件/页面/Board 链接、导出方式及文件检查结果。交稿时以通过 Gate B 的 Penpot PDF/SVG 为正式版本，同时保留 Draw.io 原件和阶段预览，不覆盖它们。

## 可复用的任务说明

> 根据本项目的题目、figure_handoff.md 和 results/verified/，先整理图 1 的事实与依赖清单。创建任何 Draw.io 对象前，搜集并比较至少三个相关模板，在 figures/figure1/template_review.md 写出选择或不用模板的理由。随后用 Scientific Illustrator 在 Draw.io 绘制可编辑初稿，完成 Gate A 后，在 Penpot 用原生对象美化并完成两轮 Gate B 检查。按本指南交付源文件、Board 链接及 SVG。不要预设模板、画面结构、颜色或赛题事实。