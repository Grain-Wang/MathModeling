# S2 Experiment Plan

## 1. Scope and stage boundary

本计划冻结 S3 Baseline 与可能的 S4 主候选如何比较；当前 S2 不拟合预测模型。

- G1/R2：PASS。
- Current Stage：S2。
- G2 PASS 前：只允许合同校验、训练组切分注册、嵌套血缘生成和合成负向门禁测试。
- 官方测试：G4 PASS 后进入 S5，且 freeze manifest 已固定模型、特征 schema、后处理、类别映射与输出格式后才允许一次性推理；任何测试数值或预测均不得返回 O2/O3/S4。
- 原始 CSV：只读且不进入 Git。

## 2. Sources of truth

- Human contract：[04_solution_plan.md](04_solution_plan.md) 与 work/models 下三份合同；
- Machine contract：[s2_experiment_plan.json](../configs/s2_experiment_plan.json)；
- Split registry：results/raw/s2/split_registry.json；
- Contract validation：results/raw/s2/contract_validation.json；
- Approved data evidence：results/raw/s1；
- Formal contract-validation commit：以最新 results/raw/s2/contract_validation.json 的 metadata.git_head 为准；该结果必须从干净提交生成。

Markdown 与 JSON 冲突时停止执行并修正，不允许临时选择更有利口径。

## 3. Data population and identity

- Raw training：1,252 AP 行、484 组；
- Eligible after A01：1,250 AP 行、482/482 strict groups；
- 2 AP：392 行、196 组；
- 3 AP：858 行、286 组；
- Duplicate-equivalence clusters：0；
- Atomic group：source_file + test_id；
- AP key：source_file + test_id + ap_id。

每次实验入口先验证：

1. 17/17 输入文件名、大小、SHA-256；
2. A01 恰隔离 2 行；
3. eligible 严格身份通过；
4. split registry 中每组每 repeat 恰出现一次；
5. train/validation 原子组交集为空；
6. 特征列白名单与目标列禁用断言；
7. 04/05、三份模型合同和 O1 的 SHA-256 与机器合同完全一致；
8. phase run manifest 通过输入白名单；S2/S3/O2/S4/O3/G4_REVIEW 若出现任一官方测试文件立即硬失败。

## 4. Frozen split registry

### 4.1 Primary outer evaluation

- Algorithm：GroupKFold；
- n_splits=5；
- shuffle=true；
- random states：202409、202410、202411；
- assignment 不读取目标；
- 共 15 个 outer folds；
- 所有问题使用同一组级 outer assignments。

目的：估计训练场景内插值性能和折间稳定性。三个 repeat 分开报告，随后合并 OOF。

### 4.2 Downstream inner model selection

对每个 outer-training 集：

- 3-fold GroupKFold；
- seed=302409 + 100×repeat_index + outer_fold；
- 只包含 outer-training groups；
- 每个 downstream inner-validation group 恰出现一次；
- 插补、编码、缩放、eta 和下游模型均在 downstream inner-training 重拟合。

### 4.3 Nested upstream split

对每个 `outer_repeat × outer_fold × downstream_inner_fold`，只在 downstream inner-training 内生成 Q1-B1 OOF 特征：

- 3-fold GroupKFold；
- seed=402409 + 1000×repeat_index + 100×outer_fold + downstream_inner_fold；
- upstream estimator 固定为 `Q1-B1 Ridge(alpha=1.0)`；
- prediction 固定为 `seq_time_bounded`；
- postprocess 固定为 `q1_clip_0_test_dur_v1`；
- downstream inner-validation 组不得进入任一 nested-upstream fit；
- 每个 downstream inner-training group 恰作为一次 nested-upstream validation；
- 全部候选复用同一分配，训练时不得重新随机划分。

split_registry.json 同时保存 outer、downstream inner、nested upstream 和 prediction-lineage batches。每个 batch 包含预测组、fit-group SHA-256、模型 ID、预测版本、后处理版本、作用域及零交集断言。

### 4.4 Mandatory scenario stress

LeaveOneGroupOut(group=source_file)，13 个固定 splits。每个 held-out source 从预处理、上游拟合、下游拟合及选择中完全排除：

