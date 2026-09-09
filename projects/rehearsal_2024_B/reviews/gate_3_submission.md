# Gate 3 Submission

## Stage

S3 — 全题 Baseline 闭环

## Review Snapshot

- G2 authorization review commit: 6504c54782dc33e111800b3166e9e1766cab6549
- Formal implementation/run commit: 2222cf5f4e17a6dac832c4e65f9c5a60cd01060d
- Formal Baseline run status: PASS
- Independent post-run validation: PASS
- Submission bundle: containing commit of this file
- Requested transition: S3 → S4
- Main Agent does not self-approve G3; S4 remains forbidden until Reviewer PASS.

## Deliverables

- [Baseline report](../work/06_baseline_report.md)
- [O2 Baseline diagnosis](../work/optimization/o2_baseline_diagnosis.md), decision=PROCEED_TO_G3
- [S3 executable entry](../src/s3_baseline.py)
- [Independent validator](../src/s3_validation.py)
- experiments/baseline/q1_baseline.json
- experiments/baseline/q2_baseline.json
- experiments/baseline/q3_baseline.json
- results/raw/baseline/run_manifest.json
- results/raw/baseline/post_run_validation.json
- results/raw/baseline/feature_schema.json
- gzip JSONL OOF/cross-fit/AP/system predictions
- Q1/Q2/Q3 metrics, Q3 CDF, Q2 support, actual lineage, strata, A03, feature-family influence, group bootstrap
- updated decisions / experiments / AI usage / CURRENT

No file has been written to results/verified/.

## Verification Commands

~~~powershell
conda run -n math_modeling python -m py_compile projects/rehearsal_2024_B/src/s3_features.py projects/rehearsal_2024_B/src/s3_metrics.py projects/rehearsal_2024_B/src/s3_io.py projects/rehearsal_2024_B/src/s3_lineage.py projects/rehearsal_2024_B/src/s3_models.py projects/rehearsal_2024_B/src/s3_evaluation.py projects/rehearsal_2024_B/src/s3_baseline.py projects/rehearsal_2024_B/src/s3_validation.py
conda run -n math_modeling python projects/rehearsal_2024_B/src/s3_baseline.py --verify-only
conda run -n math_modeling python projects/rehearsal_2024_B/src/s3_validation.py
git diff --check
git ls-files "projects/rehearsal_2024_B/**/*.csv"
git ls-files --others --ignored --exclude-standard "projects/rehearsal_2024_B/**/*.csv"
~~~

The formal model command was executed from clean commit 2222cf5. It accepts only the local 13 training CSVs from the frozen allowlist.

## Main Claims

1. **The real S3 entry guard is connected.**
   - The phase manifest is validated before any pd.read_csv.
   - It records phase/input kind, canonical paths, names, input SHA, config SHA, guard SHA and guard result.
   - Four official-test injection cases are rejected before numeric parsing.
   - Formal official-test numeric read / prediction count = 0 / 0.

2. **The actual training-side feature engine generated the schema.**
   - 312 fixed derived features.
   - Every feature contains name/dtype/unit/missing_semantics/column_order.
   - 2 AP and 3 AP columns align exactly.
   - Schema SHA-256: DD9569F8F9707F2B951AD18F75CD109F0E4AC23AA2B7717FA0F98D8FDF669C59.

3. **All eight frozen Baselines ran.**
   - Q1-B0/B1, Q2-B0/B1A/B1B, Q3-B0/B1/B2.
   - 327 fits, no tuning, no HGB, formal warning count=0.

4. **Primary and mandatory stress validation are complete.**
   - 15 grouped outer folds and 13 source-blind LOSO splits.
   - Every model×repeat has 1,250 AP OOF rows.
   - Every Q3 model×repeat has 482 system OOF groups.
   - 1,000 group-bootstrap replicates preserve all three repeat predictions.

