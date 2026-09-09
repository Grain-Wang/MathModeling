"""Validate the S2 contracts without fitting any prediction model.

Only the 13 training CSV files are parsed. The four official test files are
hash-verified by the approved S1 contract but their numerical values are never
read. Split and lineage registries contain identities only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut

from contract_guard import ContractBoundaryError, validate_phase_input_manifest
from s1_data_audit import (
    DATA,
    EXPECTED,
    PROJECT,
    git,
    native,
    now,
    sha256,
    strict_identity_audit,
    training_frames,
    verify,
)

CONFIG_PATH = PROJECT / "configs" / "s2_experiment_plan.json"
GUARD_PATH = PROJECT / "src" / "contract_guard.py"
OUTPUT = PROJECT / "results" / "raw" / "s2"


def dump(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            default=native,
        )
        + "\n",
        encoding="utf-8",
    )


def label_of(nss: Any, mcs: Any) -> str:
    return f"{int(float(nss))}|{int(float(mcs))}"


def sorted_labels(labels: set[str]) -> list[str]:
    return sorted(labels, key=lambda item: tuple(int(x) for x in item.split("|")))


def group_id(frame: pd.DataFrame) -> pd.Series:
    return (
        frame["source_file"].astype(str)
        + "::"
        + frame["test_id"].map(lambda value: str(int(value)))
    )


def group_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records = (
        frame[["source_file", "test_id"]]
        .drop_duplicates()
        .sort_values(["source_file", "test_id"])
    )
    return [
        {
            "source_file": str(row.source_file),
            "test_id": int(row.test_id),
            "ap_count": int(EXPECTED[str(row.source_file)]["ap_count"]),
        }
        for row in records.itertuples(index=False)
    ]


def support(frame: pd.DataFrame) -> dict[str, int]:
    values = [
        label_of(nss, mcs)
        for nss, mcs in zip(frame["nss"], frame["mcs"], strict=True)
    ]
    return dict(
        sorted(
            Counter(values).items(),
            key=lambda item: tuple(int(x) for x in item[0].split("|")),
        )
    )


def stable_group_hash(groups: set[str]) -> str:
    payload = "\n".join(sorted(groups)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def signed_error_contract(
    truth: list[float] | np.ndarray,
    prediction: list[float] | np.ndarray,
) -> dict[str, Any]:
    y = np.asarray(truth, dtype=float)
    yhat = np.asarray(prediction, dtype=float)
    if y.shape != yhat.shape or y.ndim != 1:
        raise ValueError("truth and prediction must be one-dimensional and aligned")
    if not np.isfinite(y).all() or not np.isfinite(yhat).all():
        raise ValueError("truth and prediction must be finite")
    zero = y == 0
    error = (yhat[~zero] - y[~zero]) / y[~zero]
    if len(error) == 0:
        raise ValueError("relative metrics require at least one nonzero truth")
    ordered = np.sort(error)
    rank = int(math.ceil(0.90 * len(ordered)))
    error_90 = float(ordered[rank - 1])
    absolute_ordered = np.sort(np.abs(error))
    absolute_error_90 = float(absolute_ordered[rank - 1])
    return {
        "defined_relative_count": int(len(error)),
        "excluded_zero_truth_count": int(zero.sum()),
        "zero_truth_absolute_errors": [
            float(value) for value in np.abs(yhat[zero] - y[zero])
        ],
        "signed_errors": [float(value) for value in error],
        "nearest_rank_one_indexed": rank,
        "error_90": error_90,
        "accuracy_90": float(1.0 - error_90),
        "absolute_relative_error_90": absolute_error_90,
    }


def synthetic_metric_tests() -> dict[str, Any]:
    direction = signed_error_contract([100, 100], [90, 120])
    zero = signed_error_contract([0, 100], [5, 90])
    ties = signed_error_contract(
        [100] * 10,
        [80, 90, 100, 110, 120, 120, 130, 140, 140, 150],
    )
    unbounded = signed_error_contract([100], [50])

    rows = pd.DataFrame(
        {
            "group": ["g1", "g1", "g2", "g2"],
            "truth": [40.0, 60.0, 20.0, 30.0],
            "prediction": [45.0, 65.0, 18.0, 27.0],
        }
    )
    sums = rows.groupby("group")[["truth", "prediction"]].sum()
    system = signed_error_contract(
        sums["truth"].to_numpy(), sums["prediction"].to_numpy()
    )

    checks = {
        "signed_direction": (
            np.allclose(direction["signed_errors"], [-0.1, 0.2])
            and np.isclose(direction["error_90"], 0.2)
            and np.isclose(direction["accuracy_90"], 0.8)
        ),
        "zero_denominator": (
            zero["excluded_zero_truth_count"] == 1
            and zero["defined_relative_count"] == 1
            and zero["zero_truth_absolute_errors"] == [5.0]
            and np.isclose(zero["error_90"], -0.1)
        ),
        "ties_and_nearest_rank": (
            ties["nearest_rank_one_indexed"] == 9
            and np.isclose(ties["error_90"], 0.4)
        ),
        "accuracy_not_clipped": np.isclose(unbounded["accuracy_90"], 1.5),
        "strict_system_sum": (
            np.allclose(sums["truth"].to_numpy(), [100.0, 50.0])
            and np.allclose(sums["prediction"].to_numpy(), [110.0, 45.0])
            and np.allclose(system["signed_errors"], [0.1, -0.1])
        ),
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "examples": {
            "signed_direction": direction,
            "zero_denominator": zero,
            "ties_and_nearest_rank": ties,
            "accuracy_not_clipped": unbounded,
            "system_sum": system,
        },
    }


def lineage_batch(
    fit_groups: set[str],
    prediction_groups: set[str],
    forbidden_fit_groups: set[str],
    role: str,
    context: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    prediction_fit_overlap = fit_groups & prediction_groups
    forbidden_fit_overlap = fit_groups & forbidden_fit_groups
    if prediction_fit_overlap:
        raise AssertionError(
            f"{role}: prediction groups entered upstream fit groups"
        )
    if forbidden_fit_overlap:
        raise AssertionError(
            f"{role}: downstream validation or held-out groups entered upstream fit"
        )

    upstream = config["upstream_feature_contract"]
    payload = {
        **context,
        "prediction_role": role,
        "prediction_mode": "OOF" if role.endswith("_oof") else "INFERENCE",
        "upstream_model_id": upstream["estimator_id"],
        "prediction_variant": upstream["prediction_variant"],
        "postprocess_version": upstream["postprocess_version"],
        "prediction_groups": sorted(prediction_groups),
        "prediction_group_count": len(prediction_groups),
        "prediction_groups_hash": stable_group_hash(prediction_groups),
        "upstream_fit_groups_hash": stable_group_hash(fit_groups),
        "upstream_fit_group_count": len(fit_groups),
        "prediction_fit_overlap_count": len(prediction_fit_overlap),
        "downstream_validation_fit_overlap_count": len(forbidden_fit_overlap),
    }
    lineage_core = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "lineage_id": hashlib.sha256(lineage_core).hexdigest().upper(),
        **payload,
    }


def synthetic_lineage_tests(config: dict[str, Any]) -> dict[str, Any]:
    good = lineage_batch(
        {"a", "b"},
        {"c"},
        {"d"},
        "synthetic_training_oof",
        {"fixture": "clean"},
        config,
    )

    def rejected(
        fit_groups: set[str],
        prediction_groups: set[str],
        forbidden_groups: set[str],
    ) -> bool:
        try:
            lineage_batch(
                fit_groups,
                prediction_groups,
                forbidden_groups,
                "synthetic_training_oof",
                {"fixture": "must_reject"},
                config,
            )
        except AssertionError:
            return True
        return False

    checks = {
        "clean_lineage_accepted": good["prediction_fit_overlap_count"] == 0
        and good["downstream_validation_fit_overlap_count"] == 0,
        "in_sample_prediction_rejected": rejected(
            {"a", "c"}, {"c"}, {"d"}
        ),
        "downstream_validation_label_bleed_rejected": rejected(
            {"a", "d"}, {"c"}, {"d"}
        ),
        "fixed_upstream_identity": (
            good["upstream_model_id"] == "Q1-B1"
            and good["prediction_variant"] == "seq_time_bounded"
            and good["postprocess_version"] == "q1_clip_0_test_dur_v1"
        ),
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "clean_example": good,
    }


def synthetic_test_release_guard_tests(
    config: dict[str, Any],
) -> dict[str, Any]:
    policy = config["test_release_contract"]
    training_file = policy["training_file_allowlist"][0]
    official_files = policy["official_test_denylist"]

    protected = validate_phase_input_manifest(
        {
            "phase": "S3",
            "input_kind": "training_csv",
            "input_files": [training_file],
        },
        config,
    )

    def rejected(manifest: dict[str, Any]) -> bool:
        try:
            validate_phase_input_manifest(manifest, config)
        except ContractBoundaryError:
            return True
        return False

    early_test_rejected = rejected(
        {
            "phase": "S3",
            "input_kind": "training_csv",
            "input_files": [official_files[0]],
        }
    )
    incomplete_release_rejected = rejected(
        {
            "phase": policy["final_release_phase"],
            "input_kind": "official_test_csv",
            "input_files": official_files,
            "gate_state": "G4_PASS",
            "prior_release_count": 0,
            "freeze_manifest": {"selection_closed": True},
            "feedback_targets": [],
        }
    )

    freeze = {
        field: "LOCKED"
        for field in policy["required_freeze_fields"]
    }
    freeze["selection_closed"] = True
    final_release = validate_phase_input_manifest(
        {
            "phase": policy["final_release_phase"],
            "input_kind": "official_test_csv",
            "input_files": official_files,
            "gate_state": policy["minimum_gate_state"],
            "prior_release_count": 0,
            "freeze_manifest": freeze,
            "feedback_targets": [],
        },
        config,
    )

    checks = {
        "protected_training_manifest_accepted": protected["status"] == "PASS",
        "early_official_test_rejected": early_test_rejected,
        "incomplete_freeze_manifest_rejected": incomplete_release_rejected,
        "complete_first_release_accepted": (
            final_release["status"] == "PASS"
            and final_release["mode"] == "ONE_TIME_FINAL_RELEASE_AUTHORIZED"
        ),
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "protected_example": protected,
        "final_release_example": final_release,
        "official_test_numeric_read_count": 0,
    }


def normalized_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace(
        "\r", "\n"
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def contract_artifact_verification(
    config: dict[str, Any],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for item in config["contract_artifacts"]["files"]:
        path = PROJECT / item["path"]
        expected = str(item["sha256"]).upper()
        actual = normalized_text_sha256(path)
        records.append(
            {
                "path": item["path"],
                "expected_sha256": expected,
                "actual_sha256": actual,
                "exists": path.is_file(),
                "match": expected == actual,
            }
        )
    return {
        "status": (
            "PASS"
            if records
            and all(record["exists"] and record["match"] for record in records)
            else "FAIL"
        ),
        "hash_algorithm": config["contract_artifacts"]["hash_algorithm"],
        "files": records,
    }


def append_nested_upstream_batches(
    frame: pd.DataFrame,
    seed: int,
    forbidden_groups: set[str],
    role: str,
    context: dict[str, Any],
    config: dict[str, Any],
    output: list[dict[str, Any]],
) -> int:
    groups = group_id(frame)
    all_groups = set(groups)
    splitter = GroupKFold(
        n_splits=int(config["split_contract"]["nested_upstream"]["n_splits"]),
        shuffle=True,
        random_state=int(seed),
    )
    seen: set[str] = set()
    assignment_count = 0
    x = np.zeros((len(frame), 1))
    for fold, (fit_index, prediction_index) in enumerate(
        splitter.split(x, groups=groups)
    ):
        fit_groups = set(groups.iloc[fit_index])
        prediction_groups = set(groups.iloc[prediction_index])
        if seen & prediction_groups:
            raise AssertionError("nested upstream group assigned twice")
        seen |= prediction_groups
        batch = lineage_batch(
            fit_groups,
            prediction_groups,
            forbidden_groups,
            role,
            {
                **context,
                "nested_upstream_random_state": int(seed),
                "nested_upstream_validation_fold": int(fold),
            },
            config,
        )
        output.append(batch)
        assignment_count += len(prediction_groups)
    if seen != all_groups:
        raise AssertionError("nested upstream registry does not cover training groups")
    return assignment_count


def split_registry(
    eligible: pd.DataFrame,
    config: dict[str, Any],
    labels: list[str],
) -> dict[str, Any]:
    primary = config["split_contract"]["primary"]
    groups = group_id(eligible)
    x = np.zeros((len(eligible), 1))
    outer_assignments: list[dict[str, Any]] = []
    inner_assignments: list[dict[str, Any]] = []
    outer_stats: list[dict[str, Any]] = []
    primary_lineage: list[dict[str, Any]] = []
    loso_lineage: list[dict[str, Any]] = []
    loso_inner_batches: list[dict[str, Any]] = []
    base = int(config["split_contract"]["inner_selection"]["random_state_base"])
    nested_base = int(
        config["split_contract"]["nested_upstream"]["random_state_base"]
    )
    nested_assignment_count = 0

    for repeat_index, seed in enumerate(primary["random_states"]):
        splitter = GroupKFold(
            n_splits=int(primary["n_splits"]),
            shuffle=True,
            random_state=int(seed),
        )
        repeat_seen: set[str] = set()
        for fold, (train_index, validation_index) in enumerate(
            splitter.split(x, groups=groups)
        ):
            train = eligible.iloc[train_index].copy()
            validation = eligible.iloc[validation_index].copy()
            train_groups = set(group_id(train))
            validation_groups = set(group_id(validation))
            if train_groups & validation_groups:
                raise AssertionError("outer train/validation group overlap")
            if repeat_seen & validation_groups:
                raise AssertionError("outer group assigned to multiple folds")
            repeat_seen |= validation_groups

            for record in group_records(validation):
                outer_assignments.append(
                    {
                        "repeat": repeat_index,
                        "random_state": int(seed),
                        "validation_fold": int(fold),
                        **record,
                    }
                )

            train_support = support(train)
            validation_support = support(validation)
            outer_stats.append(
                {
                    "repeat": repeat_index,
                    "random_state": int(seed),
                    "fold": int(fold),
                    "train_rows": int(len(train)),
                    "validation_rows": int(len(validation)),
                    "train_groups": int(len(train_groups)),
                    "validation_groups": int(len(validation_groups)),
                    "validation_groups_by_ap_count": dict(
                        sorted(
                            Counter(
                                int(EXPECTED[str(row.source_file)]["ap_count"])
                                for row in validation[["source_file", "test_id"]]
                                .drop_duplicates()
                                .itertuples(index=False)
                            ).items()
                        )
                    ),
                    "validation_source_file_counts": {
                        str(key): int(value)
                        for key, value in validation.groupby("source_file")[
                            "test_id"
                        ]
                        .nunique()
                        .sort_index()
                        .items()
                    },
                    "train_label_support": train_support,
                    "validation_label_support": validation_support,
                    "missing_train_labels": [
                        label for label in labels if label not in train_support
                    ],
                    "missing_validation_labels": [
                        label
                        for label in labels
                        if label not in validation_support
                    ],
                }
            )

            inner_seed = base + repeat_index * 100 + fold
            inner_groups = group_id(train)
            inner_x = np.zeros((len(train), 1))
            inner_splitter = GroupKFold(
                n_splits=int(
                    config["split_contract"]["inner_selection"]["n_splits"]
                ),
                shuffle=True,
                random_state=inner_seed,
            )
            inner_seen: set[str] = set()
            for inner_fold, (
                inner_train_index,
                inner_validation_index,
            ) in enumerate(inner_splitter.split(inner_x, groups=inner_groups)):
                inner_train = train.iloc[inner_train_index].copy()
                inner_validation = train.iloc[inner_validation_index].copy()
                inner_train_groups = set(group_id(inner_train))
                inner_validation_groups = set(group_id(inner_validation))
                if inner_train_groups & inner_validation_groups:
                    raise AssertionError("inner train/validation group overlap")
                if inner_seen & inner_validation_groups:
                    raise AssertionError("inner group assigned twice")
                if inner_validation_groups & validation_groups:
                    raise AssertionError("outer validation group entered inner CV")
                inner_seen |= inner_validation_groups

                for record in group_records(inner_validation):
                    inner_assignments.append(
                        {
                            "outer_repeat": repeat_index,
                            "outer_random_state": int(seed),
                            "outer_fold": int(fold),
                            "inner_random_state": int(inner_seed),
                            "inner_validation_fold": int(inner_fold),
                            **record,
                        }
                    )

                base_context = {
                    "scope": "PRIMARY",
                    "outer_repeat": repeat_index,
                    "outer_random_state": int(seed),
                    "outer_fold": int(fold),
                    "downstream_inner_random_state": int(inner_seed),
                    "downstream_inner_validation_fold": int(inner_fold),
                }
                primary_lineage.append(
                    lineage_batch(
                        inner_train_groups,
                        inner_validation_groups,
                        validation_groups,
                        "outer_train_oof",
                        base_context,
                        config,
                    )
                )
                primary_lineage.append(
                    lineage_batch(
                        inner_train_groups,
                        inner_validation_groups,
                        validation_groups | inner_validation_groups,
                        "downstream_inner_validation_inference",
                        base_context,
                        config,
                    )
                )

                nested_seed = (
                    nested_base
                    + repeat_index * 1000
                    + fold * 100
                    + inner_fold
                )
                nested_assignment_count += append_nested_upstream_batches(
                    inner_train,
                    nested_seed,
                    validation_groups | inner_validation_groups,
                    "downstream_inner_train_oof",
                    base_context,
                    config,
                    primary_lineage,
                )

            if inner_seen != train_groups:
                raise AssertionError(
                    "inner registry does not cover outer training groups"
                )

            primary_lineage.append(
                lineage_batch(
                    train_groups,
                    validation_groups,
                    validation_groups,
                    "outer_validation_inference",
                    {
                        "scope": "PRIMARY",
                        "outer_repeat": repeat_index,
                        "outer_random_state": int(seed),
                        "outer_fold": int(fold),
                    },
                    config,
                )
            )

        if len(repeat_seen) != int(primary["expected_groups"]):
            raise AssertionError("outer repeat does not cover every eligible group")

    logo = LeaveOneGroupOut()
    source = eligible["source_file"].astype(str)
    loso_stats: list[dict[str, Any]] = []
    loso_inner_assignment_count = 0
    loso_nested_assignment_count = 0
    loso_contract = config["split_contract"]["loso_selection"]

    for split_index, (train_index, validation_index) in enumerate(
        logo.split(x, groups=source)
    ):
        train = eligible.iloc[train_index].copy()
        validation = eligible.iloc[validation_index].copy()
        validation_sources = sorted(
            validation["source_file"].astype(str).unique()
        )
        if len(validation_sources) != 1:
            raise AssertionError("LOSO validation must contain one source file")
        held_out_source = validation_sources[0]
        if held_out_source in set(train["source_file"].astype(str)):
            raise AssertionError("held-out source entered LOSO training")
        train_groups = set(group_id(train))
        validation_groups = set(group_id(validation))
        if train_groups & validation_groups:
            raise AssertionError("LOSO train/validation group overlap")

        loso_lineage.append(
            lineage_batch(
                train_groups,
                validation_groups,
                validation_groups,
                "loso_validation_inference",
                {
                    "scope": "LOSO",
                    "loso_split": int(split_index),
                    "held_out_source_file": held_out_source,
                },
                config,
            )
        )

        train_support = support(train)
        loso_stats.append(
            {
                "split": int(split_index),
                "held_out_source_file": held_out_source,
                "train_rows": int(len(train)),
                "validation_rows": int(len(validation)),
                "train_groups": int(len(train_groups)),
                "validation_groups": int(len(validation_groups)),
                "selection_train_groups_hash": stable_group_hash(train_groups),
                "held_out_group_fit_overlap_count": 0,
                "train_label_support": train_support,
                "validation_label_support": support(validation),
                "missing_train_labels": [
                    label for label in labels if label not in train_support
                ],
            }
        )

        loso_inner_seed = 502409 + split_index
        loso_inner_groups = group_id(train)
        loso_inner_x = np.zeros((len(train), 1))
        loso_inner_splitter = GroupKFold(
            n_splits=int(loso_contract["downstream_inner_splits"]),
            shuffle=True,
            random_state=loso_inner_seed,
        )
        loso_inner_seen: set[str] = set()
        for inner_fold, (
            inner_train_index,
            inner_validation_index,
        ) in enumerate(
            loso_inner_splitter.split(loso_inner_x, groups=loso_inner_groups)
        ):
            inner_train = train.iloc[inner_train_index].copy()
            inner_validation = train.iloc[inner_validation_index].copy()
            inner_train_groups = set(group_id(inner_train))
            inner_validation_groups = set(group_id(inner_validation))
            if inner_train_groups & inner_validation_groups:
                raise AssertionError("LOSO inner group overlap")
            if loso_inner_seen & inner_validation_groups:
                raise AssertionError("LOSO inner group assigned twice")
            if validation_groups & (inner_train_groups | inner_validation_groups):
                raise AssertionError("held-out source entered LOSO selection")
            loso_inner_seen |= inner_validation_groups
            loso_inner_assignment_count += len(inner_validation_groups)

            context = {
                "scope": "LOSO",
                "loso_split": int(split_index),
                "held_out_source_file": held_out_source,
                "downstream_inner_random_state": int(loso_inner_seed),
                "downstream_inner_validation_fold": int(inner_fold),
            }
            loso_inner_batches.append(
                {
                    **context,
                    "training_group_count": len(inner_train_groups),
                    "training_groups_hash": stable_group_hash(
                        inner_train_groups
                    ),
                    "validation_groups": sorted(inner_validation_groups),
                    "validation_group_count": len(inner_validation_groups),
                    "validation_groups_hash": stable_group_hash(
                        inner_validation_groups
                    ),
                    "held_out_group_overlap_count": 0,
                }
            )
            loso_lineage.append(
                lineage_batch(
                    inner_train_groups,
                    inner_validation_groups,
                    validation_groups | inner_validation_groups,
                    "loso_inner_validation_inference",
                    context,
                    config,
                )
            )
            loso_nested_seed = (
                602409 + split_index * 100 + inner_fold * 10
            )
            loso_nested_assignment_count += append_nested_upstream_batches(
                inner_train,
                loso_nested_seed,
                validation_groups | inner_validation_groups,
                "loso_inner_train_oof",
                context,
                config,
                loso_lineage,
            )
        if loso_inner_seen != train_groups:
            raise AssertionError(
                "LOSO inner registry does not cover training groups"
            )

    all_lineage = primary_lineage + loso_lineage
    lineage_assertions = {
        "batch_count": len(all_lineage),
        "prediction_fit_overlap_total": sum(
            row["prediction_fit_overlap_count"] for row in all_lineage
        ),
        "downstream_validation_fit_overlap_total": sum(
            row["downstream_validation_fit_overlap_count"]
            for row in all_lineage
        ),
        "fixed_upstream_identity_all_batches": all(
            row["upstream_model_id"] == "Q1-B1"
            and row["prediction_variant"] == "seq_time_bounded"
            and row["postprocess_version"] == "q1_clip_0_test_dur_v1"
            for row in all_lineage
        ),
    }

    core = {
        "outer_assignments": outer_assignments,
        "inner_assignments": inner_assignments,
        "outer_fold_statistics": outer_stats,
        "primary_upstream_lineage_batches": primary_lineage,
        "leave_one_source_file_out": loso_stats,
        "loso_downstream_inner_batches": loso_inner_batches,
        "loso_upstream_lineage_batches": loso_lineage,
    }
    core_hash = hashlib.sha256(
        json.dumps(
            core,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest().upper()
    return {
        "contract": {
            "atomic_group": ["source_file", "test_id"],
            "primary": primary,
            "inner_selection": config["split_contract"]["inner_selection"],
            "nested_upstream": config["split_contract"]["nested_upstream"],
            "mandatory_stress": config["split_contract"]["mandatory_stress"],
            "loso_selection": config["split_contract"]["loso_selection"],
            "aggregation": config["split_contract"]["aggregation"],
            "upstream_feature": config["upstream_feature_contract"],
        },
        "eligible_rows": int(len(eligible)),
        "eligible_groups": int(groups.nunique()),
        "outer_assignment_count": len(outer_assignments),
        "inner_assignment_count": len(inner_assignments),
        "nested_upstream_assignment_count": nested_assignment_count,
        "outer_fold_count": len(outer_stats),
        "primary_lineage_batch_count": len(primary_lineage),
        "loso_split_count": len(loso_stats),
        "loso_inner_assignment_count": loso_inner_assignment_count,
        "loso_nested_upstream_assignment_count": (
            loso_nested_assignment_count
        ),
        "loso_lineage_batch_count": len(loso_lineage),
        "lineage_assertions": lineage_assertions,
        "registry_core_sha256": core_hash,
        **core,
    }


def load_training() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    frames = {
        name: pd.read_csv(DATA / name)
        for name, spec in EXPECTED.items()
        if spec["role"] == "train"
    }
    _, eligible = training_frames(frames)
    return frames, eligible


def summary_md(
    metadata: dict[str, Any],
    validation: dict[str, Any],
    registry: dict[str, Any],
) -> str:
    return "\n".join(
        [
            "# S2 Contract Validation Summary — G2 Round 2",
            "",
            f"- Generated: {metadata['generated_at']}",
            f"- Git HEAD before outputs: {metadata['git_head']}",
            f"- Worktree before outputs: {'clean' if not metadata['git_status_porcelain_before_outputs'] else 'dirty'}",
            f"- Verdict: {validation['status']}",
            f"- Contract artifact hashes: {validation['contract_artifact_verification']['status']}",
            f"- Input verification before/after: {validation['input_verification_before']['status']} / {validation['input_verification_after']['status']}",
            f"- Eligible rows/groups: {registry['eligible_rows']} / {registry['eligible_groups']}",
            f"- Outer folds: {registry['outer_fold_count']} (3 repeats x 5 folds)",
            f"- Frozen outer/downstream-inner/nested-upstream assignments: {registry['outer_assignment_count']} / {registry['inner_assignment_count']} / {registry['nested_upstream_assignment_count']}",
            f"- Primary upstream lineage batches: {registry['primary_lineage_batch_count']}",
            f"- Leave-one-source-file-out splits: {registry['loso_split_count']}",
            f"- LOSO inner/nested assignments: {registry['loso_inner_assignment_count']} / {registry['loso_nested_upstream_assignment_count']}",
            f"- LOSO upstream lineage batches: {registry['loso_lineage_batch_count']}",
            f"- Q2 global labels: {validation['q2_label_contract']['global_label_count']}",
            f"- Q3 synthetic metric tests: {validation['q3_synthetic_metric_tests']['status']}",
            f"- Synthetic lineage leakage tests: {validation['synthetic_lineage_tests']['status']}",
            f"- Synthetic official-test guard tests: {validation['synthetic_test_release_guard_tests']['status']}",
            f"- Split registry SHA-256: {registry['registry_core_sha256']}",
            "",
            "No prediction model was fitted. Official test CSV numerical values were not read.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    before = verify()
    if before["status"] != "PASS":
        print(json.dumps(before, ensure_ascii=False, indent=2))
        return 2

    contract_artifacts = contract_artifact_verification(config)
    frames, eligible = load_training()
    identity = strict_identity_audit(eligible, "S2 eligible training")
    if not identity["strict_pass"]:
        print(json.dumps(identity, ensure_ascii=False, indent=2))
        return 3

    observed = support(eligible)
    observed_labels = sorted_labels(set(observed))
    configured_labels = config["q2"]["global_joint_labels"]
    if observed_labels != configured_labels:
        print(
            json.dumps(
                {
                    "configured": configured_labels,
                    "observed": observed_labels,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 4

    config["split_contract"]["primary"]["expected_groups"] = int(
        group_id(eligible).nunique()
    )
    registry = split_registry(eligible, config, configured_labels)
    metric_tests = synthetic_metric_tests()
    lineage_tests = synthetic_lineage_tests(config)
    release_tests = synthetic_test_release_guard_tests(config)
    after = verify()

    nested_expected = int(
        config["split_contract"]["nested_upstream"][
            "expected_primary_group_assignments"
        ]
    )
    loso_contract = config["split_contract"]["loso_selection"]
    checks = {
        "schema_v2": config["schema_version"]
        == "rehearsal_2024_B.s2_contract.v2",
        "contract_artifact_hashes": contract_artifacts["status"] == "PASS",
        "input_before": before["status"] == "PASS",
        "input_after": after["status"] == "PASS",
        "input_hashes_unchanged": before["files"] == after["files"],
        "eligible_identity": identity["strict_pass"],
        "eligible_rows": len(eligible) == 1250,
        "eligible_groups": group_id(eligible).nunique() == 482,
        "q2_labels_match": observed_labels == configured_labels,
        "outer_fold_count": registry["outer_fold_count"] == 15,
        "outer_assignment_count": registry["outer_assignment_count"]
        == 482 * 3,
        "inner_assignment_count": registry["inner_assignment_count"] == 5784,
        "nested_upstream_assignment_count": (
            registry["nested_upstream_assignment_count"] == nested_expected
        ),
        "loso_split_count": registry["loso_split_count"] == 13,
        "loso_inner_assignment_count": (
            registry["loso_inner_assignment_count"]
            == int(loso_contract["expected_inner_group_assignments"])
        ),
        "loso_nested_assignment_count": (
            registry["loso_nested_upstream_assignment_count"]
            == int(
                loso_contract[
                    "expected_nested_upstream_group_assignments"
                ]
            )
        ),
        "lineage_prediction_fit_overlap_zero": (
            registry["lineage_assertions"][
                "prediction_fit_overlap_total"
            ]
            == 0
        ),
        "lineage_downstream_validation_fit_overlap_zero": (
            registry["lineage_assertions"][
                "downstream_validation_fit_overlap_total"
            ]
            == 0
        ),
        "lineage_identity_fixed": registry["lineage_assertions"][
            "fixed_upstream_identity_all_batches"
        ],
        "q3_synthetic_metrics": metric_tests["status"] == "PASS",
        "synthetic_lineage_leakage": lineage_tests["status"] == "PASS",
        "synthetic_test_release_guard": release_tests["status"] == "PASS",
        "stage_boundary": config["status"]
        == "CONTRACT_ONLY_NO_MODEL_FIT",
        "upstream_estimator_fixed": (
            config["upstream_feature_contract"]["estimator_id"] == "Q1-B1"
            and config["upstream_feature_contract"]["prediction_variant"]
            == "seq_time_bounded"
            and config["upstream_feature_contract"]["postprocess_version"]
            == "q1_clip_0_test_dur_v1"
            and not config["upstream_feature_contract"][
                "q1_hgb_candidate_may_replace_downstream_upstream"
            ]
        ),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    metadata = {
        "generated_at": now(),
        "git_head": git("rev-parse", "HEAD"),
        "git_status_porcelain_before_outputs": git("status", "--porcelain"),
        "script": "src/s2_contract_validation.py",
        "script_sha256": sha256(Path(__file__)),
        "guard_script": "src/contract_guard.py",
        "guard_script_sha256": sha256(GUARD_PATH),
        "config": "configs/s2_experiment_plan.json",
        "config_sha256": sha256(CONFIG_PATH),
        "stage": "S2",
        "model_fit_count": 0,
        "official_test_numeric_read_count": 0,
        "official_test_prediction_count": 0,
        "official_test_run_manifest_count": 0,
    }
    validation = {
        "status": status,
        "checks": checks,
        "metadata": metadata,
        "contract_artifact_verification": contract_artifacts,
        "input_verification_before": before,
        "input_verification_after": after,
        "input_hashes_unchanged_during_validation": before["files"]
        == after["files"],
        "eligible_identity": identity,
        "q2_label_contract": {
            "encoding": "nss|mcs",
            "global_labels": configured_labels,
            "global_label_count": len(configured_labels),
            "observed_support": observed,
            "missing_training_class_policy": config["q2"][
                "missing_training_class_policy"
            ],
            "macro_f1_policy": config["q2"]["metric_policy"],
        },
        "upstream_feature_contract": config["upstream_feature_contract"],
        "repeated_cv_metric_contract": config[
            "repeated_cv_metric_contract"
        ],
        "q3_synthetic_metric_tests": metric_tests,
        "synthetic_lineage_tests": lineage_tests,
        "synthetic_test_release_guard_tests": release_tests,
        "test_release_contract": config["test_release_contract"],
        "nav_unit_resolution": {
            "value": "NAV threshold",
            "unit": "dBm",
            "statement_location": "Section 4.1.3 threshold information",
            "sample_levels_from_approved_training_audit": [-88, -86, -82],
        },
        "model_fit_count": 0,
        "official_test_numeric_read_count": 0,
        "official_test_prediction_count": 0,
    }

    print(f"contract_validation={status}")
    print(f"eligible_rows={len(eligible)}")
    print(f"eligible_groups={group_id(eligible).nunique()}")
    print(f"q2_global_labels={len(configured_labels)}")
    print(f"outer_folds={registry['outer_fold_count']}")
    print(
        "nested_upstream_assignments="
        f"{registry['nested_upstream_assignment_count']}"
    )
    print(f"loso_splits={registry['loso_split_count']}")
    print(
        "loso_nested_upstream_assignments="
        f"{registry['loso_nested_upstream_assignment_count']}"
    )
    print(f"lineage_batches={registry['lineage_assertions']['batch_count']}")
    print(f"q3_synthetic_tests={metric_tests['status']}")
    print(f"lineage_synthetic_tests={lineage_tests['status']}")
    print(f"test_release_guard_tests={release_tests['status']}")
    print(f"contract_artifact_hashes={contract_artifacts['status']}")
    if args.verify_only:
        return 0 if status == "PASS" else 5

    OUTPUT.mkdir(parents=True, exist_ok=True)
    dump(
        OUTPUT / "split_registry.json",
        {
            "metadata": metadata,
            **registry,
        },
    )
    dump(OUTPUT / "contract_validation.json", validation)
    (OUTPUT / "contract_summary.md").write_text(
        summary_md(metadata, validation, registry),
        encoding="utf-8",
    )
    return 0 if status == "PASS" else 5


if __name__ == "__main__":
    raise SystemExit(main())
