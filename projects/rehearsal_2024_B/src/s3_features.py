"""Deterministic, topology-aware S3 feature engine.

This module never reads files.  It transforms an already guarded training
frame and deliberately excludes identifiers, targets, and post-event fields.
"""

from __future__ import annotations

import math
import re
from collections import OrderedDict
from typing import Any

import numpy as np
import pandas as pd

from s1_data_audit import parse_rssi

CELL_STATS = ("median", "q10", "q90", "iqr", "valid_count", "missing")
ANT_STATS = ("sum", "max", "mean")
PEER_REDUCERS = ("strongest", "weakest", "mean", "available_count", "missing_fraction")
CATEGORICAL_FEATURES = ("basic__protocol",)


def _entity_index(value: Any) -> int:
    text = str(value).strip().lower()
    match = re.search(r"(\d+)$", text)
    if match is None:
        raise ValueError(f"cannot derive numeric entity index from {value!r}")
    return int(match.group(1))


def _cell_summary(value: Any) -> dict[str, float]:
    kind, values = parse_rssi(value)
    if kind == "invalid":
        raise ValueError(f"invalid RSSI cell: {value!r}")
    if not values:
        return {
            "median": np.nan,
            "q10": np.nan,
            "q90": np.nan,
            "iqr": np.nan,
            "valid_count": 0.0,
            "missing": 1.0,
        }
    array = np.asarray(values, dtype=float)
    q10, q25, q50, q75, q90 = np.quantile(array, [0.10, 0.25, 0.50, 0.75, 0.90])
    return {
        "median": float(q50),
        "q10": float(q10),
        "q90": float(q90),
        "iqr": float(q75 - q25),
        "valid_count": float(array.size),
        "missing": 0.0,
    }


def _direct_features(
    row: pd.Series,
    relation: str,
    focal: int,
    prefix: str,
    output: OrderedDict[str, Any],
) -> None:
    for ant_stat in ANT_STATS:
        column = f"{relation}_{focal}_{ant_stat}_ant_rssi"
        summary = _cell_summary(row[column]) if column in row.index else _cell_summary(np.nan)
        for statistic in CELL_STATS:
            output[f"{prefix}__{ant_stat}__{statistic}"] = summary[statistic]


def _peer_cell_summaries(
    row: pd.Series,
    relation: str,
    focal: int,
    ap_count: int,
    ant_stat: str | None,
) -> list[dict[str, float]]:
    summaries: list[dict[str, float]] = []
    for peer in range(ap_count):
        if peer == focal:
            continue
        if ant_stat is None:
            column = f"{relation}_{peer}_rssi"
        else:
            column = f"{relation}_{peer}_{ant_stat}_ant_rssi"
        summaries.append(
            _cell_summary(row[column]) if column in row.index else _cell_summary(np.nan)
        )
    return summaries


def _aggregate_peer(
    summaries: list[dict[str, float]],
    prefix: str,
    output: OrderedDict[str, Any],
) -> None:
    for statistic in ("median", "q10", "q90", "iqr", "valid_count"):
        values = np.asarray([item[statistic] for item in summaries], dtype=float)
        finite = values[np.isfinite(values)]
        output[f"{prefix}__{statistic}__strongest"] = (
            float(np.max(finite)) if finite.size else np.nan
        )
        output[f"{prefix}__{statistic}__weakest"] = (
            float(np.min(finite)) if finite.size else np.nan
        )
        output[f"{prefix}__{statistic}__mean"] = (
            float(np.mean(finite)) if finite.size else np.nan
        )
        output[f"{prefix}__{statistic}__available_count"] = float(finite.size)
        output[f"{prefix}__{statistic}__missing_fraction"] = (
            float(1.0 - finite.size / len(values)) if len(values) else 1.0
        )


def _value(row: pd.Series, column: str) -> float:
    value = pd.to_numeric(pd.Series([row.get(column)]), errors="coerce").iloc[0]
    return float(value) if pd.notna(value) else np.nan


