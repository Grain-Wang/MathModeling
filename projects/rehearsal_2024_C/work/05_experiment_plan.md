# S2 实验计划

- Project: `rehearsal_2024_C`
- Plan version: `s2-v1`
- Global seed: `20240920`
- Bootstrap seed: `20240921`
- Optimization stability seed: `20240922`
- Environment: `math_modeling`, CPU-first
- Gate boundary: G2 PASS 前不执行下列模型拟合实验

## 1. 实验原则

1. 先完成全部 S3 Baseline，再决定是否进入任何 S4 候选。
2. 所有模型共用 `wave-v1`、`group-v1` 和同一行级折文件。
3. 所有学习型预处理在折内拟合；不得先对全数据缩放、筛选或降维。
4. 附件二、三只在模型与预处理冻结后各预测一次，不属于验证集。
5. 每次运行记录 ID、Git SHA、输入/配置 SHA、命令、环境版本、随机种子、起止时间、退出码和输出哈希。
6. 原始输出进入 `results/raw/`；G5 前不写 `results/verified/`。
7. 失败实验保留配置、错误和已产生的诊断，不用新 ID 覆盖。

## 2. 固定验证设计

### 外层与内层

- Q1：外层 `StratifiedGroupKFold`，组为 `near_shape_group`，目标 5 折；压力测试留一材料。
- Q2/Q3/Q4：外层 `GroupKFold`，组为 `condition_group`，目标 5 折；Q2 另做四次留一温度。
- 内层：需要调参的 Q1/Q4 候选只在外层训练部分做 3 折分组验证。
- 折覆盖失败按 5→4→3 降低；3 折仍失败则停止，不退回普通随机行切分。

### 指标冻结

| 问题 | 主指标/判据 | 辅助证据 |
|---|---|---|
| Q1 | Macro-F1 | Accuracy、Balanced Accuracy、逐类 Recall/F1、混淆矩阵 |
| Q2 | RMSLE | MAE、RMSE、MAPE、MdAPE、分温度残差 |
| Q3 | 调整后效应区间和 OOF log-RMSE | 因素损失增量、交互增益、折/Bootstrap 稳定性 |
| Q4 | RMSLE | MAE、RMSE、MAPE、MdAPE、$R^2$、子组与外推压力 |
| Q5 | 严格 OOF Pareto 非支配性与验证折区域支持 | OOF/full 一致性、500 次工况组 Bootstrap、观测损耗 Pareto 诊断、口径敏感性 |

回归指标统一按共享合同计算：RMSLE 使用自然对数 `log1p`，MAPE 分母下限为 `1 W/m³`，$R^2$ 在原始 W/m³ 尺度。任何主指标变更都必须先写决策日志并重新提交相应 Gate，不能在看到结果后改变。

## 3. S3 Baseline 实验队列

