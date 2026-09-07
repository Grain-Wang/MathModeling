# S3 全题 Baseline 报告

## 1. 结论与运行边界

- 阶段：S3 — 全题 Baseline 闭环
- 实现提交：`0d36ef8c16f3214b16d8580333f2925aaff45191`
- 冻结配置：`experiments/s2_frozen_config.json`（`plan_version=s2-r2-v1`）
- 环境：`math_modeling`，Python 3.11.11，scikit-learn 1.7.1
- 总体结论：G2 批准的 8 个数据/Baseline 实验均有真实输出，Q1–Q5 数据流闭环，独立复算检查 PASS；当前仅提交 G3，不自行进入 S4。

本阶段只使用附件一建立特征、拟合和验证模型。题目正文及附件二至四只在启动时核验文件 SHA-256，附件二、三没有被加载到模型、选参或 Q5 阈值流程中，也没有生成测试集预测。全部新结果仍位于 `results/raw/`，`results/verified/` 未写入。

## 2. 复现命令

在 `projects/rehearsal_2024_C/` 下运行：

```powershell
conda run --no-capture-output -n math_modeling python src/run_s3_baselines.py --config experiments/s2_frozen_config.json --verify-data-rebuild
conda run --no-capture-output -n math_modeling python src/verify_s3_outputs.py --config experiments/s2_frozen_config.json
```

第一条命令按依赖顺序运行 8 个实验，并将特征构建重复两次。第二次构建的 feature table、fold assignments 和 schema 与第一次字节级 SHA-256 一致。每个实验的配置副本、命令、种子、起止时间、环境版本、输入/输出哈希和退出码均保存在 `results/raw/baseline/<EXP-ID>/`。

`stdout.log` 采用追加记录，保留了提交前诊断运行；每份 `run_manifest.json` 的 `started_at`/`ended_at` 对应日志中的最后一段正式运行，历史段没有删除。

## 3. 共享数据与验证结果

| 项目 | 实际结果 |
|---|---:|
| 训练记录 | 12,400 |
| wave-v1 数值特征 | 48 |
| Q1 shape-only 特征 | 30 |
| `condition_group` 数量 | 4,323 |
| Q1 / 回归外层折 | 5 / 5 |
| 精确重复额外行 | 1 |
| 同组跨折 | 0 |
| feature table SHA-256 | `52E5B68F…774B2` |
| fold assignments SHA-256 | `8748FF0D…767BA` |
| 两次重建哈希 | MATCH |

共享输出：`results/raw/s3/data/feature_table.csv`、`results/raw/s3/data/feature_schema.json`、`results/raw/s3/folds/fold_assignments.csv`。

## 4. 五问 Baseline 闭环

| 问题 / 实验 | 方法 | 真实输出与核心指标 | 阶段判断 |
|---|---|---|---|
| Q1 / `EXP-Q1-BASE-001` | shape-only 多项逻辑回归，外层 StratifiedGroup 5 折、训练折内 3 折选参 | 12,400 条 OOF；Macro-F1、Accuracy、Balanced Accuracy 均为 1.000 | 跑通；需在 S4 做相位/幅值不变性与消融，避免把高度可分结果直接外推为未知测试集性能 |
| Q2 / `EXP-Q2-BASE-001` | 材料1正弦波传统 Steinmetz 对数线性回归 | 1,067 条 OOF；RMSLE 0.3607，MAPE 32.53%，原尺度 R² 0.9412 | 跑通；留一温度 RMSLE 为 0.1344–0.6262，说明温度修正是首要改进点 |
| Q3 / `EXP-Q3-DESC-001` | 48 个温度×波形×材料单元描述统计 | 48 格全部非空；共同矩形支持 1,766 行（14.24%） | 跑通；描述中位数只解释为未调整关联 |
| Q3 / `EXP-Q3-BASE-001` | 控制 `log(f)`/`log(Bm)` 样条的效应编码加性 Ridge | 12,400 条 OOF；log-RMSE 0.3434，原尺度 R² 0.6036；Gram 条件数最大 183.45 | 跑通；只解释为调整后关联，S4 再比较预定义两两交互与组 Bootstrap |
| Q4 / `EXP-Q4-NULL-001` | 训练折全局/材料×波形×温度中位数 | RMSLE 1.9002 / 1.8311 | 跑通并提供最低参照 |
| Q4 / `EXP-Q4-BASE-001` | 48 数值特征+3 类别字段的对数 Ridge，外层 Group 5 折、训练折内 3 折选参 | 12,400 条 OOF；RMSLE 0.2001，MAPE 15.85%，原尺度 R² 0.9507；优于两个中位数参照 | 跑通；最弱主要子组为低 `Bm` 四分位，RMSLE 0.2575 |
| Q5 / `EXP-Q5-BASE-001` | Q4 严格 OOF 损耗与 `f×Bm` 的实测工况 Pareto | 12,237→12,236 候选；105 个 OOF Pareto 点、109 个 full-fit 参考点、130 个观测损耗诊断点；22/702 区域达到至少 3 折支持 | 跑通基础闭环；OOF/观测区域 Jaccard=0.0962<0.50，故唯一推荐资格为 0，S4 稳健性检查待完成 |

