"""Build the read-only figure handoff package from verified project evidence."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "package_for_deliver"
ARCHIVE_NAME = "rehearsal_2024_C_figure_handoff.zip"


FILES = {
    # Core handoff and paper context.
    "docs/figure_handoff.md": PROJECT_ROOT / "work/handoff/figure_handoff.md",
    "docs/writing_handoff.md": PROJECT_ROOT / "work/handoff/writing_handoff.md",
    "docs/technical_draft.md": PROJECT_ROOT / "paper/technical_draft.md",
    "docs/solution_plan.md": PROJECT_ROOT / "work/04_solution_plan.md",
    "docs/result_freeze.md": PROJECT_ROOT / "work/10_result_freeze.md",
    "docs/result_registry.md": PROJECT_ROOT / "results/verified/result_registry.md",
    "docs/model_freeze.json": PROJECT_ROOT / "results/verified/model_freeze.json",
    "docs/provenance.json": PROJECT_ROOT / "results/verified/provenance.json",
    "docs/guides/09_plotting_protocol.md": REPO_ROOT / "guide/09_plotting_protocol.md",
    "docs/guides/figures_guide.md": REPO_ROOT / "guide/figures_guide.md",
    "docs/model_contracts/shared_data_validation.md": PROJECT_ROOT / "work/models/00_shared_data_validation_contract.md",
    "docs/model_contracts/q1_model_contract.md": PROJECT_ROOT / "work/models/q1_model_contract.md",
    "docs/model_contracts/q2_model_contract.md": PROJECT_ROOT / "work/models/q2_model_contract.md",
    "docs/model_contracts/q3_model_contract.md": PROJECT_ROOT / "work/models/q3_model_contract.md",
    "docs/model_contracts/q4_model_contract.md": PROJECT_ROOT / "work/models/q4_model_contract.md",
    "docs/model_contracts/q5_model_contract.md": PROJECT_ROOT / "work/models/q5_model_contract.md",
    # Figure 2: data audit and sample structure.
    "data/verified/data/categorical_counts.csv": PROJECT_ROOT / "results/verified/data/categorical_counts.csv",
    "data/verified/data/data_profile.json": PROJECT_ROOT / "results/verified/data/data_profile.json",
    "data/verified/data/dataset_summary.csv": PROJECT_ROOT / "results/verified/data/dataset_summary.csv",
    "data/verified/data/numeric_ranges.csv": PROJECT_ROOT / "results/verified/data/numeric_ranges.csv",
    "data/verified/data/quality_checks.csv": PROJECT_ROOT / "results/verified/data/quality_checks.csv",
    # Figures 6 and 7: temperature correction.
    "data/verified/q2/quadratic_temperature_metrics.json": PROJECT_ROOT / "results/verified/q2/quadratic_temperature_metrics.json",
    "data/verified/q2/quadratic_temperature_by_temperature.csv": PROJECT_ROOT / "results/verified/q2/quadratic_temperature_by_temperature.csv",
    "data/verified/q2/leave_one_temperature_comparison.csv": PROJECT_ROOT / "results/verified/q2/leave_one_temperature_comparison.csv",
    "data/verified/q2/quadratic_temperature_parameters.csv": PROJECT_ROOT / "results/verified/q2/quadratic_temperature_parameters.csv",
    # Figures 5, 6 and 7: Q4 prediction, ablation and stress.
    "data/verified/q4/final_oof_predictions.csv": PROJECT_ROOT / "results/verified/q4/final_oof_predictions.csv",
    "data/verified/q4/hgb_metrics.json": PROJECT_ROOT / "results/verified/q4/hgb_metrics.json",
    "data/verified/q4/hgb_subgroup_metrics.csv": PROJECT_ROOT / "results/verified/q4/hgb_subgroup_metrics.csv",
    "data/verified/q4/ablation_metrics.csv": PROJECT_ROOT / "results/verified/q4/ablation_metrics.csv",
    "data/verified/q4/ablation_metrics.json": PROJECT_ROOT / "results/verified/q4/ablation_metrics.json",
    "data/verified/q4/stress_subset_metrics.csv": PROJECT_ROOT / "results/verified/q4/stress_subset_metrics.csv",
    "data/verified/q4/stress_metrics.json": PROJECT_ROOT / "results/verified/q4/stress_metrics.json",
    "data/verified/q4/leave_one_level_out_metrics.csv": PROJECT_ROOT / "results/verified/q4/leave_one_level_out_metrics.csv",
    # Figures 4, 7 and 8: Pareto evidence, stability and decision boundary.
    "data/verified/q5/final_oof_pareto.csv": PROJECT_ROOT / "results/verified/q5/final_oof_pareto.csv",
    "data/verified/q5/final_full_fit_reference_pareto.csv": PROJECT_ROOT / "results/verified/q5/final_full_fit_reference_pareto.csv",
    "data/verified/q5/representative_conditions.json": PROJECT_ROOT / "results/verified/q5/representative_conditions.json",
    "data/verified/q5/heldout_fold_region_support.csv": PROJECT_ROOT / "results/verified/q5/heldout_fold_region_support.csv",
    "data/verified/q5/bootstrap_region_stability.csv": PROJECT_ROOT / "results/verified/q5/bootstrap_region_stability.csv",
    "data/verified/q5/robustness_metrics.json": PROJECT_ROOT / "results/verified/q5/robustness_metrics.json",
    "data/verified/q5/sensitivity_scenarios.csv": PROJECT_ROOT / "results/verified/q5/sensitivity_scenarios.csv",
    "data/verified/q5/sensitivity_metrics.json": PROJECT_ROOT / "results/verified/q5/sensitivity_metrics.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> int:
    missing = [str(source) for source in FILES.values() if not source.is_file()]
    if missing:
        raise FileNotFoundError("Missing package inputs:\n" + "\n".join(missing))
    if any("results/raw" in source.as_posix() for source in FILES.values()):
        raise RuntimeError("The delivery package must not copy results/raw files.")

    PACKAGE_ROOT.mkdir(parents=True, exist_ok=True)
    managed = set(FILES) | {"README.md", "verify_package.py", "MANIFEST_SHA256.json", ARCHIVE_NAME, "ARCHIVE_SHA256.txt"}
    unexpected = [
        path.relative_to(PACKAGE_ROOT).as_posix()
        for path in PACKAGE_ROOT.rglob("*")
        if path.is_file() and path.relative_to(PACKAGE_ROOT).as_posix() not in managed
    ]
    if unexpected:
        raise RuntimeError("Refusing to overwrite a package with unmanaged files: " + ", ".join(unexpected))

    entries = []
    for destination, source in sorted(FILES.items()):
        target = PACKAGE_ROOT / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        entries.append(
            {
                "package_path": destination,
                "source_path": source.relative_to(REPO_ROOT).as_posix(),
                "size_bytes": target.stat().st_size,
                "sha256": sha256(target),
            }
        )

    for local_name in ("README.md", "verify_package.py"):
        local_path = PACKAGE_ROOT / local_name
        entries.append(
            {
                "package_path": local_name,
                "source_path": local_path.relative_to(REPO_ROOT).as_posix(),
                "size_bytes": local_path.stat().st_size,
                "sha256": sha256(local_path),
            }
        )

    manifest = {
        "package": "rehearsal_2024_C figure handoff",
        "generated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "source_git_commit": git_head(),
        "source_policy": "Only verified numerical evidence and necessary documentation are copied; results/raw and original contest attachments are excluded.",
        "file_count_excluding_manifest_and_archive": len(entries),
        "files": sorted(entries, key=lambda item: item["package_path"]),
    }
    manifest_path = PACKAGE_ROOT / "MANIFEST_SHA256.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    archive_path = PACKAGE_ROOT / ARCHIVE_NAME
    archive_members = [PACKAGE_ROOT / item["package_path"] for item in manifest["files"]] + [manifest_path]
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for member in sorted(archive_members):
            archive.write(member, member.relative_to(PACKAGE_ROOT).as_posix())
    archive_hash = sha256(archive_path)
    (PACKAGE_ROOT / "ARCHIVE_SHA256.txt").write_text(f"{archive_hash}  {ARCHIVE_NAME}\n", encoding="utf-8")

    print(f"FIGURE_DELIVERY_PACKAGE_PASS: {len(entries)} files")
    print(f"archive={archive_path}")
    print(f"archive_sha256={archive_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
