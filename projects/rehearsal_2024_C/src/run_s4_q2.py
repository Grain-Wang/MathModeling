"""Run the frozen S4 Q2 temperature correction and its sensitivity checks."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from s3_common import (
    DEFAULT_CONFIG,
    S3_RESULTS_ROOT,
    load_features_and_folds,
    load_frozen_config,
    regression_metrics,
    set_global_seed,
    smearing_factor,
    verify_contract_registry,
    write_csv,
    write_json,
)
from s4_common import S4_RESULTS_ROOT, s4_run

EXPERIMENT_IDS = {"main": "EXP-Q2-MAIN-001", "sensitivity": "EXP-Q2-SENS-001"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=sorted(EXPERIMENT_IDS), required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def q2_design(data: pd.DataFrame, b_field: str, include_temperature: bool) -> np.ndarray:
    columns = [
        np.log(data["frequency_Hz"].to_numpy(dtype=np.float64)),
        np.log(data[b_field].to_numpy(dtype=np.float64)),
    ]
    if include_temperature:
        temperature_scaled = (data["temperature_C"].to_numpy(dtype=np.float64) - 25.0) / 65.0
        columns.extend([temperature_scaled, temperature_scaled**2])
    design = np.column_stack(columns)
    if not np.isfinite(design).all():
        raise ValueError("Q2 design contains non-finite values")
    return design


def fit_predict(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    *,
    b_field: str = "b_m_T",
    include_temperature: bool = True,
) -> tuple[LinearRegression, float, np.ndarray]:
    x_train = q2_design(train, b_field, include_temperature)
    y_log = np.log(train["core_loss_W_per_m3"].to_numpy(dtype=np.float64))
    model = LinearRegression(fit_intercept=True)
    model.fit(x_train, y_log)
    fitted = model.predict(x_train)
    smear = smearing_factor(y_log, fitted)
    prediction = np.maximum(1e-9, np.exp(model.predict(q2_design(validation, b_field, include_temperature))) * smear)
    if not np.isfinite(prediction).all() or np.any(prediction <= 0):
        raise ValueError("Q2 prediction is invalid")
    return model, smear, prediction


def parameter_record(scope: str, model: LinearRegression, smear: float, train_n: int, validation_n: int) -> dict[str, Any]:
    return {
        "scope": scope,
        "train_n": train_n,
        "validation_n": validation_n,
        "log_k_at_25C": float(model.intercept_),
        "k_at_25C": float(math.exp(model.intercept_)),
        "alpha_frequency": float(model.coef_[0]),
        "beta_b_peak": float(model.coef_[1]),
        "temperature_linear_scaled_25_to_90": float(model.coef_[2]),
        "temperature_quadratic_scaled_25_to_90": float(model.coef_[3]),
        "smearing_factor": float(smear),
    }


def q2_data() -> pd.DataFrame:
    _, _, all_data = load_features_and_folds()
    data = all_data[(all_data["material"] == "材料1") & (all_data["waveform"] == "正弦波")].copy()
    data = data.sort_values("row_id").reset_index(drop=True)
    if len(data) != 1067:
        raise ValueError(f"Expected 1067 Q2 rows, got {len(data)}")
    return data


def cross_fit(data: pd.DataFrame, b_field: str = "b_m_T") -> tuple[np.ndarray, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    folds = data["regression_outer_fold"].to_numpy(dtype=int)
    groups = data["condition_group"].to_numpy(dtype=object)
    prediction = np.full(len(data), np.nan, dtype=np.float64)
    parameters: list[dict[str, Any]] = []
    lineage: list[dict[str, Any]] = []
    models: dict[str, Any] = {}
    for fold in sorted(np.unique(folds)):
        train_index = np.flatnonzero(folds != fold)
        valid_index = np.flatnonzero(folds == fold)
        overlap = set(groups[train_index]).intersection(groups[valid_index])
        if overlap:
            raise AssertionError(f"Q2 S4 group leakage in fold {fold}")
        model, smear, fold_prediction = fit_predict(
            data.iloc[train_index], data.iloc[valid_index], b_field=b_field, include_temperature=True
        )
        prediction[valid_index] = fold_prediction
        parameters.append(parameter_record(f"outer_fold_{int(fold)}", model, smear, len(train_index), len(valid_index)))
        lineage.append(
            {
                "outer_fold": int(fold),
                "train_n": len(train_index),
                "validation_n": len(valid_index),
                "train_group_count": len(set(groups[train_index])),
                "validation_group_count": len(set(groups[valid_index])),
                "group_overlap_count": len(overlap),
            }
        )
        models[f"q2-quadratic-temperature-fold-{int(fold)}"] = {"model": model, "smearing_factor": smear, "b_field": b_field}
    if not np.isfinite(prediction).all():
        raise AssertionError("Q2 S4 OOF coverage incomplete")
    return prediction, parameters, lineage, models


def run_main(config_path: Path) -> None:
    run = s4_run(EXPERIMENT_IDS["main"], config_path, "main")
    try:
        config = load_frozen_config(config_path)
        run.record_contract_hashes(verify_contract_registry(config))
        set_global_seed(int(config["seeds"]["global"]))
        for path in (
            Path(__file__).resolve(),
            Path(__file__).with_name("s3_common.py").resolve(),
            Path(__file__).with_name("s4_common.py").resolve(),
            S3_RESULTS_ROOT / "data" / "feature_table.csv",
            S3_RESULTS_ROOT / "folds" / "fold_assignments.csv",
            S3_RESULTS_ROOT / "q2" / "baseline_oof_predictions.csv",
            S3_RESULTS_ROOT / "q2" / "baseline_metrics.json",
            S3_RESULTS_ROOT / "q2" / "metrics_by_temperature.csv",
        ):
            run.record_input(path)
        data = q2_data()
        prediction, parameter_rows, lineage_rows, fold_models = cross_fit(data)
        baseline_oof = pd.read_csv(S3_RESULTS_ROOT / "q2" / "baseline_oof_predictions.csv").sort_values("row_id").reset_index(drop=True)
        if list(data["row_id"]) != list(baseline_oof["row_id"]):
            raise ValueError("Q2 S3/S4 OOF identity mismatch")
        baseline_metrics = json.loads((S3_RESULTS_ROOT / "q2" / "baseline_metrics.json").read_text(encoding="utf-8"))
        baseline_by_temperature = pd.read_csv(S3_RESULTS_ROOT / "q2" / "metrics_by_temperature.csv")
        temperature_rows: list[dict[str, Any]] = []
        for temperature, subset in data.assign(y_pred_oof=prediction).groupby("temperature_C", observed=True):
            candidate_metrics = regression_metrics(subset["core_loss_W_per_m3"], subset["y_pred_oof"])
            baseline_row = baseline_by_temperature[baseline_by_temperature["temperature_C"] == int(temperature)].iloc[0]
            temperature_rows.append(
                {
                    "temperature_C": int(temperature),
                    **{f"candidate_{key}": value for key, value in candidate_metrics.items()},
                    "baseline_rmsle": float(baseline_row["rmsle"]),
                    "rmsle_relative_change": (float(candidate_metrics["rmsle"]) - float(baseline_row["rmsle"])) / float(baseline_row["rmsle"]),
                    "not_degraded": bool(float(candidate_metrics["rmsle"]) <= float(baseline_row["rmsle"])),
                }
            )
        candidate_metrics = regression_metrics(data["core_loss_W_per_m3"], prediction)
        baseline_rmsle = float(baseline_metrics["oof"]["rmsle"])
        improved = float(candidate_metrics["rmsle"]) < baseline_rmsle
        nondegraded_temperature_count = sum(bool(row["not_degraded"]) for row in temperature_rows)
        adopted = improved and nondegraded_temperature_count >= 3
        full_model, full_smear, _ = fit_predict(data, data.iloc[:1])
        parameter_rows.append(parameter_record("full_fit", full_model, full_smear, len(data), 0))

        output_dir = S4_RESULTS_ROOT / "q2"
        oof_path = output_dir / "quadratic_temperature_oof_predictions.csv"
        parameters_path = output_dir / "quadratic_temperature_parameters.csv"
        temperature_path = output_dir / "quadratic_temperature_by_temperature.csv"
        lineage_path = output_dir / "quadratic_temperature_lineage.csv"
        model_path = output_dir / "quadratic_temperature_models.joblib"
        metrics_path = output_dir / "quadratic_temperature_metrics.json"
        evidence_path = run.output_dir / "metrics.json"
        oof = data[["row_id", "temperature_C", "frequency_Hz", "b_m_T", "b_half_pp_T", "condition_group", "regression_outer_fold", "core_loss_W_per_m3"]].copy()
        oof["y_pred_oof"] = prediction
        oof["baseline_y_pred_oof"] = baseline_oof["y_pred_oof"].to_numpy(dtype=np.float64)
        oof["absolute_log_error"] = np.abs(np.log1p(oof["core_loss_W_per_m3"]) - np.log1p(oof["y_pred_oof"]))
        write_csv(oof_path, oof)
        write_csv(parameters_path, pd.DataFrame(parameter_rows))
        write_csv(temperature_path, pd.DataFrame(temperature_rows))
        write_csv(lineage_path, pd.DataFrame(lineage_rows))
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"fold_models": fold_models, "full_model": full_model, "full_smearing_factor": full_smear}, model_path, compress=3)
        metrics = {
            "status": "PASS",
            "model": "Steinmetz with anchored quadratic multiplicative temperature correction",
            "temperature_basis": "z=(temperature_C-25)/65; multiplier=exp(gamma1*z+gamma2*z^2)",
            "same_oof_rows_and_folds_as_baseline": True,
            "candidate_oof": candidate_metrics,
            "baseline_oof": baseline_metrics["oof"],
            "relative_rmsle_improvement": (baseline_rmsle - float(candidate_metrics["rmsle"])) / baseline_rmsle,
            "nondegraded_temperature_count": nondegraded_temperature_count,
            "adoption_rule": "overall RMSLE decreases and at least 3 of 4 temperatures do not degrade",
            "adopted": bool(adopted),
            "winner": "quadratic_temperature" if adopted else "traditional_steinmetz",
            "conditional_upgrade_triggered": bool(not adopted),
            "failure_flags": {
                "group_leakage": any(row["group_overlap_count"] != 0 for row in lineage_rows),
                "nonpositive_or_nonfinite_prediction": False,
            },
        }
        write_json(metrics_path, metrics)
        write_json(evidence_path, metrics)
        for path in (oof_path, parameters_path, temperature_path, lineage_path, model_path, metrics_path, evidence_path):
            run.record_output(path)
        run.log(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


def run_sensitivity(config_path: Path) -> None:
    run = s4_run(EXPERIMENT_IDS["sensitivity"], config_path, "sensitivity")
    try:
        config = load_frozen_config(config_path)
        run.record_contract_hashes(verify_contract_registry(config))
        set_global_seed(int(config["seeds"]["global"]))
        main_metrics_path = S4_RESULTS_ROOT / "q2" / "quadratic_temperature_metrics.json"
        for path in (
            Path(__file__).resolve(),
            Path(__file__).with_name("s3_common.py").resolve(),
            Path(__file__).with_name("s4_common.py").resolve(),
            S3_RESULTS_ROOT / "data" / "feature_table.csv",
            S3_RESULTS_ROOT / "folds" / "fold_assignments.csv",
            S3_RESULTS_ROOT / "q2" / "leave_one_temperature_out.csv",
            main_metrics_path,
        ):
            run.record_input(path)
        main_metrics = json.loads(main_metrics_path.read_text(encoding="utf-8"))
        data = q2_data()
        primary_prediction, _, _, _ = cross_fit(data, "b_m_T")
        peak_prediction, _, peak_lineage, _ = cross_fit(data, "b_half_pp_T")
        deduplicated = data.drop_duplicates("exact_record_sha256", keep="first").reset_index(drop=True)
        dedup_prediction, _, dedup_lineage, _ = cross_fit(deduplicated, "b_m_T")
        summary_rows = [
            {"analysis": "primary_Bm_all_rows", **regression_metrics(data["core_loss_W_per_m3"], primary_prediction)},
            {"analysis": "peak_to_peak_over_2_all_rows", **regression_metrics(data["core_loss_W_per_m3"], peak_prediction)},
            {"analysis": "primary_Bm_exact_duplicates_collapsed", **regression_metrics(deduplicated["core_loss_W_per_m3"], dedup_prediction)},
        ]
        baseline_loto = pd.read_csv(S3_RESULTS_ROOT / "q2" / "leave_one_temperature_out.csv")
        loto_rows: list[dict[str, Any]] = []
        for temperature in sorted(data["temperature_C"].unique()):
            train = data[data["temperature_C"] != temperature]
            valid = data[data["temperature_C"] == temperature]
            _, _, main_prediction = fit_predict(train, valid, include_temperature=True)
            _, _, base_prediction = fit_predict(train, valid, include_temperature=False)
            main_result = regression_metrics(valid["core_loss_W_per_m3"], main_prediction)
            base_result = regression_metrics(valid["core_loss_W_per_m3"], base_prediction)
            recorded = baseline_loto[baseline_loto["heldout_temperature_C"] == int(temperature)].iloc[0]
            if not np.isclose(float(recorded["rmsle"]), float(base_result["rmsle"]), rtol=1e-9, atol=1e-12):
                raise AssertionError("Q2 LOTO Baseline recomputation mismatch")
            loto_rows.append(
                {
                    "heldout_temperature_C": int(temperature),
                    "quadratic_temperature_rmsle": float(main_result["rmsle"]),
                    "traditional_steinmetz_rmsle": float(base_result["rmsle"]),
                    "relative_rmsle_improvement": (float(base_result["rmsle"]) - float(main_result["rmsle"])) / float(base_result["rmsle"]),
                    "quadratic_better": bool(float(main_result["rmsle"]) < float(base_result["rmsle"])),
                }
            )
        output_dir = S4_RESULTS_ROOT / "q2"
        summary_path = output_dir / "sensitivity_summary.csv"
        loto_path = output_dir / "leave_one_temperature_comparison.csv"
        metrics_path = output_dir / "sensitivity_metrics.json"
        evidence_path = run.output_dir / "metrics.json"
        write_csv(summary_path, pd.DataFrame(summary_rows))
        write_csv(loto_path, pd.DataFrame(loto_rows))
        primary_rmsle = float(summary_rows[0]["rmsle"])
        peak_change = (float(summary_rows[1]["rmsle"]) - primary_rmsle) / primary_rmsle
        dedup_change = (float(summary_rows[2]["rmsle"]) - primary_rmsle) / primary_rmsle
        metrics = {
            "status": "PASS",
            "winner_from_main": main_metrics["winner"],
            "primary_rmsle": primary_rmsle,
            "peak_definition_relative_rmsle_change": peak_change,
            "duplicate_collapse_relative_rmsle_change": dedup_change,
            "leave_one_temperature_quadratic_better_count": sum(row["quadratic_better"] for row in loto_rows),
            "boundary_temperature_results": {str(row["heldout_temperature_C"]): row for row in loto_rows if row["heldout_temperature_C"] in (25, 90)},
            "conclusion_reversal": bool(abs(peak_change) > 0.10 or abs(dedup_change) > 0.10),
            "group_leakage": any(row["group_overlap_count"] != 0 for row in peak_lineage + dedup_lineage),
        }
        write_json(metrics_path, metrics)
        write_json(evidence_path, metrics)
        for path in (summary_path, loto_path, metrics_path, evidence_path):
            run.record_output(path)
        run.log(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    if args.mode == "main":
        run_main(config_path)
    else:
        run_sensitivity(config_path)


if __name__ == "__main__":
    main()