# Gate 2 Review Response — Round 2

## Metadata

- Project: rehearsal_2024_B
- Gate: G2
- Review Round: 2
- Prior Verdict: REVISE
- Prior Review Commit: fe959aff8f53e0add7c473a97f981ffc679e293d
- Prior Reviewed Commit: 5bf0126d03ad0ce81cdd2c6c594a35c68d0f0ebb
- Revised Contract Implementation Commit: 43a856642e9405b0c42cf479160f30cd2dae0653
- Formal Validation Status: PASS
- Current Stage: S2
- Requested Transition: S2→S3
- Model Fits During Revision: 0
- Official Test Numeric Reads / Predictions: 0 / 0

## Response Summary

本轮只修复 Reviewer 指定的 RF-1、RF-2 及三个 Minor，没有扩展模型族、改变 G1 数据合同或启动 S3。人工合同、机器配置、split/lineage registry 和负向合成测试已经统一。

| Review item | Resolution | Main evidence | Residual risk |
|---|---|---|---|
| M2-01 / RF-1 | CLOSED CANDIDATE | experiment plan、test_release_contract、contract_guard.py、test guard synthetic tests | S3/S4 实现仍须在 read_csv 前调用 guard；已写为硬合同 |
| M2-02 / RF-2 | CLOSED CANDIDATE | fixed Q1-B1 bounded contract、primary/LOSO nested registry、409 lineage batches、negative leakage tests | 第三层增加计算量；固定 Ridge 与有限候选控制成本 |
| Minor-01 | CLOSED CANDIDATE | repeated_cv_metric_contract | 三个 repeat 只提供描述性 repeat dispersion |
| Minor-02 | CLOSED CANDIDATE | Q1/Q3 contracts 与 machine config | raw 保留但只能审计，不能参与晋升 |
| Minor-03 | CLOSED CANDIDATE | contract_artifacts SHA lock | 文本按 UTF-8 且 CRLF/CR→LF 规范化后哈希 |
| Advisory-01 | CONTRACTED FOR S3 | feature_schema_contract | 文件在 S3 feature dry-run 时生成，不在 S2 伪造 |

“CLOSED CANDIDATE”只表示 Main Agent 已提供修复证据，最终关闭权属于 Reviewer。

## RF-1 — Official Test Release

### Conflict removed

已从 S3 Phase P1 删除：

> 对官方测试执行一次 Baseline 推理。

S3/S4 的格式和导出验证改为：

- synthetic_schema_fixture；
- training_outer_validation_output；
- training_loso_output。

任何 protected phase 均不得解析、推理或人工观察官方测试预测。

### Unique release point

唯一释放流程为：

```text
O3 = FREEZE_CANDIDATE
→ G4 PASS
→ enter S5
→ freeze model IDs/parameters, training hashes, feature schema,
  Q1/Q3 postprocessing, Q2 label order and output schema
→ run guard verifies selection_closed=true and prior_release_count=0
→ exactly one official-test inference/export
→ write release ledger
→ no feedback to O2/O3/S4
```

### Machine enforcement

`configs/s2_experiment_plan.json` v2 登记：

- 13 个训练文件 allowlist；
- 4 个官方测试文件 denylist；
- protected phases：S2、S3、O2、S4、O3、G4_REVIEW；
- final release phase：S5_FINAL_INFERENCE；
- minimum gate：G4_PASS；
- freeze manifest 必填字段；
- exactly_once 与 prior_release_count=0；
- release ledger 和禁止反馈阶段。

`src/contract_guard.py` 只检查 run manifest，不打开 CSV。它在数值解析前执行。正式 S2 验证已证明：

- 合法 S3 训练 manifest 被接受；
- S3 注入官方测试文件被拒绝；
- freeze manifest 不完整的最终释放被拒绝；
- G4 PASS、完整 freeze 和首次释放条件同时满足时才被接受。

## RF-2 — Nested Q1 Feature Lineage

### Frozen upstream identity

Q2/Q3 在 S3、S4 与 LOSO 中统一使用：

- `upstream_model_id=Q1-B1`；
- `Ridge(alpha=1.0)`；
- `prediction_variant=seq_time_bounded`；
- `postprocess_version=q1_clip_0_test_dur_v1`。

Q1-HGB 只回答 Q1，不替换下游上游模型，因此不存在“先用全局 Q1 胜者再选择下游”的双重选择。

### S3 fixed Baseline

S3 下游 Baseline 固定，不做 inner-CV 选参：

- outer-training 行的 Q1 特征由冻结 inner 3-fold 产生 OOF；
- outer-validation 的 Q1 特征由完整 outer-training 拟合后推理；
- 每批保存预测组与上游 fit-group SHA。

### S4 nested selection

对每个 `outer_repeat × outer_fold × downstream_inner_fold`：

