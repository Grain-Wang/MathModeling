"""Shared, deterministic utilities for the approved S3 baseline pipeline."""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import shlex
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "experiments" / "s2_frozen_config.json"
BASELINE_CONFIG_DIR = PROJECT_ROOT / "experiments" / "baseline"
BASELINE_EVIDENCE_ROOT = PROJECT_ROOT / "results" / "raw" / "baseline"
S3_RESULTS_ROOT = PROJECT_ROOT / "results" / "raw" / "s3"
TZ = ZoneInfo("Asia/Shanghai")

SHAPE_FEATURES = [
    "shape_std",
    "shape_q05",
    "shape_q25",
    "shape_median",
    "shape_q75",
    "shape_q95",
    "shape_skew",
    "shape_kurtosis_excess",
    "shape_crest_factor",
    "shape_diff_max_abs",
    "shape_diff_mean_abs",
    "shape_diff_q50_abs",
    "shape_diff_q90_abs",
    "shape_diff_q95_abs",
    "shape_total_variation",
    "shape_positive_slope_ratio",
    "shape_negative_slope_ratio",
    "shape_plateau_ratio",
    "shape_slope_sign_changes",
    *[f"shape_fft_h{index}_energy_ratio" for index in range(1, 11)],
    "shape_fft_harmonic_to_fundamental",
]

Q4_NUMERIC_FEATURES = [
    "log_frequency_Hz",
    "log_b_m_T",
    "log_b_pp_T",
    "b_rms_T",
    "b_crest_factor",
    "b_mean_T",
    "b_std_T",
    "b_q05_T",
    "b_q25_T",
    "b_median_T",
    "b_q75_T",
    "b_q95_T",
    "diff_max_abs_T",
    "diff_mean_abs_T",
    "diff_q50_abs_T",
    "diff_q90_abs_T",
    "diff_q95_abs_T",
    "total_variation_T",
    *SHAPE_FEATURES,
]

Q4_CATEGORICAL_FEATURES = ["material", "waveform", "temperature_label"]
WAVEFORM_LABELS = ["正弦波", "三角波", "梯形波"]
MATERIAL_LABELS = ["材料1", "材料2", "材料3", "材料4"]
TEMPERATURES = [25, 50, 70, 90]
CLASS_ENCODING = {"正弦波": 1, "三角波": 2, "梯形波": 3}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_utf8_lf(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8", lineterminator="\n", float_format="%.12g")


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def load_frozen_config(path: Path | str) -> dict[str, Any]:
    config_path = Path(path).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("plan_version") != "s2-r2-v1":
        raise ValueError(f"Expected plan_version=s2-r2-v1, got {config.get('plan_version')!r}")
    return config


def verify_contract_registry(config: dict[str, Any]) -> dict[str, str]:
    registry = config["contract_registry"]
    if registry.get("hash_algorithm") != "sha256_utf8_lf":
        raise ValueError("Unsupported contract hash algorithm")
    actual: dict[str, str] = {}
    for relative, expected in registry["files"].items():
        path = PROJECT_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"Registered contract does not exist: {relative}")
        digest = sha256_utf8_lf(path)
        if digest != str(expected).upper():
            raise ValueError(f"Contract hash mismatch: {relative}; expected={expected}; actual={digest}")
        actual[relative] = digest
    return actual


def verify_raw_inputs(config: dict[str, Any]) -> dict[str, str]:
    actual: dict[str, str] = {}
    for relative, expected in config["input_hashes"].items():
        path = PROJECT_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"Required input missing: {relative}")
        digest = sha256_file(path)
        if digest != str(expected).upper():
            raise ValueError(f"Input hash mismatch: {relative}; expected={expected}; actual={digest}")
        actual[relative] = digest
    return actual


def git_commit() -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    commit = result.stdout.strip()
    if len(commit) != 40:
        raise ValueError(f"Unexpected Git commit: {commit!r}")
    return commit


