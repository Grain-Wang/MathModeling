# Result Registry

> 状态：S5 已独立核验并冻结，等待 G5；论文和正式绘图只能引用本目录。

| Evidence ID | Claim | Source File | Script / Command | Verified | Notes |
|---|---|---|---|---|---|
| E001 | Q1 分组 OOF Macro-F1=1.000；不等于附件二真实准确率 | q1/oof_metrics.json | python src/verify_s5_outputs.py --config experiments/s2_frozen_config.json | YES | 12,400 条分组 OOF |
| E002 | Q1 相位/幅值一致率及留一材料最低 Macro-F1 均为 1.000 | q1/invariance_metrics.csv; q1/leave_one_material_out.csv | 同上 | YES | 支持保留 shape-only Logistic |
| E003 | 附件二冻结分类共 80 条；正文指定样本编码：1→2, 5→2, 15→1, 25→2, 35→3, 45→3, 55→2, 65→2, 75→2, 80→1 | q1/attachment2_predictions.csv | python src/run_s5_predictions.py --config experiments/s2_frozen_config.json | YES | 类别编码：1正弦、2三角、3梯形；无测试真值 |
| E004 | Q2 二次温度修正 OOF RMSLE 0.360678→0.202567，改善 43.84% | q2/quadratic_temperature_metrics.json; q2/quadratic_temperature_parameters.csv | python src/verify_s5_outputs.py --config experiments/s2_frozen_config.json | YES | 材料1、正弦波；同折比较 |
| E005 | Q2 在 25°C/90°C 留一温度压力改善，但 50°C 局部劣化 | q2/leave_one_temperature_comparison.csv; q2/sensitivity_metrics.json | 同上 | YES | 须在局限性中披露 |
| E006 | Q3 两两交互模型 OOF log-RMSE 0.343416→0.326667，改善 4.88% | q3/interaction_metrics.json | 同上 | YES | 仅解释为调整后关联 |
| E007 | Q3 完成 500/500 簇 Bootstrap；40 个两两对比中 27 个符号稳定度≥0.90 | q3/bootstrap_metrics.json; q3/bootstrap_pairwise_interaction_intervals.csv | 同上 | YES | 共同支持仅 14.24%，不得作因果表述 |
| E008 | Q4 HGB 同折优于 Ridge；最终采用 18 特征 amplitude_and_condition 变体 | q4/hgb_metrics.json; q4/ablation_metrics.json | 同上 | YES | 最终 OOF RMSLE=0.070941 |
| E009 | Q4 最终模型 12,400 条 OOF 预测可逐行追溯 | q4/final_oof_predictions.csv | 同上 | YES | 论文精度只来自附件一分组 OOF |
| E010 | Q4 低 Bm OOF RMSLE=0.08328；LOMO/LOTO 最大 RMSLE 分别约 0.37982/0.57496 | q4/stress_metrics.json; q4/leave_one_level_out_metrics.csv | 同上 | YES | 属于外推压力，不是主 OOF |
| E011 | 附件三冻结预测共 400 条；正文指定样本（W/m³）：16→1060.2, 76→1582245.4, 98→12081.2, 126→1730.0, 168→93658.3, 230→69929.5, 271→1785363.6, 338→13398.8, 348→903120.2, 379→1396.5 | q4/attachment3_predictions.csv | python src/run_s5_predictions.py --config experiments/s2_frozen_config.json | YES | 保留 1 位小数；无测试真值 |
| E012 | Q5 主 OOF Pareto 点 118 个，折支持区域 27 个 | q5/robustness_metrics.json; q5/final_oof_pareto.csv | 同上 | YES | 只在观测联合可行域内解释 |
| E013 | Q5 完成 500/500 condition_group Bootstrap，稳定区域 42 个 | q5/bootstrap_region_stability.csv; q5/robustness_metrics.json | 同上 | YES | 固定交叉拟合候选表的重采样稳定性 |
| E014 | Q5 主模型/观测区域 Jaccard=0.39535<0.50，禁止唯一推荐 | q5/robustness_metrics.json | 同上 | YES | 敏感性结果不得覆盖主门槛失败 |
| E015 | 附件四副本的第2列前80项与 Q1 一致，第3列400项与 Q4 一致 | submission/附件四（Excel表）.xlsx | 同上 | YES | 原始附件四哈希保持不变 |

## Global limitations

- 附件二、附件三没有公开真值，正式预测不能作为新的精度证据。
- Q3 结果是控制已建模协变量后的关联，不是因果效应。
- Q4 的未见材料/温度外推压力明显高于主 OOF，不能宣称无条件域外泛化。
- Q5 不满足唯一推荐门槛，只能报告 Pareto 权衡、稳定区域和端点。
- G5 通过前，上述结果仍不得宣称为最终提交已批准。
