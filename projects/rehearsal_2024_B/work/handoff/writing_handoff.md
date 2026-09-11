# Writing Handoff — rehearsal_2024_B

## Technical storyline

The paper should follow one consistent chain:

1. build topology-aware, question-specific pre-event features from configuration and inter-node RSSI;
2. use grouped, nested validation with `source_file + test_id` as an indivisible unit and separate source-blind LOSO evidence;
3. solve Q1 with bounded Ridge, Q2 with a fixed-17 joint classifier, and Q3 with a nonnegative physics-residual HGB pipeline whose system output is the sum of AP outputs;
4. compare only pre-registered candidates, retain negative results, freeze the unique stack, and report limits;
5. use the frozen stack once on official unlabeled test inputs under the exactly-once ledger.

Writers must use only `results/verified/` and the Evidence IDs in `result_registry.md`.

## Answers by question

### Q1 — AP sending opportunity

- Frozen model: `Q1-B1`, Ridge with `alpha=1`, deterministic LSQR.
- Inputs: pre-event topology, traffic/configuration and RSSI-derived features; no `nss`, `mcs`, post-event performance fields, identifiers or true `seq_time` as predictors.
- Output: raw `seq_time` and bounded `min(max(raw,0),test_dur)` in seconds.
- Primary bounded MAE: `5.505416 s` (`E-Q1-001`).
- Interpretation: predictive contribution/conditional association only. Do not make a causal claim from feature importance.

### Q2 — joint NSS/MCS state

- Frozen model: `Q2-B1A` LogisticRegression, `C=1`, no Q1 feature.
- Output: one label from the fixed 17-label joint state space plus an aligned probability vector.
- Primary fixed-17 Macro-F1: `0.337654` (`E-Q2-001`).
- The best authorized weighted HGB gain was `+0.019002`, below the exact `+0.02` promotion threshold, so the model correctly rolled back.
- Preserve the negative conclusion: support-1–2 rare classes and source-blind generalization remain weak.

### Q3 — AP and system throughput

- Validated performance identity: the nested unified HGB selection pipeline, not a single fixed configuration, has primary `S=0.550330`, a `31.60%` reduction relative to Q3-B1 (`E-Q3-PIPE-001`).
- Deployment configuration identity: applying the frozen full-data rule to 45 primary inner records selects `Q3-physics_residual-C3` (`E-Q3-CONFIG-001`).
- Final configuration: learning rate `0.05`, 200 iterations, 15 leaves, minimum leaf size 20, L2 `1`, no early stopping, random state `202409`, no AP-count split.
- Output: `max(0, physical_base + learned_residual)` per AP; system throughput is the exact sum of bounded AP predictions.
- Actual preprocessing includes training-side median imputation, missing indicators and StandardScaler for numeric HGB inputs, plus protocol one-hot encoding. The text must match this implementation.

Recommended wording:

> 嵌套选择的统一 HGB 管线将 primary S 降至 0.5503；按全部训练侧内层证据冻结后，最终全量配置为 physics-residual C3。

Do not write “fixed residual-C3 itself scored 0.5503”. Do not attribute all 31.60% gain solely to residualization.

## Core metric definitions

Use the exact definitions in the approved model contracts:

- Q1: bounded regression errors in seconds; bounded prediction is clipped to `[0,test_dur]`.
- Q2: fixed-17 Macro-F1 is the unweighted mean of per-class F1 over the permanently frozen 17 labels; absent/prediction-collapsed classes contribute according to the frozen zero-division rule.
- Q3 AP relative error for positive truth: `(prediction-truth)/truth`; ARE90 is the one-based nearest-rank 90th percentile with no interpolation.
- Q3 system prediction: sum bounded AP predictions within `source_file + test_id`, never an independent system head.
- Primary selection score: `S=max(AP ARE90, system ARE90)`; lower is better.
- Truth-zero AP rows are excluded from relative CDFs and reported through absolute-error diagnostics, not epsilon denominators.

## Safe abstract numbers

These values may be used with the stated identities:

- Q1 bounded primary MAE `5.5054 s` — `E-Q1-001`.
- Q2 fixed-17 Macro-F1 `0.3377`; weighted HGB gain `0.0190 < 0.02`, so Logistic is retained — `E-Q2-001`.
- Q3 nested unified pipeline primary `S=0.5503`, a `31.60%` improvement over Q3-B1 — `E-Q3-PIPE-001`.
- Q3 pipeline group-bootstrap interval `[0.5090,0.6077]` — `E-Q3-UNC-001`, explicitly described as OOF group resampling.
- Q3 aggregate LOSO `S=0.7299` — `E-Q3-LOSO-001`, accompanied by the worst-source limitation.

Official-test predictions have no labels. Their existence, row counts, constraints and release provenance may be stated (`E-RELEASE-001`, `E-RELEASE-SUM-001`), but no official-test accuracy claim is possible.

## Required limitations

- Q2 rare classes are not strongly learnable with current support, and source-blind Macro-F1 is low.
- Q3 worst held-out source has `S=2.159764`; aggregate improvement does not imply uniform robustness.
- AP-count split has better aggregate LOSO (`0.685496`) but worse frozen primary S (`0.573131` versus unified `0.550330`); this is a disclosed tradeoff, not a second validation set.
- A03 is a frozen-OOF whole-group evaluation-exclusion diagnostic, not delete-group retraining robustness.
- The 95% group-bootstrap interval does not cover full retraining and model-selection uncertainty.
- Data provenance currently proves equality to the S0 local manifest, not equality to a recorded official archive hash.

## Figures and sources

Use `figure_handoff.md` for the proposed figures. Do not plot from `results/raw/`, manually retype numbers, truncate axes to exaggerate differences, hide the worst LOSO source or present official unlabeled predictions as validation.

## Freeze and release provenance

- Freeze manifest: `results/verified/freeze_manifest.json`.
- Result registry: `results/verified/result_registry.md`.
- Release ID: `S5-A4AA45A0491C-20260911T110151+0800`.
- Exactly-once successful release count: 1.
- Release post-validation: `results/verified/final_release_verification.json`.
- Frozen model files and raw release manifest remain under `results/raw/final/release/`; paper-facing predictions are the verified `official_*.jsonl` copies.

Any later model, feature, postprocess, metric, label-order or output-schema change invalidates the corresponding Evidence IDs and requires returning to the appropriate Gate. S6 may begin only after a Reviewer or the user explicitly passes G5.
