"""Run the approved Q5 strict-OOF observed-operating-point Pareto Baseline."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from s3_common import (
    DEFAULT_CONFIG,
    Q4_CATEGORICAL_FEATURES,
    Q4_NUMERIC_FEATURES,
    S3_RESULTS_ROOT,
    ExperimentRun,
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
from run_q4 import group_hash


EXPERIMENT_ID = "EXP-Q5-BASE-001"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["oof-observed-pareto"], default="oof-observed-pareto")
    parser.add_argument("--stage", choices=["baseline"], default="baseline")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def quartile_edges(values: pd.Series) -> tuple[np.ndarray, int]:
    raw = np.quantile(values.to_numpy(dtype=np.float64), [0.0, 0.25, 0.5, 0.75, 1.0], method="linear")
    unique = np.unique(raw)
    dropped = int(raw.size - unique.size)
    if unique.size < 2:
        raise ValueError("Quartile binning has fewer than two unique edges")
    return unique, dropped


def assign_bins(values: pd.Series, edges: np.ndarray) -> np.ndarray:
    bins = np.searchsorted(edges[1:-1], values.to_numpy(dtype=np.float64), side="right")
    if np.any(bins < 0) or np.any(bins >= edges.size - 1):
        raise AssertionError("Quartile bin assignment out of range")
    return bins.astype(int)


def add_region_columns(candidates: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    result = candidates.copy()
    frequency_edges, frequency_dropped = quartile_edges(result["frequency_Hz"])
    b_m_edges, b_m_dropped = quartile_edges(result["b_m_T"])
    result["frequency_quartile"] = assign_bins(result["frequency_Hz"], frequency_edges)
    result["b_m_quartile"] = assign_bins(result["b_m_T"], b_m_edges)
    result["q5_region_id"] = (
        result["material"].astype(str)
        + "|"
        + result["waveform"].astype(str)
        + "|"
        + result["temperature_C"].astype(int).astype(str)
        + "|fq"
        + result["frequency_quartile"].astype(str)
        + "|bq"
        + result["b_m_quartile"].astype(str)
    )
    metadata = {
        "version": "q5-region-v1",
        "frequency_edges_Hz": frequency_edges.tolist(),
        "b_m_edges_T": b_m_edges.tolist(),
        "frequency_duplicate_edges_dropped": frequency_dropped,
        "b_m_duplicate_edges_dropped": b_m_dropped,
        "interval_rule": "left_closed_right_open_except_last_closed",
    }
    return result, metadata


def p90_thresholds(candidates: pd.DataFrame, field: str, minimum_n: int) -> tuple[np.ndarray, list[dict[str, object]], float]:
    global_threshold = float(np.quantile(candidates[field], 0.90))
    thresholds = np.full(len(candidates), global_threshold, dtype=np.float64)
    rows: list[dict[str, object]] = []
    for (material, waveform), subset in candidates.groupby(["material", "waveform"], observed=True):
        use_local = len(subset) >= minimum_n
        threshold = float(np.quantile(subset[field], 0.90)) if use_local else global_threshold
        thresholds[subset.index.to_numpy(dtype=int)] = threshold
        rows.append(
            {
                "diagnostic": field,
                "material": material,
                "waveform": waveform,
                "n": len(subset),
                "threshold_source": "material_x_waveform" if use_local else "global_fallback",
                "p90_threshold": threshold,
            }
        )
    return thresholds, rows, global_threshold


def representative_points(pareto: pd.DataFrame) -> tuple[dict[str, object], dict[str, bool]]:
    if pareto.empty:
        raise ValueError("Cannot choose representative points from an empty Pareto set")
    ordered_loss = pareto.sort_values(["y_pred_oof", "energy_proxy_Hz_T", "row_id"], ascending=[True, False, True])
    ordered_energy = pareto.sort_values(["energy_proxy_Hz_T", "y_pred_oof", "row_id"], ascending=[False, True, True])
    loss_min = float(pareto["y_pred_oof"].min())
    loss_max = float(pareto["y_pred_oof"].max())
    energy_min = float(pareto["energy_proxy_Hz_T"].min())
    energy_max = float(pareto["energy_proxy_Hz_T"].max())
    loss_zero_range = loss_max == loss_min
    energy_zero_range = energy_max == energy_min
    normalized_loss = np.zeros(len(pareto)) if loss_zero_range else (pareto["y_pred_oof"].to_numpy() - loss_min) / (loss_max - loss_min)
    normalized_negative_energy = np.zeros(len(pareto)) if energy_zero_range else (energy_max - pareto["energy_proxy_Hz_T"].to_numpy()) / (energy_max - energy_min)
    distance = np.sqrt(normalized_loss**2 + normalized_negative_energy**2)
    knee_candidates = pareto.assign(ideal_distance=distance).sort_values(
        ["ideal_distance", "full_oof_log_gap", "oof_absolute_log_residual", "row_id"],
        ascending=[True, True, True, True],
    )
    return (
        {
            "minimum_oof_loss_endpoint_row_id": str(ordered_loss.iloc[0]["row_id"]),
            "maximum_energy_endpoint_row_id": str(ordered_energy.iloc[0]["row_id"]),
            "provisional_oof_knee_row_id": str(knee_candidates.iloc[0]["row_id"]),
            "provisional_oof_knee_ideal_distance": float(knee_candidates.iloc[0]["ideal_distance"]),
        },
        {"pareto_loss_zero_range": loss_zero_range, "pareto_energy_zero_range": energy_zero_range},
    )


def pareto_intersection_empty(first_mask: np.ndarray, second_mask: np.ndarray) -> bool:
    """Return whether two Pareto masks have no common candidate."""
    first = np.asarray(first_mask, dtype=bool)
    second = np.asarray(second_mask, dtype=bool)
    if first.shape != second.shape:
        raise ValueError("Pareto masks must have identical shapes")
    return not bool(np.any(first & second))


def region_jaccard(
    model_regions: set[str], observed_regions: set[str], threshold: float
) -> tuple[float | None, str, bool]:
    """Compute region Jaccard and make the both-empty policy explicit."""
    union = model_regions | observed_regions
    if not union:
        return None, "both_region_sets_empty", False
    score = len(model_regions & observed_regions) / len(union)
    return score, "defined", score >= threshold


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    run = ExperimentRun(EXPERIMENT_ID, config_path)
    try:
        config = load_frozen_config(config_path)
        contract_hashes = verify_contract_registry(config)
        run.record_contract_hashes(contract_hashes)
        seed = int(config["seeds"]["optimization_stability"])
        set_global_seed(seed)
        run.record_input(Path(__file__).resolve())
        run.record_input(Path(__file__).with_name("s3_common.py").resolve())
        run.record_input(Path(__file__).with_name("run_q4.py").resolve())

        feature_path = S3_RESULTS_ROOT / "data" / "feature_table.csv"
        fold_path = S3_RESULTS_ROOT / "folds" / "fold_assignments.csv"
        schema_path = S3_RESULTS_ROOT / "data" / "feature_schema.json"
        q4_oof_path = S3_RESULTS_ROOT / "q4" / "ridge_oof_predictions.csv"
        q4_full_path = S3_RESULTS_ROOT / "q4" / "ridge_full_fit_training_predictions.csv"
        q4_metrics_path = S3_RESULTS_ROOT / "q4" / "ridge_metrics.json"
        q4_lineage_path = S3_RESULTS_ROOT / "q4" / "ridge_oof_lineage.csv"
        q4_fold_models_path = S3_RESULTS_ROOT / "q4" / "ridge_fold_models.joblib"
        q4_full_model_path = S3_RESULTS_ROOT / "q4" / "ridge_full_model.joblib"
        for path in (
            feature_path,
            fold_path,
            schema_path,
            q4_oof_path,
            q4_full_path,
            q4_metrics_path,
            q4_lineage_path,
            q4_fold_models_path,
            q4_full_model_path,
        ):
            run.record_input(path)

        _, _, data = load_features_and_folds()
        data = data.sort_values("row_id").reset_index(drop=True)
        q4_oof = pd.read_csv(q4_oof_path).sort_values("row_id").reset_index(drop=True)
        q4_full = pd.read_csv(q4_full_path).sort_values("row_id").reset_index(drop=True)
        q4_lineage = pd.read_csv(q4_lineage_path)
        q4_metrics = json.loads(q4_metrics_path.read_text(encoding="utf-8"))
        if list(data["row_id"]) != list(q4_oof["row_id"]) or list(data["row_id"]) != list(q4_full["row_id"]):
            raise ValueError("Q5 input row order or identity mismatch")

        lineage_assertions: list[dict[str, object]] = []
        row_excluded = np.zeros(len(data), dtype=bool)
        for fold in sorted(data["regression_outer_fold"].unique()):
            fold_mask = data["regression_outer_fold"].to_numpy(dtype=int) == int(fold)
            train_groups = data.loc[~fold_mask, "condition_group"].to_numpy(dtype=object)
            validation_groups = data.loc[fold_mask, "condition_group"].to_numpy(dtype=object)
            overlap = set(train_groups).intersection(validation_groups)
            lineage_row = q4_lineage[q4_lineage["outer_fold"] == int(fold)]
            if len(lineage_row) != 1:
                raise ValueError(f"Q4 lineage missing or duplicated for fold {fold}")
            recorded = lineage_row.iloc[0]
            train_hash_match = str(recorded["train_groups_sha256"]) == group_hash(train_groups)
            validation_hash_match = str(recorded["validation_groups_sha256"]) == group_hash(validation_groups)
            model_id_match = bool((q4_oof.loc[fold_mask, "oof_model_id"] == recorded["model_id"]).all())
            fold_id_match = bool((q4_oof.loc[fold_mask, "regression_outer_fold"].astype(int) == int(fold)).all())
            excluded = not overlap and train_hash_match and validation_hash_match and model_id_match and fold_id_match
            row_excluded[fold_mask] = excluded
            lineage_assertions.append(
                {
                    "outer_fold": int(fold),
                    "validation_n": int(fold_mask.sum()),
                    "group_overlap_count": len(overlap),
                    "train_groups_sha256_match": train_hash_match,
                    "validation_groups_sha256_match": validation_hash_match,
                    "model_id_match": model_id_match,
                    "fold_id_match": fold_id_match,
                    "strict_oof_lineage_pass": excluded,
                }
            )
        if not row_excluded.all():
            raise AssertionError("At least one Q5 candidate lacks strict OOF lineage")

        candidates = data.copy()
        candidates["y_pred_oof"] = q4_oof["y_pred_oof"].to_numpy(dtype=np.float64)
        candidates["oof_model_id"] = q4_oof["oof_model_id"].to_numpy(dtype=object)
        candidates["y_pred_full"] = q4_full["y_pred_full"].to_numpy(dtype=np.float64)
        candidates["full_model_id"] = q4_full["full_model_id"].to_numpy(dtype=object)
        candidates["strict_oof_lineage_pass"] = row_excluded
        frequency_min, frequency_max = map(float, config["models"]["q5"]["primary_frequency_hz"])
        candidates = candidates[candidates["frequency_Hz"].between(frequency_min, frequency_max, inclusive="both")].copy()
        candidates = candidates.sort_values("row_id").reset_index(drop=True)
        if candidates.empty:
            raise ValueError("Q5 nominal candidate set is empty")

        duplicate_rows: list[pd.Series] = []
        collapsed_records: list[pd.Series] = []
        for _, subset in candidates.groupby("exact_record_sha256", sort=True, observed=True):
            ordered = subset.sort_values("row_id")
            if len(ordered) > 1:
                if np.ptp(ordered["y_pred_oof"].to_numpy(dtype=np.float64)) > 1e-8 or np.ptp(ordered["y_pred_full"].to_numpy(dtype=np.float64)) > 1e-8:
                    raise AssertionError("Exact duplicate rows received inconsistent Q4 predictions")
                duplicate_rows.extend(row for _, row in ordered.iloc[1:].iterrows())
            canonical = ordered.iloc[0].copy()
            canonical["duplicate_row_ids"] = "|".join(ordered["row_id"].astype(str))
            collapsed_records.append(canonical)
        candidates = pd.DataFrame(collapsed_records).reset_index(drop=True)
        candidates, region_metadata = add_region_columns(candidates)
        candidates["energy_proxy_Hz_T"] = candidates["frequency_Hz"] * candidates["b_m_T"]
        candidates["full_oof_log_gap"] = np.abs(np.log1p(candidates["y_pred_full"]) - np.log1p(candidates["y_pred_oof"]))
        candidates["oof_absolute_log_residual"] = np.abs(np.log1p(candidates["core_loss_W_per_m3"]) - np.log1p(candidates["y_pred_oof"]))

        minimum_reference_n = int(config["models"]["q5"]["conflict_diagnostics"]["reference_group_min_n"])
        gap_thresholds, gap_rows, global_gap_p90 = p90_thresholds(candidates, "full_oof_log_gap", minimum_reference_n)
        residual_thresholds, residual_rows, global_residual_p90 = p90_thresholds(candidates, "oof_absolute_log_residual", minimum_reference_n)
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

        heldout_pareto_parts: list[pd.DataFrame] = []
        for fold, subset in candidates.groupby("regression_outer_fold", observed=True):
            local_mask = pareto_mask(subset["y_pred_oof"], subset["energy_proxy_Hz_T"])
            assert_pareto(subset["y_pred_oof"], subset["energy_proxy_Hz_T"], local_mask)
            local = subset.loc[local_mask, ["row_id", "q5_region_id", "y_pred_oof", "energy_proxy_Hz_T"]].copy()
            local["outer_fold"] = int(fold)
            heldout_pareto_parts.append(local)
        heldout_pareto = pd.concat(heldout_pareto_parts, ignore_index=True)
        support_counts = heldout_pareto.groupby("q5_region_id", observed=True)["outer_fold"].nunique()
        actual_folds = int(candidates["regression_outer_fold"].nunique())
        support_required = int(math.ceil(float(config["models"]["q5"]["heldout_fold_region_support_fraction"]) * actual_folds))
        region_support = (
            candidates.groupby("q5_region_id", observed=True)
            .agg(candidate_n=("row_id", "size"), candidate_fold_count=("regression_outer_fold", "nunique"))
            .reset_index()
        )
        region_support["heldout_pareto_fold_support"] = region_support["q5_region_id"].map(support_counts).fillna(0).astype(int)
        region_support["required_fold_support"] = support_required
        region_support["region_fold_support_pass"] = region_support["heldout_pareto_fold_support"] >= support_required
        stable_regions = set(region_support.loc[region_support["region_fold_support_pass"], "q5_region_id"])
        candidates["region_fold_support_pass"] = candidates["q5_region_id"].isin(stable_regions)

        model_regions = set(candidates.loc[oof_mask & candidates["region_fold_support_pass"], "q5_region_id"])
        observed_regions = set(candidates.loc[observed_mask, "q5_region_id"])
        jaccard, jaccard_case, jaccard_pass = region_jaccard(
            model_regions,
            observed_regions,
            float(config["models"]["q5"]["conflict_diagnostics"]["observed_region_jaccard_min"]),
        )
        candidates["observed_region_jaccard_pass"] = jaccard_pass
        candidates["prebootstrap_single_point_eligible"] = (
            candidates["strict_oof_lineage_pass"]
            & candidates["dual_pareto_pass"]
            & candidates["full_oof_gap_pass"]
            & candidates["oof_residual_pass"]
            & candidates["region_fold_support_pass"]
            & jaccard_pass
        )

        oof_pareto = candidates.loc[oof_mask].copy().sort_values(["energy_proxy_Hz_T", "y_pred_oof"], ascending=[True, True])
        full_pareto = candidates.loc[full_mask].copy().sort_values(["energy_proxy_Hz_T", "y_pred_full"], ascending=[True, True])
        observed_pareto = candidates.loc[observed_mask].copy().sort_values(["energy_proxy_Hz_T", "core_loss_W_per_m3"], ascending=[True, True])
        representatives, degeneracy = representative_points(oof_pareto)
        empty_intersection = pareto_intersection_empty(oof_mask, full_mask)
        q4_capability = bool(q4_metrics["beats_at_least_one_median_reference"])

        config_hash = sha256_file(config_path)
        schema_hash = sha256_file(schema_path)
        fold_models_hash = sha256_file(q4_fold_models_path)
        full_model_hash = sha256_file(q4_full_model_path)
        identity_constants = {
            "feature_schema_sha256": schema_hash,
            "q4_fold_models_artifact_sha256": fold_models_hash,
            "q4_full_model_artifact_sha256": full_model_hash,
            "config_sha256": config_hash,
        }
        for column, value in identity_constants.items():
            candidates[column] = value
            oof_pareto[column] = value
            full_pareto[column] = value
            observed_pareto[column] = value

        output_dir = S3_RESULTS_ROOT / "q5"
        candidate_path = output_dir / "observed_candidate_index.csv"
        feature_snapshot_path = output_dir / "q4_feature_snapshot.csv"
        oof_pareto_path = output_dir / "oof_pareto_baseline.csv"
        full_pareto_path = output_dir / "full_fit_reference_pareto.csv"
        observed_pareto_path = output_dir / "observed_loss_pareto_diagnostic.csv"
        heldout_pareto_path = output_dir / "heldout_fold_pareto.csv"
        region_support_path = output_dir / "heldout_fold_region_support.csv"
        conflict_path = output_dir / "oof_full_conflict_diagnostics.csv"
        threshold_path = output_dir / "conflict_thresholds.csv"
        lineage_path = output_dir / "strict_oof_lineage_assertions.csv"
        candidate_lineage_path = output_dir / "candidate_oof_lineage.csv"
        representative_path = output_dir / "representative_conditions.json"
        region_manifest_path = output_dir / "q5_region_manifest.json"
        metrics_path = output_dir / "baseline_metrics.json"
        evidence_metrics_path = run.output_dir / "metrics.json"

        identity_columns = [
            "row_id",
            "source_file",
            "source_file_sha256",
            "source_sheet",
            "source_excel_row",
            "duplicate_row_ids",
            "waveform_sha256",
            "exact_record_sha256",
            "condition_group",
            "regression_outer_fold",
            "oof_model_id",
            "full_model_id",
            "material",
            "temperature_C",
            "frequency_Hz",
            "waveform",
            "b_m_T",
            "energy_proxy_Hz_T",
            *identity_constants,
        ]
        write_csv(candidate_path, candidates[identity_columns])
        snapshot_columns = ["row_id", *Q4_NUMERIC_FEATURES, *Q4_CATEGORICAL_FEATURES, *identity_constants]
        write_csv(feature_snapshot_path, candidates[snapshot_columns])
        pareto_output_columns = [
            *identity_columns,
            "q5_region_id",
            "y_pred_oof",
            "y_pred_full",
            "core_loss_W_per_m3",
            "full_oof_log_gap",
            "oof_absolute_log_residual",
            "full_oof_gap_pass",
            "oof_residual_pass",
            "region_fold_support_pass",
            "prebootstrap_single_point_eligible",
        ]
        write_csv(oof_pareto_path, oof_pareto[pareto_output_columns])
        write_csv(full_pareto_path, full_pareto[pareto_output_columns])
        write_csv(observed_pareto_path, observed_pareto[pareto_output_columns])
        write_csv(heldout_pareto_path, heldout_pareto)
        write_csv(region_support_path, region_support)
        write_csv(
            conflict_path,
            candidates[
                [
                    "row_id",
                    "material",
                    "waveform",
                    "q5_region_id",
                    "y_pred_oof",
                    "y_pred_full",
                    "core_loss_W_per_m3",
                    "full_oof_log_gap",
                    "full_oof_gap_p90",
                    "full_oof_gap_pass",
                    "oof_absolute_log_residual",
                    "oof_residual_p90",
                    "oof_residual_pass",
                    "dual_pareto_pass",
                    "region_fold_support_pass",
                    "prebootstrap_single_point_eligible",
                ]
            ],
        )
        write_csv(threshold_path, pd.DataFrame(gap_rows + residual_rows))
        write_csv(lineage_path, pd.DataFrame(lineage_assertions))
        write_csv(
            candidate_lineage_path,
            candidates[
                [
                    "row_id",
                    "condition_group",
                    "regression_outer_fold",
                    "oof_model_id",
                    "strict_oof_lineage_pass",
                ]
            ].rename(columns={"regression_outer_fold": "oof_fold"}),
        )
        write_json(region_manifest_path, region_metadata)
        representative = {
            "status": "PASS_WITH_S4_STABILITY_PENDING",
            **representatives,
            "unique_recommendation_authorized": False,
            "reason": "S3 Baseline does not execute the contract's 500-resample region stability gate; the knee is provisional.",
            "required_wording": "该实测波形轮廓下的推荐工况",
            "q4_beats_at_least_one_median_reference": q4_capability,
            "strict_oof_lineage_all_pass": bool(row_excluded.all()),
            "oof_full_pareto_intersection_empty": empty_intersection,
            "observed_region_jaccard": jaccard,
            "observed_region_jaccard_case": jaccard_case,
            "observed_region_jaccard_pass": jaccard_pass,
            "bootstrap_completed": False,
            "degenerate_objective_cases": degeneracy,
        }
        write_json(representative_path, representative)
        metrics = {
            "status": "PASS_WITH_S4_STABILITY_PENDING",
            "candidate_definition": "observed_operating_point_v1",
            "candidate_rows_before_exact_duplicate_collapse": int(len(candidates) + len(duplicate_rows)),
            "candidate_rows_after_exact_duplicate_collapse": len(candidates),
            "exact_duplicate_rows_collapsed": len(duplicate_rows),
            "strict_oof_lineage_candidate_pass_count": int(candidates["strict_oof_lineage_pass"].sum()),
            "strict_oof_lineage_candidate_fail_count": int((~candidates["strict_oof_lineage_pass"]).sum()),
            "strict_oof_lineage_training_row_pass_count": int(row_excluded.sum()),
            "strict_oof_lineage_training_row_fail_count": int((~row_excluded).sum()),
            "oof_pareto_points": int(oof_mask.sum()),
            "full_fit_reference_pareto_points": int(full_mask.sum()),
            "observed_loss_pareto_points": int(observed_mask.sum()),
            "dual_pareto_points": int(np.sum(oof_mask & full_mask)),
            "heldout_fold_count": actual_folds,
            "required_region_fold_support": support_required,
            "stable_region_count_before_bootstrap": len(stable_regions),
            "prebootstrap_single_point_eligible_count": int(candidates["prebootstrap_single_point_eligible"].sum()),
            "observed_region_jaccard": jaccard,
            "observed_region_jaccard_pass": jaccard_pass,
            "global_full_oof_gap_p90": global_gap_p90,
            "global_oof_residual_p90": global_residual_p90,
            "q4_beats_at_least_one_median_reference": q4_capability,
            "bootstrap_completed": False,
            "bootstrap_interpretation_if_run_in_s4": "condition-group resampling stability of a fixed cross-fitted candidate table, not full model-parameter uncertainty",
            "contract_hashes": contract_hashes,
            "failure_flags": {
                "q4_capability_failed": not q4_capability,
                "strict_oof_lineage_failed": not bool(row_excluded.all()),
                "oof_full_pareto_intersection_empty": empty_intersection,
                "observed_region_jaccard_failed": not jaccard_pass,
                "pareto_loss_zero_range": degeneracy["pareto_loss_zero_range"],
                "pareto_energy_zero_range": degeneracy["pareto_energy_zero_range"],
            },
        }
        write_json(metrics_path, metrics)
        write_json(evidence_metrics_path, metrics)
        for path in (
            candidate_path,
            feature_snapshot_path,
            oof_pareto_path,
            full_pareto_path,
            observed_pareto_path,
            heldout_pareto_path,
            region_support_path,
            conflict_path,
            threshold_path,
            lineage_path,
            candidate_lineage_path,
            representative_path,
            region_manifest_path,
            metrics_path,
            evidence_metrics_path,
        ):
            run.record_output(path)
        run.log(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
        run.finish("PASS")
    except BaseException as exc:
        run.fail(exc)
        raise


if __name__ == "__main__":
    main()
