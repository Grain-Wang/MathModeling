"""Independently recompute core S4 claims and validate every mandatory run manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from s3_common import (
    DEFAULT_CONFIG,
    PROJECT_ROOT,
    assert_pareto,
    classification_metrics,
    load_frozen_config,
    pareto_mask,
    regression_metrics,
    verify_contract_registry,
    write_json,
)
from s4_common import S4_EVIDENCE_ROOT, S4_RESULTS_ROOT, s4_run

EXPERIMENT_ID = "EXP-S4-COMP-001"
MANDATORY_RUNS = [
    "EXP-Q2-MAIN-001", "EXP-Q2-SENS-001", "EXP-Q4-MAIN-001", "EXP-Q4-ABL-001", "EXP-Q4-STRESS-001",
    "EXP-Q5-ROB-001", "EXP-Q5-SENS-001", "EXP-Q3-INT-001", "EXP-Q3-BOOT-001", "EXP-Q3-SENS-001", "EXP-Q1-ABL-001",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def close(left: float, right: float) -> bool:
    return bool(np.isclose(left, right, rtol=1e-9, atol=1e-12))


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    run = s4_run(EXPERIMENT_ID, config_path, "comparison")
    try:
        config = load_frozen_config(config_path)
        run.record_contract_hashes(verify_contract_registry(config))
        for path in (Path(__file__).resolve(), Path(__file__).with_name("s3_common.py").resolve(), Path(__file__).with_name("s4_common.py").resolve()):
            run.record_input(path)
        checks: list[dict[str, Any]] = []
        commits: set[str] = set()
        for experiment_id in MANDATORY_RUNS:
            manifest_path = S4_EVIDENCE_ROOT / experiment_id / "run_manifest.json"
            run.record_input(manifest_path)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            commits.add(str(manifest["git_commit"]))
            command = str(manifest.get("command_repo_relative", ""))
            passed = (
                manifest["experiment_id"] == experiment_id
                and manifest["stage"] == "S4"
                and manifest["status"] == "PASS"
                and manifest["exit_code"] == 0
                and not manifest["implementation_git_dirty_at_finish"]
                and manifest["environment"]["conda_environment"] == config["environment"]
                and "command_repo_relative" in manifest
                and str(PROJECT_ROOT).lower() not in command.lower()
                and not any("附件二" in key or "附件三" in key for key in manifest["input_hashes"])
            )
            checks.append({"check": f"manifest:{experiment_id}", "pass": bool(passed)})
        checks.append({"check": "single_fixed_implementation_commit", "pass": len(commits) == 1, "value": sorted(commits)})

        q2_oof_path = S4_RESULTS_ROOT / "q2" / "quadratic_temperature_oof_predictions.csv"
        q2_metrics_path = S4_RESULTS_ROOT / "q2" / "quadratic_temperature_metrics.json"
        q4_metrics_path = S4_RESULTS_ROOT / "q4" / "hgb_metrics.json"
        q4_final_path = S4_RESULTS_ROOT / "q4" / "final_winner.json"
        q4_final_oof_path = S4_RESULTS_ROOT / "q4" / "final_oof_predictions.csv"
        q4_oof_path = S4_RESULTS_ROOT / "q4" / "hgb_oof_predictions.csv"
        q3_metrics_path = S4_RESULTS_ROOT / "q3" / "interaction_metrics.json"
        q3_oof_path = S4_RESULTS_ROOT / "q3" / "interaction_oof_predictions.csv"
        q5_metrics_path = S4_RESULTS_ROOT / "q5" / "robustness_metrics.json"
        q5_candidates_path = S4_RESULTS_ROOT / "q5" / "final_candidate_index.csv"
        q5_bootstrap_path = S4_RESULTS_ROOT / "q5" / "bootstrap_region_stability.csv"
        q1_metrics_path = S4_RESULTS_ROOT / "q1" / "stress_metrics.json"
        for path in (q2_oof_path, q2_metrics_path, q4_metrics_path, q4_oof_path, q4_final_path, q4_final_oof_path, q3_metrics_path, q3_oof_path, q5_metrics_path, q5_candidates_path, q5_bootstrap_path, q1_metrics_path):
            run.record_input(path)

        q2_oof = pd.read_csv(q2_oof_path)
        q2_metrics = json.loads(q2_metrics_path.read_text(encoding="utf-8"))
        q2_recomputed = regression_metrics(q2_oof["core_loss_W_per_m3"], q2_oof["y_pred_oof"])
        checks.append({"check": "q2_rmsle_recomputed", "pass": close(float(q2_recomputed["rmsle"]), float(q2_metrics["candidate_oof"]["rmsle"])), "value": q2_recomputed["rmsle"]})
        checks.append({"check": "q2_same_rows_as_baseline", "pass": bool(q2_metrics["same_oof_rows_and_folds_as_baseline"]) and len(q2_oof) == 1067})

        q4_oof = pd.read_csv(q4_oof_path)
        q4_metrics = json.loads(q4_metrics_path.read_text(encoding="utf-8"))
        q4_recomputed = regression_metrics(q4_oof["core_loss_W_per_m3"], q4_oof["y_pred_oof"])
        checks.append({"check": "q4_hgb_rmsle_recomputed", "pass": close(float(q4_recomputed["rmsle"]), float(q4_metrics["candidate_oof"]["rmsle"])), "value": q4_recomputed["rmsle"]})
        rule = float(q4_metrics["relative_rmsle_improvement"]) >= 0.02 and float(q4_metrics["maximum_major_subgroup_rmsle_degradation"]) <= 0.10
        checks.append({"check": "q4_adoption_rule_recomputed", "pass": bool(rule) == bool(q4_metrics["adopted"])})
        q4_final = json.loads(q4_final_path.read_text(encoding="utf-8"))
        q4_final_oof = pd.read_csv(q4_final_oof_path)
        q4_final_recomputed = regression_metrics(q4_final_oof["core_loss_W_per_m3"], q4_final_oof["y_pred_oof"])
        checks.append({"check": "q4_final_ablation_winner_recomputed", "pass": close(float(q4_final_recomputed["rmsle"]), float(q4_final["oof_rmsle"])), "value": q4_final_recomputed["rmsle"]})

        q3_oof = pd.read_csv(q3_oof_path)
        q3_metrics = json.loads(q3_metrics_path.read_text(encoding="utf-8"))
        q3_recomputed = float(np.sqrt(np.mean((np.log(q3_oof["core_loss_W_per_m3"]) - np.log(q3_oof["y_pred_oof"])) ** 2)))
        checks.append({"check": "q3_log_rmse_recomputed", "pass": close(q3_recomputed, float(q3_metrics["candidate_oof_log_rmse"])), "value": q3_recomputed})
        bootstrap_metrics = json.loads((S4_RESULTS_ROOT / "q3" / "bootstrap_metrics.json").read_text(encoding="utf-8"))
        checks.append({"check": "q3_bootstrap_500", "pass": bootstrap_metrics["requested_repetitions"] == 500 and bootstrap_metrics["valid_repetitions"] == 500})

        candidates = pd.read_csv(q5_candidates_path)
        q5_metrics = json.loads(q5_metrics_path.read_text(encoding="utf-8"))
        oof_pareto = pareto_mask(candidates["y_pred_oof"], candidates["energy_proxy_Hz_T"])
        assert_pareto(candidates["y_pred_oof"], candidates["energy_proxy_Hz_T"], oof_pareto)
        checks.append({"check": "q5_oof_pareto_recomputed", "pass": int(oof_pareto.sum()) == int(q5_metrics["oof_pareto_count"]) and np.array_equal(oof_pareto, candidates["is_oof_pareto"].astype(bool).to_numpy())})
        q5_bootstrap = pd.read_csv(q5_bootstrap_path)
        checks.append({"check": "q5_bootstrap_500", "pass": q5_metrics["bootstrap"]["requested_repetitions"] == 500 and int(q5_bootstrap["valid_repetitions"].max()) <= 500})
        eligible_n = int(candidates["single_point_eligible"].astype(bool).sum())
        checks.append({"check": "q5_unique_recommendation_policy", "pass": eligible_n == int(q5_metrics["single_point_eligible_count"]) and bool(q5_metrics["unique_recommendation_authorized"]) == (eligible_n == 1)})

        q1_metrics = json.loads(q1_metrics_path.read_text(encoding="utf-8"))
        checks.append({"check": "q1_mandatory_stress_completed", "pass": "minimum_phase_amplitude_prediction_agreement" in q1_metrics and "minimum_leave_one_material_macro_f1" in q1_metrics})
        passed = all(bool(item["pass"]) for item in checks)
        report = {"status": "PASS" if passed else "FAIL", "implementation_commits": sorted(commits), "check_count": len(checks), "failed_count": sum(not item["pass"] for item in checks), "checks": checks}
        report_path = S4_RESULTS_ROOT / "verification_report.json"
        evidence_path = run.output_dir / "metrics.json"
        write_json(report_path, report)
        write_json(evidence_path, report)
        run.record_output(report_path)
        run.record_output(evidence_path)
        run.log(json.dumps({"status": report["status"], "check_count": len(checks), "failed_count": report["failed_count"]}, sort_keys=True))
        run.finish("PASS" if passed else "FAIL")
        if not passed:
            raise AssertionError("S4 independent verification failed")
    except BaseException as exc:
        if not run.finished:
            run.fail(exc)
        raise


if __name__ == "__main__":
    main()