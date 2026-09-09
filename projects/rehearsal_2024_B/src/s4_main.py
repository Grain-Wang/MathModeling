"""Run the bounded G3-authorized S4 improvements for Q2 and Q3."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from s1_data_audit import EXPECTED
from s2_contract_validation import group_id
from s3_evaluation import a03_sensitivity, bootstrap, evaluate_q2, evaluate_q3
from s3_features import build_feature_frame, build_feature_schema
from s3_io import (
    dump,
    dump_jsonl,
    environment_metadata,
    now,
    sha256,
)
from s3_lineage import inner_specs_loso, inner_specs_primary
from s3_metrics import classification_metrics, relative_error_metrics
from s3_models import system_records
from s4_io import (
    CONFIG_PATH,
    OUTPUT,
    PROJECT,
    REGISTRY_PATH,
    RunState,
    S4_CONFIG_PATH,
    canonical_relative,
    git,
    load_guarded_training,
    load_json,
    preflight_s4,
)
from s4_selection import (
    grid_records,
    q1_boundary_features,
    q2_fit_predict,
    q3_candidates,
    q3_fit_predict,
    select_q2,
    select_q2_records,
    select_q3,
    select_q3_records,
)

BASELINE = PROJECT / "results" / "raw" / "baseline"
MODEL_IDS_Q2 = {
    "unweighted": "Q2-M1-HGB",
    "weighted": "Q2-M1W-HGB-WEIGHTED",
    "with_q1": "Q2-M1-Q1-ABLATION",
}
MODEL_IDS_Q3 = {
    "unified": "Q3-M1-HGB-UNIFIED",
    "split": "Q3-M1-HGB-APCOUNT",
}


def _read_jsonl_gz(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _boundaries(
    frame: pd.DataFrame, registry: dict[str, Any]
) -> list[dict[str, Any]]:
    groups = group_id(frame).to_numpy()
    primary: dict[tuple[int, int], set[str]] = defaultdict(set)
    for item in registry["outer_assignments"]:
        primary[(int(item["repeat"]), int(item["validation_fold"]))].add(
            f"{item['source_file']}::{int(item['test_id'])}"
        )
    output = []
    for (repeat, fold), validation_groups in sorted(primary.items()):
        valid = np.flatnonzero(np.isin(groups, list(validation_groups)))
        train = np.flatnonzero(~np.isin(groups, list(validation_groups)))
        output.append({
            "key": f"PRIMARY-R{repeat}-F{fold}",
            "context": {
                "stage": "S4", "scope": "PRIMARY",
                "repeat": repeat, "fold": fold,
            },
            "train_index": train,
            "valid_index": valid,
            "inner_specs": inner_specs_primary(registry, repeat, fold),
        })
    for item in sorted(
        registry["leave_one_source_file_out"], key=lambda x: int(x["split"])
    ):
        split = int(item["split"])
        held = str(item["held_out_source_file"])
        mask = frame.source_file.astype(str).eq(held).to_numpy()
        output.append({
            "key": f"LOSO-{split}",
            "context": {
                "stage": "S4", "scope": "LOSO",
                "loso_split": split, "held_out_source_file": held,
            },
            "train_index": np.flatnonzero(~mask),
            "valid_index": np.flatnonzero(mask),
            "inner_specs": inner_specs_loso(registry, split),
        })
    if len(output) != 28:
        raise AssertionError("expected 15 primary and 13 LOSO boundaries")
    return output


def _final_upstream_specs(
    registry: dict[str, Any], context: dict[str, Any]
) -> list[dict[str, Any]]:
    if context["scope"] == "PRIMARY":
        rows = [
            item for item in registry["primary_upstream_lineage_batches"]
            if item["prediction_role"] == "outer_train_oof"
            and int(item["outer_repeat"]) == int(context["repeat"])
            and int(item["outer_fold"]) == int(context["fold"])
        ]
        inference = [
            item for item in registry["primary_upstream_lineage_batches"]
            if item["prediction_role"] == "outer_validation_inference"
            and int(item["outer_repeat"]) == int(context["repeat"])
            and int(item["outer_fold"]) == int(context["fold"])
        ]
    else:
        rows = [
            item for item in registry["loso_upstream_lineage_batches"]
            if item["prediction_role"] == "loso_inner_validation_inference"
            and int(item["loso_split"]) == int(context["loso_split"])
        ]
        inference = [
            item for item in registry["loso_upstream_lineage_batches"]
            if item["prediction_role"] == "loso_validation_inference"
            and int(item["loso_split"]) == int(context["loso_split"])
        ]
    if len(rows) != 3 or len(inference) != 1:
        raise AssertionError(f"final Q1 registry mismatch: {context}")
    return [{
        "validation_groups": set(item["prediction_groups"]),
        "registered_lineage_id": item["lineage_id"],
        "registered_inference_lineage_id": inference[0]["lineage_id"],
    } for item in rows]


def _q2_promotions(
    metrics: dict[str, Any], baseline: dict[str, Any]
) -> dict[str, Any]:
    base = baseline["models"]["Q2-B1A"]
    base_point = base["primary_point_estimate_repeat_mean"]
    base_repeats = {
        int(item["repeat"]): item for item in base["primary_repeat_metrics"]
    }
    result: dict[str, Any] = {
        "baseline_model_id": "Q2-B1A",
        "baseline": base_point,
        "candidates": {},
    }
    eligible = []
    for model_id, value in metrics["models"].items():
        if model_id == MODEL_IDS_Q2["with_q1"]:
            role = "dependency_ablation_not_promotion_candidate"
        else:
            role = "promotion_candidate"
        point = value["primary_point_estimate_repeat_mean"]
        improved = sum(
            item["macro_f1_fixed_17"]
            > base_repeats[int(item["repeat"])]["macro_f1_fixed_17"]
            for item in value["primary_repeat_metrics"]
        )
        checks = {
            "macro_f1_gain_at_least_0_02": (
                point["macro_f1_fixed_17"]
                - base_point["macro_f1_fixed_17"] >= 0.02
            ),
            "at_least_two_repeats_improve": improved >= 2,
            "accuracy_drop_no_more_than_0_01": (
                point["joint_accuracy"]
                >= base_point["joint_accuracy"] - 0.01
            ),
            "eligible_role": role == "promotion_candidate",
        }
        passed = all(checks.values())
        result["candidates"][model_id] = {
            "role": role,
            "primary": point,
            "macro_f1_absolute_gain": (
                point["macro_f1_fixed_17"]
                - base_point["macro_f1_fixed_17"]
            ),
            "accuracy_change": (
                point["joint_accuracy"] - base_point["joint_accuracy"]
            ),
            "improved_repeat_count": improved,
            "checks": checks,
            "promotion_pass": passed,
            "loso": value["loso_overall"],
        }
        if passed:
            eligible.append(model_id)
    result["selected_model_id"] = (
        max(
            eligible,
            key=lambda model: metrics["models"][model][
                "primary_point_estimate_repeat_mean"
            ]["macro_f1_fixed_17"],
        )
        if eligible else "Q2-B1A"
    )
    result["fallback_used"] = not eligible
    return result


def _q3_promotions(
    metrics: dict[str, Any], baseline: dict[str, Any]
) -> dict[str, Any]:
    baseline_id = min(
        ["Q3-B1", "Q3-B2"],
        key=lambda model: baseline["models"][model][
            "primary_point_estimate_repeat_mean"
        ]["selection_score"],
    )
    base = baseline["models"][baseline_id]
    base_point = base["primary_point_estimate_repeat_mean"]
    base_repeats = {
        int(item["repeat"]): item["bounded"]["selection_score"]
        for item in base["primary_repeat_metrics"]
    }
    result: dict[str, Any] = {
        "baseline_model_id": baseline_id,
        "baseline": base_point,
        "candidates": {},
    }
    eligible = []
    for model_id, value in metrics["models"].items():
        point = value["primary_point_estimate_repeat_mean"]
        improved = sum(
            item["bounded"]["selection_score"]
            < base_repeats[int(item["repeat"])]
            for item in value["primary_repeat_metrics"]
        )
        relative_gain = (
            base_point["selection_score"] - point["selection_score"]
        ) / base_point["selection_score"]
        ap_bias_limit = (
            abs(base_point["per_ap"]["median_signed_bias"]) + 0.02
        )
        sys_bias_limit = (
            abs(base_point["system_sum"]["median_signed_bias"]) + 0.02
        )
        checks = {
            "relative_score_gain_at_least_5_percent": relative_gain >= 0.05,
            "at_least_two_repeats_improve": improved >= 2,
            "per_ap_bias_guard": (
                abs(point["per_ap"]["median_signed_bias"]) <= ap_bias_limit
            ),
            "system_bias_guard": (
                abs(point["system_sum"]["median_signed_bias"]) <= sys_bias_limit
            ),
        }
        passed = all(checks.values())
        result["candidates"][model_id] = {
            "primary": point,
            "relative_selection_score_gain": relative_gain,
            "improved_repeat_count": improved,
            "bias_limits": {"per_ap": ap_bias_limit, "system": sys_bias_limit},
            "checks": checks,
            "promotion_pass": passed,
            "loso": value["loso_overall"],
        }
        if passed:
            eligible.append(model_id)
    result["selected_model_id"] = (
        min(
            eligible,
            key=lambda model: metrics["models"][model][
                "primary_point_estimate_repeat_mean"
            ]["selection_score"],
        )
        if eligible else baseline_id
    )
    result["fallback_used"] = not eligible
    return result


def _stratified(
    q2_rows: list[dict[str, Any]],
    q3_rows: list[dict[str, Any]],
    labels: list[str],
) -> dict[str, Any]:
    q2, q3 = pd.DataFrame(q2_rows), pd.DataFrame(q3_rows)
    q2 = q2[q2.scope.eq("PRIMARY")]
    q3 = q3[q3.scope.eq("PRIMARY")]
    result: dict[str, Any] = {"q2": {}, "q3": {}}
    for field in ["ap_count", "loc_id", "nav", "protocol"]:
        result["q2"][field] = [{
            "model_id": model,
            "repeat": int(repeat),
            "level": str(level),
            **classification_metrics(
                part.truth_joint_label.to_numpy(str),
                part.predicted_joint_label.to_numpy(str),
                np.vstack(part.probability_fixed_17),
                labels,
            ),
        } for (model, repeat, level), part in q2.groupby(
            ["model_id", "repeat", field]
        )]
        result["q3"][field] = [{
            "model_id": model,
            "repeat": int(repeat),
            "level": str(level),
            **relative_error_metrics(
                part.truth_throughput.to_numpy(float),
                part.throughput_bounded.to_numpy(float),
            ),
        } for (model, repeat, level), part in q3.groupby(
            ["model_id", "repeat", field]
        )]
    return result


def _failure_cases(
    q2_rows: list[dict[str, Any]],
    q3_rows: list[dict[str, Any]],
    systems: list[dict[str, Any]],
    q2_metrics: dict[str, Any],
    q3_metrics: dict[str, Any],
) -> dict[str, Any]:
    q2_model = max(
        q2_metrics["models"],
        key=lambda model: q2_metrics["models"][model][
            "primary_point_estimate_repeat_mean"
        ]["macro_f1_fixed_17"],
    )
    q3_model = min(
        q3_metrics["models"],
        key=lambda model: q3_metrics["models"][model][
            "primary_point_estimate_repeat_mean"
        ]["selection_score"],
    )
    q2 = pd.DataFrame(q2_rows)
    q2 = q2[q2.scope.eq("PRIMARY") & q2.model_id.eq(q2_model)].copy()
    q2["true_probability"] = q2.apply(
        lambda row: row.probability_fixed_17[
            row.probability_label_order.index(row.truth_joint_label)
        ], axis=1,
    )
    q2["row_log_loss"] = -np.log(np.clip(q2.true_probability, 1e-15, 1.0))
    q3 = pd.DataFrame(q3_rows)
    q3 = q3[q3.scope.eq("PRIMARY") & q3.model_id.eq(q3_model)].copy()
    q3 = q3[q3.truth_throughput.ne(0)]
    q3["absolute_relative_error"] = np.abs(
        (q3.throughput_bounded - q3.truth_throughput) / q3.truth_throughput
    )
    system = pd.DataFrame(systems)
    system = system[
        system.scope.eq("PRIMARY") & system.model_id.eq(q3_model)
    ].copy()
    system["absolute_relative_error"] = np.abs(
        (system.system_throughput_bounded - system.truth_system_throughput)
        / system.truth_system_throughput
    )
    q2_fields = [
        "row_key", "group_id", "source_file", "test_id", "ap_id",
        "repeat", "truth_joint_label", "predicted_joint_label",
        "true_probability", "row_log_loss", "ap_count", "nav", "protocol",
    ]
    q3_fields = [
        "row_key", "group_id", "source_file", "test_id", "ap_id",
        "repeat", "truth_throughput", "throughput_bounded",
        "absolute_relative_error", "ap_count", "nav", "protocol",
    ]
    sys_fields = [
        "group_id", "source_file", "test_id", "repeat",
        "truth_system_throughput", "system_throughput_bounded",
        "absolute_relative_error", "ap_count",
    ]
    return {
        "selection_role": "diagnostic_only_no_new_candidate_authorization",
        "q2_model_id": q2_model,
        "q2_highest_log_loss_rows": q2.nlargest(20, "row_log_loss")[
            q2_fields
        ].to_dict("records"),
        "q3_model_id": q3_model,
        "q3_highest_ap_relative_error_rows": q3.nlargest(
            20, "absolute_relative_error"
        )[q3_fields].to_dict("records"),
        "q3_highest_system_relative_error_groups": system.nlargest(
            20, "absolute_relative_error"
        )[sys_fields].to_dict("records"),
    }


def _schema(
    features: pd.DataFrame,
    frame: pd.DataFrame,
    baseline_schema_path: Path,
) -> dict[str, Any]:
    base = build_feature_schema(features)
    two = frame[
        frame.source_file.map(lambda x: EXPECTED[str(x)]["ap_count"] == 2)
    ]
    three = frame[
        frame.source_file.map(lambda x: EXPECTED[str(x)]["ap_count"] == 3)
    ]
    two_columns = list(build_feature_frame(two).columns)
    three_columns = list(build_feature_frame(three).columns)
    base["ap_count_alignment"] = {
        "two_ap_column_count": len(two_columns),
        "three_ap_column_count": len(three_columns),
        "same_order": two_columns == three_columns == list(features.columns),
    }
    if not base["ap_count_alignment"]["same_order"]:
        raise AssertionError("S4 2-AP and 3-AP feature schemas do not align")
    baseline_sha = sha256(baseline_schema_path)
    baseline_payload = load_json(baseline_schema_path)
    if base != baseline_payload:
        raise AssertionError("actual S4 base feature schema differs from S3")
    generated_text = json.dumps(
        base, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"
    generated_sha = hashlib.sha256(
        generated_text.encode("utf-8")
    ).hexdigest().upper()
    additions = [
        {"name": "upstream__q1_seq_time_bounded", "dtype": "float64", "unit": "s"},
        {"name": "physical__actual_nss", "dtype": "float64", "unit": "count"},
        {"name": "physical__actual_mcs", "dtype": "float64", "unit": "index"},
        {"name": "physical__phy_rate_mbps", "dtype": "float64", "unit": "Mbps"},
        {"name": "physical__q1_air_fraction", "dtype": "float64", "unit": "dimensionless"},
        {"name": "physical__proxy_mbps", "dtype": "float64", "unit": "Mbps"},
        {"name": "physical__rate_missing", "dtype": "float64", "unit": "indicator"},
    ]
    return {
        "schema_version": "s4_feature_schema_v1",
        "base_feature_schema_sha256": baseline_sha,
        "recomputed_base_feature_schema_normalized_sha256": generated_sha,
        "recomputed_base_feature_schema_matches": True,
        "base_feature_count": base["raw_feature_count"],
        "q2_feature_count": base["raw_feature_count"],
        "q2_with_q1_ablation_feature_count": base["raw_feature_count"] + 1,
        "q3_feature_count": base["raw_feature_count"] + len(additions),
        "ap_count_representation": (
            "basic__ap_count is numeric binary (2 or 3), shared by every S4 candidate"
        ),
        "q3_additional_features": [
            {
                **item,
                "missing_semantics": (
                    "NaN denotes undefined PHY rate and is paired with rate_missing"
                    if item["name"] in {
                        "physical__phy_rate_mbps", "physical__proxy_mbps"
                    }
                    else "not missing after guarded feature construction"
                ),
                "column_order": base["raw_feature_count"] + index,
            }
            for index, item in enumerate(additions)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--bootstrap-replicates", type=int, default=1000)
    args = parser.parse_args()
    started, timer = now(), time.perf_counter()
    state = RunState()
    status_before_outputs = git("status", "--short")
    config = load_json(CONFIG_PATH)
    s4_config = load_json(S4_CONFIG_PATH)
    registry = load_json(REGISTRY_PATH)
    paths, preflight, core_sha = preflight_s4(
        config, s4_config, registry, state
    )
    if args.verify_only:
        print("status=PASS")
        print("mode=verify-only")
        print("model_fit_count=0")
        print("csv_numeric_read_count=0")
        print("official_test_numeric_read_count=0")
        return 0

    frame = load_guarded_training(paths, state)
    features = build_feature_frame(frame)
    schema = _schema(features, frame, BASELINE / "feature_schema.json")
    boundaries = _boundaries(frame, registry)
    labels = list(config["q2"]["global_joint_labels"])
    common = dict(s4_config["hgb_common"])
    q2_candidates = grid_records(s4_config, "Q2")
    q3_grid = q3_candidates(s4_config)

    q2_rows: list[dict[str, Any]] = []
    q3_rows: list[dict[str, Any]] = []
    q2_trace: list[dict[str, Any]] = []
    q3_trace: list[dict[str, Any]] = []
    q2_summaries: list[dict[str, Any]] = []
    q3_summaries: list[dict[str, Any]] = []
    q2_fold_status: list[dict[str, Any]] = []
    q3_fold_status: list[dict[str, Any]] = []
    selected_q2: dict[str, dict[str, Any]] = {}
    selected_q3: dict[str, dict[str, Any]] = {}

    print("phase=Q2_unweighted_selection", flush=True)
    for number, boundary in enumerate(boundaries, start=1):
        selected, trace, summaries = select_q2(
            features,
            frame,
            boundary["train_index"],
            boundary["inner_specs"],
            labels,
            q2_candidates,
            common,
            boundary["context"],
            state,
        )
        selected_q2[boundary["key"]] = selected
        q2_trace.extend(trace)
        q2_summaries.append({
            **boundary["context"],
            "selected_config_id": selected["config_id"],
            "candidate_summaries": summaries,
        })
        q2_fold_status.append(q2_fit_predict(
            features,
            frame,
            boundary["train_index"],
            boundary["valid_index"],
            labels,
            selected,
            common,
            boundary["context"],
            state,
            q2_rows,
            MODEL_IDS_Q2["unweighted"],
        ))
        print(f"Q2_boundary={number}/28", flush=True)

    q2_unweighted = evaluate_q2(q2_rows, labels)
    collapsed = q2_unweighted["models"][MODEL_IDS_Q2["unweighted"]][
        "minority_collapse_by_repeat"
    ]
    weighting_triggered = any(bool(value) for value in collapsed.values())
    if not weighting_triggered:
        print("Q2_weighting=SKIPPED_NO_COLLAPSE", flush=True)
    else:
        print("Q2_weighting=TRIGGERED", flush=True)

    print("phase=Q1_final_boundaries_and_Q2_conditions", flush=True)
    q1_cache: dict[str, dict[str, Any]] = {}
    lineages: list[dict[str, Any]] = []
    for number, boundary in enumerate(boundaries, start=1):
        context = boundary["context"]
        roles = (
            ("outer_train_oof", "outer_validation_inference")
            if context["scope"] == "PRIMARY"
            else ("loso_train_oof", "loso_validation_inference")
        )
        q1_train, q1_valid, actual = q1_boundary_features(
            features,
            frame,
            boundary["train_index"],
            boundary["valid_index"],
            _final_upstream_specs(registry, context),
            context,
            roles,
            state,
        )
        lineages.extend(actual)
        q1_cache[boundary["key"]] = {
            "train": q1_train,
            "valid": q1_valid,
            "validation_lineage_id": actual[-1]["lineage_id"],
        }
        selected = selected_q2[boundary["key"]]
        if weighting_triggered:
            q2_fold_status.append(q2_fit_predict(
                features,
                frame,
                boundary["train_index"],
                boundary["valid_index"],
                labels,
                selected,
                common,
                context,
                state,
                q2_rows,
                MODEL_IDS_Q2["weighted"],
                weighted=True,
            ))
        q2_fold_status.append(q2_fit_predict(
            features,
            frame,
            boundary["train_index"],
            boundary["valid_index"],
            labels,
            selected,
            common,
            context,
            state,
            q2_rows,
            MODEL_IDS_Q2["with_q1"],
            q1_train=q1_train,
            q1_valid=q1_valid,
            lineage_id=actual[-1]["lineage_id"],
        ))
        print(f"Q1_Q2_boundary={number}/28", flush=True)

    print("phase=Q3_nested_selection_and_AP_count_comparison", flush=True)
    for number, boundary in enumerate(boundaries, start=1):
        selected, trace, summaries, nested_lineage = select_q3(
            features,
            frame,
            boundary["train_index"],
            boundary["inner_specs"],
            registry,
            q3_grid,
            common,
            boundary["context"],
            state,
        )
        lineages.extend(nested_lineage)
        selected_q3[boundary["key"]] = selected
        q3_trace.extend(trace)
        q3_summaries.append({
            **boundary["context"],
            "selected_candidate_id": selected["candidate_id"],
            "candidate_summaries": summaries,
        })
        cache = q1_cache[boundary["key"]]
        q3_fold_status.append(q3_fit_predict(
            features,
            frame,
            boundary["train_index"],
            boundary["valid_index"],
            cache["train"],
            cache["valid"],
            selected,
            common,
            boundary["context"],
            state,
            q3_rows,
            MODEL_IDS_Q3["unified"],
            cache["validation_lineage_id"],
            split_by_ap_count=False,
        ))
        q3_fold_status.append(q3_fit_predict(
            features,
            frame,
            boundary["train_index"],
            boundary["valid_index"],
            cache["train"],
            cache["valid"],
            selected,
            common,
            boundary["context"],
            state,
            q3_rows,
            MODEL_IDS_Q3["split"],
            cache["validation_lineage_id"],
            split_by_ap_count=True,
        ))
        print(f"Q3_boundary={number}/28", flush=True)

    systems = system_records(q3_rows)
    q2_metrics = evaluate_q2(q2_rows, labels)
    q3_metrics, q3_cdf = evaluate_q3(q3_rows, systems)
    baseline_q2 = load_json(BASELINE / "q2_metrics.json")
    baseline_q3 = load_json(BASELINE / "q3_metrics.json")
    promotions = {
        "q2": _q2_promotions(q2_metrics, baseline_q2),
        "q3": _q3_promotions(q3_metrics, baseline_q3),
    }
    global_q2, global_q2_summaries = select_q2_records([
        x for x in q2_trace if x["scope"] == "PRIMARY"
    ])
    global_q3, global_q3_summaries = select_q3_records([
        x for x in q3_trace if x["scope"] == "PRIMARY"
    ])
    final_candidate = {
        "selection_closed_for_g4_submission": True,
        "test_data_used": False,
        "q1": {
            "model_id": "Q1-B1",
            "estimator": "Ridge",
            "parameters": {"alpha": 1.0, "solver": "lsqr"},
            "prediction_variant": "seq_time_bounded",
            "postprocess_version": "q1_clip_0_test_dur_v1",
        },
        "q2": {
            "model_id": promotions["q2"]["selected_model_id"],
            "promotion": promotions["q2"],
            "full_data_configuration": (
                {
                    **global_q2,
                    "weighted": promotions["q2"]["selected_model_id"]
                    == MODEL_IDS_Q2["weighted"],
                    "uses_q1": False,
                }
                if not promotions["q2"]["fallback_used"]
                else {
                    "estimator": "LogisticRegression",
                    "C": 1.0,
                    "class_weight": None,
                    "uses_q1": False,
                }
            ),
        },
        "q3": {
            "model_id": promotions["q3"]["selected_model_id"],
            "promotion": promotions["q3"],
            "full_data_configuration": (
                {
                    **global_q3,
                    "ap_count_split": promotions["q3"]["selected_model_id"]
                    == MODEL_IDS_Q3["split"],
                }
                if not promotions["q3"]["fallback_used"]
                else {
                    "estimator": "Ridge",
                    "alpha": 1.0,
                    "solver": "lsqr",
                    "uses_q1": True,
                }
            ),
        },
        "unique_configuration_rule": s4_config[
            "final_full_data_configuration_rule"
        ],
    }
    baseline_q1_rows = _read_jsonl_gz(BASELINE / "q1_oof_predictions.jsonl.gz")
    uncertainty = bootstrap(
        baseline_q1_rows,
        q2_rows,
        q3_rows,
        systems,
        labels,
        args.bootstrap_replicates,
        int(s4_config["bootstrap"]["random_state"]),
    )
    uncertainty = {"contract": uncertainty["contract"], "q2": uncertainty["q2"], "q3": uncertainty["q3"]}
    stratified = _stratified(q2_rows, q3_rows, labels)
    a03 = a03_sensitivity(q2_rows, q3_rows, systems, labels)
    failures = _failure_cases(q2_rows, q3_rows, systems, q2_metrics, q3_metrics)
    lineage_assertions = {
        "batch_count": len(lineages),
        "primary_batch_count": sum(x["scope"] == "PRIMARY" for x in lineages),
        "loso_batch_count": sum(x["scope"] == "LOSO" for x in lineages),
        "prediction_fit_overlap_total": sum(
            x["prediction_fit_overlap_count"] for x in lineages
        ),
        "downstream_validation_fit_overlap_total": sum(
            x["downstream_validation_fit_overlap_count"] for x in lineages
        ),
        "fixed_upstream_identity": all(
            x["upstream_model_id"] == "Q1-B1"
            and x["prediction_variant"] == "seq_time_bounded"
            and x["postprocess_version"] == "q1_clip_0_test_dur_v1"
            for x in lineages
        ),
    }
    expected_lineage = {
        "batch_count": 448,
        "primary_batch_count": 240,
        "loso_batch_count": 208,
        "prediction_fit_overlap_total": 0,
        "downstream_validation_fit_overlap_total": 0,
        "fixed_upstream_identity": True,
    }
    if lineage_assertions != expected_lineage:
        raise AssertionError(f"S4 lineage mismatch: {lineage_assertions}")
    if state.warnings:
        raise RuntimeError(f"S4 fit warnings are not allowed: {state.warnings[:3]}")

    dump(OUTPUT / "s4_feature_schema.json", schema)
    dump_jsonl(OUTPUT / "q2_oof_predictions.jsonl.gz", q2_rows)
    dump_jsonl(OUTPUT / "q3_ap_oof_predictions.jsonl.gz", q3_rows)
    dump_jsonl(OUTPUT / "q3_system_oof_predictions.jsonl.gz", systems)
    dump(OUTPUT / "q1_actual_upstream_lineage.json", {
        "assertions": lineage_assertions,
        "batches": lineages,
    })
    dump(OUTPUT / "q2_selection.json", {
        "candidate_budget": 4,
        "weighting_triggered": weighting_triggered,
        "unweighted_collapse": collapsed,
        "per_boundary": q2_summaries,
        "inner_trace": q2_trace,
        "global_full_data_selection": global_q2,
        "global_candidate_summaries": global_q2_summaries,
    })
    dump(OUTPUT / "q3_selection.json", {
        "candidate_budget": 8,
        "ap_count_split_comparisons": 1,
        "per_boundary": q3_summaries,
        "inner_trace": q3_trace,
        "global_full_data_selection": global_q3,
        "global_candidate_summaries": global_q3_summaries,
    })
    dump(OUTPUT / "q2_candidate_metrics.json", q2_metrics)
    dump(OUTPUT / "q3_candidate_metrics.json", q3_metrics)
    dump(OUTPUT / "q3_error_cdf.json", q3_cdf)
    dump(OUTPUT / "promotion_decision.json", promotions)
    dump(OUTPUT / "final_candidate.json", final_candidate)
    dump(OUTPUT / "group_bootstrap_intervals.json", uncertainty)
    dump(OUTPUT / "stratified_metrics.json", stratified)
    dump(OUTPUT / "a03_evaluation_exclusion.json", a03)
    dump(OUTPUT / "failure_cases.json", failures)
    dump(OUTPUT / "fold_status.json", {
        "q2": q2_fold_status, "q3": q3_fold_status
    })

    metadata = {
        "status": "PASS",
        "started_at": started,
        "finished_at": now(),
        "runtime_seconds": float(time.perf_counter() - timer),
        "git_head": git("rev-parse", "HEAD"),
        "git_status_before_outputs": status_before_outputs,
        **environment_metadata(),
        "config_sha256": sha256(CONFIG_PATH),
        "s4_config_sha256": sha256(S4_CONFIG_PATH),
        "split_registry_sha256": sha256(REGISTRY_PATH),
        "split_registry_core_sha256": core_sha,
        "base_feature_schema_sha256": sha256(BASELINE / "feature_schema.json"),
        "s4_feature_schema_sha256": sha256(OUTPUT / "s4_feature_schema.json"),
        "eligible_rows": len(frame),
        "eligible_groups": int(group_id(frame).nunique()),
        "outer_fold_count": 15,
        "loso_split_count": 13,
        "q2_grid_count": 4,
        "q3_candidate_count": 8,
        "q2_weighting_triggered": weighting_triggered,
        "q2_weighting_formula_count": 1 if weighting_triggered else 0,
        "q3_ap_count_split_comparison_count": 1,
        "model_fit_count": state.model_fit_count,
        "training_csv_numeric_read_count": state.csv_numeric_read_count,
        "official_test_hash_only_count": 4,
        "official_test_numeric_read_count": 0,
        "official_test_prediction_count": 0,
        "actual_lineage_assertions": lineage_assertions,
        "warning_count": len(state.warnings),
        "warnings": state.warnings,
        "ap_count_representation": s4_config["ap_count_representation"],
        "a03_analysis_type": s4_config["a03_sensitivity"],
    }
    dump(OUTPUT / "main_summary.json", {
        "status": "PASS",
        "metadata": metadata,
        "q2": q2_metrics,
        "q3": q3_metrics,
        "promotions": promotions,
        "final_candidate": final_candidate,
    })
    dump(OUTPUT / "run_manifest.json", {
        **metadata,
        "preflight": preflight,
        "phase_input_manifest": preflight["entry"],
        "output_artifacts": [
            {
                "path": canonical_relative(path),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in sorted(OUTPUT.glob("*"))
            if path.is_file()
            and path.name not in {
                "run_manifest.json",
                "post_run_validation.json",
                "validation_manifest.json",
            }
        ],
    })
    print("status=PASS")
    print(f"eligible_rows={len(frame)}")
    print("outer_folds=15")
    print("loso_splits=13")
    print("q2_grid=4")
    print("q3_candidates=8")
    print(f"q2_weighting_triggered={weighting_triggered}")
    print("q3_ap_count_split_comparisons=1")
    print(f"actual_lineage_batches={len(lineages)}")
    print(f"model_fit_count={state.model_fit_count}")
    print("official_test_numeric_read_count=0")
    print("official_test_prediction_count=0")
    print(f"runtime_seconds={metadata['runtime_seconds']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
