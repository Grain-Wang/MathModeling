"""Execute the eight frozen S3 Baselines on one evaluation fold."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge

from s1_data_audit import EXPECTED
from s2_contract_validation import group_id, label_of
from s3_features import feature_families
from s3_io import RunState, row_keys
from s3_lineage import (
    aligned_probabilities,
    majority_prediction,
    make_pipeline,
    permute_family_by_group,
    phy_rate,
    q1_crossfit,
    q1_pipeline,
    q2_pipeline,
)
from s3_metrics import regression_metrics


def _common(
    frame: pd.DataFrame, index: int, context: dict[str, Any],
) -> dict[str, Any]:
    source = str(frame.at[index, "source_file"])
    return {
        "row_key": row_keys(frame.iloc[[index]]).iloc[0],
        "group_id": group_id(frame.iloc[[index]]).iloc[0],
        "source_file": source,
        "test_id": int(frame.at[index, "test_id"]),
        "ap_id": str(frame.at[index, "ap_id"]),
        "ap_count": int(EXPECTED[source]["ap_count"]),
        "loc_id": str(frame.at[index, "loc_id"]),
        "nav": float(frame.at[index, "nav"]),
        "protocol": str(frame.at[index, "protocol"]),
        **context,
    }


def _append_q1(
    output: list[dict[str, Any]], frame: pd.DataFrame,
    indices: np.ndarray, context: dict[str, Any], model_id: str,
    raw: np.ndarray, bounded: np.ndarray, lineage_id: str | None,
) -> None:
    for local, index in enumerate(indices):
        output.append({
            **_common(frame, int(index), context),
            "truth_seq_time": float(frame.at[index, "seq_time"]),
            "test_dur": float(frame.at[index, "test_dur"]),
            "seq_time_raw": float(raw[local]),
            "seq_time_bounded": float(bounded[local]),
            "clipped": bool(abs(raw[local] - bounded[local]) > 1e-12),
            "model_id": model_id, "lineage_id": lineage_id,
        })


def _append_q2(
    output: list[dict[str, Any]], frame: pd.DataFrame,
    indices: np.ndarray, context: dict[str, Any], model_id: str,
    prediction: np.ndarray, probability: np.ndarray,
    labels: list[str], missing: list[str], lineage_id: str | None,
) -> None:
    for local, index in enumerate(indices):
        predicted = str(prediction[local])
        output.append({
            **_common(frame, int(index), context),
            "truth_joint_label": label_of(
                frame.at[index, "nss"], frame.at[index, "mcs"]
            ),
            "predicted_joint_label": predicted,
            "predict_nss": int(predicted.split("|")[0]),
            "predict_mcs": int(predicted.split("|")[1]),
            "probability_fixed_17": [
                float(x) for x in probability[local]
            ],
            "probability_label_order": labels,
            "missing_train_labels": missing,
            "model_id": model_id,
            "upstream_lineage_id": lineage_id,
        })


def _append_q3(
    output: list[dict[str, Any]], frame: pd.DataFrame,
    indices: np.ndarray, context: dict[str, Any], model_id: str,
    raw: np.ndarray, bounded: np.ndarray,
    q1_prediction: np.ndarray | None, proxy: np.ndarray | None,
    eta: float | None, lineage_id: str | None,
) -> None:
    rates = phy_rate(frame.iloc[indices])
    for local, index in enumerate(indices):
        output.append({
            **_common(frame, int(index), context),
            "truth_throughput": float(frame.at[index, "throughput"]),
            "throughput_raw": float(raw[local]),
            "throughput_bounded": float(bounded[local]),
            "negative_clipped": bool(raw[local] < 0),
            "phy_rate_mbps": (
                None if not np.isfinite(rates[local])
                else float(rates[local])
            ),
            "rate_missing": bool(not np.isfinite(rates[local])),
            "q1_seq_time_bounded": (
                None if q1_prediction is None
                else float(q1_prediction[local])
            ),
            "physical_proxy_mbps": (
                None if proxy is None or not np.isfinite(proxy[local])
                else float(proxy[local])
            ),
            "eta": eta, "model_id": model_id,
            "upstream_lineage_id": lineage_id,
        })


def _coefficients(model: Any) -> list[dict[str, Any]]:
    names = model.named_steps["preprocess"].get_feature_names_out()
    values = np.asarray(model.named_steps["model"].coef_, dtype=float)
    if len(names) != len(values):
        raise AssertionError("Ridge feature-name/coef mismatch")
    return [
        {
            "transformed_feature": str(name),
            "coefficient": float(value),
            "absolute_coefficient": float(abs(value)),
        }
        for name, value in zip(names, values, strict=True)
    ]


def run_fold(
    features: pd.DataFrame, frame: pd.DataFrame,
    train_index: np.ndarray, valid_index: np.ndarray,
    inner_specs: list[dict[str, Any]], context: dict[str, Any],
    labels: list[str], state: RunState,
    outputs: dict[str, list[dict[str, Any]]],
    run_influence: bool,
) -> None:
    columns = list(features.columns)
    q1_oof, q1_raw, q1_bounded, q1_full, lineage, crossfit = q1_crossfit(
        features, frame, train_index, valid_index, inner_specs, context, state
    )
    outputs["lineage"].extend(lineage)
    outputs["crossfit"].extend(crossfit)
    lineage_id = lineage[-1]["lineage_id"]

    y1 = frame.iloc[train_index]["seq_time"].to_numpy(float)
    dummy1 = DummyRegressor(strategy="median")
    state.fit(
        dummy1, np.zeros((len(train_index), 1)), y1,
        f"{context}:Q1-B0",
    )
    dummy1_raw = np.asarray(
        dummy1.predict(np.zeros((len(valid_index), 1))), dtype=float
    )
    duration = frame.iloc[valid_index]["test_dur"].to_numpy(float)
    dummy1_bounded = np.clip(dummy1_raw, 0.0, duration)
    _append_q1(
        outputs["q1"], frame, valid_index, context, "Q1-B0",
        dummy1_raw, dummy1_bounded, None,
    )
    _append_q1(
        outputs["q1"], frame, valid_index, context, "Q1-B1",
        q1_raw, q1_bounded, lineage_id,
    )

    y2 = np.asarray([
        label_of(nss, mcs)
        for nss, mcs in zip(
            frame.iloc[train_index]["nss"],
            frame.iloc[train_index]["mcs"], strict=True,
        )
    ])
    d_pred, d_prob, d_missing = majority_prediction(
        y2, len(valid_index), labels
    )
    _append_q2(
        outputs["q2"], frame, valid_index, context, "Q2-B0",
        d_pred, d_prob, labels, d_missing, None,
    )

    logistic_a = q2_pipeline(columns)
    state.fit(
        logistic_a, features.iloc[train_index], y2,
        f"{context}:Q2-B1A",
    )
    a_pred, a_prob, a_missing = aligned_probabilities(
        logistic_a, features.iloc[valid_index], labels
    )
    _append_q2(
        outputs["q2"], frame, valid_index, context, "Q2-B1A",
        a_pred, a_prob, labels, a_missing, None,
    )

    q1_column = "upstream__q1_seq_time_bounded"
    downstream_columns = columns + [q1_column]
    train_x = features.iloc[train_index].copy()
    train_x[q1_column] = q1_oof
    valid_x = features.iloc[valid_index].copy()
    valid_x[q1_column] = q1_bounded
    logistic_b = q2_pipeline(downstream_columns)
    state.fit(logistic_b, train_x, y2, f"{context}:Q2-B1B")
    b_pred, b_prob, b_missing = aligned_probabilities(
        logistic_b, valid_x, labels
    )
    _append_q2(
        outputs["q2"], frame, valid_index, context, "Q2-B1B",
        b_pred, b_prob, labels, b_missing, lineage_id,
    )

    y3 = frame.iloc[train_index]["throughput"].to_numpy(float)
    dummy3 = DummyRegressor(strategy="median")
    state.fit(
        dummy3, np.zeros((len(train_index), 1)), y3,
        f"{context}:Q3-B0",
    )
    dummy3_raw = np.asarray(
        dummy3.predict(np.zeros((len(valid_index), 1))), dtype=float
    )
    _append_q3(
        outputs["q3"], frame, valid_index, context, "Q3-B0",
        dummy3_raw, np.maximum(0.0, dummy3_raw),
        None, None, None, None,
    )

    ridge3 = make_pipeline(downstream_columns, Ridge(alpha=1.0, solver="lsqr", tol=1e-8, max_iter=10000))
    state.fit(ridge3, train_x, y3, f"{context}:Q3-B1")
    ridge3_raw = np.asarray(ridge3.predict(valid_x), dtype=float)
    valid_rate = phy_rate(frame.iloc[valid_index])
    valid_proxy = (
        q1_bounded
        / frame.iloc[valid_index]["test_dur"].to_numpy(float)
        * valid_rate
    )
    _append_q3(
        outputs["q3"], frame, valid_index, context, "Q3-B1",
        ridge3_raw, np.maximum(0.0, ridge3_raw),
        q1_bounded, valid_proxy, None, lineage_id,
    )

    train_rate = phy_rate(frame.iloc[train_index])
    train_proxy = (
        q1_oof / frame.iloc[train_index]["test_dur"].to_numpy(float)
        * train_rate
    )
    usable = np.isfinite(train_proxy)
    denominator = float(np.sum(np.square(train_proxy[usable])))
    if denominator <= 0 or not math.isfinite(denominator):
        raise RuntimeError(f"{context}: invalid Q3-B2 eta denominator")
    eta = float(np.clip(
        np.sum(train_proxy[usable] * y3[usable]) / denominator, 0.0, 1.0
    ))
    physics_raw = eta * valid_proxy
    missing_rate = ~np.isfinite(physics_raw)
    physics_raw[missing_rate] = ridge3_raw[missing_rate]
    _append_q3(
        outputs["q3"], frame, valid_index, context, "Q3-B2",
        physics_raw, np.maximum(0.0, physics_raw),
        q1_bounded, valid_proxy, eta, lineage_id,
    )

    outputs["fold_status"].append({
        **context, "status": "PASS",
        "train_rows": int(len(train_index)),
        "validation_rows": int(len(valid_index)),
        "train_groups": int(group_id(frame.iloc[train_index]).nunique()),
        "validation_groups": int(group_id(frame.iloc[valid_index]).nunique()),
        "q2_missing_train_labels": {
            "Q2-B0": d_missing, "Q2-B1A": a_missing,
            "Q2-B1B": b_missing,
        },
        "q3_eta": eta,
        "actual_upstream_lineage_ids": [x["lineage_id"] for x in lineage],
    })

    if not run_influence:
        return
    truth = frame.iloc[valid_index]["seq_time"].to_numpy(float)
    full_mae = regression_metrics(truth, q1_bounded)["mae"]
    families = feature_families(columns)
    for family_index, (family, family_columns) in enumerate(families.items()):
        kept = [x for x in columns if x not in set(family_columns)]
        ablated = q1_pipeline(kept)
        state.fit(
            ablated, features.iloc[train_index][kept], y1,
            f"{context}:Q1-B1:ablate:{family}",
        )
        ablated_raw = np.asarray(
            ablated.predict(features.iloc[valid_index][kept]), dtype=float
        )
        ablated_mae = regression_metrics(
            truth, np.clip(ablated_raw, 0.0, duration)
        )["mae"]
        valid_features = features.iloc[valid_index].copy()
        valid_frame = frame.iloc[valid_index].copy()
        permuted = permute_family_by_group(
            valid_features, valid_frame, family_columns,
            702409 + int(context["repeat"]) * 100
            + int(context["fold"]) * 10 + family_index,
        )
        permuted_raw = np.asarray(q1_full.predict(permuted), dtype=float)
        permuted_mae = regression_metrics(
            truth, np.clip(permuted_raw, 0.0, duration)
        )["mae"]
        outputs["influence"].append({
            **context, "family": family,
            "feature_count": len(family_columns),
            "full_bounded_mae": full_mae,
            "ablation_bounded_mae": ablated_mae,
            "ablation_delta_mae": float(ablated_mae - full_mae),
            "whole_group_permutation_bounded_mae": permuted_mae,
            "permutation_delta_mae": float(permuted_mae - full_mae),
        })
    outputs["coefficients"].extend(
        {**context, **item} for item in _coefficients(q1_full)
    )


def system_records(ap_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in ap_rows:
        groups[(
            row["scope"], row["model_id"], row.get("repeat"),
            row.get("fold"), row.get("loso_split"),
            row["source_file"], row["test_id"],
        )].append(row)
    output = []
    for key, rows in sorted(groups.items(), key=lambda item: str(item[0])):
        expected = int(EXPECTED[rows[0]["source_file"]]["ap_count"])
        if len(rows) != expected:
            raise AssertionError(f"incomplete Q3 system group: {key}")
        output.append({
            "scope": rows[0]["scope"], "model_id": rows[0]["model_id"],
            "repeat": rows[0].get("repeat"), "fold": rows[0].get("fold"),
            "loso_split": rows[0].get("loso_split"),
            "held_out_source_file": rows[0].get("held_out_source_file"),
            "group_id": rows[0]["group_id"],
            "source_file": rows[0]["source_file"],
            "test_id": rows[0]["test_id"], "ap_count": expected,
            "truth_system_throughput": math.fsum(
                x["truth_throughput"] for x in rows
            ),
            "system_throughput_raw": math.fsum(
                x["throughput_raw"] for x in rows
            ),
            "system_throughput_bounded": math.fsum(
                x["throughput_bounded"] for x in rows
            ),
            "component_row_keys": sorted(x["row_key"] for x in rows),
            "strict_identity_pass": True,
            "bounded_sum_equality_absolute_error": 0.0,
        })
    return output


def influence_summary(
    rows: list[dict[str, Any]], coefficients: list[dict[str, Any]],
) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    families = {}
    for family, subset in frame.groupby("family"):
        repeats = [{
            "repeat": int(repeat),
            "ablation_delta_mae": float(part["ablation_delta_mae"].mean()),
            "permutation_delta_mae": float(part["permutation_delta_mae"].mean()),
        } for repeat, part in subset.groupby("repeat")]
        families[family] = {
            "fold_count": int(len(subset)), "repeat_means": repeats,
            "mean_ablation_delta_mae": float(
                subset["ablation_delta_mae"].mean()
            ),
            "mean_permutation_delta_mae": float(
                subset["permutation_delta_mae"].mean()
            ),
            "ablation_positive_repeat_count": sum(
                x["ablation_delta_mae"] > 0 for x in repeats
            ),
            "permutation_positive_repeat_count": sum(
                x["permutation_delta_mae"] > 0 for x in repeats
            ),
        }
    coeff = pd.DataFrame(coefficients)
    ranked = []
    for name, subset in coeff.groupby("transformed_feature"):
        values = subset["coefficient"].to_numpy(float)
        ranked.append({
            "transformed_feature": name,
            "mean_coefficient": float(values.mean()),
            "mean_absolute_coefficient": float(np.abs(values).mean()),
            "positive_fold_count": int(np.sum(values > 0)),
            "negative_fold_count": int(np.sum(values < 0)),
            "fold_count": int(len(values)),
        })
    ranked.sort(key=lambda x: x["mean_absolute_coefficient"], reverse=True)
    return {
        "interpretation_boundary": (
            "held-out predictive contribution/conditional association only; "
            "not a causal effect"
        ),
        "feature_families": families,
        "ridge_coefficients_ranked": ranked,
    }