def implementation_git_dirty() -> bool:
    tracked_inputs = [
        (PROJECT_ROOT / "src").relative_to(REPO_ROOT).as_posix(),
        (PROJECT_ROOT / "experiments").relative_to(REPO_ROOT).as_posix(),
    ]
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--", *tracked_inputs],
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def environment_info() -> dict[str, str]:
    try:
        import openpyxl

        openpyxl_version = openpyxl.__version__
    except Exception:
        openpyxl_version = "unavailable"
    return {
        "conda_environment": os.environ.get("CONDA_DEFAULT_ENV", "unknown"),
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
        "openpyxl": openpyxl_version,
    }


def _repo_relative_arg(value: str) -> str:
    """Render absolute paths inside this project as portable project-relative arguments."""
    candidate = Path(value)
    if not candidate.is_absolute():
        return value.replace("\\", "/")
    try:
        return candidate.resolve().relative_to(PROJECT_ROOT).as_posix()
    except (OSError, ValueError):
        return value


def relative_command() -> str:
    script = _repo_relative_arg(str(Path(sys.argv[0]).resolve()))
    arguments = [_repo_relative_arg(value) for value in sys.argv[1:]]
    return shlex.join(["python", script, *arguments])


def regression_metrics(y_true: Sequence[float], y_pred: Sequence[float]) -> dict[str, float | int]:
    true = np.asarray(y_true, dtype=np.float64)
    pred = np.asarray(y_pred, dtype=np.float64)
    if true.shape != pred.shape or true.ndim != 1:
        raise ValueError("Regression metric inputs must be one-dimensional and equal length")
    if not np.isfinite(true).all() or not np.isfinite(pred).all():
        raise ValueError("Regression metric inputs contain non-finite values")
    if np.any(true <= 0) or np.any(pred <= 0):
        raise ValueError("Regression targets and predictions must be strictly positive")
    log_error = np.log1p(np.maximum(pred, 0.0)) - np.log1p(true)
    absolute_percentage = np.abs(true - pred) / np.maximum(np.abs(true), 1.0)
    return {
        "n": int(true.size),
        "rmsle": float(np.sqrt(np.mean(log_error**2))),
        "mae_W_per_m3": float(mean_absolute_error(true, pred)),
        "rmse_W_per_m3": float(np.sqrt(mean_squared_error(true, pred))),
        "mape_percent": float(100.0 * np.mean(absolute_percentage)),
        "median_ape_percent": float(100.0 * np.median(absolute_percentage)),
        "r2_original_scale": float(r2_score(true, pred)),
    }


