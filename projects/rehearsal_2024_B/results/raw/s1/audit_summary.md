# S1 Data Audit Summary

- Generated: 2026-09-09T10:48:56+08:00
- Git HEAD before outputs: affff4fa6ef2d9a5431adac6e7341c993b946f4d
- Verdict: PASS_WITH_WARNINGS
- Input verification before/after: PASS / PASS
- Raw/eligible training rows: 1252 / 1250
- Raw strict groups: 482 / 484
- Eligible strict groups: 482 / 482
- Official-test strict groups: 136 / 136
- Within-file exact duplicate training rows: 0
- Cross-file duplicate row/group fingerprint clusters: 0 / 0
- Q3 training/test system groups: 482 / 75
- Q3 zero denominators, AP/system training: 5 / 0

## Frozen anomaly handling

- A01 [WARN]: two shifted rows in training_set_2ap_loc2_nav82.csv.
  Handling: Do not edit source; isolate the two already-incomplete test_id 40/41 groups (one corrupt ap_1 row each, 2 rows total) from training and model selection. Strict identity auditing verifies every remaining group.
- A02 [WARN]: three AP0 RSSI columns entirely missing in one source file.
  Handling: Preserve missingness; never synthesize reverse links. At S2 use availability indicators plus a missing-aware preprocessor/model, or omit only unavailable directions.
- A03 [WARN]: three internally consistent (NSS,MCS)=(0,0) observations.
  Handling: Retain unchanged as sentinel-risk; do not coerce to NSS=1. S2 must report sensitivity with and without these rows before freezing the Q2 label policy.
- A04 [WARN]: schema aliases and empty prediction placeholders differ across files.
  Handling: Normalize aliases only in derived data; exclude every predict/error placeholder from features; retain original headers.
- A05 [WARN]: two other_air_time values exceed their 60-second test duration.
  Handling: Treat these two field values as invalid/missing in derived analysis and never as model inputs. Keep otherwise plausible target rows; S2 adds whole-group exclusion sensitivity if relevant.
- A06 [WARN]: one training filename location token disagrees with its content.
  Handling: Do not rename or rewrite source. Use content loc_id=loc4 as the feature value, preserve source_file as a scenario key, and keep the intended official label UNKNOWN.

## Strict identity and duplicate boundary

- Complete means expected row count, exact AP ID set/multiplicity, and unique composite row key.
- A01 explains the two raw invalid groups; every eligible training and official-test group must pass.
- Duplicate claims distinguish within-file full-row equality from cross-file normalized fingerprints.

## Q3 output and metric contract

- Per-AP key: source_file + test_id + ap_id; system key: source_file + test_id.
- System throughput is the sum of all AP throughput in the strict group, in Mbps.
- Primary statement error is signed relative error; its empirical 90th percentile uses nearest rank with no interpolation.
- Zero true throughput is excluded from relative CDF and reported separately with absolute error.
- Absolute-relative-error CDF is supplementary and cannot replace the statement metric.

## Leakage and validation boundary

- Atomic split unit: source_file + test_id; AP rows never cross folds.
- Leave-one-source-file-out is a mandatory S2 stress test.
- Official test sets remain distribution-sealed for final inference/export.
- Q1 excludes every post-event statistic and output.
- Q2 permits only leakage-safe out-of-fold Q1 predictions.
- Q3 may use actual MCS/NSS as explicitly permitted, but not PER or other post-event fields.

## Machine-readable evidence

- data_profile.json: file schemas, missingness, numeric summaries and training-only distributions.
- quality_checks.json: complete S1 quality, anomaly, leakage and metric contracts.
- identity_checks.json: strict row/group identity and duplicate fingerprints.
- q3_target_contract.json: AP/system target constructibility and executable CDF/ERROR_90 contract.