5. **Actual downstream Q1 lineage is closed.**
   - Q1-B1 / seq_time_bounded / q1_clip_0_test_dur_v1 only.
   - Primary 60 + LOSO 52 = 112 actual batches.
   - prediction∩fit=0 and held-out∩fit=0.

6. **Q1 Baseline is usable.**
   - Q1-B1 primary MAE=5.5054 s vs Q1-B0=11.1226 s.
   - B1 95% group-bootstrap interval=[5.1977, 5.8370] s.
   - LOSO MAE=7.0266 s; clip fraction=0.
   - Mechanism/peer/desired RSSI ablation direction is positive in 3/3 repeats.

7. **Q2 closes the task but exposes a real rare-class problem.**
   - Q2-B1A primary fixed-17 macro-F1=0.3377, accuracy=0.7552.
   - LOSO macro-F1=0.1609.
   - Q1 OOF does not improve the Logistic Baseline.
   - Several support 1–2 labels collapse, fully disclosed.
   - A03 whole-group evaluation exclusion does not change the conclusion.

8. **Q3 AP/system closure and metrics are exact.**
   - Q3-B1 primary S=0.8046; AP/system ARE90=0.8046/0.3481.
   - Q3-B2 primary S=0.8556 but LOSO S=0.9347 vs B1 LOSO=1.3233.
   - All bounded AP predictions are finite/nonnegative.
   - Every system prediction equals the sum of bounded AP predictions within 1e-9; stored/recomputed error is 0.
   - Five zero AP truths are excluded from relative denominators without epsilon.

9. **O2 is evidence-driven and bounded.**
   - Decision=PROCEED_TO_G3.
   - Only two S4 directions are selected: Q2 finite HGB with at most one conditional fixed weighting run; Q3 direct vs physics-residual HGB with one conditional AP-count split comparison.
   - Q1-HGB, broad split modeling, larger grids, deep learning and independent system heads are not authorized.

## G3 Evidence Checklist

| Required evidence | Artifact / result |
|---|---|
| Guard before training parse | run_manifest preflight + src/s3_io.py |
| Contract/config/guard/split hashes | run_manifest; all PASS |
| Real feature schema and 2/3 AP alignment | feature_schema.json; PASS |
| Eight runs and failure handling | experiments/baseline + run_manifest |
| 15 primary folds | all model×repeat coverage PASS |
| 13 source-blind LOSO | all models complete |
| Actual upstream OOF/inference lineage | q1_actual_upstream_lineage.json; 112, overlaps 0 |
| Q2 17 classes/support/missing/A03 | q2_class_support.json + a03_sensitivity.json |
| Q3 bounded AP/system and exact sum | q3 metrics/predictions + validator; PASS |
| No official-test numerical access | read/prediction=0/0; injection tests PASS |
| O2 failure diagnosis | PROCEED_TO_G3; two bounded directions |

## Known Limitations

1. Q2 rare classes remain poorly learned; fixed-label macro-F1 and LOSO expose the limitation.
2. Q3 has a large 3 AP/source-extrapolation gap; B1 and B2 show a primary-vs-LOSO tradeoff.
3. Q1 3 AP MAE exceeds 2 AP, but Q1-B1 remains the frozen downstream upstream and rollback.
4. A03 sensitivity excludes complete groups from OOF evaluation without a separate refit; effect is negligible and no label is changed.
5. Raw inputs are intentionally absent from Git and must be restored exactly by manifest.
6. G2 Minor-02 exactly-once ledger remains due before G4/S5 final release.
7. The unique final full-data configuration rule remains due in S4/O3.

## Unresolved Risks

- HGB may not improve Q2 labels with support 1–2.
- Q3 nonlinear models may overfit source-correlated legal features.
- Conditional AP-count split reduces each training pool and must meet the same promotion threshold.
- No result in this submission is yet approved for results/verified/.

## Requested Verdict

**PASS**, authorizing S3 → S4 under the two directions and limits frozen in O2.

If any coverage, lineage, metric, test-governance or reproducibility defect is found, return **REVISE**; do not authorize S4.
