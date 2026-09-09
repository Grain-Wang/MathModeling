"""Nested S4 selection for the two G3-authorized model directions."""

from __future__ import annotations

import hashlib
import json
import math
import warnings
from collections import Counter
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)
from sklearn.linear_model import Ridge

from s1_data_audit import EXPECTED
from s2_contract_validation import group_id, label_of, stable_group_hash
from s3_lineage import aligned_probabilities, make_pipeline, phy_rate, q1_pipeline
from s3_metrics import classification_metrics, regression_metrics, relative_error_metrics
from s3_models import _append_q2, _append_q3
from s3_io import RunState, row_keys

Q1_COLUMN = "upstream__q1_seq_time_bounded"


def grid_records(s4_config: dict[str, Any], prefix: str) -> list[dict[str, Any]]:
    records = []
    for index, values in enumerate(s4_config["hgb_grid"]):
        records.append({
            "config_id": f"{prefix}-C{index}",
            "config_index": index,
            **values,
        })
    return records


def _fit(
    state: RunState,
    estimator: Any,
    x: pd.DataFrame,
    y: np.ndarray,
    context: str,
    sample_weight: np.ndarray | None = None,
) -> Any:
    if sample_weight is None:
        return state.fit(estimator, x, y, context)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        estimator.fit(x, y, model__sample_weight=sample_weight)
    state.model_fit_count += 1
    state.warnings.extend({
        "context": context,
        "category": item.category.__name__,
        "message": str(item.message),
    } for item in caught)
    return estimator


def _hgb_classifier(
    columns: list[str], candidate: dict[str, Any], common: dict[str, Any]
) -> Any:
    estimator = HistGradientBoostingClassifier(
        loss="log_loss",
        learning_rate=float(candidate["learning_rate"]),
        max_iter=int(common["max_iter"]),
        max_leaf_nodes=int(candidate["max_leaf_nodes"]),
        min_samples_leaf=int(common["min_samples_leaf"]),
        l2_regularization=float(candidate["l2_regularization"]),
        early_stopping=bool(common["early_stopping"]),
        random_state=int(common["random_state"]),
    )
    return make_pipeline(columns, estimator)


def _hgb_regressor(
    columns: list[str], candidate: dict[str, Any], common: dict[str, Any]
) -> Any:
    estimator = HistGradientBoostingRegressor(
        loss="squared_error",
        learning_rate=float(candidate["learning_rate"]),
        max_iter=int(common["max_iter"]),
        max_leaf_nodes=int(candidate["max_leaf_nodes"]),
        min_samples_leaf=int(common["min_samples_leaf"]),
        l2_regularization=float(candidate["l2_regularization"]),
        early_stopping=bool(common["early_stopping"]),
        random_state=int(common["random_state"]),
    )
    return make_pipeline(columns, estimator)


def _prediction_hash(
    frame: pd.DataFrame, indices: np.ndarray, prediction: np.ndarray
) -> str:
    rows = [
        f"{key}\t{float(value):.17g}"
        for key, value in sorted(zip(
            row_keys(frame.iloc[indices]).tolist(), prediction, strict=True
        ))
    ]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest().upper()


def _actual_lineage(
    frame: pd.DataFrame,
    prediction_index: np.ndarray,
    fit_index: np.ndarray,
    forbidden_groups: set[str],
    prediction: np.ndarray,
    context: dict[str, Any],
    role: str,
    registered_lineage_id: str | None,
) -> dict[str, Any]:
    predicted = set(group_id(frame.iloc[prediction_index]))
    fitted = set(group_id(frame.iloc[fit_index]))
    overlap = predicted & fitted
    forbidden_overlap = forbidden_groups & fitted
    if overlap or forbidden_overlap:
        raise AssertionError(f"S4 Q1 lineage leakage: {context}:{role}")
    identity = json.dumps(
        {**context, "role": role, "prediction_groups": sorted(predicted)},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return {
        "lineage_id": "S4-L-" + hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:20].upper(),
        "registered_lineage_id": registered_lineage_id,
        **context,
        "upstream_model_id": "Q1-B1",
        "prediction_variant": "seq_time_bounded",
        "postprocess_version": "q1_clip_0_test_dur_v1",
        "prediction_role": role,
        "prediction_groups": sorted(predicted),
        "prediction_group_count": len(predicted),
        "prediction_row_count": int(len(prediction_index)),
        "prediction_sha256": _prediction_hash(frame, prediction_index, prediction),
        "upstream_fit_groups_hash": stable_group_hash(fitted),
        "upstream_fit_group_count": len(fitted),
        "prediction_fit_overlap_count": len(overlap),
        "downstream_validation_fit_overlap_count": len(forbidden_overlap),
        "forbidden_group_count": len(forbidden_groups),
    }