- S3 固定 Baseline 不做参数选择；
- S4 只在剩余 source 内执行 downstream inner 与 nested upstream 选择；
- LOSO downstream inner seed=502409+split_index；
- LOSO nested upstream seed=602409+100×split_index+10×downstream_inner_fold；
- 不得复用接触过 held-out source 的全局最优配置。

LOSO 与 primary CV 分开报告，不能用较好的一套替代较差的一套。

### 4.5 Repeated-CV aggregation and bootstrap

- 每个 repeat 内先合并该 repeat 的 OOF，再独立计算指标；
- 主点估计为 3 个 repeat 指标的算术平均；
- fold dispersion 与 repeat dispersion 分开命名，仅作描述性离散度；
- resampling unit：原始完整 source_file + test_id group；
- 1,000 replicates，seed=202412，percentile 95% group-bootstrap uncertainty interval；
- 同一组全部 AP 行以及 3 个 repeat 的预测共同抽样，不把重复预测当独立样本；
- bootstrap 只在已产生 OOF 预测后计算，不重新调模型。

## 5. Cross-fitting graph

### 5.1 S3 fixed Baseline

~~~text
outer-train
    +--> inner 3-fold fixed Q1-B1 bounded OOF
    |       -> downstream fixed Baseline training features
    +--> fit Q1-B1 on all outer-train
            -> outer-validation Q1 bounded inference
            -> downstream outer-validation prediction
~~~

### 5.2 S4 downstream candidate selection

~~~text
outer-train
    +--> downstream inner-training
    |       +--> nested-upstream 3-fold Q1-B1 bounded OOF
    |       |       -> downstream inner-training features
    |       +--> fit Q1-B1 on all downstream inner-training
    |               -> downstream inner-validation Q1 bounded inference
    +--> select downstream candidate using inner-validation only
    +--> rebuild outer-train OOF features with frozen inner registry
            -> fit selected downstream candidate
            -> evaluate outer-validation once
~~~

禁止任何训练行使用 Q1 训练内预测。每个 lineage batch 保存 `upstream_model_id=Q1-B1`、`prediction_variant=seq_time_bounded`、`postprocess_version=q1_clip_0_test_dur_v1`、`prediction_role`、预测组列表、`upstream_fit_groups_hash` 和交集计数；任一 OOF 目标组或 downstream inner-validation 组进入相应 fit groups 时立即失败。

## 6. Preprocessing experiment invariant

所有候选共享：

- 同一 eligible 行；
- 同一 split registry；
- 同一 RSSI 解析和 focal/peer 对齐；
- 同一门限裕量定义；
- 同一缺失指示；
- 同一输出键和指标实现。

只允许估计器及合同中显式列出的 ablation 不同。任何在全数据拟合的插补、缩放、类别编码或特征选择都判泄漏。

## 7. Candidate budget

### 7.1 S3 mandatory Baselines

| Run ID | Question | Candidate | Tuning | Purpose |
|---|---|---|---|---|
| EXP-S3-Q1-B0 | Q1 | median Dummy | None | 无信息下界 |
| EXP-S3-Q1-B1 | Q1 | Ridge alpha=1 | None | 结构线性 Baseline |
| EXP-S3-Q2-B0 | Q2 | most-frequent joint class | None | 类别不平衡下界 |
| EXP-S3-Q2-B1A | Q2 | Logistic C=1 without Q1 | None | 不依赖上游 |
| EXP-S3-Q2-B1B | Q2 | Logistic C=1 with Q1 cross-fit | None | Q1 依赖 Baseline |
| EXP-S3-Q3-B0 | Q3 | median Dummy | None | 无信息下界 |
| EXP-S3-Q3-B1 | Q3 | Ridge with Q1 cross-fit | None | 结构线性 Baseline |
| EXP-S3-Q3-B2 | Q3 | constrained physical eta | One fold-only scalar | Q1 airtime + Q2 PHY Rate 闭环 |

S3 不搜索 alpha、C、特征组合或权重。所有 Baseline 必须先跑通全题，才能执行 O2。

