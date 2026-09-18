# 任务：使用 Penpot 美化图3的两个现有SVG候选方案

请使用 Penpot MCP，对图3“Q3物理残差与AP→系统结构”的两个现有候选版本进行视觉重构。

## 一、现有文件位置

候选C：系统框图结构

projects/rehearsal_2024_B/figures/figure3/C_system_block/fig03_q3_structure_C.drawio
projects/rehearsal_2024_B/figures/figure3/C_system_block/fig03_q3_structure_C.svg

候选D：残差块结构

projects/rehearsal_2024_B/figures/figure3/D_resnet_block/fig03_q3_structure_D.drawio
projects/rehearsal_2024_B/figures/figure3/D_resnet_block/fig03_q3_structure_D.svg

模板筛选与审核记录：

projects/rehearsal_2024_B/figures/figure3/fig03_template_candidates.md
projects/rehearsal_2024_B/figures/figure3/template_review.md

语义核对文件：

projects/rehearsal_2024_B/results/verified/figure_data/fig03_q3_structure.json
projects/rehearsal_2024_B/work/04_solution_plan.md
projects/rehearsal_2024_B/work/10_result_freeze.md
projects/rehearsal_2024_B/results/verified/result_registry.md

## 二、执行原则

1. 不覆盖C、D候选的原始drawio和SVG文件。
2. 不改变公式、模型名称、数字和真实依赖关系。
3. 不新增模型结果、验证成绩或因果结论。
4. 使用Penpot原生文本、矩形、分组、路径和箭头重建主要视觉元素。
5. 原始SVG只作为内容和布局参考，不直接作为最终交付图。
6. 所有主要对象保持独立可编辑。
7. 图层使用语义化名称。

## 三、Penpot页面

在Penpot文件中创建：

- 00_References
- 01_StyleA_Modular
- 02_StyleB_Sectioned

在00_References中导入并锁定：

- fig03_q3_structure_C.svg
- fig03_q3_structure_D.svg

## 四、方案A：清爽模块拼贴风

主要参考：

projects/rehearsal_2024_B/figures/figure3/C_system_block/fig03_q3_structure_C.svg

新建Board：

fig03_q3_structure_styleA

视觉要求：

- 白色或极浅灰背景；
- 使用绿色或灰绿色虚线框划分功能区域；
- 使用浅蓝、浅绿、浅紫卡片；
- 模块分区丰富但保持整齐；
- 物理基线分支使用低饱和蓝；
- residual HGB分支使用低饱和绿或紫；
- 非负约束使用低饱和橙；
- AP与系统输出使用深青色；
- 箭头简洁，避免交叉；
- 可使用非常轻的阴影；
- 不使用渐变、玻璃效果和卡通图标。

建议分区：

1. 输入与真实PHY状态；
2. 物理容量代理与效率系数；
3. residual HGB；
4. fallback；
5. 融合与非负约束；
6. AP到系统聚合。

## 五、方案B：黑虚线学术分区风

主要参考：

projects/rehearsal_2024_B/figures/figure3/D_resnet_block/fig03_q3_structure_D.svg

新建Board：

fig03_q3_structure_styleB

视觉要求：

- 白色背景；
- 使用黑色或深灰粗虚线框划分大区域；
- 每个区域设置简洁标题；
- 内部使用浅紫、浅蓝和浅灰模块；
- 减少装饰和小卡片数量；
- 增加留白；
- 强调主流程和双分支汇合；
- 箭头使用深灰细线；
- fallback使用灰色虚线；
- 不使用阴影、渐变和多余图标。

建议分区：

1. Input and PHY Information；
2. Physical Baseline；
3. Residual HGB；
4. Nonnegative AP Output；
5. AP-to-System Aggregation。

## 六、两个方案都必须保持的结构

输入：

- Q1 bounded发送时长预测；
- 真实NSS、MCS；
- PHY Rate；
- 共享机制与RSSI特征。

物理分支：

pᵢ = (ŝᵢ / test_durᵢ)Rᵢ
→ η裁剪到[0,1]
→ 物理基线。

残差分支：

特征与物理代理
→ Q3-M1-HGB-UNIFIED
→ Q3-physics_residual-C3
→ residual correction。

融合：

物理基线 + residual
→ max(0,·)
→ AP级非负吞吐量。

聚合：

同一严格完整组中的AP预测
→ Σ严格求和
→ 系统吞吐量。

必须注明：

- 训练阶段Q3使用登记的Q1 OOF预测；
- 部署阶段使用全量训练后的Q1-B1预测；
- Q2不进入Q3；
- fallback仅在PHY Rate不可用时启用；
- 2 AP与3 AP共用统一模型；
- AP count只是输入特征；
- 系统吞吐量没有独立预测头。

## 七、禁止事项

不得：

- 添加Q2→Q3箭头；
- 把HGB画成神经网络；
- 画两个独立的2 AP和3 AP模型；
- 添加独立system prediction head；
- 添加准确率、误差、综合得分或提升比例；
- 把嵌套管线成绩归因于固定C3配置；
- 改变fallback的触发条件；
- 改变max(0,·)和Σ的执行顺序；
- 将信息流箭头解释为因果关系。

证据边界：

- E-Q3-CONFIG-001
- E-FREEZE-001

## 八、输出目录

创建：

projects/rehearsal_2024_B/figures/figure3/E_penpot_styleA/
projects/rehearsal_2024_B/figures/figure3/F_penpot_styleB/

输出方案A：

projects/rehearsal_2024_B/figures/figure3/E_penpot_styleA/fig03_q3_structure_E.svg
projects/rehearsal_2024_B/figures/figure3/E_penpot_styleA/fig03_q3_structure_E.pdf
projects/rehearsal_2024_B/figures/figure3/E_penpot_styleA/fig03_q3_structure_E.png

输出方案B：

projects/rehearsal_2024_B/figures/figure3/F_penpot_styleB/fig03_q3_structure_F.svg
projects/rehearsal_2024_B/figures/figure3/F_penpot_styleB/fig03_q3_structure_F.pdf
projects/rehearsal_2024_B/figures/figure3/F_penpot_styleB/fig03_q3_structure_F.png

同时创建：

projects/rehearsal_2024_B/figures/figure3/penpot_style_compare.md

记录：

- 两个方案分别参考了哪个候选；
- 主要视觉修改；
- 采用的字体和颜色；
- 哪个更适合论文正文；
- 哪个更适合答辩展示；
- 仍需人工检查的事项。

## 九、质量检查

每个版本至少执行两轮：

Penpot修改
→ 导出PNG
→ 检查
→ 修正
→ 再次导出。

检查：

1. 公式和节点是否准确；
2. 是否有文字截断；
3. 箭头是否穿过节点；
4. 物理分支与残差分支是否清晰；
5. fallback是否明显但不抢眼；
6. max(0,·)的位置是否正确；
7. AP到系统的Σ求和是否清楚；
8. Q2是否保持独立；
9. 是否不存在独立系统预测头；
10. 缩小到论文整页宽度后是否可读；
11. 黑白打印是否仍可区分；
12. 原始C、D文件是否保持不变。

不要只给设计建议，实际完成两个Penpot版本、导出文件和比较说明。