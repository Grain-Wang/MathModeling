"""Run all eight G2-approved S3 Baselines.

Usage:
  conda run -n math_modeling python \
    projects/rehearsal_2024_B/src/s3_baseline.py
"""

from __future__ import annotations

import argparse
import time
from collections import defaultdict

import numpy as np
import pandas as pd

from s1_data_audit import EXPECTED
from s2_contract_validation import group_id, label_of
from s3_evaluation import (
    a03_sensitivity,
    bootstrap,
    evaluate_q1,
    evaluate_q2,
    evaluate_q3,
    strata,
)
from s3_features import build_feature_frame, build_feature_schema
from s3_io import (
    CONFIG_PATH,
    EXPERIMENTS,
    OUTPUT,
    PROJECT,
    REGISTRY_PATH,
    RunState,
    canonical_relative,
    dump,
    dump_jsonl,
    environment_metadata,
    git,
    load_guarded_training,
    load_json,
    now,
    preflight,
    sha256,
)
from s3_lineage import inner_specs_loso, inner_specs_primary
from s3_models import influence_summary, run_fold, system_records


def _run_configs(metadata: dict, labels: list[str]) -> dict[str, dict]:
    common = {
        "stage": "S3", "git_head": metadata["git_head"],
        "command": (
            "conda run -n math_modeling python "
            "projects/rehearsal_2024_B/src/s3_baseline.py"
        ),
        "config_sha256": metadata["config_sha256"],
        "split_registry_sha256": metadata["split_registry_sha256"],
        "split_registry_core_sha256": metadata["split_registry_core_sha256"],
        "feature_schema_sha256": metadata["feature_schema_sha256"],
        "primary_split": "3 repeats x 5 frozen grouped outer folds",
        "mandatory_stress": "13 source-blind LOSO folds",
        "threads": 1, "official_test_numeric_read_count": 0,
    }
    return {
        "q1_baseline.json": {
            **common,
            "runs": {
                "EXP-S3-Q1-B0": {
                    "model": "DummyRegressor", "strategy": "median"
                },
                "EXP-S3-Q1-B1": {
                    "model": "Ridge", "alpha": 1.0, "solver": "lsqr",
                    "primary_prediction": "seq_time_bounded",
                },
            },
        },
        "q2_baseline.json": {
            **common, "fixed_label_order": labels,
            "runs": {
                "EXP-S3-Q2-B0": {"model": "most-frequent joint label"},
                "EXP-S3-Q2-B1A": {
                    "model": "LogisticRegression", "C": 1.0,
                    "upstream_q1": False,
                },
                "EXP-S3-Q2-B1B": {
                    "model": "LogisticRegression", "C": 1.0,
                    "upstream_q1": "Q1-B1 bounded cross-fit",
                },
            },
        },
        "q3_baseline.json": {
            **common,
            "runs": {
                "EXP-S3-Q3-B0": {
                    "model": "DummyRegressor", "strategy": "median"
                },
                "EXP-S3-Q3-B1": {
                    "model": "Ridge", "alpha": 1.0, "solver": "lsqr",
                    "upstream_q1": "Q1-B1 bounded cross-fit",
                },
                "EXP-S3-Q3-B2": {
                    "model": "constrained scalar efficiency",
                    "eta_bounds": [0.0, 1.0],
                    "rate_missing_fallback": "fold-local Q3-B1",
                },
            },
        },
    }


