# Q3 Model Contract — AP and System Throughput

## Problem

结合 Q1 发送机会与 Q2 速率状态分析，预测 test_set_1 中：

1. 185 个 AP 的 throughput；
2. 75 个严格完整系统组的 throughput，定义为组内所有 AP throughput 之和；
3. AP 和系统两级题面 signed error CDF、ERROR_90 与 accuracy_90。

AP 与系统必须代数一致，不训练互相矛盾的独立系统模型。

## Inputs

### Allowed

- S2 统一基本信息、拓扑感知 RSSI 与门限裕量；
- AP 数、protocol、eirp；
- 固定 Q1-B1 Ridge(alpha=1.0) 的 seq_time_bounded：训练阶段严格 OOF，验证/最终推理阶段 inference；postprocess=q1_clip_0_test_dur_v1；
- 题面明确许可的真实 nss、mcs；
- 由真实 nss/mcs 和题面 20 MHz 表唯一映射的 PHY Rate；
- 基于以上合法量构造的 airtime fraction 和物理容量代理。

### Key or stratum only

source_file、test_id、loc_id、bss_id、名称、MAC、ap_id、sta_id。

### Forbidden

per、num_ampdu、ppdu_dur、other_air_time、真实 seq_time、作为输入的 throughput、Q1 训练内拟合值、预测/误差占位列，以及官方测试数值分布。

Q3 对真实 nss/mcs 的许可不扩展到任何其他事后字段。

## Outputs

AP level：

- key：source_file + test_id + ap_id；
- throughput_raw、throughput_bounded=max(0,throughput_raw)，Mbps；
- model/config/repeat/fold；
- physical proxy、rate_missing 和 Q1 prediction lineage。

System level：

- key：source_file + test_id；
- AP count；
- system_throughput=sum of exported AP throughput，Mbps；
- 组成 AP 键列表与严格身份状态。

官方输出数量：185 AP 行、75 系统组。系统输出只由 AP 输出求和，不设独立预测头。

## Variables and Units

| Symbol | Meaning | Unit |
|---|---|---|
| z_ig | 统一合法特征 | mixed |
| shat_ig | Q1 cross-fitted / inference seq_time | s |
| T_ig | test_dur | s |
| R_ig | 题面 (NSS,MCS) PHY Rate | Mbps |
| p_ig | airtime × PHY Rate 容量代理 | Mbps |
| eta | 有效传输效率系数 | dimensionless |
| y_ig, yhat_ig | AP 真实/预测吞吐量 | Mbps |
| Y_g, Yhat_g | 系统真实/预测吞吐量 | Mbps |
| nav | NAV 门限 | dBm |
| r | 有符号相对误差 | dimensionless |

题面 20 MHz PHY Rate 映射：

| NSS | MCS 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8.6 | 17.2 | 25.8 | 34.4 | 51.6 | 68.8 | 77.4 | 86.0 | 103.2 | 114.7 | 129.0 | 143.4 |
| 2 | 17.2 | 34.4 | 51.6 | 68.8 | 103.2 | 137.6 | 154.9 | 172.1 | 206.5 | 229.4 | 258.1 | 286.8 |

0|0 没有题面映射，视为 rate_missing，不擅自设为 0 Mbps 或 NSS=1。

## Assumptions

1. 真实 nss/mcs 在 Q3 test_set_1 可用，且题面明确授权。
2. Q1 预测的发送时长可作为占用信道时间的代理，但不是完整空口效率。
3. PHY Rate × airtime fraction 是容量上界型代理，实际吞吐还受聚合、冲突、PER 和协议开销影响；这些事后量不能作为输入。
4. 一个折内可用单一 eta 建立最简单物理 Baseline，残差模型再学习合法特征中的系统性偏差。
5. AP 预测非负；不强制上界裁剪到 PHY Rate，只报告超 PHY Rate 诊断，避免未验证约束破坏数据拟合。
6. AP 真实目标有 5 个零值；系统 482 个训练目标均大于 0。
7. 系统指标只有在严格身份组上有效。

## Mathematical Definition

容量代理：

$$
p_{ig}=
\frac{\widehat s_{ig}}{T_{ig}}
R(nss_{ig},mcs_{ig})。
$$

Q3-B2 折内效率估计：

$$
\widehat\eta=
\operatorname{clip}_{[0,1]}
\frac{\sum_{ig\in A}p_{ig}y_{ig}}
{\sum_{ig\in A}p_{ig}^2}，
$$

