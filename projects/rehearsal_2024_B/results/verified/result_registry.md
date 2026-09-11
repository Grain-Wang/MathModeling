# S5 Verified Result Registry

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

## Reproduction commands

~~~powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_validation.py --phase prepare-freeze
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_release.py --preflight-only
~~~

The second command is a no-parse guard check before release. After one successful release it must fail by design.
