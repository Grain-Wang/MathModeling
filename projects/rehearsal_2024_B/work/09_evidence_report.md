# S4 Evidence Report

## 1. Evidence verdict

- Formal S4 run: PASS
- Independent artifact validation: PASS
- Selection closed: yes
- O3 candidate uniqueness: yes
- Official test numeric access/prediction: 0 / 0
- `results/verified/` writes: none
- Gate status: G4 pending; Main Agent does not self-approve G4

## 2. Provenance chain

| Item | Evidence |
|---|---|
| G3 authorization | review commit `a5433257bf94ab651a53b86244d8a86edc72f9e4` |
| Formal implementation/run commit | `329566748d594e877b57f99cfdddf6796a584d81` |
| Formal Git status before outputs | empty / clean |
| Formal start / finish | 2026-09-09T19:36:22+08:00 / 2026-09-09T20:56:14+08:00 |
| Runtime / fits / warnings | 4,791.800 s / 1,751 / 0 |
| Python / scikit-learn | 3.11.11 / 1.7.1 |
| Formal generation sources unchanged at validation | true |
| Formal run head is validation-head ancestor | true |
| Independent validator SHA-256 | `2442739C7FA9B6A17430DDC5F8E2D19EBB70E395EDE0FB02EE2D3669CA186A9D` |
| Validation consumed artifacts | 22, each recorded with hash |

`validation_manifest.json` independently records validator identity, validation command, Git head/status, consumed artifact hashes and validation output hash. Validation only reads committed/formal JSON and gzip JSONL artifacts; it does not read raw CSV.

The validation working-tree status records the untracked formal result directory and an unrelated `.gitignore` edit for local `sshconfig.md`. The formal run itself started clean, and the manifest proves all formal model-generation source hashes remained unchanged.

## 3. Frozen hashes and input guard

| Artifact/contract | SHA-256 |
|---|---|
| S1/S2 base config | `5C2AD614190F64AA67D699F2925808434BED4B8CF8B24B036ABD9AF0B352683A` |
| S4 candidate plan | `C1C35E93AF0196B1F04E6F3F65E39997FA829164FC588296E96592219274C811` |
| Split registry file | `B20D719E287D4F4D295D2EC497F13226C7A80C5986B70CA2269E1016BDAA3FF7` |
| Split registry core | `88B108D181C2EA3A723303DED3D0E64BACEF7FA482F8322712ED97ED020A6C2D` |
| Base feature schema | `DD9569F8F9707F2B951AD18F75CD109F0E4AC23AA2B7717FA0F98D8FDF669C59` |
| S4 feature schema | `E3B998D7231B3CFF6BA8C644E21931F40C82ED2AFAA27A037A3BB922D8CCFF73` |

S4 entry behavior:

1. validates phase=`S4`, training allowlist, canonical path, file size and SHA before any CSV numeric parser;
2. rejects each of four official test injection fixtures before parsing;
3. numerically reads exactly 13 training CSV files;
4. hashes all 17 raw files for identity, but never parses official test values;
5. verifies the frozen G3 PASS review and immutable S3 Baseline snapshot.

## 4. Coverage and selection evidence

| Check | Formal result |
|---|---|
| Eligible AP rows / system groups | 1,250 / 482 |
| Primary boundaries | 3 repeats × 5 folds = 15 |
| Source-blind LOSO | 13 held-out sources |
| Q2 inner grid | exactly 4 fixed configs |
| Q2 weighting formulas | exactly 1; condition triggered |
| Q3 inner candidates | exactly 8: 4 direct + 4 physics-residual |
| Q3 AP-count comparisons | exactly 1 |
| Q2 primary prediction rows | complete for each evaluated model×repeat |
| Q3 primary AP/system rows | complete for each model×repeat |
| LOSO rows/groups | 1,250 AP / 482 system for each reported model |
| Group bootstrap | 1,000 replicates, seed=202412, three repeats kept together |

The final full-data configuration rule uses only the 45 primary downstream-inner records per candidate and the frozen lexicographic tie rules. Outer promotion decides only weighting/AP-count-split retention. No official test evidence participates.

## 5. Leakage and upstream-lineage evidence

Formal actual Q1 lineage assertions:

| Check | Result |
|---|---:|
| Total actual batches | 448 |
| Primary batches | 240 |
| LOSO batches | 208 |
| prediction ∩ fit overlap | 0 |
| downstream validation ∩ fit overlap | 0 |
| Upstream identity | fixed Q1-B1 / bounded / v1 |