| Experiment ID | 目的与方法 | 输入 | 计划命令 | 主要输出 | 验收/失败 | CPU 预算 |
|---|---|---|---|---|---|---:|
| EXP-S3-DATA-001 | 构建 `wave-v1`、指纹、近形状/工况组和固定折 | 附件一；S1 profile；冻结配置 | `python src/build_features.py --config experiments/s2_frozen_config.json` | feature table、schema、fold assignments、run manifest | 12,400 行；无非有限；同组同折；重跑哈希一致 | 20 min |
| EXP-Q1-BASE-001 | 逻辑回归形状分类 Baseline | feature table；Q1 folds | `python src/run_q1.py --model logistic --stage baseline --config ...` | OOF 概率、类别、指标、混淆矩阵 | OOF 覆盖全部行、三类编码正确；否则阻断 Q1 | 15 min |
| EXP-Q2-BASE-001 | 传统 Steinmetz 方程 | 材料1正弦波；Q2 folds | `python src/run_q2.py --model steinmetz --stage baseline --config ...` | 参数、OOF 预测、总体/分温度误差 | 正参数输入、有限预测、同折比较基础成立 | 10 min |
| EXP-Q3-DESC-001 | 因素与联合工况描述统计 | 附件一 feature table | `python src/run_q3.py --model descriptive --stage baseline --config ...` | 48 格分布、共同支持诊断 | 48 格完整；明确不可比区域 | 5 min |
| EXP-Q3-BASE-001 | 控制 $f/B_m$ 的加性效应模型 | feature table；Q3 folds | `python src/run_q3.py --model additive --stage baseline --config ...` | OOF 预测、主效应初值、残差 | 设计可识别、OOF 有限；否则回退分层描述 | 15 min |
| EXP-Q4-NULL-001 | 全局/分组中位数损耗参照 | feature table；Q4 folds | `python src/run_q4.py --model median --stage baseline --config ...` | OOF 预测和指标 | 为所有候选提供最低参照 | 5 min |
| EXP-Q4-BASE-001 | Ridge 对数回归 Baseline | 完整 `wave-v1`；Q4 folds | `python src/run_q4.py --model ridge --stage baseline --config ...` | OOF 预测、总体/子组指标 | 必须优于至少一个中位数参照；否则先修数据/特征 | 30 min |
| EXP-Q5-BASE-001 | 用 Q4 Baseline 的严格 OOF 分数枚举实测点 Pareto | Q4 Baseline 完整 OOF；附件一候选 | `python src/run_q5.py --mode oof-observed-pareto --stage baseline --config ...` | 可复算候选索引、OOF Pareto、端点、膝点、full-fit 参考表 | 每点 OOF 模型未见其 `condition_group`；候选身份闭合；无被支配输出点 | 10 min |

S3 完成条件是上述 8 个实验都有可重现输出，Q1–Q5 全部形成最小闭环；某个 Baseline 失败时优先修复它，不跳到主模型掩盖问题。

## 4. S4 候选、比较与稳健性队列

| Experiment ID | 目的与方法 | 进入条件 | 主要比较/输出 | 采用或回退规则 | CPU 预算 |
|---|---|---|---|---|---:|
| EXP-Q1-MAIN-001 | HistGradientBoosting 分类 | Q1 Baseline 完整 | 同折 OOF 候选表 | Macro-F1 提升为正且类别 Recall 降幅≤0.02，否则 Logistic | 30 min |
| EXP-Q1-CHAL-001 | RandomForest 分类挑战者 | 主候选仍有明显残差结构且有预算 | 同折 OOF 候选表 | 只保留一个胜者，不堆叠 | 30 min |
| EXP-Q1-ABL-001 | 形状-only、辅助字段、特征组和相位/幅值不变性 | Q1 候选完成 | 消融与不变性表 | 代理字段提升但压力测试下降则拒绝 | 20 min |
| EXP-Q2-MAIN-001 | 二次乘性温度修正 | Q2 Baseline 完整 | 同折参数、OOF、分温度误差 | 总体 RMSLE 降且≥3/4 温度不劣化 | 10 min |
| EXP-Q2-EXT-001 | 预定义温度×log(f/Bm) 交互 | 主修正触发失败条件 | 有限两交互比较 | 仍无稳定改善则停止扩张 | 10 min |
| EXP-Q2-SENS-001 | 峰值口径、重复和留一温度 | Q2 主比较完成 | 敏感性和外推表 | 结论反转则双口径报告 | 15 min |
| EXP-Q3-INT-001 | 三组两两交互模型 | 加性 Baseline 可识别 | 交互模型 OOF 和增量 | OOF 劣化则回退加性 |
| EXP-Q3-BOOT-001 | 500 次工况组 Bootstrap | Q3 胜者冻结 | 主效应、交互、影响度和最低组合区间 | 方向不稳则缩小结论 | 60 min |
| EXP-Q3-SENS-001 | 共同支持、峰值口径和重复敏感性 | Bootstrap 完成 | 结论稳定性表 | 只保留共同稳定结论 | 20 min |
| EXP-Q4-MAIN-001 | HistGradientBoosting 回归 | Q4 Ridge 优于参照、S3 全题闭环 | 嵌套 OOF 候选比较 | RMSLE 相对改善≥2%，子组恶化≤10% | 90 min |
| EXP-Q4-CHAL-001 | RandomForest 回归挑战者 | 主候选未稳定胜出或互补诊断有依据 | 同折 OOF 候选比较 | 只保留一个胜者，不集成 | 60 min |
| EXP-Q4-ABL-001 | 工况-only/幅值/完整波形特征消融 | Q4 候选完成 | OOF 消融表 | 无增益的特征组删除 | 30 min |
| EXP-Q4-STRESS-001 | 留一材料/温度、边界和尾部压力 | Q4 胜者暂定 | schema 已知未见水平、泛化压力和校准；主要子组 `n≥100` 且覆盖≥3折 | 崩溃则限制适用范围或回退 | 45 min |
| EXP-Q5-ROB-001 | 严格 OOF 的折级区域与簇 Bootstrap 稳定性 | Q4 胜者满足最低能力 | 各验证折区域、500 次重采样、双 Pareto/P90 冲突诊断 | 未达折级、Bootstrap 或冲突门槛则不给唯一推荐 | 20 min |
| EXP-Q5-SENS-001 | 频率域、峰值口径和重复敏感性 | Q5 Baseline 有效 | 三类敏感性表 | 条件反转则只报稳定区域 | 15 min |

