"""Run the bounded S4 Q4 HGB comparison, ablation, and stress checks."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, ParameterSampler

from run_q4 import group_hash, q4_subgroup_metrics
from s3_common import (
    DEFAULT_CONFIG,
    PROJECT_ROOT,
    Q4_NUMERIC_FEATURES,
    S3_RESULTS_ROOT,
    SHAPE_FEATURES,
    load_features_and_folds,
    load_frozen_config,
    regression_metrics,
    set_global_seed,
    sha256_file,
    verify_contract_registry,
    write_csv,
    write_json,
)
from s4_common import (
    S4_RESULTS_ROOT,
    add_temperature_label,
    compare_subgroups,
    fit_log_model,
    modal_parameters,
    parameter_key,
    predict_log_model,
    relative_improvement,
    s4_run,
)

EXPERIMENT_IDS = {
    "main": "EXP-Q4-MAIN-001",
    "ablation": "EXP-Q4-ABL-001",
    "stress": "EXP-Q4-STRESS-001",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=sorted(EXPERIMENT_IDS), required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def q4_data() -> pd.DataFrame:
    _, _, data = load_features_and_folds()
    return add_temperature_label(data.sort_values("row_id").reset_index(drop=True))


def hgb_candidates(config: dict[str, Any]) -> list[dict[str, Any]]:
    settings = config["models"]["q4"]["search_space"]["hist_gradient_boosting"]
    search = {
        "learning_rate": [float(value) for value in settings["learning_rate"]],
        "max_leaf_nodes": [int(value) for value in settings["max_leaf_nodes"]],
        "min_samples_leaf": [int(value) for value in settings["min_samples_leaf"]],
        "l2_regularization": [float(value) for value in settings["l2_regularization"]],
    }
    sampled = list(
        ParameterSampler(
            search,
            n_iter=int(settings["n_iter"]),
            random_state=int(settings["random_state"]),
        )
    )
    result: list[dict[str, Any]] = []
    for candidate in sampled:
        result.append(
            {
                **candidate,
                "max_iter": int(settings["max_iter"]),
                "random_state": int(settings["random_state"]),
            }
        )
    if len(result) != int(config["models"]["q4"]["max_main_candidates"]):
        raise AssertionError("Q4 HGB candidate count differs from frozen maximum")
    return result


def select_hgb(
    train: pd.DataFrame,
    candidates: list[dict[str, Any]],
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    groups = train["condition_group"].to_numpy(dtype=object)
    splitter = GroupKFold(n_splits=3, shuffle=True, random_state=seed)
    splits = list(splitter.split(train, groups=groups))
    rows: list[dict[str, Any]] = []
    means: list[tuple[float, str, dict[str, Any]]] = []
    for candidate_index, parameters in enumerate(candidates):
        scores: list[float] = []
        for inner_fold, (fit_index, valid_index) in enumerate(splits):
            if set(groups[fit_index]).intersection(groups[valid_index]):
                raise AssertionError("Q4 HGB inner group leakage")
            model, smear = fit_log_model("hgb", parameters, train.iloc[fit_index])
            _, prediction = predict_log_model(model, smear, train.iloc[valid_index])
            score = float(regression_metrics(train.iloc[valid_index]["core_loss_W_per_m3"], prediction)["rmsle"])
            scores.append(score)
            rows.append(
                {
                    "candidate_index": candidate_index,
                    "parameters_json": parameter_key(parameters),
                    "inner_fold": inner_fold,
                    "rmsle": score,
                }
            )
        mean_score = float(np.mean(scores))
        rows.append(
            {
                "candidate_index": candidate_index,
                "parameters_json": parameter_key(parameters),
                "inner_fold": "mean",
                "rmsle": mean_score,
            }
        )
        means.append((mean_score, parameter_key(parameters), parameters))
    means.sort(key=lambda item: (item[0], item[1]))
    return dict(means[0][2]), rows


def run_main(config_path: Path) -> None:
    run = s4_run(EXPERIMENT_IDS["main"], config_path, "main")
    try:
        config = load_frozen_config(config_path)
        run.record_contract_hashes(verify_contract_registry(config))
        seed = int(config["seeds"]["global"])
        set_global_seed(seed)
        required = (
            Path(__file__).resolve(),
            Path(__file__).with_name("s3_common.py").resolve(),
            Path(__file__).with_name("s4_common.py").resolve(),
            Path(__file__).with_name("run_q4.py").resolve(),
            S3_RESULTS_ROOT / "data" / "feature_table.csv",
            S3_RESULTS_ROOT / "data" / "feature_schema.json",
            S3_RESULTS_ROOT / "folds" / "fold_assignments.csv",
            S3_RESULTS_ROOT / "q4" / "ridge_oof_predictions.csv",
            S3_RESULTS_ROOT / "q4" / "ridge_metrics.json",
            S3_RESULTS_ROOT / "q4" / "ridge_subgroup_metrics.csv",
        )
        for path in required:
            run.record_input(path)
        data = q4_data()
        y = data["core_loss_W_per_m3"].to_numpy(dtype=np.float64)
        folds = data["regression_outer_fold"].to_numpy(dtype=int)
        groups = data["condition_group"].to_numpy(dtype=object)
        candidates = hgb_candidates(config)
        prediction = np.full(len(data), np.nan, dtype=np.float64)
        prediction_log = np.full(len(data), np.nan, dtype=np.float64)
        model_ids = np.empty(len(data), dtype=object)
        selection_rows: list[dict[str, Any]] = []
        lineage_rows: list[dict[str, Any]] = []
        selected_parameters: list[dict[str, Any]] = []
        fold_models: dict[str, Any] = {}
        for fold in sorted(np.unique(folds)):
            train_index = np.flatnonzero(folds != fold)
            valid_index = np.flatnonzero(folds == fold)
            overlap = set(groups[train_index]).intersection(groups[valid_index])
            if overlap:
                raise AssertionError(f"Q4 HGB outer group leakage in fold {fold}")
            train = data.iloc[train_index].reset_index(drop=True)
            parameters, inner_rows = select_hgb(train, candidates, seed + int(fold))
            for row in inner_rows:
                selection_rows.append({"outer_fold": int(fold), **row})
            model, smear = fit_log_model("hgb", parameters, data.iloc[train_index])
            fold_log, fold_prediction = predict_log_model(model, smear, data.iloc[valid_index])
            prediction_log[valid_index] = fold_log
            prediction[valid_index] = fold_prediction
            model_id = f"q4-hgb-fold-{int(fold)}"
            model_ids[valid_index] = model_id
            selected_parameters.append(parameters)
            fold_models[model_id] = {
                "model": model,
                "smearing_factor": smear,
                "validation_fold": int(fold),
                "parameters": parameters,
            }
            lineage_rows.append(
                {
                    "outer_fold": int(fold),
                    "model_id": model_id,
                    "selected_parameters_json": parameter_key(parameters),
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
            run.log(f"outer_fold={fold} selected={parameter_key(parameters)} validation_n={len(valid_index)}")
        if not np.isfinite(prediction).all() or pd.isna(model_ids).any():
            raise AssertionError("Q4 HGB OOF coverage incomplete")
        full_parameters = modal_parameters(selected_parameters)
        full_model, full_smear = fit_log_model("hgb", full_parameters, data)
        full_prediction_log, full_prediction = predict_log_model(full_model, full_smear, data)

        baseline_oof = pd.read_csv(S3_RESULTS_ROOT / "q4" / "ridge_oof_predictions.csv").sort_values("row_id").reset_index(drop=True)
        if list(data["row_id"]) != list(baseline_oof["row_id"]):
            raise ValueError("Q4 HGB/Ridge OOF identity mismatch")
        baseline_metrics = json.loads((S3_RESULTS_ROOT / "q4" / "ridge_metrics.json").read_text(encoding="utf-8"))
        minimum_n = int(config["validation_contract"]["q4_major_subgroup_min_n"])
        minimum_folds = int(config["validation_contract"]["q4_major_subgroup_min_outer_folds"])
        candidate_subgroups = q4_subgroup_metrics(data, prediction, minimum_n, minimum_folds)
        baseline_subgroups = pd.read_csv(S3_RESULTS_ROOT / "q4" / "ridge_subgroup_metrics.csv")
        comparison = compare_subgroups(baseline_subgroups, candidate_subgroups)
        major = comparison[comparison["is_major_subgroup_ridge"].astype(bool) & comparison["is_major_subgroup_candidate"].astype(bool)]
        max_degradation = float(major["rmsle_relative_change"].max())
        candidate_metrics = regression_metrics(y, prediction)
        baseline_rmsle = float(baseline_metrics["oof"]["rmsle"])
        improvement = relative_improvement(baseline_rmsle, float(candidate_metrics["rmsle"]))
        required_improvement = float(config["models"]["q4"]["min_relative_rmsle_improvement"])
        allowed_degradation = float(config["models"]["q4"]["max_subgroup_rmsle_degradation"])
        adopted = improvement >= required_improvement and max_degradation <= allowed_degradation
        low_bm = comparison[comparison["group_field"] == "b_m_quartile"].sort_values("rmsle_ridge", ascending=False).iloc[0]

        output_dir = S4_RESULTS_ROOT / "q4"
        oof_path = output_dir / "hgb_oof_predictions.csv"
        full_path = output_dir / "hgb_full_fit_training_predictions.csv"
        selection_path = output_dir / "hgb_inner_selection.csv"
        lineage_path = output_dir / "hgb_oof_lineage.csv"
        subgroup_path = output_dir / "hgb_subgroup_metrics.csv"
        comparison_path = output_dir / "hgb_vs_ridge_subgroup_comparison.csv"
        fold_models_path = output_dir / "hgb_fold_models.joblib"
        full_model_path = output_dir / "hgb_full_model.joblib"
        metrics_path = output_dir / "hgb_metrics.json"
        winner_path = output_dir / "winner.json"
        evidence_path = run.output_dir / "metrics.json"
        oof = data[["row_id", "material", "waveform", "temperature_C", "frequency_Hz", "b_m_T", "b_half_pp_T", "condition_group", "regression_outer_fold", "core_loss_W_per_m3"]].copy()
        oof["oof_model_id"] = model_ids
        oof["y_pred_log_oof"] = prediction_log
        oof["y_pred_oof"] = prediction
        oof["ridge_y_pred_oof"] = baseline_oof["y_pred_oof"].to_numpy(dtype=np.float64)
        oof["absolute_log_error"] = np.abs(np.log1p(y) - np.log1p(prediction))
        full = data[["row_id", "condition_group", "regression_outer_fold"]].copy()
        full["full_model_id"] = "q4-hgb-full"
        full["y_pred_log_full"] = full_prediction_log
        full["y_pred_full"] = full_prediction
        write_csv(oof_path, oof)
        write_csv(full_path, full)
        write_csv(selection_path, pd.DataFrame(selection_rows))
        write_csv(lineage_path, pd.DataFrame(lineage_rows))
        write_csv(subgroup_path, candidate_subgroups)
        write_csv(comparison_path, comparison)
        fold_models_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(fold_models, fold_models_path, compress=3)
        joblib.dump({"model": full_model, "smearing_factor": full_smear, "parameters": full_parameters}, full_model_path, compress=3)
        metrics = {
            "status": "PASS",
            "model": "nested grouped HistGradientBoostingRegressor on log loss",
            "candidate_count": len(candidates),
            "outer_folds": len(np.unique(folds)),
            "inner_folds": 3,
            "candidate_oof": candidate_metrics,
            "ridge_oof": baseline_metrics["oof"],
            "relative_rmsle_improvement": improvement,
            "minimum_required_relative_improvement": required_improvement,
            "maximum_major_subgroup_rmsle_degradation": max_degradation,
            "maximum_allowed_major_subgroup_degradation": allowed_degradation,
            "low_b_m_focus": {
                "group_value": str(low_bm["group_value"]),
                "ridge_rmsle": float(low_bm["rmsle_ridge"]),
                "hgb_rmsle": float(low_bm["rmsle_candidate"]),
                "relative_change": float(low_bm["rmsle_relative_change"]),
            },
            "adopted": bool(adopted),
            "winner": "hgb" if adopted else "ridge",
            "random_forest_triggered": bool(not adopted),
            "full_fit_parameters_from_outer_mode": full_parameters,
            "fold_models_sha256": sha256_file(fold_models_path),
            "full_model_sha256": sha256_file(full_model_path),
            "failure_flags": {
                "group_leakage": any(row["group_overlap_count"] != 0 for row in lineage_rows),
                "improvement_below_2_percent": improvement < required_improvement,
                "major_subgroup_degradation_above_10_percent": max_degradation > allowed_degradation,
            },
        }
        winner = {
            "winner": metrics["winner"],
            "decision_rule_pass": bool(adopted),
            "oof_predictions": "results/raw/main/q4/hgb_oof_predictions.csv" if adopted else "results/raw/s3/q4/ridge_oof_predictions.csv",
            "full_predictions": "results/raw/main/q4/hgb_full_fit_training_predictions.csv" if adopted else "results/raw/s3/q4/ridge_full_fit_training_predictions.csv",
            "fold_models": "results/raw/main/q4/hgb_fold_models.joblib" if adopted else "results/raw/s3/q4/ridge_fold_models.joblib",
            "full_model": "results/raw/main/q4/hgb_full_model.joblib" if adopted else "results/raw/s3/q4/ridge_full_model.joblib",
        }
        write_json(metrics_path, metrics)
        write_json(winner_path, winner)
        write_json(evidence_path, metrics)
        for path in (
            oof_path, full_path, selection_path, lineage_path, subgroup_path, comparison_path,
            fold_models_path, full_model_path, metrics_path, winner_path, evidence_path,
        ):
            run.record_output(path)
        run.log(json.dumps({"candidate_oof": candidate_metrics, "winner": metrics["winner"], "max_subgroup_degradation": max_degradation}, ensure_ascii=False, sort_keys=True))
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


def preliminary_winner_spec() -> tuple[str, dict[int, dict[str, Any]], dict[str, Any]]:
    metrics = json.loads((S4_RESULTS_ROOT / "q4" / "hgb_metrics.json").read_text(encoding="utf-8"))
    if metrics["winner"] == "hgb":
        lineage = pd.read_csv(S4_RESULTS_ROOT / "q4" / "hgb_oof_lineage.csv")
        by_fold = {int(row["outer_fold"]): json.loads(row["selected_parameters_json"]) for _, row in lineage.iterrows()}
        return "hgb", by_fold, dict(metrics["full_fit_parameters_from_outer_mode"])
    lineage = pd.read_csv(S3_RESULTS_ROOT / "q4" / "ridge_oof_lineage.csv")
    by_fold = {int(row["outer_fold"]): {"alpha": float(row["selected_alpha"])} for _, row in lineage.iterrows()}
    base = json.loads((S3_RESULTS_ROOT / "q4" / "ridge_metrics.json").read_text(encoding="utf-8"))
    return "ridge", by_fold, {"alpha": float(base["full_fit_alpha_from_outer_mode"])}


def cross_fit_fixed(
    data: pd.DataFrame,
    model_kind: str,
    parameters_by_fold: dict[int, dict[str, Any]],
    numeric_features: list[str],
    model_label: str,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]], dict[str, Any]]:
    folds = data["regression_outer_fold"].to_numpy(dtype=int)
    groups = data["condition_group"].to_numpy(dtype=object)
    prediction = np.full(len(data), np.nan, dtype=np.float64)
    prediction_log = np.full(len(data), np.nan, dtype=np.float64)
    lineage: list[dict[str, Any]] = []
    fold_models: dict[str, Any] = {}
    for fold in sorted(np.unique(folds)):
        train_index = np.flatnonzero(folds != fold)
        valid_index = np.flatnonzero(folds == fold)
        overlap = set(groups[train_index]).intersection(groups[valid_index])
        if overlap:
            raise AssertionError("Q4 fixed-fit group leakage")
        parameters = parameters_by_fold[int(fold)]
        model, smear = fit_log_model(model_kind, parameters, data.iloc[train_index], numeric_features)
        fold_log, fold_prediction = predict_log_model(model, smear, data.iloc[valid_index], numeric_features)
        prediction_log[valid_index] = fold_log
        prediction[valid_index] = fold_prediction
        model_id = f"q4-{model_kind}-{model_label}-fold-{int(fold)}"
        fold_models[model_id] = {
            "model": model,
            "smearing_factor": smear,
            "validation_fold": int(fold),
            "parameters": parameters,
            "numeric_features": numeric_features,
        }
        lineage.append(
            {
                "outer_fold": int(fold),
                "model_id": model_id,
                "group_overlap_count": len(overlap),
                "selected_parameters_json": parameter_key(parameters),
                "train_groups_sha256": group_hash(groups[train_index]),
                "validation_groups_sha256": group_hash(groups[valid_index]),
            }
        )
    if not np.isfinite(prediction).all():
        raise AssertionError("Q4 fixed-fit OOF coverage incomplete")
    return prediction_log, prediction, lineage, fold_models


def run_ablation(config_path: Path) -> None:
    run = s4_run(EXPERIMENT_IDS["ablation"], config_path, "ablation")
    try:
        config = load_frozen_config(config_path)
        run.record_contract_hashes(verify_contract_registry(config))
        set_global_seed(int(config["seeds"]["global"]))
        for path in (
            Path(__file__).resolve(), Path(__file__).with_name("s3_common.py").resolve(), Path(__file__).with_name("s4_common.py").resolve(),
            S3_RESULTS_ROOT / "data" / "feature_table.csv", S3_RESULTS_ROOT / "folds" / "fold_assignments.csv",
            S4_RESULTS_ROOT / "q4" / "hgb_metrics.json", S4_RESULTS_ROOT / "q4" / "winner.json",
        ):
            run.record_input(path)
        data = q4_data()
        model_kind, parameters_by_fold, full_parameters = preliminary_winner_spec()
        amplitude_features = [feature for feature in Q4_NUMERIC_FEATURES if feature not in SHAPE_FEATURES]
        variants = {
            "condition_only": ["log_frequency_Hz", "log_b_m_T"],
            "amplitude_and_condition": amplitude_features,
            "full_wave_v1": list(Q4_NUMERIC_FEATURES),
        }
        metric_rows: list[dict[str, Any]] = []
        prediction_table = data[["row_id", "regression_outer_fold", "core_loss_W_per_m3"]].copy()
        variant_outputs: dict[str, tuple[np.ndarray, np.ndarray, list[dict[str, Any]], dict[str, Any]]] = {}
        for variant, features in variants.items():
            output = cross_fit_fixed(data, model_kind, parameters_by_fold, features, variant)
            variant_outputs[variant] = output
            _, prediction, lineage, _ = output
            result = regression_metrics(data["core_loss_W_per_m3"], prediction)
            metric_rows.append({"variant": variant, "numeric_feature_count": len(features), **result})
            prediction_table[f"y_pred_{variant}"] = prediction
            if any(row["group_overlap_count"] != 0 for row in lineage):
                raise AssertionError("Q4 ablation lineage contains leakage")
            run.log(f"variant={variant} rmsle={result['rmsle']}")
        full_rmsle = float(next(row["rmsle"] for row in metric_rows if row["variant"] == "full_wave_v1"))
        for row in metric_rows:
            row["relative_rmsle_change_vs_full"] = (float(row["rmsle"]) - full_rmsle) / full_rmsle
        selected = sorted(metric_rows, key=lambda row: (float(row["rmsle"]), int(row["numeric_feature_count"]), str(row["variant"])))[0]
        selected_variant = str(selected["variant"])
        selected_features = variants[selected_variant]
        selected_log, selected_prediction, selected_lineage, selected_models = variant_outputs[selected_variant]
        full_model, full_smear = fit_log_model(model_kind, full_parameters, data, selected_features)
        full_log, full_prediction = predict_log_model(full_model, full_smear, data, selected_features)

        output_dir = S4_RESULTS_ROOT / "q4"
        table_path = output_dir / "ablation_metrics.csv"
        prediction_path = output_dir / "ablation_oof_predictions.csv"
        lineage_path = output_dir / "final_oof_lineage.csv"
        selected_oof_path = output_dir / "final_oof_predictions.csv"
        selected_full_path = output_dir / "final_full_fit_training_predictions.csv"
        fold_models_path = output_dir / "final_fold_models.joblib"
        full_model_path = output_dir / "final_full_model.joblib"
        final_winner_path = output_dir / "final_winner.json"
        metrics_path = output_dir / "ablation_metrics.json"
        evidence_path = run.output_dir / "metrics.json"
        write_csv(table_path, pd.DataFrame(metric_rows))
        write_csv(prediction_path, prediction_table)
        write_csv(lineage_path, pd.DataFrame(selected_lineage))
        selected_oof = data[["row_id", "material", "waveform", "temperature_C", "frequency_Hz", "b_m_T", "b_half_pp_T", "condition_group", "regression_outer_fold", "core_loss_W_per_m3"]].copy()
        selected_oof["oof_model_id"] = np.empty(len(data), dtype=object)
        for row in selected_lineage:
            selected_oof.loc[selected_oof["regression_outer_fold"] == row["outer_fold"], "oof_model_id"] = row["model_id"]
        selected_oof["y_pred_log_oof"] = selected_log
        selected_oof["y_pred_oof"] = selected_prediction
        selected_oof["absolute_log_error"] = np.abs(np.log1p(selected_oof["core_loss_W_per_m3"]) - np.log1p(selected_prediction))
        full = data[["row_id", "condition_group", "regression_outer_fold"]].copy()
        full["full_model_id"] = f"q4-{model_kind}-{selected_variant}-full"
        full["y_pred_log_full"] = full_log
        full["y_pred_full"] = full_prediction
        write_csv(selected_oof_path, selected_oof)
        write_csv(selected_full_path, full)
        fold_models_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(selected_models, fold_models_path, compress=3)
        joblib.dump({"model": full_model, "smearing_factor": full_smear, "parameters": full_parameters, "numeric_features": selected_features}, full_model_path, compress=3)
        final_winner = {
            "winner": model_kind,
            "feature_variant": selected_variant,
            "numeric_features": selected_features,
            "selection_rule": "lowest predefined ablation OOF RMSLE; ties prefer fewer numeric features",
            "selection_reused_without_retuning": True,
            "oof_rmsle": float(selected["rmsle"]),
            "oof_predictions": "results/raw/main/q4/final_oof_predictions.csv",
            "full_predictions": "results/raw/main/q4/final_full_fit_training_predictions.csv",
            "lineage": "results/raw/main/q4/final_oof_lineage.csv",
            "fold_models": "results/raw/main/q4/final_fold_models.joblib",
            "full_model": "results/raw/main/q4/final_full_model.joblib",
            "full_fit_parameters": full_parameters,
        }
        metrics = {
            "status": "PASS",
            "winner_model": model_kind,
            "selection_reused_without_retuning": True,
            "variants": metric_rows,
            "selected_feature_variant": selected_variant,
            "selected_numeric_feature_count": len(selected_features),
            "selected_oof_rmsle": float(selected["rmsle"]),
            "full_wave_features_retained": selected_variant == "full_wave_v1",
            "shape_features_removed": selected_variant != "full_wave_v1",
            "group_leakage": False,
            "final_fold_models_sha256": sha256_file(fold_models_path),
            "final_full_model_sha256": sha256_file(full_model_path),
        }
        write_json(metrics_path, metrics)
        write_json(final_winner_path, final_winner)
        write_json(evidence_path, metrics)
        for path in (
            table_path, prediction_path, lineage_path, selected_oof_path, selected_full_path,
            fold_models_path, full_model_path, final_winner_path, metrics_path, evidence_path,
        ):
            run.record_output(path)
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise

def run_stress(config_path: Path) -> None:
    run = s4_run(EXPERIMENT_IDS["stress"], config_path, "sensitivity")
    try:
        config = load_frozen_config(config_path)
        run.record_contract_hashes(verify_contract_registry(config))
        set_global_seed(int(config["seeds"]["global"]))
        for path in (
            Path(__file__).resolve(), Path(__file__).with_name("s3_common.py").resolve(), Path(__file__).with_name("s4_common.py").resolve(),
            S3_RESULTS_ROOT / "data" / "feature_table.csv", S3_RESULTS_ROOT / "folds" / "fold_assignments.csv",
            S4_RESULTS_ROOT / "q4" / "hgb_metrics.json", S4_RESULTS_ROOT / "q4" / "winner.json",
            S4_RESULTS_ROOT / "q4" / "ablation_metrics.json", S4_RESULTS_ROOT / "q4" / "final_winner.json",
        ):
            run.record_input(path)
        data = q4_data()
        winner = json.loads((S4_RESULTS_ROOT / "q4" / "final_winner.json").read_text(encoding="utf-8"))
        model_kind = str(winner["winner"])
        full_parameters = dict(winner["full_fit_parameters"])
        numeric_features = list(winner["numeric_features"])
        winner_oof_path = PROJECT_ROOT / winner["oof_predictions"]
        run.record_input(winner_oof_path)
        winner_oof = pd.read_csv(winner_oof_path).sort_values("row_id").reset_index(drop=True)
        if list(data["row_id"]) != list(winner_oof["row_id"]):
            raise ValueError("Q4 winner OOF identity mismatch")
        prediction = winner_oof["y_pred_oof"].to_numpy(dtype=np.float64)
        scopes: list[dict[str, Any]] = []
        b_edges = np.quantile(data["b_m_T"], [0.25, 0.75])
        f_edges = np.quantile(data["frequency_Hz"], [0.1, 0.9])
        loss_edge = np.quantile(data["core_loss_W_per_m3"], 0.9)
        masks = {
            "low_b_m_quartile": data["b_m_T"].to_numpy() <= b_edges[0],
            "high_b_m_quartile": data["b_m_T"].to_numpy() >= b_edges[1],
            "frequency_lower_tail_10pct": data["frequency_Hz"].to_numpy() <= f_edges[0],
            "frequency_upper_tail_10pct": data["frequency_Hz"].to_numpy() >= f_edges[1],
            "loss_upper_tail_10pct": data["core_loss_W_per_m3"].to_numpy() >= loss_edge,
            "frequency_outside_nominal_50k_500k": ~data["frequency_Hz"].between(50000, 500000, inclusive="both").to_numpy(),
        }
        for scope, mask in masks.items():
            if int(np.sum(mask)):
                scopes.append({"scope": scope, **regression_metrics(data.loc[mask, "core_loss_W_per_m3"], prediction[mask])})
        holdout_rows: list[dict[str, Any]] = []
        for field in ("material", "temperature_C"):
            for value in sorted(data[field].unique(), key=str):
                train = data[data[field] != value]
                valid = data[data[field] == value]
                model, smear = fit_log_model(model_kind, full_parameters, train, numeric_features)
                _, heldout_prediction = predict_log_model(model, smear, valid, numeric_features)
                holdout_rows.append({"heldout_field": field, "heldout_value": value, **regression_metrics(valid["core_loss_W_per_m3"], heldout_prediction)})
        output_dir = S4_RESULTS_ROOT / "q4"
        scope_path = output_dir / "stress_subset_metrics.csv"
        holdout_path = output_dir / "leave_one_level_out_metrics.csv"
        metrics_path = output_dir / "stress_metrics.json"
        evidence_path = run.output_dir / "metrics.json"
        write_csv(scope_path, pd.DataFrame(scopes))
        write_csv(holdout_path, pd.DataFrame(holdout_rows))
        metrics = {
            "status": "PASS",
            "winner_model": model_kind,
            "feature_variant": winner["feature_variant"],
            "overall_oof": regression_metrics(data["core_loss_W_per_m3"], prediction),
            "low_b_m_quartile": next(row for row in scopes if row["scope"] == "low_b_m_quartile"),
            "maximum_leave_one_material_rmsle": max(float(row["rmsle"]) for row in holdout_rows if row["heldout_field"] == "material"),
            "maximum_leave_one_temperature_rmsle": max(float(row["rmsle"]) for row in holdout_rows if row["heldout_field"] == "temperature_C"),
            "interpretation": "Leave-one-level results are extrapolation stress tests, not the primary OOF estimate.",
        }
        write_json(metrics_path, metrics)
        write_json(evidence_path, metrics)
        for path in (scope_path, holdout_path, metrics_path, evidence_path):
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
    elif args.mode == "ablation":
        run_ablation(config_path)
    else:
        run_stress(config_path)


if __name__ == "__main__":
    main()