# 图 1 总体技术路线图：Draw.io → Penpot 工作流

本指南供正式比赛复用。它固定**事实核对 → 模板搜集与比较 → Draw.io 可编辑初稿 → 初稿验收 → Penpot 原生美化与候选验收 → 用户确认 → 正式导出**的顺序，不预先指定模板、泳道、阶段数、方向、颜色或画布尺寸。具体图形结构由本次赛题的信息和模板比较结果决定。图 1 的内容要求见 [八图总指南](figures_guide.md)，正式绘图数据遵守 [绘图规范](09_plotting_protocol.md)。

## 0. 准备事实与绘图任务

1. 读取题目、项目的 work/handoff/figure_handoff.md、模型与结果说明，以及 results/verified/ 中的正式结果；为关键数值和结论记录证据文件或 Evidence ID。尚未核验的内容只能标成草案，不能进入最终图。
2. 列出图 1 要回答的问题、需要出现的输入、处理、各子问题、模型、验证、产物和最终输出。另列真实的数据流、计算依赖和时间顺序；不要把流程箭头自动解释为因果关系。
3. 标明必须保留的名称、数字、限制条件，以及不得画出的关系。绘图前按项目绘图规范记录 Draw.io 的绘制方式和理由；Scientific Illustrator 可按需要选用，不是必经工具。

**进入下一步的条件：**有可逐项核对的节点与连接清单；事实不清楚时先回到题目或结果文件，不靠图形补全。

## 1. 搜罗和比较模板：Draw.io 开始前的必经步骤

### 1.1 适用模板库网址

以下网址只作为模板发现入口，不代表其中任何具体模板已经通过用户验证。

