"""Run Q5 stability closure on the frozen Q4 winner and predefined sensitivity scenarios."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from run_q4 import group_hash
from run_q5 import (
    add_region_columns,
    pareto_intersection_empty,
    p90_thresholds,
    region_jaccard,
    representative_points,
)
from s3_common import (
    DEFAULT_CONFIG,
    PROJECT_ROOT,
    S3_RESULTS_ROOT,
    assert_pareto,
    load_features_and_folds,
    load_frozen_config,
    pareto_mask,
    set_global_seed,
    sha256_file,
    verify_contract_registry,
    write_csv,
    write_json,
)
from s4_common import S4_RESULTS_ROOT, s4_run

EXPERIMENT_IDS = {"robustness": "EXP-Q5-ROB-001", "sensitivity": "EXP-Q5-SENS-001"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=sorted(EXPERIMENT_IDS), required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def winner_inputs() -> tuple[dict[str, Any], Path, Path, Path, Path, Path]:
    winner_path = S4_RESULTS_ROOT / "q4" / "winner.json"
    winner = json.loads(winner_path.read_text(encoding="utf-8"))
    return (
        winner,
        winner_path,
        project_path(winner["oof_predictions"]),
        project_path(winner["full_predictions"]),
        project_path(winner["fold_models"]),
        project_path(winner["full_model"]),
    )


def load_winner_candidates() -> tuple[pd.DataFrame, dict[str, Any], list[dict[str, Any]], list[Path]]:
    winner, winner_path, oof_path, full_path, fold_models_path, full_model_path = winner_inputs()
    _, _, data = load_features_and_folds()
    data = data.sort_values("row_id").reset_index(drop=True)
    oof = pd.read_csv(oof_path).sort_values("row_id").reset_index(drop=True)
    full = pd.read_csv(full_path).sort_values("row_id").reset_index(drop=True)
    if list(data["row_id"]) != list(oof["row_id"]) or list(data["row_id"]) != list(full["row_id"]):
        raise ValueError("Q5 winner prediction identity mismatch")
    folds = data["regression_outer_fold"].to_numpy(dtype=int)
    groups = data["condition_group"].to_numpy(dtype=object)
    lineage_path = (
        S4_RESULTS_ROOT / "q4" / "hgb_oof_lineage.csv"
        if winner["winner"] == "hgb"
        else S3_RESULTS_ROOT / "q4" / "ridge_oof_lineage.csv"
    )
    lineage = pd.read_csv(lineage_path)
    lineage_rows: list[dict[str, Any]] = []
    strict = np.zeros(len(data), dtype=bool)
    for fold in sorted(np.unique(folds)):
        train_groups = groups[folds != fold]
        valid_groups = groups[folds == fold]
        row = lineage[lineage["outer_fold"] == int(fold)].iloc[0]
        overlap = set(train_groups).intersection(valid_groups)
        train_match = str(row["train_groups_sha256"]) == group_hash(train_groups)
        valid_match = str(row["validation_groups_sha256"]) == group_hash(valid_groups)
        model_match = bool((oof.loc[folds == fold, "oof_model_id"] == row["model_id"]).all())
        passed = not overlap and train_match and valid_match and model_match
        strict[folds == fold] = passed
        lineage_rows.append(
            {
                "outer_fold": int(fold),
                "group_overlap_count": len(overlap),
                "train_groups_sha256_match": train_match,
                "validation_groups_sha256_match": valid_match,
                "model_id_match": model_match,
                "strict_oof_lineage_pass": passed,
            }
        )
    if not strict.all():
        raise AssertionError("Q5 final winner lacks strict OOF lineage")
    candidates = data.copy()
    candidates["y_pred_oof"] = oof["y_pred_oof"].to_numpy(dtype=np.float64)
    candidates["oof_model_id"] = oof["oof_model_id"].to_numpy(dtype=object)
    candidates["y_pred_full"] = full["y_pred_full"].to_numpy(dtype=np.float64)
    candidates["full_model_id"] = full["full_model_id"].to_numpy(dtype=object)
    candidates["strict_oof_lineage_pass"] = strict
    inputs = [winner_path, oof_path, full_path, fold_models_path, full_model_path, lineage_path]
    return candidates, winner, lineage_rows, inputs


def collapse_exact(candidates: pd.DataFrame, keep_duplicates: bool = False) -> tuple[pd.DataFrame, int]:
    if keep_duplicates:
        result = candidates.copy().sort_values("row_id").reset_index(drop=True)
        result["duplicate_row_ids"] = result["row_id"]
        return result, 0
    records: list[pd.Series] = []
    dropped = 0
    for _, subset in candidates.groupby("exact_record_sha256", sort=True, observed=True):
        ordered = subset.sort_values("row_id")
        if len(ordered) > 1:
            if np.ptp(ordered["y_pred_oof"].to_numpy(dtype=np.float64)) > 1e-8 or np.ptp(ordered["y_pred_full"].to_numpy(dtype=np.float64)) > 1e-8:
                raise AssertionError("Exact duplicates received inconsistent Q4 winner predictions")
            dropped += len(ordered) - 1
        row = ordered.iloc[0].copy()
        row["duplicate_row_ids"] = "|".join(ordered["row_id"].astype(str))
        records.append(row)
    return pd.DataFrame(records).reset_index(drop=True), dropped


def primary_candidates(all_candidates: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any], int]:
    lower, upper = map(float, config["models"]["q5"]["primary_frequency_hz"])
    filtered = all_candidates[all_candidates["frequency_Hz"].between(lower, upper, inclusive="both")].copy()
    collapsed, dropped = collapse_exact(filtered)
    collapsed, region_metadata = add_region_columns(collapsed)
    collapsed["energy_proxy_Hz_T"] = collapsed["frequency_Hz"] * collapsed["b_m_T"]
    collapsed["full_oof_log_gap"] = np.abs(np.log1p(collapsed["y_pred_full"]) - np.log1p(collapsed["y_pred_oof"]))
    collapsed["oof_absolute_log_residual"] = np.abs(np.log1p(collapsed["core_loss_W_per_m3"]) - np.log1p(collapsed["y_pred_oof"]))
    return collapsed, region_metadata, dropped


def run_robustness(config_path: Path) -> None:
    run = s4_run(EXPERIMENT_IDS["robustness"], config_path, "robustness")
    try:
        config = load_frozen_config(config_path)
        run.record_contract_hashes(verify_contract_registry(config))
        seed = int(config["models"]["q5"]["bootstrap"]["seed"])
        set_global_seed(seed)
        all_candidates, winner, lineage_rows, winner_paths = load_winner_candidates()
        for path in (
            Path(__file__).resolve(), Path(__file__).with_name("run_q5.py").resolve(), Path(__file__).with_name("run_q4.py").resolve(),
            Path(__file__).with_name("s3_common.py").resolve(), Path(__file__).with_name("s4_common.py").resolve(),
            S3_RESULTS_ROOT / "data" / "feature_table.csv", S3_RESULTS_ROOT / "folds" / "fold_assignments.csv", *winner_paths,
        ):
            run.record_input(path)
        candidates, region_metadata, duplicate_dropped = primary_candidates(all_candidates, config)
        minimum_reference_n = int(config["models"]["q5"]["conflict_diagnostics"]["reference_group_min_n"])
        gap_thresholds, gap_rows, global_gap = p90_thresholds(candidates, "full_oof_log_gap", minimum_reference_n)
        residual_thresholds, residual_rows, global_residual = p90_thresholds(candidates, "oof_absolute_log_residual", minimum_reference_n)
        candidates["full_oof_gap_p90"] = gap_thresholds
        candidates["oof_residual_p90"] = residual_thresholds
        candidates["full_oof_gap_pass"] = candidates["full_oof_log_gap"] <= candidates["full_oof_gap_p90"]
        candidates["oof_residual_pass"] = candidates["oof_absolute_log_residual"] <= candidates["oof_residual_p90"]
        oof_mask = pareto_mask(candidates["y_pred_oof"], candidates["energy_proxy_Hz_T"])
        full_mask = pareto_mask(candidates["y_pred_full"], candidates["energy_proxy_Hz_T"])
        observed_mask = pareto_mask(candidates["core_loss_W_per_m3"], candidates["energy_proxy_Hz_T"])
        assert_pareto(candidates["y_pred_oof"], candidates["energy_proxy_Hz_T"], oof_mask)
        assert_pareto(candidates["y_pred_full"], candidates["energy_proxy_Hz_T"], full_mask)
        assert_pareto(candidates["core_loss_W_per_m3"], candidates["energy_proxy_Hz_T"], observed_mask)
        candidates["is_oof_pareto"] = oof_mask
        candidates["is_full_fit_pareto"] = full_mask
        candidates["is_observed_loss_pareto"] = observed_mask
        candidates["dual_pareto_pass"] = oof_mask & full_mask

        heldout_parts: list[pd.DataFrame] = []
        for fold, subset in candidates.groupby("regression_outer_fold", observed=True):
            local_mask = pareto_mask(subset["y_pred_oof"], subset["energy_proxy_Hz_T"])
            part = subset.loc[local_mask, ["row_id", "q5_region_id"]].copy()
            part["outer_fold"] = int(fold)
            heldout_parts.append(part)
        heldout = pd.concat(heldout_parts, ignore_index=True)
        support_counts = heldout.groupby("q5_region_id", observed=True)["outer_fold"].nunique()
        actual_folds = int(candidates["regression_outer_fold"].nunique())
        support_required = int(math.ceil(float(config["models"]["q5"]["heldout_fold_region_support_fraction"]) * actual_folds))
        region_support = candidates.groupby("q5_region_id", observed=True).agg(candidate_n=("row_id", "size"), candidate_fold_count=("regression_outer_fold", "nunique")).reset_index()
        region_support["heldout_pareto_fold_support"] = region_support["q5_region_id"].map(support_counts).fillna(0).astype(int)
        region_support["required_fold_support"] = support_required
        region_support["region_fold_support_pass"] = region_support["heldout_pareto_fold_support"] >= support_required
        fold_stable_regions = set(region_support.loc[region_support["region_fold_support_pass"], "q5_region_id"])
        candidates["region_fold_support_pass"] = candidates["q5_region_id"].isin(fold_stable_regions)
        model_regions = set(candidates.loc[oof_mask & candidates["region_fold_support_pass"], "q5_region_id"])
        observed_regions = set(candidates.loc[observed_mask, "q5_region_id"])
        jaccard_threshold = float(config["models"]["q5"]["conflict_diagnostics"]["observed_region_jaccard_min"])
        jaccard, jaccard_case, jaccard_pass = region_jaccard(model_regions, observed_regions, jaccard_threshold)

        bootstrap = config["models"]["q5"]["bootstrap"]
        repetitions = int(bootstrap["repetitions"])
        min_valid = int(bootstrap["min_valid_repetitions_per_region"])
        min_rate = float(bootstrap["conditional_region_pareto_rate_min"])
        group_indices = candidates.groupby("condition_group", observed=True).indices
        group_ids = np.array(sorted(group_indices), dtype=object)
        index_by_group = {group_id: np.asarray(group_indices[group_id], dtype=int) for group_id in group_ids}
        rng = np.random.default_rng(seed)
        candidate_appearance = np.zeros(len(candidates), dtype=np.int32)
        candidate_pareto = np.zeros(len(candidates), dtype=np.int32)
        regions = sorted(candidates["q5_region_id"].unique())
        region_position = {region: index for index, region in enumerate(regions)}
        region_appearance = np.zeros(len(regions), dtype=np.int32)
        region_pareto = np.zeros(len(regions), dtype=np.int32)
        region_values = candidates["q5_region_id"].to_numpy(dtype=object)
        for repetition in range(repetitions):
            sampled_groups = rng.choice(group_ids, size=len(group_ids), replace=True)
            sampled_index = np.concatenate([index_by_group[group_id] for group_id in sampled_groups])
            present = np.unique(sampled_index)
            candidate_appearance[present] += 1
            local_pareto = pareto_mask(
                candidates.iloc[sampled_index]["y_pred_oof"],
                candidates.iloc[sampled_index]["energy_proxy_Hz_T"],
            )
            selected = np.unique(sampled_index[local_pareto])
            candidate_pareto[selected] += 1
            for region in np.unique(region_values[present]):
                region_appearance[region_position[region]] += 1
            for region in np.unique(region_values[selected]):
                region_pareto[region_position[region]] += 1
            if (repetition + 1) % 100 == 0:
                run.log(f"bootstrap_completed={repetition + 1}/{repetitions}")
        candidate_rates = np.divide(candidate_pareto, candidate_appearance, out=np.zeros(len(candidates), dtype=float), where=candidate_appearance > 0)
        bootstrap_candidates = candidates[["row_id", "condition_group", "q5_region_id"]].copy()
        bootstrap_candidates["valid_repetitions"] = candidate_appearance
        bootstrap_candidates["pareto_repetitions"] = candidate_pareto
        bootstrap_candidates["conditional_pareto_rate"] = candidate_rates
        region_rates = np.divide(region_pareto, region_appearance, out=np.zeros(len(regions), dtype=float), where=region_appearance > 0)
        bootstrap_regions = pd.DataFrame(
            {
                "q5_region_id": regions,
                "valid_repetitions": region_appearance,
                "pareto_repetitions": region_pareto,
                "conditional_region_pareto_rate": region_rates,
            }
        )
        bootstrap_regions["minimum_valid_repetitions"] = min_valid
        bootstrap_regions["minimum_conditional_rate"] = min_rate
        bootstrap_regions["bootstrap_region_stability_pass"] = (bootstrap_regions["valid_repetitions"] >= min_valid) & (bootstrap_regions["conditional_region_pareto_rate"] >= min_rate)
        stable_bootstrap_regions = set(bootstrap_regions.loc[bootstrap_regions["bootstrap_region_stability_pass"], "q5_region_id"])
        candidates["bootstrap_region_stability_pass"] = candidates["q5_region_id"].isin(stable_bootstrap_regions)
        candidates["candidate_bootstrap_valid_repetitions"] = candidate_appearance
        candidates["candidate_bootstrap_pareto_rate"] = candidate_rates
        candidates["observed_region_jaccard_pass"] = jaccard_pass
        candidates["single_point_eligible"] = (
            candidates["strict_oof_lineage_pass"] & candidates["dual_pareto_pass"] & candidates["full_oof_gap_pass"]
            & candidates["oof_residual_pass"] & candidates["region_fold_support_pass"]
            & candidates["bootstrap_region_stability_pass"] & jaccard_pass
        )
        representatives, degeneracy = representative_points(candidates.loc[oof_mask].copy())

        output_dir = S4_RESULTS_ROOT / "q5"
        candidates_path = output_dir / "final_candidate_index.csv"
        oof_path = output_dir / "final_oof_pareto.csv"
        full_path = output_dir / "final_full_fit_reference_pareto.csv"
        observed_path = output_dir / "observed_loss_pareto_diagnostic.csv"
        heldout_path = output_dir / "heldout_fold_pareto.csv"
        support_path = output_dir / "heldout_fold_region_support.csv"
        bootstrap_candidate_path = output_dir / "bootstrap_candidate_stability.csv"
        bootstrap_region_path = output_dir / "bootstrap_region_stability.csv"
        thresholds_path = output_dir / "conflict_thresholds.csv"
        lineage_path = output_dir / "strict_oof_lineage_assertions.csv"
        representatives_path = output_dir / "representative_conditions.json"
        metrics_path = output_dir / "robustness_metrics.json"
        evidence_path = run.output_dir / "metrics.json"
        write_csv(candidates_path, candidates)
        write_csv(oof_path, candidates.loc[oof_mask].copy())
        write_csv(full_path, candidates.loc[full_mask].copy())
        write_csv(observed_path, candidates.loc[observed_mask].copy())
        write_csv(heldout_path, heldout)
        write_csv(support_path, region_support)
        write_csv(bootstrap_candidate_path, bootstrap_candidates)
        write_csv(bootstrap_region_path, bootstrap_regions)
        threshold_rows = [{"diagnostic": "full_oof_log_gap", "global_p90": global_gap, **row} for row in gap_rows] + [{"diagnostic": "oof_absolute_log_residual", "global_p90": global_residual, **row} for row in residual_rows]
        write_csv(thresholds_path, pd.DataFrame(threshold_rows))
        write_csv(lineage_path, pd.DataFrame(lineage_rows))
        write_json(representatives_path, {"provisional_only": True, **representatives, "degeneracy": degeneracy})
        eligible_n = int(candidates["single_point_eligible"].sum())
        metrics = {
            "status": "PASS" if eligible_n else "PASS_WITH_NO_UNIQUE_RECOMMENDATION",
            "q4_winner": winner["winner"],
            "candidate_rows_before_exact_duplicate_collapse": len(candidates) + duplicate_dropped,
            "candidate_rows_after_exact_duplicate_collapse": len(candidates),
            "exact_duplicate_rows_dropped": duplicate_dropped,
            "oof_pareto_count": int(oof_mask.sum()),
            "full_fit_pareto_count": int(full_mask.sum()),
            "observed_loss_pareto_count": int(observed_mask.sum()),
            "oof_full_pareto_intersection_empty": pareto_intersection_empty(oof_mask, full_mask),
            "fold_supported_region_count": len(fold_stable_regions),
            "bootstrap": {
                "unit": "condition_group",
                "requested_repetitions": repetitions,
                "valid_repetitions": repetitions,
                "stable_region_count": len(stable_bootstrap_regions),
                "minimum_valid_repetitions_per_region": min_valid,
                "conditional_region_pareto_rate_min": min_rate,
                "interval_name": bootstrap["interval_name"],
                "interpretation": "Resampling stability of the fixed cross-fitted candidate table, not full model-parameter uncertainty.",
            },
            "observed_region_jaccard": jaccard,
            "observed_region_jaccard_case": jaccard_case,
            "observed_region_jaccard_min": jaccard_threshold,
            "observed_region_jaccard_pass": jaccard_pass,
            "single_point_eligible_count": eligible_n,
            "unique_recommendation_authorized": bool(eligible_n == 1),
            "region_metadata": region_metadata,
            "representatives_are_provisional": True,
            "failure_flags": {
                "strict_oof_lineage_failure": not all(row["strict_oof_lineage_pass"] for row in lineage_rows),
                "jaccard_failure": not jaccard_pass,
                "no_single_point_eligible": eligible_n == 0,
            },
        }
        write_json(metrics_path, metrics)
        write_json(evidence_path, metrics)
        for path in (
            candidates_path, oof_path, full_path, observed_path, heldout_path, support_path,
            bootstrap_candidate_path, bootstrap_region_path, thresholds_path, lineage_path,
            representatives_path, metrics_path, evidence_path,
        ):
            run.record_output(path)
        run.log(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


def scenario_summary(
    all_candidates: pd.DataFrame,
    *,
    name: str,
    frequency_range: tuple[float, float],
    b_field: str,
    keep_duplicates: bool,
    primary_regions: set[str] | None,
) -> tuple[dict[str, Any], set[str]]:
    data = all_candidates[all_candidates["frequency_Hz"].between(*frequency_range, inclusive="both")].copy()
    data, dropped = collapse_exact(data, keep_duplicates=keep_duplicates)
    region_input = data.copy()
    region_input["b_m_T"] = region_input[b_field]
    region_input, _ = add_region_columns(region_input)
    energy = region_input["frequency_Hz"].to_numpy(dtype=np.float64) * region_input[b_field].to_numpy(dtype=np.float64)
    oof = pareto_mask(region_input["y_pred_oof"], energy)
    observed = pareto_mask(region_input["core_loss_W_per_m3"], energy)
    model_regions = set(region_input.loc[oof, "q5_region_id"])
    observed_regions = set(region_input.loc[observed, "q5_region_id"])
    jaccard, _, _ = region_jaccard(model_regions, observed_regions, 0.5)
    overlap = None
    if primary_regions is not None:
        union = model_regions | primary_regions
        overlap = None if not union else len(model_regions & primary_regions) / len(union)
    return (
        {
            "scenario": name,
            "frequency_min_Hz": frequency_range[0],
            "frequency_max_Hz": frequency_range[1],
            "b_peak_field": b_field,
            "keep_exact_duplicates": keep_duplicates,
            "candidate_count": len(region_input),
            "exact_duplicates_dropped": dropped,
            "oof_pareto_count": int(oof.sum()),
            "observed_pareto_count": int(observed.sum()),
            "oof_observed_region_jaccard": jaccard,
            "oof_region_jaccard_vs_primary": overlap,
        },
        model_regions,
    )


def run_sensitivity(config_path: Path) -> None:
    run = s4_run(EXPERIMENT_IDS["sensitivity"], config_path, "sensitivity")
    try:
        config = load_frozen_config(config_path)
        run.record_contract_hashes(verify_contract_registry(config))
        set_global_seed(int(config["seeds"]["optimization_stability"]))
        all_candidates, _, _, winner_paths = load_winner_candidates()
        robustness_path = S4_RESULTS_ROOT / "q5" / "robustness_metrics.json"
        for path in (
            Path(__file__).resolve(), Path(__file__).with_name("run_q5.py").resolve(), Path(__file__).with_name("s3_common.py").resolve(), Path(__file__).with_name("s4_common.py").resolve(),
            S3_RESULTS_ROOT / "data" / "feature_table.csv", S3_RESULTS_ROOT / "folds" / "fold_assignments.csv", robustness_path, *winner_paths,
        ):
            run.record_input(path)
        primary_range = tuple(map(float, config["models"]["q5"]["primary_frequency_hz"]))
        sensitivity_range = tuple(map(float, config["models"]["q5"]["sensitivity_frequency_hz"]))
        primary, primary_regions = scenario_summary(all_candidates, name="primary", frequency_range=primary_range, b_field="b_m_T", keep_duplicates=False, primary_regions=None)
        scenarios = [primary]
        for name, frequency_range, b_field, keep_duplicates in (
            ("expanded_frequency", sensitivity_range, "b_m_T", False),
            ("peak_to_peak_over_2", primary_range, "b_half_pp_T", False),
            ("exact_duplicates_retained", primary_range, "b_m_T", True),
        ):
            result, _ = scenario_summary(all_candidates, name=name, frequency_range=frequency_range, b_field=b_field, keep_duplicates=keep_duplicates, primary_regions=primary_regions)
            scenarios.append(result)
        output_dir = S4_RESULTS_ROOT / "q5"
        table_path = output_dir / "sensitivity_scenarios.csv"
        metrics_path = output_dir / "sensitivity_metrics.json"
        evidence_path = run.output_dir / "metrics.json"
        write_csv(table_path, pd.DataFrame(scenarios))
        metrics = {
            "status": "PASS",
            "scenarios": scenarios,
            "minimum_oof_region_jaccard_vs_primary": min(float(row["oof_region_jaccard_vs_primary"]) for row in scenarios[1:] if row["oof_region_jaccard_vs_primary"] is not None),
            "all_scenarios_observed_jaccard_pass_0_5": all(row["oof_observed_region_jaccard"] is not None and float(row["oof_observed_region_jaccard"]) >= 0.5 for row in scenarios),
            "unique_recommendation_policy": "Sensitivity does not override any failed dual-Pareto, fold, bootstrap, or observed-Jaccard gate.",
        }
        write_json(metrics_path, metrics)
        write_json(evidence_path, metrics)
        for path in (table_path, metrics_path, evidence_path):
            run.record_output(path)
        run.log(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    if args.mode == "robustness":
        run_robustness(config_path)
    else:
        run_sensitivity(config_path)


if __name__ == "__main__":
    main()