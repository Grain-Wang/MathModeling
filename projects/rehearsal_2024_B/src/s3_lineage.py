"""Fold-local preprocessing and auditable Q1 cross-fitting for S3."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from s2_contract_validation import group_id, stable_group_hash
from s3_features import CATEGORICAL_FEATURES
from s3_io import PHY_RATE, RunState, row_keys


def make_pipeline(columns: list[str], estimator: Any) -> Pipeline:
    categorical = [x for x in columns if x in set(CATEGORICAL_FEATURES)]
    numeric = [x for x in columns if x not in categorical]
    transformers = []
    if numeric:
        transformers.append((
            "num",
            Pipeline([
                ("impute", SimpleImputer(
                    strategy="median", add_indicator=True,
                    keep_empty_features=True,
                )),
                ("scale", StandardScaler()),
            ]),
            numeric,
        ))
    if categorical:
        transformers.append((
            "cat",
            Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(
                    handle_unknown="ignore", sparse_output=False
                )),
            ]),
            categorical,
        ))
    return Pipeline([
        ("preprocess", ColumnTransformer(
            transformers, remainder="drop", sparse_threshold=0.0,
            verbose_feature_names_out=True,
        )),
        ("model", estimator),
    ])


def q1_pipeline(columns: list[str]) -> Pipeline:
    return make_pipeline(columns, Ridge(alpha=1.0, solver="lsqr", tol=1e-8, max_iter=10000))


def q2_pipeline(columns: list[str]) -> Pipeline:
    return make_pipeline(columns, LogisticRegression(
        C=1.0, max_iter=2000, class_weight=None, solver="lbfgs"
    ))


def phy_rate(frame: pd.DataFrame) -> np.ndarray:
    return np.asarray([
        PHY_RATE.get((int(float(nss)), int(float(mcs))), np.nan)
        for nss, mcs in zip(frame["nss"], frame["mcs"], strict=True)
    ], dtype=float)


def inner_specs_primary(
    registry: dict[str, Any], repeat: int, fold: int,
) -> list[dict[str, Any]]:
    grouped: dict[int, set[str]] = defaultdict(set)
    seeds = {}
    for item in registry["inner_assignments"]:
        if (
            int(item["outer_repeat"]) == repeat
            and int(item["outer_fold"]) == fold
        ):
            inner = int(item["inner_validation_fold"])
            grouped[inner].add(
                f"{item['source_file']}::{int(item['test_id'])}"
            )
            seeds[inner] = int(item["inner_random_state"])
    return [
        {
            "inner_fold": inner, "random_state": seeds[inner],
            "validation_groups": groups,
        }
        for inner, groups in sorted(grouped.items())
    ]


def inner_specs_loso(
    registry: dict[str, Any], split: int,
) -> list[dict[str, Any]]:
    rows = [
        item for item in registry["loso_downstream_inner_batches"]
        if int(item["loso_split"]) == split
    ]
    return [
        {
            "inner_fold": int(item["downstream_inner_validation_fold"]),
            "random_state": int(item["downstream_inner_random_state"]),
            "validation_groups": set(item["validation_groups"]),
        }
        for item in sorted(
            rows, key=lambda x: int(x["downstream_inner_validation_fold"])
        )
    ]


def _prediction_hash(keys: list[str], prediction: np.ndarray) -> str:
    rows = [
        f"{key}\t{float(value):.17g}"
        for key, value in sorted(zip(keys, prediction, strict=True))
    ]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest().upper()


def _lineage(
    context: dict[str, Any], role: str, frame: pd.DataFrame,
    prediction_index: np.ndarray, fit_index: np.ndarray,
    forbidden_groups: set[str], prediction: np.ndarray,
) -> dict[str, Any]:
    predicted = set(group_id(frame.iloc[prediction_index]))
    fitted = set(group_id(frame.iloc[fit_index]))
    if predicted & fitted or forbidden_groups & fitted:
        raise AssertionError(f"actual Q1 lineage leakage in {context}:{role}")
    identity = json.dumps(
        {**context, "role": role, "prediction_groups": sorted(predicted)},
        sort_keys=True, separators=(",", ":"),
    )
    lineage_id = (
        "L-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20].upper()
    )
    return {
        "lineage_id": lineage_id, **context,
        "upstream_model_id": "Q1-B1",
        "prediction_variant": "seq_time_bounded",
        "postprocess_version": "q1_clip_0_test_dur_v1",
        "prediction_role": role,
        "prediction_groups": sorted(predicted),
        "prediction_group_count": len(predicted),
        "prediction_row_count": int(len(prediction_index)),
        "prediction_sha256": _prediction_hash(
            row_keys(frame.iloc[prediction_index]).tolist(), prediction
        ),
        "upstream_fit_groups_hash": stable_group_hash(fitted),
        "upstream_fit_group_count": len(fitted),
        "prediction_fit_overlap_count": 0,
        "downstream_validation_fit_overlap_count": 0,
        "forbidden_group_count": len(forbidden_groups),
    }


def q1_crossfit(
    features: pd.DataFrame, frame: pd.DataFrame,
    train_index: np.ndarray, validation_index: np.ndarray,
    inner_specs: list[dict[str, Any]], context: dict[str, Any],
    state: RunState,
) -> tuple[
    np.ndarray, np.ndarray, np.ndarray, Pipeline,
    list[dict[str, Any]], list[dict[str, Any]],
]:
    columns = list(features.columns)
    train_groups = set(group_id(frame.iloc[train_index]))
    held_groups = set(group_id(frame.iloc[validation_index]))
    all_groups = group_id(frame).to_numpy()
    oof = np.full(len(frame), np.nan, dtype=float)
    lineages, rows = [], []

    for spec in inner_specs:
        targets = spec["validation_groups"] & train_groups
        inner_valid = train_index[np.isin(all_groups[train_index], list(targets))]
        inner_train = train_index[~np.isin(all_groups[train_index], list(targets))]
        if not len(inner_valid) or not len(inner_train):
            raise AssertionError("empty frozen Q1 cross-fit fold")
        model = q1_pipeline(columns)
        state.fit(
            model, features.iloc[inner_train],
            frame.iloc[inner_train]["seq_time"].to_numpy(float),
            f"{context}:Q1-B1:inner-{spec['inner_fold']}",
        )
        raw = np.asarray(model.predict(features.iloc[inner_valid]), dtype=float)
        bounded = np.clip(
            raw, 0.0,
            frame.iloc[inner_valid]["test_dur"].to_numpy(float),
        )
        oof[inner_valid] = bounded
        role = (
            "outer_train_oof" if context["scope"] == "PRIMARY"
            else "loso_train_oof"
        )
        lineage = _lineage(
            {**context, "inner_fold": int(spec["inner_fold"])}, role,
            frame, inner_valid, inner_train, held_groups, bounded,
        )
        lineages.append(lineage)
        for local, index in enumerate(inner_valid):
            rows.append({
                "row_key": row_keys(frame.iloc[[index]]).iloc[0],
                "group_id": all_groups[index],
                "source_file": str(frame.at[index, "source_file"]),
                "test_id": int(frame.at[index, "test_id"]),
                "ap_id": str(frame.at[index, "ap_id"]),
                **context, "prediction_role": role,
                "lineage_id": lineage["lineage_id"],
                "seq_time_bounded": float(bounded[local]),
            })
    if np.isnan(oof[train_index]).any():
        raise AssertionError("Q1 OOF does not cover downstream training rows")

    full = q1_pipeline(columns)
    state.fit(
        full, features.iloc[train_index],
        frame.iloc[train_index]["seq_time"].to_numpy(float),
        f"{context}:Q1-B1:full",
    )
    raw = np.asarray(full.predict(features.iloc[validation_index]), dtype=float)
    bounded = np.clip(
        raw, 0.0,
        frame.iloc[validation_index]["test_dur"].to_numpy(float),
    )
    role = (
        "outer_validation_inference" if context["scope"] == "PRIMARY"
        else "loso_validation_inference"
    )
    lineage = _lineage(
        context, role, frame, validation_index, train_index,
        held_groups, bounded,
    )
    lineages.append(lineage)
    for local, index in enumerate(validation_index):
        rows.append({
            "row_key": row_keys(frame.iloc[[index]]).iloc[0],
            "group_id": all_groups[index],
            "source_file": str(frame.at[index, "source_file"]),
            "test_id": int(frame.at[index, "test_id"]),
            "ap_id": str(frame.at[index, "ap_id"]),
            **context, "prediction_role": role,
            "lineage_id": lineage["lineage_id"],
            "seq_time_bounded": float(bounded[local]),
        })
    return oof[train_index], raw, bounded, full, lineages, rows


def aligned_probabilities(
    model: Pipeline, features: pd.DataFrame, labels: list[str],
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    local = np.asarray(model.predict_proba(features), dtype=float)
    classes = [str(x) for x in model.named_steps["model"].classes_]
    aligned = np.zeros((len(features), len(labels)), dtype=float)
    for source, label in enumerate(classes):
        aligned[:, labels.index(label)] = local[:, source]
    if not np.allclose(aligned.sum(axis=1), 1.0, atol=1e-10, rtol=0):
        raise AssertionError("fixed-label probabilities do not sum to one")
    prediction = np.asarray(
        [labels[index] for index in np.argmax(aligned, axis=1)], dtype=str
    )
    return prediction, aligned, [x for x in labels if x not in classes]


def majority_prediction(
    train_labels: np.ndarray, size: int, labels: list[str],
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    counts = Counter(str(x) for x in train_labels)
    winner = max(labels, key=lambda x: (counts[x], -labels.index(x)))
    prediction = np.repeat(winner, size)
    probability = np.zeros((size, len(labels)), dtype=float)
    probability[:, labels.index(winner)] = 1.0
    return prediction, probability, [x for x in labels if counts[x] == 0]


def permute_family_by_group(
    features: pd.DataFrame, frame: pd.DataFrame,
    columns: list[str], seed: int,
) -> pd.DataFrame:
    output = features.copy()
    rng = np.random.default_rng(seed)
    groups = group_id(frame)
    counts = frame.groupby(["source_file", "test_id"])["ap_id"].transform("size")
    for ap_count in sorted(counts.unique()):
        ids = sorted(groups.loc[counts.eq(ap_count)].unique())
        donors = list(rng.permutation(ids))
        for target, donor in zip(ids, donors, strict=True):
            target_index = list(frame.index[groups.eq(target)])
            donor_index = list(frame.index[groups.eq(donor)])
            target_index.sort(key=lambda x: str(frame.at[x, "ap_id"]))
            donor_index.sort(key=lambda x: str(frame.at[x, "ap_id"]))
            output.loc[target_index, columns] = features.loc[
                donor_index, columns
            ].to_numpy()
    return output
