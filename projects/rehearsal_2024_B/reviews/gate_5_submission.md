# Gate 5 Submission

## Stage

S5 — 结果核验、冻结与交接

## Review Snapshot

- G4 authorization review commit: `70d6a1436192339c61c749188e104b15cf4bbbb7`
- S5 implementation commit: `474acb71dfc0bcaa27e6cca908c2243efa65660f`
- Pre-release verified freeze commit: `473a8ad8bf04cfa7d62511dadbe620f3a6ba8570`
- Freeze manifest SHA-256: `A4AA45A0491C35C1D816164AADABB20998E9984D7521AFDE55D01A8B027E5E6D`
- Final release ID: `S5-A4AA45A0491C-20260911T110151+0800`
- Exactly-once successful release count: `1`
- Submission bundle: containing commit of this file
- Requested transition: S5 → S6
- Main Agent does not self-approve G5; S6 remains forbidden until Reviewer PASS or explicit user approval.

## Deliverables

- [S5 result freeze](../work/10_result_freeze.md)
- [Verified result registry](../results/verified/result_registry.md)
- [Freeze manifest](../results/verified/freeze_manifest.json) and SHA-256 sidecar
- [Independent selection reconstruction](../results/verified/selection_reconstruction.json)
- [Verified metric summary](../results/verified/verified_metrics.json)
- [Final release verification](../results/verified/final_release_verification.json)
- verified Q1/Q2/Q3 metrics, group-bootstrap intervals, stratified metrics and failure cases
- verified official unlabeled Q1/Q2/Q3 AP and Q3 system prediction JSONL files
- [Figure handoff](../work/handoff/figure_handoff.md)
- [Writing handoff](../work/handoff/writing_handoff.md)
- `src/s5_validation.py`, independent of production Q2/Q3 evaluation functions
- `src/s5_release.py`, disk-ledger-derived exactly-once release entry
- `configs/s5_output_schema.json`
- raw final ledger, release manifest, three serialized model artifacts and four released output artifacts
- updated decisions, experiments, AI-usage log and CURRENT

## Verification Commands

Current post-release snapshot:

~~~powershell
conda run --no-capture-output -n math_modeling python -m py_compile projects/rehearsal_2024_B/src/s5_validation.py projects/rehearsal_2024_B/src/s5_release.py
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_validation.py --phase finalize-release
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s5_release.py --preflight-only
git diff --check
~~~

Expected outcomes:

- compile: PASS;
- finalization: PASS, exactly one successful release, 10 cross-artifact plus 12 per-file schema/order checks;
- second release preflight: hard FAIL with `a successful official-test release already exists`;
- diff check: PASS.

The complete pre-release command sequence is preserved in `work/10_result_freeze.md`; it must not be rerun as a second release on the current snapshot.

## Main Claims

1. G4's three Minor items are closed at the S5 evidence/specification layer:
   - Q3 nested pipeline performance and final residual-C3 configuration have distinct Evidence IDs;
   - selection/configuration/promotion are independently reconstructed directly from traces and OOF predictions;
   - HGB's real imputation + StandardScaler preprocessing is stated faithfully.
2. The unique frozen model stack is Q1-B1 + Q2-B1A + Q3 unified with full-data physics-residual C3; no candidate search was reopened.
3. Freeze manifest includes complete model parameters, training hashes, feature schemas, postprocess versions, Q2 label order, split/config/source hashes, output schema/order, and separate Q3 evidence identities.
4. Official release ran exactly once only after the real disk-ledger guard passed. The ledger contains input, freeze, model and output hashes; a second release is rejected.
5. All paper-facing evidence is under `results/verified/` and registered by Evidence ID. Official predictions are marked unlabeled and are not used as performance evidence.
6. Figure and writing handoffs identify data, units, safe claims and prohibited overstatements without asking downstream workers to infer technical meaning.

## Known Limitations

1. Q2 support-1–2 rare classes and source-blind Macro-F1 remain weak.
2. Q3's worst held-out source remains `S=2.159764`; only aggregate primary/LOSO improvement is supported.
3. Q3 group-bootstrap does not represent full retraining/selection uncertainty.
4. unified/AP-count is a controlled shared-evidence comparison, not a confirmatory test.
5. Official-test predictions are unlabeled and cannot establish accuracy.
6. The local data source URL/archive hash remains unavailable; only equality to the S0 file manifest is established.

## Unresolved Risks

- No Critical or Major issue is known in the S5 artifact chain.
- S6 must keep all numerical claims tied to the Evidence IDs and must not reopen the model because of official prediction appearance.
- Actual figure generation still requires user confirmation of a concrete plotting skill under repository policy.

## Requested Verdict

**PASS**, authorizing S5 → S6 for paper technical consistency and final submission preparation.

If the freeze hash, ledger success count, released artifact hashes, independent Q2/Q3 reconstruction, Q3 evidence identity separation, or verified registry is inconsistent, return **REVISE** and do not authorize S6.
