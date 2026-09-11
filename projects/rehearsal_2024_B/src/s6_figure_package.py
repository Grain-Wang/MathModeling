"""Build a verified-only, deterministic handoff package for the figure teammate."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
VERIFIED = PROJECT / "results" / "verified"
PACKAGE_ROOT = PROJECT / "package_for_deliver"
PACKAGE_NAME = "figure_handoff_2024_B"
PACKAGE_DIR = PACKAGE_ROOT / PACKAGE_NAME
ZIP_PATH = PACKAGE_ROOT / "rehearsal_2024_B_figure_handoff.zip"
S6_MANIFEST = VERIFIED / "s6_handoff_manifest.json"
G5_REVIEW_COMMIT = "3862fee66a3c1ca362202b8d5d9e8b5d7eb2137b"

COPY_MAP = {
    PROJECT / "work" / "handoff" / "figure_handoff.md": "handoff/figure_handoff.md",
    VERIFIED / "result_registry.md": "handoff/result_registry.md",
    PROJECT / "work" / "10_result_freeze.md": "handoff/result_freeze.md",
    VERIFIED / "verified_metrics.json": "data/verified_metrics.json",
    VERIFIED / "q1_metrics.json": "data/q1_metrics.json",
    VERIFIED / "q2_baseline_metrics.json": "data/q2_baseline_metrics.json",
    VERIFIED / "q2_candidate_metrics.json": "data/q2_candidate_metrics.json",
    VERIFIED / "q3_baseline_metrics.json": "data/q3_baseline_metrics.json",
    VERIFIED / "q3_candidate_metrics.json": "data/q3_candidate_metrics.json",
    VERIFIED / "group_bootstrap_intervals.json": "data/group_bootstrap_intervals.json",
    VERIFIED / "stratified_metrics.json": "data/stratified_metrics.json",
    VERIFIED / "failure_cases.json": "data/failure_cases.json",
    VERIFIED / "selection_reconstruction.json": "data/selection_reconstruction.json",
    VERIFIED / "freeze_manifest.json": "evidence/freeze_manifest.json",
    VERIFIED / "post_release_binding_attestation.json": "evidence/post_release_binding_attestation.json",
    REPO / "guide" / "09_plotting_protocol.md": "guides/09_plotting_protocol.md",
    REPO / "guide" / "figures_guide.md": "guides/figures_guide.md",
    REPO / "guide" / "figure_color1_guide.md": "guides/figure_color1_guide.md",
    REPO / "guide" / "figure_color2_guide.md": "guides/figure_color2_guide.md",
}

README = """# 2024_B 配图交接包

本包是 S6 配图同学的只读输入快照。包内数值材料全部来自
`projects/rehearsal_2024_B/results/verified/`；请只使用
`handoff/result_registry.md` 中已登记的 Evidence ID，并遵循
`handoff/figure_handoff.md` 的图题、坐标、精度和禁止措辞要求。

## 建议作图范围

- F1：Q3 冻结模型比较，来源 `q3_baseline_metrics.json`、`q3_candidate_metrics.json`。
- F2：Q3 分组 bootstrap 不确定性，来源 `group_bootstrap_intervals.json`。
- F3：Q3 primary 与 source-blind LOSO 对比，来源 `q3_candidate_metrics.json`、`stratified_metrics.json`。
- F4：Q2 晋级阈值与回退，来源 `verified_metrics.json`、Q2 baseline/candidate metrics。
- F5：当前只可绘制 Q1 已验证的准确性部分，来源 `q1_metrics.json`；特征重要性文件尚未迁入 verified，不得自行从 raw 取用。

## 边界

- 包内不含原始 CSV、joblib 模型和官方无标签预测文件。
- 官方测试预测没有标签，禁止绘制或声称 accuracy、误差或性能提升。
- 不得手工抄写图中数值；绘图脚本应直接读取 `data/` 文件并保留图数据快照。
- 正式作图前，主负责人仍需按仓库规则确认具体绘图 skill；本包本身不生成任何图。
- 图注必须写明 Evidence ID 和源文件；bootstrap 只能称为 OOF group-resampling uncertainty。

