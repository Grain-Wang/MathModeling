# Verified Result Registry (S5 freeze + S6 figure resources)

Only evidence listed as `YES` may be used for formal figures or writing. Official-test predictions are unlabeled deployment outputs and must never be presented as measured performance.

| Evidence ID | Claim | Source File | Script / Command | Verified | Notes |
|---|---|---|---|---|---|
| `E-Q1-001` | Frozen Q1 is `Q1-B1` Ridge with bounded primary MAE `5.505416 s`. | `q1_metrics.json`, `freeze_manifest.json` | `s5_validation.py --phase prepare-freeze` | YES | Predictive association only; not a causal effect. |
| `E-Q2-001` | Q2 freezes `Q2-B1A`; its primary fixed-17 Macro-F1 is `0.337654`. | `verified_metrics.json`, `selection_reconstruction.json` | `s5_validation.py --phase prepare-freeze` | YES | Final HGB gain `0.019002 < 0.02`; threshold was not rounded or relaxed. |
| `E-Q3-PIPE-001` | The nested unified HGB selection pipeline has primary `S=0.550330`, a `31.60%` improvement over Q3-B1. | `verified_metrics.json`, `q3_candidate_metrics.json` | `s5_validation.py --phase prepare-freeze` | YES | This is pipeline-level outer OOF evidence, not a fixed residual-C3 score. |
| `E-Q3-CONFIG-001` | The final full-data deployment configuration is `Q3-physics_residual-C3`, selected from 45 primary inner records. | `selection_reconstruction.json`, `freeze_manifest.json` | `s5_validation.py --phase prepare-freeze` | YES | Configuration identity is deliberately separate from `E-Q3-PIPE-001`. |
| `E-Q3-UNC-001` | Q3 pipeline group-bootstrap interval for primary S is `[0.509020, 0.607660]`. | `group_bootstrap_intervals.json` | S4 bootstrap + S5 hash verification | YES | OOF group-resampling interval; it is not full retraining/selection uncertainty. |
| `E-Q3-LOSO-001` | Q3 unified aggregate source-blind LOSO `S=0.729921`; worst held-out source remains `S=2.159764`. | `q3_candidate_metrics.json`, `stratified_metrics.json` | S4 LOSO + S5 hash verification | YES | Supports aggregate improvement only, not every-source robustness. |
| `E-Q3-TRADE-001` | AP-count split has primary `S=0.573131` and LOSO `S=0.685496`; frozen primary rule therefore retains unified. | `q3_candidate_metrics.json`, `selection_reconstruction.json` | `s5_validation.py --phase prepare-freeze` | YES | Controlled comparison, not an independent confirmatory test. |
| `E-FREEZE-001` | Q1/Q2/Q3 IDs, parameters, schemas, labels, postprocessing, inputs and output order are frozen with `selection_closed=true`. | `freeze_manifest.json`, `freeze_manifest.sha256` | `s5_validation.py --phase prepare-freeze` | YES | Freeze SHA-256 is the release prerequisite. |
| `E-RELEASE-001` | Exactly one official-test release succeeded under release ID `S5-A4AA45A0491C-20260911T110151+0800`. | `final_release_verification.json`, raw final ledger and release manifest | `s5_release.py`; `s5_validation.py --phase finalize-release` | YES | Four unlabeled prediction artifacts; not performance evidence and no feedback to model selection. |
| `E-RELEASE-SUM-001` | Q3 system predictions are strict sums of bounded AP predictions; Q2 probabilities close over the frozen 17-label order. | `official_q2_ap_predictions.jsonl`, `official_q3_ap_predictions.jsonl`, `official_q3_system_predictions.jsonl` | `s5_validation.py --phase finalize-release` | YES | 10 cross-artifact checks plus 12 per-file schema/order checks passed. |
| `E-DATA-001` | S1 training audit records 1,252 raw AP rows, A01 isolates 2, leaving 1,250 eligible AP rows and 482 strict groups. | `figure_data/fig02_data_quality.json` | `s6_eight_figure_resources.py`; G1/R2-reviewed S1 Git blob verified | YES | Training-side data quality only; other anomalies are not all deleted. |
| `E-Q1-IMP-001` | Q1 feature-family permutation/ablation values are audited held-out predictive contributions. | `q1_feature_family_importance.json`, `figure_data/fig06_model_selection.json` | S3 run-manifest SHA + S3 validation PASS + S6 copy/hash verification | YES | Not causal; do not interpret Ridge coefficient signs as effects. |
| `E-Q2-CONF-001` | Q2-B1A has three fixed-17 primary OOF confusion matrices, each covering the same 1,250 training AP rows. | `q2_baseline_metrics.json`, `figure_data/fig05_prediction_diagnostics.json` | S5 verified hash + S6 label/order/count assertions | YES | Three repeats are not 3,750 independent observations. |
| `E-Q3-OOF-001` | Q3 unified primary repeat-0 has 1,250 AP and 482 system OOF predictions, with exact AP component sets and bounded system sums. | `figure_data/fig04_q3_core_result.json`, `figure_data/fig05_prediction_diagnostics.json` | G4 consumed-artifact SHA + S6 coverage/sum/MAE assertions | YES | Training-side OOF only; repeat-0 plots are illustrative, three-repeat metrics remain authoritative. |

## Eight-figure resource rebuild

~~~powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s6_eight_figure_resources.py
~~~
This generates only verified figure data/specifications, not images or new model predictions. Do not rerun the S5 release or use official-test predictions as measured performance.

## Archived S5 post-release verification

Historical S5 validation commands are retained for provenance only; do not rerun `finalize-release` on this S6 snapshot because it rewrites verified manifests:

~~~powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_validation.py --phase finalize-release
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_release.py --preflight-only
~~~

At the original S5 gate, the first command passed and the second exactly-once negative test failed as intended. The fresh pre-release sequence is archived in `work/10_result_freeze.md`; do not rerun its prepare/release steps on the current snapshot.
