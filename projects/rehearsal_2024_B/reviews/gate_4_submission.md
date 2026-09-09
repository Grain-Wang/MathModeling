# Gate 4 Submission

## Stage

S4 — 主模型改进与证据构建

## Review Snapshot

- G3 authorization review commit: `a5433257bf94ab651a53b86244d8a86edc72f9e4`
- Formal implementation/run commit: `329566748d594e877b57f99cfdddf6796a584d81`
- Formal S4 run status: PASS
- Independent post-run validation: PASS
- O3 decision: `FREEZE_CANDIDATE`
- Submission bundle: containing commit of this file
- Requested transition: S4 → S5
- Main Agent does not self-approve G4; S5 and official-test release remain forbidden until Reviewer PASS.

## Deliverables

- [S4 failure analysis](../work/07_failure_analysis.md)
- [S4 main model report](../work/08_main_model_report.md)
- [S4 evidence report](../work/09_evidence_report.md)
- [O3 freeze decision](../work/optimization/o3_freeze_decision.md), decision=`FREEZE_CANDIDATE`
- `configs/s4_candidate_plan.json`
- `experiments/main/s4_main.json`
- `experiments/comparison/baseline_comparison.json`
- `experiments/ablation/q1_and_architecture.json`
- `experiments/sensitivity/a03_and_ap_count.json`
- `experiments/robustness/source_blind_loso.json`
- `results/raw/main/` formal predictions, metrics, selection traces, failure cases and manifests
- `src/s4_io.py`, `src/s4_selection.py`, `src/s4_main.py`, `src/s4_validation.py`
- updated decisions / experiments / AI usage / CURRENT

No file has been written to `results/verified/`.

## Verification Commands

~~~powershell
conda run -n math_modeling python -m py_compile projects/rehearsal_2024_B/src/s4_io.py projects/rehearsal_2024_B/src/s4_selection.py projects/rehearsal_2024_B/src/s4_main.py projects/rehearsal_2024_B/src/s4_validation.py
conda run -n math_modeling python projects/rehearsal_2024_B/src/s4_main.py --verify-only
conda run -n math_modeling python projects/rehearsal_2024_B/src/s4_validation.py --check-only
git diff --check
git ls-files "projects/rehearsal_2024_B/**/*.csv"
git ls-files --others --ignored --exclude-standard "projects/rehearsal_2024_B/**/*.csv"
~~~

The formal model command ran from clean commit `3295667`. The independent validator reads only the committed/formal JSON and gzip JSONL artifacts and records its own provenance in `validation_manifest.json`.

## Frozen Final Stack

| Question | Frozen model | Decision |
|---|---|---|
| Q1 | Q1-B1 Ridge, bounded v1 | unchanged |
| Q2 | Q2-B1A LogisticRegression(C=1.0), no Q1 | HGB candidates failed threshold; rollback |
| Q3 | Q3-M1-HGB-UNIFIED, physics-residual Q3-C3 | promoted |

The Q3 full-data configuration is `learning_rate=0.05`, `max_leaf_nodes=15`, `l2_regularization=1.0`, no AP-count split. System throughput has no independent head and equals the exact sum of bounded AP predictions.

## Main Claims

1. **The G3 boundary was followed exactly.**
   - Q2 used four frozen unweighted HGB configs, one conditionally triggered fixed weighting formula and one with-Q1 dependency ablation.
   - Q3 used four direct plus four physics-residual configs and exactly one AP-count split comparison.
   - No Q1-HGB, expanded grid, additional weighting, new model family or independent system head was run.

2. **The real S4 entry guard remains sealed against official test data.**
   - It validates S4 authorization, 13-file training allowlist, paths, sizes, hashes, contracts and Baseline snapshot before numeric parsing.
   - Four official-test injection cases are rejected before parser access.
   - Formal official-test numeric read / prediction count = 0 / 0.

3. **Nested selection and actual upstream lineage are complete.**
   - 15 primary outer folds and 13 source-blind LOSO splits ran.
   - Full-data configs use 45 primary inner records per candidate and frozen lexicographic rules.
   - Actual Q1 lineage has 448 batches: primary 240 + LOSO 208.
   - prediction∩fit=0 and downstream-validation∩fit=0.