## 5. 前后数据流

```text
附件一（只读）
  -> wave-v1 特征、身份哈希、固定分组折
  -> Q1 波形分类 OOF
  -> Q2 Steinmetz OOF / Q3 描述与加性 OOF
  -> Q4 中位数参照与 Ridge 严格 OOF + full-fit 参考
  -> Q5 实测工况候选身份 + 严格 OOF Pareto + 折级区域/冲突诊断
```

Q5 的主损耗分数只取候选所属外层验证折的 `y_pred_oof`。`results/raw/s3/q5/candidate_oof_lineage.csv` 对 12,236 个候选逐行记录 `condition_group`、外层折、模型 ID 和排除断言；所有断言为真。full-fit 预测仅用于参考 Pareto 和 full/OOF 差异诊断。

## 6. G2 Round 2 实现检查闭环

1. 候选级 OOF 谱系：12,236/12,236 PASS，另有 5 条折级训练/验证组哈希断言。
2. 跨折可比性：提交每折 Pareto、`ceil(0.6×5)=3` 折区域支持、full/OOF P90 差异及观测损耗 Pareto/Jaccard。
3. Bootstrap 边界：S3 未执行 500 次重采样，也未声称完成；S4 若复用固定 OOF 表，只解释为交叉拟合候选表的工况组重采样稳定性，不解释为完整模型参数不确定性。
4. 退化边界：代码与合成测试覆盖 Pareto 零范围、OOF/full 空交、Jaccard 双空集和重复四分位边界。
5. 合同哈希：每次实验启动均实际重算 8 份 `sha256_utf8_lf` 合同哈希；Q5 指标及独立验证报告保留实际值。

## 7. 输出定位与基本验证

- Q1：`results/raw/s3/q1/`（OOF 概率/类别、混淆矩阵、分组指标、内层选择、模型）
- Q2：`results/raw/s3/q2/`（参数、OOF、分温度指标、留一温度压力测试、模型）
- Q3：`results/raw/s3/q3/`（48 格描述、共同支持、OOF、系数、谱系、模型）
- Q4：`results/raw/s3/q4/`（两种中位数参照、Ridge OOF/full-fit、子组、谱系、模型）
- Q5：`results/raw/s3/q5/`（候选索引、Q4 特征快照、三类 Pareto、折级区域、冲突阈值、逐候选谱系、临时代表点）
- 独立复算：`results/raw/s3/verification_report.json`，状态 PASS。

本阶段以可复算表格和指标作为基本结果，没有把 `results/raw/` 制作为论文图，也没有声称这些数值已经 G5 核验。

## 8. 已知不足、失败样本与 S4 优先级

1. Q5 的主要失败信号是真实存在的：模型稳定区域与观测损耗 Pareto 区域 Jaccard 仅 0.0962，因此不能给唯一最优工况；这不是运行失败，而是合同定义的降级输出。
2. Q2 对 25°C 和 90°C 留一温度的 RMSLE 分别为 0.6262 和 0.5543，优先实现冻结的二次乘性温度修正；若触发失败条件才启用预定义交互。
3. Q4 低 `Bm` 四分位 RMSLE 0.2575，高于总体 0.2001；S4 主模型与消融应重点检查幅值/完整波形特征的增益及该子组恶化约束。
4. Q1 的完美 OOF 分类应视为形状类别高度可分的待压力测试现象，而非测试集准确率承诺；优先做相位、幅值不变性和代理字段消融。
5. Q3 共同矩形支持仅覆盖 14.24%，因素结论必须保持“关联”口径，并在共同支持、峰值口径和重复敏感性中核验方向。
6. S3 尚未执行任何 S4 HGB、RandomForest、交互胜者选择、500 次 Bootstrap 或测试附件正式预测。

建议的 S4 顺序：Q2 温度修正 → Q4 HGB 同折比较与消融/子组压力 → Q5 500 次区域稳定性与敏感性 → Q1 不变性/消融及必要候选 → Q3 交互与组 Bootstrap。
