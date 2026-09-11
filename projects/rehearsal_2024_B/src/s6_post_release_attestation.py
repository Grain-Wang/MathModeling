"""Post-release binding and semantic attestation for G5 Minor-01/02.

This script deliberately does not open an official-test CSV and never invokes
model inference.  It hashes frozen training-side inputs and tracked contracts,
then validates only the already committed release JSONL and joblib metadata.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import joblib


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
VERIFIED = PROJECT / "results" / "verified"
RAW_MAIN = PROJECT / "results" / "raw" / "main"
RAW_BASE = PROJECT / "results" / "raw" / "baseline"
FINAL = PROJECT / "results" / "raw" / "final"
RELEASE = FINAL / "release"
DATA = PROJECT / "problem" / "data"
FREEZE_PATH = VERIFIED / "freeze_manifest.json"
FREEZE_SIDECAR = VERIFIED / "freeze_manifest.sha256"
LEDGER_PATH = FINAL / "test_release_ledger.json"
RELEASE_MANIFEST_PATH = RELEASE / "release_manifest.json"
OUTPUT_SCHEMA_PATH = PROJECT / "configs" / "s5_output_schema.json"
ATTESTATION_PATH = VERIFIED / "post_release_binding_attestation.json"

RAW_OUTPUTS = {
    "q1": RELEASE / "q1_ap_predictions.jsonl",
    "q2": RELEASE / "q2_ap_predictions.jsonl",
    "q3": RELEASE / "q3_ap_predictions.jsonl",
    "q3_system": RELEASE / "q3_system_predictions.jsonl",
}
MODEL_PATHS = {
    "q1": RELEASE / "models" / "q1_model.joblib",
    "q2": RELEASE / "models" / "q2_model.joblib",
    "q3": RELEASE / "models" / "q3_model_bundle.joblib",
}


def now() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")


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


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def check(condition: bool, name: str) -> bool:
    if not condition:
        raise AssertionError(name)
    return True


def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=REPO,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def record_hashes(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observed = []
    for frozen in records:
        path = REPO / frozen["path"]
        actual = sha256(path)
        check(actual == frozen["sha256"], f"frozen artifact drift: {frozen['path']}")
        observed.append({
            "path": frozen["path"],
            "expected_sha256": frozen["sha256"],
            "actual_sha256": actual,
            "match": True,
        })
    return observed


def validate_bindings(
    freeze: dict[str, Any], ledger: dict[str, Any], release: dict[str, Any]
) -> tuple[dict[str, bool], dict[str, Any], dict[str, Any]]:
    sidecar = FREEZE_SIDECAR.read_text(encoding="ascii").split()[0].upper()
    checks: dict[str, bool] = {}
    checks["freeze_sidecar_matches_manifest"] = check(
        sidecar == sha256(FREEZE_PATH), "freeze manifest sidecar mismatch"
    )

    training_records = []
    for frozen in freeze["training_inputs"]:
        path = DATA / frozen["name"]
        actual = sha256(path)
        size = path.stat().st_size
        check(actual == frozen["sha256"], f"training input hash drift: {frozen['name']}")
        check(size == int(frozen["bytes"]), f"training input size drift: {frozen['name']}")
        training_records.append({
            "name": frozen["name"], "bytes": size, "sha256": actual, "match": True
        })
    checks["all_13_training_hashes_match_freeze"] = check(
        len(training_records) == 13, "frozen training input count is not 13"
    )
    checks["training_aggregate_hash_matches_freeze"] = check(
        canonical_sha([
            {"name": row["name"], "bytes": row["bytes"], "sha256": row["sha256"]}
            for row in training_records
        ]) == freeze["training_inputs_sha256"],
        "training aggregate hash mismatch",
    )

    configs = record_hashes(freeze["configs"])
    schemas = record_hashes(freeze["feature_schemas"])
    split = record_hashes([freeze["split_registry"]])
    output_schema = record_hashes([freeze["output_schema"]])
    checks["s2_s4_config_hashes_match_freeze"] = check(
        len(configs) == 2, "frozen config count mismatch"
    )
    checks["feature_schema_hashes_match_freeze"] = check(
        canonical_sha([
            {"path": row["path"], "sha256": row["actual_sha256"]}
            for row in schemas
        ]) == freeze["feature_schema_sha256"],
        "feature schema aggregate hash mismatch",
    )
    checks["split_registry_hash_matches_freeze"] = check(
        len(split) == 1, "split registry binding mismatch"
    )
    checks["output_schema_hash_matches_freeze"] = check(
        output_schema[0]["actual_sha256"] == freeze["output_schema_sha256"],
        "output schema top-level hash mismatch",
    )

    validation_manifest = RAW_MAIN / "validation_manifest.json"
    checks["g4_validation_manifest_hash_matches_freeze"] = check(
        sha256(validation_manifest)
        == freeze["prior_validation"]["g4_validated_artifact_manifest_sha256"],
        "G4 validation manifest hash mismatch",
    )
    consumed = {
        item["path"]: item for item in load(validation_manifest)["consumed_artifacts"]
    }
    baseline_run = load(RAW_BASE / "run_manifest.json")
    main_run = load(RAW_MAIN / "run_manifest.json")
    baseline_outputs = {
        item["path"]: item for item in baseline_run["output_artifacts"]
    }
    q1_oof = RAW_BASE / "q1_oof_predictions.jsonl.gz"
    q1_oof_key = relative(q1_oof)
    checks["q1_oof_hash_matches_g4_manifest"] = check(
        q1_oof_key in consumed and sha256(q1_oof) == consumed[q1_oof_key]["sha256"],
        "Q1 OOF hash mismatch against G4 manifest",
    )
    prior_artifacts = {**baseline_outputs, **consumed}
    for frozen_schema in freeze["feature_schemas"]:
        path = frozen_schema["path"]
        check(
            path in prior_artifacts
            and prior_artifacts[path]["sha256"] == frozen_schema["sha256"],
            f"feature schema is not bound by a prior manifest: {path}",
        )
    checks["feature_schemas_match_prior_run_and_g4_manifests"] = True
    checks["split_registry_matches_prior_run_manifests"] = check(
        baseline_run["split_registry_sha256"] == freeze["split_registry"]["sha256"]
        and main_run["split_registry_sha256"] == freeze["split_registry"]["sha256"],
        "split registry differs from a prior run manifest",
    )

    successes = [item for item in ledger["attempts"] if item["status"] == "SUCCEEDED"]
    checks["ledger_has_exactly_one_success"] = check(
        ledger["successful_release_count"] == 1 and len(successes) == 1,
        "exactly-once ledger success count mismatch",
    )
    success = successes[0]
    release_id = success["release_id"]
    checks["release_manifest_hash_matches_ledger"] = check(
        sha256(RELEASE_MANIFEST_PATH) == success["release_manifest_sha256"],
        "release manifest hash mismatch against ledger",
    )
    checks["release_identity_matches_ledger_and_freeze"] = check(
        release["release_id"] == release_id
        and release["freeze_manifest_sha256"] == sidecar
        and success["freeze_manifest_sha256"] == sidecar,
        "release identity mismatch",
    )
    checks["release_execution_head_descends_from_frozen_source"] = check(
        git_is_ancestor(freeze["source_commit"], release["execution_head"]),
        "release execution head is not a descendant of frozen source commit",
    )

    manifest_artifacts = {item["path"]: item for item in release["artifacts"]}
    ledger_artifacts = {item["path"]: item for item in success["model_and_output_artifacts"]}
    checks["ledger_and_release_artifact_sets_match"] = check(
        manifest_artifacts == ledger_artifacts and len(manifest_artifacts) == 7,
        "ledger/release artifact records differ",
    )
    artifact_records = []
    for path_text, frozen_artifact in sorted(manifest_artifacts.items()):
        path = REPO / path_text
        actual_hash = sha256(path)
        actual_bytes = path.stat().st_size
        check(actual_hash == frozen_artifact["sha256"], f"release hash drift: {path_text}")
        check(actual_bytes == frozen_artifact["bytes"], f"release size drift: {path_text}")
        artifact_records.append({
            "path": path_text, "bytes": actual_bytes, "sha256": actual_hash, "match": True
        })
    checks["all_release_model_and_output_hashes_match"] = True

    verified_copies = []
    for path in RAW_OUTPUTS.values():
        copy = VERIFIED / f"official_{path.name}"
        check(sha256(copy) == sha256(path), f"verified output copy drift: {copy.name}")
        verified_copies.append({
            "raw_path": relative(path), "verified_path": relative(copy),
            "sha256": sha256(copy), "match": True,
        })
    checks["verified_output_copies_match_release"] = True
    details = {
        "training_inputs": training_records,
        "configs": configs,
        "feature_schemas": schemas,
        "split_registry": split,
        "output_schema": output_schema,
        "release_artifacts": artifact_records,
        "verified_output_copies": verified_copies,
        "q1_oof": {"path": q1_oof_key, "sha256": sha256(q1_oof)},
    }
    return checks, details, {"release_id": release_id, "success": success}


def validate_rows_and_models(
    freeze: dict[str, Any], release: dict[str, Any], identity: dict[str, Any]
) -> tuple[dict[str, bool], dict[str, Any]]:
    release_id = identity["release_id"]
    rows = {name: read_jsonl(path) for name, path in RAW_OUTPUTS.items()}
    schema = load(OUTPUT_SCHEMA_PATH)["artifacts"]
    expected_counts = {
        "q1": schema["q1_ap_predictions.jsonl"]["row_count"],
        "q2": schema["q2_ap_predictions.jsonl"]["row_count"],
        "q3": schema["q3_ap_predictions.jsonl"]["row_count"],
        "q3_system": schema["q3_system_predictions.jsonl"]["row_count"],
    }
    checks: dict[str, bool] = {}
    checks["output_row_counts_match_schema"] = check(
        all(len(rows[name]) == count for name, count in expected_counts.items()),
        "release output row count mismatch",
    )
    checks["all_rows_match_unique_release_id"] = check(
        all(row["release_id"] == release_id for group in rows.values() for row in group),
        "output row release_id mismatch",
    )

    feature_hash = freeze["feature_schema_sha256"]
    q1_id = freeze["models"]["q1"]["model_id"]
    q2_id = freeze["models"]["q2"]["model_id"]
    q3_id = freeze["models"]["q3"]["model_id"]
    q3_config = freeze["models"]["q3"]["configuration_id"]
    checks["q1_rows_match_frozen_model_and_feature_bundle"] = check(
        all(row["model_id"] == q1_id and row["feature_schema_sha256"] == feature_hash
            for row in rows["q1"]),
        "Q1 row metadata mismatch",
    )
    labels = freeze["q2_label_order"]
    q2_semantics = True
    for row in rows["q2"]:
        probabilities = row["probability_fixed_17"]
        argmax_index = max(range(len(probabilities)), key=probabilities.__getitem__)
        predicted = labels[argmax_index]
        nss, mcs = (int(value) for value in predicted.split("|", 1))
        q2_semantics = q2_semantics and (
            row["model_id"] == q2_id
            and row["feature_schema_sha256"] == feature_hash
            and row["probability_label_order"] == labels
            and len(probabilities) == len(labels)
            and row["predicted_joint_label"] == predicted
            and int(row["predict_nss"]) == nss
            and int(row["predict_mcs"]) == mcs
        )
    checks["q2_argmax_label_split_and_frozen_metadata_match"] = check(
        q2_semantics, "Q2 posterior semantic assertion failed"
    )
    checks["q3_rows_match_frozen_model_config_and_feature_bundle"] = check(
        all(
            row["model_id"] == q3_id
            and row["configuration_id"] == q3_config
            and row["feature_schema_sha256"] == feature_hash
            and row["q1_model_id"] == q1_id
            for row in rows["q3"]
        ),
        "Q3 row metadata mismatch",
    )
    checks["q3_system_rows_match_frozen_model"] = check(
        all(row["model_id"] == q3_id for row in rows["q3_system"]),
        "Q3 system model metadata mismatch",
    )

    q1_by_key = {row["row_key"]: row for row in rows["q1"]}
    q3_by_key = {row["row_key"]: row for row in rows["q3"]}
    checks["q1_q3_row_key_sets_and_bounded_values_are_identical"] = check(
        q1_by_key.keys() == q3_by_key.keys()
        and all(
            q1_by_key[key]["seq_time_bounded"]
            == q3_by_key[key]["q1_seq_time_bounded"]
            for key in q1_by_key
        ),
        "Q1/Q3 bounded Q1 feature mismatch",
    )

    ap_groups: dict[str, set[str]] = {}
    for row in rows["q3"]:
        group_id = f"{row['source_file']}::{int(row['test_id'])}"
        ap_groups.setdefault(group_id, set()).add(row["row_key"])
    system_component_match = True
    for row in rows["q3_system"]:
        expected = ap_groups.get(row["group_id"], set())
        system_component_match = system_component_match and (
            set(row["component_row_keys"]) == expected
            and len(row["component_row_keys"]) == len(expected) == int(row["ap_count"])
        )
    checks["system_component_row_keys_equal_ap_component_sets"] = check(
        system_component_match and len(ap_groups) == len(rows["q3_system"]),
        "Q3 system component set mismatch",
    )

    model_packages = {name: joblib.load(path) for name, path in MODEL_PATHS.items()}
    eta = float(release["audit"]["q3_eta"])
    expected_q1_training_feature = "three-repeat registered Q1-B1 outer-OOF mean"
    checks["q1_joblib_outer_metadata_matches_freeze_and_release"] = check(
        model_packages["q1"].get("release_id") == release_id
        and model_packages["q1"].get("model_id") == q1_id,
        "Q1 joblib metadata mismatch",
    )
    checks["q2_joblib_outer_metadata_matches_freeze_and_release"] = check(
        model_packages["q2"].get("release_id") == release_id
        and model_packages["q2"].get("model_id") == q2_id
        and model_packages["q2"].get("label_order") == labels,
        "Q2 joblib metadata mismatch",
    )
    checks["q3_joblib_outer_metadata_matches_freeze_and_release"] = check(
        model_packages["q3"].get("release_id") == release_id
        and model_packages["q3"].get("model_id") == q3_id
        and model_packages["q3"].get("configuration_id") == q3_config
        and math.isclose(float(model_packages["q3"].get("eta")), eta, rel_tol=0.0, abs_tol=0.0)
        and model_packages["q3"].get("q1_training_feature") == expected_q1_training_feature
        and all(math.isclose(float(row["eta"]), eta, rel_tol=0.0, abs_tol=0.0)
                for row in rows["q3"]),
        "Q3 joblib metadata mismatch",
    )

    details = {
        "release_id": release_id,
        "row_counts": {name: len(group) for name, group in rows.items()},
        "frozen_model_ids": {"q1": q1_id, "q2": q2_id, "q3": q3_id},
        "q3_configuration_id": q3_config,
        "feature_bundle_sha256": feature_hash,
        "q2_label_order_sha256": freeze["q2_label_order_sha256"],
        "q3_eta": eta,
        "joblib_access": "outer metadata loaded; no pipeline method invoked",
    }
    return checks, details


def main() -> int:
    freeze = load(FREEZE_PATH)
    ledger = load(LEDGER_PATH)
    release = load(RELEASE_MANIFEST_PATH)
    binding_checks, binding_details, identity = validate_bindings(freeze, ledger, release)
    semantic_checks, semantic_details = validate_rows_and_models(freeze, release, identity)
    all_checks = {**binding_checks, **semantic_checks}
    payload = {
        "status": "PASS",
        "stage": "S6_POST_RELEASE_ATTESTATION",
        "created_at": "2026-09-11T00:00:00+08:00",
        "scope": "frozen training/config/schema hashes and committed release artifacts only",
        "official_test_csv_numeric_read_count": 0,
        "model_inference_count": 0,
        "release_id": identity["release_id"],
        "freeze_manifest_sha256": sha256(FREEZE_PATH),
        "release_manifest_sha256": sha256(RELEASE_MANIFEST_PATH),
        "ledger_sha256": sha256(LEDGER_PATH),
        "check_count": len(all_checks),
        "checks": all_checks,
        "binding_details": binding_details,
        "semantic_details": semantic_details,
    }
    check(all(all_checks.values()), "post-release attestation contains a failed check")
    dump(ATTESTATION_PATH, payload)
    print("status=PASS")
    print(f"checks={len(all_checks)}/{len(all_checks)}")
    print("official_test_csv_numeric_read_count=0")
    print("model_inference_count=0")
    print(f"output={relative(ATTESTATION_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