4. **Q2 correctly stops and rolls back.**
   - Q2-M1-HGB primary fixed-17 macro-F1=0.351390, gain=+0.013736.
   - Minority collapse triggered the only authorized weighting run.
   - Q2-M1W-HGB-WEIGHTED macro-F1=0.356656, gain=+0.019002, still below +0.02 at full precision.
   - Q1 ablation does not improve the candidate.
   - Final Q2 remains Q2-B1A; thresholds were not relaxed.

5. **Q3 meets promotion conditions.**
   - Q3-M1-HGB-UNIFIED primary S=0.550330 vs Q3-B1=0.804609, a 31.60% reduction.
   - It improves 3/3 repeats and passes AP/system bias guards.
   - AP/system ARE90=0.550330/0.189701; AP/system median bias=-0.006036/-0.001447.
   - Selection-score group-bootstrap 95% interval=`[0.50902, 0.60766]`.

6. **The AP-count comparison is disclosed and stopped.**
   - Split primary S=0.573131 and LOSO S=0.685496; unified primary/LOSO S=0.550330/0.729921.
   - Both pass absolute promotion, but frozen primary selection retains unified.
   - The split result remains comparison evidence and is not the final architecture.

7. **Robustness limits are not hidden.**
   - Q2 weighted LOSO macro-F1=0.167729 and rare classes remain weak.
   - Q3 unified LOSO S=0.729921, but worst source S=2.159764.
   - Twenty Q2 rows, twenty Q3 AP rows and twenty Q3 system groups are stored as diagnostic failures.
   - No universal source or support=1–2 learnability claim is made.

8. **G3 Minor and Advisory findings are closed.**
   - AP-count is explicitly numeric binary 2/3 and shared by every S4 candidate.
   - A03 is named only `evaluation-exclusion diagnostic`; no delete-group refit claim.
   - A separate validation manifest stores validator hash, Git state, input hashes and output hash.
   - Concrete high-error samples/groups and rare-class cautions are included.

9. **Independent validation passed.**
   - 25 global + 14 selection + 16 Q2 + 19 Q3 checks = 74 PASS.
   - Metrics are recomputed from predictions.
   - Q3 system sums, budgets, trace counts, lineage, bootstrap, promotion and output boundaries are verified.
   - Formal model-generation sources were unchanged after the formal run.

10. **O3 produces one closed candidate and stop decision.**
    - Q1-B1 + Q2-B1A + Q3-M1-HGB-UNIFIED is the only final stack.
    - No S4 direction remains open.
    - O3=`FREEZE_CANDIDATE`; test data was not used.

## G4 Evidence Checklist

| Required evidence | Artifact / result |
|---|---|
| work/07 failure analysis | complete; high-error rows/groups + source/strata risks |
| work/08 main model report | complete; selection, comparison, ablation, final stack |
| work/09 evidence report | complete; provenance, leakage, recomputation, finding closure |
| main/comparison/ablation/sensitivity/robustness configs | present |
| results/raw/main | formal JSON/gzip evidence present |
| Q2 conditional weighting gate | triggered once; no second formula |
| Q3 direct/residual and split budgets | 8 candidates + exactly 1 split comparison |
| Actual nested upstream lineage | 448 batches; overlaps 0 |
| Independent validation provenance | separate manifest; PASS |
| O3 | `FREEZE_CANDIDATE`; unique final stack |
| Official test sealing | numeric read/prediction=0/0 |
| Verified boundary | no `results/verified/` writes |

## Known Limitations

1. Q2 falls back to the S3 Logistic model; rare classes and source-blind classification remain weak.
2. Q3 has substantial per-source variation despite strong aggregate primary/LOSO improvement.
3. The unified-versus-split Q3 choice follows primary evidence; split has a better LOSO aggregate and remains a disclosed tradeoff.
4. A03 excludes groups from evaluation only and does not prove training robustness.
5. AP-count remains numeric binary for comparability rather than changing to a new encoded representation.
6. Raw inputs are absent from Git and must be restored exactly by manifest.
7. The exactly-once official-test release ledger remains due after G4 PASS and before S5 inference.

## Requested Verdict

**PASS**, authorizing S4 → S5 for final freeze-manifest construction and the governed exactly-once official-test release.

If any candidate-budget, nested-lineage, metric recomputation, Q3 sum, provenance or test-sealing defect is found, return **REVISE** and do not authorize S5.
