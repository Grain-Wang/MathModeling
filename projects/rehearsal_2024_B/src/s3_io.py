"""S3 guarded I/O and reproducibility helpers."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import platform
import subprocess
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import sklearn

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
SRC = PROJECT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contract_guard import ContractBoundaryError, validate_phase_input_manifest
from s1_data_audit import DATA, EXPECTED, native as s1_native
from s1_data_audit import strict_identity_audit, training_frames
from s2_contract_validation import contract_artifact_verification, group_id

CONFIG_PATH = PROJECT / "configs" / "s2_experiment_plan.json"
REGISTRY_PATH = PROJECT / "results" / "raw" / "s2" / "split_registry.json"
REVIEW_PATH = PROJECT / "reviews" / "gate_2_review_r2.md"
OUTPUT = PROJECT / "results" / "raw" / "baseline"
EXPERIMENTS = PROJECT / "experiments" / "baseline"
EXPECTED_CORE_SHA = "88B108D181C2EA3A723303DED3D0E64BACEF7FA482F8322712ED97ED020A6C2D"
LABELS_EXPECTED = [
    "0|0", "1|0", "1|4", "1|5", "1|6", "1|7", "1|9",
    "2|2", "2|3", "2|4", "2|5", "2|6", "2|7", "2|8",
    "2|9", "2|10", "2|11",
]
PHY_RATE = {
    (1, 0): 8.6, (1, 1): 17.2, (1, 2): 25.8, (1, 3): 34.4,
    (1, 4): 51.6, (1, 5): 68.8, (1, 6): 77.4, (1, 7): 86.0,
    (1, 8): 103.2, (1, 9): 114.7, (1, 10): 129.0, (1, 11): 143.4,
    (2, 0): 17.2, (2, 1): 34.4, (2, 2): 51.6, (2, 3): 68.8,
    (2, 4): 103.2, (2, 5): 137.6, (2, 6): 154.9, (2, 7): 172.1,
    (2, 8): 206.5, (2, 9): 229.4, (2, 10): 258.1, (2, 11): 286.8,
}


class RunState:
    def __init__(self) -> None:
        self.model_fit_count = 0
        self.csv_numeric_read_count = 0
        self.warnings: list[dict[str, Any]] = []

    def fit(self, estimator: Any, x: Any, y: Any, context: str) -> Any:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            estimator.fit(x, y)
        self.model_fit_count += 1
        self.warnings.extend(
            {
                "context": context,
                "category": item.category.__name__,
                "message": str(item.message),
            }
            for item in caught
        )
        return estimator


def now() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")


def git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def json_native(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_native(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_native(item) for item in value]
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return s1_native(value)
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(json_native(payload), ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def dump_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".gz":
        handle = gzip.open(path, "wt", encoding="utf-8", newline="\n")
    else:
        handle = path.open("w", encoding="utf-8", newline="\n")
    with handle:
        for row in rows:
            handle.write(
                json.dumps(
                    json_native(row), ensure_ascii=False, sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            )

def canonical_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def registry_core_sha(registry: dict[str, Any]) -> str:
    keys = [
        "outer_assignments", "inner_assignments", "outer_fold_statistics",
        "primary_upstream_lineage_batches", "leave_one_source_file_out",
        "loso_downstream_inner_batches", "loso_upstream_lineage_batches",
    ]
    core = {key: registry[key] for key in keys}
    return hashlib.sha256(
        json.dumps(
            core, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest().upper()


def verify_gate_review() -> dict[str, Any]:
    text = REVIEW_PATH.read_text(encoding="utf-8")
    checks = {
        "verdict_pass": "Verdict: **PASS**" in text,
        "transition_authorized": "S2 -> S3 = AUTHORIZED" in text,
        "reviewed_commit": "facedf109a9025cb241d9a93074b0467c93143cb" in text,
    }
    if not all(checks.values()):
        raise RuntimeError(f"G2/R2 authorization check failed: {checks}")
    return {
        "status": "PASS", "path": canonical_relative(REVIEW_PATH),
        "sha256": sha256(REVIEW_PATH), "checks": checks,
    }


def guarded_inputs(
    config: dict[str, Any], state: RunState,
    names_override: list[str] | None = None,
) -> tuple[list[Path], dict[str, Any]]:
    policy = config["test_release_contract"]
    names = list(names_override) if names_override is not None else list(
        policy["training_file_allowlist"]
    )
    paths = [DATA / name for name in names]
    manifest = {
        "phase": "S3", "input_kind": "training_csv",
        "input_files": [str(path) for path in paths],
        "config_sha256": sha256(CONFIG_PATH),
        "guard_sha256": sha256(SRC / "contract_guard.py"),
    }
    guard = validate_phase_input_manifest(manifest, config)
    if names_override is not None:
        return paths, {"manifest": manifest, "guard_result": guard}
    if {path.name for path in paths} != set(policy["training_file_allowlist"]):
        raise RuntimeError("training input list differs from frozen allowlist")
    records = []
    for path in paths:
        resolved = path.resolve()
        spec = EXPECTED[path.name]
        if resolved.parent != DATA.resolve() or spec["role"] != "train":
            raise RuntimeError(f"illegal S3 numeric input: {path}")
        if not path.is_file() or path.stat().st_size != spec["bytes"]:
            raise RuntimeError(f"training input missing/size mismatch: {path.name}")
        digest = sha256(path)
        if digest != spec["sha256"]:
            raise RuntimeError(f"training input hash mismatch: {path.name}")
        records.append({
            "name": path.name,
            "canonical_relative_path": canonical_relative(path),
            "bytes": path.stat().st_size, "sha256": digest, "role": "train",
        })
    return paths, {
        "manifest": manifest, "guard_result": guard,
        "canonical_input_records": records,
        "numeric_read_count_at_guard_return": state.csv_numeric_read_count,
    }


def real_entry_guard_tests(config: dict[str, Any]) -> dict[str, Any]:
    state = RunState()
    train = list(config["test_release_contract"]["training_file_allowlist"])
    official = list(config["test_release_contract"]["official_test_denylist"])
    legal = guarded_inputs(config, state, train)[1]["guard_result"]
    rejected = []
    for name in official:
        try:
            guarded_inputs(config, state, train + [name])
        except ContractBoundaryError as error:
            rejected.append({"file": name, "rejected": True, "message": str(error)})
        else:
            rejected.append({"file": name, "rejected": False})
    checks = {
        "legal_training_manifest_passes": legal["status"] == "PASS",
        "all_official_injections_rejected": all(x["rejected"] for x in rejected),
        "no_csv_numeric_parser_called": state.csv_numeric_read_count == 0,
    }
    if not all(checks.values()):
        raise AssertionError(f"real entry guard tests failed: {checks}")
    return {"status": "PASS", "checks": checks, "cases": rejected}


def verify_all_file_hashes() -> dict[str, Any]:
    records = []
    for name, spec in sorted(EXPECTED.items()):
        path = DATA / name
        exists = path.is_file()
        digest = sha256(path) if exists else None
        size = path.stat().st_size if exists else None
        ok = exists and digest == spec["sha256"] and size == spec["bytes"]
        records.append({
            "name": name, "role": spec["role"], "bytes": size,
            "sha256": digest, "pass": ok,
            "access": (
                "byte_hash_only_no_numeric_parse" if spec["role"] != "train"
                else "identity_check_before_guarded_numeric_parse"
            ),
        })
    if not all(item["pass"] for item in records):
        raise RuntimeError("17-file size/hash verification failed")
    return {
        "status": "PASS", "file_count": len(records),
        "training_file_count": sum(x["role"] == "train" for x in records),
        "official_test_hash_only_count": sum(x["role"] != "train" for x in records),
        "files": records,
    }


def load_guarded_training(paths: list[Path], state: RunState) -> pd.DataFrame:
    frames = {}
    for path in paths:
        frames[path.name] = pd.read_csv(path)
        state.csv_numeric_read_count += 1
    _, eligible = training_frames(frames)
    eligible = eligible.reset_index(drop=True)
    identity = strict_identity_audit(eligible, "S3 eligible training")
    if not identity["strict_pass"]:
        raise AssertionError("eligible S3 training identity failed")
    if len(eligible) != 1250 or group_id(eligible).nunique() != 482:
        raise AssertionError("eligible S3 population differs from contract")
    return eligible


def row_keys(frame: pd.DataFrame) -> pd.Series:
    return (
        frame["source_file"].astype(str) + "::"
        + frame["test_id"].map(lambda value: str(int(value))) + "::"
        + frame["ap_id"].astype(str)
    )


def preflight(
    config: dict[str, Any], registry: dict[str, Any], state: RunState,
) -> tuple[list[Path], dict[str, Any], str]:
    gate = verify_gate_review()
    guard_tests = real_entry_guard_tests(config)
    paths, entry = guarded_inputs(config, state)
    identities = verify_all_file_hashes()
    contracts = contract_artifact_verification(config)
    core = registry_core_sha(registry)
    if contracts["status"] != "PASS":
        raise RuntimeError("approved contract artifact hashes no longer match")
    if core != registry["registry_core_sha256"] or core != EXPECTED_CORE_SHA:
        raise RuntimeError("frozen split registry core hash mismatch")
    labels = list(config["q2"]["global_joint_labels"])
    if labels != LABELS_EXPECTED:
        raise RuntimeError("fixed Q2 label order mismatch")
    evidence = {
        "status": "PASS", "gate_review": gate,
        "real_entry_guard_tests": guard_tests, "entry": entry,
        "file_identity": identities, "contract_artifacts": contracts,
        "split_registry": {
            "path": canonical_relative(REGISTRY_PATH),
            "file_sha256": sha256(REGISTRY_PATH),
            "recorded_core_sha256": registry["registry_core_sha256"],
            "recomputed_core_sha256": core,
            "outer_fold_count": registry["outer_fold_count"],
            "loso_split_count": registry["loso_split_count"],
        },
        "model_fit_count": 0, "csv_numeric_read_count": 0,
        "official_test_numeric_read_count": 0,
        "official_test_prediction_count": 0,
    }
    return paths, evidence, core


def environment_metadata() -> dict[str, Any]:
    return {
        "python": sys.version, "platform": platform.platform(),
        "numpy": np.__version__, "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__, "threads": 1,
    }