1. downstream inner-validation 完全隔离；
2. 只在 downstream inner-training 内执行第三层 3-fold；
3. 第三层为 inner-training 每组产生一次 Q1-B1 bounded OOF；
4. 完整 inner-training 的 Q1-B1 只用于预测 inner-validation；
5. 全部下游候选共享相同 frozen nested assignments；
6. 选参结束后再按 outer 边界重建 OOF/validation 特征。

### LOSO source blindness

每个 held-out source：

- 从预处理、Q1/Q2/Q3 拟合和选择中全部排除；
- S3 固定 Baseline 不做选参；
- S4 只在剩余 source 内执行 downstream inner 与 nested upstream；
- 不复用接触过 held-out source 的全局最优配置。

### Formal machine evidence

正式结果来自干净 commit `43a856642e9405b0c42cf479160f30cd2dae0653`：

- outer assignments：1,446；
- downstream-inner assignments：5,784；
- primary nested-upstream assignments：11,568；
- primary upstream lineage batches：240；
- LOSO splits：13；
- LOSO downstream-inner assignments：5,784；
- LOSO nested-upstream assignments：11,568；
- LOSO upstream lineage batches：169；
- total lineage batches：409；
- prediction∩fit overlap total：0；
- downstream-validation/held-out∩fit overlap total：0；
- fixed upstream identity：all batches PASS；
- split registry SHA-256：88B108D181C2EA3A723303DED3D0E64BACEF7FA482F8322712ED97ED020A6C2D。

负向合成测试明确验证：

- in-sample Q1 prediction lineage 被拒绝；
- downstream inner-validation 标签进入上游 fit 被拒绝；
- 干净 lineage 被接受。

## Minor Resolutions

### Repeated CV and bootstrap

- 每个 repeat 内先合并 OOF 并独立计算指标；
- 主点估计为三个 repeat 指标的算术平均；
- fold/repeat dispersion 分开命名且只作描述性离散度；
- bootstrap 以原始 source_file+test_id 为抽样单位；
- 同一组全部 AP 行和三个 repeat 预测共同抽样，不视为独立样本；
- 区间命名为 group-bootstrap uncertainty interval。

### Raw and bounded

- Q1：bounded MAE 为唯一晋升口径，bounded 进入 Q2/Q3；raw 只作审计。
- Q3：bounded AP 为唯一晋升口径；system 为 bounded AP 严格求和；raw AP/system 只作审计。
- 裁剪比例、raw 指标和异常率继续报告，但不得事后替换主结果。

### Contract artifact lock

机器合同登记并验证以下 LF-normalized UTF-8 SHA-256：

- work/04_solution_plan.md
- work/05_experiment_plan.md
- work/models/q1_model_contract.md
- work/models/q2_model_contract.md
- work/models/q3_model_contract.md
- work/optimization/o1_solution_optimization.md

正式验证结果：contract_artifact_hashes=PASS。

### Feature schema

S3 feature dry-run 必须生成 `results/raw/baseline/feature_schema.json`，至少包含：

- name；
- dtype；
- unit；
- missing_semantics；
- column_order。

该文件尚未生成，因为 G2 PASS 前禁止启动 S3；机器合同已冻结其位置和必填字段。

## Verification

```powershell
conda run -n math_modeling python -m py_compile projects/rehearsal_2024_B/src/contract_guard.py projects/rehearsal_2024_B/src/s2_contract_validation.py
conda run -n math_modeling python projects/rehearsal_2024_B/src/s2_contract_validation.py --verify-only
```

正式写出仅从干净 implementation commit 执行：

```powershell
conda run -n math_modeling python projects/rehearsal_2024_B/src/s2_contract_validation.py
```

正式验证同时满足：

- worktree before outputs=clean；
- input before/after=PASS 且哈希不变；
- contract artifact hashes=PASS；
- Q3 metric、lineage leakage、test release guard synthetic tests=PASS；
- model_fit_count=0；
- official_test_numeric_read_count=0；
- official_test_prediction_count=0。

## Files Changed for Review

- work/04_solution_plan.md
- work/05_experiment_plan.md
- work/models/q1_model_contract.md
- work/models/q2_model_contract.md
- work/models/q3_model_contract.md
- work/optimization/o1_solution_optimization.md
- configs/s2_experiment_plan.json
- src/contract_guard.py
- src/s2_contract_validation.py
- results/raw/s2/
- logs/decisions.md
- logs/experiments.md
- CURRENT.md
- work/revisions/gate_2_response.md
- reviews/gate_2_submission_r2.md

## Remaining Boundary

G2 Round 2 PASS 前：

- Current Stage 保持 S2；
- 不启动 S3，不拟合任何预测模型；
- 不读取官方测试数值、不生成测试预测；
- Main Agent 不创建或修改 reviews/gate_2_review_r2.md。
