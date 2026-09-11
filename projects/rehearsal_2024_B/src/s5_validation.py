"""Independent S5 evidence reconstruction, freeze, and final-release checks.

The pre-release phase reads only training-side artifacts plus byte identities for
the sealed official tests.  It deliberately does not import the production
evaluation functions.  The post-release phase validates the immutable ledger,
artifact hashes, row schemas, probability closure, and AP-to-system sums.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
SRC = PROJECT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from s1_data_audit import DATA, EXPECTED

RAW_BASE = PROJECT / "results" / "raw" / "baseline"
RAW_MAIN = PROJECT / "results" / "raw" / "main"
RAW_FINAL = PROJECT / "results" / "raw" / "final"
VERIFIED = PROJECT / "results" / "verified"
CONFIG = PROJECT / "configs" / "s2_experiment_plan.json"
S4_CONFIG = PROJECT / "configs" / "s4_candidate_plan.json"
OUTPUT_SCHEMA = PROJECT / "configs" / "s5_output_schema.json"
SPLITS = PROJECT / "results" / "raw" / "s2" / "split_registry.json"
G4_REVIEW = PROJECT / "reviews" / "gate_4_review.md"
G4_REVIEW_COMMIT = "70d6a1436192339c61c749188e104b15cf4bbbb7"
G4_REVIEWED_COMMIT = "b9922fd7752af80fb9ffa1d3ae7118192e0abd20"
LABELS = [
    "0|0", "1|0", "1|4", "1|5", "1|6", "1|7", "1|9",
    "2|2", "2|3", "2|4", "2|5", "2|6", "2|7", "2|8",
    "2|9", "2|10", "2|11",
]
SOURCE_FILES = [
    "contract_guard.py", "s1_data_audit.py", "s2_contract_validation.py",
    "s3_features.py", "s3_io.py", "s3_lineage.py", "s3_models.py",
    "s4_selection.py", "s5_release.py", "s5_validation.py",
]
CORE_COPIES = {
    RAW_BASE / "q1_metrics.json": VERIFIED / "q1_metrics.json",
    RAW_BASE / "q2_metrics.json": VERIFIED / "q2_baseline_metrics.json",
    RAW_BASE / "q3_metrics.json": VERIFIED / "q3_baseline_metrics.json",
    RAW_MAIN / "q2_candidate_metrics.json": VERIFIED / "q2_candidate_metrics.json",
    RAW_MAIN / "q3_candidate_metrics.json": VERIFIED / "q3_candidate_metrics.json",
    RAW_MAIN / "group_bootstrap_intervals.json": VERIFIED / "group_bootstrap_intervals.json",
    RAW_MAIN / "stratified_metrics.json": VERIFIED / "stratified_metrics.json",
    RAW_MAIN / "failure_cases.json": VERIFIED / "failure_cases.json",
}


def now() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True, stderr=subprocess.DEVNULL
    ).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_sha(payload: Any) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    opener = gzip.open if path.suffix == ".gz" else Path.open
    kwargs = {"mode": "rt", "encoding": "utf-8"} if path.suffix == ".gz" else {
        "mode": "r", "encoding": "utf-8"
    }
    with opener(path, **kwargs) as handle:  # type: ignore[arg-type]
        return [json.loads(line) for line in handle if line.strip()]


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tolerance)


def macro_f1(truth: list[str], prediction: list[str]) -> float:
    scores = []
    for label in LABELS:
        tp = sum(t == label and p == label for t, p in zip(truth, prediction, strict=True))
        fp = sum(t != label and p == label for t, p in zip(truth, prediction, strict=True))
        fn = sum(t == label and p != label for t, p in zip(truth, prediction, strict=True))
        denominator = 2 * tp + fp + fn
        scores.append(0.0 if denominator == 0 else 2.0 * tp / denominator)
    return float(np.mean(scores))


def nearest_rank_90(values: Iterable[float]) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise AssertionError("nearest-rank statistic has no positive denominator")
    return ordered[math.ceil(0.9 * len(ordered)) - 1]


def relative_summary(truth: list[float], prediction: list[float]) -> dict[str, float]:
    ratios = [
        (p - t) / t
        for t, p in zip(truth, prediction, strict=True)
        if t > 0
    ]
    return {
        "absolute_relative_error_90": nearest_rank_90(abs(value) for value in ratios),
        "median_signed_bias": float(np.median(np.asarray(ratios, dtype=float))),
    }


def verify_g4() -> dict[str, Any]:
    text = G4_REVIEW.read_text(encoding="utf-8")
    head = git("rev-parse", "HEAD")
    checks = {
        "verdict_pass": "Verdict: **PASS**" in text,
        "transition_authorized": "S4 -> S5 = AUTHORIZED" in text,
        "reviewed_commit": G4_REVIEWED_COMMIT in text,
        "review_commit_is_ancestor": git(
            "merge-base", G4_REVIEW_COMMIT, head
        ) == G4_REVIEW_COMMIT,
    }
    if not all(checks.values()):
        raise AssertionError(f"G4 authorization mismatch: {checks}")
    return {
        "status": "PASS", "path": relative(G4_REVIEW),
        "sha256": sha256(G4_REVIEW), "review_commit": G4_REVIEW_COMMIT,
        "reviewed_commit": G4_REVIEWED_COMMIT, "checks": checks,
    }


def verified_raw_hashes() -> dict[str, Any]:
    manifest = load(RAW_MAIN / "validation_manifest.json")
    records = []
    for item in manifest["consumed_artifacts"]:
        path = REPO / item["path"]
        actual = sha256(path)
        if actual != item["sha256"]:
            raise AssertionError(f"G4-validated artifact drift: {item['path']}")
        records.append({**item, "current_sha256": actual, "match": True})
    baseline_validation = load(RAW_BASE / "post_run_validation.json")
    main_validation = load(RAW_MAIN / "post_run_validation.json")
    if baseline_validation["status"] != "PASS" or main_validation["status"] != "PASS":
        raise AssertionError("S3/S4 validator status is not PASS")
    return {
        "status": "PASS", "g4_consumed_artifact_count": len(records),
        "g4_validation_manifest_sha256": sha256(RAW_MAIN / "validation_manifest.json"),
        "baseline_validation_sha256": sha256(RAW_BASE / "post_run_validation.json"),
        "main_validation_sha256": sha256(RAW_MAIN / "post_run_validation.json"),
        "records": records,
    }


def select_q2_from_trace(records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summaries = []
    for config_id in sorted({str(row["config_id"]) for row in records}):
        rows = [row for row in records if row["config_id"] == config_id]
        first = rows[0]
        summaries.append({
            "config_id": config_id,
            "config_index": int(first["config_index"]),
            "learning_rate": float(first["learning_rate"]),
            "max_leaf_nodes": int(first["max_leaf_nodes"]),
            "l2_regularization": float(first["l2_regularization"]),
            "inner_record_count": len(rows),
            "macro_f1_fixed_17": float(np.mean([row["macro_f1_fixed_17"] for row in rows])),
            "joint_accuracy": float(np.mean([row["joint_accuracy"] for row in rows])),
            "multiclass_log_loss": float(np.mean([row["multiclass_log_loss"] for row in rows])),
        })
    best_f1 = max(row["macro_f1_fixed_17"] for row in summaries)
    eligible = [row for row in summaries if best_f1 - row["macro_f1_fixed_17"] < 0.002]
    selected = min(eligible, key=lambda row: (
        -row["joint_accuracy"], row["multiclass_log_loss"],
        row["max_leaf_nodes"], row["config_index"],
    ))
    return dict(selected), summaries


def select_q3_from_trace(records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summaries = []
    for candidate_id in sorted({str(row["candidate_id"]) for row in records}):
        rows = [row for row in records if row["candidate_id"] == candidate_id]
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
            "selection_score": float(np.mean([row["selection_score"] for row in rows])),
            "mean_normalized_ap_system_mae": float(np.mean([
                row["mean_normalized_ap_system_mae"] for row in rows
            ])),
            "worst_absolute_median_signed_bias": float(np.mean([
                max(abs(row["per_ap_median_signed_bias"]), abs(row["system_median_signed_bias"]))
                for row in rows
            ])),
        })
    best_score = min(row["selection_score"] for row in summaries)
    eligible = [row for row in summaries if row["selection_score"] <= best_score * 1.005]
    selected = min(eligible, key=lambda row: (
        row["mean_normalized_ap_system_mae"],
        row["worst_absolute_median_signed_bias"],
        0 if row["architecture"] == "direct" else 1,
        row["max_leaf_nodes"], row["config_index"],
    ))
    return dict(selected), summaries


def q2_repeat_metrics(rows: list[dict[str, Any]], model_id: str) -> dict[int, dict[str, float]]:
    result = {}
    for repeat in (0, 1, 2):
        part = [
            row for row in rows
            if row["scope"] == "PRIMARY" and row["model_id"] == model_id
            and int(row["repeat"]) == repeat
        ]
        if len(part) != 1250 or len({row["row_key"] for row in part}) != 1250:
            raise AssertionError(f"Q2 coverage mismatch: {model_id}/repeat-{repeat}")
        truth = [str(row["truth_joint_label"]) for row in part]
        prediction = [str(row["predicted_joint_label"]) for row in part]
        result[repeat] = {
            "macro_f1_fixed_17": macro_f1(truth, prediction),
            "joint_accuracy": float(np.mean([t == p for t, p in zip(truth, prediction, strict=True)])),
        }
    return result


def q3_repeat_metrics(rows: list[dict[str, Any]], model_id: str) -> dict[int, dict[str, Any]]:
    result = {}
    for repeat in (0, 1, 2):
        part = [
            row for row in rows
            if row["scope"] == "PRIMARY" and row["model_id"] == model_id
            and int(row["repeat"]) == repeat
        ]
        if len(part) != 1250 or len({row["row_key"] for row in part}) != 1250:
            raise AssertionError(f"Q3 coverage mismatch: {model_id}/repeat-{repeat}")
        ap = relative_summary(
            [float(row["truth_throughput"]) for row in part],
            [float(row["throughput_bounded"]) for row in part],
        )
        groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
        for row in part:
            groups[(str(row["source_file"]), int(row["test_id"]))].append(row)
        if len(groups) != 482:
            raise AssertionError(f"Q3 group coverage mismatch: {model_id}/repeat-{repeat}")
        system_truth, system_prediction = [], []
        for group_rows in groups.values():
            expected = int(EXPECTED[str(group_rows[0]["source_file"])]["ap_count"])
            if len(group_rows) != expected:
                raise AssertionError("Q3 incomplete system group")
            system_truth.append(math.fsum(float(row["truth_throughput"]) for row in group_rows))
            system_prediction.append(math.fsum(float(row["throughput_bounded"]) for row in group_rows))
        system = relative_summary(system_truth, system_prediction)
        result[repeat] = {
            "per_ap": ap, "system_sum": system,
            "selection_score": max(
                ap["absolute_relative_error_90"],
                system["absolute_relative_error_90"],
            ),
        }
    return result


def mean_q3(repeats: dict[int, dict[str, Any]]) -> dict[str, Any]:
    return {
        "selection_score": float(np.mean([row["selection_score"] for row in repeats.values()])),
        "per_ap": {
            key: float(np.mean([row["per_ap"][key] for row in repeats.values()]))
            for key in ("absolute_relative_error_90", "median_signed_bias")
        },
        "system_sum": {
            key: float(np.mean([row["system_sum"][key] for row in repeats.values()]))
            for key in ("absolute_relative_error_90", "median_signed_bias")
        },
    }


def reconstruct_selection_and_promotion() -> dict[str, Any]:
    q2_selection = load(RAW_MAIN / "q2_selection.json")
    q3_selection = load(RAW_MAIN / "q3_selection.json")
    q2_primary_trace = [row for row in q2_selection["inner_trace"] if row["scope"] == "PRIMARY"]
    q3_primary_trace = [row for row in q3_selection["inner_trace"] if row["scope"] == "PRIMARY"]
    if len(q2_primary_trace) != 180 or len(q3_primary_trace) != 360:
        raise AssertionError("primary inner trace count mismatch")
    q2_selected, q2_summaries = select_q2_from_trace(q2_primary_trace)
    q3_selected, q3_summaries = select_q3_from_trace(q3_primary_trace)
    if q2_selected != q2_selection["global_full_data_selection"]:
        raise AssertionError("independent Q2 full-data selection mismatch")
    if q3_selected != q3_selection["global_full_data_selection"]:
        raise AssertionError("independent Q3 full-data selection mismatch")

    base_q2_rows = read_jsonl(RAW_BASE / "q2_oof_predictions.jsonl.gz")
    main_q2_rows = read_jsonl(RAW_MAIN / "q2_oof_predictions.jsonl.gz")
    base_q2 = q2_repeat_metrics(base_q2_rows, "Q2-B1A")
    base_q2_point = {
        key: float(np.mean([row[key] for row in base_q2.values()]))
        for key in ("macro_f1_fixed_17", "joint_accuracy")
    }
    q2_candidates = {}
    q2_eligible = []
    for model_id in sorted({row["model_id"] for row in main_q2_rows}):
        repeats = q2_repeat_metrics(main_q2_rows, model_id)
        point = {
            key: float(np.mean([row[key] for row in repeats.values()]))
            for key in ("macro_f1_fixed_17", "joint_accuracy")
        }
        improved = sum(
            repeats[index]["macro_f1_fixed_17"] > base_q2[index]["macro_f1_fixed_17"]
            for index in repeats
        )
        role = "dependency_ablation_not_promotion_candidate" if model_id == "Q2-M1-Q1-ABLATION" else "promotion_candidate"
        checks = {
            "macro_f1_gain_at_least_0_02": point["macro_f1_fixed_17"] - base_q2_point["macro_f1_fixed_17"] >= 0.02,
            "at_least_two_repeats_improve": improved >= 2,
            "accuracy_drop_no_more_than_0_01": point["joint_accuracy"] >= base_q2_point["joint_accuracy"] - 0.01,
            "eligible_role": role == "promotion_candidate",
        }
        q2_candidates[model_id] = {
            "role": role, "repeat_metrics": repeats, "point": point,
            "macro_f1_absolute_gain": point["macro_f1_fixed_17"] - base_q2_point["macro_f1_fixed_17"],
            "improved_repeat_count": improved, "checks": checks,
            "promotion_pass": all(checks.values()),
        }
        if all(checks.values()):
            q2_eligible.append(model_id)
    q2_final = max(
        q2_eligible, key=lambda model: q2_candidates[model]["point"]["macro_f1_fixed_17"]
    ) if q2_eligible else "Q2-B1A"

    base_q3_rows = read_jsonl(RAW_BASE / "q3_ap_oof_predictions.jsonl.gz")
    main_q3_rows = read_jsonl(RAW_MAIN / "q3_ap_oof_predictions.jsonl.gz")
    base_options = {}
    for model_id in ("Q3-B1", "Q3-B2"):
        repeats = q3_repeat_metrics(base_q3_rows, model_id)
        base_options[model_id] = {"repeat_metrics": repeats, "point": mean_q3(repeats)}
    base_q3_id = min(base_options, key=lambda model: base_options[model]["point"]["selection_score"])
    base_q3 = base_options[base_q3_id]
    q3_candidates = {}
    q3_eligible = []
    for model_id in sorted({row["model_id"] for row in main_q3_rows}):
        repeats = q3_repeat_metrics(main_q3_rows, model_id)
        point = mean_q3(repeats)
        improved = sum(
            repeats[index]["selection_score"] < base_q3["repeat_metrics"][index]["selection_score"]
            for index in repeats
        )
        relative_gain = (
            base_q3["point"]["selection_score"] - point["selection_score"]
        ) / base_q3["point"]["selection_score"]
        ap_limit = abs(base_q3["point"]["per_ap"]["median_signed_bias"]) + 0.02
        system_limit = abs(base_q3["point"]["system_sum"]["median_signed_bias"]) + 0.02
        checks = {
            "relative_score_gain_at_least_5_percent": relative_gain >= 0.05,
            "at_least_two_repeats_improve": improved >= 2,
            "per_ap_bias_guard": abs(point["per_ap"]["median_signed_bias"]) <= ap_limit,
            "system_bias_guard": abs(point["system_sum"]["median_signed_bias"]) <= system_limit,
        }
        q3_candidates[model_id] = {
            "repeat_metrics": repeats, "point": point,
            "relative_selection_score_gain": relative_gain,
            "improved_repeat_count": improved, "checks": checks,
            "promotion_pass": all(checks.values()),
        }
        if all(checks.values()):
            q3_eligible.append(model_id)
    q3_final = min(
        q3_eligible, key=lambda model: q3_candidates[model]["point"]["selection_score"]
    ) if q3_eligible else base_q3_id

    stored = load(RAW_MAIN / "promotion_decision.json")
    checks = {
        "q2_full_configuration_is_C3": q2_selected["config_id"] == "Q2-C3",
        "q2_fallback_reconstructed": q2_final == stored["q2"]["selected_model_id"] == "Q2-B1A",
        "q2_weighted_gain_below_threshold": q2_candidates["Q2-M1W-HGB-WEIGHTED"]["macro_f1_absolute_gain"] < 0.02,
        "q3_full_configuration_is_residual_C3": q3_selected["candidate_id"] == "Q3-physics_residual-C3",
        "q3_unified_promotion_reconstructed": q3_final == stored["q3"]["selected_model_id"] == "Q3-M1-HGB-UNIFIED",
        "q3_apcount_is_not_final": stored["q3"]["selected_model_id"] != "Q3-M1-HGB-APCOUNT",
    }
    if not all(checks.values()):
        raise AssertionError(f"independent selection/promotion mismatch: {checks}")
    return {
        "status": "PASS", "validator_independence": (
            "manual fixed-17 F1, nearest-rank ARE90, system grouping, selection, "
            "and promotion logic; production evaluate_q2/evaluate_q3 are not imported"
        ),
        "checks": checks,
        "q2": {
            "primary_inner_record_count": len(q2_primary_trace),
            "selected_full_data_configuration": q2_selected,
            "candidate_summaries": q2_summaries,
            "baseline_point": base_q2_point, "candidates": q2_candidates,
            "final_model_id": q2_final,
        },
        "q3": {
            "primary_inner_record_count": len(q3_primary_trace),
            "selected_full_data_configuration": q3_selected,
            "candidate_summaries": q3_summaries,
            "baseline_model_id": base_q3_id, "baseline": base_q3,
            "candidates": q3_candidates, "final_model_id": q3_final,
        },
    }


def training_inputs() -> tuple[list[dict[str, Any]], str]:
    records = []
    for name, spec in sorted(EXPECTED.items()):
        if spec["role"] != "train":
            continue
        path = DATA / name
        actual = sha256(path)
        if path.stat().st_size != spec["bytes"] or actual != spec["sha256"]:
            raise AssertionError(f"training input identity mismatch: {name}")
        records.append({"name": name, "bytes": spec["bytes"], "sha256": actual})
    return records, canonical_sha(records)


def official_identities() -> list[dict[str, Any]]:
    records = []
    for name, spec in EXPECTED.items():
        if spec["role"] == "train":
            continue
        path = DATA / name
        actual = sha256(path)
        if path.stat().st_size != spec["bytes"] or actual != spec["sha256"]:
            raise AssertionError(f"official test byte identity mismatch: {name}")
        records.append({
            "name": name, "role": spec["role"], "bytes": spec["bytes"],
            "rows": spec["rows"], "ap_count": spec["ap_count"],
            "sha256": actual, "access": "byte_identity_only_no_numeric_parse",
        })
    return records


def build_freeze(reconstruction: dict[str, Any], raw_hashes: dict[str, Any]) -> dict[str, Any]:
    config = load(CONFIG)
    final_candidate = load(RAW_MAIN / "final_candidate.json")
    output_schema = load(OUTPUT_SCHEMA)
    labels = list(config["q2"]["global_joint_labels"])
    if labels != LABELS:
        raise AssertionError("frozen Q2 label order drift")
    inputs, inputs_sha = training_inputs()
    sources = [{
        "path": relative(SRC / name), "sha256": sha256(SRC / name)
    } for name in SOURCE_FILES]
    source_sha = canonical_sha(sources)
    base_schema = RAW_BASE / "feature_schema.json"
    s4_schema = RAW_MAIN / "s4_feature_schema.json"
    schema_records = [
        {"path": relative(base_schema), "sha256": sha256(base_schema)},
        {"path": relative(s4_schema), "sha256": sha256(s4_schema)},
    ]
    models = {
        "q1": {
            "model_id": "Q1-B1", "estimator": "Ridge",
            "parameters": {"alpha": 1.0, "solver": "lsqr", "tol": 1e-8, "max_iter": 10000},
            "preprocess": "fold/full-training-side median imputation with indicators, StandardScaler, protocol one-hot",
            "prediction_variant": "seq_time_bounded",
            "postprocess_version": "q1_clip_0_test_dur_v1",
        },
        "q2": {
            "model_id": "Q2-B1A", "estimator": "LogisticRegression",
            "parameters": {"C": 1.0, "max_iter": 2000, "class_weight": None, "solver": "lbfgs"},
            "uses_q1": False,
            "preprocess": "full-training-side median imputation with indicators, StandardScaler, protocol one-hot",
        },
        "q3": {
            "pipeline_evidence_id": "Q3_NESTED_SELECTION_PIPELINE_PERFORMANCE",
            "configuration_evidence_id": "Q3_FINAL_FULL_DATA_CONFIGURATION",
            "model_id": "Q3-M1-HGB-UNIFIED",
            "configuration_id": "Q3-physics_residual-C3",
            "architecture": "physics_residual", "ap_count_split": False,
            "parameters": {
                "loss": "squared_error", "learning_rate": 0.05,
                "max_iter": 200, "max_leaf_nodes": 15,
                "min_samples_leaf": 20, "l2_regularization": 1.0,
                "early_stopping": False, "random_state": 202409,
            },
            "preprocess": (
                "actual code-faithful full-training-side median imputation with "
                "indicators, StandardScaler (including HGB numeric inputs), and protocol one-hot"
            ),
            "physical_base": {
                "eta": "full-training least squares on Q1 OOF physical proxy, clipped to [0,1]",
                "missing_rate_fallback": "Q3-B1 Ridge fit on all eligible training rows",
            },
            "q1_training_feature": (
                "mean of three registered primary Q1-B1 bounded outer-OOF predictions per row"
            ),
            "q1_deployment_feature": "Q1-B1 fitted on all eligible training rows",
            "postprocess_version": "q3_nonnegative_v1",
            "system_head": "strict sum of bounded AP predictions",
        },
    }
    if reconstruction["q2"]["final_model_id"] != models["q2"]["model_id"]:
        raise AssertionError("Q2 reconstructed model differs from freeze")
    if reconstruction["q3"]["final_model_id"] != models["q3"]["model_id"]:
        raise AssertionError("Q3 reconstructed model differs from freeze")
    if final_candidate["q3"]["full_data_configuration"]["candidate_id"] != models["q3"]["configuration_id"]:
        raise AssertionError("Q3 final configuration differs from freeze")
    manifest = {
        "status": "FROZEN", "stage": "S5", "created_at": now(),
        "selection_closed": True, "test_data_used_for_selection": False,
        "g4_review": verify_g4(),
        "source_commit": git("rev-parse", "HEAD"),
        "source_files": sources, "source_files_sha256": source_sha,
        "models": models,
        "model_ids_and_parameters_sha256": canonical_sha(models),
        "training_inputs": inputs, "training_inputs_sha256": inputs_sha,
        "feature_schemas": schema_records,
        "feature_schema_sha256": canonical_sha(schema_records),
        "q1_postprocess_version": "q1_clip_0_test_dur_v1",
        "q2_label_order": labels,
        "q2_label_order_sha256": canonical_sha(labels),
        "q3_postprocess_version": "q3_nonnegative_v1",
        "split_registry": {"path": relative(SPLITS), "sha256": sha256(SPLITS)},
        "configs": [
            {"path": relative(CONFIG), "sha256": sha256(CONFIG)},
            {"path": relative(S4_CONFIG), "sha256": sha256(S4_CONFIG)},
        ],
        "output_schema": {"path": relative(OUTPUT_SCHEMA), "sha256": sha256(OUTPUT_SCHEMA)},
        "output_schema_sha256": sha256(OUTPUT_SCHEMA),
        "official_test_inputs": official_identities(),
        "official_test_numeric_read_count_at_freeze": 0,
        "official_test_prediction_count_at_freeze": 0,
        "release_contract": {
            "phase": "S5_FINAL_INFERENCE", "exactly_once": True,
            "ledger_path": "projects/rehearsal_2024_B/results/raw/final/test_release_ledger.json",
            "release_directory": "projects/rehearsal_2024_B/results/raw/final/release",
            "feedback_targets": [],
            "post_release_feedback_forbidden": ["O2", "O3", "S4"],
        },
        "evidence_identity_boundary": {
            "Q3_NESTED_SELECTION_PIPELINE_PERFORMANCE": {
                "meaning": "outer OOF performance of the frozen nested unified selection pipeline",
                "selection_score": reconstruction["q3"]["candidates"]["Q3-M1-HGB-UNIFIED"]["point"]["selection_score"],
                "not_a_fixed_C3_score": True,
            },
            "Q3_FINAL_FULL_DATA_CONFIGURATION": {
                "meaning": "final deployment configuration selected from 45 primary inner records",
                "configuration_id": models["q3"]["configuration_id"],
                "inner_record_count": reconstruction["q3"]["selected_full_data_configuration"]["inner_record_count"],
                "not_an_outer_OOF_score": True,
            },
        },
        "prior_validation": {
            "g4_validated_artifact_manifest_sha256": raw_hashes["g4_validation_manifest_sha256"],
            "independent_selection_reconstruction_sha256": "FILLED_AFTER_WRITE",
        },
    }
    return manifest


def prepare_freeze() -> None:
    if git("status", "--short"):
        raise RuntimeError("pre-release freeze requires a clean Git worktree")
    g4 = verify_g4()
    raw_hashes = verified_raw_hashes()
    reconstruction = reconstruct_selection_and_promotion()
    VERIFIED.mkdir(parents=True, exist_ok=True)
    reconstruction_path = VERIFIED / "selection_reconstruction.json"
    dump(reconstruction_path, reconstruction)
    metrics = {
        "status": "VERIFIED", "verified_at": now(),
        "g4_review": g4,
        "claims": {
            "Q1_FINAL_MODEL": {"model_id": "Q1-B1", "postprocess": "q1_clip_0_test_dur_v1"},
            "Q2_FINAL_ROLLBACK": {
                "model_id": "Q2-B1A",
                "baseline_macro_f1_fixed_17": reconstruction["q2"]["baseline_point"]["macro_f1_fixed_17"],
                "weighted_gain": reconstruction["q2"]["candidates"]["Q2-M1W-HGB-WEIGHTED"]["macro_f1_absolute_gain"],
                "promotion_threshold": 0.02,
            },
            "Q3_NESTED_SELECTION_PIPELINE_PERFORMANCE": {
                "model_id": "Q3-M1-HGB-UNIFIED",
                "primary_selection_score": reconstruction["q3"]["candidates"]["Q3-M1-HGB-UNIFIED"]["point"]["selection_score"],
                "relative_gain_vs_Q3_B1": reconstruction["q3"]["candidates"]["Q3-M1-HGB-UNIFIED"]["relative_selection_score_gain"],
                "interpretation": "nested unified selection pipeline, not fixed residual-C3 alone",
            },
            "Q3_FINAL_FULL_DATA_CONFIGURATION": {
                "configuration_id": reconstruction["q3"]["selected_full_data_configuration"]["candidate_id"],
                "inner_record_count": reconstruction["q3"]["selected_full_data_configuration"]["inner_record_count"],
                "interpretation": "deployment configuration, not an outer OOF score",
            },
        },
    }
    dump(VERIFIED / "verified_metrics.json", metrics)
    for source, destination in CORE_COPIES.items():
        shutil.copy2(source, destination)
    manifest = build_freeze(reconstruction, raw_hashes)
    manifest["prior_validation"]["independent_selection_reconstruction_sha256"] = sha256(reconstruction_path)
    freeze_path = VERIFIED / "freeze_manifest.json"
    dump(freeze_path, manifest)
    freeze_hash = sha256(freeze_path)
    (VERIFIED / "freeze_manifest.sha256").write_text(
        f"{freeze_hash}  freeze_manifest.json\n", encoding="ascii"
    )
    artifact_records = []
    for path in sorted(VERIFIED.iterdir()):
        if path.is_file() and path.name not in {"artifact_manifest.json", "result_registry.md"}:
            artifact_records.append({
                "path": relative(path), "bytes": path.stat().st_size, "sha256": sha256(path)
            })
    dump(VERIFIED / "artifact_manifest.json", {
        "status": "PASS", "phase": "PRE_RELEASE_FREEZE", "created_at": now(),
        "official_test_numeric_read_count": 0,
        "artifacts": artifact_records,
    })
    print("status=PASS")
    print("phase=PRE_RELEASE_FREEZE")
    print(f"freeze_manifest_sha256={freeze_hash}")
    print("independent_selection_checks=6/6")
    print("official_test_numeric_read_count=0")


def exact_fields(row: dict[str, Any], fields: list[str]) -> bool:
    return list(row.keys()) == fields


def validate_release_rows(release_dir: Path, schema: dict[str, Any]) -> dict[str, Any]:
    outputs = {}
    for name, contract in schema["artifacts"].items():
        path = release_dir / name
        rows = read_jsonl(path)
        fields = list(contract["fields"])
        checks = {
            "row_count": len(rows) == int(contract["row_count"]),
            "field_order": all(exact_fields(row, fields) for row in rows),
            "row_order": [int(row["row_order"]) for row in rows] == list(range(len(rows))),
        }
        if not all(checks.values()):
            raise AssertionError(f"release output schema mismatch: {name}: {checks}")
        outputs[name] = {"rows": rows, "checks": checks, "sha256": sha256(path)}
    q1 = outputs["q1_ap_predictions.jsonl"]["rows"]
    q2 = outputs["q2_ap_predictions.jsonl"]["rows"]
    q3 = outputs["q3_ap_predictions.jsonl"]["rows"]
    systems = outputs["q3_system_predictions.jsonl"]["rows"]
    checks = {
        "q1_unique_keys": len({row["row_key"] for row in q1}) == 185,
        "q1_finite_and_bounded": all(
            math.isfinite(float(row["seq_time_raw"]))
            and 0 <= float(row["seq_time_bounded"]) <= float(row["test_dur"])
            for row in q1
        ),
        "q2_unique_keys": len({row["row_key"] for row in q2}) == 151,
        "q2_labels_fixed": all(row["predicted_joint_label"] in LABELS for row in q2),
        "q2_probability_order": all(row["probability_label_order"] == LABELS for row in q2),
        "q2_probability_closure": all(
            len(row["probability_fixed_17"]) == 17
            and all(math.isfinite(float(value)) and float(value) >= 0 for value in row["probability_fixed_17"])
            and close(math.fsum(float(value) for value in row["probability_fixed_17"]), 1.0, 1e-10)
            for row in q2
        ),
        "q3_unique_keys": len({row["row_key"] for row in q3}) == 185,
        "q3_finite_nonnegative": all(
            math.isfinite(float(row["throughput_raw"]))
            and math.isfinite(float(row["throughput_bounded"]))
            and float(row["throughput_bounded"]) >= 0
            for row in q3
        ),
        "q3_system_count": len(systems) == 75,
    }
    by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in q3:
        by_group[f"{row['source_file']}::{int(row['test_id'])}"].append(row)
    for row in systems:
        components = by_group[row["group_id"]]
        predicted = math.fsum(float(item["throughput_bounded"]) for item in components)
        if not close(predicted, float(row["system_throughput_bounded"]), 1e-9):
            checks["q3_system_sum_equality"] = False
            break
    else:
        checks["q3_system_sum_equality"] = len(by_group) == 75
    if not all(checks.values()):
        raise AssertionError(f"final release row checks failed: {checks}")
    return {
        "status": "PASS", "checks": checks,
        "artifacts": {
            name: {"sha256": value["sha256"], "row_count": len(value["rows"]), "checks": value["checks"]}
            for name, value in outputs.items()
        },
    }


def finalize_release() -> None:
    freeze_path = VERIFIED / "freeze_manifest.json"
    sidecar = (VERIFIED / "freeze_manifest.sha256").read_text(encoding="ascii").split()[0]
    if sha256(freeze_path) != sidecar:
        raise AssertionError("freeze manifest sidecar mismatch")
    freeze = load(freeze_path)
    for item in freeze["source_files"]:
        if sha256(REPO / item["path"]) != item["sha256"]:
            raise AssertionError(f"frozen source drift: {item['path']}")
    ledger = load(RAW_FINAL / "test_release_ledger.json")
    successes = [attempt for attempt in ledger["attempts"] if attempt["status"] == "SUCCEEDED"]
    if len(successes) != 1 or ledger["successful_release_count"] != 1:
        raise AssertionError("exactly-once ledger does not contain one success")
    success = successes[0]
    release_dir = REPO / success["release_directory"]
    manifest_path = release_dir / "release_manifest.json"
    if sha256(manifest_path) != success["release_manifest_sha256"]:
        raise AssertionError("release manifest hash differs from ledger")
    release_manifest = load(manifest_path)
    if release_manifest["freeze_manifest_sha256"] != sidecar:
        raise AssertionError("release used a different freeze manifest")
    for item in release_manifest["artifacts"]:
        path = REPO / item["path"]
        if sha256(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
            raise AssertionError(f"released artifact drift: {item['path']}")
    row_checks = validate_release_rows(release_dir, load(OUTPUT_SCHEMA))
    copied = []
    for name in load(OUTPUT_SCHEMA)["artifacts"]:
        source = release_dir / name
        destination = VERIFIED / f"official_{name}"
        shutil.copy2(source, destination)
        copied.append({"path": relative(destination), "sha256": sha256(destination)})
    validation = {
        "status": "PASS", "phase": "POST_RELEASE_FINALIZATION",
        "validated_at": now(), "freeze_manifest_sha256": sidecar,
        "ledger_sha256": sha256(RAW_FINAL / "test_release_ledger.json"),
        "release_manifest_sha256": sha256(manifest_path),
        "successful_release_count": 1,
        "official_test_numeric_read_count": release_manifest["official_test_numeric_read_count"],
        "official_test_prediction_artifact_count": 4,
        "row_checks": row_checks, "verified_copies": copied,
        "test_predictions_used_for_model_feedback": False,
    }
    dump(VERIFIED / "final_release_verification.json", validation)
    artifact_records = []
    for path in sorted(VERIFIED.iterdir()):
        if path.is_file() and path.name not in {"artifact_manifest.json", "result_registry.md"}:
            artifact_records.append({
                "path": relative(path), "bytes": path.stat().st_size, "sha256": sha256(path)
            })
    dump(VERIFIED / "artifact_manifest.json", {
        "status": "PASS", "phase": "POST_RELEASE_FINALIZATION", "created_at": now(),
        "successful_release_count": 1, "artifacts": artifact_records,
    })
    print("status=PASS")
    print("phase=POST_RELEASE_FINALIZATION")
    print("successful_release_count=1")
    print("final_output_checks=13/13")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("prepare-freeze", "finalize-release"))
    args = parser.parse_args()
    if args.phase == "prepare-freeze":
        prepare_freeze()
    else:
        finalize_release()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
