# 2024 C 题论文配图交接包使用说明

## 1. 交接目标

本包用于完成论文的八张建议配图。包内数值数据全部复制自项目的 `results/verified/`，已经通过 G5 审核；不包含 `results/raw/`、原始赛题大附件、训练模型或附件三无真值预测表。

请先阅读：

1. `docs/figure_handoff.md`：每张图的目的、坐标、证据与红线；
2. `docs/technical_draft.md`：图在论文中的上下文；
3. `docs/result_registry.md`：E001–E015 的正式证据索引；
4. `docs/guides/09_plotting_protocol.md` 与 `docs/guides/figures_guide.md`：统一绘图规则。

## 2. 完整性检查

解压后在本目录运行：

```powershell
python verify_package.py
```

出现 `PACKAGE_VERIFY_PASS` 才能开始。逐文件来源、大小和 SHA-256 位于 `MANIFEST_SHA256.json`；ZIP 自身哈希位于 `ARCHIVE_SHA256.txt`。

## 3. 数据使用边界

- 只能使用本包 `data/verified/` 下的数值；
- 不得另行从项目 `results/raw/` 选择更好看的数字；
- 不得手工移动、补造或平滑真实数据点；
- 若需要新的数据切片，应编写脚本从包内 verified 文件生成，并保留脚本；
- 损耗统一为 W/m³，峰值磁通密度为 T，频率为 Hz，传输磁能代理 $fB_m$ 为 Hz·T；
- 附件二、附件三没有公开真值，不能生成测试准确率或测试误差图。

## 4. 工具和 Skill 门槛

正式绘图前需由仓库负责人确认具体 Skill：

- 图1、图3、图8：建议 `Scientific Illustrator`，必须保留可编辑矢量源；
- 图2、图4、图5、图6、图7：使用经确认的 Python scientific plotting Skill，程序直接读取包内 CSV/JSON；
- 当前仓库缺少 `guide/figure_color_guide.md`，所以最终配色必须另行获得负责人确认。确认前可做探索性草图，但不能标为论文最终图。

## 5. 八图任务卡

### 图1：总体技术路线

- 建议文件名：`fig1_overall_workflow`
- 输入：`docs/solution_plan.md`、`docs/result_freeze.md`、`docs/figure_handoff.md`
- 必须包含：数据审计、wave-v1、Q1–Q5、Q4→Q5、分组 OOF、raw→verified、84项核验、附件输出；
- 禁止：把五问画成互不相干模块；把附件二/三画成训练反馈。

### 图2：数据质量与样本结构

- 建议文件名：`fig2_data_quality`
- 数据目录：`data/verified/data/`
- 建议面板：材料样本量；温度/波形分布；质量检查 PASS/WARN；频率、损耗、$B_m$ 范围；
- 必须标注：附件一 12,400 条、附件二 80 条、附件三 400 条；
- 禁止：把诊断性 IQR 数量写成已删除样本；将轻微频率越界记录静默删掉。

### 图3：模型变量与信息依赖

- 建议文件名：`fig3_variable_structure`
- 输入：`docs/model_contracts/`、`docs/model_freeze.json`
- 必须表达：波形→wave-v1→Q1；材料1正弦子集→Q2；控制 $f,B_m$ 后的 Q3 调整关联；18特征→Q4；Q4 严格 OOF+$fB_m$→Q5；
- 禁止：用因果箭头表示 Q3；把附件三反馈到模型选择。

### 图4：Q5 Pareto 核心结果

- 建议文件名：`fig4_primary_result`
- 数据：
  - `data/verified/q5/final_oof_pareto.csv`
  - `data/verified/q5/final_full_fit_reference_pareto.csv`
  - `data/verified/q5/representative_conditions.json`
  - `data/verified/q5/heldout_fold_region_support.csv`
- 横轴：$fB_m$（Hz·T，越大越好）；
- 纵轴：严格 OOF 损耗（W/m³，越小越好，建议对数轴）；
- 标记：118个 OOF Pareto 点、27个折支持区域、最小损耗端、临时膝点、最大能量端；
- 强制图注：`Jaccard=0.39535<0.50`，三个代表点都不是唯一最优解。
- Evidence：E012、E014。

### 图5：Q4 分组 OOF 预测与残差