其中 A 只含 PHY Rate 有定义且分母有效的 outer-train AP 行。若分母为 0，Q3-B2 失败。有效行预测为：

$$
\widehat y^{phy}_{ig}=\widehat\eta p_{ig}。
$$

rate_missing 行使用同一 outer-train 拟合的 Q3-B1 预测作物理 Baseline 回退，不删除该行。

主候选：

- direct：
  $$
  \widehat y^{raw}_{ig}=F_3(z_{ig},\widehat s_{ig},R_{ig},p_{ig})；
  $$
- residual：
  $$
  \widehat y^{raw}_{ig}=b_{ig}
  +F_3(z_{ig},\widehat s_{ig},R_{ig},p_{ig})，
  $$
  其中 b 为 Q3-B2 或 rate_missing 时的 Q3-B1。

非负输出：

$$
\widehat y_{ig}=\max(0,\widehat y^{raw}_{ig})。
$$

系统输出：

$$
Y_g=\sum_{i\in g}y_{ig},
\qquad
\widehat Y_g=\sum_{i\in g}\widehat y_{ig}。
$$

## Objective

拟合目标：

- Q3-B0：训练折中位数；
- Q3-B1：Ridge 平方损失；
- Q3-B2：受 [0,1] 约束的单参数最小二乘；
- direct/residual HGB：squared_error。

模型选择使用不会奖励系统性低估的预注册分数：

$$
S_{Q3}=
\max\{Q_{0.90}^{nearest}(|r^{AP}|),
Q_{0.90}^{nearest}(|r^{SYS}|)\}，
$$

越小越好。

若 S 差异小于 0.5%，依次比较：

1. AP 与系统归一化 MAE 的平均；
2. 两级绝对 median signed bias；
3. 模型复杂度。

题面 signed CDF 仍必须完整报告，但不直接作为可被低估操纵的选择目标。

## Constraints

- source_file + test_id 是所有切分和系统求和原子；
- AP 和系统键先通过严格身份检查；
- 系统预测只能是最终 AP 预测之和；
- Q1 输入必须具有 Q1-B1、seq_time_bounded、q1_clip_0_test_dur_v1、prediction_role 和 fit-group hash 血缘；
- 所有预处理、eta、上游和下游模型只在当前训练边界拟合；
- Q3-B2 不使用真实 seq_time；
- rate_missing 不静默填 0、不改标签；
- AP 输出不小于 0，raw 与 bounded 都保存；
- 真实 throughput=0 不进入相对误差分母；
- S2/S3/O2/S4/O3/G4_REVIEW 的输入 manifest 不得含官方测试文件；
- 官方测试只允许在 G4 PASS 后的 S5 freeze manifest 完整时一次最终推理，且不参与任何模型、裁剪或规则选择；
- 不使用 PER、聚合、PPDU 或 other_air_time 作为特征。

## Parameters

- split：3×5 outer GroupKFold，固定 registry；
- inner：3-fold GroupKFold；
- Ridge alpha=1；
- eta bounds=[0,1]；
- HGB common：max_iter=200、min_samples_leaf=20、learning_rate=0.05、early_stopping=false；
- max_leaf_nodes ∈ {7,15}；
- l2_regularization ∈ {0,1}；
- direct 最多 4 个配置，residual 最多 4 个，总计 8；
- group bootstrap：1,000 次，seed=202412；
- 相对误差零值判断：真实浮点值精确等于 0，禁止事后添加 epsilon。

## Training / Solving Procedure