`EXP-Q3-INT-001` 预算为 20 分钟。所有时间是硬上限；超时保存状态并标记失败，不自动扩大资源。

## 5. 实验依赖与顺序

```text
EXP-S3-DATA-001
├─ Q1-BASE ──> Q1-MAIN/CHAL ──> Q1-ABL
├─ Q2-BASE ──> Q2-MAIN ──> Q2-EXT(条件触发) ──> Q2-SENS
├─ Q3-DESC ──> Q3-BASE ──> Q3-INT ──> Q3-BOOT/SENS
└─ Q4-NULL ──> Q4-BASE ──> Q5-BASE
                  └─ Q4-MAIN/CHAL ──> Q4-ABL/STRESS ──> Q5-ROB/SENS
```

Q5 只能消费一个已冻结的 Q4 接口；Q4 模型改变后，旧 Q5 结果自动失效并须重新计算。

## 6. 参数搜索纪律

- 搜索空间只使用各模型合同 `Parameters` 表中的有限集合，并在 `experiments/s2_frozen_config.json` 保存同一网格、抽样上限和规范化合同 SHA-256；实现时配置 JSON 为机器读取的单一事实源。
- 候选多时用 `ParameterSampler` 固定抽样数量和 seed，不在运行后追加“看起来可能更好”的点。
- 外层折只用于最终候选比较；内层选择完成后不得针对外层坏折继续调参。
- Q1/Q4 的胜者由主指标、子组约束、运行时和简洁性共同决定，不按单一最好折选择。
- 不选择随机种子；随机性检查使用预先给出的三个种子 `{20240920,20240921,20240922}`，全部保留。

## 7. 输出与运行清单

每个实验目录至少包含：

```text
config.json
run_manifest.json
metrics.json
oof_predictions.csv（预测任务）
stdout.log
```

`run_manifest.json` 最低字段：

| Field | Requirement |
|---|---|
| `experiment_id` | 与日志一致且唯一 |
| `git_commit` | 40 位完整 SHA |
| `input_hashes` | 原始/特征/折文件 SHA-256 |
| `command` | 可复制执行的完整相对路径命令 |
| `environment` | Conda 名、Python 与核心包版本 |
| `seed` | 所有随机源 |
| `started_at/ended_at/runtime_seconds` | Asia/Shanghai 与秒 |
| `exit_code/status` | PASS/FAIL/INVALID |
| `output_hashes` | 正式输出文件 SHA-256 |

