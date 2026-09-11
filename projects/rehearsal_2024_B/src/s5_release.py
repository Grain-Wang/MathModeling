"""Governed exactly-once S5 fit, official-test inference, and export.

The disk-backed guard runs before every numerical CSV parser.  A successful
release cannot be repeated; failed attempts are recorded separately and may be
retried only when no conflicting release directory exists.
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
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
SRC = PROJECT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contract_guard import ContractBoundaryError, validate_phase_input_manifest
from s1_data_audit import DATA, EXPECTED, strict_identity_audit, training_frames
from s2_contract_validation import group_id, label_of
from s3_features import build_feature_frame
from s3_io import RunState
from s3_lineage import aligned_probabilities, make_pipeline, phy_rate, q1_pipeline, q2_pipeline
from s4_selection import Q1_COLUMN, _augment_q3, _hgb_regressor

CONFIG = PROJECT / "configs" / "s2_experiment_plan.json"
S4_CONFIG = PROJECT / "configs" / "s4_candidate_plan.json"
OUTPUT_SCHEMA = PROJECT / "configs" / "s5_output_schema.json"
FREEZE = PROJECT / "results" / "verified" / "freeze_manifest.json"
FREEZE_SIDECAR = PROJECT / "results" / "verified" / "freeze_manifest.sha256"
BASE_SCHEMA = PROJECT / "results" / "raw" / "baseline" / "feature_schema.json"
Q1_OOF = PROJECT / "results" / "raw" / "baseline" / "q1_oof_predictions.jsonl.gz"
FINAL_ROOT = PROJECT / "results" / "raw" / "final"
LEDGER = FINAL_ROOT / "test_release_ledger.json"
RELEASE_DIRECTORY = FINAL_ROOT / "release"


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


def dump_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def verified_freeze(requested_hash: str) -> tuple[dict[str, Any], str]:
    if not FREEZE.is_file() or not FREEZE_SIDECAR.is_file():
        raise ContractBoundaryError("freeze manifest or sidecar is missing")
    sidecar = FREEZE_SIDECAR.read_text(encoding="ascii").split()[0].upper()
    actual = sha256(FREEZE)
    if actual != sidecar or requested_hash.upper() != actual:
        raise ContractBoundaryError("freeze manifest hash mismatch")
    freeze = load(FREEZE)
    if freeze.get("status") != "FROZEN" or freeze.get("selection_closed") is not True:
        raise ContractBoundaryError("freeze manifest is not closed")
    for item in freeze["source_files"]:
        path = REPO / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise ContractBoundaryError(f"frozen source drift: {item['path']}")
    review = REPO / freeze["g4_review"]["path"]
    text = review.read_text(encoding="utf-8")
    if sha256(review) != freeze["g4_review"]["sha256"]:
        raise ContractBoundaryError("G4 review hash mismatch")
    if "Verdict: **PASS**" not in text or "S4 -> S5 = AUTHORIZED" not in text:
        raise ContractBoundaryError("G4 review does not authorize S5")
    return freeze, actual


def ledger_state() -> tuple[dict[str, Any], int, int]:
    if not LEDGER.exists():
        return {
            "schema_version": "s5_exactly_once_ledger_v1",
            "exactly_once": True,
            "successful_release_count": 0,
            "attempts": [],
        }, 0, 0
    try:
        ledger = load(LEDGER)
    except (OSError, json.JSONDecodeError) as error:
        raise ContractBoundaryError("release ledger is unreadable") from error
    attempts = list(ledger.get("attempts", []))
    successes = sum(item.get("status") == "SUCCEEDED" for item in attempts)
    running = sum(item.get("status") == "RUNNING" for item in attempts)
    if successes != int(ledger.get("successful_release_count", -1)):
        raise ContractBoundaryError("release ledger success count is inconsistent")
    return ledger, successes, running


def release_guard() -> tuple[dict[str, Any], dict[str, Any], str, dict[str, Any]]:
    config = load(CONFIG)
    requested_hash = FREEZE_SIDECAR.read_text(encoding="ascii").split()[0] if FREEZE_SIDECAR.exists() else ""
    freeze, freeze_hash = verified_freeze(requested_hash)
    ledger, successes, running = ledger_state()
    if successes:
        raise ContractBoundaryError("a successful official-test release already exists")
    if running:
        raise ContractBoundaryError("an unresolved RUNNING release attempt requires manual audit")
    if RELEASE_DIRECTORY.exists():
        raise ContractBoundaryError("final release directory already exists")
    policy = config["test_release_contract"]
    names = list(policy["official_test_denylist"])
    frozen = {item["name"]: item for item in freeze["official_test_inputs"]}
    if set(frozen) != set(names):
        raise ContractBoundaryError("freeze official-test identity set is incomplete")
    for name in names:
        path = DATA / name
        item = frozen[name]
        if (
            not path.is_file()
            or path.stat().st_size != int(item["bytes"])
            or sha256(path) != item["sha256"]
        ):
            raise ContractBoundaryError(f"official test byte identity mismatch: {name}")
    request = {
        "phase": "S5_FINAL_INFERENCE",
        "input_kind": "official_test_csv",
        "input_files": [str(DATA / name) for name in names],
        "gate_state": "G4_PASS",
        "prior_release_count": successes,
        "freeze_manifest_sha256": freeze_hash,
        "freeze_manifest": freeze,
        "feedback_targets": [],
    }
    contract_result = validate_phase_input_manifest(request, config)
    guard = {
        **contract_result,
        "release_state_source": "disk_ledger_and_artifact_state",
        "freeze_manifest_sha256": freeze_hash,
        "prior_attempt_count": len(ledger["attempts"]),
        "prior_failed_attempt_count": sum(item.get("status") == "FAILED" for item in ledger["attempts"]),
        "derived_prior_successful_release_count": successes,
        "output_conflict_count": 0,
        "official_test_numeric_read_count_at_guard_return": 0,
    }
    return freeze, ledger, freeze_hash, guard


def update_attempt(ledger: dict[str, Any], release_id: str, **values: Any) -> None:
    matches = [item for item in ledger["attempts"] if item["release_id"] == release_id]
    if len(matches) != 1:
        raise RuntimeError("release attempt identity is not unique")
    matches[0].update(values)
    ledger["successful_release_count"] = sum(
        item.get("status") == "SUCCEEDED" for item in ledger["attempts"]
    )
    dump(LEDGER, ledger)


def read_training(paths: list[Path], state: RunState) -> pd.DataFrame:
    frames = {}
    for path in paths:
        frames[path.name] = pd.read_csv(path, low_memory=False)
        state.csv_numeric_read_count += 1
    _, eligible = training_frames(frames)
    eligible = eligible.reset_index(drop=True)
    audit = strict_identity_audit(eligible, "S5 eligible training")
    if not audit["strict_pass"] or len(eligible) != 1250 or group_id(eligible).nunique() != 482:
        raise AssertionError("S5 training population identity mismatch")
    return eligible


def read_official(paths: list[Path], state: RunState) -> dict[str, pd.DataFrame]:
    frames = {}
    for path in paths:
        frame = pd.read_csv(path, low_memory=False)
        state.csv_numeric_read_count += 1
        state.official_numeric_read_count += 1  # type: ignore[attr-defined]
        spec = EXPECTED[path.name]
        if frame.shape != (spec["rows"], spec["cols"]):
            raise AssertionError(f"official test shape mismatch: {path.name}")
        frames[path.name] = frame.assign(
            source_file=path.name, source_row_index=np.arange(len(frame))
        )
    return frames


def concat_role(frames: dict[str, pd.DataFrame], role: str) -> pd.DataFrame:
    parts = [frame for name, frame in frames.items() if EXPECTED[name]["role"] == role]
    output = pd.concat(parts, ignore_index=True, sort=False)
    audit = strict_identity_audit(output, f"S5 {role}")
    if not audit["strict_pass"]:
        raise AssertionError(f"official test identity mismatch: {role}")
    return output


def oof_q1_training_feature(train: pd.DataFrame) -> np.ndarray:
    values: dict[str, list[float]] = defaultdict(list)
    with gzip.open(Q1_OOF, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row["scope"] == "PRIMARY" and row["model_id"] == "Q1-B1":
                values[str(row["row_key"])].append(float(row["seq_time_bounded"]))
    keys = (
        train["source_file"].astype(str) + "::"
        + train["test_id"].map(lambda value: str(int(value))) + "::"
        + train["ap_id"].astype(str)
    ).tolist()
    if set(keys) != set(values) or any(len(values[key]) != 3 for key in keys):
        raise AssertionError("registered Q1 OOF feature coverage mismatch")
    return np.asarray([float(np.mean(values[key])) for key in keys], dtype=float)


def row_key(frame: pd.DataFrame, index: int) -> str:
    return f"{frame.at[index, 'source_file']}::{int(frame.at[index, 'test_id'])}::{frame.at[index, 'ap_id']}"


def common_row(frame: pd.DataFrame, index: int, release_id: str, order: int) -> dict[str, Any]:
    source = str(frame.at[index, "source_file"])
    return {
        "release_id": release_id,
        "scope": "OFFICIAL_TEST_UNLABELED",
        "row_order": order,
        "row_key": row_key(frame, index),
        "source_file": source,
        "source_row_index": int(frame.at[index, "source_row_index"]),
        "test_id": int(frame.at[index, "test_id"]),
        "ap_id": str(frame.at[index, "ap_id"]),
        "ap_count": int(EXPECTED[source]["ap_count"]),
    }


def schema_columns(features: pd.DataFrame) -> None:
    expected = [item["name"] for item in load(BASE_SCHEMA)["features"]]
    if list(features.columns) != expected:
        raise AssertionError("feature columns differ from frozen S3 schema")


def fit_and_predict(
    freeze: dict[str, Any], release_id: str, staging: Path, state: RunState
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    config = load(CONFIG)
    s4_config = load(S4_CONFIG)
    training_paths = [DATA / name for name in config["test_release_contract"]["training_file_allowlist"]]
    official_paths = [DATA / name for name in config["test_release_contract"]["official_test_denylist"]]
    train = read_training(training_paths, state)
    official = read_official(official_paths, state)
    test1 = concat_role(official, "test_q1_q3").reset_index(drop=True)
    test2 = concat_role(official, "test_q2").reset_index(drop=True)
    if len(test1) != 185 or len(test2) != 151:
        raise AssertionError("official question row count mismatch")
    train_features = build_feature_frame(train)
    test1_features = build_feature_frame(test1)
    test2_features = build_feature_frame(test2)
    schema_columns(train_features)
    schema_columns(test1_features)
    schema_columns(test2_features)
    feature_hash = freeze["feature_schema_sha256"]

    q1 = q1_pipeline(list(train_features.columns))
    state.fit(q1, train_features, train["seq_time"].to_numpy(float), "S5:Q1-B1:full")
    q1_raw = np.asarray(q1.predict(test1_features), dtype=float)
    q1_bounded = np.clip(q1_raw, 0.0, test1["test_dur"].to_numpy(float))
    q1_rows = []
    for index in range(len(test1)):
        q1_rows.append({
            **common_row(test1, index, release_id, index),
            "model_id": "Q1-B1", "feature_schema_sha256": feature_hash,
            "test_dur": float(test1.at[index, "test_dur"]),
            "seq_time_raw": float(q1_raw[index]),
            "seq_time_bounded": float(q1_bounded[index]),
            "clipped": bool(abs(q1_raw[index] - q1_bounded[index]) > 1e-12),
        })

    labels = list(config["q2"]["global_joint_labels"])
    q2 = q2_pipeline(list(train_features.columns))
    q2_y = np.asarray([
        label_of(nss, mcs) for nss, mcs in zip(train["nss"], train["mcs"], strict=True)
    ])
    state.fit(q2, train_features, q2_y, "S5:Q2-B1A:full")
    q2_prediction, q2_probability, missing = aligned_probabilities(q2, test2_features, labels)
    q2_rows = []
    for index in range(len(test2)):
        predicted = str(q2_prediction[index])
        q2_rows.append({
            **common_row(test2, index, release_id, index),
            "model_id": "Q2-B1A", "feature_schema_sha256": feature_hash,
            "predicted_joint_label": predicted,
            "predict_nss": int(predicted.split("|")[0]),
            "predict_mcs": int(predicted.split("|")[1]),
            "probability_label_order": labels,
            "probability_fixed_17": [float(value) for value in q2_probability[index]],
            "missing_train_labels": missing,
        })

    q1_train = oof_q1_training_feature(train)
    train_q3 = _augment_q3(train_features, train, q1_train)
    test_q3 = _augment_q3(test1_features, test1, q1_bounded)
    fallback_train = train_features.copy()
    fallback_test = test1_features.copy()
    fallback_train[Q1_COLUMN] = q1_train
    fallback_test[Q1_COLUMN] = q1_bounded
    fallback = make_pipeline(
        list(fallback_train.columns),
        Ridge(alpha=1.0, solver="lsqr", tol=1e-8, max_iter=10000),
    )
    throughput = train["throughput"].to_numpy(float)
    state.fit(fallback, fallback_train, throughput, "S5:Q3:physical-fallback")
    fallback_train_prediction = np.asarray(fallback.predict(fallback_train), dtype=float)
    fallback_test_prediction = np.asarray(fallback.predict(fallback_test), dtype=float)
    train_rate = phy_rate(train)
    test_rate = phy_rate(test1)
    train_proxy = q1_train / train["test_dur"].to_numpy(float) * train_rate
    test_proxy = q1_bounded / test1["test_dur"].to_numpy(float) * test_rate
    usable = np.isfinite(train_proxy)
    denominator = float(np.sum(np.square(train_proxy[usable])))
    if denominator <= 0 or not math.isfinite(denominator):
        raise AssertionError("Q3 physical eta denominator is invalid")
    eta = float(np.clip(np.sum(train_proxy[usable] * throughput[usable]) / denominator, 0.0, 1.0))
    train_base = eta * train_proxy
    test_base = eta * test_proxy
    train_missing = ~np.isfinite(train_base)
    test_missing = ~np.isfinite(test_base)
    train_base[train_missing] = fallback_train_prediction[train_missing]
    test_base[test_missing] = fallback_test_prediction[test_missing]
    candidate = {
        "candidate_id": "Q3-physics_residual-C3", "architecture": "physics_residual",
        "config_id": "Q3-C3", "config_index": 3, "learning_rate": 0.05,
        "max_leaf_nodes": 15, "l2_regularization": 1.0,
    }
    q3 = _hgb_regressor(list(train_q3.columns), candidate, dict(s4_config["hgb_common"]))
    state.fit(q3, train_q3, throughput - train_base, "S5:Q3:physics-residual-C3:full")
    q3_raw = test_base + np.asarray(q3.predict(test_q3), dtype=float)
    q3_bounded = np.maximum(0.0, q3_raw)
    q3_rows = []
    for index in range(len(test1)):
        q3_rows.append({
            **common_row(test1, index, release_id, index),
            "model_id": "Q3-M1-HGB-UNIFIED",
            "configuration_id": "Q3-physics_residual-C3",
            "feature_schema_sha256": feature_hash, "q1_model_id": "Q1-B1",
            "q1_seq_time_bounded": float(q1_bounded[index]),
            "throughput_raw": float(q3_raw[index]),
            "throughput_bounded": float(q3_bounded[index]),
            "negative_clipped": bool(q3_raw[index] < 0),
            "phy_rate_mbps": None if not np.isfinite(test_rate[index]) else float(test_rate[index]),
            "physical_proxy_mbps": None if not np.isfinite(test_proxy[index]) else float(test_proxy[index]),
            "eta": eta, "rate_missing": bool(not np.isfinite(test_rate[index])),
        })
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in q3_rows:
        grouped[f"{row['source_file']}::{row['test_id']}"] .append(row)
    system_rows = []
    for order, (key, rows) in enumerate(grouped.items()):
        if len(rows) != int(rows[0]["ap_count"]):
            raise AssertionError(f"incomplete official Q3 system group: {key}")
        total = math.fsum(float(row["throughput_bounded"]) for row in rows)
        system_rows.append({
            "release_id": release_id, "scope": "OFFICIAL_TEST_UNLABELED",
            "row_order": order, "group_id": key,
            "source_file": rows[0]["source_file"], "test_id": rows[0]["test_id"],
            "ap_count": rows[0]["ap_count"], "model_id": "Q3-M1-HGB-UNIFIED",
            "system_throughput_bounded": total,
            "component_row_keys": sorted(row["row_key"] for row in rows),
            "bounded_sum_equality_absolute_error": 0.0,
        })
    outputs = {
        "q1_ap_predictions.jsonl": q1_rows,
        "q2_ap_predictions.jsonl": q2_rows,
        "q3_ap_predictions.jsonl": q3_rows,
        "q3_system_predictions.jsonl": system_rows,
    }
    for name, rows in outputs.items():
        dump_jsonl(staging / name, rows)
    models = staging / "models"
    models.mkdir()
    joblib.dump({"release_id": release_id, "model_id": "Q1-B1", "pipeline": q1}, models / "q1_model.joblib")
    joblib.dump({"release_id": release_id, "model_id": "Q2-B1A", "label_order": labels, "pipeline": q2}, models / "q2_model.joblib")
    joblib.dump({
        "release_id": release_id, "model_id": "Q3-M1-HGB-UNIFIED",
        "configuration_id": "Q3-physics_residual-C3", "residual_pipeline": q3,
        "physical_fallback_pipeline": fallback, "eta": eta,
        "q1_training_feature": "three-repeat registered Q1-B1 outer-OOF mean",
    }, models / "q3_model_bundle.joblib")
    audits = {
        "training_rows": len(train), "test_q1_q3_rows": len(test1),
        "test_q2_rows": len(test2), "test_q3_system_rows": len(system_rows),
        "q1_training_oof_feature_count": len(q1_train),
        "q2_missing_training_labels": missing, "q3_eta": eta,
        "q3_training_rate_missing_count": int(train_missing.sum()),
        "q3_test_rate_missing_count": int(test_missing.sum()),
    }
    return [row for rows in outputs.values() for row in rows], audits


def validate_staging(staging: Path) -> dict[str, Any]:
    schema = load(OUTPUT_SCHEMA)
    records = {}
    for name, contract in schema["artifacts"].items():
        rows = []
        with (staging / name).open("r", encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle if line.strip()]
        if len(rows) != contract["row_count"]:
            raise AssertionError(f"release row count mismatch: {name}")
        if any(list(row) != contract["fields"] for row in rows):
            raise AssertionError(f"release field order mismatch: {name}")
        if [row["row_order"] for row in rows] != list(range(len(rows))):
            raise AssertionError(f"release row order mismatch: {name}")
        records[name] = rows
    q1 = records["q1_ap_predictions.jsonl"]
    q2 = records["q2_ap_predictions.jsonl"]
    q3 = records["q3_ap_predictions.jsonl"]
    systems = records["q3_system_predictions.jsonl"]
    checks = {
        "q1_unique_keys": len({row["row_key"] for row in q1}) == 185,
        "q1_finite_bounded": all(
            math.isfinite(row["seq_time_raw"]) and 0 <= row["seq_time_bounded"] <= row["test_dur"]
            for row in q1
        ),
        "q2_unique_keys": len({row["row_key"] for row in q2}) == 151,
        "q2_probability_closure": all(
            len(row["probability_fixed_17"]) == 17
            and math.isclose(math.fsum(row["probability_fixed_17"]), 1.0, abs_tol=1e-10, rel_tol=0)
            for row in q2
        ),
        "q3_unique_keys": len({row["row_key"] for row in q3}) == 185,
        "q3_nonnegative": all(math.isfinite(row["throughput_raw"]) and row["throughput_bounded"] >= 0 for row in q3),
        "q3_system_count": len(systems) == 75,
    }
    ap_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in q3:
        ap_groups[f"{row['source_file']}::{row['test_id']}"] .append(row)
    checks["q3_system_sum_equality"] = all(
        math.isclose(
            math.fsum(item["throughput_bounded"] for item in ap_groups[row["group_id"]]),
            row["system_throughput_bounded"], abs_tol=1e-9, rel_tol=0,
        ) for row in systems
    )
    if not all(checks.values()):
        raise AssertionError(f"release staging validation failed: {checks}")
    return {"status": "PASS", "checks": checks}


def execute_release(freeze: dict[str, Any], ledger: dict[str, Any], freeze_hash: str, guard: dict[str, Any]) -> None:
    FINAL_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%dT%H%M%S%z")
    release_id = f"S5-{freeze_hash[:12]}-{stamp}"
    if any(item.get("release_id") == release_id for item in ledger["attempts"]):
        raise RuntimeError("generated release ID already exists in ledger")
    staging = FINAL_ROOT / f".staging_{release_id}"
    if staging.exists():
        raise RuntimeError("release staging directory already exists")
    attempt = {
        "release_id": release_id, "status": "RUNNING", "started_at": now(),
        "freeze_manifest_sha256": freeze_hash,
        "derived_prior_successful_release_count": guard["derived_prior_successful_release_count"],
        "official_test_input_sha256": {
            item["name"]: item["sha256"]
            for item in freeze["official_test_inputs"]
        },
        "official_test_numeric_read_count_at_guard_return": 0,
    }
    ledger["attempts"].append(attempt)
    dump(LEDGER, ledger)
    state = RunState()
    state.official_numeric_read_count = 0  # type: ignore[attr-defined]
    started = time.perf_counter()
    try:
        staging.mkdir()
        _, audit = fit_and_predict(freeze, release_id, staging, state)
        validation = validate_staging(staging)
        if state.warnings:
            raise RuntimeError(f"final model fit emitted warnings: {state.warnings[:3]}")
        artifacts = []
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                artifacts.append({
                    "path": relative(RELEASE_DIRECTORY / path.relative_to(staging)),
                    "bytes": path.stat().st_size, "sha256": sha256(path),
                })
        release_manifest = {
            "status": "PASS", "release_id": release_id,
            "created_at": now(), "source_commit": freeze["source_commit"],
            "execution_head": git("rev-parse", "HEAD"),
            "freeze_manifest_sha256": freeze_hash,
            "output_schema_sha256": freeze["output_schema_sha256"],
            "model_fit_count": state.model_fit_count,
            "training_csv_numeric_read_count": state.csv_numeric_read_count - state.official_numeric_read_count,
            "official_test_numeric_read_count": state.official_numeric_read_count,
            "official_test_prediction_artifact_count": 4,
            "warnings": state.warnings, "runtime_seconds": time.perf_counter() - started,
            "guard": guard, "audit": audit, "validation": validation,
            "artifacts": artifacts,
            "feedback_targets": [], "test_predictions_used_for_model_feedback": False,
        }
        dump(staging / "release_manifest.json", release_manifest)
        staging.replace(RELEASE_DIRECTORY)
        release_manifest_hash = sha256(RELEASE_DIRECTORY / "release_manifest.json")
        update_attempt(
            ledger, release_id, status="SUCCEEDED", finished_at=now(),
            release_directory=relative(RELEASE_DIRECTORY),
            release_manifest_sha256=release_manifest_hash,
            official_test_numeric_read_count=state.official_numeric_read_count,
            model_and_output_artifacts=release_manifest["artifacts"],
            official_test_prediction_artifact_count=4,
        )
    except Exception as error:
        if staging.exists():
            shutil.rmtree(staging)
        update_attempt(
            ledger, release_id, status="FAILED", finished_at=now(),
            error_type=type(error).__name__, error_message=str(error),
            official_test_numeric_read_count=state.official_numeric_read_count,
        )
        raise
    print("status=PASS")
    print(f"release_id={release_id}")
    print("successful_release_count=1")
    print(f"model_fit_count={state.model_fit_count}")
    print(f"official_test_numeric_read_count={state.official_numeric_read_count}")
    print("official_test_prediction_artifact_count=4")
    print("test_predictions_used_for_model_feedback=false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    freeze, ledger, freeze_hash, guard = release_guard()
    if args.preflight_only:
        print("status=PASS")
        print("mode=PRE_RELEASE_GUARD_ONLY")
        print(f"freeze_manifest_sha256={freeze_hash}")
        print("derived_prior_successful_release_count=0")
        print("official_test_numeric_read_count=0")
        return 0
    execute_release(freeze, ledger, freeze_hash, guard)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
