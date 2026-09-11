# 2024_B 配图交接包

本包是 S6 配图同学的只读输入快照。包内数值材料全部来自
`projects/rehearsal_2024_B/results/verified/`；请只使用
`handoff/result_registry.md` 中已登记的 Evidence ID，并遵循
`handoff/figure_handoff.md` 的图题、坐标、精度和禁止措辞要求。

## 建议作图范围

- F1：Q3 冻结模型比较，来源 `q3_baseline_metrics.json`、`q3_candidate_metrics.json`。
- F2：Q3 分组 bootstrap 不确定性，来源 `group_bootstrap_intervals.json`。
- F3：Q3 primary 与 source-blind LOSO 对比，来源 `q3_candidate_metrics.json`、`stratified_metrics.json`。
- F4：Q2 晋级阈值与回退，来源 `verified_metrics.json`、Q2 baseline/candidate metrics。
- F5：当前只可绘制 Q1 已验证的准确性部分，来源 `q1_metrics.json`；特征重要性文件尚未迁入 verified，不得自行从 raw 取用。

## 边界

- 包内不含原始 CSV、joblib 模型和官方无标签预测文件。
- 官方测试预测没有标签，禁止绘制或声称 accuracy、误差或性能提升。
- 不得手工抄写图中数值；绘图脚本应直接读取 `data/` 文件并保留图数据快照。
- 正式作图前，主负责人仍需按仓库规则确认具体绘图 skill；本包本身不生成任何图。
- 图注必须写明 Evidence ID 和源文件；bootstrap 只能称为 OOF group-resampling uncertainty。

`PACKAGE_MANIFEST.json` 记录每个输入文件的仓库来源与 SHA-256，可用于收包验真。