逐样本预测不得只存在于图或 notebook；任何汇总指标都必须能由 OOF CSV 独立重算。

## 8. 测试集单次释放流程

只有以下条件全部满足才允许预测附件二或三：

1. 对应胜者、预处理、特征 schema、类别编码/反变换和参数已冻结；
2. 模型选择日志已关闭，后续不得因测试输入结果改变模型；
3. 全量重拟合命令和模型哈希已记录；
4. 输出验证脚本已先用模拟表测试 ID、行数、范围和舍入；
5. 复制附件四到 `results/raw/`，核验副本初始哈希与原件相同；
6. 预测一次并记录，若只发生纯格式错误可修复写出代码，但不得借机改模型。

附件二输出检查：80 行、ID 1–80、类别值只为 1/2/3、三类计数和为 80。附件三输出检查：400 行、ID 1–400、值有限且正、保留 1 位小数。两组指定 ID 必须从同一冻结 CSV 自动抽取。

## 9. 结果比较与不确定性

- 模型指标差用相同 OOF 行的成对损失；
- Bootstrap 以 `condition_group` 为重采样单位，500 次并记录有效/失败次数；
- 报告均值、中位数、折间标准差和 95% 区间，不只报最好值；
- 子组样本太少时不作强比较，明确样本量；
- IQR 高值、频率边界和完全重复记录均做保留/替代敏感性，不自动删除；
- Q5 报告 Pareto 集而非只给膝点，膝点规则和端点同时公开。

### 9.1 Q5 严格 OOF 与拒绝协议

1. `observed_candidate_set.csv` 必须保存 `row_id`、来源文件哈希/工作表/Excel 行、波形 SHA-256、全部 Q4 输入特征、`condition_group`、`oof_fold` 和模型/配置哈希；抽象五元组仅作汇总列。
2. 主 Pareto 的损耗列只能是该候选唯一留出模型产生的 `y_pred_oof`；全量模型只生成参考 Pareto，不参与折外计票。
3. 每折只在本折验证候选中构造 Pareto；按 `q5-region-v1` 聚合，稳定区域须出现在至少 `ceil(0.6*K)` 个折的验证 Pareto 中。
4. 在严格 OOF 候选表上以 `condition_group` 为单位做 500 次 Bootstrap，seed `20240922`。区域至少有 400 次有效出现才评价，条件 Pareto 入选率须 `≥0.50`；报告区间名为“95% condition-group cluster bootstrap percentile interval”。
5. 单点还须同时属于 OOF/full-fit Pareto，且 OOF 绝对对数残差和 full/OOF 绝对对数差均不超过材料×波形参照组 P90；参照组 `n<100` 时回退全局。
6. 另做模型预测 Pareto 与观测损耗 Pareto 的诊断比较。观测损耗不替代优化目标，但明显冲突会触发降级。
7. 任一门槛失败时只报告稳定区域、因素区间和两个端点；5 个折模型的范围只能称“重拟合扰动范围”，不能称 95% 置信区间。

## 10. 阶段停止条件

立即停止相应路线并记录：

- 原始哈希改变、schema 不符或折泄漏；
- 输出不可复算、OOF 覆盖不全或非有限；
- 任何附件二/三参与模型选择；
- 单实验超过合同预算；
- 主候选不满足增益/子组阈值；
- Q3 只能得到不稳定关联却被写成因果；
- Q5 候选身份不能完整复算、OOF 模型见过其 `condition_group`、双 Pareto/P90/折级/Bootstrap 任一门槛失败却仍输出唯一推荐，或 Q4 在该区域失效。

总时间不足时，停止候选扩张，优先保留：五问 Baseline 闭环、合法验证、附件输出一致性、结果核验和论文交接。

## 11. S3 启动条件

本计划、总体方案和五份模型合同经 G2 PASS 后，才创建/实现上述 `src/` 入口并运行 S3 Baseline。当前文档中的命令是冻结的预期接口，不代表脚本或结果已经存在。
