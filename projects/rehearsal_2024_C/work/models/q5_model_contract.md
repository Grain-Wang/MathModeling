# Q5 Model Contract — 实测工况点上的磁性元件双目标优化

## Problem

以 Q4 冻结损耗预测模型为损耗目标，同时最大化题目指定的传输磁能代理 $E=fB_m$。优化对象是带有可追溯完整波形的附件一实测工况点，而不是能脱离波形轮廓独立决定损耗的抽象五元组。

## Inputs

- Q4 冻结 Pipeline、特征 schema、全量模型、逐行严格 OOF 预测及对应外层折模型；
- 附件一满足可行域规则的实测行、完整 1,024 点波形和观测损耗；
- `row_id`、来源文件 SHA-256、工作表、Excel 行号、`condition_group`、`oof_fold`；
- $T,f,w,B_m,m$、完整 `wave-v1` 特征和波形 SHA-256；
- Q4 OOF 误差、主要子组指标、模型/配置/特征 schema 哈希和失败状态。

不使用附件二；附件三不用于构造优化域、选择候选、调整阈值或评价最优解。

## Outputs

- 可完整复算的实测工况候选索引；
- 以严格 OOF 损耗为主目标的 Pareto 集、两个端点和膝点；
- 全量 Q4 模型的参考 Pareto 及 OOF/full 一致性诊断；
- 每个输出点的 `row_id`、来源定位、波形 SHA-256、全部 Q4 输入特征、$T,f,w,B_m,m,\widehat P_v^{OOF},\widehat P_v^{full},E$；
- 仅用各验证折候选形成的折级 Pareto 和 `q5-region-v1` 支持表；
- 500 次 `condition_group` 簇 Bootstrap 的区域稳定性及正确命名的百分位区间；
- 模型预测 Pareto 与观测损耗 Pareto 的诊断比较；
- 题面名义频率域、实测边界域和峰值口径的敏感性结果；
- 若任一资格门槛失败，只给稳定区域和端点，不给唯一“最优”。

## Variables and Units

| Variable | Type / meaning | Domain / unit |
|---|---|---|
| $c_i$ | 实测工况点决策对象 | `row_id`、来源定位、完整波形/签名、`wave-v1` 与五因素 |
| $g_i=(T_i,f_i,w_i,B_{m,i},m_i)$ | 五因素汇总，不是完整决策身份 | mixed |
| $T$ | 离散工况 | {25,50,70,90} °C |
| $f$ | 实测值 | 主结果 50,000–500,000 Hz |
| $w$ | 离散工况 | 正弦波、三角波、梯形波 |
| $B_m$ | 实测波形峰值 | T，主口径 `max(abs(B))` |
| $m$ | 离散工况 | 材料1–4 |
| $\phi_i$ | Q4 消费的完整 `wave-v1` 特征 | mixed |
| $\widehat P_{v,i}^{OOF}$ | 未训练该点 `condition_group` 的模型预测 | W/m³，主损耗目标 |
| $\widehat P_{v,i}^{full}$ | 附件一全量重拟合模型预测 | W/m³，仅参考/部署诊断 |
| $E_i=f_iB_{m,i}$ | 题目传输磁能代理 | Hz·T，最大化 |

## Assumptions

1. 附件一实测状态是当前最可信的联合可行域代理；不把逐变量边界任意组合假设为可行。
2. 详细波形会改变 Q4 损耗预测，因此五因素不能唯一代表一个优化候选。
3. 严格 OOF 预测比训练内或全量重拟合预测更适合筛查训练候选中的低损耗极值。
4. $fB_m$ 只是题目规定代理，不包含磁芯尺寸、饱和、温升、成本等真实工程约束。
5. 多目标没有题面给定权重，因此 Pareto 集优先于主观加权和。
6. 实测点枚举只回答数据支持域内的权衡，不证明连续物理空间全局最优。

## Mathematical Definition

实测工况点为：

\[
c_i=(\text{row\_id}_i,\text{source}_i,\text{wave\_sha256}_i,
T_i,f_i,w_i,B_{m,i},m_i,B_{i,0:1023},\phi_i).
\]

`row_id=file|sheet|excel_row`。波形签名使用 1,024 个值转为 little-endian IEEE-754 float64、把 `-0.0` 规范为 `+0.0` 后的连续字节计算 SHA-256；非有限值在签名前即失败。来源文件 SHA-256、工作表和 Excel 行号可以从只读原件恢复完整波形，$\phi_i$ 保存 Q4 实际输入，因此每个输出点均可复算。

主可行集合为：

\[
\mathcal X_{obs}=\{c_i\in\text{附件一}:50000\le f_i\le500000\}.
\]

完全相同状态折叠时保留规范 `row_id` 和全部 `duplicate_row_ids`。令 $k(i)$ 是包含候选 $i$ 的唯一外层验证折，$M_{-k(i)}$ 从未使用该候选的 `condition_group` 拟合或调参，则：

