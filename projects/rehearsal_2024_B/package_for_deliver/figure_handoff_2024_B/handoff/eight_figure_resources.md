# 2024_B 八图绘图资源交接

状态：**八图数据/结构规格就绪，图片尚未绘制**。本文件按仓库 `guide/figures_guide.md` 的八图证据链编号；原 `figure_handoff.md` 的 F1–F5 是候选统计图编号，不等同于论文图 1–8。正式排版顺序可调整，但必须保留 Evidence ID、源文件和图注边界。

每张图的机器规格与最终绘图数据位于 `results/verified/figure_data/fig01_*.json` 至 `fig08_*.json`；`figure_resource_manifest.json` 记录八份文件的 SHA-256。构建器为 `src/s6_eight_figure_resources.py`，只读取 G1/S3/G4 已核验的训练侧产物和既有 verified 文件；官方测试 CSV 读取、模型推理、实际绘图均为 0。

| 论文图 | 内容与推荐表现 | 规格文件 | Evidence ID | 与旧 F 编号的关系 |
|---|---|---|---|---|
| 图 1 | 三问总体技术路线；可编辑结构图 | `fig01_overall_workflow.json` | `E-FREEZE-001`, `E-Q3-CONFIG-001` | 新增 |
| 图 2 | S1 数据质量、A01 隔离与保留异常；同尺度面板 | `fig02_data_quality.json` | `E-DATA-001` | 新增 |
| 图 3 | Q3 物理基准＋残差 HGB＋非负约束＋AP 求和；可编辑结构图 | `fig03_q3_structure.json` | `E-Q3-CONFIG-001`, `E-FREEZE-001` | 新增 |
| 图 4 | Q3 训练侧第 0 次 grouped OOF 的 482 个系统真值–预测值点 | `fig04_q3_core_result.json` | `E-Q3-OOF-001`, `E-Q3-PIPE-001` | 核心结果；勿误作官方测试性能 |
| 图 5 | Q3 AP 真值–预测/残差，附 Q2 固定 17 类混淆矩阵 | `fig05_prediction_diagnostics.json` | `E-Q3-OOF-001`, `E-Q2-CONF-001` | 补齐诊断图；每次重复分别标注 |
| 图 6 | Q1 预测贡献、Q2 晋级阈值与 Q3 Baseline/统一/AP-count 对照；不同量纲分面 | `fig06_model_selection.json` | `E-Q1-001`, `E-Q1-IMP-001`, `E-Q2-001`, `E-Q3-PIPE-001`, `E-Q3-TRADE-001` | 旧 F1、F4、F5 的合并 |
| 图 7 | Q3 group-bootstrap 区间、primary/LOSO 与最差 held-out source | `fig07_robustness_uncertainty.json` | `E-Q3-UNC-001`, `E-Q3-LOSO-001`, `E-Q3-TRADE-001` | 旧 F2、F3 的合并 |
| 图 8 | 冻结模型的部署解释与风险处置；可编辑结构图 | `fig08_deployment_decision.json` | `E-FREEZE-001`, `E-Q2-001`, `E-Q3-CONFIG-001`, `E-RELEASE-001` | 新增；不是网络优化方案 |

## 重要口径

- 图 2 只使用训练侧 S1 审计；A01 隔离 2 行不等于删除所有异常。A02 缺失保留，A03 `(0,0)` 保留，A05 仅字段无效，A06 文件名不修改。
- 图 4/5 的逐点数据来自 S4 `PRIMARY`、`repeat=0`、`Q3-M1-HGB-UNIFIED` 的已验证 OOF。全局主指标采用三次重复汇总；不得把第 0 次画成独立测试或唯一成绩。
- 图 5 的 Q2 混淆矩阵有 3 个重复，每个重复覆盖同一 1,250 行；不得把 3,750 次预测称为 3,750 个独立样本。
- 图 6 中 Q1 特征组图只能称为 held-out predictive contribution / 条件关联，不能称因果效应。Q2 weighted HGB 增益 `0.0190017375 < 0.02`，图上不能四舍五入后误判晋级。Q3 `S=0.5503296083` 是 nested pipeline OOF，不是固定 residual-C3 的 OOF。
- 图 7 必须显示 unified 最差 held-out source `S=2.159764`，bootstrap 只描述固定 OOF group-resampling uncertainty，不是全流程重新拟合/重选参的不确定性。
- 图 8 仅说明已冻结模型如何产生 AP/系统结果与如何披露风险；赛题未求解网络参数优化，不能画出不存在的推荐配置或经济收益。官方测试输出无标签，不能写 accuracy 或误差。

## 绘制与回传合同

正式画图前按 `guide/09_plotting_protocol.md` 与项目负责人确认具体 skill。仓库八图指南优先建议图 1、3、8 使用 Scientific Illustrator 的可编辑矢量工作流；图 2、4、5、6、7 的数值点必须由适用绘图 skill 驱动脚本直接读取 `results/verified/figure_data/`，不手工摆点。当前只是资料准备，不代表已选定或调用该 skill。

每张图回传同名可编辑源/生成脚本、最终 PDF/SVG/PNG、图数据快照、图注、Evidence ID 与 SHA-256。图 1/3/8 的箭头与文字要逐项对照模型合同；图 4/5/6/7 的坐标、单位、样本数、误差条和尺度要逐项复核。八张正式图和论文源/PDF 均未回传，G6 仍为 NOT READY。
