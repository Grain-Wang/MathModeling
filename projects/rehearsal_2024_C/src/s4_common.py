"""Shared helpers for the approved, bounded S4 experiments."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from s3_common import (
    MATERIAL_LABELS,
    PROJECT_ROOT,
    Q4_CATEGORICAL_FEATURES,
    Q4_NUMERIC_FEATURES,
    TEMPERATURES,
    WAVEFORM_LABELS,
    ExperimentRun,
    regression_metrics,
    smearing_factor,
)

S4_RESULTS_ROOT = PROJECT_ROOT / "results" / "raw" / "main"
S4_EVIDENCE_ROOT = S4_RESULTS_ROOT / "runs"
S4_DESCRIPTOR_ROOT = PROJECT_ROOT / "experiments"


def s4_run(experiment_id: str, config_path: Path, category: str) -> ExperimentRun:
    return ExperimentRun(
        experiment_id,
        config_path,
        descriptor_path=S4_DESCRIPTOR_ROOT / category / f"{experiment_id}.json",
        evidence_root=S4_EVIDENCE_ROOT,
        stage="S4",
    )


def add_temperature_label(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy()
    result["temperature_label"] = result["temperature_C"].astype(int).astype(str)
    return result


def q4_transformer(numeric_features: list[str], *, scale_numeric: bool) -> ColumnTransformer:
    categorical_levels = [MATERIAL_LABELS, WAVEFORM_LABELS, [str(value) for value in TEMPERATURES]]
    numeric_transformer: str | StandardScaler = StandardScaler() if scale_numeric else "passthrough"
    return ColumnTransformer(
        [
            ("numeric", numeric_transformer, numeric_features),
            (
                "categorical",
                OneHotEncoder(categories=categorical_levels, handle_unknown="ignore", sparse_output=False),
                Q4_CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


def make_q4_model(model_kind: str, parameters: dict[str, Any], numeric_features: list[str] | None = None) -> Pipeline:
    numeric = list(numeric_features or Q4_NUMERIC_FEATURES)
    if model_kind == "hgb":
        estimator = HistGradientBoostingRegressor(
            learning_rate=float(parameters["learning_rate"]),
            max_leaf_nodes=int(parameters["max_leaf_nodes"]),
            min_samples_leaf=int(parameters["min_samples_leaf"]),
            l2_regularization=float(parameters["l2_regularization"]),
            max_iter=int(parameters["max_iter"]),
            random_state=int(parameters["random_state"]),
            early_stopping=False,
        )
        return Pipeline([("features", q4_transformer(numeric, scale_numeric=False)), ("model", estimator)])
    if model_kind == "ridge":
        estimator = Ridge(alpha=float(parameters["alpha"]))
        return Pipeline([("features", q4_transformer(numeric, scale_numeric=True)), ("model", estimator)])
    raise ValueError(f"Unsupported Q4 model kind: {model_kind}")


def fit_log_model(
    model_kind: str,
    parameters: dict[str, Any],
    train: pd.DataFrame,
    numeric_features: list[str] | None = None,
) -> tuple[Pipeline, float]:
    numeric = list(numeric_features or Q4_NUMERIC_FEATURES)
    features = numeric + Q4_CATEGORICAL_FEATURES
    model = make_q4_model(model_kind, parameters, numeric)
    y_log = np.log(train["core_loss_W_per_m3"].to_numpy(dtype=np.float64))
    model.fit(train[features], y_log)
    smear = smearing_factor(y_log, model.predict(train[features]))
    return model, smear


def predict_log_model(
    model: Pipeline,
    smear: float,
    data: pd.DataFrame,
    numeric_features: list[str] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    numeric = list(numeric_features or Q4_NUMERIC_FEATURES)
    prediction_log = model.predict(data[numeric + Q4_CATEGORICAL_FEATURES])
    prediction = np.maximum(1e-9, np.exp(prediction_log) * smear)
    if not np.isfinite(prediction).all() or np.any(prediction <= 0):
        raise ValueError("Q4 model produced invalid predictions")
    return prediction_log, prediction


def parameter_key(parameters: dict[str, Any]) -> str:
    return json.dumps(parameters, sort_keys=True, separators=(",", ":"))


def modal_parameters(values: Iterable[dict[str, Any]]) -> dict[str, Any]:
    materialized = [dict(value) for value in values]
    counts = Counter(parameter_key(value) for value in materialized)
    best_key = sorted(counts, key=lambda key: (-counts[key], key))[0]
    return json.loads(best_key)


def relative_improvement(baseline: float, candidate: float) -> float:
    if baseline <= 0:
        raise ValueError("Baseline metric must be positive")
    return (baseline - candidate) / baseline


def compare_subgroups(baseline: pd.DataFrame, candidate: pd.DataFrame) -> pd.DataFrame:
    keys = ["group_field", "group_value"]
    left = baseline.copy()
    right = candidate.copy()
    for frame in (left, right):
        frame["group_value"] = frame["group_value"].astype(str)
    merged = left.merge(right, on=keys, suffixes=("_ridge", "_candidate"), validate="one_to_one")
    merged["rmsle_relative_change"] = (
        merged["rmsle_candidate"] - merged["rmsle_ridge"]
    ) / merged["rmsle_ridge"]
    return merged


def metrics_row(scope: str, y_true: np.ndarray, prediction: np.ndarray) -> dict[str, Any]:
    return {"scope": scope, **regression_metrics(y_true, prediction)}