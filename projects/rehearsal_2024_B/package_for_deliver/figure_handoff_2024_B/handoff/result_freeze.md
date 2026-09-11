# S5 Result Freeze

## Status

- Stage: `S5 — 结果核验、冻结与交接`
- G4 authorization: PASS, review commit `70d6a1436192339c61c749188e104b15cf4bbbb7`
- Selection: closed; no S4 model, grid, weight, threshold, AP-count structure, postprocess, label order or metric was reopened
- Freeze source commit: `474acb71dfc0bcaa27e6cca908c2243efa65660f`
- Pre-release freeze commit: `473a8ad8bf04cfa7d62511dadbe620f3a6ba8570`
- Freeze manifest SHA-256: `A4AA45A0491C35C1D816164AADABB20998E9984D7521AFDE55D01A8B027E5E6D`
- Official release ID: `S5-A4AA45A0491C-20260911T110151+0800`
- Exactly-once state: one successful release; second release guard returns a hard failure
- Current gate: G5, pending independent Reviewer

## Frozen model stack

| Question | Frozen model | Deployment details |
|---|---|---|
| Q1 | `Q1-B1` Ridge | `alpha=1`, `solver=lsqr`; `seq_time` clipped to `[0,test_dur]` by `q1_clip_0_test_dur_v1` |
| Q2 | `Q2-B1A` LogisticRegression | `C=1`, no Q1 input; probabilities aligned to the frozen 17-label order |
| Q3 | `Q3-M1-HGB-UNIFIED` | final full-data configuration `Q3-physics_residual-C3`; `learning_rate=0.05`, `max_iter=200`, `max_leaf_nodes=15`, `min_samples_leaf=20`, `l2_regularization=1`, `early_stopping=false`, `random_state=202409`; AP-count is a shared numeric 2/3 feature, not a split model |

The actual preprocessing is recorded faithfully: numerical inputs use training-side median imputation with missing indicators and `StandardScaler`, including HGB inputs; protocol uses most-frequent imputation and unknown-safe one-hot encoding. This closes G4 Minor-03 without changing or rerunning S4 model selection.

Q3 full-data training uses the mean of the three registered Q1-B1 bounded primary outer-OOF predictions as its training-side upstream feature. Deployment uses Q1-B1 fitted on all 1,250 eligible training rows. The physical base fits full-training eta, clipped to `[0,1]`, with a full-training Q3-B1 Ridge fallback for missing PHY rates. Final AP predictions are nonnegative; system prediction is strictly the sum of bounded AP predictions.

## Independent S5 reconstruction

`src/s5_validation.py` does not import the production `evaluate_q2` or `evaluate_q3` functions. It directly reads selection traces, Q2/Q3 OOF rows, S3 Baseline evidence and the frozen candidate plan, then independently reconstructs:

1. Q2 four-configuration lexicographic selection and full-data C3 identity;
2. Q2 fixed-17 Macro-F1, repeat comparisons and exact `0.0190017375 < 0.02` rollback;
3. Q3 eight-candidate lexicographic selection and residual-C3 identity from 45 primary inner records;
4. Q3 nearest-rank AP/system ARE90, repeat and bias guards;
5. unified/AP-count promotion and final unified choice;
6. correspondence with the frozen final candidate.

All six selection/promotion conclusions passed. The prior S4 artifact manifest and its 74/74 validation result were hash-checked before results entered `results/verified/`.

## Evidence identity boundary

- `E-Q3-PIPE-001` / `Q3_NESTED_SELECTION_PIPELINE_PERFORMANCE`: outer OOF performance of the unified HGB pipeline that executes frozen inner selection independently inside each training boundary. Primary `S=0.550330`, relative gain `31.60%` versus Q3-B1.
- `E-Q3-CONFIG-001` / `Q3_FINAL_FULL_DATA_CONFIGURATION`: residual-C3 selected for final full-data deployment from 45 primary inner records.

These identities are not interchangeable. The project does not claim that a fixed residual-C3 model itself directly obtained outer OOF `S=0.550330`, and it does not attribute all pipeline gain to the residual architecture alone.

## Exactly-once release

Before any official CSV parser ran, the release entry independently derived from disk that:

- the real G4 review exists, hash-matches and authorizes S5;
- freeze manifest and sidecar exist and hash-match;
- every frozen source file still matches its hash;
- the actual ledger has zero prior successful releases and no unresolved RUNNING attempt;
- all four official test files match frozen filename, size and SHA-256 identities;
- the final release directory does not exist;
- feedback targets are empty.

The successful attempt records its immutable release ID, timestamps, four input hashes, freeze hash, release-manifest hash, and all model/output hashes. A second `--preflight-only` call exits with `ContractBoundaryError: a successful official-test release already exists`.

Formal run summary:

| Item | Value |
|---|---:|
| Runtime | 29.320 s |
| Full-data model fits | 4 |
| Training CSV numeric reads | 13 |
| Official-test CSV numeric reads | 4 |
| Warnings | 0 |
| Q1 rows | 185 |
| Q2 rows | 151 |
| Q3 AP rows | 185 |
| Q3 system rows | 75 |

The post-release validator passed 10 cross-artifact checks plus 12 per-file schema/order checks. Official predictions are unlabeled deployment outputs and are not performance evidence. No prediction value or distribution was used to alter a model or return to O2/O3/S4.

## Verified evidence

The authoritative index is [`results/verified/result_registry.md`](../results/verified/result_registry.md). Important machine artifacts are:

- `freeze_manifest.json` and `freeze_manifest.sha256`;
- `selection_reconstruction.json` and `verified_metrics.json`;
- verified S3/S4 metric, uncertainty, stratification and failure-case files;
- `final_release_verification.json`;
- `official_q1_ap_predictions.jsonl`, `official_q2_ap_predictions.jsonl`, `official_q3_ap_predictions.jsonl`, and `official_q3_system_predictions.jsonl`.

## Reproduction and guards

Fresh pre-release snapshot only:

~~~powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_validation.py --phase prepare-freeze
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_release.py --preflight-only
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_release.py
~~~

Current post-release snapshot:

~~~powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_validation.py --phase finalize-release
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_release.py --preflight-only
~~~

The first current command must pass; the second must fail because the exactly-once release has already succeeded.

## Remaining limitations

- Q2 rare classes with support 1–2 remain weakly learnable and source-blind Macro-F1 remains low.
- Q3 aggregate primary and LOSO evidence improves, but the worst held-out source still has `S=2.159764`; no every-source robustness claim is allowed.
- The Q3 group-bootstrap interval resamples existing OOF groups and is not full model-retraining/selection uncertainty.
- unified versus AP-count split is one controlled comparison on shared outer evidence, not an independent confirmatory test.
- Official predictions have no labels and cannot validate accuracy.
- Local CSV provenance is limited to equality with the S0 manifest; the official archive URL and archive-level hash remain unavailable.

S5 is complete as a Main Agent work product and is submitted to G5. This document does not self-approve G5 or authorize S6.