1. 校验输入哈希、A01、严格身份、合同 SHA 和 phase 输入白名单。
2. 读取 outer/downstream-inner/nested-upstream/LOSO registry。
3. S3 的 outer-training 使用 inner 3-fold Q1-B1 bounded OOF；outer-validation 使用完整 outer-training 拟合的 Q1-B1 bounded 预测。
4. 由题面表映射实际 nss/mcs 到 PHY Rate，0|0 标 rate_missing。
5. S3 依次运行固定 Q3-B0、Q3-B1、Q3-B2，不做下游调参。
6. 每个 AP 先得到 throughput_raw 和 throughput_bounded=max(0,raw)；主系统预测严格求和 bounded AP。
7. 同时计算 bounded AP/system 主指标、raw 审计指标和逐组诊断。
8. O2 若授权主候选，对每个 downstream inner fold，只在 inner-training 的 nested-upstream 3-fold 生成 Q1-B1 bounded OOF，并由完整 inner-training 预测 inner-validation，再比较 direct/residual 的最多 8 个配置。
9. 每个 lineage 断言 OOF 目标和 downstream inner-validation 均不进入相应上游 fit groups；外层只评价 inner 已选配置。
10. 运行 A03 完整组排除、with/without 固定 Q1、2/3 AP 分层和 source-blind LOSO；LOSO 的选择只使用剩余 source。
11. 每个 repeat 独立计算指标后取算术平均；组 bootstrap 保留同组所有 repeat 预测。
12. S3/S4 导出 dry-run 只用合成 fixture 或训练侧 outer-validation/LOSO 输出。
13. 只有 G4 PASS 后进入 S5，且 freeze manifest 固定模型、schema、Q1/Q3 后处理和输出格式，才可用全 eligible 训练重拟合并对 test_set_1 一次最终推理。
14. 导出前验证 185 AP、75 system、键、组和 bounded sum equality，容许绝对数值误差 1e-9 Mbps；写 release ledger 后不得反馈选择。

## Baseline

### Q3-B0

训练折 throughput 中位数，检查模型是否优于无信息常数。

### Q3-B1

Ridge(alpha=1.0)，共享合法特征和 Q1 cross-fitted 预测。

### Q3-B2

受约束物理效率 Baseline，显式连接 Q1 airtime 和 Q2 PHY Rate。它是主 residual 架构的物理锚点；rate_missing 行回退 Q3-B1。

## Evaluation

题面主报告以 throughput_bounded 为唯一晋升口径，AP 与 bounded AP 严格求和后的系统分别计算：

$$
r=(\widehat y-y)/y，
\quad
F(x)=\#\{r_i\le x\}/n。
$$

- ERROR_90：r 升序后第 ceil(0.90n) 项，一基、最近秩、不插值；
- accuracy_90=1-ERROR_90，不裁剪；
- 并列值全部保留；
- y=0 从相对 CDF 排除、披露数目，并单报绝对误差。

辅助：

- absolute-relative-error CDF 与 nearest-rank 90%；
- MAE、RMSE、R²；
- median signed bias；
- raw AP/system 审计指标、raw/bounded 差异、负预测裁剪率、超 PHY Rate 率；raw 不参与晋升或事后替换；
- AP 数、loc、nav、protocol 分层；
- 每个 repeat 独立指标、三者算术平均、fold/repeat dispersion；
- source-blind LOSO，以及以原始组为单位并保留全部 repeat 预测的 95% group-bootstrap uncertainty interval；
- A03 组排除、有/无 Q1、direct/residual 消融。

## Failure Conditions

1. AP/system 行数、键、严格身份或 sum equality 失败；
2. 输入哈希、切分或白名单失败；
3. 真实 seq_time、PER 或其他事后字段泄漏；
4. eta 分母为 0 或非有限；仅 Q3-B2 回退，不阻断其他 Baseline；
5. 非有限预测，或 bounded 后仍有负值；
6. 主候选 S_Q3 相对最佳 Q3-B1/B2 改善不足 5%，或三个 repeat 中不足两个改善；
7. 任一层绝对 median signed bias 比最佳 Baseline 恶化超过 0.02；
8. LOSO 相对最佳 Baseline 明显恶化却未披露；
9. 5 个 AP 零目标被加入 epsilon 相对误差；
10. 测试分布用于选择；
11. 输出不是 185 AP / 75 system。

回退顺序：residual/direct HGB → 最佳 Q3-B1 或 Q3-B2 → Q3-B0。若物理 Baseline失效，不影响线性 Baseline 完成全题闭环。

## Expected Artifacts

S3/S4 预期产生：

- experiments/baseline/q3_baseline.json
- results/raw/baseline/q3_ap_oof_predictions.jsonl
- results/raw/baseline/q3_system_oof_predictions.jsonl
- results/raw/baseline/q3_metrics.json
- results/raw/main/q3_candidate_metrics.json
- results/raw/main/q3_error_cdf.json
- results/raw/sensitivity/q3_a03_and_q1_sensitivity.json
- work/06_baseline_report.md 中 Q3 章节
- logs/experiments.md 对应运行记录

上述路径是合同，不表示结果已经产生。
