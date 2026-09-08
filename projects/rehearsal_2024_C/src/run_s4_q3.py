"""Run the frozen S4 Q3 pairwise interaction, cluster bootstrap, and sensitivity analyses."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler

from run_q3 import additive_design, make_additive_model
from s3_common import (
    DEFAULT_CONFIG,
    MATERIAL_LABELS,
    S3_RESULTS_ROOT,
    TEMPERATURES,
    WAVEFORM_LABELS,
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
from s4_common import S4_RESULTS_ROOT, modal_parameters, s4_run

EXPERIMENT_IDS = {
    "interaction": "EXP-Q3-INT-001",
    "bootstrap": "EXP-Q3-BOOT-001",
    "sensitivity": "EXP-Q3-SENS-001",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=sorted(EXPERIMENT_IDS), required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def interaction_design(data: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    design, effect_columns = additive_design(data)
    families = {
        "temperature": [column for column in effect_columns if column.startswith("effect_temperature_")],
        "waveform": [column for column in effect_columns if column.startswith("effect_waveform_")],
        "material": [column for column in effect_columns if column.startswith("effect_material_")],
    }
    interaction_columns: list[str] = []
    for first, second in (("temperature", "waveform"), ("temperature", "material"), ("waveform", "material")):
        for first_column in families[first]:
            for second_column in families[second]:
                name = f"interaction_{first_column.removeprefix('effect_')}__{second_column.removeprefix('effect_')}"
                design[name] = design[first_column].to_numpy() * design[second_column].to_numpy()
                interaction_columns.append(name)
    return design, effect_columns, interaction_columns


def make_interaction_model(effect_and_interaction_columns: list[str], alpha: float, knots: int, degree: int) -> Pipeline:
    transformer = ColumnTransformer(
        [
            (
                "operating_splines",
                SplineTransformer(n_knots=knots, degree=degree, include_bias=False),
                ["log_frequency_Hz", "log_b_m_T"],
            ),
            ("effect_and_interactions", "passthrough", effect_and_interaction_columns),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )
    return Pipeline([("features", transformer), ("scale", StandardScaler()), ("model", Ridge(alpha=alpha))])


def model_and_design(data: pd.DataFrame, model_kind: str, alpha: float, knots: int, degree: int) -> tuple[Pipeline, pd.DataFrame]:
    if model_kind == "interaction":
        design, effects, interactions = interaction_design(data)
        return make_interaction_model(effects + interactions, alpha, knots, degree), design
    design, effects = additive_design(data)
    return make_additive_model(effects, alpha, knots, degree), design


def select_alpha(
    train: pd.DataFrame,
    alphas: list[float],
    knots: int,
    degree: int,
    seed: int,
) -> tuple[float, list[dict[str, Any]]]:
    design, effects, interactions = interaction_design(train)
    y = train["core_loss_W_per_m3"].to_numpy(dtype=np.float64)
    y_log = np.log(y)
    groups = train["condition_group"].to_numpy(dtype=object)
    splitter = GroupKFold(n_splits=3, shuffle=True, random_state=seed)
    splits = list(splitter.split(design, groups=groups))
    rows: list[dict[str, Any]] = []
    means: list[tuple[float, float]] = []
    for alpha in alphas:
        scores: list[float] = []
        for inner_fold, (fit_index, valid_index) in enumerate(splits):
            if set(groups[fit_index]).intersection(groups[valid_index]):
                raise AssertionError("Q3 interaction inner group leakage")
            model = make_interaction_model(effects + interactions, alpha, knots, degree)
            model.fit(design.iloc[fit_index], y_log[fit_index])
            smear = smearing_factor(y_log[fit_index], model.predict(design.iloc[fit_index]))
            prediction = np.maximum(1e-9, np.exp(model.predict(design.iloc[valid_index])) * smear)
            score = float(log_rmse(y[valid_index], prediction))
            scores.append(score)
            rows.append({"alpha": alpha, "inner_fold": inner_fold, "log_rmse": score})
        mean_score = float(np.mean(scores))
        rows.append({"alpha": alpha, "inner_fold": "mean", "log_rmse": mean_score})
        means.append((mean_score, -alpha))
    means.sort()
    return float(-means[0][1]), rows


def q3_data() -> pd.DataFrame:
    _, _, data = load_features_and_folds()
    return data.sort_values("row_id").reset_index(drop=True)


def cross_fit(
    data: pd.DataFrame,
    model_kind: str,
    parameters_by_fold: dict[int, float],
    knots: int,
    degree: int,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    folds = data["regression_outer_fold"].to_numpy(dtype=int)
    groups = data["condition_group"].to_numpy(dtype=object)
    y = data["core_loss_W_per_m3"].to_numpy(dtype=np.float64)
    y_log = np.log(y)
    prediction = np.full(len(data), np.nan, dtype=np.float64)
    prediction_log = np.full(len(data), np.nan, dtype=np.float64)
    lineage: list[dict[str, Any]] = []
    for fold in sorted(np.unique(folds)):
        train_index = np.flatnonzero(folds != fold)
        valid_index = np.flatnonzero(folds == fold)
        if set(groups[train_index]).intersection(groups[valid_index]):
            raise AssertionError("Q3 outer group leakage")
        model, design = model_and_design(data, model_kind, parameters_by_fold[int(fold)], knots, degree)
        model.fit(design.iloc[train_index], y_log[train_index])
        smear = smearing_factor(y_log[train_index], model.predict(design.iloc[train_index]))
        predicted_log = model.predict(design.iloc[valid_index])
        predicted = np.maximum(1e-9, np.exp(predicted_log) * smear)
        prediction_log[valid_index] = predicted_log
        prediction[valid_index] = predicted
        lineage.append(
            {
                "outer_fold": int(fold),
                "selected_alpha": parameters_by_fold[int(fold)],
                "train_n": len(train_index),
                "validation_n": len(valid_index),
                "group_overlap_count": 0,
                "smearing_factor": smear,
            }
        )
    if not np.isfinite(prediction).all():
        raise AssertionError("Q3 OOF coverage incomplete")
    return prediction_log, prediction, lineage


def run_interaction(config_path: Path) -> None:
    run = s4_run(EXPERIMENT_IDS["interaction"], config_path, "main")
    try:
        config = load_frozen_config(config_path)
        run.record_contract_hashes(verify_contract_registry(config))
        seed = int(config["seeds"]["global"])
        set_global_seed(seed)
        for path in (
            Path(__file__).resolve(), Path(__file__).with_name("s3_common.py").resolve(), Path(__file__).with_name("s4_common.py").resolve(), Path(__file__).with_name("run_q3.py").resolve(),
            S3_RESULTS_ROOT / "data" / "feature_table.csv", S3_RESULTS_ROOT / "folds" / "fold_assignments.csv",
            S3_RESULTS_ROOT / "q3" / "additive_oof_predictions.csv", S3_RESULTS_ROOT / "q3" / "additive_metrics.json",
        ):
            run.record_input(path)
        data = q3_data()
        settings = config["models"]["q3"]["fixed_search"]
        alphas = [float(value) for value in settings["ridge_alpha"]]
        knots = int(settings["spline_knots"])
        degree = int(settings["spline_degree"])
        folds = data["regression_outer_fold"].to_numpy(dtype=int)
        groups = data["condition_group"].to_numpy(dtype=object)
        y = data["core_loss_W_per_m3"].to_numpy(dtype=np.float64)
        y_log = np.log(y)
        prediction = np.full(len(data), np.nan, dtype=np.float64)
        prediction_log = np.full(len(data), np.nan, dtype=np.float64)
        selection_rows: list[dict[str, Any]] = []
        coefficient_rows: list[dict[str, Any]] = []
        lineage_rows: list[dict[str, Any]] = []
        selected_alphas: list[dict[str, Any]] = []
        fold_models: dict[str, Any] = {}
        for fold in sorted(np.unique(folds)):
            train_index = np.flatnonzero(folds != fold)
            valid_index = np.flatnonzero(folds == fold)
            if set(groups[train_index]).intersection(groups[valid_index]):
                raise AssertionError("Q3 interaction outer group leakage")
            alpha, inner_rows = select_alpha(data.iloc[train_index].reset_index(drop=True), alphas, knots, degree, seed + int(fold))
            for row in inner_rows:
                selection_rows.append({"outer_fold": int(fold), **row})
            model, design = model_and_design(data, "interaction", alpha, knots, degree)
            model.fit(design.iloc[train_index], y_log[train_index])
            smear = smearing_factor(y_log[train_index], model.predict(design.iloc[train_index]))
            fold_log = model.predict(design.iloc[valid_index])
            fold_prediction = np.maximum(1e-9, np.exp(fold_log) * smear)
            prediction_log[valid_index] = fold_log
            prediction[valid_index] = fold_prediction
            names = model.named_steps["features"].get_feature_names_out()
            for name, coefficient in zip(names, model.named_steps["model"].coef_, strict=True):
                coefficient_rows.append({"outer_fold": int(fold), "feature": name, "scaled_coefficient": float(coefficient)})
            model_id = f"q3-interaction-fold-{int(fold)}"
            fold_models[model_id] = {"model": model, "smearing_factor": smear, "alpha": alpha}
            selected_alphas.append({"alpha": alpha})
            lineage_rows.append({"outer_fold": int(fold), "model_id": model_id, "selected_alpha": alpha, "train_n": len(train_index), "validation_n": len(valid_index), "group_overlap_count": 0})
            run.log(f"outer_fold={fold} selected_alpha={alpha}")
        if not np.isfinite(prediction).all():
            raise AssertionError("Q3 interaction OOF coverage incomplete")
        full_alpha = float(modal_parameters(selected_alphas)["alpha"])
        full_model, full_design = model_and_design(data, "interaction", full_alpha, knots, degree)
        full_model.fit(full_design, y_log)
        full_smear = smearing_factor(y_log, full_model.predict(full_design))
        additive = json.loads((S3_RESULTS_ROOT / "q3" / "additive_metrics.json").read_text(encoding="utf-8"))
        additive_log_rmse = float(additive["oof_log_rmse"])
        candidate_log_rmse = float(log_rmse(y, prediction))
        adopted = candidate_log_rmse < additive_log_rmse

        output_dir = S4_RESULTS_ROOT / "q3"
        oof_path = output_dir / "interaction_oof_predictions.csv"
        selection_path = output_dir / "interaction_inner_selection.csv"
        coefficients_path = output_dir / "interaction_fold_coefficients.csv"
        lineage_path = output_dir / "interaction_lineage.csv"
        models_path = output_dir / "interaction_models.joblib"
        metrics_path = output_dir / "interaction_metrics.json"
        winner_path = output_dir / "winner.json"
        evidence_path = run.output_dir / "metrics.json"
        oof = data[["row_id", "temperature_C", "waveform", "material", "frequency_Hz", "b_m_T", "b_half_pp_T", "condition_group", "regression_outer_fold", "core_loss_W_per_m3"]].copy()
        oof["y_pred_log_oof"] = prediction_log
        oof["y_pred_oof"] = prediction
        additive_oof = pd.read_csv(S3_RESULTS_ROOT / "q3" / "additive_oof_predictions.csv").sort_values("row_id").reset_index(drop=True)
        if list(oof["row_id"]) != list(additive_oof["row_id"]):
            raise ValueError("Q3 additive/interaction row identity mismatch")
        oof["additive_y_pred_oof"] = additive_oof["y_pred_oof"].to_numpy(dtype=np.float64)
        write_csv(oof_path, oof)
        write_csv(selection_path, pd.DataFrame(selection_rows))
        write_csv(coefficients_path, pd.DataFrame(coefficient_rows))
        write_csv(lineage_path, pd.DataFrame(lineage_rows))
        models_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"fold_models": fold_models, "full_model": full_model, "full_smearing_factor": full_smear, "full_alpha": full_alpha}, models_path, compress=3)
        metrics = {
            "status": "PASS",
            "model": "pairwise interaction effect-coded spline Ridge",
            "predefined_interactions": settings["interactions"],
            "outer_folds": len(np.unique(folds)),
            "inner_folds": 3,
            "candidate_oof_log_rmse": candidate_log_rmse,
            "candidate_oof_original_scale": regression_metrics(y, prediction),
            "additive_oof_log_rmse": additive_log_rmse,
            "relative_log_rmse_improvement": (additive_log_rmse - candidate_log_rmse) / additive_log_rmse,
            "adopted": bool(adopted),
            "winner": "interaction" if adopted else "additive",
            "full_fit_alpha_from_outer_mode": full_alpha,
            "interpretation": "Adjusted association model; interaction estimates are not causal effects.",
            "failure_flags": {"group_leakage": False, "interaction_oof_worse_than_additive": not adopted},
        }
        write_json(metrics_path, metrics)
        write_json(winner_path, {"winner": metrics["winner"], "full_alpha": full_alpha if adopted else 0.01})
        write_json(evidence_path, metrics)
        for path in (oof_path, selection_path, coefficients_path, lineage_path, models_path, metrics_path, winner_path, evidence_path):
            run.record_output(path)
        run.log(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


def adjusted_grid(data: pd.DataFrame) -> pd.DataFrame:
    log_f = float(np.median(data["log_frequency_Hz"]))
    log_b = float(np.median(data["log_b_m_T"]))
    rows = [
        {"temperature_C": temperature, "waveform": waveform, "material": material, "log_frequency_Hz": log_f, "log_b_m_T": log_b}
        for temperature, waveform, material in itertools.product(TEMPERATURES, WAVEFORM_LABELS, MATERIAL_LABELS)
    ]
    return pd.DataFrame(rows)


def summarize_bootstrap(values: pd.DataFrame, keys: list[str], value_field: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key_values, subset in values.groupby(keys, observed=True):
        if not isinstance(key_values, tuple):
            key_values = (key_values,)
        sample = subset[value_field].to_numpy(dtype=np.float64)
        row = {key: value for key, value in zip(keys, key_values, strict=True)}
        row.update(
            {
                "bootstrap_n": len(sample),
                "median": float(np.median(sample)),
                "ci_lower_2_5pct": float(np.quantile(sample, 0.025)),
                "ci_upper_97_5pct": float(np.quantile(sample, 0.975)),
                "positive_fraction": float(np.mean(sample > 0)),
                "sign_stability": float(max(np.mean(sample > 0), np.mean(sample < 0))),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def run_bootstrap(config_path: Path) -> None:
    run = s4_run(EXPERIMENT_IDS["bootstrap"], config_path, "robustness")
    try:
        config = load_frozen_config(config_path)
        run.record_contract_hashes(verify_contract_registry(config))
        seed = int(config["seeds"]["bootstrap"])
        set_global_seed(seed)
        for path in (
            Path(__file__).resolve(), Path(__file__).with_name("run_q3.py").resolve(), Path(__file__).with_name("s3_common.py").resolve(), Path(__file__).with_name("s4_common.py").resolve(),
            S3_RESULTS_ROOT / "data" / "feature_table.csv", S3_RESULTS_ROOT / "folds" / "fold_assignments.csv",
            S4_RESULTS_ROOT / "q3" / "interaction_metrics.json", S4_RESULTS_ROOT / "q3" / "winner.json",
        ):
            run.record_input(path)
        data = q3_data()
        settings = config["models"]["q3"]["fixed_search"]
        repetitions = int(config["models"]["q3"]["bootstrap_repetitions"])
        winner = json.loads((S4_RESULTS_ROOT / "q3" / "winner.json").read_text(encoding="utf-8"))
        model_kind = str(winner["winner"])
        alpha = float(winner["full_alpha"])
        knots = int(settings["spline_knots"])
        degree = int(settings["spline_degree"])
        groups = data.groupby("condition_group", observed=True).indices
        group_ids = np.array(sorted(groups), dtype=object)
        group_rows = {group_id: np.asarray(groups[group_id], dtype=int) for group_id in group_ids}
        rng = np.random.default_rng(seed)
        grid = adjusted_grid(data)
        main_rows: list[dict[str, Any]] = []
        interaction_rows: list[dict[str, Any]] = []
        cell_rows: list[dict[str, Any]] = []
        lowest_counts: Counter[str] = Counter()
        y_log_all = np.log(data["core_loss_W_per_m3"].to_numpy(dtype=np.float64))
        for repetition in range(repetitions):
            sampled_groups = rng.choice(group_ids, size=len(group_ids), replace=True)
            sample_index = np.concatenate([group_rows[group_id] for group_id in sampled_groups])
            model, design = model_and_design(data, model_kind, alpha, knots, degree)
            model.fit(design.iloc[sample_index], y_log_all[sample_index])
            _, grid_design = model_and_design(grid, model_kind, alpha, knots, degree)
            prediction = model.predict(grid_design)
            evaluated = grid[["temperature_C", "waveform", "material"]].copy()
            evaluated["adjusted_log_loss"] = prediction
            grand = float(np.mean(prediction))
            for factor in ("temperature_C", "waveform", "material"):
                for level, subset in evaluated.groupby(factor, observed=True):
                    main_rows.append({"repetition": repetition, "factor": factor, "level": level, "effect": float(subset["adjusted_log_loss"].mean() - grand)})
            for first, second, marginalized in (
                ("temperature_C", "waveform", "material"),
                ("temperature_C", "material", "waveform"),
                ("waveform", "material", "temperature_C"),
            ):
                pair = evaluated.groupby([first, second], observed=True)["adjusted_log_loss"].mean()
                first_mean = evaluated.groupby(first, observed=True)["adjusted_log_loss"].mean()
                second_mean = evaluated.groupby(second, observed=True)["adjusted_log_loss"].mean()
                for (first_level, second_level), value in pair.items():
                    contrast = float(value - first_mean[first_level] - second_mean[second_level] + grand)
                    interaction_rows.append({"repetition": repetition, "pair": f"{first}_x_{second}", "first_level": first_level, "second_level": second_level, "marginalized_over": marginalized, "effect": contrast})
            for row_index, row in evaluated.iterrows():
                cell_rows.append({"repetition": repetition, **row.to_dict()})
            lowest = evaluated.sort_values(["adjusted_log_loss", "temperature_C", "waveform", "material"]).iloc[0]
            lowest_counts[f"{int(lowest['temperature_C'])}|{lowest['waveform']}|{lowest['material']}"] += 1
            if (repetition + 1) % 100 == 0:
                run.log(f"bootstrap_completed={repetition + 1}/{repetitions}")
        main_intervals = summarize_bootstrap(pd.DataFrame(main_rows), ["factor", "level"], "effect")
        interaction_intervals = summarize_bootstrap(pd.DataFrame(interaction_rows), ["pair", "first_level", "second_level", "marginalized_over"], "effect")
        cell_intervals = summarize_bootstrap(pd.DataFrame(cell_rows), ["temperature_C", "waveform", "material"], "adjusted_log_loss")
        lowest_rows = [
            {"combination": combination, "selection_count": count, "selection_frequency": count / repetitions}
            for combination, count in sorted(lowest_counts.items(), key=lambda item: (-item[1], item[0]))
        ]
        output_dir = S4_RESULTS_ROOT / "q3"
        main_path = output_dir / "bootstrap_main_effect_intervals.csv"
        interactions_path = output_dir / "bootstrap_pairwise_interaction_intervals.csv"
        cells_path = output_dir / "bootstrap_adjusted_cell_intervals.csv"
        lowest_path = output_dir / "bootstrap_lowest_combination_frequency.csv"
        metrics_path = output_dir / "bootstrap_metrics.json"
        evidence_path = run.output_dir / "metrics.json"
        write_csv(main_path, main_intervals)
        write_csv(interactions_path, interaction_intervals)
        write_csv(cells_path, cell_intervals)
        write_csv(lowest_path, pd.DataFrame(lowest_rows))
        metrics = {
            "status": "PASS",
            "winner_model": model_kind,
            "unit": "condition_group",
            "requested_repetitions": repetitions,
            "valid_repetitions": repetitions,
            "interval": "95% condition-group cluster bootstrap percentile interval",
            "pairwise_contrast_count": len(interaction_intervals),
            "stable_pairwise_contrast_count_sign_ge_0_90": int((interaction_intervals["sign_stability"] >= 0.90).sum()),
            "most_frequent_adjusted_lowest_combination": lowest_rows[0],
            "interpretation": "Adjusted associations under the fitted support; not causal effects.",
        }
        write_json(metrics_path, metrics)
        write_json(evidence_path, metrics)
        for path in (main_path, interactions_path, cells_path, lowest_path, metrics_path, evidence_path):
            run.record_output(path)
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
        for path in (
            Path(__file__).resolve(), Path(__file__).with_name("run_q3.py").resolve(), Path(__file__).with_name("s3_common.py").resolve(), Path(__file__).with_name("s4_common.py").resolve(),
            S3_RESULTS_ROOT / "data" / "feature_table.csv", S3_RESULTS_ROOT / "folds" / "fold_assignments.csv",
            S3_RESULTS_ROOT / "q3" / "common_support_summary.json", S3_RESULTS_ROOT / "q3" / "additive_oof_predictions.csv",
            S4_RESULTS_ROOT / "q3" / "interaction_metrics.json", S4_RESULTS_ROOT / "q3" / "winner.json", S4_RESULTS_ROOT / "q3" / "interaction_oof_predictions.csv",
        ):
            run.record_input(path)
        data = q3_data()
        settings = config["models"]["q3"]["fixed_search"]
        knots = int(settings["spline_knots"])
        degree = int(settings["spline_degree"])
        winner = json.loads((S4_RESULTS_ROOT / "q3" / "winner.json").read_text(encoding="utf-8"))
        model_kind = str(winner["winner"])
        if model_kind == "interaction":
            lineage = pd.read_csv(S4_RESULTS_ROOT / "q3" / "interaction_lineage.csv")
            parameters = {int(row["outer_fold"]): float(row["selected_alpha"]) for _, row in lineage.iterrows()}
            winner_oof = pd.read_csv(S4_RESULTS_ROOT / "q3" / "interaction_oof_predictions.csv").sort_values("row_id").reset_index(drop=True)
        else:
            parameters = {int(fold): 0.01 for fold in sorted(data["regression_outer_fold"].unique())}
            winner_oof = pd.read_csv(S3_RESULTS_ROOT / "q3" / "additive_oof_predictions.csv").sort_values("row_id").reset_index(drop=True)
        if list(data["row_id"]) != list(winner_oof["row_id"]):
            raise ValueError("Q3 winner OOF identity mismatch")
        primary_prediction = winner_oof["y_pred_oof"].to_numpy(dtype=np.float64)
        peak_data = data.copy()
        peak_data["log_b_m_T"] = np.log(peak_data["b_half_pp_T"].to_numpy(dtype=np.float64))
        _, peak_prediction, peak_lineage = cross_fit(peak_data, model_kind, parameters, knots, degree)
        dedup_data = data.drop_duplicates("exact_record_sha256", keep="first").reset_index(drop=True)
        _, dedup_prediction, dedup_lineage = cross_fit(dedup_data, model_kind, parameters, knots, degree)
        support = json.loads((S3_RESULTS_ROOT / "q3" / "common_support_summary.json").read_text(encoding="utf-8"))
        support_mask = (
            data["frequency_Hz"].between(*support["common_frequency_Hz"], inclusive="both")
            & data["b_m_T"].between(*support["common_b_m_T"], inclusive="both")
        ).to_numpy()
        additive_oof = pd.read_csv(S3_RESULTS_ROOT / "q3" / "additive_oof_predictions.csv").sort_values("row_id").reset_index(drop=True)
        rows = [
            {"analysis": "winner_primary_all", "log_rmse": log_rmse(data["core_loss_W_per_m3"], primary_prediction), **regression_metrics(data["core_loss_W_per_m3"], primary_prediction)},
            {"analysis": "winner_primary_common_support", "log_rmse": log_rmse(data.loc[support_mask, "core_loss_W_per_m3"], primary_prediction[support_mask]), **regression_metrics(data.loc[support_mask, "core_loss_W_per_m3"], primary_prediction[support_mask])},
            {"analysis": "additive_common_support", "log_rmse": log_rmse(data.loc[support_mask, "core_loss_W_per_m3"], additive_oof.loc[support_mask, "y_pred_oof"]), **regression_metrics(data.loc[support_mask, "core_loss_W_per_m3"], additive_oof.loc[support_mask, "y_pred_oof"])},
            {"analysis": "winner_peak_to_peak_over_2", "log_rmse": log_rmse(data["core_loss_W_per_m3"], peak_prediction), **regression_metrics(data["core_loss_W_per_m3"], peak_prediction)},
            {"analysis": "winner_exact_duplicates_collapsed", "log_rmse": log_rmse(dedup_data["core_loss_W_per_m3"], dedup_prediction), **regression_metrics(dedup_data["core_loss_W_per_m3"], dedup_prediction)},
        ]
        output_dir = S4_RESULTS_ROOT / "q3"
        table_path = output_dir / "sensitivity_summary.csv"
        metrics_path = output_dir / "sensitivity_metrics.json"
        evidence_path = run.output_dir / "metrics.json"
        write_csv(table_path, pd.DataFrame(rows))
        primary = float(rows[0]["log_rmse"])
        metrics = {
            "status": "PASS",
            "winner_model": model_kind,
            "common_support_rows": int(np.sum(support_mask)),
            "common_support_fraction": float(np.mean(support_mask)),
            "winner_vs_additive_common_support_relative_log_rmse_improvement": (float(rows[2]["log_rmse"]) - float(rows[1]["log_rmse"])) / float(rows[2]["log_rmse"]),
            "peak_definition_relative_log_rmse_change": (float(rows[3]["log_rmse"]) - primary) / primary,
            "duplicate_collapse_relative_log_rmse_change": (float(rows[4]["log_rmse"]) - primary) / primary,
            "group_leakage": any(row["group_overlap_count"] != 0 for row in peak_lineage + dedup_lineage),
            "interpretation": "Only adjusted associations stable across support and sensitivity analyses should be reported.",
        }
        write_json(metrics_path, metrics)
        write_json(evidence_path, metrics)
        for path in (table_path, metrics_path, evidence_path):
            run.record_output(path)
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    if args.mode == "interaction":
        run_interaction(config_path)
    elif args.mode == "bootstrap":
        run_bootstrap(config_path)
    else:
        run_sensitivity(config_path)


if __name__ == "__main__":
    main()