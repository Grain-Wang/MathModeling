# Figure Handoff — 论文配图交接

## 1. Handoff Status

- 数据交接：`READY`
- 正式绘图：`PENDING SKILL CONFIRMATION`
- 唯一允许的数据根目录：`results/verified/`
- 证据索引：`results/verified/result_registry.md`
- 来源核验：`results/verified/provenance.json`

本文件只交接已核验数据、图意、坐标、单位和禁止表述，不直接生成图片。

## 2. Mandatory Skill Gate

`guide/09_plotting_protocol.md` 要求每张图片必须明确使用某个 Skill，并在绘图前由用户确认。当前：

1. `.agents/skills/` 为空；
2. `guide/figures_guide.md` 指定图1、图3、图8应使用 `scientific-illustrator@scientific-illustrator-tools`，但该插件/Skill 尚未安装；
3. `guide/09_plotting_protocol.md` 引用的 `guide/figure_color_guide.md` 不存在；
4. 因此本轮不得绕过 Skill 直接画正式图片。

建议确认语句：

> 图1、图3、图8使用 Scientific Illustrator，因为它能保留流程、结构和决策场景的可编辑矢量源；图2、图4、图5、图6、图7使用待安装/指定的 Python scientific plotting Skill，因为这些图必须从 verified 数值自动生成，不能手工摆点。

用户确认并补齐 Skill 前，只允许队友制作明确标为“探索性”的草图，不得放入最终论文。

## 3. Common Plot Rules

- 只能读取 `results/verified/`，不得从 `results/raw/` 挑数；
- 坐标轴、单位、样本量、验证口径必须写清；
- 损耗跨度大时优先使用对数坐标，并在图注说明；
- OOF 必须标为“分组 OOF”，附件三必须标为“无真值冻结预测”；
- 不得把 Q3 关联画成因果箭头；
- 不得把 Q5 临时膝点或任一端点标成“唯一最优”；
- Q5 图中必须显式标注 `Jaccard=0.39535<0.50` 和“唯一推荐未授权”；
- 配色最终版须等待缺失的 `guide/figure_color_guide.md`，不得自行宣称符合仓库配色规范；
- 每图保留可编辑源、PDF/SVG 和至少 2000 px PNG。

## 4. Proposed Eight-Figure Evidence Chain

### Fig. 1 全题技术路线

- 目的：说明附件一审计如何流向 Q1–Q5、Q4 如何供给 Q5，以及 OOF→验证→冻结→附件输出的闭环；
- Skill：`scientific-illustrator@scientific-illustrator-tools`（待安装与确认）；
- 输入文档：`work/04_solution_plan.md`、`work/10_result_freeze.md`；
- 关键节点：数据审计、wave-v1、Q1分类、Q2温度修正、Q3调整关联、Q4 HGB、Q5 OOF Pareto、84项核验；
- 标题建议：`数据驱动磁芯损耗建模与证据冻结总体流程`；
- 禁止：把五问画成彼此无关模块；漏画 Q4→Q5 和 raw→verified Gate。

### Fig. 2 数据质量与样本结构

- 目的：证明四材料12,400条训练记录、80/400条测试记录及154项审计结果；
- Skill：待指定的 Python scientific plotting Skill；
- 数据：
  - `results/verified/data/dataset_summary.csv`
  - `results/verified/data/quality_checks.csv`
  - `results/verified/data/numeric_ranges.csv`
  - `results/verified/data/categorical_counts.csv`
- 面板建议：
  - (a) 四材料训练样本量，横轴材料、纵轴样本数；
  - (b) 温度/波形类别分布；
  - (c) 154项检查按 PASS/WARN 与严重度汇总；
  - (d) 频率、损耗、`B_m` 的范围对照；
- Evidence：数据审计来源已由 S5 provenance 核验；
- 禁止：把频率轻微题面越界样本当异常删除；把诊断性 IQR 数量称为已删除样本。

### Fig. 3 模型变量与信息依赖

- 目的：区分输入、状态、模型输出和决策域，强调测试集不参与选择；
- Skill：`scientific-illustrator@scientific-illustrator-tools`（待安装与确认）；
- 输入：五份 `work/models/q*_model_contract.md` 与 `results/verified/model_freeze.json`；
- 必须画出：
  - 波形→wave-v1→Q1；
  - 材料1/正弦子集→Q2；
  - `T,w,m` 与 `f,B_m` 控制→Q3调整关联；
  - 18特征+三类别变量→Q4；
  - Q4严格OOF+`fB_m`→Q5；
- 禁止：从 Q3 变量指向损耗的箭头标为已证因果；把附件三反馈到模型训练。

### Fig. 4 Q5 双目标主结果

- 目的：直接展示数据支持域中的损耗—传输磁能权衡，以及为什么不提供唯一推荐；
- Skill：待指定的 Python scientific plotting Skill；
- 数据：
  - `results/verified/q5/final_oof_pareto.csv`
  - `results/verified/q5/final_full_fit_reference_pareto.csv`
  - `results/verified/q5/representative_conditions.json`
  - `results/verified/q5/heldout_fold_region_support.csv`