### 7.2 Conditional S4 candidates

只有 O2=PROCEED_TO_G3 且给出对应失败证据后：

| Question | Family / architecture | Fixed configurations | Maximum |
|---|---|---:|---:|
| Q1 | HGB regressor | 4 | 4 |
| Q2 | HGB classifier | 4 | 4 |
| Q3 | direct HGB | 4 | 4 |
| Q3 | residual HGB around physics | 4 | 4 |

共同固定：learning_rate=0.05、max_iter=200、min_samples_leaf=20、early_stopping=false；只交叉 max_leaf_nodes={7,15} 与 l2_regularization={0,1}。

禁止扩大网格。Q2 平方根逆频率权重最多一次，且仅在 O2 记录 minority collapse 后执行。

### 7.3 Conditional AP-count split model

统一模型为默认。只有同时满足以下条件才允许一次 2 AP/3 AP 分模对照：

1. 最差 AP 数分层的主指标比另一层差至少 10%；
2. 三个 repeat 中至少两个出现同方向；
3. 每层训练组数足够运行相同切分；
4. O2 将其选为至多两个主要改进之一。

失败即回退统一模型。

## 8. Evaluation contract

### 8.1 Q1

Primary：基于 seq_time_bounded 的 grouped OOF MAE，s；每个 repeat 独立计算后取三者算术平均。

Secondary：raw MAE/RMSE/R²、bounded RMSE/R²、裁剪率、fold/repeat dispersion、分层、LOSO、组 bootstrap。raw 只作审计，不得与 bounded 事后择优。

Promotion：HGB 相对 Q1-B1 MAE 至少改善 5%，且三个 repeat 至少两个改善；不得让 LOSO 相对退化多 10 个百分点以上。

### 8.2 Q2

Primary：

- 固定 17 类 macro-F1，zero_division=0；
- joint exact-match accuracy。

Secondary：balanced accuracy、NSS/MCS 分量准确率、log loss、混淆矩阵、support、缺类、分层、LOSO、A03、with/without Q1。

Promotion：macro-F1 至少提高 0.02，至少两个 repeat 改善，joint accuracy 不下降超过 0.01。

Global labels：

~~~text
0|0
1|0, 1|4, 1|5, 1|6, 1|7, 1|9
2|2, 2|3, 2|4, 2|5, 2|6, 2|7, 2|8, 2|9, 2|10, 2|11
~~~

训练折缺类：概率列补零、不能预测、明确披露。配置外标签硬失败。

### 8.3 Q3

AP 与 system 分开计算题面主指标：

- signed r=(prediction-truth)/truth；
- empirical CDF；
- ERROR_90=升序第 ceil(0.90n) 项，一基、不插值；
- accuracy_90=1-ERROR_90，不裁剪；
- truth=0 排除相对指标并单列绝对误差。

Selection score：

$$
S_{Q3}=\max\{ARE90_{AP},ARE90_{SYS}\}。
$$

Promotion：相对最佳 Q3-B1/B2 改善至少 5%，三个 repeat 至少两个改善，且任一层 absolute median signed bias 不恶化超过 0.02。

系统一致性：主评价使用 throughput_bounded=max(0,throughput_raw)；每个 system prediction 必须等于其 bounded AP predictions 之和，绝对容差 1e-9 Mbps。raw AP/system 指标只作审计，不得用于事后替换 bounded 主结果。

## 9. Execution order and decision points

### Phase P0 — S2 contract validation

1. py_compile；
2. --verify-only；
3. 从干净实现 commit 运行 s2_contract_validation.py；
4. 固定 outer/inner/LOSO registry；
5. 运行 Q3 合成指标测试；
6. 断言 model_fit_count=0、official_test_numeric_read_count=0。

完成后执行 O1。O1 不是性能实验。

### Phase P1 — S3 Baseline, only after G2 PASS

