"""Run the approved Q4 median references and nested grouped Ridge Baseline."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from s3_common import (
    DEFAULT_CONFIG,
    MATERIAL_LABELS,
    Q4_CATEGORICAL_FEATURES,
    Q4_NUMERIC_FEATURES,
    S3_RESULTS_ROOT,
    TEMPERATURES,
    WAVEFORM_LABELS,
    ExperimentRun,
    load_features_and_folds,
    load_frozen_config,
    regression_metrics,
    set_global_seed,
    sha256_file,
    smearing_factor,
    verify_contract_registry,
    write_csv,
    write_json,
)


EXPERIMENT_IDS = {
    "median": "EXP-Q4-NULL-001",
    "ridge": "EXP-Q4-BASE-001",
}
GROUP_FIELDS = ["material", "waveform", "temperature_C"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=sorted(EXPERIMENT_IDS), required=True)
    parser.add_argument("--stage", choices=["baseline"], default="baseline")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def group_hash(groups: np.ndarray) -> str:
    return hashlib.sha256(("\n".join(sorted(map(str, set(groups)))) + "\n").encode("utf-8")).hexdigest().upper()


def run_median(data: pd.DataFrame, run: ExperimentRun) -> None:
    y = data["core_loss_W_per_m3"].to_numpy(dtype=np.float64)
    folds = data["regression_outer_fold"].to_numpy(dtype=int)
    groups = data["condition_group"].to_numpy(dtype=object)
    global_prediction = np.full(len(data), np.nan, dtype=np.float64)
    grouped_prediction = np.full(len(data), np.nan, dtype=np.float64)
    lineage_rows: list[dict[str, object]] = []

    for fold in sorted(np.unique(folds)):
        train_index = np.flatnonzero(folds != fold)
        valid_index = np.flatnonzero(folds == fold)
        overlap = set(groups[train_index]).intersection(groups[valid_index])
        if overlap:
            raise AssertionError(f"Q4 median condition_group leakage in fold {fold}")
        train = data.iloc[train_index]
        valid = data.iloc[valid_index]
        global_median = float(np.median(train["core_loss_W_per_m3"]))
        medians = train.groupby(GROUP_FIELDS, observed=True)["core_loss_W_per_m3"].median()
        keys = pd.MultiIndex.from_frame(valid[GROUP_FIELDS])
        mapped = medians.reindex(keys).to_numpy(dtype=np.float64)
        mapped = np.where(np.isfinite(mapped), mapped, global_median)
        global_prediction[valid_index] = global_median
        grouped_prediction[valid_index] = mapped
        lineage_rows.append(
            {
                "outer_fold": int(fold),
                "train_n": len(train_index),
                "validation_n": len(valid_index),
                "train_group_count": len(set(groups[train_index])),
                "validation_group_count": len(set(groups[valid_index])),
                "group_overlap_count": len(overlap),
                "global_median_W_per_m3": global_median,
                "group_fallback_count": int(np.sum(~np.isfinite(medians.reindex(keys).to_numpy(dtype=np.float64)))),
            }
        )

    if not np.isfinite(global_prediction).all() or not np.isfinite(grouped_prediction).all():
        raise AssertionError("Q4 median OOF coverage incomplete")
    output_dir = S3_RESULTS_ROOT / "q4"
    oof_path = output_dir / "median_oof_predictions.csv"
    metrics_path = output_dir / "median_baseline_metrics.json"
    lineage_path = output_dir / "median_oof_lineage.csv"
    evidence_metrics_path = run.output_dir / "metrics.json"
    oof = data[["row_id", "material", "waveform", "temperature_C", "condition_group", "regression_outer_fold", "core_loss_W_per_m3"]].copy()
    oof["global_median_y_pred_oof"] = global_prediction
    oof["grouped_median_y_pred_oof"] = grouped_prediction
    write_csv(oof_path, oof)
    write_csv(lineage_path, pd.DataFrame(lineage_rows))
    metrics = {
        "status": "PASS",
        "global_median_oof": regression_metrics(y, global_prediction),
        "grouped_median_oof": regression_metrics(y, grouped_prediction),
        "outer_folds": len(np.unique(folds)),
        "group_fields": GROUP_FIELDS,
        "failure_flags": {"group_leakage": any(row["group_overlap_count"] != 0 for row in lineage_rows)},
    }
    write_json(metrics_path, metrics)
    write_json(evidence_metrics_path, metrics)
    for path in (oof_path, metrics_path, lineage_path, evidence_metrics_path):
        run.record_output(path)
    run.log(json.dumps(metrics, ensure_ascii=False, sort_keys=True))


def make_ridge_model(alpha: float) -> Pipeline:
    categorical_levels = [MATERIAL_LABELS, WAVEFORM_LABELS, [str(value) for value in TEMPERATURES]]
    transformer = ColumnTransformer(
        [
            ("numeric", StandardScaler(), Q4_NUMERIC_FEATURES),
            (
                "categorical",
                OneHotEncoder(categories=categorical_levels, handle_unknown="ignore", sparse_output=False),
                Q4_CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )
    return Pipeline([("features", transformer), ("model", Ridge(alpha=alpha))])


def predict_positive(model: Pipeline, smear: float, x: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    prediction_log = model.predict(x)
    prediction = np.maximum(1e-9, np.exp(prediction_log) * smear)
    if not np.isfinite(prediction).all() or np.any(prediction <= 0):
        raise ValueError("Q4 Ridge produced invalid predictions")
    return prediction_log, prediction


def select_alpha(
    x: pd.DataFrame,
    y: np.ndarray,
    groups: np.ndarray,
    alphas: list[float],
    seed: int,
) -> tuple[float, list[dict[str, object]]]:
    splitter = GroupKFold(n_splits=3, shuffle=True, random_state=seed)
    rows: list[dict[str, object]] = []
    for alpha in alphas:
        fold_scores: list[float] = []
        for inner_fold, (train_index, valid_index) in enumerate(splitter.split(x, groups=groups)):
            overlap = set(groups[train_index]).intersection(groups[valid_index])
            if overlap:
                raise AssertionError("Q4 inner condition_group leakage")
            model = make_ridge_model(alpha)
            y_log_train = np.log(y[train_index])
            model.fit(x.iloc[train_index], y_log_train)
            smear = smearing_factor(y_log_train, model.predict(x.iloc[train_index]))
            _, prediction = predict_positive(model, smear, x.iloc[valid_index])
            score = regression_metrics(y[valid_index], prediction)["rmsle"]
            fold_scores.append(float(score))
            rows.append({"alpha": alpha, "inner_fold": inner_fold, "rmsle": score})
        rows.append({"alpha": alpha, "inner_fold": "mean", "rmsle": float(np.mean(fold_scores))})
    means = [row for row in rows if row["inner_fold"] == "mean"]
    means.sort(key=lambda row: (float(row["rmsle"]), -float(row["alpha"])))
    return float(means[0]["alpha"]), rows


def q4_subgroup_metrics(data: pd.DataFrame, prediction: np.ndarray, minimum_n: int, minimum_folds: int) -> pd.DataFrame:
    evaluated = data.copy()
    evaluated["y_pred_oof"] = prediction
    evaluated["frequency_quartile"] = pd.qcut(evaluated["frequency_Hz"], q=4, duplicates="drop").astype(str)
    evaluated["b_m_quartile"] = pd.qcut(evaluated["b_m_T"], q=4, duplicates="drop").astype(str)
    rows: list[dict[str, object]] = []
    for field in ("material", "waveform", "temperature_C", "frequency_quartile", "b_m_quartile"):
        for value, subset in evaluated.groupby(field, observed=True):
            metrics = regression_metrics(subset["core_loss_W_per_m3"], subset["y_pred_oof"])
            fold_count = int(subset["regression_outer_fold"].nunique())
            rows.append(
                {
                    "group_field": field,
                    "group_value": value,
                    **metrics,
                    "outer_fold_count": fold_count,
                    "is_major_subgroup": bool(len(subset) >= minimum_n and fold_count >= minimum_folds),
                }
            )
    return pd.DataFrame(rows)


def run_ridge(data: pd.DataFrame, config: dict[str, object], run: ExperimentRun) -> None:
    data = data.copy()
    data["temperature_label"] = data["temperature_C"].astype(int).astype(str)
    missing_features = sorted(set(Q4_NUMERIC_FEATURES + Q4_CATEGORICAL_FEATURES) - set(data.columns))
    if missing_features:
        raise ValueError(f"Q4 feature columns missing: {missing_features}")
    x = data[Q4_NUMERIC_FEATURES + Q4_CATEGORICAL_FEATURES]
    y = data["core_loss_W_per_m3"].to_numpy(dtype=np.float64)
    y_log = np.log(y)
    folds = data["regression_outer_fold"].to_numpy(dtype=int)
    groups = data["condition_group"].to_numpy(dtype=object)
    alphas = [float(value) for value in config["models"]["q4"]["search_space"]["ridge"]["alpha"]]
    seed = int(config["seeds"]["global"])
    prediction = np.full(len(data), np.nan, dtype=np.float64)
    prediction_log = np.full(len(data), np.nan, dtype=np.float64)
    model_ids = np.empty(len(data), dtype=object)
    selection_rows: list[dict[str, object]] = []
    lineage_rows: list[dict[str, object]] = []
    selected_alphas: list[float] = []
    fold_models: dict[str, dict[str, object]] = {}

    for fold in sorted(np.unique(folds)):
        train_index = np.flatnonzero(folds != fold)
        valid_index = np.flatnonzero(folds == fold)
        overlap = set(groups[train_index]).intersection(groups[valid_index])
        if overlap:
            raise AssertionError(f"Q4 outer condition_group leakage in fold {fold}")
        alpha, inner_rows = select_alpha(
            x.iloc[train_index].reset_index(drop=True),
            y[train_index],
            groups[train_index],
            alphas,
            seed + int(fold),
        )
        for row in inner_rows:
            selection_rows.append({"outer_fold": int(fold), **row})
        model = make_ridge_model(alpha)
        model.fit(x.iloc[train_index], y_log[train_index])
        smear = smearing_factor(y_log[train_index], model.predict(x.iloc[train_index]))
        fold_log, fold_prediction = predict_positive(model, smear, x.iloc[valid_index])
        prediction_log[valid_index] = fold_log
        prediction[valid_index] = fold_prediction
        model_id = f"q4-ridge-fold-{int(fold)}"
        model_ids[valid_index] = model_id
        selected_alphas.append(alpha)
        fold_models[model_id] = {"model": model, "smearing_factor": smear, "validation_fold": int(fold)}
        lineage_rows.append(
            {
                "outer_fold": int(fold),
                "model_id": model_id,
                "selected_alpha": alpha,
                "smearing_factor": smear,
                "train_n": len(train_index),
                "validation_n": len(valid_index),
                "train_group_count": len(set(groups[train_index])),
                "validation_group_count": len(set(groups[valid_index])),
                "group_overlap_count": len(overlap),
                "train_groups_sha256": group_hash(groups[train_index]),
                "validation_groups_sha256": group_hash(groups[valid_index]),
            }
        )
        run.log(f"outer_fold={fold} selected_alpha={alpha} validation_n={len(valid_index)}")

    if not np.isfinite(prediction).all() or pd.isna(model_ids).any():
        raise AssertionError("Q4 Ridge OOF predictions or model lineage are incomplete")

    alpha_counts = Counter(selected_alphas)
    full_alpha = sorted(alpha_counts, key=lambda value: (-alpha_counts[value], -value))[0]
    full_model = make_ridge_model(full_alpha)
    full_model.fit(x, y_log)
    full_smear = smearing_factor(y_log, full_model.predict(x))
    full_prediction_log, full_prediction = predict_positive(full_model, full_smear, x)

    median_path = S3_RESULTS_ROOT / "q4" / "median_oof_predictions.csv"
    median_metrics_path = S3_RESULTS_ROOT / "q4" / "median_baseline_metrics.json"
    run.record_input(median_path)
    run.record_input(median_metrics_path)
    median_oof = pd.read_csv(median_path)
    median_metrics = json.loads(median_metrics_path.read_text(encoding="utf-8"))
    if list(median_oof["row_id"]) != list(data["row_id"]):
        raise ValueError("Q4 median and Ridge row order mismatch")

    output_dir = S3_RESULTS_ROOT / "q4"
    oof_path = output_dir / "ridge_oof_predictions.csv"
    full_prediction_path = output_dir / "ridge_full_fit_training_predictions.csv"
    metrics_path = output_dir / "ridge_metrics.json"
    subgroup_path = output_dir / "ridge_subgroup_metrics.csv"
    selection_path = output_dir / "ridge_inner_selection.csv"
    lineage_path = output_dir / "ridge_oof_lineage.csv"
    fold_models_path = output_dir / "ridge_fold_models.joblib"
    full_model_path = output_dir / "ridge_full_model.joblib"
    evidence_metrics_path = run.output_dir / "metrics.json"

    oof = data[["row_id", "material", "waveform", "temperature_C", "frequency_Hz", "b_m_T", "condition_group", "regression_outer_fold", "core_loss_W_per_m3"]].copy()
    oof["oof_model_id"] = model_ids
    oof["y_pred_log_oof"] = prediction_log
    oof["y_pred_oof"] = prediction
    oof["absolute_log_error"] = np.abs(np.log1p(y) - np.log1p(prediction))
    full_predictions = data[["row_id", "condition_group", "regression_outer_fold"]].copy()
    full_predictions["full_model_id"] = "q4-ridge-full"
    full_predictions["y_pred_log_full"] = full_prediction_log
    full_predictions["y_pred_full"] = full_prediction
    write_csv(oof_path, oof)
    write_csv(full_prediction_path, full_predictions)
    write_csv(selection_path, pd.DataFrame(selection_rows))
    write_csv(lineage_path, pd.DataFrame(lineage_rows))
    minimum_n = int(config["validation_contract"]["q4_major_subgroup_min_n"])
    minimum_folds = int(config["validation_contract"]["q4_major_subgroup_min_outer_folds"])
    write_csv(subgroup_path, q4_subgroup_metrics(data, prediction, minimum_n, minimum_folds))
    fold_models_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(fold_models, fold_models_path, compress=3)
    joblib.dump({"model": full_model, "smearing_factor": full_smear, "alpha": full_alpha}, full_model_path, compress=3)

    ridge_oof_metrics = regression_metrics(y, prediction)
    beats_global = ridge_oof_metrics["rmsle"] < median_metrics["global_median_oof"]["rmsle"]
    beats_grouped = ridge_oof_metrics["rmsle"] < median_metrics["grouped_median_oof"]["rmsle"]
    metrics = {
        "status": "PASS",
        "model": "nested grouped Ridge on log loss",
        "features": {"numeric": Q4_NUMERIC_FEATURES, "categorical": Q4_CATEGORICAL_FEATURES},
        "outer_folds": len(np.unique(folds)),
        "inner_folds": 3,
        "oof": ridge_oof_metrics,
        "median_references": median_metrics,
        "beats_global_median_rmsle": bool(beats_global),
        "beats_grouped_median_rmsle": bool(beats_grouped),
        "beats_at_least_one_median_reference": bool(beats_global or beats_grouped),
        "full_fit_alpha_from_outer_mode": full_alpha,
        "full_fit_smearing_factor": full_smear,
        "full_model_sha256": sha256_file(full_model_path),
        "fold_models_sha256": sha256_file(fold_models_path),
        "failure_flags": {
            "group_leakage": any(row["group_overlap_count"] != 0 for row in lineage_rows),
            "does_not_beat_any_median_reference": not (beats_global or beats_grouped),
            "nonpositive_or_nonfinite_prediction": False,
        },
    }
    write_json(metrics_path, metrics)
    write_json(evidence_metrics_path, metrics)
    for path in (
        oof_path,
        full_prediction_path,
        metrics_path,
        subgroup_path,
        selection_path,
        lineage_path,
        fold_models_path,
        full_model_path,
        evidence_metrics_path,
    ):
        run.record_output(path)
    run.log(json.dumps({"oof": ridge_oof_metrics, "beats_at_least_one_median": beats_global or beats_grouped}, ensure_ascii=False, sort_keys=True))


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    run = ExperimentRun(EXPERIMENT_IDS[args.model], config_path)
    try:
        config = load_frozen_config(config_path)
        contract_hashes = verify_contract_registry(config)
        run.record_contract_hashes(contract_hashes)
        seed = int(config["seeds"]["global"])
        set_global_seed(seed)
        run.record_input(Path(__file__).resolve())
        run.record_input(Path(__file__).with_name("s3_common.py").resolve())
        feature_path = S3_RESULTS_ROOT / "data" / "feature_table.csv"
        fold_path = S3_RESULTS_ROOT / "folds" / "fold_assignments.csv"
        schema_path = S3_RESULTS_ROOT / "data" / "feature_schema.json"
        for path in (feature_path, fold_path, schema_path):
            run.record_input(path)
        _, _, data = load_features_and_folds()
        data = data.sort_values("row_id").reset_index(drop=True)
        if args.model == "median":
            run_median(data, run)
        else:
            run_ridge(data, config, run)
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


if __name__ == "__main__":
    main()