def _primary_counts(outputs: dict, systems: list[dict]) -> dict:
    result = {}
    for key, models, rows, row_name in [
        ("q1", 2, outputs["q1"], "rows_per_model_repeat"),
        ("q2", 3, outputs["q2"], "rows_per_model_repeat"),
        ("q3_ap", 3, outputs["q3"], "rows_per_model_repeat"),
        ("q3_system", 3, systems, "rows_per_model_repeat"),
    ]:
        frame = pd.DataFrame(rows)
        frame = frame[frame.scope.eq("PRIMARY")]
        counts = {
            model: {
                str(int(repeat)): int(len(part))
                for repeat, part in frame[frame.model_id.eq(model)].groupby("repeat")
            }
            for model in sorted(frame.model_id.unique())
        }
        expected_rows = 482 if key == "q3_system" else 1250
        if len(counts) != models or any(
            set(values.values()) != {expected_rows} for values in counts.values()
        ):
            raise AssertionError(f"incomplete primary output: {key}")
        result[key] = {row_name: counts}
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--bootstrap-replicates", type=int, default=1000)
    args = parser.parse_args()
    started, timer = now(), time.perf_counter()
    state = RunState()
    status_before_outputs = git("status", "--short")
    config, registry = load_json(CONFIG_PATH), load_json(REGISTRY_PATH)
    paths, preflight_evidence, core_sha = preflight(config, registry, state)
    if args.verify_only:
        print("status=PASS")
        print("mode=verify-only")
        print("model_fit_count=0")
        print("csv_numeric_read_count=0")
        print("official_test_numeric_read_count=0")
        return 0

    labels = list(config["q2"]["global_joint_labels"])
    eligible = load_guarded_training(paths, state)
    observed = sorted(
        {
            label_of(nss, mcs)
            for nss, mcs in zip(eligible.nss, eligible.mcs, strict=True)
        },
        key=lambda x: tuple(int(value) for value in x.split("|")),
    )
    if observed != labels:
        raise AssertionError("eligible labels differ from fixed 17-label order")

    features = build_feature_frame(eligible)
    if len(features) != len(eligible):
        raise AssertionError("feature/eligible row mismatch")
    schema = build_feature_schema(features)
    two = eligible[
        eligible.source_file.map(lambda x: EXPECTED[str(x)]["ap_count"] == 2)
    ]
    three = eligible[
        eligible.source_file.map(lambda x: EXPECTED[str(x)]["ap_count"] == 3)
    ]
    two_columns = list(build_feature_frame(two).columns)
    three_columns = list(build_feature_frame(three).columns)
    schema["ap_count_alignment"] = {
        "two_ap_column_count": len(two_columns),
        "three_ap_column_count": len(three_columns),
        "same_order": (
            two_columns == three_columns == list(features.columns)
        ),
    }
    if not schema["ap_count_alignment"]["same_order"]:
        raise AssertionError("2-AP and 3-AP feature schemas do not align")
    dump(OUTPUT / "feature_schema.json", schema)
    feature_sha = sha256(OUTPUT / "feature_schema.json")

    outputs = {
        key: [] for key in [
            "q1", "q2", "q3", "lineage", "crossfit", "fold_status",
            "influence", "coefficients",
        ]
    }
    all_groups = group_id(eligible).to_numpy()
    outer: dict[tuple[int, int], set[str]] = defaultdict(set)
    for item in registry["outer_assignments"]:
        outer[(int(item["repeat"]), int(item["validation_fold"]))].add(
            f"{item['source_file']}::{int(item['test_id'])}"
        )
    for (repeat, fold), validation_groups in sorted(outer.items()):
        valid_index = np.flatnonzero(
            np.isin(all_groups, list(validation_groups))
        )
        train_index = np.flatnonzero(
            ~np.isin(all_groups, list(validation_groups))
        )
        run_fold(
            features, eligible, train_index, valid_index,
            inner_specs_primary(registry, repeat, fold),
            {"scope": "PRIMARY", "repeat": repeat, "fold": fold},
            labels, state, outputs, run_influence=True,
        )

    for item in sorted(
        registry["leave_one_source_file_out"],
        key=lambda x: int(x["split"]),
    ):
        split, held = int(item["split"]), str(item["held_out_source_file"])
        held_mask = eligible.source_file.astype(str).eq(held).to_numpy()
        run_fold(
            features, eligible, np.flatnonzero(~held_mask),
            np.flatnonzero(held_mask), inner_specs_loso(registry, split),
            {
                "scope": "LOSO", "loso_split": split,
                "held_out_source_file": held,
            },
            labels, state, outputs, run_influence=False,
        )

    systems = system_records(outputs["q3"])
    counts = _primary_counts(outputs, systems)
    lineage = {
        "batch_count": len(outputs["lineage"]),
        "primary_batch_count": sum(
            x["scope"] == "PRIMARY" for x in outputs["lineage"]
        ),
        "loso_batch_count": sum(
            x["scope"] == "LOSO" for x in outputs["lineage"]
        ),
        "prediction_fit_overlap_total": sum(
            x["prediction_fit_overlap_count"] for x in outputs["lineage"]
        ),
        "held_out_fit_overlap_total": sum(
            x["downstream_validation_fit_overlap_count"]
            for x in outputs["lineage"]
        ),
        "fixed_upstream_identity": all(
            x["upstream_model_id"] == "Q1-B1"
            and x["prediction_variant"] == "seq_time_bounded"
            and x["postprocess_version"] == "q1_clip_0_test_dur_v1"
            for x in outputs["lineage"]
        ),
    }
    if lineage != {
        "batch_count": 112, "primary_batch_count": 60,
        "loso_batch_count": 52, "prediction_fit_overlap_total": 0,
        "held_out_fit_overlap_total": 0, "fixed_upstream_identity": True,
    }:
        raise AssertionError(f"actual lineage failed: {lineage}")

    q1_metrics = evaluate_q1(outputs["q1"])
    q2_metrics = evaluate_q2(outputs["q2"], labels)
    q3_metrics, q3_cdf = evaluate_q3(outputs["q3"], systems)
    boot = bootstrap(
        outputs["q1"], outputs["q2"], outputs["q3"], systems, labels,
        args.bootstrap_replicates,
        int(config["split_contract"]["bootstrap"]["random_state"]),
    )
    stratified = strata(
        outputs["q1"], outputs["q2"], outputs["q3"], labels
    )
    a03 = a03_sensitivity(outputs["q2"], outputs["q3"], systems, labels)
    influence = influence_summary(
        outputs["influence"], outputs["coefficients"]
    )

    dump_jsonl(OUTPUT / "q1_oof_predictions.jsonl.gz", outputs["q1"])
    dump_jsonl(
        OUTPUT / "q1_crossfit_for_downstream.jsonl.gz", outputs["crossfit"]
    )
    dump_jsonl(OUTPUT / "q2_oof_predictions.jsonl.gz", outputs["q2"])
    dump_jsonl(OUTPUT / "q3_ap_oof_predictions.jsonl.gz", outputs["q3"])
    dump_jsonl(OUTPUT / "q3_system_oof_predictions.jsonl.gz", systems)
    dump(OUTPUT / "q1_actual_upstream_lineage.json", {
        "contract": {
            "upstream_model_id": "Q1-B1",
            "prediction_variant": "seq_time_bounded",
            "postprocess_version": "q1_clip_0_test_dur_v1",
        },
        "assertions": lineage, "batches": outputs["lineage"],
    })
    dump(OUTPUT / "q1_metrics.json", q1_metrics)
    dump(OUTPUT / "q2_metrics.json", q2_metrics)
    dump(OUTPUT / "q3_metrics.json", q3_metrics)
    dump(OUTPUT / "q3_error_cdf.json", q3_cdf)
    dump(OUTPUT / "group_bootstrap_intervals.json", boot)
    dump(OUTPUT / "stratified_metrics.json", stratified)
    dump(OUTPUT / "a03_sensitivity.json", a03)
    dump(OUTPUT / "q1_feature_family_importance.json", influence)
    dump(OUTPUT / "q2_class_support.json", {
        "fixed_label_order": labels,
        "eligible_support": {
            label: sum(
                label_of(nss, mcs) == label
                for nss, mcs in zip(eligible.nss, eligible.mcs, strict=True)
            )
            for label in labels
        },
        "fold_status": outputs["fold_status"],
        "minority_collapse": {
            model: value["minority_collapse_by_repeat"]
            for model, value in q2_metrics["models"].items()
        },
    })

    finished = now()
    metadata = {
        "status": "PASS", "started_at": started, "finished_at": finished,
        "runtime_seconds": float(time.perf_counter() - timer),
        "git_head": git("rev-parse", "HEAD"),
        "git_status_before_outputs": status_before_outputs,
        **environment_metadata(),
        "config_sha256": sha256(CONFIG_PATH),
        "guard_sha256": sha256(PROJECT / "src" / "contract_guard.py"),
        "s3_entry_sha256": sha256(PROJECT / "src" / "s3_baseline.py"),
        "split_registry_sha256": sha256(REGISTRY_PATH),
        "split_registry_core_sha256": core_sha,
        "feature_schema_sha256": feature_sha,
        "eligible_rows": len(eligible),
        "eligible_groups": int(group_id(eligible).nunique()),
        "outer_fold_count": 15, "loso_split_count": 13,
        "baseline_run_count": 8,
        "model_fit_count": state.model_fit_count,
        "training_csv_numeric_read_count": state.csv_numeric_read_count,
        "official_test_hash_only_count": 4,
        "official_test_numeric_read_count": 0,
        "official_test_prediction_count": 0,
        "actual_lineage_assertions": lineage,
        "primary_output_counts": counts,
        "warning_count": len(state.warnings),
        "warnings": state.warnings,
    }
    for name, payload in _run_configs(metadata, labels).items():
        dump(EXPERIMENTS / name, payload)

    summary = {
        "status": "PASS", "metadata": metadata,
        "preflight_status": preflight_evidence["status"],
        "feature_schema": {
            "path": canonical_relative(OUTPUT / "feature_schema.json"),
            "sha256": feature_sha,
            "raw_feature_count": schema["raw_feature_count"],
            "two_three_ap_alignment": True,
        },
        "q1_primary": {
            model: value["primary_point_estimate_repeat_mean"]
            for model, value in q1_metrics["models"].items()
        },
        "q1_loso": {
            model: value["loso_overall"]
            for model, value in q1_metrics["models"].items()
        },
        "q2_primary": {
            model: value["primary_point_estimate_repeat_mean"]
            for model, value in q2_metrics["models"].items()
        },
        "q2_loso": {
            model: value["loso_overall"]
            for model, value in q2_metrics["models"].items()
        },
        "q3_primary": {
            model: value["primary_point_estimate_repeat_mean"]
            for model, value in q3_metrics["models"].items()
        },
        "q3_loso": {
            model: value["loso_overall"]
            for model, value in q3_metrics["models"].items()
        },
        "a03": a03, "lineage": lineage,
    }
    dump(OUTPUT / "baseline_summary.json", summary)
    dump(OUTPUT / "run_manifest.json", {
        **metadata, "preflight": preflight_evidence,
        "phase_input_manifest": preflight_evidence["entry"],
        "output_artifacts": [
            {
                "path": canonical_relative(path),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in sorted(OUTPUT.glob("*"))
            if path.is_file() and path.name != "run_manifest.json"
        ],
    })

    print("status=PASS")
    print(f"eligible_rows={len(eligible)}")
    print(f"eligible_groups={group_id(eligible).nunique()}")
    print("outer_folds=15")
    print("loso_splits=13")
    print(f"feature_count={schema['raw_feature_count']}")
    print(f"actual_lineage_batches={lineage['batch_count']}")
    print(f"model_fit_count={state.model_fit_count}")
    print("official_test_numeric_read_count=0")
    print("official_test_prediction_count=0")
    print(f"runtime_seconds={metadata['runtime_seconds']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