def log_rmse(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    true = np.asarray(y_true, dtype=np.float64)
    pred = np.asarray(y_pred, dtype=np.float64)
    if np.any(true <= 0) or np.any(pred <= 0):
        raise ValueError("log RMSE inputs must be positive")
    return float(np.sqrt(np.mean((np.log(true) - np.log(pred)) ** 2)))


def classification_metrics(y_true: Sequence[str], y_pred: Sequence[str]) -> dict[str, Any]:
    true = np.asarray(y_true, dtype=object)
    pred = np.asarray(y_pred, dtype=object)
    report = classification_report(
        true,
        pred,
        labels=WAVEFORM_LABELS,
        output_dict=True,
        zero_division=0,
    )
    return {
        "n": int(true.size),
        "accuracy": float(accuracy_score(true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(true, pred)),
        "macro_f1": float(f1_score(true, pred, labels=WAVEFORM_LABELS, average="macro")),
        "per_class": {label: report[label] for label in WAVEFORM_LABELS},
    }


def confusion_frame(y_true: Sequence[str], y_pred: Sequence[str]) -> pd.DataFrame:
    matrix = confusion_matrix(y_true, y_pred, labels=WAVEFORM_LABELS)
    frame = pd.DataFrame(matrix, index=WAVEFORM_LABELS, columns=WAVEFORM_LABELS)
    frame.index.name = "actual"
    return frame.reset_index()


def smearing_factor(y_log_train: np.ndarray, fitted_log_train: np.ndarray) -> float:
    residual = np.asarray(y_log_train) - np.asarray(fitted_log_train)
    factor = float(np.mean(np.exp(residual)))
    if not math.isfinite(factor) or factor <= 0:
        raise ValueError(f"Invalid smearing factor: {factor}")
    return factor


def pareto_mask(loss: Sequence[float], energy: Sequence[float]) -> np.ndarray:
    """Return nondominated mask for minimizing loss and maximizing energy."""

    loss_array = np.asarray(loss, dtype=np.float64)
    energy_array = np.asarray(energy, dtype=np.float64)
    if loss_array.shape != energy_array.shape or loss_array.ndim != 1:
        raise ValueError("Pareto arrays must be one-dimensional and equal length")
    if not np.isfinite(loss_array).all() or not np.isfinite(energy_array).all():
        raise ValueError("Pareto arrays contain non-finite values")
    result = np.zeros(loss_array.size, dtype=bool)
    order = np.lexsort((loss_array, -energy_array))
    best_loss_at_greater_energy = math.inf
    cursor = 0
    while cursor < order.size:
        end = cursor + 1
        current_energy = energy_array[order[cursor]]
        while end < order.size and energy_array[order[end]] == current_energy:
            end += 1
        group_indices = order[cursor:end]
        group_min_loss = float(np.min(loss_array[group_indices]))
        if group_min_loss < best_loss_at_greater_energy:
            tied = group_indices[loss_array[group_indices] == group_min_loss]
            result[tied] = True
            best_loss_at_greater_energy = group_min_loss
        cursor = end
    return result


def assert_pareto(loss: Sequence[float], energy: Sequence[float], mask: np.ndarray) -> None:
    loss_array = np.asarray(loss, dtype=np.float64)
    energy_array = np.asarray(energy, dtype=np.float64)
    selected = np.flatnonzero(mask)
    if selected.size == 0:
        raise AssertionError("Pareto set is empty")
    for index in selected:
        dominated = (
            (loss_array <= loss_array[index])
            & (energy_array >= energy_array[index])
            & ((loss_array < loss_array[index]) | (energy_array > energy_array[index]))
        )
        if np.any(dominated):
            raise AssertionError(f"Selected Pareto point {index} is dominated")


def frame_hash(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return sha256_file(path)


def load_features_and_folds() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    feature_path = S3_RESULTS_ROOT / "data" / "feature_table.csv"
    fold_path = S3_RESULTS_ROOT / "folds" / "fold_assignments.csv"
    features = pd.read_csv(feature_path)
    folds = pd.read_csv(fold_path)
    if features["row_id"].duplicated().any() or folds["row_id"].duplicated().any():
        raise ValueError("Duplicate row_id in feature or fold table")
    if set(features["row_id"]) != set(folds["row_id"]):
        raise ValueError("Feature and fold row_id sets differ")
    audit_columns = ["near_shape_group", "condition_group", "exact_record_sha256"]
    audit = features[["row_id", *audit_columns]].merge(
        folds[["row_id", *audit_columns]],
        on="row_id",
        how="inner",
        validate="one_to_one",
        suffixes=("_feature", "_fold"),
    )
    for column in audit_columns:
        if not (audit[f"{column}_feature"] == audit[f"{column}_fold"]).all():
            raise ValueError(f"Feature/fold lineage mismatch for {column}")
    merged = features.merge(
        folds[["row_id", "q1_outer_fold", "regression_outer_fold"]],
        on="row_id",
        how="inner",
        validate="one_to_one",
    )
    if len(merged) != 12400:
        raise ValueError(f"Expected 12400 merged training rows, got {len(merged)}")
    return features, folds, merged


class ExperimentRun:
    """Small run recorder that writes reproducible evidence without hiding failures."""

    def __init__(
        self,
        experiment_id: str,
        frozen_config_path: Path,
        manifest_aliases: Iterable[Path] = (),
        *,
        descriptor_path: Path | None = None,
        evidence_root: Path | None = None,
        stage: str = "S3",
    ) -> None:
        self.experiment_id = experiment_id
        self.stage = stage
        self.frozen_config_path = frozen_config_path.resolve()
        self.descriptor_path = (descriptor_path or (BASELINE_CONFIG_DIR / f"{experiment_id}.json")).resolve()
        if not self.descriptor_path.is_file():
            raise FileNotFoundError(f"Missing experiment descriptor: {self.descriptor_path}")
        self.descriptor = json.loads(self.descriptor_path.read_text(encoding="utf-8"))
        if self.descriptor.get("experiment_id") != experiment_id:
            raise ValueError("Experiment descriptor ID mismatch")
        self.output_dir = (evidence_root or BASELINE_EVIDENCE_ROOT).resolve() / experiment_id
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stdout_path = self.output_dir / "stdout.log"
        self.config_copy_path = self.output_dir / "config.json"
        self.config_copy_path.write_bytes(canonical_json_bytes(self.descriptor))
        self.manifest_aliases = list(manifest_aliases)
        self.started = datetime.now(TZ)
        self.started_perf = time.perf_counter()
        self.inputs: dict[str, str] = {
            str(self.frozen_config_path.relative_to(PROJECT_ROOT)).replace("\\", "/"): sha256_file(self.frozen_config_path),
            str(self.descriptor_path.relative_to(PROJECT_ROOT)).replace("\\", "/"): sha256_file(self.descriptor_path),
        }
        self.outputs: set[Path] = set()
        self.contract_hashes: dict[str, str] = {}
        self.finished = False
        self.log(f"START {experiment_id}")
        self.log(f"COMMAND {relative_command()}")

    def log(self, message: str) -> None:
        line = f"[{datetime.now(TZ).isoformat()}] {message}"
        print(line, flush=True)
        with self.stdout_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line + "\n")

    def record_input(self, path: Path, label: str | None = None) -> None:
        resolved = path.resolve()
        key = label or str(resolved.relative_to(PROJECT_ROOT)).replace("\\", "/")
        self.inputs[key] = sha256_file(resolved)

    def record_output(self, path: Path) -> None:
        self.outputs.add(path.resolve())

    def record_contract_hashes(self, hashes: dict[str, str]) -> None:
        if not hashes:
            raise ValueError("Contract hash registry is empty")
        self.contract_hashes = dict(sorted(hashes.items()))

    def finish(self, status: str = "PASS", error: str | None = None) -> dict[str, Any]:
        if self.finished:
            raise RuntimeError("Experiment run already finalized")
        if status == "PASS" and not self.contract_hashes:
            raise RuntimeError("Passing run must record recomputed contract hashes")
        ended = datetime.now(TZ)
        output_hashes: dict[str, str] = {}
        for path in sorted(self.outputs, key=lambda item: str(item)):
            if not path.is_file():
                raise FileNotFoundError(f"Registered output missing: {path}")
            try:
                label = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
            except ValueError:
                label = str(path)
            output_hashes[label] = sha256_file(path)
        manifest = {
            "experiment_id": self.experiment_id,
            "stage": self.stage,
            "git_commit": git_commit(),
            "implementation_git_dirty_at_finish": implementation_git_dirty(),
            "command": relative_command(),
            "command_repo_relative": relative_command(),
            "environment": environment_info(),
            "seed": self.descriptor.get("seed"),
            "started_at": self.started.isoformat(),
            "ended_at": ended.isoformat(),
            "runtime_seconds": round(time.perf_counter() - self.started_perf, 6),
            "exit_code": 0 if status == "PASS" else 1,
            "status": status,
            "error": error,
            "input_hashes": dict(sorted(self.inputs.items())),
            "contract_hashes": self.contract_hashes,
            "output_hashes": output_hashes,
        }
        manifest_path = self.output_dir / "run_manifest.json"
        write_json(manifest_path, manifest)
        for alias in self.manifest_aliases:
            write_json(alias, manifest)
        self.log(f"END {self.experiment_id} status={status} runtime_seconds={manifest['runtime_seconds']}")
        self.finished = True
        return manifest

    def fail(self, exc: BaseException) -> None:
        detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        self.log(detail.rstrip())
        self.finish("FAIL", error=f"{type(exc).__name__}: {exc}")