1. 启动时复算合同文件 SHA-256，并让 phase run manifest 通过训练文件白名单；
2. 共享特征引擎 dry-run，生成 feature_schema.json；
3. Q1-B0/B1；
4. 用固定 Q1-B1 bounded 版本生成 S3 cross-fit；
5. Q2-B0/B1A/B1B；
6. Q3-B0/B1/B2；
7. 在 outer-validation/LOSO 或合成 fixture 上执行 AP/system 指标和导出格式 dry-run；
8. 完成 source-blind LOSO；
9. 冻结 S3 Baseline report；
10. 执行 O2。

P1 禁止解析、推理或人工查看四个官方测试文件的数值或预测。

### Phase P2 — S4 bounded improvements

只执行 O2 选出的最多两个主要方向。所有含 Q1 特征的下游选参必须使用 frozen nested-upstream registry；每个 LOSO 折只在其训练 source 内选择。每个方向先最小验证，达到晋升条件才完成全量 repeated CV/LOSO；否则停止并回退。S4/O3 仍禁止官方测试推理。

### Phase P3 — model freeze and one-time release

1. O3 决定 FREEZE_CANDIDATE；
2. 提交并通过 G4；
3. 进入 S5，将最终模型 ID/参数、训练输入哈希、feature_schema SHA、Q1 bounded 后处理、Q2 类别顺序、Q3 非负后处理和导出格式写入不可变 freeze manifest；
4. run guard 确认 gate_state=G4_PASS、selection_closed=true、prior_release_count=0；
5. 仅此时对四个官方测试文件执行一次最终推理和导出；
6. 写入 release ledger；之后禁止返回 O2/O3/S4，也不得因预测外观调整模型或规则。

## 10. Runtime and storage budget

预估而非已测结果：

| Work item | Compute time box | Failure action |
|---|---:|---|
| S2 contract/split validation | 15 min | 修复合同，不进入 G2 |
| S3 all Baselines primary CV | 60 min | 单线程定位，回退最简模型 |
| S3 LOSO and reports | 60 min | 保留 primary，修复后补齐 mandatory LOSO |
| Each S4 question family | 120 min | 超 2 倍即停止扩张 |
| Bootstrap/report generation | 45 min | 降低展示复杂度，不改主点估计 |

数据规模小于 1,300 行；当前 CPU 足以完成，A800 非必要。并行固定线程数并记录，避免不同运行的资源差异影响可复现性。

所有输出使用 JSON/JSONL/PNG 或模型二进制，不使用 CSV，避免触发项目全局 CSV 忽略规则。

## 11. Artifacts and logging

每次运行记录：

- run ID、Git SHA、config SHA、split registry SHA；
- 开始/结束 ISO 时间、随机种子、线程数；
- 输入哈希；
- 特征 schema 哈希；
- estimator 与完整参数；
- train/validation group 数；
- 指标与失败状态；
- 输出路径；
- phase input manifest 与白名单检查结果；
- upstream lineage hash、预测版本和后处理版本；
- 是否使用官方测试；若是必须为 S5 final inference/export，并记录 G4 PASS、freeze manifest SHA、release ID 和 prior_release_count=0。

feature_schema.json 至少冻结派生特征名称、dtype、单位、缺失语义和列顺序。原始输出进入 results/raw；G5 前不得写入 results/verified。

## 12. Global stop conditions

任一发生立即停止对应运行：

1. 输入哈希、严格身份、A01 或 split registry 不匹配；
2. train/validation 组交集非空；
3. S2/S3/O2/S4/O3/G4_REVIEW 的 run manifest 出现官方测试文件，或测试数值/预测进入选择；
4. 禁止字段出现在模型矩阵；
5. 下游训练使用非 cross-fitted Q1、非 Q1-B1、非 bounded 版本，或 lineage 交集非零；
6. Q2 标签/概率合同失败；
7. Q3 合成指标或 AP/system sum equality 失败；
8. 非有限结果、输出行数或键失败；
9. 候选超预算；
10. 运行超时间盒 2 倍；
11. 代码与模型合同冲突。

发生全局错误时不生成“成功”日志，不覆盖最近可用版本，并在 decisions/experiments 中登记。

## 13. G2 stop point

S2 完成 P0 与 O1 后，只提交方案、合同、切分和合成验证证据。G2 PASS 前不执行 P1。
