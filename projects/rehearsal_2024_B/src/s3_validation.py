"""Independent post-run validator for S3 Baseline artifacts.

This validator reads generated JSON/JSONL evidence only.  It never opens raw CSV.
"""

from __future__ import annotations

import gzip
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from s3_io import (
    LABELS_EXPECTED,
    OUTPUT,
    PROJECT,
    dump,
    git,
    load_json,
    sha256,
)
from s3_metrics import nearest_rank


def read_jsonl_gz(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    return math.isclose(float(a), float(b), rel_tol=tolerance, abs_tol=tolerance)


def q1_checks(rows: list[dict[str, Any]], metrics: dict[str, Any]) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    checks = {
        "primary_total_rows": len(frame[frame.scope.eq("PRIMARY")]) == 7500,
        "loso_total_rows": len(frame[frame.scope.eq("LOSO")]) == 2500,
        "finite_predictions": np.isfinite(
            frame[["seq_time_raw", "seq_time_bounded"]].to_numpy(float)
        ).all(),
        "bounded_physical_range": (
            (frame.seq_time_bounded >= 0)
            & (frame.seq_time_bounded <= frame.test_dur)
        ).all(),
    }
    for model in ["Q1-B0", "Q1-B1"]:
        part = frame[
            frame.scope.eq("PRIMARY") & frame.model_id.eq(model)
        ]
        for repeat, subset in part.groupby("repeat"):
            checks[f"{model}_repeat_{int(repeat)}_coverage"] = (
                len(subset) == 1250 and subset.row_key.nunique() == 1250
            )
        computed = []
        for _, subset in part.groupby("repeat"):
            computed.append(float(np.mean(np.abs(
                subset.seq_time_bounded.to_numpy(float)
                - subset.truth_seq_time.to_numpy(float)
            ))))
        recorded = metrics["models"][model][
            "primary_point_estimate_repeat_mean"
        ]["bounded"]["mae"]
        checks[f"{model}_primary_mae_recomputed"] = close(
            np.mean(computed), recorded
        )
    if not all(checks.values()):
        raise AssertionError(f"Q1 artifact checks failed: {checks}")
    return checks


def q2_checks(rows: list[dict[str, Any]], metrics: dict[str, Any]) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    probabilities = np.vstack(frame.probability_fixed_17)
    checks = {
        "primary_total_rows": len(frame[frame.scope.eq("PRIMARY")]) == 11250,
        "loso_total_rows": len(frame[frame.scope.eq("LOSO")]) == 3750,
        "fixed_probability_width": probabilities.shape[1] == 17,
        "probabilities_finite": np.isfinite(probabilities).all(),
        "probabilities_sum_one": np.allclose(
            probabilities.sum(axis=1), 1.0, atol=1e-10, rtol=0
        ),
        "predictions_in_fixed_labels": set(
            frame.predicted_joint_label
        ) <= set(LABELS_EXPECTED),
        "stored_label_order_fixed": all(
            value == LABELS_EXPECTED for value in frame.probability_label_order
        ),
    }
    for model in ["Q2-B0", "Q2-B1A", "Q2-B1B"]:
        part = frame[
            frame.scope.eq("PRIMARY") & frame.model_id.eq(model)
        ]
        computed = []
        for repeat, subset in part.groupby("repeat"):
            checks[f"{model}_repeat_{int(repeat)}_coverage"] = (
                len(subset) == 1250 and subset.row_key.nunique() == 1250
            )
            computed.append(float(f1_score(
                subset.truth_joint_label.to_numpy(str),
                subset.predicted_joint_label.to_numpy(str),
                labels=LABELS_EXPECTED, average="macro", zero_division=0,
            )))
        recorded = metrics["models"][model][
            "primary_point_estimate_repeat_mean"
        ]["macro_f1_fixed_17"]
        checks[f"{model}_macro_f1_recomputed"] = close(
            np.mean(computed), recorded
        )
    if not all(checks.values()):
        raise AssertionError(f"Q2 artifact checks failed: {checks}")
    return checks


def q3_checks(
    ap_rows: list[dict[str, Any]], system_rows: list[dict[str, Any]],
    metrics: dict[str, Any],
) -> dict[str, Any]:
    ap, system = pd.DataFrame(ap_rows), pd.DataFrame(system_rows)
    checks = {
        "primary_ap_total_rows": len(ap[ap.scope.eq("PRIMARY")]) == 11250,
        "loso_ap_total_rows": len(ap[ap.scope.eq("LOSO")]) == 3750,
        "primary_system_total_rows": (
            len(system[system.scope.eq("PRIMARY")]) == 4338
        ),
        "loso_system_total_rows": (
            len(system[system.scope.eq("LOSO")]) == 1446
        ),
        "finite_ap_predictions": np.isfinite(
            ap[["throughput_raw", "throughput_bounded"]].to_numpy(float)
        ).all(),
        "bounded_ap_nonnegative": (ap.throughput_bounded >= 0).all(),
        "stored_sum_error_zero": (
            system.bounded_sum_equality_absolute_error <= 1e-12
        ).all(),
    }
    grouping = [
        "scope", "model_id", "repeat", "fold", "loso_split",
        "source_file", "test_id",
    ]
    recomputed = ap.groupby(grouping, dropna=False).agg(
        predicted=("throughput_bounded", "sum"),
        truth=("truth_throughput", "sum"),
    ).reset_index()
    merged = system.merge(recomputed, on=grouping, validate="one_to_one")
    checks["system_row_alignment"] = len(merged) == len(system)
    checks["system_prediction_sum_equality"] = np.allclose(
        merged.system_throughput_bounded, merged.predicted,
        atol=1e-9, rtol=0,
    )
    checks["system_truth_sum_equality"] = np.allclose(
        merged.truth_system_throughput, merged.truth,
        atol=1e-9, rtol=0,
    )
    for model in ["Q3-B0", "Q3-B1", "Q3-B2"]:
        ap_model = ap[ap.scope.eq("PRIMARY") & ap.model_id.eq(model)]
        sys_model = system[
            system.scope.eq("PRIMARY") & system.model_id.eq(model)
        ]
        scores = []
        for repeat, ap_part in ap_model.groupby("repeat"):
            sys_part = sys_model[sys_model.repeat.eq(repeat)]
            checks[f"{model}_ap_repeat_{int(repeat)}_coverage"] = (
                len(ap_part) == 1250 and ap_part.row_key.nunique() == 1250
            )
            checks[f"{model}_system_repeat_{int(repeat)}_coverage"] = (
                len(sys_part) == 482 and sys_part.group_id.nunique() == 482
            )
            ap_truth = ap_part.truth_throughput.to_numpy(float)
            ap_pred = ap_part.throughput_bounded.to_numpy(float)
            nonzero = ap_truth != 0
            ap90 = nearest_rank(
                np.abs((ap_pred[nonzero] - ap_truth[nonzero]) / ap_truth[nonzero]),
                .90,
            )
            sys_truth = sys_part.truth_system_throughput.to_numpy(float)
            sys_pred = sys_part.system_throughput_bounded.to_numpy(float)
            sys90 = nearest_rank(
                np.abs((sys_pred - sys_truth) / sys_truth), .90
            )
            scores.append(max(ap90, sys90))
        recorded = metrics["models"][model][
            "primary_point_estimate_repeat_mean"
        ]["selection_score"]
        checks[f"{model}_selection_score_recomputed"] = close(
            np.mean(scores), recorded
        )
    if not all(checks.values()):
        raise AssertionError(f"Q3 artifact checks failed: {checks}")
    return checks


def main() -> int:
    manifest = load_json(OUTPUT / "run_manifest.json")
    q1_rows = read_jsonl_gz(OUTPUT / "q1_oof_predictions.jsonl.gz")
    q2_rows = read_jsonl_gz(OUTPUT / "q2_oof_predictions.jsonl.gz")
    q3_rows = read_jsonl_gz(OUTPUT / "q3_ap_oof_predictions.jsonl.gz")
    system_rows = read_jsonl_gz(
        OUTPUT / "q3_system_oof_predictions.jsonl.gz"
    )
    lineage = load_json(OUTPUT / "q1_actual_upstream_lineage.json")
    schema = load_json(OUTPUT / "feature_schema.json")
    bootstrap = load_json(OUTPUT / "group_bootstrap_intervals.json")
    q1_metrics = load_json(OUTPUT / "q1_metrics.json")
    q2_metrics = load_json(OUTPUT / "q2_metrics.json")
    q3_metrics = load_json(OUTPUT / "q3_metrics.json")

    required_schema_fields = {
        "name", "dtype", "unit", "missing_semantics", "column_order"
    }
    global_checks = {
        "run_status": manifest["status"] == "PASS",
        "formal_head_is_ancestor": git(
            "merge-base", manifest["git_head"], git("rev-parse", "HEAD")
        ) == manifest["git_head"],
        "formal_model_sources_unchanged": git(
            "diff", "--name-only", manifest["git_head"], "--",
            "projects/rehearsal_2024_B/src/s3_baseline.py",
            "projects/rehearsal_2024_B/src/s3_evaluation.py",
            "projects/rehearsal_2024_B/src/s3_features.py",
            "projects/rehearsal_2024_B/src/s3_io.py",
            "projects/rehearsal_2024_B/src/s3_lineage.py",
            "projects/rehearsal_2024_B/src/s3_metrics.py",
            "projects/rehearsal_2024_B/src/s3_models.py",
        ) == "",
        "formal_run_started_clean": manifest["git_status_before_outputs"] == "",
        "baseline_run_count": manifest["baseline_run_count"] == 8,
        "model_fit_count_positive": manifest["model_fit_count"] > 0,
        "outer_fold_count": manifest["outer_fold_count"] == 15,
        "loso_split_count": manifest["loso_split_count"] == 13,
        "training_numeric_read_count": (
            manifest["training_csv_numeric_read_count"] == 13
        ),
        "official_test_numeric_read_count_zero": (
            manifest["official_test_numeric_read_count"] == 0
        ),
        "official_test_prediction_count_zero": (
            manifest["official_test_prediction_count"] == 0
        ),
        "real_entry_guard_pass": (
            manifest["preflight"]["real_entry_guard_tests"]["status"] == "PASS"
        ),
        "warnings_zero": manifest["warning_count"] == 0,
        "feature_schema_hash": (
            manifest["feature_schema_sha256"] == sha256(
                OUTPUT / "feature_schema.json"
            )
        ),
        "feature_schema_required_fields": all(
            required_schema_fields <= set(item) for item in schema["features"]
        ),
        "feature_schema_order": [
            item["column_order"] for item in schema["features"]
        ] == list(range(schema["raw_feature_count"])),
        "two_three_ap_schema_alignment": (
            schema["ap_count_alignment"]["same_order"] is True
        ),
        "bootstrap_replicates_1000": (
            bootstrap["contract"]["replicates"] == 1000
        ),
        "lineage_batch_count": lineage["assertions"]["batch_count"] == 112,
        "lineage_overlap_zero": (
            lineage["assertions"]["prediction_fit_overlap_total"] == 0
            and lineage["assertions"]["held_out_fit_overlap_total"] == 0
        ),
        "lineage_fixed_identity": (
            lineage["assertions"]["fixed_upstream_identity"] is True
        ),
    }
    if not all(global_checks.values()):
        raise AssertionError(f"global S3 checks failed: {global_checks}")

    result = {
        "status": "PASS", "git_head": manifest["git_head"],
        "global_checks": global_checks,
        "q1_checks": q1_checks(q1_rows, q1_metrics),
        "q2_checks": q2_checks(q2_rows, q2_metrics),
        "q3_checks": q3_checks(q3_rows, system_rows, q3_metrics),
        "official_test_numeric_read_count": 0,
        "official_test_prediction_count": 0,
    }
    dump(OUTPUT / "post_run_validation.json", result)
    print("status=PASS")
    print(f"global_checks={len(global_checks)}")
    print(f"q1_checks={len(result['q1_checks'])}")
    print(f"q2_checks={len(result['q2_checks'])}")
    print(f"q3_checks={len(result['q3_checks'])}")
    print("official_test_numeric_read_count=0")
    print("official_test_prediction_count=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