| 模板库 | 网址 | 与本图的匹配点 | 使用说明 |
|---|---|---|---|
| diagrams.net 官方示例库 | [https://github.com/jgraph/drawio-diagrams](https://github.com/jgraph/drawio-diagrams) | 通用流程、分区、节点—边关系、顺序结构和泳道初稿 | 优先查看可编辑 `.drawio`/XML；只借鉴拓扑与排版，节点和箭头必须按当前赛题重建 |
| tech-route-maker | [https://github.com/Stephen-studying/tech-route-maker](https://github.com/Stephen-studying/tech-route-maker) | 论文方法框架、中文技术路线、研究阶段和证据驱动工作流 | 可从结构化 JSON 渲染 Draw.io、PPTX、SVG 等可编辑初稿；自动结果仍须逐项核对事实、依赖和证据，不能直接视为最终图 |
| OpenTikZ | [https://github.com/opentikz/opentikz](https://github.com/opentikz/opentikz) | 公式密集、模块规整、论文 LaTeX 字体一致的技术路线和方法框图 | 提供可编辑 `.tex` 模板与示例；适合紧凑规则结构，复杂自由布局或频繁拖拽修改时可改用 Draw.io |
| sci-box：scibox-diagram | [https://github.com/jihe520/sci-box](https://github.com/jihe520/sci-box) | 三栏研究框架、阶段条带、横向任务流水线和多带式路线图 | 提供 Draw.io 科研图模板；授权未确认时只借鉴分栏、层级和留白，不直接复制模板资产或图标 |
| Graphviz Gallery | [https://graphviz.org/gallery/](https://graphviz.org/gallery/) | 分支多、依赖复杂、需要自动减少交叉线的有向流程和层级结构 | 使用 `.dot` 源码可重建；自动布局只解决几何问题，不得把依赖边改写成因果、反馈或时间顺序 |
| C4 Draw.io 模板库 | [https://github.com/kaminzo/c4-draw.io](https://github.com/kaminzo/c4-draw.io) | 题目确有系统、模块、外部参与者、接口和层级边界时的路线总览 | 不把普通变量或论文子问题硬套成软件容器；采用素材时核对 CC BY 4.0 署名要求 |

### 1.2 已验证好用的模板

暂无已确认模板。只有用户明确确认某个具体模板好用后，才能在下表添加记录；代理自行筛选、成功打开或完成试绘均不算用户确认。

| 模板名称 | 具体模板链接或路径 | 适用场景 | 确认记录 |
|---|---|---|---|

### 1.3 按路线拓扑选择模板类型

在创建 Draw.io 节点、连线或画布之前，先根据事实清单判断路线图的真实拓扑，再从相应入口查找具体示例：

- **线性或分阶段研究路线：**优先查看 diagrams.net、tech-route-maker 和 sci-box，比较横向阶段、纵向层级与上下双带布局。
- **公式、数学模块和算法接口较多：**优先查看 OpenTikZ；需要后续拖拽美化时，可先用其结构作为参考，再在 Draw.io 中重建。
- **分支、汇合和依赖边很多：**优先查看 Graphviz Gallery，用自动布局测试可读性，再决定是否转为 Draw.io 原生对象。
- **真实存在系统、平台、设备、外部参与者和接口：**可查看 C4 Draw.io；先证明这些边界属于赛题事实，再采用对应层级。
- **需要证据定位和多格式初稿：**可用 tech-route-maker 生成可审查草案，但必须完成本指南的模板比较、Gate A 和 Penpot Gate B。
- **节点很少或没有合适模板：**比较后使用空白画布通常优于强行套用复杂框架。

图 1 是“整篇论文如何从输入走到结论”的总路线，不应画成图 3 的变量关系图、图 8 的部署执行图，也不应把论文目录机械排列成若干框。只有配色截图、不可编辑宣传图或与本题依赖不同的华丽流程图，不能计作结构模板。

### 1.4 模板检索与比较要求

按本题的内容结构实际打开至少三个相关候选，查看源文件、节点、连线、分组和许可说明，而非只看预览。若确实不足三个，记录检索来源、关键词和未找到更多适用模板的原因。可以借鉴模板的分组或连线方式，也可以在比较后选择空白画布。

在 projects/<project_name>/figures/figure1/template_review.md 留下比较表：

| 候选及来源链接 | 与本题节点和依赖的匹配程度 | 可编辑性、连线和缩小后的可读性 | 需要改动的部分 | 采用或放弃的理由 |
| --- | --- | --- | --- | --- |

每个候选至少记录具体示例链接或文件路径、源文件类型、许可与署名要求、计划借鉴和明确不借鉴的元素、可能造成的错误语义以及改造量。选择适合本题的**结构参考**，说明哪些部分可借鉴、哪些必须重画。配色灵感与结构模板分开记录；不因为模板好看就改变事实、箭头方向或增加无关节点。模板比较记录完成后，才进入 Draw.io 绘制。

## 2. 在 Draw.io 绘制可编辑初稿

在 Draw.io 中根据节点与连接清单规划阅读顺序、分组和连接线，再逐区域绘制。模板只作为参考，所有文字、节点、箭头、图例和分区仍须适配本题并保持可编辑；不把整张参考图贴成位图。涉及真实数值的曲线、地图或统计图由数据绘图程序生成，图 1 仅表达其在研究流程中的位置。

保存 fig1_overall_workflow.drawio，并导出 fig1_overall_workflow_drawio.png 供后续对照；用户确认最终版本前不保留 SVG/PDF。图内的每个数字、模型名和依赖应能回指第 0 步的事实清单。

### Gate A：Draw.io 初稿验收

- 重新打开 .drawio，确认节点、文字和连线可编辑，导出的 PNG 完整可读。
- 按事实清单逐项核对名称、数字、箭头方向及数据/验证边界；不存在凭空添加的因果关系。
- 检查阅读顺序、文字截断与重叠、连线穿过节点、无意义交叉线，以及论文版面缩小后的可读性。
- 修正后重新导出，并在交付记录中标记通过 Gate A。未通过时继续修改 Draw.io，不进入 Penpot。

## 3. 在 Penpot 美化并保留原生对象

先检查 Penpot MCP 服务、插件连接和目标文件；新文件先做可逆的读写验证。将 Draw.io 的 PNG 预览放在独立参考页并锁定。最终 Board 应以 Penpot 原生文本、形状和路径重建，不能以参考位图充当成品。

在不改变 Gate A 内容和箭头语义的前提下，统一栅格、间距、字体层级、分组、线型和色彩。具体版式与配色在看过本题内容和 Draw.io 初稿后确定。保留 Draw.io 源文件，在交付记录中写明 Penpot 文件、页面、Board 的名称和链接。

### Gate B：Penpot 候选验收

至少执行两轮“导出 PNG → 检查 → 修正 → 再检查”。逐项比对 Draw.io 初稿、事实清单与 Penpot Board，确认没有漏项、改名、改数、反向箭头或新增关系；检查文字、节点、线条、图例、证据标识、PNG 至少为 2× 及缩小后的可读性。将 Penpot 原生 Board、Draw.io 源和两阶段 PNG 交给用户确认。用户明确选定最终版本后，才从选定 Board 导出 SVG/PDF，并在最终论文版面检查矢量性、裁切和字体；异常时修正源文件、重新导出并复核。

Penpot 阶段是图 1 的**必经交付门槛**。连接或导出失败时，保留已验收的 Draw.io 初稿、记录阻塞并排障；不能把未完成 Penpot 验收的图标记为最终图。

## 4. 交付目录与记录

图 1 的全部文件放在 projects/<project_name>/figures/figure1/；图 2 至图 8 分别放在同级 figure2/ 至 figure8/。图 1 至少保留：

~~~text
projects/<project_name>/figures/figure1/
├── template_review.md                 # 绘图前完成的模板比较
├── fig1_overall_workflow.drawio       # 可编辑的 Draw.io 初稿
├── fig1_overall_workflow_drawio.png   # 初稿视觉预览
├── fig1_overall_workflow_penpot.png   # 候选阶段至少 2× 的预览图
├── fig1_overall_workflow_penpot.svg   # 用户确认后仅为最终版生成
├── fig1_overall_workflow_penpot.pdf   # 用户确认后仅为最终版生成
└── delivery.md                        # 证据、Penpot Board 链接、检查与导出记录
~~~

delivery.md 记录事实源和版本、模板比较结论、两次验收结果、Penpot 文件/页面/Board 链接、用户最终版确认及正式导出检查。确认前只保留源文件、Board 和 PNG；交稿时以用户确认且通过矢量检查的 Penpot PDF/SVG 为正式版本，同时保留 Draw.io 原件和阶段 PNG，不覆盖它们。

## 可复用的任务说明

> 根据本项目的题目、figure_handoff.md 和 results/verified/，先整理图 1 的事实与依赖清单。按路线拓扑从本指南列出的模板库中实际打开至少三个具体模板或源码示例，把网址、源文件、许可、适配性、错误语义风险和借鉴边界写入 figures/figure1/template_review.md；比较后可以选择空白画布。随后在 Draw.io 绘制可编辑初稿，完成 Gate A 后，在 Penpot 用原生对象美化并完成两轮 Gate B 检查；Scientific Illustrator 可按需选用。候选阶段只保留源文件、Board 链接及 PNG，交给我确认最终版本后再为选定版导出 SVG/PDF。不要预设模板、画面结构、颜色或赛题事实。