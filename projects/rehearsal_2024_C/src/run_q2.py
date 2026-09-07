"""Run the approved Q2 traditional Steinmetz Baseline on material 1 sine waves."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from s3_common import (
    DEFAULT_CONFIG,
    S3_RESULTS_ROOT,
    ExperimentRun,
    load_features_and_folds,
    load_frozen_config,
    regression_metrics,
    set_global_seed,
    smearing_factor,
    verify_contract_registry,
    write_csv,
    write_json,
)


EXPERIMENT_ID = "EXP-Q2-BASE-001"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["steinmetz"], default="steinmetz")
    parser.add_argument("--stage", choices=["baseline"], default="baseline")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def fit_predict(train: pd.DataFrame, validation: pd.DataFrame) -> tuple[LinearRegression, float, np.ndarray]:
    x_train = train[["log_frequency_Hz", "log_b_m_T"]].to_numpy(dtype=np.float64)
    y_train_log = np.log(train["core_loss_W_per_m3"].to_numpy(dtype=np.float64))
    model = LinearRegression(fit_intercept=True)
    model.fit(x_train, y_train_log)
    fitted_train = model.predict(x_train)
    smear = smearing_factor(y_train_log, fitted_train)
    predicted_log = model.predict(validation[["log_frequency_Hz", "log_b_m_T"]].to_numpy(dtype=np.float64))
    prediction = np.maximum(1e-9, np.exp(predicted_log) * smear)
    if not np.isfinite(prediction).all() or np.any(prediction <= 0):
        raise ValueError("Steinmetz produced invalid predictions")
    return model, smear, prediction


def parameter_record(scope: str, model: LinearRegression, smear: float, train_n: int, validation_n: int) -> dict[str, object]:
    return {
        "scope": scope,
        "train_n": train_n,
        "validation_n": validation_n,
        "log_k": float(model.intercept_),
        "k": float(math.exp(model.intercept_)),
        "alpha_frequency": float(model.coef_[0]),
        "beta_b_peak": float(model.coef_[1]),
        "smearing_factor": smear,
    }


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    run = ExperimentRun(EXPERIMENT_ID, config_path)
    try:
        config = load_frozen_config(config_path)
        verify_contract_registry(config)
        seed = int(config["seeds"]["global"])
        set_global_seed(seed)
        run.record_input(Path(__file__).resolve())
        run.record_input(Path(__file__).with_name("s3_common.py").resolve())
        feature_path = S3_RESULTS_ROOT / "data" / "feature_table.csv"
        fold_path = S3_RESULTS_ROOT / "folds" / "fold_assignments.csv"
        run.record_input(feature_path)
        run.record_input(fold_path)
        _, _, all_data = load_features_and_folds()
        data = all_data[(all_data["material"] == "材料1") & (all_data["waveform"] == "正弦波")].copy()
        data = data.sort_values("row_id").reset_index(drop=True)
        if len(data) != 1067:
            raise ValueError(f"Expected 1067 material-1 sine rows, got {len(data)}")
        if np.any(data[["frequency_Hz", "b_m_T", "core_loss_W_per_m3"]].to_numpy() <= 0):
            raise ValueError("Q2 requires positive frequency, B_m and loss")

        folds = data["regression_outer_fold"].to_numpy(dtype=int)
        groups = data["condition_group"].to_numpy(dtype=object)
        prediction = np.full(len(data), np.nan, dtype=np.float64)
        median_prediction = np.full(len(data), np.nan, dtype=np.float64)
        parameter_rows: list[dict[str, object]] = []
        lineage_rows: list[dict[str, object]] = []
        fold_models: dict[str, dict[str, object]] = {}

        for fold in sorted(np.unique(folds)):
            train_index = np.flatnonzero(folds != fold)
            valid_index = np.flatnonzero(folds == fold)
            overlap = set(groups[train_index]).intersection(groups[valid_index])
            if overlap:
                raise AssertionError(f"Q2 condition_group leakage in fold {fold}")
            model, smear, fold_prediction = fit_predict(data.iloc[train_index], data.iloc[valid_index])
            prediction[valid_index] = fold_prediction
            median_prediction[valid_index] = float(np.median(data.iloc[train_index]["core_loss_W_per_m3"]))
            record = parameter_record(f"outer_fold_{int(fold)}", model, smear, len(train_index), len(valid_index))
            parameter_rows.append(record)
            lineage_rows.append(
                {
                    "outer_fold": int(fold),
                    "train_n": len(train_index),
                    "validation_n": len(valid_index),
                    "train_group_count": len(set(groups[train_index])),
                    "validation_group_count": len(set(groups[valid_index])),
                    "group_overlap_count": len(overlap),
                }
            )
            fold_models[f"q2-steinmetz-fold-{int(fold)}"] = {"model": model, "smearing_factor": smear}

        if not np.isfinite(prediction).all() or not np.isfinite(median_prediction).all():
            raise AssertionError("Q2 OOF coverage incomplete")

        full_model, full_smear, _ = fit_predict(data, data.iloc[:1])
        parameter_rows.append(parameter_record("full_fit", full_model, full_smear, len(data), 0))

        temperature_rows: list[dict[str, object]] = []
        for temperature, subset in data.assign(y_pred_oof=prediction).groupby("temperature_C", observed=True):
            temperature_rows.append({"temperature_C": int(temperature), **regression_metrics(subset["core_loss_W_per_m3"], subset["y_pred_oof"])})

        pressure_rows: list[dict[str, object]] = []
        for temperature in sorted(data["temperature_C"].unique()):
            train = data[data["temperature_C"] != temperature]
            valid = data[data["temperature_C"] == temperature]
            _, _, heldout_prediction = fit_predict(train, valid)
            pressure_rows.append(
                {
                    "heldout_temperature_C": int(temperature),
                    **regression_metrics(valid["core_loss_W_per_m3"], heldout_prediction),
                }
            )

        output_dir = S3_RESULTS_ROOT / "q2"
        oof_path = output_dir / "baseline_oof_predictions.csv"
        metrics_path = output_dir / "baseline_metrics.json"
        parameters_path = output_dir / "steinmetz_baseline_parameters.csv"
        temperature_path = output_dir / "metrics_by_temperature.csv"
        pressure_path = output_dir / "leave_one_temperature_out.csv"
        lineage_path = output_dir / "oof_lineage.csv"
        models_path = output_dir / "steinmetz_models.joblib"
        evidence_metrics_path = run.output_dir / "metrics.json"

        oof = data[["row_id", "temperature_C", "frequency_Hz", "b_m_T", "condition_group", "regression_outer_fold", "core_loss_W_per_m3"]].copy()
        oof["y_pred_oof"] = prediction
        oof["median_y_pred_oof"] = median_prediction
        oof["absolute_log_error"] = np.abs(np.log1p(oof["core_loss_W_per_m3"]) - np.log1p(oof["y_pred_oof"]))
        write_csv(oof_path, oof)
        write_csv(parameters_path, pd.DataFrame(parameter_rows))
        write_csv(temperature_path, pd.DataFrame(temperature_rows))
        write_csv(pressure_path, pd.DataFrame(pressure_rows))
        write_csv(lineage_path, pd.DataFrame(lineage_rows))
        models_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"fold_models": fold_models, "full_model": full_model, "full_smearing_factor": full_smear}, models_path, compress=3)

        metrics = {
            "status": "PASS",
            "model": "traditional Steinmetz log-linear regression",
            "subset_rows": len(data),
            "outer_folds": len(np.unique(folds)),
            "oof": regression_metrics(data["core_loss_W_per_m3"], prediction),
            "median_oof": regression_metrics(data["core_loss_W_per_m3"], median_prediction),
            "full_parameters": parameter_record("full_fit", full_model, full_smear, len(data), 0),
            "failure_flags": {
                "group_leakage": any(row["group_overlap_count"] != 0 for row in lineage_rows),
                "nonpositive_or_nonfinite_prediction": False,
            },
        }
        write_json(metrics_path, metrics)
        write_json(evidence_metrics_path, metrics)
        for path in (oof_path, metrics_path, parameters_path, temperature_path, pressure_path, lineage_path, models_path, evidence_metrics_path):
            run.record_output(path)
        run.log(json.dumps(metrics["oof"], ensure_ascii=False, sort_keys=True))
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


if __name__ == "__main__":
    main()
