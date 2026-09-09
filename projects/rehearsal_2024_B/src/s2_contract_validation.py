"""Validate the S2 contracts without fitting any prediction model.

This script reads training CSV files only. Official test files are hash-verified by
the approved S1 manifest contract but are never parsed for numerical values.
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
OUTPUT = PROJECT / "results" / "raw" / "s2"


def dump(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
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
    return dict(sorted(Counter(values).items(), key=lambda item: tuple(
        int(x) for x in item[0].split("|")
    )))


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

    rows = pd.DataFrame({
        "group": ["g1", "g1", "g2", "g2"],
        "truth": [40.0, 60.0, 20.0, 30.0],
        "prediction": [45.0, 65.0, 18.0, 27.0],
    })
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
    base = int(config["split_contract"]["inner_selection"]["random_state_base"])

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
                outer_assignments.append({
                    "repeat": repeat_index,
                    "random_state": int(seed),
                    "validation_fold": int(fold),
                    **record,
                })

            train_support = support(train)
            validation_support = support(validation)
            outer_stats.append({
                "repeat": repeat_index,
                "random_state": int(seed),
                "fold": int(fold),
                "train_rows": int(len(train)),
                "validation_rows": int(len(validation)),
                "train_groups": int(len(train_groups)),
                "validation_groups": int(len(validation_groups)),
                "validation_groups_by_ap_count": dict(sorted(Counter(
                    int(EXPECTED[str(row.source_file)]["ap_count"])
                    for row in validation[["source_file", "test_id"]]
                    .drop_duplicates()
                    .itertuples(index=False)
                ).items())),
                "validation_source_file_counts": {
                    str(key): int(value)
                    for key, value in validation.groupby("source_file")[
                        "test_id"
                    ].nunique().sort_index().items()
                },
                "train_label_support": train_support,
                "validation_label_support": validation_support,
                "missing_train_labels": [
                    label for label in labels if label not in train_support
                ],
                "missing_validation_labels": [
                    label for label in labels if label not in validation_support
                ],
            })

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
            for inner_fold, (inner_train_index, inner_validation_index) in enumerate(
                inner_splitter.split(inner_x, groups=inner_groups)
            ):
                inner_train_groups = set(inner_groups.iloc[inner_train_index])
                inner_validation_groups = set(
                    inner_groups.iloc[inner_validation_index]
                )
                if inner_train_groups & inner_validation_groups:
                    raise AssertionError("inner train/validation group overlap")
                if inner_seen & inner_validation_groups:
                    raise AssertionError("inner group assigned twice")
                if inner_validation_groups & validation_groups:
                    raise AssertionError("outer validation group entered inner CV")
                inner_seen |= inner_validation_groups
                inner_validation = train.iloc[inner_validation_index]
                for record in group_records(inner_validation):
                    inner_assignments.append({
                        "outer_repeat": repeat_index,
                        "outer_random_state": int(seed),
                        "outer_fold": int(fold),
                        "inner_random_state": int(inner_seed),
                        "inner_validation_fold": int(inner_fold),
                        **record,
                    })
            if inner_seen != train_groups:
                raise AssertionError("inner registry does not cover outer training groups")

        if len(repeat_seen) != int(primary["expected_groups"]):
            raise AssertionError("outer repeat does not cover every eligible group")

    logo = LeaveOneGroupOut()
    source = eligible["source_file"].astype(str)
    loso_stats: list[dict[str, Any]] = []
    for split_index, (train_index, validation_index) in enumerate(
        logo.split(x, groups=source)
    ):
        train = eligible.iloc[train_index]
        validation = eligible.iloc[validation_index]
        validation_sources = sorted(validation["source_file"].astype(str).unique())
        if len(validation_sources) != 1:
            raise AssertionError("LOSO validation must contain one source file")
        train_support = support(train)
        loso_stats.append({
            "split": int(split_index),
            "held_out_source_file": validation_sources[0],
            "train_rows": int(len(train)),
            "validation_rows": int(len(validation)),
            "train_groups": int(group_id(train).nunique()),
            "validation_groups": int(group_id(validation).nunique()),
            "train_label_support": train_support,
            "validation_label_support": support(validation),
            "missing_train_labels": [
                label for label in labels if label not in train_support
            ],
        })

    core = {
        "outer_assignments": outer_assignments,
        "inner_assignments": inner_assignments,
        "outer_fold_statistics": outer_stats,
        "leave_one_source_file_out": loso_stats,
    }
    core_hash = hashlib.sha256(
        json.dumps(
            core, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest().upper()
    return {
        "contract": {
            "atomic_group": ["source_file", "test_id"],
            "primary": primary,
            "inner_selection": config["split_contract"]["inner_selection"],
            "mandatory_stress": config["split_contract"]["mandatory_stress"],
        },
        "eligible_rows": int(len(eligible)),
        "eligible_groups": int(groups.nunique()),
        "outer_assignment_count": len(outer_assignments),
        "inner_assignment_count": len(inner_assignments),
        "outer_fold_count": len(outer_stats),
        "loso_split_count": len(loso_stats),
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
    return "\n".join([
        "# S2 Contract Validation Summary",
        "",
        f"- Generated: {metadata['generated_at']}",
        f"- Git HEAD before outputs: {metadata['git_head']}",
        f"- Worktree before outputs: {'clean' if not metadata['git_status_porcelain_before_outputs'] else 'dirty'}",
        f"- Verdict: {validation['status']}",
        f"- Input verification before/after: {validation['input_verification_before']['status']} / {validation['input_verification_after']['status']}",
        f"- Eligible rows/groups: {registry['eligible_rows']} / {registry['eligible_groups']}",
        f"- Outer folds: {registry['outer_fold_count']} (3 repeats x 5 folds)",
        f"- Frozen outer/inner assignments: {registry['outer_assignment_count']} / {registry['inner_assignment_count']}",
        f"- Leave-one-source-file-out splits: {registry['loso_split_count']}",
        f"- Q2 global labels: {validation['q2_label_contract']['global_label_count']}",
        f"- Q3 synthetic metric tests: {validation['q3_synthetic_metric_tests']['status']}",
        f"- Split registry SHA-256: {registry['registry_core_sha256']}",
        "",
        "No prediction model was fitted. Official test CSV numerical values were not read.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    before = verify()
    if before["status"] != "PASS":
        print(json.dumps(before, ensure_ascii=False, indent=2))
        return 2

    frames, eligible = load_training()
    identity = strict_identity_audit(eligible, "S2 eligible training")
    if not identity["strict_pass"]:
        print(json.dumps(identity, ensure_ascii=False, indent=2))
        return 3

    observed = support(eligible)
    observed_labels = sorted_labels(set(observed))
    configured_labels = config["q2"]["global_joint_labels"]
    if observed_labels != configured_labels:
        print(json.dumps({
            "configured": configured_labels,
            "observed": observed_labels,
        }, ensure_ascii=False, indent=2))
        return 4

    config["split_contract"]["primary"]["expected_groups"] = int(
        group_id(eligible).nunique()
    )
    registry = split_registry(eligible, config, configured_labels)
    synthetic = synthetic_metric_tests()
    after = verify()

    checks = {
        "input_before": before["status"] == "PASS",
        "input_after": after["status"] == "PASS",
        "input_hashes_unchanged": before["files"] == after["files"],
        "eligible_identity": identity["strict_pass"],
        "eligible_rows": len(eligible) == 1250,
        "eligible_groups": group_id(eligible).nunique() == 482,
        "q2_labels_match": observed_labels == configured_labels,
        "outer_fold_count": registry["outer_fold_count"] == 15,
        "outer_assignment_count": registry["outer_assignment_count"] == 482 * 3,
        "loso_split_count": registry["loso_split_count"] == 13,
        "q3_synthetic_metrics": synthetic["status"] == "PASS",
        "stage_boundary": config["status"] == "CONTRACT_ONLY_NO_MODEL_FIT",
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    metadata = {
        "generated_at": now(),
        "git_head": git("rev-parse", "HEAD"),
        "git_status_porcelain_before_outputs": git("status", "--porcelain"),
        "script": "src/s2_contract_validation.py",
        "config": "configs/s2_experiment_plan.json",
        "config_sha256": sha256(CONFIG_PATH),
        "stage": "S2",
        "model_fit_count": 0,
        "official_test_numeric_read_count": 0,
    }
    validation = {
        "status": status,
        "checks": checks,
        "metadata": metadata,
        "input_verification_before": before,
        "input_verification_after": after,
        "input_hashes_unchanged_during_validation": before["files"] == after["files"],
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
        "q3_synthetic_metric_tests": synthetic,
        "nav_unit_resolution": {
            "value": "NAV threshold",
            "unit": "dBm",
            "statement_location": "Section 4.1.3 threshold information",
            "sample_levels_from_approved_training_audit": [-88, -86, -82],
        },
        "model_fit_count": 0,
        "official_test_numeric_read_count": 0,
    }

    print(f"contract_validation={status}")
    print(f"eligible_rows={len(eligible)}")
    print(f"eligible_groups={group_id(eligible).nunique()}")
    print(f"q2_global_labels={len(configured_labels)}")
    print(f"outer_folds={registry['outer_fold_count']}")
    print(f"loso_splits={registry['loso_split_count']}")
    print(f"q3_synthetic_tests={synthetic['status']}")
    if args.verify_only:
        return 0 if status == "PASS" else 5

    OUTPUT.mkdir(parents=True, exist_ok=True)
    dump(OUTPUT / "split_registry.json", {
        "metadata": metadata,
        **registry,
    })
    dump(OUTPUT / "contract_validation.json", validation)
    (OUTPUT / "contract_summary.md").write_text(
        summary_md(metadata, validation, registry),
        encoding="utf-8",
    )
    return 0 if status == "PASS" else 5


if __name__ == "__main__":
    raise SystemExit(main())