`PACKAGE_MANIFEST.json` 记录每个输入文件的仓库来源与 SHA-256，可用于收包验真。
"""


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


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()


def build_tree(staging: Path) -> tuple[Path, dict[str, Any]]:
    root = staging / PACKAGE_NAME
    root.mkdir(parents=True)
    records = []
    for source, destination_text in sorted(COPY_MAP.items(), key=lambda item: item[1]):
        if not source.is_file():
            raise FileNotFoundError(f"required package source missing: {relative(source)}")
        destination = root / destination_text
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        source_hash = sha256(source)
        copied_hash = sha256(destination)
        if source_hash != copied_hash:
            raise AssertionError(f"copy hash mismatch: {destination_text}")
        records.append({
            "archive_path": f"{PACKAGE_NAME}/{destination_text}",
            "source_path": relative(source),
            "source_sha256": source_hash,
            "copied_sha256": copied_hash,
            "bytes": destination.stat().st_size,
        })

    readme_path = root / "README.md"
    readme_path.write_text(README, encoding="utf-8", newline="\n")
    records.append({
        "archive_path": f"{PACKAGE_NAME}/README.md",
        "source_path": "generated by projects/rehearsal_2024_B/src/s6_figure_package.py",
        "source_sha256": sha256(Path(__file__)),
        "copied_sha256": sha256(readme_path),
        "bytes": readme_path.stat().st_size,
    })
    records.sort(key=lambda row: row["archive_path"])
    data_records = [row for row in records if "/data/" in row["archive_path"]]
    manifest = {
        "status": "PASS",
        "package_role": "S6_VERIFIED_FIGURE_INPUT_HANDOFF",
        "created_at": "2026-09-11T00:00:00+08:00",
        "project": "rehearsal_2024_B",
        "g5_review_commit": G5_REVIEW_COMMIT,
        "build_head_before_packaging": git_head(),
        "build_script": relative(Path(__file__)),
        "build_script_sha256": sha256(Path(__file__)),
        "content_file_count": len(records),
        "content_files": records,
        "figure_input_snapshot_sha256": canonical_sha(data_records),
        "official_test_csv_included": False,
        "official_test_predictions_included": False,
        "model_artifacts_included": False,
        "official_test_csv_numeric_read_count": 0,
        "model_inference_count": 0,
        "formal_figures_generated": False,
    }
    dump(root / "PACKAGE_MANIFEST.json", manifest)
    return root, manifest


def deterministic_zip(source_root: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source_root.rglob("*")):
            if not path.is_file():
                continue
            arcname = path.relative_to(source_root.parent).as_posix()
            info = zipfile.ZipInfo(arcname, date_time=(2026, 9, 11, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def write_s6_manifest(package_manifest: dict[str, Any]) -> None:
    fixed_inputs = {
        "result_registry": VERIFIED / "result_registry.md",
        "figure_handoff": PROJECT / "work" / "handoff" / "figure_handoff.md",
        "writing_handoff": PROJECT / "work" / "handoff" / "writing_handoff.md",
        "result_freeze": PROJECT / "work" / "10_result_freeze.md",
        "post_release_binding_attestation": VERIFIED / "post_release_binding_attestation.json",
        "figure_package_manifest": PACKAGE_DIR / "PACKAGE_MANIFEST.json",
        "figure_handoff_zip": ZIP_PATH,
    }
    records = {
        name: {"path": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size}
        for name, path in fixed_inputs.items()
    }
    dump(S6_MANIFEST, {
        "status": "S6_HANDOFF_READY_G6_NOT_READY",
        "created_at": now(),
        "g5_review_commit": G5_REVIEW_COMMIT,
        "records": records,
        "figure_input_snapshot_sha256": package_manifest["figure_input_snapshot_sha256"],
        "final_figure_data_snapshot": {"status": "PENDING_FIGURE_TEAM_OUTPUT"},
        "paper_source": {"status": "PENDING_WRITING_TEAM_OUTPUT"},
        "final_pdf": {"status": "PENDING_WRITING_TEAM_OUTPUT"},
        "official_test_csv_numeric_read_count": 0,
        "model_inference_count": 0,
        "g6_ready": False,
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replace", action="store_true",
        help="replace only this script's existing package directory and zip",
    )
    args = parser.parse_args()
    PACKAGE_ROOT.mkdir(parents=True, exist_ok=True)
    if PACKAGE_DIR.exists() or ZIP_PATH.exists():
        if not args.replace:
            raise FileExistsError("package already exists; use --replace for this generated target")
        if PACKAGE_DIR.exists():
            shutil.rmtree(PACKAGE_DIR)
        if ZIP_PATH.exists():
            ZIP_PATH.unlink()

    with tempfile.TemporaryDirectory(prefix="2024_B_figure_handoff_") as temporary:
        staged_root, manifest = build_tree(Path(temporary))
        shutil.copytree(staged_root, PACKAGE_DIR)
    deterministic_zip(PACKAGE_DIR, ZIP_PATH)
    write_s6_manifest(manifest)
    print("status=PASS")
    print(f"content_files={manifest['content_file_count']}")
    print(f"figure_input_snapshot_sha256={manifest['figure_input_snapshot_sha256']}")
    print(f"zip_sha256={sha256(ZIP_PATH)}")
    print(f"package={relative(PACKAGE_DIR)}")
    print(f"zip={relative(ZIP_PATH)}")
    print(f"s6_manifest={relative(S6_MANIFEST)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
