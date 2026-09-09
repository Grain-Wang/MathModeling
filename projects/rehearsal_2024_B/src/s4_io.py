"""Guarded S4 input and provenance helpers.

This module deliberately leaves the frozen S3 implementation untouched. The
S4 entry has its own G3 authorization check and invokes the phase guard before
the first numerical CSV parser call.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from contract_guard import ContractBoundaryError, validate_phase_input_manifest
from s1_data_audit import DATA, EXPECTED
from s2_contract_validation import contract_artifact_verification
from s3_io import (
    CONFIG_PATH,
    PROJECT,
    REGISTRY_PATH,
    REPO,
    RunState,
    canonical_relative,
    git,
    load_guarded_training,
    load_json,
    registry_core_sha,
    sha256,
    verify_all_file_hashes,
)

S4_CONFIG_PATH = PROJECT / "configs" / "s4_candidate_plan.json"
G3_REVIEW_PATH = PROJECT / "reviews" / "gate_3_review.md"
OUTPUT = PROJECT / "results" / "raw" / "main"
EXPERIMENT_ROOT = PROJECT / "experiments"
EXPECTED_G3_REVIEW_COMMIT = "a5433257bf94ab651a53b86244d8a86edc72f9e4"
EXPECTED_REVIEWED_COMMIT = "e352c4233bb6a974e974ab697481b712a9c83d0b"
EXPECTED_CORE_SHA = "88B108D181C2EA3A723303DED3D0E64BACEF7FA482F8322712ED97ED020A6C2D"
BASELINE_FORMAL_HEAD = "2222cf5f4e17a6dac832c4e65f9c5a60cd01060d"
BASELINE_SOURCES = [
    PROJECT / "src" / name
    for name in [
        "s3_baseline.py",
        "s3_evaluation.py",
        "s3_features.py",
        "s3_io.py",
        "s3_lineage.py",
        "s3_metrics.py",
        "s3_models.py",
    ]
]
BASELINE_EVIDENCE = [
    PROJECT / "results" / "raw" / "baseline" / name
    for name in [
        "run_manifest.json",
        "post_run_validation.json",
        "feature_schema.json",
        "q1_oof_predictions.jsonl.gz",
        "q2_oof_predictions.jsonl.gz",
        "q3_ap_oof_predictions.jsonl.gz",
        "q3_system_oof_predictions.jsonl.gz",
        "q1_metrics.json",
        "q2_metrics.json",
        "q3_metrics.json",
    ]
]


def verify_g3_review() -> dict[str, Any]:
    text = G3_REVIEW_PATH.read_text(encoding="utf-8")
    checks = {
        "verdict_pass": "Verdict: **PASS**" in text,
        "transition_authorized": "S3 -> S4 = AUTHORIZED" in text,
        "reviewed_commit": EXPECTED_REVIEWED_COMMIT in text,
        "review_commit_is_current_ancestor": git(
            "merge-base", EXPECTED_G3_REVIEW_COMMIT, git("rev-parse", "HEAD")
        ) == EXPECTED_G3_REVIEW_COMMIT,
    }
    if not all(checks.values()):
        raise RuntimeError(f"G3 authorization check failed: {checks}")
    return {
        "status": "PASS",
        "path": canonical_relative(G3_REVIEW_PATH),
        "sha256": sha256(G3_REVIEW_PATH),
        "review_commit": EXPECTED_G3_REVIEW_COMMIT,
        "checks": checks,
    }


def guarded_s4_inputs(
    config: dict[str, Any],
    state: RunState,
    names_override: list[str] | None = None,
) -> tuple[list[Path], dict[str, Any]]:
    policy = config["test_release_contract"]
    names = (
        list(names_override)
        if names_override is not None
        else list(policy["training_file_allowlist"])
    )
    paths = [DATA / name for name in names]
    manifest = {
        "phase": "S4",
        "input_kind": "training_csv",
        "input_files": [str(path) for path in paths],
        "config_sha256": sha256(CONFIG_PATH),
        "s4_config_sha256": sha256(S4_CONFIG_PATH),
        "guard_sha256": sha256(PROJECT / "src" / "contract_guard.py"),
    }
    guard = validate_phase_input_manifest(manifest, config)
    if names_override is not None:
        return paths, {"manifest": manifest, "guard_result": guard}
    allowlist = set(policy["training_file_allowlist"])
    if {path.name for path in paths} != allowlist or len(paths) != len(allowlist):
        raise RuntimeError("S4 training input list differs from frozen allowlist")
    records = []
    for path in paths:
        spec = EXPECTED[path.name]
        if path.resolve().parent != DATA.resolve() or spec["role"] != "train":
            raise RuntimeError(f"illegal S4 numerical input: {path}")
        if not path.is_file() or path.stat().st_size != spec["bytes"]:
            raise RuntimeError(f"S4 input missing/size mismatch: {path.name}")
        digest = sha256(path)
        if digest != spec["sha256"]:
            raise RuntimeError(f"S4 input hash mismatch: {path.name}")
        records.append({
            "name": path.name,
            "canonical_relative_path": canonical_relative(path),
            "bytes": path.stat().st_size,
            "sha256": digest,
            "role": "train",
        })
    return paths, {
        "manifest": manifest,
        "guard_result": guard,
        "canonical_input_records": records,
        "numeric_read_count_at_guard_return": state.csv_numeric_read_count,
    }


def real_s4_entry_guard_tests(config: dict[str, Any]) -> dict[str, Any]:
    state = RunState()
    train = list(config["test_release_contract"]["training_file_allowlist"])
    official = list(config["test_release_contract"]["official_test_denylist"])
    legal = guarded_s4_inputs(config, state, train)[1]["guard_result"]
    rejected = []
    for name in official:
        try:
            guarded_s4_inputs(config, state, train + [name])
        except ContractBoundaryError as error:
            rejected.append({
                "file": name,
                "rejected": True,
                "message": str(error),
            })
        else:
            rejected.append({"file": name, "rejected": False})
    checks = {
        "legal_training_manifest_passes": legal["status"] == "PASS",
        "all_official_injections_rejected": all(x["rejected"] for x in rejected),
        "no_csv_numeric_parser_called": state.csv_numeric_read_count == 0,
    }
    if not all(checks.values()):
        raise AssertionError(f"real S4 entry guard tests failed: {checks}")
    return {"status": "PASS", "checks": checks, "cases": rejected}


def verify_s4_plan(
    config: dict[str, Any], s4_config: dict[str, Any]
) -> dict[str, Any]:
    frozen_grid = config["main_candidate_budget"]["grid"]
    checks = {
        "stage": s4_config["stage"] == "S4",
        "review_commit": (
            s4_config["authorized_by_review_commit"]
            == EXPECTED_G3_REVIEW_COMMIT
        ),
        "only_q2_q3": s4_config["authorized_directions"] == ["Q2", "Q3"],
        "grid_exact": s4_config["hgb_grid"] == frozen_grid,
        "q2_grid_count": len(s4_config["hgb_grid"]) == 4,
        "q3_candidate_count": len(s4_config["hgb_grid"]) * 2 == 8,
        "ap_count_numeric_shared": (
            s4_config["ap_count_representation"]
            == "numeric_binary_2_or_3_shared_by_all_s4_candidates"
        ),
        "a03_honest_boundary": (
            s4_config["a03_sensitivity"]
            == "evaluation_exclusion_diagnostic_only_no_training_robustness_claim"
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(f"S4 plan mismatch: {checks}")
    return {"status": "PASS", "checks": checks}


def verify_baseline_snapshot() -> dict[str, Any]:
    missing = [canonical_relative(path) for path in BASELINE_EVIDENCE if not path.is_file()]
    if missing:
        raise RuntimeError(f"missing baseline evidence: {missing}")
    changed = git(
        "diff", "--name-only", BASELINE_FORMAL_HEAD, "--",
        *[canonical_relative(path) for path in BASELINE_SOURCES],
    )
    manifest = load_json(BASELINE_EVIDENCE[0])
    validation = load_json(BASELINE_EVIDENCE[1])
    checks = {
        "formal_head": manifest["git_head"] == BASELINE_FORMAL_HEAD,
        "run_pass": manifest["status"] == "PASS",
        "validation_pass": validation["status"] == "PASS",
        "generation_sources_unchanged": changed == "",
        "official_test_numeric_reads_zero": (
            manifest["official_test_numeric_read_count"] == 0
        ),
        "official_test_predictions_zero": (
            manifest["official_test_prediction_count"] == 0
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(f"baseline snapshot failed: {checks}")
    return {
        "status": "PASS",
        "checks": checks,
        "artifacts": [
            {
                "path": canonical_relative(path),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in BASELINE_EVIDENCE
        ],
    }


def preflight_s4(
    config: dict[str, Any],
    s4_config: dict[str, Any],
    registry: dict[str, Any],
    state: RunState,
) -> tuple[list[Path], dict[str, Any], str]:
    gate = verify_g3_review()
    plan = verify_s4_plan(config, s4_config)
    guard_tests = real_s4_entry_guard_tests(config)
    paths, entry = guarded_s4_inputs(config, state)
    identities = verify_all_file_hashes()
    contracts = contract_artifact_verification(config)
    core = registry_core_sha(registry)
    baseline = verify_baseline_snapshot()
    if contracts["status"] != "PASS":
        raise RuntimeError("approved contract artifact hashes no longer match")
    if core != registry["registry_core_sha256"] or core != EXPECTED_CORE_SHA:
        raise RuntimeError("frozen split registry core hash mismatch")
    evidence = {
        "status": "PASS",
        "gate_review": gate,
        "s4_plan": plan,
        "real_entry_guard_tests": guard_tests,
        "entry": entry,
        "file_identity": identities,
        "contract_artifacts": contracts,
        "baseline_snapshot": baseline,
        "split_registry": {
            "path": canonical_relative(REGISTRY_PATH),
            "file_sha256": sha256(REGISTRY_PATH),
            "recorded_core_sha256": registry["registry_core_sha256"],
            "recomputed_core_sha256": core,
            "outer_fold_count": registry["outer_fold_count"],
            "loso_split_count": registry["loso_split_count"],
        },
        "model_fit_count": 0,
        "csv_numeric_read_count": 0,
        "official_test_numeric_read_count": 0,
        "official_test_prediction_count": 0,
    }
    return paths, evidence, core


__all__ = [
    "CONFIG_PATH",
    "EXPERIMENT_ROOT",
    "OUTPUT",
    "PROJECT",
    "REGISTRY_PATH",
    "REPO",
    "RunState",
    "S4_CONFIG_PATH",
    "canonical_relative",
    "git",
    "load_guarded_training",
    "load_json",
    "preflight_s4",
    "sha256",
]
