"""Run the approved Q3 descriptive and additive association Baselines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler

from s3_common import (
    DEFAULT_CONFIG,
    MATERIAL_LABELS,
    S3_RESULTS_ROOT,
    TEMPERATURES,
    WAVEFORM_LABELS,
    ExperimentRun,
    load_features_and_folds,
    load_frozen_config,
    log_rmse,
    regression_metrics,
    set_global_seed,
    smearing_factor,
    verify_contract_registry,
    write_csv,
    write_json,
)


EXPERIMENT_IDS = {
    "descriptive": "EXP-Q3-DESC-001",
    "additive": "EXP-Q3-BASE-001",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=sorted(EXPERIMENT_IDS), required=True)
    parser.add_argument("--stage", choices=["baseline"], default="baseline")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def effect_code(series: pd.Series, levels: list[object], prefix: str) -> pd.DataFrame:
    values = series.to_numpy(dtype=object)
    unknown = set(values) - set(levels)
    if unknown:
        raise ValueError(f"Unknown {prefix} levels: {unknown}")
    reference = levels[-1]
    result: dict[str, np.ndarray] = {}
    for level in levels[:-1]:
        column = np.zeros(len(values), dtype=np.float64)
        column[values == level] = 1.0
        column[values == reference] = -1.0
        result[f"effect_{prefix}_{level}"] = column
    return pd.DataFrame(result, index=series.index)


def additive_design(data: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    design = data[["log_frequency_Hz", "log_b_m_T"]].copy()
    encoded = [
        effect_code(data["temperature_C"].astype(int), TEMPERATURES, "temperature"),
        effect_code(data["waveform"], WAVEFORM_LABELS, "waveform"),
        effect_code(data["material"], MATERIAL_LABELS, "material"),
    ]
    for frame in encoded:
        design = pd.concat([design, frame], axis=1)
    effect_columns = [column for column in design.columns if column.startswith("effect_")]
    return design, effect_columns


def make_additive_model(effect_columns: list[str], alpha: float, knots: int, degree: int) -> Pipeline:
    transformer = ColumnTransformer(
        [
            (
                "operating_splines",
                SplineTransformer(n_knots=knots, degree=degree, include_bias=False),
                ["log_frequency_Hz", "log_b_m_T"],
            ),
            ("effect_codes", "passthrough", effect_columns),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )
    return Pipeline(
        [
            ("features", transformer),
            ("scale", StandardScaler()),
            ("model", Ridge(alpha=alpha)),
        ]
    )


def run_descriptive(data: pd.DataFrame, run: ExperimentRun) -> None:
    output_dir = S3_RESULTS_ROOT / "q3"
    group_fields = ["temperature_C", "waveform", "material"]
    grouped = data.groupby(group_fields, observed=True)
    table = grouped.agg(
        n=("row_id", "size"),
        loss_q25_W_per_m3=("core_loss_W_per_m3", lambda values: float(np.quantile(values, 0.25))),
        loss_median_W_per_m3=("core_loss_W_per_m3", "median"),
        loss_q75_W_per_m3=("core_loss_W_per_m3", lambda values: float(np.quantile(values, 0.75))),
        frequency_min_Hz=("frequency_Hz", "min"),
        frequency_max_Hz=("frequency_Hz", "max"),
        b_m_min_T=("b_m_T", "min"),
        b_m_max_T=("b_m_T", "max"),
    ).reset_index()
    if len(table) != 48 or int(table["n"].sum()) != 12400 or np.any(table["n"] <= 0):
        raise AssertionError(f"Q3 expected 48 nonempty cells covering 12400 rows, got {len(table)}")

    common_frequency_min = float(table["frequency_min_Hz"].max())
    common_frequency_max = float(table["frequency_max_Hz"].min())
    common_b_m_min = float(table["b_m_min_T"].max())
    common_b_m_max = float(table["b_m_max_T"].min())
    has_common_support = common_frequency_min <= common_frequency_max and common_b_m_min <= common_b_m_max
    in_common_support = (
        data["frequency_Hz"].between(common_frequency_min, common_frequency_max, inclusive="both")
        & data["b_m_T"].between(common_b_m_min, common_b_m_max, inclusive="both")
    ) if has_common_support else pd.Series(False, index=data.index)

    marginal_rows: list[dict[str, object]] = []
    for field in group_fields:
        for value, subset in data.groupby(field, observed=True):
            marginal_rows.append(
                {
                    "factor": field,
                    "level": value,
                    "n": len(subset),
                    "loss_q25_W_per_m3": float(np.quantile(subset["core_loss_W_per_m3"], 0.25)),
                    "loss_median_W_per_m3": float(np.median(subset["core_loss_W_per_m3"])),
                    "loss_q75_W_per_m3": float(np.quantile(subset["core_loss_W_per_m3"], 0.75)),
                }
            )

    table_path = output_dir / "descriptive_factor_table.csv"
    marginal_path = output_dir / "descriptive_factor_marginals.csv"
    support_path = output_dir / "common_support_summary.json"
    metrics_path = run.output_dir / "metrics.json"
    write_csv(table_path, table)
    write_csv(marginal_path, pd.DataFrame(marginal_rows))
    support = {
        "status": "PASS",
        "factor_cell_count": len(table),
        "all_cells_nonempty": True,
        "common_frequency_Hz": [common_frequency_min, common_frequency_max],
        "common_b_m_T": [common_b_m_min, common_b_m_max],
        "has_global_rectangular_common_support": bool(has_common_support),
        "rows_in_global_common_support": int(in_common_support.sum()),
        "common_support_fraction": float(in_common_support.mean()),
        "interpretation": "Descriptive medians are unadjusted associations; unsupported cells require adjusted or limited comparisons.",
    }
    write_json(support_path, support)
    write_json(metrics_path, support)
    for path in (table_path, marginal_path, support_path, metrics_path):
        run.record_output(path)
    run.log(json.dumps(support, ensure_ascii=False, sort_keys=True))


def run_additive(data: pd.DataFrame, config: dict[str, object], run: ExperimentRun) -> None:
    design, effect_columns = additive_design(data)
    y = data["core_loss_W_per_m3"].to_numpy(dtype=np.float64)
    y_log = np.log(y)
    folds = data["regression_outer_fold"].to_numpy(dtype=int)
    groups = data["condition_group"].to_numpy(dtype=object)
    q3_config = config["models"]["q3"]["fixed_search"]
    alpha = 0.01
    if alpha not in [float(value) for value in q3_config["ridge_alpha"]]:
        raise ValueError("Frozen Q3 Baseline alpha is absent from approved grid")
    knots = int(q3_config["spline_knots"])
    degree = int(q3_config["spline_degree"])
    prediction = np.full(len(data), np.nan, dtype=np.float64)
    prediction_log = np.full(len(data), np.nan, dtype=np.float64)
    lineage_rows: list[dict[str, object]] = []
    coefficient_rows: list[dict[str, object]] = []
    fold_models: dict[str, dict[str, object]] = {}

    for fold in sorted(np.unique(folds)):
        train_index = np.flatnonzero(folds != fold)
        valid_index = np.flatnonzero(folds == fold)
        overlap = set(groups[train_index]).intersection(groups[valid_index])
        if overlap:
            raise AssertionError(f"Q3 condition_group leakage in fold {fold}")
        model = make_additive_model(effect_columns, alpha, knots, degree)
        model.fit(design.iloc[train_index], y_log[train_index])
        fitted_train = model.predict(design.iloc[train_index])
        smear = smearing_factor(y_log[train_index], fitted_train)
        predicted_log = model.predict(design.iloc[valid_index])
        predicted = np.maximum(1e-9, np.exp(predicted_log) * smear)
        prediction[valid_index] = predicted
        prediction_log[valid_index] = predicted_log
        transformed = model.named_steps["scale"].transform(model.named_steps["features"].transform(design.iloc[train_index]))
        raw_gram_condition = float(np.linalg.cond(np.asarray(transformed).T @ np.asarray(transformed)))
        gram_condition = raw_gram_condition if np.isfinite(raw_gram_condition) else None
        feature_names = model.named_steps["features"].get_feature_names_out()
        for name, coefficient in zip(feature_names, model.named_steps["model"].coef_, strict=True):
            coefficient_rows.append({"outer_fold": int(fold), "feature": name, "scaled_coefficient": float(coefficient)})
        lineage_rows.append(
            {
                "outer_fold": int(fold),
                "train_n": len(train_index),
                "validation_n": len(valid_index),
                "train_group_count": len(set(groups[train_index])),
                "validation_group_count": len(set(groups[valid_index])),
                "group_overlap_count": len(overlap),
                "smearing_factor": smear,
                "gram_condition_number": gram_condition,
                "gram_condition_nonfinite": gram_condition is None,
            }
        )
        fold_models[f"q3-additive-fold-{int(fold)}"] = {"model": model, "smearing_factor": smear}

    if not np.isfinite(prediction).all() or np.any(prediction <= 0):
        raise AssertionError("Q3 additive OOF predictions are incomplete or invalid")

    full_model = make_additive_model(effect_columns, alpha, knots, degree)
    full_model.fit(design, y_log)
    full_smear = smearing_factor(y_log, full_model.predict(design))

    output_dir = S3_RESULTS_ROOT / "q3"
    oof_path = output_dir / "additive_oof_predictions.csv"
    metrics_path = output_dir / "additive_metrics.json"
    coefficient_path = output_dir / "additive_fold_coefficients.csv"
    lineage_path = output_dir / "additive_oof_lineage.csv"
    models_path = output_dir / "additive_models.joblib"
    evidence_metrics_path = run.output_dir / "metrics.json"
    oof = data[["row_id", "temperature_C", "waveform", "material", "frequency_Hz", "b_m_T", "condition_group", "regression_outer_fold", "core_loss_W_per_m3"]].copy()
    oof["y_pred_log_oof"] = prediction_log
    oof["y_pred_oof"] = prediction
    oof["absolute_log_error"] = np.abs(np.log(y) - prediction_log)
    write_csv(oof_path, oof)
    write_csv(coefficient_path, pd.DataFrame(coefficient_rows))
    write_csv(lineage_path, pd.DataFrame(lineage_rows))
    models_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"fold_models": fold_models, "full_model": full_model, "full_smearing_factor": full_smear, "effect_columns": effect_columns}, models_path, compress=3)
    metrics = {
        "status": "PASS",
        "model": "additive effect-coded spline Ridge",
        "ridge_alpha": alpha,
        "spline_knots": knots,
        "spline_degree": degree,
        "outer_folds": len(np.unique(folds)),
        "oof_log_rmse": log_rmse(y, prediction),
        "oof_original_scale": regression_metrics(y, prediction),
        "max_finite_gram_condition_number": max(
            (row["gram_condition_number"] for row in lineage_rows if row["gram_condition_number"] is not None),
            default=None,
        ),
        "nonfinite_gram_condition_fold_count": sum(row["gram_condition_nonfinite"] for row in lineage_rows),
        "failure_flags": {
            "group_leakage": any(row["group_overlap_count"] != 0 for row in lineage_rows),
            "nonpositive_or_nonfinite_prediction": False,
        },
        "interpretation": "Adjusted association Baseline; coefficients are not causal effects.",
    }
    write_json(metrics_path, metrics)
    write_json(evidence_metrics_path, metrics)
    for path in (oof_path, metrics_path, coefficient_path, lineage_path, models_path, evidence_metrics_path):
        run.record_output(path)
    run.log(json.dumps(metrics, ensure_ascii=False, sort_keys=True))


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
        run.record_input(feature_path)
        run.record_input(fold_path)
        _, _, data = load_features_and_folds()
        data = data.sort_values("row_id").reset_index(drop=True)
        if args.model == "descriptive":
            run_descriptive(data, run)
        else:
            run_additive(data, config, run)
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


if __name__ == "__main__":
    main()
