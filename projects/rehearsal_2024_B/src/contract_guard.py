"""Machine-enforced phase input guard for rehearsal_2024_B.

The guard inspects a run manifest before any numerical file parser is called. It
does not open CSV files. Protected phases reject every official-test filename.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ContractBoundaryError(RuntimeError):
    """Raised when a run manifest crosses a frozen experiment boundary."""


def _basename_set(paths: list[str]) -> set[str]:
    names = [Path(value).name for value in paths]
    if len(names) != len(set(names)):
        raise ContractBoundaryError("input_files contains duplicate basenames")
    return set(names)


def validate_phase_input_manifest(
    manifest: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Validate filenames and release prerequisites without opening input data."""

    policy = config["test_release_contract"]
    phase = str(manifest.get("phase", ""))
    input_kind = str(manifest.get("input_kind", "training_csv"))
    input_files = manifest.get("input_files")
    if not phase or not isinstance(input_files, list):
        raise ContractBoundaryError("phase and input_files list are required")

    names = _basename_set([str(value) for value in input_files])
    training = set(policy["training_file_allowlist"])
    official = set(policy["official_test_denylist"])
    protected = set(policy["protected_phases"])
    detected_official = names & official

    if phase in protected:
        if detected_official:
            raise ContractBoundaryError(
                "official test input is forbidden before final release: "
                + ", ".join(sorted(detected_official))
            )
        if input_kind == "training_csv":
            unknown = names - training
            if unknown:
                raise ContractBoundaryError(
                    "protected training run contains a non-allowlisted input: "
                    + ", ".join(sorted(unknown))
                )
        elif input_kind not in set(policy["dry_run_sources"]):
            raise ContractBoundaryError(
                f"unsupported protected-phase input_kind: {input_kind}"
            )
        return {
            "status": "PASS",
            "phase": phase,
            "mode": "PROTECTED_NO_OFFICIAL_TEST",
            "official_test_file_count": 0,
            "input_file_count": len(names),
        }

    if phase != policy["final_release_phase"]:
        if detected_official:
            raise ContractBoundaryError(
                f"official test input is not authorized in phase {phase}"
            )
        raise ContractBoundaryError(f"unregistered phase: {phase}")

    if names != official:
        missing = sorted(official - names)
        extra = sorted(names - official)
        raise ContractBoundaryError(
            f"final release must name exactly all official test files; "
            f"missing={missing}, extra={extra}"
        )
    if manifest.get("gate_state") != policy["minimum_gate_state"]:
        raise ContractBoundaryError("final release requires G4_PASS")
    if int(manifest.get("prior_release_count", -1)) != int(
        policy["prior_release_count_required"]
    ):
        raise ContractBoundaryError("final release is not the first release")

    freeze = manifest.get("freeze_manifest")
    if not isinstance(freeze, dict):
        raise ContractBoundaryError("freeze_manifest object is required")
    for field in policy["required_freeze_fields"]:
        if field not in freeze or freeze[field] in (None, "", False):
            raise ContractBoundaryError(
                f"freeze_manifest field is missing or false: {field}"
            )
    if freeze.get("selection_closed") is not True:
        raise ContractBoundaryError("selection_closed must be true")

    feedback_targets = manifest.get("feedback_targets", [])
    if feedback_targets:
        raise ContractBoundaryError("post-release feedback targets must be empty")

    return {
        "status": "PASS",
        "phase": phase,
        "mode": "ONE_TIME_FINAL_RELEASE_AUTHORIZED",
        "official_test_file_count": len(official),
        "input_file_count": len(names),
        "selection_closed": True,
        "prior_release_count": 0,
    }
