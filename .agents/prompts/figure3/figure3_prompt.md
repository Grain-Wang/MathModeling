# 任务：绘制图3“Q3物理残差与AP→系统结构”

请读取：

- guide/figures_guide.md
- projects/rehearsal_2024_B/work/handoff/eight_figure_resources.md
- projects/rehearsal_2024_B/results/verified/figure_data/fig03_q3_structure.json
- projects/rehearsal_2024_B/work/04_solution_plan.md
- projects/rehearsal_2024_B/work/08_main_model_report.md
- projects/rehearsal_2024_B/work/10_result_freeze.md
- projects/rehearsal_2024_B/results/verified/freeze_manifest.json
- projects/rehearsal_2024_B/results/verified/result_registry.md
- projects/rehearsal_2024_B/src/s3_lineage.py
- projects/rehearsal_2024_B/src/s4_selection.py
- projects/rehearsal_2024_B/src/s5_release.py

## 模板库

优先检索：

1. https://github.com/opentikz/opentikz
   - templates/system-block-diagram
   - templates/resnet-block
   - templates/flowchart

2. https://github.com/FriendlyUser/LatexDiagrams
   - ControlSystems
   - ArtificialIntelligence
   - EngineeringSoftwareDesign

3. https://github.com/jgraph/drawio-diagrams
   - templates/flowcharts
   - templates/software
   - templates/engineering
   - templates/layout

4. https://github.com/xinychen/awesome-latex-drawing
   - Framework

先比较至少3个候选模板，记录到：

projects/rehearsal_2024_B/figures/fig03_template_candidates.md

记录模板路径、可复用结构、局限和最终选择理由。

## 必须表达的模型结构

整体采用横向“双分支汇合”结构。

输入：

- Q1 bounded发送时长预测 ŝᵢ；
- 真实NSS、MCS映射得到PHY Rate Rᵢ；
- 共享机制与RSSI特征 zᵢ。

物理分支：

pᵢ = (ŝᵢ / test_durᵢ) Rᵢ
→ η经训练侧拟合并裁剪到[0,1]
→ 物理基线 ŷᵢphy = ηpᵢ

fallback：

- 仅当PHY Rate不可用时启用Q3-B1 Ridge；
- 使用灰色虚线；
- 不得画成与正常物理基线同时相加。

残差分支：

zᵢ、pᵢ及相关派生特征
→ Q3-M1-HGB-UNIFIED
→ Q3-physics_residual-C3
→ 残差 f₃(zᵢ,pᵢ)

融合：

ŷᵢ = max(0, ŷᵢphy + f₃(zᵢ,pᵢ))

然后：

AP级非负吞吐量
→ 同一严格完整组内求和 Σ
→ 系统吞吐量

必须注明：

- 系统吞吐量没有独立预测头；
- 训练阶段Q3使用登记的Q1 OOF预测；
- 部署阶段使用全量训练后的Q1-B1预测；
- Q2不进入Q3；
- 2 AP与3 AP共用统一模型，AP count只是输入特征。

## 视觉规范

- 使用本地Draw.io绘制；
- 所有节点、公式和箭头保持可编辑；
- 物理分支使用低饱和蓝；
- HGB残差分支使用低饱和绿或紫；
- 非负约束和选择节点使用橙色；
- fallback使用灰色虚线；
- 输出使用深青色；
- 加法节点用圆形“+”；
- 组内聚合用圆形“Σ”；
- 使用虚线大框包住Q3 physics-residual C3；
- 无渐变、无重阴影、无卡通图标；
- 不得把HGB画成神经网络。

## 禁止内容

不得加入：

- Q2→Q3箭头；
- 独立的2 AP与3 AP模型；
- 独立系统吞吐量预测头；
- 官方测试成绩；
- S=0.550330或提升比例；
- 将嵌套管线成绩归因于固定residual-C3；
- 因果关系描述；
- 测试结果返回训练流程的箭头。

证据边界：

- E-Q3-CONFIG-001
- E-FREEZE-001

如提到嵌套选模表现，必须与固定C3全量配置严格区分。

## 输出

生成：

projects/rehearsal_2024_B/figures/fig03_q3_structure.drawio
projects/rehearsal_2024_B/figures/fig03_q3_structure.svg
projects/rehearsal_2024_B/figures/fig03_q3_structure.pdf
projects/rehearsal_2024_B/figures/fig03_q3_structure.png
projects/rehearsal_2024_B/figures/fig03_q3_structure_delivery.md

完成第一版后至少执行两轮：

绘制 → 导出PNG → 检查 → 修改。

检查：

- 公式和节点是否准确；
- fallback条件是否清楚；
- 物理与残差分支是否容易区分；
- 箭头是否穿过节点；
- Q1训练/部署口径是否准确；
- Q2是否保持独立；
- AP→系统求和关系是否清楚；
- 缩小到论文整页宽度后是否可读。

不要只给设计方案，完成模板比较、绘图、导出和检查。