def q1_boundary_features(
    features: pd.DataFrame,
    frame: pd.DataFrame,
    train_index: np.ndarray,
    validation_index: np.ndarray,
    upstream_specs: list[dict[str, Any]],
    context: dict[str, Any],
    roles: tuple[str, str],
    state: RunState,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    groups = group_id(frame).to_numpy()
    train_groups = set(groups[train_index])
    validation_groups = set(groups[validation_index])
    covered: Counter[str] = Counter()
    oof = np.full(len(frame), np.nan, dtype=float)
    lineages: list[dict[str, Any]] = []
    columns = list(features.columns)
    for position, spec in enumerate(upstream_specs):
        targets = set(spec["validation_groups"])
        if not targets or not targets <= train_groups:
            raise AssertionError(f"invalid frozen upstream targets: {context}")
        covered.update(targets)
        predicted_index = train_index[np.isin(groups[train_index], list(targets))]
        fit_index = train_index[~np.isin(groups[train_index], list(targets))]
        model = q1_pipeline(columns)
        state.fit(
            model,
            features.iloc[fit_index],
            frame.iloc[fit_index]["seq_time"].to_numpy(float),
            f"{context}:Q1-B1:{roles[0]}:{position}",
        )
        raw = np.asarray(model.predict(features.iloc[predicted_index]), dtype=float)
        bounded = np.clip(
            raw,
            0.0,
            frame.iloc[predicted_index]["test_dur"].to_numpy(float),
        )
        oof[predicted_index] = bounded
        lineages.append(_actual_lineage(
            frame,
            predicted_index,
            fit_index,
            validation_groups,
            bounded,
            {**context, "upstream_fold": position},
            roles[0],
            spec.get("registered_lineage_id"),
        ))
    if set(covered) != train_groups or any(value != 1 for value in covered.values()):
        raise AssertionError(f"frozen upstream coverage failed: {context}")
    if np.isnan(oof[train_index]).any():
        raise AssertionError(f"S4 Q1 OOF incomplete: {context}")

    full = q1_pipeline(columns)
    state.fit(
        full,
        features.iloc[train_index],
        frame.iloc[train_index]["seq_time"].to_numpy(float),
        f"{context}:Q1-B1:{roles[1]}",
    )
    raw = np.asarray(full.predict(features.iloc[validation_index]), dtype=float)
    bounded = np.clip(
        raw,
        0.0,
        frame.iloc[validation_index]["test_dur"].to_numpy(float),
    )
    registered_full = next(
        (
            item.get("registered_inference_lineage_id")
            for item in upstream_specs
            if item.get("registered_inference_lineage_id")
        ),
        None,
    )
    lineages.append(_actual_lineage(
        frame,
        validation_index,
        train_index,
        validation_groups,
        bounded,
        context,
        roles[1],
        registered_full,
    ))
    return oof[train_index], bounded, lineages


def nested_upstream_specs(
    registry: dict[str, Any],
    context: dict[str, Any],
    downstream_inner_fold: int,
) -> list[dict[str, Any]]:
    if context["scope"] == "PRIMARY":
        rows = [
            item for item in registry["primary_upstream_lineage_batches"]
            if item["prediction_role"] == "downstream_inner_train_oof"
            and int(item["outer_repeat"]) == int(context["repeat"])
            and int(item["outer_fold"]) == int(context["fold"])
            and int(item["downstream_inner_validation_fold"])
            == downstream_inner_fold
        ]
        inference = [
            item for item in registry["primary_upstream_lineage_batches"]
            if item["prediction_role"] == "downstream_inner_validation_inference"
            and int(item["outer_repeat"]) == int(context["repeat"])
            and int(item["outer_fold"]) == int(context["fold"])
            and int(item["downstream_inner_validation_fold"])
            == downstream_inner_fold
        ]
    else:
        rows = [
            item for item in registry["loso_upstream_lineage_batches"]
            if item["prediction_role"] == "loso_inner_train_oof"
            and int(item["loso_split"]) == int(context["loso_split"])
            and int(item["downstream_inner_validation_fold"])
            == downstream_inner_fold
        ]
        inference = [
            item for item in registry["loso_upstream_lineage_batches"]
            if item["prediction_role"] == "loso_inner_validation_inference"
            and int(item["loso_split"]) == int(context["loso_split"])
            and int(item["downstream_inner_validation_fold"])
            == downstream_inner_fold
        ]
    if len(rows) != 3 or len(inference) != 1:
        raise AssertionError(
            f"nested upstream registry mismatch: {context}:{downstream_inner_fold}"
        )
    return [
        {
            "validation_groups": set(item["prediction_groups"]),
            "registered_lineage_id": item["lineage_id"],
            "registered_inference_lineage_id": inference[0]["lineage_id"],
        }
        for item in rows
    ]


def select_q2(
    features: pd.DataFrame,
    frame: pd.DataFrame,
    train_index: np.ndarray,
    inner_specs: list[dict[str, Any]],
    labels: list[str],
    candidates: list[dict[str, Any]],
    common: dict[str, Any],
    context: dict[str, Any],
    state: RunState,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    groups = group_id(frame).to_numpy()
    train_groups = set(groups[train_index])
    trace: list[dict[str, Any]] = []
    columns = list(features.columns)
    for spec in inner_specs:
        inner_fold = int(spec["inner_fold"])
        targets = set(spec["validation_groups"]) & train_groups
        inner_valid = train_index[np.isin(groups[train_index], list(targets))]
        inner_train = train_index[~np.isin(groups[train_index], list(targets))]
        y_train = np.asarray([
            label_of(nss, mcs)
            for nss, mcs in zip(
                frame.iloc[inner_train]["nss"],
                frame.iloc[inner_train]["mcs"],
                strict=True,
            )
        ])
        y_valid = np.asarray([
            label_of(nss, mcs)
            for nss, mcs in zip(
                frame.iloc[inner_valid]["nss"],
                frame.iloc[inner_valid]["mcs"],
                strict=True,
            )
        ])
        for candidate in candidates:
            model = _hgb_classifier(columns, candidate, common)
            state.fit(
                model,
                features.iloc[inner_train],
                y_train,
                f"{context}:Q2:{candidate['config_id']}:inner-{inner_fold}",
            )
            prediction, probability, missing = aligned_probabilities(
                model, features.iloc[inner_valid], labels
            )
            metric = classification_metrics(
                y_valid, prediction, probability, labels
            )
            trace.append({
                **context,
                "downstream_inner_fold": inner_fold,
                "train_rows": int(len(inner_train)),
                "validation_rows": int(len(inner_valid)),
                "missing_train_labels": missing,
                **candidate,
                "macro_f1_fixed_17": metric["macro_f1_fixed_17"],
                "joint_accuracy": metric["joint_accuracy"],
                "multiclass_log_loss": metric["multiclass_log_loss"],
            })
    selected, summaries = select_q2_records(trace)
    return selected, trace, summaries


def select_q2_records(
    records: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summaries = []
    for config_id in sorted({str(x["config_id"]) for x in records}):
        rows = [x for x in records if x["config_id"] == config_id]
        first = rows[0]
        summaries.append({
            "config_id": config_id,
            "config_index": int(first["config_index"]),
            "learning_rate": float(first["learning_rate"]),
            "max_leaf_nodes": int(first["max_leaf_nodes"]),
            "l2_regularization": float(first["l2_regularization"]),
            "inner_record_count": len(rows),
            "macro_f1_fixed_17": float(np.mean([
                x["macro_f1_fixed_17"] for x in rows
            ])),
            "joint_accuracy": float(np.mean([
                x["joint_accuracy"] for x in rows
            ])),
            "multiclass_log_loss": float(np.mean([
                x["multiclass_log_loss"] for x in rows
            ])),
        })
    best_f1 = max(x["macro_f1_fixed_17"] for x in summaries)
    eligible = [
        x for x in summaries
        if best_f1 - x["macro_f1_fixed_17"] < 0.002
    ]
    selected = min(eligible, key=lambda x: (
        -x["joint_accuracy"],
        x["multiclass_log_loss"],
        x["max_leaf_nodes"],
        x["config_index"],
    ))
    return dict(selected), summaries


def q2_fit_predict(
    features: pd.DataFrame,
    frame: pd.DataFrame,
    train_index: np.ndarray,
    valid_index: np.ndarray,
    labels: list[str],
    selected: dict[str, Any],
    common: dict[str, Any],
    context: dict[str, Any],
    state: RunState,
    output: list[dict[str, Any]],
    model_id: str,
    weighted: bool = False,
    q1_train: np.ndarray | None = None,
    q1_valid: np.ndarray | None = None,
    lineage_id: str | None = None,
) -> dict[str, Any]:
    train_x = features.iloc[train_index].copy()
    valid_x = features.iloc[valid_index].copy()
    uses_q1 = q1_train is not None
    if uses_q1:
        if q1_valid is None:
            raise AssertionError("Q2 with-Q1 validation feature missing")
        train_x[Q1_COLUMN] = q1_train
        valid_x[Q1_COLUMN] = q1_valid
    columns = list(train_x.columns)
    y_train = np.asarray([
        label_of(nss, mcs)
        for nss, mcs in zip(
            frame.iloc[train_index]["nss"],
            frame.iloc[train_index]["mcs"],
            strict=True,
        )
    ])
    weights = None
    weight_audit: dict[str, Any] | None = None
    if weighted:
        counts = Counter(y_train)
        n, k = len(y_train), len(labels)
        by_class = {
            label: min(5.0, math.sqrt(n / (k * count)))
            for label, count in counts.items()
        }
        weights = np.asarray([by_class[str(label)] for label in y_train])
        weight_audit = {
            "formula": "sqrt(N/(K*n_k))",
            "K": k,
            "cap": 5.0,
            "class_weights": by_class,
            "minimum": float(weights.min()),
            "maximum": float(weights.max()),
        }
    model = _hgb_classifier(columns, selected, common)
    _fit(
        state,
        model,
        train_x,
        y_train,
        f"{context}:{model_id}:{selected['config_id']}",
        sample_weight=weights,
    )
    prediction, probability, missing = aligned_probabilities(
        model, valid_x, labels
    )
    before = len(output)
    _append_q2(
        output,
        frame,
        valid_index,
        context,
        model_id,
        prediction,
        probability,
        labels,
        missing,
        lineage_id,
    )
    for row in output[before:]:
        row.update({
            "selected_config_id": selected["config_id"],
            "selected_parameters": {
                key: selected[key]
                for key in [
                    "learning_rate", "max_leaf_nodes", "l2_regularization"
                ]
            },
            "weighted": weighted,
            "uses_q1": uses_q1,
            "ap_count_representation": "numeric_binary_2_or_3",
        })
    return {
        **context,
        "model_id": model_id,
        "selected_config_id": selected["config_id"],
        "weighted": weighted,
        "uses_q1": uses_q1,
        "missing_train_labels": missing,
        "weight_audit": weight_audit,
    }


def _augment_q3(
    features: pd.DataFrame,
    frame: pd.DataFrame,
    q1_prediction: np.ndarray,
) -> pd.DataFrame:
    output = features.copy()
    rate = phy_rate(frame)
    duration = frame["test_dur"].to_numpy(float)
    output[Q1_COLUMN] = q1_prediction
    output["physical__actual_nss"] = frame["nss"].to_numpy(float)
    output["physical__actual_mcs"] = frame["mcs"].to_numpy(float)
    output["physical__phy_rate_mbps"] = rate
    output["physical__q1_air_fraction"] = q1_prediction / duration
    output["physical__proxy_mbps"] = q1_prediction / duration * rate
    output["physical__rate_missing"] = (~np.isfinite(rate)).astype(float)
    return output


def _physical_base(
    base_features: pd.DataFrame,
    frame: pd.DataFrame,
    train_index: np.ndarray,
    valid_index: np.ndarray,
    q1_train: np.ndarray,
    q1_valid: np.ndarray,
    state: RunState,
    context: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    train_x = base_features.iloc[train_index].copy()
    valid_x = base_features.iloc[valid_index].copy()
    train_x[Q1_COLUMN] = q1_train
    valid_x[Q1_COLUMN] = q1_valid
    ridge = make_pipeline(
        list(train_x.columns),
        Ridge(alpha=1.0, solver="lsqr", tol=1e-8, max_iter=10000),
    )
    y = frame.iloc[train_index]["throughput"].to_numpy(float)
    state.fit(ridge, train_x, y, f"{context}:Q3-B1-fallback")
    ridge_train = np.asarray(ridge.predict(train_x), dtype=float)
    ridge_valid = np.asarray(ridge.predict(valid_x), dtype=float)
    train_rate = phy_rate(frame.iloc[train_index])
    valid_rate = phy_rate(frame.iloc[valid_index])
    train_proxy = (
        q1_train / frame.iloc[train_index]["test_dur"].to_numpy(float)
        * train_rate
    )
    valid_proxy = (
        q1_valid / frame.iloc[valid_index]["test_dur"].to_numpy(float)
        * valid_rate
    )
    usable = np.isfinite(train_proxy)
    denominator = float(np.sum(np.square(train_proxy[usable])))
    if denominator <= 0 or not math.isfinite(denominator):
        raise RuntimeError(f"{context}: invalid physical eta denominator")
    eta = float(np.clip(
        np.sum(train_proxy[usable] * y[usable]) / denominator,
        0.0,
        1.0,
    ))
    train_base = eta * train_proxy
    valid_base = eta * valid_proxy
    train_missing = ~np.isfinite(train_base)
    valid_missing = ~np.isfinite(valid_base)
    train_base[train_missing] = ridge_train[train_missing]
    valid_base[valid_missing] = ridge_valid[valid_missing]
    return train_base, valid_base, {
        "eta": eta,
        "train_rate_missing": int(train_missing.sum()),
        "validation_rate_missing": int(valid_missing.sum()),
        "rate_missing_fallback": "fold-local Q3-B1",
    }


def q3_selection_metric(
    frame: pd.DataFrame,
    indices: np.ndarray,
    prediction: np.ndarray,
) -> dict[str, Any]:
    truth = frame.iloc[indices]["throughput"].to_numpy(float)
    bounded = np.maximum(0.0, prediction)
    ap = relative_error_metrics(truth, bounded)
    temporary = pd.DataFrame({
        "group_id": group_id(frame.iloc[indices]).to_numpy(),
        "truth": truth,
        "prediction": bounded,
    })
    grouped = temporary.groupby("group_id", sort=True)[["truth", "prediction"]].sum()
    system = relative_error_metrics(
        grouped["truth"].to_numpy(float),
        grouped["prediction"].to_numpy(float),
    )
    ap_mae = regression_metrics(truth, bounded)["mae"] / float(np.mean(truth))
    sys_mae = regression_metrics(
        grouped["truth"].to_numpy(float),
        grouped["prediction"].to_numpy(float),
    )["mae"] / float(grouped["truth"].mean())
    return {
        "selection_score": max(
            ap["absolute_relative_error_90"],
            system["absolute_relative_error_90"],
        ),
        "per_ap_are90": ap["absolute_relative_error_90"],
        "system_are90": system["absolute_relative_error_90"],
        "per_ap_median_signed_bias": ap["median_signed_bias"],
        "system_median_signed_bias": system["median_signed_bias"],
        "mean_normalized_ap_system_mae": float((ap_mae + sys_mae) / 2),
    }


def _predict_q3_candidate(
    train_x: pd.DataFrame,
    y_train: np.ndarray,
    valid_x: pd.DataFrame,
    train_base: np.ndarray,
    valid_base: np.ndarray,
    candidate: dict[str, Any],
    common: dict[str, Any],
    state: RunState,
    context: str,
) -> tuple[np.ndarray, Any]:
    model = _hgb_regressor(list(train_x.columns), candidate, common)
    architecture = candidate["architecture"]
    target = y_train if architecture == "direct" else y_train - train_base
    state.fit(model, train_x, target, context)
    component = np.asarray(model.predict(valid_x), dtype=float)
    raw = component if architecture == "direct" else valid_base + component
    return raw, model


def select_q3(
    features: pd.DataFrame,
    frame: pd.DataFrame,
    train_index: np.ndarray,
    inner_specs: list[dict[str, Any]],
    registry: dict[str, Any],
    candidates: list[dict[str, Any]],
    common: dict[str, Any],
    context: dict[str, Any],
    state: RunState,
) -> tuple[
    dict[str, Any], list[dict[str, Any]], list[dict[str, Any]],
    list[dict[str, Any]],
]:
    groups = group_id(frame).to_numpy()
    train_groups = set(groups[train_index])
    trace: list[dict[str, Any]] = []
    lineages: list[dict[str, Any]] = []
    for spec in inner_specs:
        inner_fold = int(spec["inner_fold"])
        targets = set(spec["validation_groups"]) & train_groups
        inner_valid = train_index[np.isin(groups[train_index], list(targets))]
        inner_train = train_index[~np.isin(groups[train_index], list(targets))]
        nested = nested_upstream_specs(registry, context, inner_fold)
        q1_train, q1_valid, nested_lineage = q1_boundary_features(
            features,
            frame,
            inner_train,
            inner_valid,
            nested,
            {**context, "downstream_inner_fold": inner_fold},
            (
                "downstream_inner_train_oof"
                if context["scope"] == "PRIMARY"
                else "loso_inner_train_oof",
                "downstream_inner_validation_inference"
                if context["scope"] == "PRIMARY"
                else "loso_inner_validation_inference",
            ),
            state,
        )
        lineages.extend(nested_lineage)
        train_x = _augment_q3(
            features.iloc[inner_train].copy(),
            frame.iloc[inner_train].copy(),
            q1_train,
        )
        valid_x = _augment_q3(
            features.iloc[inner_valid].copy(),
            frame.iloc[inner_valid].copy(),
            q1_valid,
        )
        train_base, valid_base, base_audit = _physical_base(
            features,
            frame,
            inner_train,
            inner_valid,
            q1_train,
            q1_valid,
            state,
            f"{context}:Q3:inner-{inner_fold}",
        )
        y_train = frame.iloc[inner_train]["throughput"].to_numpy(float)
        for candidate in candidates:
            raw, _ = _predict_q3_candidate(
                train_x,
                y_train,
                valid_x,
                train_base,
                valid_base,
                candidate,
                common,
                state,
                f"{context}:Q3:{candidate['candidate_id']}:inner-{inner_fold}",
            )
            metric = q3_selection_metric(frame, inner_valid, raw)
            trace.append({
                **context,
                "downstream_inner_fold": inner_fold,
                "train_rows": int(len(inner_train)),
                "validation_rows": int(len(inner_valid)),
                **candidate,
                **metric,
                "physical_base": base_audit,
            })
    selected, summaries = select_q3_records(trace)
    return selected, trace, summaries, lineages


def select_q3_records(
    records: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summaries = []
    for candidate_id in sorted({str(x["candidate_id"]) for x in records}):
        rows = [x for x in records if x["candidate_id"] == candidate_id]
        first = rows[0]
        summaries.append({
            "candidate_id": candidate_id,
            "architecture": first["architecture"],
            "config_id": first["config_id"],
            "config_index": int(first["config_index"]),
            "learning_rate": float(first["learning_rate"]),
            "max_leaf_nodes": int(first["max_leaf_nodes"]),
            "l2_regularization": float(first["l2_regularization"]),
            "inner_record_count": len(rows),
            "selection_score": float(np.mean([
                x["selection_score"] for x in rows
            ])),
            "mean_normalized_ap_system_mae": float(np.mean([
                x["mean_normalized_ap_system_mae"] for x in rows
            ])),
            "worst_absolute_median_signed_bias": float(np.mean([
                max(
                    abs(x["per_ap_median_signed_bias"]),
                    abs(x["system_median_signed_bias"]),
                )
                for x in rows
            ])),
        })
    best_score = min(x["selection_score"] for x in summaries)
    eligible = [
        x for x in summaries
        if x["selection_score"] <= best_score * 1.005
    ]
    selected = min(eligible, key=lambda x: (
        x["mean_normalized_ap_system_mae"],
        x["worst_absolute_median_signed_bias"],
        0 if x["architecture"] == "direct" else 1,
        x["max_leaf_nodes"],
        x["config_index"],
    ))
    return dict(selected), summaries


def q3_fit_predict(
    features: pd.DataFrame,
    frame: pd.DataFrame,
    train_index: np.ndarray,
    valid_index: np.ndarray,
    q1_train: np.ndarray,
    q1_valid: np.ndarray,
    selected: dict[str, Any],
    common: dict[str, Any],
    context: dict[str, Any],
    state: RunState,
    output: list[dict[str, Any]],
    model_id: str,
    lineage_id: str,
    split_by_ap_count: bool,
) -> dict[str, Any]:
    train_x = _augment_q3(
        features.iloc[train_index].copy(),
        frame.iloc[train_index].copy(),
        q1_train,
    )
    valid_x = _augment_q3(
        features.iloc[valid_index].copy(),
        frame.iloc[valid_index].copy(),
        q1_valid,
    )
    train_base, valid_base, base_audit = _physical_base(
        features,
        frame,
        train_index,
        valid_index,
        q1_train,
        q1_valid,
        state,
        f"{context}:{model_id}",
    )
    y_train = frame.iloc[train_index]["throughput"].to_numpy(float)
    candidate = dict(selected)
    if not split_by_ap_count:
        raw, _ = _predict_q3_candidate(
            train_x,
            y_train,
            valid_x,
            train_base,
            valid_base,
            candidate,
            common,
            state,
            f"{context}:{model_id}:{candidate['candidate_id']}",
        )
    else:
        train_counts = np.asarray([
            int(EXPECTED[str(source)]["ap_count"])
            for source in frame.iloc[train_index]["source_file"]
        ])
        valid_counts = np.asarray([
            int(EXPECTED[str(source)]["ap_count"])
            for source in frame.iloc[valid_index]["source_file"]
        ])
        raw = np.full(len(valid_index), np.nan, dtype=float)
        for ap_count in (2, 3):
            train_local = np.flatnonzero(train_counts == ap_count)
            valid_local = np.flatnonzero(valid_counts == ap_count)
            if not len(train_local):
                raise AssertionError(
                    f"AP-count split training lacks stratum {ap_count}"
                )
            if not len(valid_local):
                continue
            part, _ = _predict_q3_candidate(
                train_x.iloc[train_local],
                y_train[train_local],
                valid_x.iloc[valid_local],
                train_base[train_local],
                valid_base[valid_local],
                candidate,
                common,
                state,
                f"{context}:{model_id}:{candidate['candidate_id']}:ap{ap_count}",
            )
            raw[valid_local] = part
        if not np.isfinite(raw).all():
            raise AssertionError("AP-count split emitted non-finite prediction")
    bounded = np.maximum(0.0, raw)
    rate = phy_rate(frame.iloc[valid_index])
    proxy = (
        q1_valid / frame.iloc[valid_index]["test_dur"].to_numpy(float) * rate
    )
    before = len(output)
    _append_q3(
        output,
        frame,
        valid_index,
        context,
        model_id,
        raw,
        bounded,
        q1_valid,
        proxy,
        float(base_audit["eta"]),
        lineage_id,
    )
    for row in output[before:]:
        row.update({
            "selected_candidate_id": selected["candidate_id"],
            "selected_architecture": selected["architecture"],
            "selected_parameters": {
                key: selected[key]
                for key in [
                    "learning_rate", "max_leaf_nodes", "l2_regularization"
                ]
            },
            "ap_count_split": split_by_ap_count,
            "ap_count_representation": "numeric_binary_2_or_3",
        })
    return {
        **context,
        "model_id": model_id,
        "selected_candidate_id": selected["candidate_id"],
        "selected_architecture": selected["architecture"],
        "ap_count_split": split_by_ap_count,
        "physical_base": base_audit,
    }


def q3_candidates(s4_config: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    for architecture in s4_config["q3"]["architectures"]:
        for item in grid_records(s4_config, "Q3"):
            output.append({
                **item,
                "architecture": architecture,
                "candidate_id": f"Q3-{architecture}-C{item['config_index']}",
            })
    return output
