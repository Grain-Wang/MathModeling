# 任务：检索模板并生成图8的三个候选版本

请为2024年B题绘制图8：

“冻结模型的部署与风险处置”。

先读取项目事实，在线检索指定模板库，选择三个最适合的模板组合，
再生成三个可编辑Draw.io候选版本并比较。不要覆盖最终正式图。

## 一、必须读取

projects/rehearsal_2024_B/results/verified/figure_data/fig08_deployment_decision.json
projects/rehearsal_2024_B/results/verified/figure_data/fig07_robustness_uncertainty.json
projects/rehearsal_2024_B/results/verified/freeze_manifest.json
projects/rehearsal_2024_B/results/verified/final_release_verification.json
projects/rehearsal_2024_B/results/verified/result_registry.md
projects/rehearsal_2024_B/work/handoff/eight_figure_resources.md
guide/figures_guide.md
guide/09_plotting_protocol.md

重点核对：

- E-FREEZE-001
- E-Q2-001
- E-Q3-CONFIG-001
- E-RELEASE-001

## 二、必须表达的事实

冻结模型栈：

- Q1：Q1-B1
- Q2：Q2-B1A
- Q3：Q3-M1-HGB-UNIFIED
- Q3部署配置：Q3-physics_residual-C3

节点：

- 已授权的WLAN场景输入
- Q1 bounded时长
- Q2固定17类NSS/MCS概率，保留Logistic
- Q3 unified residual-C3 AP吞吐
- 系统吞吐=同组bounded AP严格求和
- 低支持类别/来源外推风险
- 人工核查，不反向调模

依赖：

- scenario→Q1
- scenario→Q2
- scenario→Q3
- Q1→Q3
- Q3→system
- Q2→risk
- system→risk

不得增加Q2→Q3箭头。

## 三、发布与风险边界

必须表达：

- 模型选择已冻结，selection_closed=true；
- 官方测试仅执行一次S5 release；
- release status=PASS只表示交付验证通过；
- 官方测试无标签，不能写准确率或误差；
- 官方输出不得反馈到训练、选模或调参；
- 系统吞吐不存在独立预测头；
- 保留低支持类别和最差source的风险提示；
- 风险处置为人工核查和披露。

不得绘制：

- 网络参数优化建议；
- 推荐信道、带宽或功率配置；
- 经济收益；
- 官方测试性能；
- 测试输出返回模型的箭头；
- 未定义的自动拒绝阈值。

## 四、在线检索模板库

### 1. OpenTikZ

https://github.com/opentikz/opentikz

重点查看：

- templates/inference-serving
- templates/system-block-diagram
- templates/flowchart

搜索：

deployment pipeline
inference serving
system block diagram
risk gate
manual review
fallback flow

### 2. diagrams.net官方模板

https://github.com/jgraph/drawio-diagrams

重点查看：

- templates/business/bpmn_*.xml
- templates/business/business_continuity_1.xml
- templates/flowcharts/cross_functional_flowchart_*.xml
- templates/flowcharts/workflow_*.xml

搜索：

BPMN
swimlane
business continuity
risk process
manual review
decision workflow

### 3. drawio-ai-kit

https://github.com/sparklabx/drawio-ai-kit

重点查看：

- examples/bpmn/build_bpmn.mjs
- examples/aws/build_pipeline.mjs
- rules/diagram-types.md
- rules/principles.md

搜索：

bpmn swimlane
pipeline
sequence
risk governance
manual task
validation

### 4. Scientific Illustrator

https://github.com/icebird1998/scientific-illustrator

读取设计和Draw.io工作流，只作为最终绘制工具，不算模板候选。

## 五、生成三个候选方案

### 候选A：部署管线+风险闸门

布局：

场景输入
→ 冻结模型栈
→ AP与系统输出
→ 风险核查

冻结模型栈内并列Q1、Q2、Q3，并明确Q1→Q3。

使用虚线框表示Frozen inference stack。

右侧风险区包含：

- 低支持类别
- 来源外推
- 人工核查
- 不反向调模

### 候选B：三泳道BPMN

泳道：

1. 场景与输入
2. 冻结模型推理
3. 输出与风险治理

使用并行分支表示Q1/Q2/Q3。

使用人工任务表示风险核查。

终点明确为：

已披露风险的部署输出。

不得画返回训练的循环。

### 候选C：模型卡片+底部治理带

上方：

- 场景输入
- Q1/Q2/Q3模型卡
- AP输出
- 系统求和

底部横跨全图：

Risk & Governance

包含：

- 低支持类别风险
- 最差source外推风险
- 人工核查
- 无测试反馈

使用连接线从Q2和system接入治理带。

## 六、视觉要求

- 正式论文风格；
- 横向版式；
- 白色或极浅灰背景；
- 低饱和、色盲友好；
- 无渐变、重阴影和卡通图标；
- 节点、文字、箭头和分区全部可编辑；
- Q1蓝色、Q2紫色、Q3绿色；
- 系统输出使用深青色；
- 风险与人工核查使用低饱和橙色；
- 冻结与发布状态使用中性灰或小型状态徽标；
- 主推理流使用实线；
- 风险提示流使用虚线或不同线型；
- 不使用红色大面积警报风格；
- 黑白打印仍能依靠线型和边框理解。

## 七、候选输出

输出到：

projects/rehearsal_2024_B/figures/figure8/

创建：

template_review.md
candidate_comparison.md

生成：

fig08_candidate_A.drawio
fig08_candidate_A.svg
fig08_candidate_A.pdf
fig08_candidate_A.png

fig08_candidate_B.drawio
fig08_candidate_B.svg
fig08_candidate_B.pdf
fig08_candidate_B.png

fig08_candidate_C.drawio
fig08_candidate_C.svg
fig08_candidate_C.pdf
fig08_candidate_C.png

## 八、模板审查

在template_review.md中记录：

- 实际访问的模板页面；
- 具体模板或源码路径；
- 可复用结构；
- 与本题不匹配的部分；
- 三个候选各自采用的模板组合；
- 可编辑性；
- 论文正文适配性；
- 黑白打印适配性。

## 九、候选比较

在candidate_comparison.md中比较：

- 冻结模型栈是否清晰；
- Q1→Q3是否准确；
- Q2是否保持独立；
- AP→系统求和是否清楚；
- 风险信息是否足够但不过度；
- 人工核查与无反馈边界是否清楚；
- release PASS是否会被误解为准确率；
- 缩小到论文整页宽度后的可读性；
- 与图1和图3的视觉一致性；
- 后续修改成本。

基于实际生成结果给出推荐顺序，但保留三个候选。

## 十、绘制与检查

使用Scientific Illustrator连接实时Draw.io绘制。

每个候选至少执行一轮：

绘制→导出PNG→检查→修正。

检查：

1. 所有节点和依赖是否与JSON一致；
2. 是否错误出现Q2→Q3；
3. 是否错误出现独立system head；
4. 是否存在测试结果返回模型的箭头；
5. 是否错误把PASS解释为性能；
6. 是否保留低支持类别和最差source风险；
7. 是否出现未求解的网络调参建议；
8. 箭头是否穿过节点；
9. 文字是否截断；
10. PDF、SVG、PNG画布是否一致。

## 十一、最终汇报

完成后汇报：

- 检索的模板库与页面；
- 三个候选采用的模板组合；
- 模型栈与依赖核验结果；
- 发布与无反馈边界核验结果；
- 三个候选的主要区别；
- 推荐顺序及理由；
- 输出文件列表；
- 尚需人工确认的问题。

不要只给设计建议，实际完成三个可编辑候选图和比较文档。