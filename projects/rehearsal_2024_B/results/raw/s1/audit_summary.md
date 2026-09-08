# S1 Data Audit Summary

- Generated: 2026-09-08T23:09:15+08:00
- Git HEAD before outputs: f4b8b9f70e049d497edf56a3bdac43669da932a6
- Verdict: PASS_WITH_WARNINGS
- Input verification before/after: PASS / PASS
- Raw/eligible training rows: 1252 / 1250
- Structurally audited test rows: 336
- Training duplicate rows: 0
- Eligible incomplete AP groups: 0

## Frozen anomaly handling

- A01 [WARN]: two shifted rows in training_set_2ap_loc2_nav82.csv.
  Handling: Do not edit source; isolate the two already-incomplete test_id 40/41 groups (one corrupt ap_1 row each, 2 rows total) from training and model selection. The remaining groups all retain their expected AP count.
- A02 [WARN]: three AP0 RSSI columns entirely missing in one source file.
  Handling: Preserve missingness; never synthesize reverse links. At S2 use availability indicators plus a missing-aware preprocessor/model, or omit only unavailable directions.
- A03 [WARN]: three internally consistent (NSS,MCS)=(0,0) observations.
  Handling: Retain unchanged as sentinel-risk; do not coerce to NSS=1. S2 must report sensitivity with and without these rows before freezing the Q2 label policy.
- A04 [WARN]: schema aliases and empty prediction placeholders differ across files.
  Handling: Normalize aliases only in derived data; exclude every predict/error placeholder from features; retain original headers in source files.
- A05 [WARN]: two other_air_time values exceed their 60-second test duration by orders of magnitude.
  Handling: Treat these two field values as invalid/missing in derived analysis and never as model inputs. Keep their otherwise plausible target rows; S2 must include a whole-group exclusion sensitivity check if those rows affect a candidate model.
- A06 [WARN]: one training filename location token disagrees with its content.
  Handling: Do not rename or rewrite the source. Use content loc_id=loc4 as the feature value, preserve source_file as a separate scenario key, and do not infer whether the intended official label was loc4 or loc33.

## Leakage and validation boundary

- Atomic split unit: source_file + test_id; AP rows never cross folds.
- Official test sets remain sealed for final inference/export.
- Q1 excludes every post-event statistic and output.
- Q2 permits only leakage-safe out-of-fold Q1 predictions, never true labels.
- Q3 may use actual MCS/NSS as explicitly permitted, but not PER or other post-event fields.

## Machine-readable evidence

- data_profile.json: file schemas, missingness, numeric summaries and training-only distributions.
- quality_checks.json: hashes, anomalies, RSSI parsing, test boundary and leakage contracts.