\[
\widehat P_{v,i}^{OOF}=M_{-k(i)}(c_i),
\qquad
F_{OOF}(c_i)=\left(\widehat P_{v,i}^{OOF},-f_iB_{m,i}\right).
\]

主 Pareto 集由 $F_{OOF}$ 严格非支配排序得到。全量重拟合模型 $M_{full}$ 只产生：

\[
F_{full}(c_i)=\left(M_{full}(c_i),-f_iB_{m,i}\right)
\]

的参考 Pareto，不参与折外入选计票。

一致性诊断为：

\[
d_i=|\log(1+\widehat P_{v,i}^{full})-\log(1+\widehat P_{v,i}^{OOF})|,
\]

\[
r_i=|\log(1+P_{v,i})-\log(1+\widehat P_{v,i}^{OOF})|.
\]

$d_i,r_i$ 的拒绝阈值是材料×波形参照层的经验 P90；参照层 `n<100` 时回退全局 P90。观测损耗 Pareto使用 $(P_{v,i},-f_iB_{m,i})$，只作诊断。

`q5-region-v1` 定义为 `(material, waveform, temperature, frequency_quartile, Bm_quartile)`。两个四分位边界在 $\mathcal X_{obs}$ 上不读取 $P_v$ 或预测值，采用线性经验分位数一次计算；重复边界合并，区间左闭右开、最后一区间右闭，边界写入 run manifest。

对每个外层折 $k$，只在该折验证候选上用严格 OOF 预测形成 $\mathcal P_k^{OOF}$。区域折支持为包含至少一个 $\mathcal P_k^{OOF}$ 点的折数，最低为 $\lceil0.6K\rceil$。

Bootstrap 以 `condition_group` 为单位重采样严格 OOF 候选表 500 次。对区域 $R$，只在该次重采样包含 $R$ 时计为有效；条件 Pareto 入选率为“有效重采样中 $R$ 至少含一个 Pareto 点”的比例，至少 400 次有效且比例不低于 0.50 才称稳定。

膝点规则：在主 OOF Pareto 内分别把两个目标线性归一化到 $[0,1]$，选择到理想点 $(0,0)$ 欧氏距离最小者；并列时先选 $d_i+r_i$ 较小者，再按 `row_id` 排序。该规则不代表用户偏好。

## Objective

在真实联合支持域内找到严格 OOF 预测损耗与 $fB_m$ 的非支配权衡，并阻止隐藏波形、训练内拟合或单个稀疏极值被写成普遍的五因素最优条件。

## Constraints

1. Q4 未冻结、OOF 覆盖不完整或未通过最低预测能力检查时，不给正式 Q5 推荐。
2. 主候选必须来自 $\mathcal X_{obs}$；不得合成未观测的材料、温度、频率、幅值或波形组合。
3. 候选身份必须含来源定位、波形签名和全部 Q4 输入；五因素只作汇总。
4. 同一候选的主损耗只能来自未训练其 `condition_group` 的唯一 OOF 模型。
5. 全量模型和见过候选的折模型不得给严格 OOF 稳定性投票。
6. 主结果排除 49,990 或 501,180 Hz 行；这些只进入边界敏感性。
7. 观测 $P_v$ 不能替代 Q4 目标，只能用于残差与 Pareto 诊断。
8. 附件二、三不得改变候选域、阈值、权重、膝点或结论。
9. 输出不得称为连续空间或真实工程全局最优。

## Parameters

| Parameter | Frozen value |
|---|---|
| candidate definition | `observed_operating_point_v1` |
| candidate identity | `row_id` + source SHA/sheet/row + waveform SHA + all Q4 features + model/config hashes |
| primary loss score | corresponding strict `y_pred_oof` |
| full-model use | reference Pareto and consistency diagnostic only |
| main frequency domain | 50,000–500,000 Hz |
| boundary sensitivity domain | 49,990–501,180 Hz |
| primary / sensitivity peak | `max(abs(B))` / `B_pp/2` |
| region version | `q5-region-v1`，类别三元组 + 全局 $f/B_m$ 四分位箱 |
| fold-region support | at least `ceil(0.60*K)` held-out folds |
| conflict reference group | material×waveform；`min_n=100`，否则全局 |
| OOF residual / full-OOF gap limit | respective empirical P90 |
| candidate dual-Pareto rule | must be in both OOF and full-fit Pareto |
| observed-region Jaccard warning | `<0.50` 时降级为区域/端点报告 |
| Bootstrap | 500 `condition_group` resamples，seed `20240922` |
| Bootstrap validity / stability | at least 400 valid resamples；conditional region rate `≥0.50` |
| interval name | 95% condition-group cluster bootstrap percentile interval |
| fold-model range name | refit perturbation range，不是置信区间 |
| continuous extension | disabled；需新合同和新 Gate |

## Training / Solving Procedure