- 建议文件名：`fig5_prediction_residuals`
- 数据：
  - `data/verified/q4/final_oof_predictions.csv`
  - `data/verified/q4/hgb_subgroup_metrics.csv`
  - `data/verified/q4/stress_subset_metrics.csv`
- 建议面板：真实—预测双对数散点与 $y=x$；log1p 残差—预测；材料/温度/波形子组 RMSLE；
- 标注：分组 OOF，$n=12,400$，RMSLE=0.070941；
- 禁止：把附件三 400 条无真值预测加入真实—预测散点。
- Evidence：E008–E010。

### 图6：Baseline、主模型与消融

- 建议文件名：`fig6_baseline_ablation`
- 数据：
  - `data/verified/q2/quadratic_temperature_metrics.json`
  - `data/verified/q4/hgb_metrics.json`
  - `data/verified/q4/ablation_metrics.csv`
- Q2：Steinmetz 0.360678 → 温度修正 0.202567；
- Q4：Ridge 0.200097 → 48特征 HGB 0.076397 → 18特征 HGB 0.070941；
- 纵轴：RMSLE，越低越好；
- 禁止：没有重复层统计时伪造误差棒。可以使用同折连线，或明确标注固定分组 OOF 汇总。
- Evidence：E004、E008。

### 图7：温度、外推与稳定性边界

- 建议文件名：`fig7_sensitivity_robustness`
- 数据：
  - `data/verified/q2/quadratic_temperature_by_temperature.csv`
  - `data/verified/q2/leave_one_temperature_comparison.csv`
  - `data/verified/q4/leave_one_level_out_metrics.csv`
  - `data/verified/q5/bootstrap_region_stability.csv`
  - `data/verified/q5/sensitivity_scenarios.csv`
- 建议面板：Q2 各温度比较；Q4 留一材料/温度压力；Q5 区域稳定性；
- 强制标注：Q2 的50°C局部劣化；Q4最大 LOMO=0.37982、LOTO=0.57496；Q5 实际 Jaccard=0.39535、门槛0.50；
- Evidence：E005、E010、E013、E014。

### 图8：工程解释与决策边界

- 建议文件名：`fig8_decision_scenario`
- 输入：`docs/writing_handoff.md`、`data/verified/q5/representative_conditions.json`、`data/verified/q5/bootstrap_region_stability.csv`
- 流程：用户偏好/工程约束→选择 Pareto 区段→检查材料、温度、波形、频率、$B_m$→复核热、饱和、成本等题外约束→保留备选；
- 禁止：把临时膝点或最大能量端画成唯一推荐；不得省略真实工程约束缺失。
- Evidence：E012–E014。

## 6. 统一视觉与版式要求

- 一张图只回答一个核心问题；
- 统一中文字体、英文字体、线宽、标记尺寸和编号格式；
- 数据、模型、验证、风险采用固定语义配色；
- 同类比较必须使用一致尺度；不截断坐标轴制造夸张差异；
- 图题、坐标轴、单位、图例、样本量和验证口径齐全；
- 损耗跨度大时优先采用对数轴，并在图注中明确；
- Q3 关系箭头必须注明“调整后关联”；
- Q5 图必须出现“唯一推荐未授权”；
- 缩放到论文单栏/双栏实际尺寸后，正文和图例仍应清晰可读。

## 7. 每张图的交付物

队友完成后请按以下结构返回：

```text
figures/
├── scripts/    # 数值图完整脚本及环境说明
├── data/       # 从本包数据自动导出的绘图切片
├── sources/    # drawio/AI/PPTX 等可编辑源
└── final/      # PDF 或 SVG + 宽度至少 2000 px PNG
```

每张图还需附一条登记信息：图号、目的、数据文件、脚本、横纵轴与单位、图例、Evidence ID、导出文件、Skill 名称及版本。

## 8. 返回前自检

- [ ] 运行脚本可从本包数据重生成数值图；
- [ ] 没有使用 `results/raw/` 或未登记数字；
- [ ] 没有把附件二/三预测称为测试精度；
- [ ] 没有把 Q3 画成因果结论；
- [ ] 没有把 Q5 代表点标为唯一最优；
- [ ] 图4和图7正确展示 `0.39535<0.50`；
- [ ] 所有轴、单位、图例和验证口径完整；
- [ ] 可编辑源、脚本、矢量图和 PNG 均已提供；
- [ ] 最终配色已获负责人确认。