def _mechanism_features(
    row: pd.Series,
    focal: int,
    ap_count: int,
    output: OrderedDict[str, Any],
) -> None:
    peer_max = _peer_cell_summaries(row, "ap_from_ap", focal, ap_count, "max")
    peer_mean = _peer_cell_summaries(row, "ap_from_ap", focal, ap_count, "mean")
    max_medians = np.asarray([item["median"] for item in peer_max], dtype=float)
    mean_medians = np.asarray([item["median"] for item in peer_mean], dtype=float)
    max_finite = max_medians[np.isfinite(max_medians)]
    mean_finite = mean_medians[np.isfinite(mean_medians)]
    strongest_max = float(np.max(max_finite)) if max_finite.size else np.nan
    strongest_mean = float(np.max(mean_finite)) if mean_finite.size else np.nan
    pd_threshold = _value(row, "pd")
    ed_threshold = _value(row, "ed")
    nav_threshold = _value(row, "nav")

    for label, threshold in (("pd", pd_threshold), ("ed", ed_threshold)):
        margins = max_finite - threshold if max_finite.size and np.isfinite(threshold) else np.asarray([])
        output[f"mechanism__peer_max_minus_{label}__strongest"] = (
            float(np.max(margins)) if margins.size else np.nan
        )
        output[f"mechanism__peer_max_above_{label}__count"] = (
            float(np.sum(margins > 0)) if margins.size else 0.0
        )
        output[f"mechanism__peer_max_above_{label}__fraction"] = (
            float(np.mean(margins > 0)) if margins.size else np.nan
        )

    nav_margins = (
        mean_finite - nav_threshold
        if mean_finite.size and np.isfinite(nav_threshold)
        else np.asarray([])
    )
    output["mechanism__peer_mean_minus_nav__strongest"] = (
        float(np.max(nav_margins)) if nav_margins.size else np.nan
    )
    output["mechanism__peer_mean_above_nav__count"] = (
        float(np.sum(nav_margins > 0)) if nav_margins.size else 0.0
    )
    output["mechanism__peer_mean_above_nav__fraction"] = (
        float(np.mean(nav_margins > 0)) if nav_margins.size else np.nan
    )

    for relation, label in (
        ("sta_to_ap", "desired_sta_to_focal"),
        ("sta_from_ap", "desired_sta_from_focal"),
    ):
        column = f"{relation}_{focal}_max_ant_rssi"
        desired = _cell_summary(row[column])["median"] if column in row.index else np.nan
        output[f"mechanism__{label}_minus_strongest_peer_ap"] = (
            float(desired - strongest_max)
            if np.isfinite(desired) and np.isfinite(strongest_max)
            else np.nan
        )
    output["mechanism__peer_ap_mean_signal_minus_nav"] = (
        float(strongest_mean - nav_threshold)
        if np.isfinite(strongest_mean) and np.isfinite(nav_threshold)
        else np.nan
    )


