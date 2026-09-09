"""Independent artifact-only validation for the S4 main-model run."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from s3_evaluation import evaluate_q2, evaluate_q3
from s3_io import dump, now, sha256
from s3_models import system_records
from s4_io import OUTPUT, PROJECT, canonical_relative, git, load_json

BASELINE = PROJECT / "results" / "raw" / "baseline"
GENERATION_SOURCES = [
    PROJECT / "src" / "s4_io.py",
    PROJECT / "src" / "s4_selection.py",
    PROJECT / "src" / "s4_main.py",
    PROJECT / "configs" / "s4_candidate_plan.json",
]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _all(checks: dict[str, bool], label: str) -> None:
    failed = [key for key, value in checks.items() if not value]
    if failed:
        raise AssertionError(f"{label} validation failed: {failed}")


def _artifact_hash_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    result = {}
    for item in manifest["output_artifacts"]:
        path = PROJECT.parents[1] / item["path"]
        result[item["path"]] = (
            path.is_file()
            and path.stat().st_size == int(item["bytes"])
            and sha256(path) == item["sha256"]
        )
    return result


def _q2_checks(
    rows: list[dict[str, Any]],
    stored: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, bool]:
    frame = pd.DataFrame(rows)
    labels = list(stored["fixed_label_order"])
    recomputed = evaluate_q2(rows, labels)
    primary = frame[frame.scope.eq("PRIMARY")]
    loso = frame[frame.scope.eq("LOSO")]
    expected_models = 3 if manifest["q2_weighting_triggered"] else 2
    counts = primary.groupby(["model_id", "repeat"]).size()
    loso_counts = loso.groupby("model_id").size()
    probabilities = np.vstack(frame.probability_fixed_17)
    sources = set(frame.source_file.astype(str))
    return {
        "metrics_exactly_recomputed": recomputed == stored,
        "model_count": frame.model_id.nunique() == expected_models,
        "primary_model_repeat_count": len(counts) == expected_models * 3,
        "primary_rows_each": bool((counts == 1250).all()),
        "loso_rows_each": bool((loso_counts == 1250).all()),
        "loso_split_count": loso.loso_split.nunique() == 13,
        "probability_width_17": probabilities.shape[1] == 17,
        "probability_finite": bool(np.isfinite(probabilities).all()),
        "probability_sum_one": bool(np.allclose(
            probabilities.sum(axis=1), 1.0, atol=1e-10, rtol=0
        )),
        "fixed_label_order": all(
            value == labels for value in frame.probability_label_order
        ),
        "predictions_legal": set(frame.predicted_joint_label) <= set(labels),
        "training_sources_only": all(
            source.startswith("training_set_") for source in sources
        ),
        "unweighted_present": "Q2-M1-HGB" in set(frame.model_id),
        "q1_ablation_present": "Q2-M1-Q1-ABLATION" in set(frame.model_id),
        "conditional_weight_consistent": (
            ("Q2-M1W-HGB-WEIGHTED" in set(frame.model_id))
            == bool(manifest["q2_weighting_triggered"])
        ),
        "numeric_ap_count_shared": set(frame.ap_count_representation)
        == {"numeric_binary_2_or_3"},
    }


def _q3_checks(
    ap_rows: list[dict[str, Any]],
    stored_system_rows: list[dict[str, Any]],
    stored_metrics: dict[str, Any],
) -> dict[str, bool]:
    ap = pd.DataFrame(ap_rows)
    system = pd.DataFrame(stored_system_rows)
    rebuilt_system_rows = system_records(ap_rows)
    rebuilt_system = pd.DataFrame(rebuilt_system_rows)
    recomputed, _ = evaluate_q3(ap_rows, rebuilt_system_rows)
    primary_ap = ap[ap.scope.eq("PRIMARY")]
    primary_sys = system[system.scope.eq("PRIMARY")]
    loso_ap = ap[ap.scope.eq("LOSO")]
    loso_sys = system[system.scope.eq("LOSO")]
    ap_counts = primary_ap.groupby(["model_id", "repeat"]).size()
    sys_counts = primary_sys.groupby(["model_id", "repeat"]).size()
    key = ["scope", "model_id", "repeat", "fold", "loso_split", "group_id"]
    left = system.sort_values(key, na_position="first").reset_index(drop=True)
    right = rebuilt_system.sort_values(key, na_position="first").reset_index(drop=True)
    return {
        "metrics_exactly_recomputed": recomputed == stored_metrics,
        "model_count": ap.model_id.nunique() == 2,
        "primary_ap_rows_each": bool((ap_counts == 1250).all()),
        "primary_system_rows_each": bool((sys_counts == 482).all()),
        "loso_ap_rows_each": bool((loso_ap.groupby("model_id").size() == 1250).all()),
        "loso_system_rows_each": bool((loso_sys.groupby("model_id").size() == 482).all()),
        "loso_split_count": loso_ap.loso_split.nunique() == 13,
        "bounded_finite": bool(np.isfinite(ap.throughput_bounded).all()),
        "bounded_nonnegative": bool((ap.throughput_bounded >= 0).all()),
        "raw_finite": bool(np.isfinite(ap.throughput_raw).all()),
        "system_row_count_matches_rebuild": len(left) == len(right),
        "system_truth_exact": bool(np.allclose(
            left.truth_system_throughput,
            right.truth_system_throughput,
            atol=1e-12,
            rtol=0,
        )),
        "system_prediction_exact": bool(np.allclose(
            left.system_throughput_bounded,
            right.system_throughput_bounded,
            atol=1e-12,
            rtol=0,
        )),
        "stored_sum_error_zero": bool(
            (system.bounded_sum_equality_absolute_error == 0).all()
        ),
        "zero_truth_count_preserved": int((ap.truth_throughput == 0).sum())
        == 5 * (3 * 2 + 2),
        "unified_present": "Q3-M1-HGB-UNIFIED" in set(ap.model_id),
        "single_ap_count_comparison_present": (
            set(ap.model_id)
            == {"Q3-M1-HGB-UNIFIED", "Q3-M1-HGB-APCOUNT"}
        ),
        "numeric_ap_count_shared": set(ap.ap_count_representation)
        == {"numeric_binary_2_or_3"},
        "training_sources_only": all(
            str(source).startswith("training_set_")
            for source in set(ap.source_file)
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    status_before_validation = git("status", "--short")
    manifest = load_json(OUTPUT / "run_manifest.json")
    q2_rows = _read_jsonl(OUTPUT / "q2_oof_predictions.jsonl.gz")
    q3_rows = _read_jsonl(OUTPUT / "q3_ap_oof_predictions.jsonl.gz")
    system_rows = _read_jsonl(OUTPUT / "q3_system_oof_predictions.jsonl.gz")
    q2_metrics = load_json(OUTPUT / "q2_candidate_metrics.json")
    q3_metrics = load_json(OUTPUT / "q3_candidate_metrics.json")
    q2_selection = load_json(OUTPUT / "q2_selection.json")
    q3_selection = load_json(OUTPUT / "q3_selection.json")
    lineage = load_json(OUTPUT / "q1_actual_upstream_lineage.json")
    promotion = load_json(OUTPUT / "promotion_decision.json")
    final = load_json(OUTPUT / "final_candidate.json")
    bootstrap = load_json(OUTPUT / "group_bootstrap_intervals.json")
    a03 = load_json(OUTPUT / "a03_evaluation_exclusion.json")
    formal_head = manifest["git_head"]
    current_head = git("rev-parse", "HEAD")
    source_diff = git(
        "diff", "--name-only", formal_head, "--",
        *[canonical_relative(path) for path in GENERATION_SOURCES],
    )
    global_checks = {
        "run_status": manifest["status"] == "PASS",
        "formal_head_is_ancestor": git(
            "merge-base", formal_head, current_head
        ) == formal_head,
        "formal_generation_sources_unchanged": source_diff == "",
        "formal_run_started_clean": manifest["git_status_before_outputs"] == "",
        "eligible_rows": manifest["eligible_rows"] == 1250,
        "eligible_groups": manifest["eligible_groups"] == 482,
        "outer_fold_count": manifest["outer_fold_count"] == 15,
        "loso_split_count": manifest["loso_split_count"] == 13,
        "q2_grid_count": manifest["q2_grid_count"] == 4,
        "q3_candidate_count": manifest["q3_candidate_count"] == 8,
        "q2_weight_formula_budget": manifest["q2_weighting_formula_count"] <= 1,
        "q3_ap_count_comparison_budget": (
            manifest["q3_ap_count_split_comparison_count"] == 1
        ),
        "warnings_zero": manifest["warning_count"] == 0,
        "model_fits_positive": manifest["model_fit_count"] > 0,
        "test_numeric_reads_zero": manifest["official_test_numeric_read_count"] == 0,
        "test_predictions_zero": manifest["official_test_prediction_count"] == 0,
        "numeric_ap_count_declared": manifest["ap_count_representation"]
        == "numeric_binary_2_or_3_shared_by_all_s4_candidates",
        "a03_boundary_declared": manifest["a03_analysis_type"]
        == "evaluation_exclusion_diagnostic_only_no_training_robustness_claim",
        "artifact_hashes": all(_artifact_hash_checks(manifest).values()),
        "bootstrap_replicates": bootstrap["contract"]["replicates"] == 1000,
        "selection_closed": final["selection_closed_for_g4_submission"] is True,
        "test_not_used_for_final_rule": final["test_data_used"] is False,
        "promotion_final_q2_consistent": (
            final["q2"]["model_id"] == promotion["q2"]["selected_model_id"]
        ),
        "promotion_final_q3_consistent": (
            final["q3"]["model_id"] == promotion["q3"]["selected_model_id"]
        ),
        "results_verified_untouched": not any(
            path.is_file()
            for path in (PROJECT / "results" / "verified").glob("**/*")
        ) if (PROJECT / "results" / "verified").exists() else True,
    }
    selection_checks = {
        "q2_inner_trace_count": len(q2_selection["inner_trace"]) == 28 * 3 * 4,
        "q2_exact_four_configs": len({
            x["config_id"] for x in q2_selection["inner_trace"]
        }) == 4,
        "q2_weight_trigger_matches_manifest": (
            q2_selection["weighting_triggered"]
            == manifest["q2_weighting_triggered"]
        ),
        "q3_inner_trace_count": len(q3_selection["inner_trace"]) == 28 * 3 * 8,
        "q3_exact_eight_candidates": len({
            x["candidate_id"] for x in q3_selection["inner_trace"]
        }) == 8,
        "q3_direct_residual_only": {
            x["architecture"] for x in q3_selection["inner_trace"]
        } == {"direct", "physics_residual"},
        "q3_one_ap_count_comparison": (
            q3_selection["ap_count_split_comparisons"] == 1
        ),
        "lineage_batch_count": lineage["assertions"]["batch_count"] == 448,
        "lineage_primary_count": lineage["assertions"]["primary_batch_count"] == 240,
        "lineage_loso_count": lineage["assertions"]["loso_batch_count"] == 208,
        "lineage_prediction_fit_overlap_zero": (
            lineage["assertions"]["prediction_fit_overlap_total"] == 0
        ),
        "lineage_heldout_fit_overlap_zero": (
            lineage["assertions"]["downstream_validation_fit_overlap_total"] == 0
        ),
        "lineage_fixed_upstream": lineage["assertions"]["fixed_upstream_identity"],
        "a03_is_evaluation_exclusion": a03["analysis_type"].startswith(
            "whole-group evaluation exclusion"
        ),
    }
    q2_checks = _q2_checks(q2_rows, q2_metrics, manifest)
    q3_checks = _q3_checks(q3_rows, system_rows, q3_metrics)
    _all(global_checks, "global")
    _all(selection_checks, "selection")
    _all(q2_checks, "Q2")
    _all(q3_checks, "Q3")
    result = {
        "status": "PASS",
        "global_checks": global_checks,
        "selection_checks": selection_checks,
        "q2_checks": q2_checks,
        "q3_checks": q3_checks,
        "official_test_numeric_read_count": 0,
        "official_test_prediction_count": 0,
    }
    if not args.check_only:
        dump(OUTPUT / "post_run_validation.json", result)
        consumed = [
            path for path in sorted(OUTPUT.glob("*"))
            if path.is_file()
            and path.name not in {"post_run_validation.json", "validation_manifest.json"}
        ] + [
            BASELINE / "q2_metrics.json",
            BASELINE / "q3_metrics.json",
            BASELINE / "q1_oof_predictions.jsonl.gz",
        ]
        validation_manifest = {
            "status": "PASS",
            "executed_at": now(),
            "command": (
                "conda run -n math_modeling python "
                "projects/rehearsal_2024_B/src/s4_validation.py"
            ),
            "validator_path": canonical_relative(Path(__file__)),
            "validator_sha256": sha256(Path(__file__)),
            "git_head_at_validation": current_head,
            "git_status_before_validation": status_before_validation,
            "formal_run_head": formal_head,
            "formal_run_head_is_ancestor": global_checks["formal_head_is_ancestor"],
            "formal_generation_sources_unchanged": global_checks[
                "formal_generation_sources_unchanged"
            ],
            "consumed_artifacts": [{
                "path": canonical_relative(path),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            } for path in consumed],
            "validation_output": {
                "path": canonical_relative(OUTPUT / "post_run_validation.json"),
                "sha256": sha256(OUTPUT / "post_run_validation.json"),
                "bytes": (OUTPUT / "post_run_validation.json").stat().st_size,
            },
            "check_counts": {
                "global": len(global_checks),
                "selection": len(selection_checks),
                "q2": len(q2_checks),
                "q3": len(q3_checks),
            },
        }
        dump(OUTPUT / "validation_manifest.json", validation_manifest)
    print("status=PASS")
    print(f"global_checks={len(global_checks)}")
    print(f"selection_checks={len(selection_checks)}")
    print(f"q2_checks={len(q2_checks)}")
    print(f"q3_checks={len(q3_checks)}")
    print("official_test_numeric_read_count=0")
    print("official_test_prediction_count=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
