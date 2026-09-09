# Gate 2 Submission — Review Round 2

## Submission Metadata

- Project: rehearsal_2024_B
- Gate: G2
- Stage: S2 — 总体方案与模型合同
- Review Round: 2
- Prior Verdict: REVISE
- Prior Review Commit: fe959aff8f53e0add7c473a97f981ffc679e293d
- Prior Reviewed Commit: 5bf0126d03ad0ce81cdd2c6c594a35c68d0f0ebb
- Revised Contract Implementation Commit: 43a856642e9405b0c42cf479160f30cd2dae0653
- Formal Validation: PASS
- Response: [work/revisions/gate_2_response.md](../work/revisions/gate_2_response.md)
- Review Target: 推送完成后的 origin/main 完整 SHA，由交接消息提供
- Expected Review: reviews/gate_2_review_r2.md

## Requested Review Scope

1. RF-1：S3/O2/O3/S4 前是否已彻底删除官方测试推理，唯一释放是否冻结为 G4 PASS 后、S5 freeze manifest 完成后的一次最终推理。
2. RF-1：机器 guard 是否能在数值解析前拒绝 protected phase 中的四个官方测试文件，并拒绝不完整/重复释放。
3. RF-2：Q2/Q3 上游是否唯一固定为 Q1-B1 Ridge(alpha=1.0) 的 seq_time_bounded。
4. RF-2：primary 与 LOSO 的 downstream inner / nested upstream registry 和逐批 fit-group lineage 是否证明零交集。
5. Minor：repeat-first 聚合、原始组 bootstrap、Q1/Q3 bounded 主口径和合同文件 SHA 锁是否闭合。
6. 是否可关闭 M2-01/M2-02 并授权 S2→S3。

## Main Changes

### M2-01

- 删除 S3 Phase P1 官方测试 Baseline 推理。
- S3/S4 dry-run 改用合成 fixture 或训练侧 validation/LOSO 输出。
- 新增 `src/contract_guard.py`。
- 机器配置登记 13 个训练文件 allowlist、4 个测试文件 denylist、protected phases、G4 PASS/S5 freeze prerequisites、exactly-once 和 release ledger。
- 合成测试验证：提前测试输入拒绝、不完整 freeze 拒绝、完整首次最终释放接受。

### M2-02

- 下游固定 `Q1-B1 / Ridge(alpha=1.0) / seq_time_bounded / q1_clip_0_test_dur_v1`。
- Q1-HGB 不替换下游上游模型。
- 为每个 downstream inner-training 增加第三层 3-fold Q1 OOF。
- 每个 inner-validation 仅接受完整 inner-training 拟合的 Q1 inference。
- LOSO 每折只在剩余 source 内执行选择。
- 保存 409 个 prediction-lineage batches 和 fit-group SHA。
- 合成泄漏 fixture 验证 in-sample 与 inner-validation label bleed 均被拒绝。

## Formal Evidence

正式验证来自干净提交：

`43a856642e9405b0c42cf479160f30cd2dae0653`

| Assertion | Result |
|---|---:|
| Eligible rows / groups | 1,250 / 482 |
| Outer folds / assignments | 15 / 1,446 |
| Downstream-inner assignments | 5,784 |
| Primary nested-upstream assignments | 11,568 |
| Primary lineage batches | 240 |
| LOSO splits | 13 |
| LOSO inner / nested assignments | 5,784 / 11,568 |
| LOSO lineage batches | 169 |
| Total lineage batches | 409 |
| Prediction∩fit overlap total | 0 |
| Downstream-validation/held-out∩fit overlap total | 0 |
| Contract artifact hashes | PASS |
| Synthetic lineage leakage tests | PASS |
| Synthetic official-test guard tests | PASS |
| Q3 synthetic metric tests | PASS |
| Model fits | 0 |
| Official test numeric reads / predictions | 0 / 0 |

Split registry core SHA-256：

`88B108D181C2EA3A723303DED3D0E64BACEF7FA482F8322712ED97ED020A6C2D`

## Deliverables

- [Review response](../work/revisions/gate_2_response.md)
- [Unified solution plan](../work/04_solution_plan.md)
- [Experiment plan](../work/05_experiment_plan.md)
- [Q1 model contract](../work/models/q1_model_contract.md)
- [Q2 model contract](../work/models/q2_model_contract.md)
- [Q3 model contract](../work/models/q3_model_contract.md)
- [O1](../work/optimization/o1_solution_optimization.md)
- [Machine contract](../configs/s2_experiment_plan.json)
- [Run-manifest guard](../src/contract_guard.py)
- [Contract validator](../src/s2_contract_validation.py)
- [Validation summary](../results/raw/s2/contract_summary.md)
- [Validation evidence](../results/raw/s2/contract_validation.json)
- [Split and lineage registry](../results/raw/s2/split_registry.json)

## Verification Commands

```powershell
conda run -n math_modeling python -m py_compile projects/rehearsal_2024_B/src/contract_guard.py projects/rehearsal_2024_B/src/s2_contract_validation.py
conda run -n math_modeling python projects/rehearsal_2024_B/src/s2_contract_validation.py --verify-only
```

复审可重点检查：

- `contract_validation.json → checks`
- `contract_validation.json → synthetic_lineage_tests`
- `contract_validation.json → synthetic_test_release_guard_tests`
- `split_registry.json → primary_upstream_lineage_batches`
- `split_registry.json → loso_upstream_lineage_batches`
- `split_registry.json → lineage_assertions`

## Known Limitations

- 原始 17 个 CSV 继续被 Git 忽略；Reviewer 需按 manifest 在本地恢复。
- feature_schema.json 将在 G2 PASS 后的 S3 训练侧 dry-run 生成，本轮只冻结其机器合同，不伪造文件。
- 第三层 cross-fitting 增加计算量，但上游固定 Ridge、下游候选和时间盒均未扩大。
- 团队实名责任分配与全新环境 clean rebuild 仍待后续完成。

## Boundary

G2 Round 2 审核结果出来前：

- Current Stage 保持 S2；
- S2→S3 未授权；
- 不拟合正式 Baseline，不调参；
- 不读取官方测试数值，不生成测试预测；
- Main Agent 不创建或修改 reviews/gate_2_review_r2.md。

## Requested Verdict

PASS / REVISE / BLOCK