def build_feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Return label-free, fixed-width features in source row order."""

    records: list[OrderedDict[str, Any]] = []
    group_sizes = frame.groupby(["source_file", "test_id"], sort=False).size()
    grouped = {
        (str(source), int(test_id)): group.copy()
        for (source, test_id), group in frame.groupby(
            ["source_file", "test_id"], sort=False
        )
    }

    for _, row in frame.iterrows():
        source = str(row["source_file"])
        test_id = int(row["test_id"])
        group = grouped[(source, test_id)]
        ap_count = int(group_sizes.loc[(source, test_id)])
        focal = _entity_index(row["ap_id"])
        if focal < 0 or focal >= ap_count:
            raise ValueError(
                f"focal AP index {focal} outside group size {ap_count}: "
                f"{source}::{test_id}"
            )

        output: OrderedDict[str, Any] = OrderedDict()
        output["basic__test_dur"] = _value(row, "test_dur")
        output["basic__pkt_len"] = _value(row, "pkt_len")
        output["basic__pd"] = _value(row, "pd")
        output["basic__ed"] = _value(row, "ed")
        output["basic__nav"] = _value(row, "nav")
        output["basic__eirp"] = _value(row, "eirp")
        output["basic__ap_count"] = float(ap_count)
        protocol = row.get("protocol")
        output["basic__protocol"] = (
            str(protocol).strip().lower() if pd.notna(protocol) else np.nan
        )

        _direct_features(
            row, "sta_to_ap", focal, "desired_sta_to_focal", output
        )
        _direct_features(
            row, "sta_from_ap", focal, "desired_sta_from_focal", output
        )

        for relation, prefix in (
            ("ap_from_ap", "peer_ap_to_focal"),
            ("sta_to_ap", "focal_sta_to_peer_ap"),
            ("sta_from_ap", "focal_sta_from_peer_ap"),
        ):
            for ant_stat in ANT_STATS:
                summaries = _peer_cell_summaries(
                    row, relation, focal, ap_count, ant_stat
                )
                _aggregate_peer(
                    summaries, f"{prefix}__{ant_stat}", output
                )

        _aggregate_peer(
            _peer_cell_summaries(
                row, "sta_from_sta", focal, ap_count, None
            ),
            "peer_sta_to_focal_sta",
            output,
        )
        _mechanism_features(row, focal, ap_count, output)

        peer_rows = group.loc[
            group["ap_id"].map(_entity_index).ne(focal)
        ]
        peer_eirp = pd.to_numeric(peer_rows["eirp"], errors="coerce").to_numpy(
            dtype=float
        )
        finite_eirp = peer_eirp[np.isfinite(peer_eirp)]
        focal_eirp = _value(row, "eirp")
        output["group_context__peer_eirp__strongest"] = (
            float(np.max(finite_eirp)) if finite_eirp.size else np.nan
        )
        output["group_context__peer_eirp__weakest"] = (
            float(np.min(finite_eirp)) if finite_eirp.size else np.nan
        )
        output["group_context__peer_eirp__mean"] = (
            float(np.mean(finite_eirp)) if finite_eirp.size else np.nan
        )
        output["group_context__focal_minus_peer_eirp_mean"] = (
            float(focal_eirp - np.mean(finite_eirp))
            if np.isfinite(focal_eirp) and finite_eirp.size
            else np.nan
        )
        peer_protocol = peer_rows["protocol"].astype("string").str.lower()
        output["group_context__peer_tcp__count"] = float(
            peer_protocol.eq("tcp").sum()
        )
        output["group_context__peer_tcp__fraction"] = (
            float(peer_protocol.eq("tcp").mean()) if len(peer_protocol) else np.nan
        )
        records.append(output)

    features = pd.DataFrame.from_records(records, index=frame.index)
    if tuple(features.columns).count("basic__protocol") != 1:
        raise AssertionError("feature schema must contain one protocol column")
    numeric = features.drop(columns=list(CATEGORICAL_FEATURES))
    values = numeric.to_numpy(dtype=float)
    if np.isinf(values).any():
        raise AssertionError("feature engine emitted infinite values")
    return features


def feature_family(name: str) -> str:
    if name.startswith("basic__"):
        return "basic"
    if name.startswith("desired_"):
        return "desired_rssi"
    if name.startswith("mechanism__"):
        return "mechanism"
    if name.startswith("group_context__"):
        return "group_context"
    return "peer_rssi"


def feature_families(columns: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for column in columns:
        result.setdefault(feature_family(column), []).append(column)
    return {key: value for key, value in sorted(result.items())}


def _unit_for(name: str) -> str:
    if name == "basic__test_dur":
        return "s"
    if name == "basic__pkt_len":
        return "byte"
    if name == "basic__ap_count" or name.endswith("__count") or "valid_count" in name or "available_count" in name:
        return "count"
    if name == "basic__protocol":
        return "categorical"
    if name.endswith("__fraction") or "missing_fraction" in name or name.endswith("__missing"):
        return "dimensionless"
    if "rssi" in name or "minus_" in name or name in {
        "basic__pd", "basic__ed", "basic__nav", "basic__eirp"
    } or "eirp" in name:
        return "dBm or dB difference"
    return "dimensionless"


def build_feature_schema(features: pd.DataFrame) -> dict[str, Any]:
    rows = []
    for position, name in enumerate(features.columns):
        categorical = name in CATEGORICAL_FEATURES
        rows.append(
            {
                "name": name,
                "dtype": "string" if categorical else "float64",
                "unit": _unit_for(name),
                "missing_semantics": (
                    "unknown protocol; fold-local most-frequent imputation and "
                    "one-hot unknown-category handling"
                    if categorical
                    else "NaN means unavailable source signal/statistic; fold-local "
                    "median imputation with an explicit missing indicator"
                ),
                "column_order": position,
                "family": feature_family(name),
            }
        )
    return {
        "schema_version": "s3_feature_schema_v1",
        "engine": "topology_aware_rssi_v1",
        "training_side_only": True,
        "raw_feature_count": len(rows),
        "categorical_features": list(CATEGORICAL_FEATURES),
        "families": feature_families(list(features.columns)),
        "features": rows,
    }