The independent validator checks the stored prediction-fit hashes, held-out identifiers, roles and batch counts. Q2's no-Q1 main path remains independent of this optional feature; Q2's one with-Q1 ablation and Q3's fixed Q1 inputs use the nested registry.

## 6. Metric and physical recomputation

Independent validation recomputed from artifacts:

- global checks: 25;
- selection checks: 14;
- Q2 checks: 16;
- Q3 checks: 19;
- total: 74, all PASS.

It verifies:

- Q2 fixed 17-label probability order, missing-class zeros, normalization, coverage and stored metrics;
- Q3 AP/system coverage, finite/nonnegative bounded predictions and stored metrics;
- exact system reconstruction from the sum of bounded AP predictions;
- relative-error denominator counts and separately recorded zero-truth absolute errors;
- candidate/weighting/split budgets, inner trace counts and final promotion consistency;
- bootstrap contract, formal metadata, output hashes and absence of `results/verified/` writes.

## 7. Evidence for final decisions

### Q2 rollback

- Q2-M1-HGB gain: +0.013736 macro-F1; FAIL `<0.02`.
- Q2-M1W-HGB-WEIGHTED gain: +0.019002; FAIL `<0.02`.
- Accuracy guard and 2/3 repeat condition pass, but every required condition is conjunctive.
- With-Q1 ablation is not eligible and does not improve the no-Q1 candidate.
- Final: Q2-B1A rollback.

### Q3 promotion

- Q3-M1-HGB-UNIFIED primary S=0.550330 vs Q3-B1=0.804609, relative improvement=31.60%.
- Repeat improvement=3/3; AP and system bias guards pass.
- AP-count split primary S=0.573131; it passes promotion but loses the frozen primary comparison.
- Final: unified physics-residual Q3-C3.

### Sensitivity and stress

- A03 is explicitly tagged `evaluation_exclusion_diagnostic_only_no_training_robustness_claim`.
- AP-count uses `numeric_binary_2_or_3_shared_by_all_s4_candidates`.
- Q3 unified LOSO S=0.729921, but worst held-out source S=2.159764; no universal robustness claim.
- Q2 weighted LOSO macro-F1=0.167729; rare-class/source risk remains.

## 8. G3 finding closure

| G3 finding | S4 closure |
|---|---|
| Minor-01 AP-count wording/implementation | Numeric binary 2/3 is explicit in config, run manifest and final model report; all candidates share it |
| Minor-02 A03 overclaim risk | Only evaluation-exclusion diagnostic; no training robustness wording |
| Minor-03 validator provenance | Separate `validation_manifest.json` with validator hash, Git status/head, consumed artifact hashes and output hash |
| Advisory-01 concrete failures | 20 Q2 rows + 20 Q3 AP rows + 20 Q3 system groups stored; worst sources summarized in work/07 |
| Advisory-02 support 1–2 caution | Reports explicitly prohibit strong learnability claims |

## 9. Artifact map

| Evidence class | Main artifacts |
|---|---|
| Configuration | `configs/s4_candidate_plan.json`, `experiments/main/s4_main.json` |
| Comparison/ablation | `experiments/comparison/`, `experiments/ablation/` |
| Sensitivity/robustness | `experiments/sensitivity/`, `experiments/robustness/` |
| Predictions | gzip Q2, Q3 AP and Q3 system JSONL under `results/raw/main/` |
| Selection | `q2_selection.json`, `q3_selection.json`, `promotion_decision.json`, `final_candidate.json` |
| Metrics | Q2/Q3 candidate metrics, Q3 CDF, bootstrap, strata, A03 and failure cases |
| Leakage | `q1_actual_upstream_lineage.json` |
| Provenance | `run_manifest.json`, `post_run_validation.json`, `validation_manifest.json` |
| Human reports | work/07, work/08, work/09 and optimization/O3 |

## 10. Gate readiness and remaining release boundary

All S4 and O3 evidence required by G3 is present. The only valid next action is submit G4 with O3=`FREEZE_CANDIDATE` and wait for Reviewer.

Still forbidden:

- reading, predicting or manually inspecting official test numeric values before G4 PASS and S5 freeze manifest completion;
- writing any S4 result to `results/verified/`;
- changing the candidate, grid, label set, split, metric or bounded/system-sum rule;
- treating aggregate LOSO or A03 evaluation exclusion as universal training robustness.

G2's exactly-once release ledger remains due at the S5 official-test entry. This evidence report establishes readiness for G4 review, not permission to release the test set.
