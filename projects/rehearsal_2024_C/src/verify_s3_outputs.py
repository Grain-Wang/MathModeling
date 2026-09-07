"""Verify the completed S3 evidence bundle and recompute its core metrics."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from s3_common import (
    BASELINE_EVIDENCE_ROOT,
    DEFAULT_CONFIG,
    PROJECT_ROOT,
    S3_RESULTS_ROOT,
    WAVEFORM_LABELS,
    assert_pareto,
    classification_metrics,
    git_commit,
    load_frozen_config,
    log_rmse,
    pareto_mask,
    regression_metrics,
    sha256_file,
    verify_contract_registry,
    write_json,
)


EXPERIMENT_IDS = [
    "EXP-S3-DATA-001",
    "EXP-Q1-BASE-001",
    "EXP-Q2-BASE-001",
    "EXP-Q3-DESC-001",
    "EXP-Q3-BASE-001",
    "EXP-Q4-NULL-001",
    "EXP-Q4-BASE-001",
    "EXP-Q5-BASE-001",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def assert_close(actual: float, expected: float, label: str, tolerance: float = 1e-10) -> None:
    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(f"{label}: actual={actual}, expected={expected}")


def verify_manifest(experiment_id: str, expected_commit: str) -> dict[str, Any]:
    path = BASELINE_EVIDENCE_ROOT / experiment_id / "run_manifest.json"
    manifest = read_json(path)
    if manifest["experiment_id"] != experiment_id or manifest["status"] != "PASS" or manifest["exit_code"] != 0:
        raise AssertionError(f"Failed or mismatched run manifest: {experiment_id}")
    if manifest["git_commit"] != expected_commit:
        raise AssertionError(f"Run {experiment_id} used {manifest['git_commit']}, expected {expected_commit}")
    if manifest.get("implementation_git_dirty_at_finish"):
        raise AssertionError(f"Implementation/config inputs were dirty during {experiment_id}")
    for relative, expected_hash in manifest["output_hashes"].items():
        output_path = PROJECT_ROOT / relative
        if sha256_file(output_path) != expected_hash:
            raise AssertionError(f"Output hash mismatch for {relative}")
    return manifest


def verify_q1() -> dict[str, Any]:
    output = pd.read_csv(S3_RESULTS_ROOT / "q1" / "baseline_oof_predictions.csv")
    if set(output["actual_label"]) - set(WAVEFORM_LABELS) or set(output["predicted_label"]) - set(WAVEFORM_LABELS):
        raise AssertionError("Q1 predictions contain an unknown label")
    recomputed = classification_metrics(output["actual_label"], output["predicted_label"])
    reported = read_json(S3_RESULTS_ROOT / "q1" / "baseline_metrics.json")["oof"]
    for metric in ("accuracy", "balanced_accuracy", "macro_f1"):
        assert_close(float(recomputed[metric]), float(reported[metric]), f"Q1 {metric}")
    return {metric: recomputed[metric] for metric in ("accuracy", "balanced_accuracy", "macro_f1")}


def verify_regression(question: str, filename: str, metrics_filename: str) -> dict[str, Any]:
    output = pd.read_csv(S3_RESULTS_ROOT / question / filename)
    recomputed = regression_metrics(output["core_loss_W_per_m3"], output["y_pred_oof"])
    reported_document = read_json(S3_RESULTS_ROOT / question / metrics_filename)
    reported = reported_document.get("oof", reported_document)
    for metric in ("rmsle", "mae_W_per_m3", "rmse_W_per_m3", "mape_percent", "median_ape_percent"):
        assert_close(float(recomputed[metric]), float(reported[metric]), f"{question.upper()} {metric}", 1e-8)
    return recomputed


def verify_q3() -> dict[str, Any]:
    output = pd.read_csv(S3_RESULTS_ROOT / "q3" / "additive_oof_predictions.csv")
    actual = log_rmse(output["core_loss_W_per_m3"], output["y_pred_oof"])
    reported = read_json(S3_RESULTS_ROOT / "q3" / "additive_metrics.json")["oof_log_rmse"]
    assert_close(actual, float(reported), "Q3 log_rmse", 1e-8)
    return {"oof_log_rmse": actual}


def verify_q4() -> dict[str, Any]:
    ridge = verify_regression("q4", "ridge_oof_predictions.csv", "ridge_metrics.json")
    null_output = pd.read_csv(S3_RESULTS_ROOT / "q4" / "median_oof_predictions.csv")
    null_metrics: dict[str, Any] = {}
    for column in ("global_median_y_pred_oof", "grouped_median_y_pred_oof"):
        null_metrics[column] = regression_metrics(null_output["core_loss_W_per_m3"], null_output[column])
    return {"ridge": ridge, "null": null_metrics}


def verify_q5() -> dict[str, Any]:
    candidate_index = pd.read_csv(S3_RESULTS_ROOT / "q5" / "observed_candidate_index.csv")
    conflicts = pd.read_csv(S3_RESULTS_ROOT / "q5" / "oof_full_conflict_diagnostics.csv")
    candidates = candidate_index.merge(conflicts[["row_id", "y_pred_oof"]], on="row_id", validate="one_to_one")
    expected_mask = pareto_mask(candidates["y_pred_oof"], candidates["energy_proxy_Hz_T"])
    expected_ids = set(candidates.loc[expected_mask, "row_id"])
    reported_pareto = pd.read_csv(S3_RESULTS_ROOT / "q5" / "oof_pareto_baseline.csv")
    if expected_ids != set(reported_pareto["row_id"]):
        raise AssertionError("Q5 strict OOF Pareto membership cannot be reproduced")
    assert_pareto(candidates["y_pred_oof"], candidates["energy_proxy_Hz_T"], expected_mask)
    lineage = pd.read_csv(S3_RESULTS_ROOT / "q5" / "candidate_oof_lineage.csv")
    if not lineage["strict_oof_lineage_pass"].astype(bool).all() or set(lineage["row_id"]) != set(candidates["row_id"]):
        raise AssertionError("Q5 candidate-level OOF exclusion assertion failed")
    metrics = read_json(S3_RESULTS_ROOT / "q5" / "baseline_metrics.json")
    if int(expected_mask.sum()) != int(metrics["oof_pareto_points"]):
        raise AssertionError("Q5 Pareto count does not match metrics.json")
    return {
        "candidate_count": int(len(candidates)),
        "strict_oof_pareto_count": int(expected_mask.sum()),
        "lineage_rows": int(len(lineage)),
    }


def main() -> None:
    args = parse_args()
    config = load_frozen_config(args.config)
    contract_hashes = verify_contract_registry(config)
    expected_commit = git_commit()
    manifests = {experiment_id: verify_manifest(experiment_id, expected_commit) for experiment_id in EXPERIMENT_IDS}
    report = {
        "status": "PASS",
        "stage": "S3",
        "implementation_commit": expected_commit,
        "contract_hashes": contract_hashes,
        "manifest_count": len(manifests),
        "q1": verify_q1(),
        "q2": verify_regression("q2", "baseline_oof_predictions.csv", "baseline_metrics.json"),
        "q3": verify_q3(),
        "q4": verify_q4(),
        "q5": verify_q5(),
    }
    output_path = S3_RESULTS_ROOT / "verification_report.json"
    write_json(output_path, report)
    print(f"PASS: verified S3 evidence bundle; report={output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
