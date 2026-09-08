"""Reproducible, read-only S1 audit for rehearsal_2024_B raw CSV files."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / "problem" / "data"
OUTPUT = PROJECT / "results" / "raw" / "s1"

# name: bytes, sha256, rows, columns, role, AP count
EXPECTED_ROWS = [
    ("test_set_1_2ap.csv", 229577, "A797C24918C7549AE2BE2A5B13D1059B4803C944BF17D41E314C2DD9D72223B2", 80, 47, "test_q1_q3", 2),
    ("test_set_1_3ap.csv", 3486596, "774B0E8FFCA2CED5B2849DA4719D2D9A7E0CF969753C8740F2FB1E36511F12B3", 105, 57, "test_q1_q3", 3),
    ("test_set_2_2ap.csv", 1265585, "1020D75AB0EA6369E243B87100A2B2E6BFDCFCC2C5E7BCCAC356FD07F099925B", 64, 46, "test_q2", 2),
    ("test_set_2_3ap.csv", 2795529, "8312A393D3957BE1AF2BD333BBB3158F2FA5753378CEC1B81A151E7F21CFAB67", 87, 56, "test_q2", 3),
    ("training_set_2ap_loc0_nav82.csv", 245805, "9F255CA192FDF1F99CC441E6321DA0EF7D4D1B2FFE9B58870533B74AE34D068E", 82, 43, "train", 2),
    ("training_set_2ap_loc0_nav86.csv", 378917, "4FB41351844354FC92483496B1CAAC9F95BA1E93E0C1276DE8232AB429250321", 80, 43, "train", 2),
    ("training_set_2ap_loc1_nav82.csv", 409486, "7F2E41CFACDE6BECFD0BF6E5F66DE9E39EB5FF1199FF664A1180882E9FA404B4", 78, 43, "train", 2),
    ("training_set_2ap_loc1_nav86.csv", 352700, "07831A66D218EF6BB23D2504CE2CC382104F9E48CDCC716A37D30D412B99D8AD", 74, 43, "train", 2),
    ("training_set_2ap_loc2_nav82.csv", 345269, "3C9F76FC140D6DDF900F515D16FBABEDE182152DBC09919CE29CA0103624A08F", 80, 43, "train", 2),
    ("training_set_3ap_loc30_nav82.csv", 828587, "A539D3C29A80DA3CA002B6A9C0E49B7D7BC501A17C965192309C0229E2A0035B", 123, 55, "train", 3),
    ("training_set_3ap_loc30_nav86.csv", 761332, "8DA8932B49FDFEA4E5521B045F0D407F74721E7401CC4156EA8AA6B5BE8FBCC8", 120, 55, "train", 3),
    ("training_set_3ap_loc31_nav82.csv", 912194, "ADCD55978E14288539FE239AEBF7292D1AD961CD82813B4493E00934CCCB6FFB", 126, 53, "train", 3),
    ("training_set_3ap_loc31_nav86.csv", 783574, "1E44346B859058B9E7B0C59026E9E06F9F44CE093952ACE88F787807644A44EC", 108, 53, "train", 3),
    ("training_set_3ap_loc32_nav82.csv", 3691461, "B07ABD7E401090F5B6667A61708FDE75D48FF0BD0158AB9E4D31565CBC369112", 111, 53, "train", 3),
    ("training_set_3ap_loc32_nav86.csv", 2023495, "EF0C5478D00BEB47C04332A84569CD54F34CA2A047A722E97F27CB8E47B716DA", 60, 53, "train", 3),
    ("training_set_3ap_loc33_nav82.csv", 2720436, "BEAB6D49A62A089F5A0996C572E98DA3D50560B0F9F1F7D12284BF41353C1D26", 111, 53, "train", 3),
    ("training_set_3ap_loc33_nav88.csv", 3251013, "4DCE45EC10ED08DB154C979CD122CEAFC428E0B772D1A33E2D2AC6E1D3B9174E", 99, 53, "train", 3),
]
EXPECTED = {
    row[0]: dict(zip(("bytes", "sha256", "rows", "cols", "role", "ap_count"), row[1:]))
    for row in EXPECTED_ROWS
}

IDENTIFIERS = ["test_id", "loc_id", "bss_id", "ap_name", "ap_mac", "ap_id", "sta_mac", "sta_id"]
CONFIG = ["test_dur", "protocol", "pkt_len", "pd", "ed", "nav", "eirp"]
POST_EVENT = ["nss", "mcs", "per", "num_ampdu", "ppdu_dur", "other_air_time", "seq_time", "throughput"]
PREDICTION = ["predict nss", "predict mcs", "predict seq_time", "predict throughput", "error%", "error%.1"]
NUMERIC = ["test_dur", "pkt_len", "pd", "ed", "nav", "eirp", *POST_EVENT]
UNITS = {
    "test_id": "dimensionless group identifier",
    "test_dur": "s (statement appendix)",
    "loc_id": "scenario identifier",
    "protocol": "categorical tcp/udp",
    "pkt_len": "byte",
    "bss_id": "dimensionless BSS identifier",
    "ap_name": "device model/category",
    "ap_mac": "identifier only",
    "ap_id": "AP identifier within test_id",
    "pd": "dBm threshold",
    "ed": "dBm threshold",
    "nav": "dBm supplied scenario threshold",
    "eirp": "dBm",
    "*_rssi": "dBm samples encoded as numeric list or scalar",
    "sta_mac": "identifier only",
    "sta_id": "station identifier within test_id",
    "nss": "spatial-stream class/count; zero is sentinel-risk",
    "mcs": "dimensionless MCS index",
    "per": "ratio [0,1]",
    "num_ampdu": "count; CSV name differs from statement num_ppdu",
    "ppdu_dur": "s",
    "other_air_time": "s",
    "seq_time": "s",
    "throughput": "Mbps",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def native(value: Any) -> Any:
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def now() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")


def git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=PROJECT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def verify() -> dict[str, Any]:
    actual = sorted(path.name for path in DATA.glob("*.csv"))
    missing = sorted(set(EXPECTED) - set(actual))
    extra = sorted(set(actual) - set(EXPECTED))
    failures = ([f"missing files: {missing}"] if missing else []) + ([f"unexpected CSV files: {extra}"] if extra else [])
    files = []
    for name, spec in sorted(EXPECTED.items()):
        path = DATA / name
        exists = path.is_file()
        size = path.stat().st_size if exists else None
        digest = sha256(path) if exists else None
        if not exists or size != spec["bytes"] or digest != spec["sha256"]:
            failures.append(f"{name}: missing or size/hash mismatch")
        files.append({
            "file": name, "exists": exists, "bytes": size, "expected_bytes": spec["bytes"],
            "size_ok": size == spec["bytes"], "sha256": digest,
            "expected_sha256": spec["sha256"], "hash_ok": digest == spec["sha256"],
        })
    return {
        "status": "PASS" if not failures else "FAIL",
        "expected_count": len(EXPECTED), "actual_count": len(actual),
        "missing": missing, "extra": extra, "failures": failures, "files": files,
    }


def num_summary(series: pd.Series) -> dict[str, Any]:
    values = pd.to_numeric(series, errors="coerce")
    finite = values[np.isfinite(values)]
    if finite.empty:
        return {"count": 0, "coercion_failures": int(series.notna().sum())}
    q = finite.quantile([0, .25, .5, .75, 1])
    return {
        "count": int(finite.count()), "mean": float(finite.mean()),
        "std": float(finite.std()) if finite.count() > 1 else 0.0,
        "min": float(q.loc[0]), "q25": float(q.loc[.25]), "median": float(q.loc[.5]),
        "q75": float(q.loc[.75]), "max": float(q.loc[1]),
        "coercion_failures": int(series.notna().sum() - finite.count()),
    }


def parse_rssi(value: Any) -> tuple[str, list[float]]:
    if pd.isna(value):
        return "missing", []
    if isinstance(value, (int, float, np.integer, np.floating)):
        number = float(value)
        return ("scalar", [number]) if math.isfinite(number) else ("invalid", [])
    text = str(value).strip()
    try:
        number = float(text)
        return ("scalar", [number]) if math.isfinite(number) else ("invalid", [])
    except ValueError:
        pass
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)
            if not isinstance(parsed, (list, tuple)) or not parsed:
                return "invalid", []
            values = [float(item) for item in parsed]
            return ("list", values) if all(math.isfinite(item) for item in values) else ("invalid", [])
        except (ValueError, SyntaxError, TypeError):
            pass
    return "invalid", []


def rssi_audit(frames: dict[str, pd.DataFrame]) -> dict[str, Any]:
    formats: Counter[str] = Counter()
    invalid, out_of_range, lengths, all_values = [], [], Counter(), []
    for name, frame in frames.items():
        for column in (col for col in frame.columns if "rssi" in col.lower()):
            for index, raw in frame[column].items():
                kind, values = parse_rssi(raw)
                formats[kind] += 1
                if kind == "list":
                    lengths[len(values)] += 1
                base = {
                    "file": name, "row_index_zero_based": int(index),
                    "test_id": native(frame.at[index, "test_id"]),
                    "ap_id": native(frame.at[index, "ap_id"]), "column": column,
                }
                if kind == "invalid" and len(invalid) < 100:
                    invalid.append({**base, "raw": str(raw)})
                for value in values:
                    all_values.append(value)
                    if not -120 <= value <= 0 and len(out_of_range) < 100:
                        out_of_range.append({**base, "value": value})
    return {
        "accepted_encodings": ["finite numeric scalar", "non-empty list of finite numerics"],
        "plausibility_range_used_for_flagging_only": [-120.0, 0.0],
        "format_counts": dict(sorted(formats.items())),
        "observed_value_min": min(all_values) if all_values else None,
        "observed_value_max": max(all_values) if all_values else None,
        "list_length_counts": {str(k): v for k, v in sorted(lengths.items())},
        "invalid_cell_count": formats["invalid"], "invalid_examples": invalid,
        "range_violation_count": len(out_of_range), "range_violation_examples": out_of_range,
    }


def profile_file(name: str, frame: pd.DataFrame) -> dict[str, Any]:
    spec = EXPECTED[name]
    sizes = frame.groupby("test_id", dropna=False).size()
    bad = [{"test_id": native(key), "rows": int(size)} for key, size in sizes.items() if size != spec["ap_count"]]
    return {
        "file": name, "role": spec["role"], "ap_count": spec["ap_count"],
        "rows": int(len(frame)), "columns_count": int(frame.shape[1]),
        "expected_rows": spec["rows"], "expected_columns_count": spec["cols"],
        "shape_ok": frame.shape == (spec["rows"], spec["cols"]),
        "test_id_count": int(frame.test_id.nunique(dropna=False)),
        "group_size_counts": {str(int(k)): int(v) for k, v in sizes.value_counts().sort_index().items()},
        "bad_group_count": len(bad), "bad_groups": bad,
        "exact_duplicate_rows": int(frame.duplicated().sum()),
        "columns": list(frame.columns),
        "dtypes": {col: str(dtype) for col, dtype in frame.dtypes.items()},
        "missing_counts": {col: int(v) for col, v in frame.isna().sum().items() if v},
        "all_null_columns": [col for col in frame if frame[col].isna().all()],
        "numeric_summary": {col: num_summary(frame[col]) for col in NUMERIC if col in frame},
    }


def training_frames(frames: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.concat(
        [frame.assign(source_file=name) for name, frame in frames.items() if EXPECTED[name]["role"] == "train"],
        ignore_index=True, sort=False,
    )
    a01 = raw.source_file.eq("training_set_2ap_loc2_nav82.csv") & raw.test_id.isin([40, 41])
    return raw, raw.loc[~a01].copy()


def counts(series: pd.Series) -> dict[str, int]:
    return {str(native(key)): int(value) for key, value in series.value_counts(dropna=False).items()}


def boundary(frames: dict[str, pd.DataFrame]) -> dict[str, Any]:
    output = {}
    for name, frame in sorted(frames.items()):
        role = EXPECTED[name]["role"]
        if not role.startswith("test"):
            continue
        fields = [col for col in POST_EVENT + PREDICTION if col in frame]
        output[name] = {
            "role": role, "rows": len(frame),
            "non_null_counts": {col: int(frame[col].notna().sum()) for col in fields},
            "contract": (
                "nss/mcs/per supplied; seq_time/throughput and prediction/error fields blank"
                if role == "test_q1_q3" else
                "nss/mcs and all post-event/output fields blank"
            ),
        }
    return output


def profile(frames: dict[str, pd.DataFrame]) -> dict[str, Any]:
    raw, eligible = training_frames(frames)
    union = sorted({col for frame in frames.values() for col in frame})
    pair = eligible[["nss", "mcs"]].astype("string").agg("|".join, axis=1)
    return {
        "metadata": {
            "generated_at": now(), "project": "rehearsal_2024_B", "stage": "S1",
            "script": "src/s1_data_audit.py", "python": platform.python_version(),
            "pandas": pd.__version__, "numpy": np.__version__, "platform": platform.platform(),
            "git_head": git("rev-parse", "HEAD"),
            "git_status_porcelain_before_outputs": git("status", "--porcelain"),
        },
        "scope": {
            "training_file_count": 13, "test_file_count": 4,
            "training_rows_raw": len(raw), "training_rows_eligible_after_A01": len(eligible),
            "test_rows": sum(len(frame) for name, frame in frames.items() if EXPECTED[name]["role"].startswith("test")),
            "test_content_use": "structure and missingness only; no distribution-driven tuning",
        },
        "files": [profile_file(name, frames[name]) for name in sorted(frames)],
        "schema": {
            "union_columns": union,
            "column_file_coverage": {col: sorted(name for name, frame in frames.items() if col in frame) for col in union},
            "identifier_columns": IDENTIFIERS, "configuration_columns": CONFIG,
            "rssi_columns_rule": "column name contains rssi",
            "post_event_columns": POST_EVENT,
            "prediction_placeholder_columns": PREDICTION,
            "units_and_semantics": UNITS,
        },
        "eligible_training_distributions": {
            **{col: counts(eligible[col]) for col in ["protocol", "loc_id", "nav", "nss", "mcs"]},
            "nss_mcs_pair": counts(pair),
        },
        "eligible_training_numeric_summary": {col: num_summary(eligible[col]) for col in NUMERIC if col in eligible},
    }


def quality(frames: dict[str, pd.DataFrame], before: dict[str, Any]) -> dict[str, Any]:
    raw, eligible = training_frames(frames)
    corrupt = (
        raw.source_file.eq("training_set_2ap_loc2_nav82.csv")
        & raw.test_id.isin([40, 41]) & raw.ap_id.eq("ap_1")
    )
    isolate = raw.source_file.eq("training_set_2ap_loc2_nav82.csv") & raw.test_id.isin([40, 41])
    zero = raw.loc[pd.to_numeric(raw.nss, errors="coerce").eq(0)]
    a02 = frames["training_set_3ap_loc30_nav86.csv"]
    a02_cols = [col for col in a02 if col.startswith("ap_from_ap_0_") and a02[col].isna().all()]
    eligible_bad = []
    for (name, test_id), size in eligible.groupby(["source_file", "test_id"], dropna=False).size().items():
        if size != EXPECTED[name]["ap_count"]:
            eligible_bad.append({"file": name, "test_id": native(test_id), "rows": int(size)})
    per = pd.to_numeric(raw.per, errors="coerce")
    anomalies = [
        {
            "id": "A01", "severity": "WARN",
            "title": "two shifted rows in training_set_2ap_loc2_nav82.csv",
            "detected_corrupt_rows": int(corrupt.sum()),
            "row_keys": [
                {"source_file": row.source_file, "row_index_zero_based": int(index),
                 "test_id": native(row.test_id), "ap_id": native(row.ap_id)}
                for index, row in raw.loc[corrupt].iterrows()
            ],
            "isolated_group_count": 2, "isolated_row_count": int(isolate.sum()),
            "frozen_handling": "Do not edit source; isolate both complete test_id 40/41 groups (4 rows) from training and model selection, because retaining only ap_0 breaks the AP-group unit.",
        },
        {
            "id": "A02", "severity": "WARN",
            "title": "three AP0 RSSI columns entirely missing in one source file",
            "file": "training_set_3ap_loc30_nav86.csv", "columns": a02_cols,
            "missing_rows_per_column": {col: int(a02[col].isna().sum()) for col in a02_cols},
            "frozen_handling": "Preserve missingness; never synthesize reverse links. At S2 use availability indicators plus a missing-aware preprocessor/model, or omit only unavailable directions.",
        },
        {
            "id": "A03", "severity": "WARN",
            "title": "three internally consistent (NSS,MCS)=(0,0) observations",
            "row_count": len(zero),
            "rows": [
                {"source_file": row.source_file, "test_id": native(row.test_id), "ap_id": native(row.ap_id),
                 "nss": native(row.nss), "mcs": native(row.mcs), "per": native(row.per),
                 "seq_time": native(row.seq_time), "throughput": native(row.throughput)}
                for _, row in zero.iterrows()
            ],
            "frozen_handling": "Retain unchanged as sentinel-risk; do not coerce to NSS=1. S2 must report sensitivity with and without these rows before freezing the Q2 label policy.",
        },
        {
            "id": "A04", "severity": "WARN",
            "title": "schema aliases and empty prediction placeholders differ across files",
            "details": {
                "training_files_with_empty_predict_columns": ["training_set_3ap_loc30_nav82.csv", "training_set_3ap_loc30_nav86.csv"],
                "test_set_1_duplicate_error_header_parsed_as": ["error%", "error%.1"],
                "statement_csv_alias": {"statement": "num_ppdu", "csv": "num_ampdu"},
            },
            "frozen_handling": "Normalize aliases only in derived data; exclude every predict/error placeholder from features; retain original headers in source files.",
        },
    ]
    return {
        "audit_status": "PASS_WITH_WARNINGS", "critical_failures": [],
        "input_verification_before": before,
        "training_rows_raw": len(raw),
        "training_rows_eligible_after_A01_group_isolation": len(eligible),
        "A01_isolated_rows": int(isolate.sum()),
        "eligible_training_bad_group_count": len(eligible_bad),
        "eligible_training_bad_groups": eligible_bad,
        "training_exact_duplicate_rows": int(raw.duplicated().sum()),
        "per_outside_0_1_count": int((per.notna() & ~per.between(0, 1)).sum()),
        "rssi_audit": rssi_audit(frames), "anomalies": anomalies,
        "test_boundary": boundary(frames),
        "feature_contracts": {
            "shared_keys_not_raw_features": IDENTIFIERS,
            "q1": {
                "target": "seq_time", "allowed_base_families": CONFIG + ["RSSI-derived summaries"],
                "forbidden": POST_EVENT + PREDICTION,
            },
            "q2": {
                "targets": ["nss", "mcs"], "allowed_base_families": CONFIG + ["RSSI-derived summaries"],
                "conditionally_allowed": ["out-of-fold Q1 seq_time predictions during training", "Q1 predictions at inference"],
                "forbidden": ["true nss/mcs or derivatives", "per", "num_ampdu", "ppdu_dur", "other_air_time", "true seq_time", "throughput", *PREDICTION],
            },
            "q3": {
                "target": "throughput", "allowed_base_families": CONFIG + ["RSSI-derived summaries"],
                "explicitly_allowed_by_statement": ["actual nss", "actual mcs", "Q1-predicted seq_time or out-of-fold equivalent"],
                "forbidden": ["per", "num_ampdu", "ppdu_dur", "other_air_time", "true seq_time", "throughput", *PREDICTION],
                "boundary_note": "Q3 permission for actual MCS/NSS is not generalized to PER or other post-event fields.",
            },
        },
        "validation_contract": {
            "atomic_group": ["source_file", "test_id"], "rule": "Every AP row for a test remains in one fold.",
            "primary_candidate": "GroupKFold or repeated grouped holdout; fit preprocessing inside each training fold.",
            "scenario_stress_tests": ["leave-one-source-file-out", "leave-one-loc_id-out where feasible", "report by ap_count/loc_id/nav/protocol"],
            "stacking_rule": "Any Q1 prediction used to train Q2/Q3 must be out-of-fold; in-sample upstream predictions are forbidden.",
            "sealed_test_rule": "Official tests are final inference/export only; their feature distributions and blank targets cannot drive feature, rule, hyperparameter, or model selection.",
        },
        "external_data_contract": {
            "required": False, "current_use": "None",
            "policy": "Later external data/artifacts require provenance, license, version/hash, download date, and a no-external-data ablation.",
        },
    }


def summary_md(p: dict[str, Any], q: dict[str, Any]) -> str:
    lines = [
        "# S1 Data Audit Summary", "",
        f"- Generated: {p['metadata']['generated_at']}",
        f"- Git HEAD before outputs: {p['metadata']['git_head']}",
        f"- Verdict: {q['audit_status']}",
        f"- Input verification before/after: {q['input_verification_before']['status']} / {q['input_verification_after']['status']}",
        f"- Raw/eligible training rows: {q['training_rows_raw']} / {q['training_rows_eligible_after_A01_group_isolation']}",
        f"- Structurally audited test rows: {p['scope']['test_rows']}",
        f"- Training duplicate rows: {q['training_exact_duplicate_rows']}",
        f"- Eligible incomplete AP groups: {q['eligible_training_bad_group_count']}", "",
        "## Frozen anomaly handling", "",
    ]
    for anomaly in q["anomalies"]:
        lines += [f"- {anomaly['id']} [{anomaly['severity']}]: {anomaly['title']}.", f"  Handling: {anomaly['frozen_handling']}"]
    lines += [
        "", "## Leakage and validation boundary", "",
        "- Atomic split unit: source_file + test_id; AP rows never cross folds.",
        "- Official test sets remain sealed for final inference/export.",
        "- Q1 excludes every post-event statistic and output.",
        "- Q2 permits only leakage-safe out-of-fold Q1 predictions, never true labels.",
        "- Q3 may use actual MCS/NSS as explicitly permitted, but not PER or other post-event fields.", "",
        "## Machine-readable evidence", "",
        "- data_profile.json: file schemas, missingness, numeric summaries and training-only distributions.",
        "- quality_checks.json: hashes, anomalies, RSSI parsing, test boundary and leakage contracts.", "",
    ]
    return "\n".join(lines)


def dump(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true", help="verify inventory, sizes and hashes; write nothing")
    args = parser.parse_args()
    before = verify()
    print(f"input_verification={before['status']}")
    print(f"expected_csv={before['expected_count']} actual_csv={before['actual_count']}")
    if before["status"] != "PASS":
        for failure in before["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 2
    if args.verify_only:
        return 0

    frames, failures = {}, []
    for name, spec in sorted(EXPECTED.items()):
        try:
            frame = pd.read_csv(DATA / name, low_memory=False)
            if frame.shape != (spec["rows"], spec["cols"]):
                failures.append(f"{name}: expected {(spec['rows'], spec['cols'])}, got {frame.shape}")
            frames[name] = frame
        except Exception as exc:
            failures.append(f"{name}: {type(exc).__name__}: {exc}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 3

    p = profile(frames)
    q = quality(frames, before)
    after = verify()
    q["input_verification_after"] = after
    q["input_hashes_unchanged_during_audit"] = (
        before["status"] == after["status"] == "PASS"
        and [item["sha256"] for item in before["files"]] == [item["sha256"] for item in after["files"]]
    )
    if not q["input_hashes_unchanged_during_audit"]:
        print("FAIL: input hashes changed during audit", file=sys.stderr)
        return 4

    OUTPUT.mkdir(parents=True, exist_ok=True)
    dump(OUTPUT / "data_profile.json", p)
    dump(OUTPUT / "quality_checks.json", q)
    (OUTPUT / "audit_summary.md").write_text(summary_md(p, q), encoding="utf-8")
    print(f"audit_status={q['audit_status']}")
    print(f"raw_training_rows={q['training_rows_raw']}")
    print(f"eligible_training_rows={q['training_rows_eligible_after_A01_group_isolation']}")
    print(f"test_rows={p['scope']['test_rows']}")
    print(f"output_dir={OUTPUT.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