1. 核验 Q4 胜者、Pipeline/schema/config 哈希、逐行 OOF 覆盖和每个 `condition_group` 只属于一个验证折；若失败则停止。
2. 从附件一构造名义域实测点，生成确定性来源定位和波形 SHA；完全重复仅在保存全部来源映射后折叠。
3. 导出全部 Q4 输入特征和身份字段；逐点断言从保存字段重算的 Q4 输入向量一致。
4. 用对应外层留出模型的 `y_pred_oof` 形成主 OOF Pareto、两个端点和膝点；不得使用其他折模型替换。
5. 用 Q4 全量模型形成参考 Pareto，计算 $d_i,r_i$ 和材料×波形 P90 阈值；生成双 Pareto资格表。
6. 每折只评价本折验证候选，构造折级 OOF Pareto；按 `q5-region-v1` 统计区域支持。
7. 对严格 OOF 候选表执行 500 次 `condition_group` 簇 Bootstrap，记录有效次数、区域条件入选率和百分位区间。
8. 构造观测损耗 Pareto，报告其与模型稳定区域的重叠/Jaccard；Jaccard `<0.50` 时禁止唯一推荐。
9. 单点必须同时通过双 Pareto、两个 P90、折级区域、Bootstrap 和观测区域一致性门槛；否则只汇总稳定区域与端点。
10. 切换到实测边界域和 `B_pp/2` 口径重算敏感性。任何条件反转均触发降级。
11. 输出时附规范措辞“该实测波形轮廓下的推荐工况”；连续扩展保持关闭。

## Baseline

在 $\mathcal X_{obs}$ 上用 Q4 Baseline 的逐行严格 OOF 预测执行非支配排序，并输出两个单目标端点和 OOF 膝点。全量模型结果仅作为并列参考表。

这条路线可在 S3 复用 Q4 OOF 产物完成，不需要遗传算法、粒子群或额外模型拟合。

## Evaluation

- 身份闭合：每个输出点可由来源定位、波形 SHA、特征 schema 和模型哈希完整复算；
- 折外性：每个 `y_pred_oof` 的模型训练组与候选 `condition_group` 不相交；
- 非支配性：OOF/full/观测三个 Pareto 表分别通过支配断言；
- 预测可靠性：$r_i$、所属 Q4 主要子组误差和观测 Pareto 对照；
- 一致性：$d_i$、双 Pareto资格和稳定区域 Jaccard；
- 折级稳定性：只比较各验证折 OOF Pareto 的 `q5-region-v1` 支持；
- 重采样稳定性：500 次 `condition_group` Bootstrap 的有效次数、条件入选率和百分位区间；
- 敏感性：题面/实测频率域、`B_m`/`B_pp/2`、保留/折叠重复；
- 复现：相同输入、模型和配置哈希下，候选排序与输出哈希一致。

## Failure Conditions

- Q4 未优于至少一个无结构/分组中位数参照，或 OOF 覆盖/分组隔离失败；
- 候选缺少来源定位、波形签名、完整 Q4 特征或模型/配置哈希；
- 用训练过该候选 `condition_group` 的模型分数参与主 Pareto或稳定计票；
- 候选不同时属于 OOF 与 full-fit Pareto；
- 候选 $r_i$ 或 $d_i$ 超过相应参照层 P90；
- 候选区域未在至少 `ceil(0.60*K)` 个验证折 Pareto 出现；
- 区域 Bootstrap 有效次数少于 400 或条件入选率低于 0.50；
- 模型稳定区域与观测损耗区域 Jaccard `<0.50`；
- 频率/峰值口径改变后条件完全反转，或推荐只落在误差最大、边界、稀疏子组；
- 把折模型范围称为 95% 置信区间，把 $fB_m$ 称为实际传输磁能，或宣称五因素/连续空间全局最优；
- 为获得连续最优而临时引入未验证启发式算法。

任一资格条件失败时，仅报告稳定因素区域、频率/$B_m$ 区间、两个端点和明确不确定性；不强行给唯一推荐。连续搜索不是完成本问的必要条件。

## Expected Artifacts

- `results/raw/s3/q5/observed_candidate_index.csv`
- `results/raw/s3/q5/q4_feature_snapshot.csv`
- `results/raw/s3/q5/oof_pareto_baseline.csv`
- `results/raw/s3/q5/full_fit_reference_pareto.csv`
- `results/raw/s3/q5/representative_conditions.json`
- `results/raw/s4/q5/heldout_fold_region_support.csv`
- `results/raw/s4/q5/oof_full_conflict_diagnostics.csv`
- `results/raw/s4/q5/cluster_bootstrap_region_stability.csv`
- `results/raw/s4/q5/observed_loss_pareto_diagnostic.csv`
- `results/raw/s4/q5/frequency_domain_sensitivity.csv`
- `results/raw/s4/q5/peak_definition_sensitivity.csv`
- `results/raw/s4/q5/pareto_validation_report.md`