- 横轴：传输磁能代理 `fB_m`（Hz·T，越大越好）；
- 纵轴：严格 OOF 预测损耗（W/m³，越小越好，建议log尺度）；
- 标记：118个 OOF Pareto 点、最小损耗端点、最大能量端点、临时膝点；用不同轮廓区分折支持区域；
- Evidence：E012、E014；
- 标题建议：`观测联合可行域中的磁芯损耗—传输磁能 Pareto 权衡`；
- 强制图注：临时膝点只由几何规则选取，不代表用户偏好；Jaccard门槛失败，禁止唯一推荐。

### Fig. 5 Q4 分组 OOF 预测与残差

- 目的：同时展示插值验证精度与系统误差结构；
- Skill：待指定的 Python scientific plotting Skill；
- 数据：
  - `results/verified/q4/final_oof_predictions.csv`
  - `results/verified/q4/hgb_subgroup_metrics.csv`
  - `results/verified/q4/stress_subset_metrics.csv`
- 面板：
  - (a) 真实损耗—OOF预测散点，双对数轴与 `y=x`；
  - (b) `log1p` 残差—预测值；
  - (c) 材料/温度/波形子组 RMSLE；
- 指标：n=12,400，RMSLE=0.070941；
- Evidence：E008–E010；
- 禁止：将附件三400条无真值预测加入真实—预测散点；把留一水平压力称为主精度。

### Fig. 6 Baseline、主模型与消融

- 目的：证明复杂度增加有收益，并说明删除无增益 shape 特征；
- Skill：待指定的 Python scientific plotting Skill；
- 数据：
  - `results/verified/q4/hgb_metrics.json`
  - `results/verified/q4/ablation_metrics.csv`
  - `results/verified/q2/quadratic_temperature_metrics.json`
- 面板：
  - (a) Q2 Steinmetz 0.360678 vs 温度修正 0.202567；
  - (b) Q4 Ridge 0.200097、完整48特征HGB 0.076397、最终18特征HGB 0.070941；
- 纵轴：RMSLE（越低越好）；
- Evidence：E004、E008；
- 误差表达：若没有可直接作为误差棒的重复层统计，不得伪造误差棒；可以改用同折连线或注明“同一固定分组OOF汇总”。

### Fig. 7 温度、外推与稳定性边界

- 目的：展示主结论在温度、峰值口径、频率边界和Bootstrap下的稳定与失败区域；
- Skill：待指定的 Python scientific plotting Skill；
- 数据：
  - `results/verified/q2/quadratic_temperature_by_temperature.csv`
  - `results/verified/q2/leave_one_temperature_comparison.csv`
  - `results/verified/q4/leave_one_level_out_metrics.csv`
  - `results/verified/q5/bootstrap_region_stability.csv`
  - `results/verified/q5/sensitivity_scenarios.csv`
- 面板：
  - (a) Q2 各温度 Baseline/Candidate RMSLE；
  - (b) Q4 留一材料与留一温度 RMSLE；
  - (c) Q5 区域条件 Pareto 入选率和有效重采样次数；
- Evidence：E005、E010、E013、E014；
- 强制标注：Q2 50°C局部劣化；Q4最大 LOMO/LOTO；Q5主门槛0.50及实际0.39535。

### Fig. 8 工程解释与决策边界

- 目的：把模型结果转化为“可选权衡区域+核验流程+不适用边界”，而不是伪造单点方案；
- Skill：`scientific-illustrator@scientific-illustrator-tools`（待安装与确认）；
- 输入：
  - `results/verified/q5/representative_conditions.json`
  - `results/verified/q5/bootstrap_region_stability.csv`
  - `work/handoff/writing_handoff.md`
- 结构：用户偏好/工程约束→选择 Pareto 区段→检查材料/温度/波形/频率/`B_m`→复核热/饱和/成本等题外约束→保留备选；
- Evidence：E012–E014；
- 禁止：把材料1、70°C、三角波的最大能量端点包装成唯一推荐；省略真实工程约束缺失。

## 5. File Delivery Convention

本项目按仓库现有结构保存：

```text
figures/
├── data/       # 可选：从 verified 自动导出的只读绘图切片
├── scripts/    # 可复现绘图代码
├── sources/    # drawio 等可编辑源
└── final/      # PDF/SVG/PNG
```

建议文件名沿用 `guide/figures_guide.md`：

`fig1_overall_workflow` 至 `fig8_decision_scenario`。

## 6. Pre-Plot Confirmation Required

开始正式绘图前必须由用户确认：

1. 是否安装并使用 Scientific Illustrator 绘制图1、图3、图8；
2. 数值图使用哪个具体 Python plotting Skill；
3. 是否先补齐 `guide/figure_color_guide.md`，或由用户书面批准临时配色方案。
