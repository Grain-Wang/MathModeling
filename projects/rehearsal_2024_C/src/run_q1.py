"""Run the approved Q1 shape-only multinomial logistic Baseline."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from s3_common import (
    CLASS_ENCODING,
    DEFAULT_CONFIG,
    S3_RESULTS_ROOT,
    SHAPE_FEATURES,
    WAVEFORM_LABELS,
    ExperimentRun,
    classification_metrics,
    confusion_frame,
    load_features_and_folds,
    load_frozen_config,
    set_global_seed,
    verify_contract_registry,
    write_csv,
    write_json,
)


EXPERIMENT_ID = "EXP-Q1-BASE-001"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["logistic"], default="logistic")
    parser.add_argument("--stage", choices=["baseline"], default="baseline")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def make_model(c_value: float, class_weight: str | None, max_iter: int, seed: int) -> Pipeline:
    return Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    C=c_value,
                    class_weight=class_weight,
                    max_iter=max_iter,
                    solver="lbfgs",
                    random_state=seed,
                ),
            ),
        ]
    )


def select_parameters(
    x: pd.DataFrame,
    y: np.ndarray,
    groups: np.ndarray,
    candidates: list[tuple[float, str | None]],
    max_iter: int,
    seed: int,
) -> tuple[tuple[float, str | None], list[dict[str, object]]]:
    splitter = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=seed)
    rows: list[dict[str, object]] = []
    for c_value, class_weight in candidates:
        scores: list[float] = []
        for inner_fold, (train_index, valid_index) in enumerate(splitter.split(x, y, groups)):
            if set(groups[train_index]).intersection(groups[valid_index]):
                raise AssertionError("Q1 inner group leakage")
            model = make_model(c_value, class_weight, max_iter, seed)
            model.fit(x.iloc[train_index], y[train_index])
            prediction = model.predict(x.iloc[valid_index])
            score = classification_metrics(y[valid_index], prediction)["macro_f1"]
            scores.append(float(score))
            rows.append(
                {
                    "C": c_value,
                    "class_weight": "None" if class_weight is None else class_weight,
                    "inner_fold": inner_fold,
                    "macro_f1": score,
                }
            )
        rows.append(
            {
                "C": c_value,
                "class_weight": "None" if class_weight is None else class_weight,
                "inner_fold": "mean",
                "macro_f1": float(np.mean(scores)),
            }
        )
    means = [row for row in rows if row["inner_fold"] == "mean"]
    means.sort(key=lambda row: (-float(row["macro_f1"]), float(row["C"]), row["class_weight"] != "None"))
    best = means[0]
    return (float(best["C"]), None if best["class_weight"] == "None" else str(best["class_weight"])), rows


def subgroup_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for field in ("material", "temperature_C"):
        for value, subset in frame.groupby(field, observed=True):
            metrics = classification_metrics(subset["actual_label"], subset["predicted_label"])
            rows.append({"group_field": field, "group_value": value, **{key: metrics[key] for key in ("n", "accuracy", "balanced_accuracy", "macro_f1")}})
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    run = ExperimentRun(EXPERIMENT_ID, config_path)
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
        if data[SHAPE_FEATURES].isna().any().any():
            raise ValueError("Q1 shape features contain missing values")

        x = data[SHAPE_FEATURES]
        y = data["waveform"].to_numpy(dtype=object)
        groups = data["near_shape_group"].to_numpy(dtype=object)
        folds = data["q1_outer_fold"].to_numpy(dtype=int)
        outer_fold_values = sorted(np.unique(folds))
        if len(outer_fold_values) < 3:
            raise ValueError("Q1 requires at least three outer folds")

        logistic_grid = config["models"]["q1"]["search_space"]["logistic"]
        candidates = list(itertools.product(map(float, logistic_grid["C"]), logistic_grid["class_weight"]))
        max_iter = int(logistic_grid["max_iter"])
        probabilities = np.full((len(data), len(WAVEFORM_LABELS)), np.nan, dtype=np.float64)
        predictions = np.empty(len(data), dtype=object)
        majority_predictions = np.empty(len(data), dtype=object)
        parameter_rows: list[dict[str, object]] = []
        lineage_rows: list[dict[str, object]] = []
        fold_models: dict[str, Pipeline] = {}
        selected_parameters: list[tuple[float, str | None]] = []

        for outer_fold in outer_fold_values:
            train_index = np.flatnonzero(folds != outer_fold)
            valid_index = np.flatnonzero(folds == outer_fold)
            overlap = set(groups[train_index]).intersection(groups[valid_index])
            if overlap:
                raise AssertionError(f"Q1 outer group leakage in fold {outer_fold}")
            best, inner_rows = select_parameters(
                x.iloc[train_index].reset_index(drop=True),
                y[train_index],
                groups[train_index],
                candidates,
                max_iter,
                seed + int(outer_fold),
            )
            for row in inner_rows:
                parameter_rows.append({"outer_fold": int(outer_fold), **row})
            model = make_model(best[0], best[1], max_iter, seed)
            model.fit(x.iloc[train_index], y[train_index])
            fold_probability = model.predict_proba(x.iloc[valid_index])
            class_positions = {label: position for position, label in enumerate(model.classes_)}
            for output_position, label in enumerate(WAVEFORM_LABELS):
                probabilities[valid_index, output_position] = fold_probability[:, class_positions[label]]
            predictions[valid_index] = model.predict(x.iloc[valid_index])
            majority_label = Counter(y[train_index]).most_common(1)[0][0]
            majority_predictions[valid_index] = majority_label
            model_id = f"q1-logistic-fold-{int(outer_fold)}"
            fold_models[model_id] = model
            selected_parameters.append(best)
            lineage_rows.append(
                {
                    "outer_fold": int(outer_fold),
                    "train_n": int(train_index.size),
                    "validation_n": int(valid_index.size),
                    "train_group_count": len(set(groups[train_index])),
                    "validation_group_count": len(set(groups[valid_index])),
                    "group_overlap_count": len(overlap),
                    "selected_C": best[0],
                    "selected_class_weight": "None" if best[1] is None else best[1],
                }
            )
            run.log(f"outer_fold={outer_fold} selected_C={best[0]} class_weight={best[1]} validation_n={valid_index.size}")

        if pd.isna(predictions).any() or not np.isfinite(probabilities).all():
            raise AssertionError("Q1 OOF predictions are incomplete or non-finite")
        if not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-8):
            raise AssertionError("Q1 OOF probabilities do not sum to one")

        selected_counter = Counter(selected_parameters)
        full_parameters = sorted(selected_counter, key=lambda item: (-selected_counter[item], item[0], item[1] is not None))[0]
        full_model = make_model(full_parameters[0], full_parameters[1], max_iter, seed)
        full_model.fit(x, y)

        output_dir = S3_RESULTS_ROOT / "q1"
        oof_path = output_dir / "baseline_oof_predictions.csv"
        metrics_path = output_dir / "baseline_metrics.json"
        confusion_path = output_dir / "confusion_matrix.csv"
        subgroup_path = output_dir / "subgroup_metrics.csv"
        parameter_path = output_dir / "inner_selection.csv"
        lineage_path = output_dir / "oof_lineage.csv"
        fold_models_path = output_dir / "logistic_fold_models.joblib"
        full_model_path = output_dir / "logistic_full_model.joblib"
        evidence_metrics_path = run.output_dir / "metrics.json"

        oof = data[["row_id", "material", "temperature_C", "frequency_Hz", "b_m_T", "near_shape_group", "q1_outer_fold"]].copy()
        oof["actual_label"] = y
        oof["actual_code"] = [CLASS_ENCODING[value] for value in y]
        oof["predicted_label"] = predictions
        oof["predicted_code"] = [CLASS_ENCODING[str(value)] for value in predictions]
        for position, label in enumerate(WAVEFORM_LABELS):
            oof[f"probability_{CLASS_ENCODING[label]}_{label}"] = probabilities[:, position]
        write_csv(oof_path, oof)
        write_csv(confusion_path, confusion_frame(y, predictions))
        write_csv(subgroup_path, subgroup_metrics(oof))
        write_csv(parameter_path, pd.DataFrame(parameter_rows))
        write_csv(lineage_path, pd.DataFrame(lineage_rows))
        fold_models_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(fold_models, fold_models_path, compress=3)
        joblib.dump(full_model, full_model_path, compress=3)

        metrics = {
            "status": "PASS",
            "model": "shape-only multinomial logistic regression",
            "features": SHAPE_FEATURES,
            "outer_folds": len(outer_fold_values),
            "oof": classification_metrics(y, predictions),
            "majority_oof": classification_metrics(y, majority_predictions),
            "full_fit_parameters_from_outer_mode": {
                "C": full_parameters[0],
                "class_weight": full_parameters[1],
            },
            "class_encoding": CLASS_ENCODING,
            "failure_flags": {
                "minimum_class_recall_below_0_90": min(
                    value["recall"] for value in classification_metrics(y, predictions)["per_class"].values()
                )
                < 0.90,
                "group_leakage": any(row["group_overlap_count"] != 0 for row in lineage_rows),
            },
        }
        write_json(metrics_path, metrics)
        write_json(evidence_metrics_path, metrics)
        for path in (
            oof_path,
            metrics_path,
            confusion_path,
            subgroup_path,
            parameter_path,
            lineage_path,
            fold_models_path,
            full_model_path,
            evidence_metrics_path,
        ):
            run.record_output(path)
        run.log(json.dumps(metrics["oof"], ensure_ascii=False, sort_keys=True))
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


if __name__ == "__main__":
    main()
