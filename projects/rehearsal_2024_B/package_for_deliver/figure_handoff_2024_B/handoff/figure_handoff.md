# Figure Handoff — rehearsal_2024_B

## Boundary

All formal figure data must come from `results/verified/` and carry the Evidence ID below. No figure has been generated in S5: repository policy requires confirming the concrete plotting skill with the user before drawing. Official-test predictions are unlabeled and should not be plotted as performance evidence.

## Recommended figures

### F1 — Frozen model comparison for Q3

- Purpose: show the primary improvement from Q3-B1 to the nested unified HGB pipeline and the unified/AP-count tradeoff.
- Evidence: `E-Q3-PIPE-001`, `E-Q3-TRADE-001`.
- Data: `q3_baseline_metrics.json`, `q3_candidate_metrics.json`.
- X axis: model/pipeline (`Q3-B1`, unified, AP-count split).
- Y axis: primary selection score `S=max(AP ARE90, system ARE90)`, dimensionless; lower is better.
- Recommended title: “Primary grouped validation selection score of frozen Q3 candidates”.
- Required annotation: unified `0.550330`, AP-count `0.573131`, Q3-B1 `0.804609`.
- Do not label the unified value as a fixed residual-C3 score. Do not imply a significance test.

### F2 — Q3 primary uncertainty

- Purpose: show sample-group resampling stability of the selected nested pipeline.
- Evidence: `E-Q3-UNC-001`.
- Data: `group_bootstrap_intervals.json`.
- X axis: AP-level `S` and system ARE90.
- Y axis: metric value, dimensionless; lower is better.
- Display: point estimate plus 95% group-bootstrap interval; unified S interval `[0.509020,0.607660]`.
- Recommended title: “Group-bootstrap uncertainty of frozen Q3 OOF metrics”.
- Caption must state that models were not retrained inside each bootstrap replicate.

### F3 — Primary versus source-blind Q3 robustness

- Purpose: disclose the gap between grouped primary validation and source-blind LOSO.
- Evidence: `E-Q3-PIPE-001`, `E-Q3-LOSO-001`, `E-Q3-TRADE-001`.
- Data: `q3_candidate_metrics.json`, `stratified_metrics.json`.
- X axis: validation scope/model.
- Y axis: selection score S, dimensionless; lower is better.
- Recommended title: “Primary and source-blind performance of Q3 pipelines”.
- Use a shared zero-based scale. Include or annotate the worst held-out source `S=2.159764`; do not crop it away.
- Do not claim every-source or every-3AP robustness.

### F4 — Q2 promotion threshold and rollback

- Purpose: show why the more complex Q2 HGB was rejected.
- Evidence: `E-Q2-001`.
- Data: `verified_metrics.json`, `q2_candidate_metrics.json`, `q2_baseline_metrics.json`.
- X axis: Q2 candidate.
- Y axis: fixed-17 Macro-F1 absolute gain versus Q2-B1A.
- Add a horizontal threshold at `+0.02`; weighted HGB is `+0.019002`.
- Recommended title: “Pre-registered Q2 promotion threshold and observed gains”.
- Use full precision for the pass/fail annotation; do not round `0.019002` to `0.02`.

### F5 — Q1 predictive contribution, not causality

- Purpose: summarize the frozen Q1 bounded predictive accuracy and feature-family stability.
- Evidence: `E-Q1-001` plus the G4-validated Q1 importance evidence recorded in S3.
- Data: `q1_metrics.json`; if importance is plotted, first migrate the required S3 importance file through the same verified registry procedure.
- Y axes: MAE in seconds for accuracy; permutation/ablation delta MAE in seconds for contribution.
- Recommended title: “Grouped validation accuracy and predictive feature contribution for Q1”.
- Captions must use “predictive contribution” or “conditional association”, never “causal effect”.

## Style and export requirements

- Follow `guide/figures_guide.md` and the applicable color guide after the user confirms a plotting skill.
- Keep model colors consistent across figures; use the same y-scale for direct comparisons.
- Export vector PDF/SVG plus PNG; retain a generation script and figure-data snapshot.
- Every caption must name its Evidence ID and source file.
- Do not use `results/raw/` directly and do not manually type plotted values.
