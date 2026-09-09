"""Aggregate S3 Baseline metrics without refitting models."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from s3_metrics import (
    classification_metrics,
    fixed_confusion,
    percentile_interval,
    regression_metrics,
    relative_error_metrics,
)


def _mean(rows: list[dict[str, Any]], fields: list[str]) -> dict[str, float]:
    return {
        field: float(np.mean([float(row[field]) for row in rows]))
        for field in fields
    }


def evaluate_q1(rows: list[dict[str, Any]]) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    primary, loso = frame[frame.scope.eq("PRIMARY")], frame[frame.scope.eq("LOSO")]
    result: dict[str, Any] = {"models": {}}
    for model in sorted(frame.model_id.unique()):
        repeats, folds = [], []
        model_primary = primary[primary.model_id.eq(model)]
        for repeat, part in model_primary.groupby("repeat"):
            repeats.append({
                "repeat": int(repeat),
                "raw": regression_metrics(
                    part.truth_seq_time.to_numpy(float),
                    part.seq_time_raw.to_numpy(float),
                ),
                "bounded": regression_metrics(
                    part.truth_seq_time.to_numpy(float),
                    part.seq_time_bounded.to_numpy(float),
                ),
                "clip_fraction": float(part.clipped.mean()),
            })
        for (repeat, fold), part in model_primary.groupby(["repeat", "fold"]):
            folds.append({
                "repeat": int(repeat), "fold": int(fold),
                "bounded": regression_metrics(
                    part.truth_seq_time.to_numpy(float),
                    part.seq_time_bounded.to_numpy(float),
                ),
            })
        model_loso = loso[loso.model_id.eq(model)]
        by_source = [{
            "held_out_source_file": source,
            **regression_metrics(
                part.truth_seq_time.to_numpy(float),
                part.seq_time_bounded.to_numpy(float),
            ),
        } for source, part in model_loso.groupby("held_out_source_file")]
        result["models"][model] = {
            "primary_repeat_metrics": repeats,
            "primary_point_estimate_repeat_mean": {
                "raw": _mean([x["raw"] for x in repeats], ["mae", "rmse", "r2"]),
                "bounded": _mean(
                    [x["bounded"] for x in repeats], ["mae", "rmse", "r2"]
                ),
                "clip_fraction": float(np.mean([x["clip_fraction"] for x in repeats])),
            },
            "primary_fold_metrics": folds,
            "primary_fold_mae_std": float(np.std(
                [x["bounded"]["mae"] for x in folds], ddof=1
            )),
            "primary_repeat_mae_std": float(np.std(
                [x["bounded"]["mae"] for x in repeats], ddof=1
            )),
            "loso_overall": regression_metrics(
                model_loso.truth_seq_time.to_numpy(float),
                model_loso.seq_time_bounded.to_numpy(float),
            ),
            "loso_by_source": by_source,
        }
    return result


def evaluate_q2(
    rows: list[dict[str, Any]], labels: list[str],
) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    primary, loso = frame[frame.scope.eq("PRIMARY")], frame[frame.scope.eq("LOSO")]
    result: dict[str, Any] = {"fixed_label_order": labels, "models": {}}
    fields = [
        "macro_f1_fixed_17", "joint_accuracy", "balanced_accuracy",
        "nss_accuracy", "mcs_accuracy", "multiclass_log_loss",
    ]
    for model in sorted(frame.model_id.unique()):
        repeats, confusions = [], []
        model_primary = primary[primary.model_id.eq(model)]
        for repeat, part in model_primary.groupby("repeat"):
            metric = classification_metrics(
                part.truth_joint_label.to_numpy(str),
                part.predicted_joint_label.to_numpy(str),
                np.vstack(part.probability_fixed_17), labels,
            )
            repeats.append({"repeat": int(repeat), **metric})
            confusions.append({
                "repeat": int(repeat),
                **fixed_confusion(
                    part.truth_joint_label.to_numpy(str),
                    part.predicted_joint_label.to_numpy(str), labels,
                ),
            })
        model_loso = loso[loso.model_id.eq(model)]
        by_source = [{
            "held_out_source_file": source,
            **classification_metrics(
                part.truth_joint_label.to_numpy(str),
                part.predicted_joint_label.to_numpy(str),
                np.vstack(part.probability_fixed_17), labels,
            ),
        } for source, part in model_loso.groupby("held_out_source_file")]
        collapsed = {
            str(x["repeat"]): [
                label for label in labels
                if x["true_class_support"][label] > 0
                and x["predicted_class_support"][label] == 0
            ] for x in repeats
        }
        result["models"][model] = {
            "primary_repeat_metrics": repeats,
            "primary_point_estimate_repeat_mean": _mean(repeats, fields),
            "primary_repeat_macro_f1_std": float(np.std(
                [x["macro_f1_fixed_17"] for x in repeats], ddof=1
            )),
            "primary_confusion_matrices": confusions,
            "minority_collapse_by_repeat": collapsed,
            "loso_overall": classification_metrics(
                model_loso.truth_joint_label.to_numpy(str),
                model_loso.predicted_joint_label.to_numpy(str),
                np.vstack(model_loso.probability_fixed_17), labels,
            ),
            "loso_by_source": by_source,
        }
    return result


def evaluate_q3(
    ap_rows: list[dict[str, Any]], system_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    ap, system = pd.DataFrame(ap_rows), pd.DataFrame(system_rows)
    result: dict[str, Any] = {"models": {}}
    cdf: dict[str, Any] = {"models": {}}
    level_fields = [
        "mae", "rmse", "r2", "signed_error_90", "accuracy_90",
        "absolute_relative_error_90", "median_signed_bias",
    ]
    for model in sorted(ap.model_id.unique()):
        repeats, cdf_rows = [], []
        model_ap = ap[ap.scope.eq("PRIMARY") & ap.model_id.eq(model)]
        model_system = system[
            system.scope.eq("PRIMARY") & system.model_id.eq(model)
        ]
        for repeat, ap_part in model_ap.groupby("repeat"):
            sys_part = model_system[model_system.repeat.eq(repeat)]
            ap_main = relative_error_metrics(
                ap_part.truth_throughput.to_numpy(float),
                ap_part.throughput_bounded.to_numpy(float),
            )
            sys_main = relative_error_metrics(
                sys_part.truth_system_throughput.to_numpy(float),
                sys_part.system_throughput_bounded.to_numpy(float),
            )
            repeats.append({
                "repeat": int(repeat),
                "bounded": {
                    "per_ap": ap_main, "system_sum": sys_main,
                    "selection_score": max(
                        ap_main["absolute_relative_error_90"],
                        sys_main["absolute_relative_error_90"],
                    ),
                },
                "raw_audit": {
                    "per_ap": relative_error_metrics(
                        ap_part.truth_throughput.to_numpy(float),
                        ap_part.throughput_raw.to_numpy(float),
                    ),
                    "system_sum": relative_error_metrics(
                        sys_part.truth_system_throughput.to_numpy(float),
                        sys_part.system_throughput_raw.to_numpy(float),
                    ),
                },
                "negative_ap_clip_fraction": float(ap_part.negative_clipped.mean()),
            })
            cdf_rows.append({
                "repeat": int(repeat),
                "per_ap": relative_error_metrics(
                    ap_part.truth_throughput.to_numpy(float),
                    ap_part.throughput_bounded.to_numpy(float), include_cdf=True,
                ),
                "system_sum": relative_error_metrics(
                    sys_part.truth_system_throughput.to_numpy(float),
                    sys_part.system_throughput_bounded.to_numpy(float),
                    include_cdf=True,
                ),
            })
        loso_ap = ap[ap.scope.eq("LOSO") & ap.model_id.eq(model)]
        loso_sys = system[
            system.scope.eq("LOSO") & system.model_id.eq(model)
        ]
        loso_ap_metric = relative_error_metrics(
            loso_ap.truth_throughput.to_numpy(float),
            loso_ap.throughput_bounded.to_numpy(float),
        )
        loso_sys_metric = relative_error_metrics(
            loso_sys.truth_system_throughput.to_numpy(float),
            loso_sys.system_throughput_bounded.to_numpy(float),
        )
        by_source = []
        for source, ap_part in loso_ap.groupby("held_out_source_file"):
            sys_part = loso_sys[loso_sys.held_out_source_file.eq(source)]
            ap_metric = relative_error_metrics(
                ap_part.truth_throughput.to_numpy(float),
                ap_part.throughput_bounded.to_numpy(float),
            )
            sys_metric = relative_error_metrics(
                sys_part.truth_system_throughput.to_numpy(float),
                sys_part.system_throughput_bounded.to_numpy(float),
            )
            by_source.append({
                "held_out_source_file": source,
                "per_ap": ap_metric, "system_sum": sys_metric,
                "selection_score": max(
                    ap_metric["absolute_relative_error_90"],
                    sys_metric["absolute_relative_error_90"],
                ),
            })
        result["models"][model] = {
            "primary_repeat_metrics": repeats,
            "primary_point_estimate_repeat_mean": {
                "selection_score": float(np.mean([
                    x["bounded"]["selection_score"] for x in repeats
                ])),
                "per_ap": _mean(
                    [x["bounded"]["per_ap"] for x in repeats], level_fields
                ),
                "system_sum": _mean(
                    [x["bounded"]["system_sum"] for x in repeats], level_fields
                ),
                "negative_ap_clip_fraction": float(np.mean([
                    x["negative_ap_clip_fraction"] for x in repeats
                ])),
            },
            "primary_repeat_selection_score_std": float(np.std([
                x["bounded"]["selection_score"] for x in repeats
            ], ddof=1)),
            "loso_overall": {
                "per_ap": loso_ap_metric, "system_sum": loso_sys_metric,
                "selection_score": max(
                    loso_ap_metric["absolute_relative_error_90"],
                    loso_sys_metric["absolute_relative_error_90"],
                ),
            },
            "loso_by_source": by_source,
        }
        cdf["models"][model] = cdf_rows
    return result, cdf


def _weighted_rank(
    values: np.ndarray, weights: np.ndarray, quantile: float,
) -> float:
    order = np.argsort(values)
    target = math.ceil(quantile * float(weights.sum()))
    position = int(np.searchsorted(
        np.cumsum(weights[order]), target, side="left"
    ))
    return float(values[order[min(position, len(order) - 1)]])


def bootstrap(
    q1_rows: list[dict[str, Any]], q2_rows: list[dict[str, Any]],
    q3_rows: list[dict[str, Any]], system_rows: list[dict[str, Any]],
    labels: list[str], replicates: int, seed: int,
) -> dict[str, Any]:
    q1, q2 = pd.DataFrame(q1_rows), pd.DataFrame(q2_rows)
    q3, system = pd.DataFrame(q3_rows), pd.DataFrame(system_rows)
    q1, q2 = q1[q1.scope.eq("PRIMARY")], q2[q2.scope.eq("PRIMARY")]
    q3, system = q3[q3.scope.eq("PRIMARY")], system[system.scope.eq("PRIMARY")]
    groups = sorted(q1.group_id.unique())
    group_index = {group: i for i, group in enumerate(groups)}
    rng = np.random.default_rng(seed)
    counts = np.asarray([
        np.bincount(
            rng.integers(0, len(groups), len(groups)), minlength=len(groups)
        )
        for _ in range(replicates)
    ])
    result: dict[str, Any] = {
        "contract": {
            "resampling_unit": "original source_file+test_id group",
            "replicates": replicates, "seed": seed,
            "three_repeat_predictions_kept_together": True,
        },
        "q1": {}, "q2": {}, "q3": {},
    }
    for model, model_frame in q1.groupby("model_id"):
        values = []
        for count in counts:
            per_repeat = []
            for _, part in model_frame.groupby("repeat"):
                weights = part.group_id.map(
                    lambda x: count[group_index[x]]
                ).to_numpy(float)
                errors = np.abs(
                    part.seq_time_bounded.to_numpy(float)
                    - part.truth_seq_time.to_numpy(float)
                )
                per_repeat.append(float(np.average(errors, weights=weights)))
            values.append(float(np.mean(per_repeat)))
        result["q1"][model] = {"bounded_mae": percentile_interval(values)}

    for model, model_frame in q2.groupby("model_id"):
        f1_values, accuracy_values = [], []
        for count in counts:
            per_f1, per_accuracy = [], []
            for _, part in model_frame.groupby("repeat"):
                weights = part.group_id.map(
                    lambda x: count[group_index[x]]
                ).to_numpy(float)
                truth = part.truth_joint_label.to_numpy(str)
                predicted = part.predicted_joint_label.to_numpy(str)
                per_f1.append(float(f1_score(
                    truth, predicted, labels=labels, average="macro",
                    zero_division=0, sample_weight=weights,
                )))
                per_accuracy.append(float(np.average(
                    truth == predicted, weights=weights
                )))
            f1_values.append(float(np.mean(per_f1)))
            accuracy_values.append(float(np.mean(per_accuracy)))
        result["q2"][model] = {
            "macro_f1_fixed_17": percentile_interval(f1_values),
            "joint_accuracy": percentile_interval(accuracy_values),
        }

    for model, model_ap in q3.groupby("model_id"):
        model_system = system[system.model_id.eq(model)]
        score_values, ap_values, sys_values = [], [], []
        for count in counts:
            per_score, per_ap, per_sys = [], [], []
            for repeat, ap_part in model_ap.groupby("repeat"):
                sys_part = model_system[model_system.repeat.eq(repeat)]
                ap_weights = ap_part.group_id.map(
                    lambda x: count[group_index[x]]
                ).to_numpy(int)
                sys_weights = sys_part.group_id.map(
                    lambda x: count[group_index[x]]
                ).to_numpy(int)
                truth = ap_part.truth_throughput.to_numpy(float)
                predicted = ap_part.throughput_bounded.to_numpy(float)
                nonzero = truth != 0
                ap90 = _weighted_rank(
                    np.abs((predicted[nonzero] - truth[nonzero]) / truth[nonzero]),
                    ap_weights[nonzero], 0.90,
                )
                truth_sys = sys_part.truth_system_throughput.to_numpy(float)
                pred_sys = sys_part.system_throughput_bounded.to_numpy(float)
                sys90 = _weighted_rank(
                    np.abs((pred_sys - truth_sys) / truth_sys),
                    sys_weights, 0.90,
                )
                per_ap.append(ap90); per_sys.append(sys90)
                per_score.append(max(ap90, sys90))
            ap_values.append(float(np.mean(per_ap)))
            sys_values.append(float(np.mean(per_sys)))
            score_values.append(float(np.mean(per_score)))
        result["q3"][model] = {
            "selection_score": percentile_interval(score_values),
            "per_ap_absolute_relative_error_90": percentile_interval(ap_values),
            "system_absolute_relative_error_90": percentile_interval(sys_values),
        }
    return result


def strata(
    q1_rows: list[dict[str, Any]], q2_rows: list[dict[str, Any]],
    q3_rows: list[dict[str, Any]], labels: list[str],
) -> dict[str, Any]:
    q1, q2, q3 = map(pd.DataFrame, (q1_rows, q2_rows, q3_rows))
    q1 = q1[q1.scope.eq("PRIMARY") & q1.model_id.eq("Q1-B1")]
    q2 = q2[q2.scope.eq("PRIMARY") & q2.model_id.isin(["Q2-B1A", "Q2-B1B"])]
    q3 = q3[q3.scope.eq("PRIMARY") & q3.model_id.isin(["Q3-B1", "Q3-B2"])]
    result: dict[str, Any] = {"q1": {}, "q2": {}, "q3": {}}
    for field in ["ap_count", "loc_id", "nav", "protocol"]:
        result["q1"][field] = [{
            "repeat": int(repeat), "level": str(level),
            **regression_metrics(
                part.truth_seq_time.to_numpy(float),
                part.seq_time_bounded.to_numpy(float),
            ),
        } for (repeat, level), part in q1.groupby(["repeat", field])]
        result["q2"][field] = [{
            "model_id": model, "repeat": int(repeat), "level": str(level),
            **classification_metrics(
                part.truth_joint_label.to_numpy(str),
                part.predicted_joint_label.to_numpy(str),
                np.vstack(part.probability_fixed_17), labels,
            ),
        } for (model, repeat, level), part in q2.groupby(
            ["model_id", "repeat", field]
        )]
        result["q3"][field] = [{
            "model_id": model, "repeat": int(repeat), "level": str(level),
            **relative_error_metrics(
                part.truth_throughput.to_numpy(float),
                part.throughput_bounded.to_numpy(float),
            ),
        } for (model, repeat, level), part in q3.groupby(
            ["model_id", "repeat", field]
        )]
    return result


def a03_sensitivity(
    q2_rows: list[dict[str, Any]], q3_rows: list[dict[str, Any]],
    system_rows: list[dict[str, Any]], labels: list[str],
) -> dict[str, Any]:
    q2, q3, system = map(pd.DataFrame, (q2_rows, q3_rows, system_rows))
    groups = sorted(q2[q2.truth_joint_label.eq("0|0")].group_id.unique())
    q2 = q2[q2.scope.eq("PRIMARY") & ~q2.group_id.isin(groups)]
    q3 = q3[q3.scope.eq("PRIMARY") & ~q3.group_id.isin(groups)]
    system = system[system.scope.eq("PRIMARY") & ~system.group_id.isin(groups)]
    result: dict[str, Any] = {
        "analysis_type": (
            "whole-group evaluation exclusion on primary OOF predictions; "
            "primary model fits retain A03"
        ),
        "excluded_groups": groups, "excluded_group_count": len(groups),
        "q2": {}, "q3": {},
    }
    q2_fields = [
        "macro_f1_fixed_17", "joint_accuracy", "balanced_accuracy",
        "nss_accuracy", "mcs_accuracy", "multiclass_log_loss",
    ]
    for model, model_frame in q2.groupby("model_id"):
        metrics = [
            classification_metrics(
                part.truth_joint_label.to_numpy(str),
                part.predicted_joint_label.to_numpy(str),
                np.vstack(part.probability_fixed_17), labels,
            )
            for _, part in model_frame.groupby("repeat")
        ]
        result["q2"][model] = _mean(metrics, q2_fields)
    for model, model_frame in q3.groupby("model_id"):
        values = []
        model_system = system[system.model_id.eq(model)]
        for repeat, part in model_frame.groupby("repeat"):
            sys_part = model_system[model_system.repeat.eq(repeat)]
            ap_metric = relative_error_metrics(
                part.truth_throughput.to_numpy(float),
                part.throughput_bounded.to_numpy(float),
            )
            sys_metric = relative_error_metrics(
                sys_part.truth_system_throughput.to_numpy(float),
                sys_part.system_throughput_bounded.to_numpy(float),
            )
            values.append({
                "per_ap_are90": ap_metric["absolute_relative_error_90"],
                "system_are90": sys_metric["absolute_relative_error_90"],
                "selection_score": max(
                    ap_metric["absolute_relative_error_90"],
                    sys_metric["absolute_relative_error_90"],
                ),
            })
        result["q3"][model] = _mean(
            values, ["per_ap_are90", "system_are90", "selection_score"]
        )
    return result
