# Optimization Report — O3 Freeze Decision

## 1. Decision

**O3: FREEZE_CANDIDATE**

S4 selection is closed. Freeze the unique stack below and submit G4; do not run another candidate iteration.

| Question | Frozen model | Full-data configuration | Decision basis |
|---|---|---|---|
| Q1 | Q1-B1 Ridge | alpha=1.0, solver=lsqr, `seq_time_bounded`, `q1_clip_0_test_dur_v1` | unchanged S3 model and sole downstream upstream identity |
| Q2 | Q2-B1A LogisticRegression | C=1.0, class_weight=null, uses_q1=false | both authorized HGB promotion candidates failed +0.02 macro-F1 threshold |
| Q3 | Q3-M1-HGB-UNIFIED | physics-residual Q3-C3; lr=0.05, leaves=15, l2=1.0; no AP-count split | primary S=0.550330; 31.60% gain; 3/3 repeats; bias guards pass |

This decision authorizes only a G4 submission. It does not authorize S5, official-test release or `results/verified/`.

## 2. Inputs to O3

- G3 authorization: review commit `a5433257bf94ab651a53b86244d8a86edc72f9e4`.
- Formal implementation/run commit: `329566748d594e877b57f99cfdddf6796a584d81`.
- Formal run: PASS, 1,751 fits, 0 warnings, 4,791.800 s.
- Validation: 15 primary outer folds, 13 source-blind LOSO, 1,000 group-bootstrap replicates.
- Independent artifact validation: 74/74 checks PASS.
- Actual Q1 lineage: 448 batches, both leakage-overlap totals 0.
- Official test numeric reads/predictions: 0/0.
- Detailed evidence: [07_failure_analysis.md](../07_failure_analysis.md), [08_main_model_report.md](../08_main_model_report.md), [09_evidence_report.md](../09_evidence_report.md).

## 3. Frozen unique full-data configuration rule

The rule was fixed before formal results and is now closed:

1. **Scope:** use only primary downstream-inner validation evidence; test data never participates.
2. **Q2 config:** aggregate all 45 primary inner records for each of four configurations. Maximize fixed-17 macro-F1; within 0.002 maximize accuracy; then minimize log loss and complexity. This selects Q2-C3. Outer promotion decides whether the unweighted/weighted HGB is retained; because neither passes, use Q2-B1A.
3. **Q3 config:** aggregate all 45 primary inner records for each direct/residual candidate. Minimize `max(ARE90_AP, ARE90_system)`; within 0.5% minimize normalized MAE, absolute bias and complexity. This selects physics-residual Q3-C3. Outer promotion decides whether the one AP-count split comparison is retained; unified wins the frozen primary comparison.
4. **Fallbacks:** Q1-B1, Q2-B1A and Q3-B1 remain the only predeclared rollbacks. The final stack uses the first two fallbacks and promotes Q3 only.

No manual choice, official-test observation or post-result threshold change is allowed.

## 4. Q2 stop decision

### Evidence

| Candidate | Primary macro-F1 | Absolute gain | Repeat condition | Accuracy guard | Result |
|---|---:|---:|---|---|---|
| Q2-M1-HGB | 0.351390 | +0.013736 | 3/3 improve | pass | fail F1 threshold |
| Q2-M1W-HGB-WEIGHTED | 0.356656 | +0.019002 | 3/3 improve | pass | fail F1 threshold |
| Q2-M1-Q1-ABLATION | 0.350026 | +0.012372 | diagnostic | pass | not eligible |

Unweighted minority collapse legally triggered the one fixed weighting formula. The weighted candidate came close but remains below +0.02 using full precision. Q1 dependency does not help. The authorized Q2 budget is exhausted, and rare-class/source-blind risk persists.

### Decision

- Stop Q2 HGB development.
- Retain Q2-B1A exactly as the final Q2 component.
- Do not add a second weighting scheme, threshold tuning, class merging, resampling or larger model/grid.

## 5. Q3 freeze decision

### Evidence

| Candidate | Primary S | Relative gain vs Q3-B1 | Repeat improvement | Bias guards | LOSO S |
|---|---:|---:|---:|---|---:|
| Q3-M1-HGB-UNIFIED | **0.550330** | **31.60%** | 3/3 | pass | 0.729921 |
| Q3-M1-HGB-APCOUNT | 0.573131 | 28.77% | 3/3 | pass | **0.685496** |

Both pass the absolute promotion requirements. The AP-count split improves system/LOSO aggregate metrics but is worse on the frozen primary selection score and reduces each training pool. The selection rule therefore retains the unified model. The unified bootstrap interval `[0.50902, 0.60766]` and repeat SD=0.01078 support stability within primary validation.

### Decision

- Promote Q3-M1-HGB-UNIFIED with physics-residual Q3-C3.
- Stop and discard AP-count split as a final architecture; retain its results as a disclosed comparison.
- Preserve exact bounded AP → system sum; no independent system head.
- Do not claim uniform source robustness: worst LOSO source S=2.159764.

## 6. Time box and budget closure

| Family | Authorized budget | Executed | Closure |
|---|---|---|---|
| Q2 | 4 unweighted configs + conditional one weighting formula + one Q1 dependency ablation | exactly executed | exhausted; rollback |
| Q3 | 4 direct + 4 physics-residual configs + one AP-count comparison | exactly executed | exhausted; unified promoted |
| Q1 | no new S4 model | none | unchanged |

Formal runtime stayed below the O2 per-family 2× stop limit. No additional candidate direction is justified or authorized.

## 7. Risk acceptance

FREEZE_CANDIDATE accepts and discloses these residual risks:

- Q2 rare labels with support 1–2 remain weak and cannot support class-specific learnability claims.
- Q2 LOSO macro-F1 remains low; Q2-B1A is a conservative rollback, not a solved classifier.
- Q3 aggregate primary and LOSO improve, but several 3 AP sources have large tail error and bias.
- A03 is only whole-group evaluation exclusion without refit.
- AP-count numeric binary is intentionally retained consistently; no representation-change experiment was run.

None of these risks invalidates the frozen metrics, leakage boundary, arithmetic closure or reproducibility evidence. They must remain visible in the paper and any G5 evidence.

## 8. Rollback and release boundary

- Immutable Baseline snapshot: `2222cf5f4e17a6dac832c4e65f9c5a60cd01060d`.
- Immutable S4 formal source snapshot: `329566748d594e877b57f99cfdddf6796a584d81`.
- If G4 rejects Q3 promotion, rollback is Q3-B1; Q1/Q2 already use their approved baselines.
- Before official-test execution, G4 must PASS and S5 must create a complete freeze manifest plus exactly-once release ledger.
- Official-test output must be generated once without feedback into selection; this O3 decision cannot be reopened from test appearance or ranges.

## 9. Gate action

Submit G4 requesting S4 → S5 authorization. Stop at G4 pending Reviewer verdict.
