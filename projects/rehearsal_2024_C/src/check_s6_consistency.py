"""Read-only S6 consistency checks for the paper technical draft.

The checker never writes to results/verified.  Its only output is a JSON report
under results/raw/s6 so that paper claims remain traceable to frozen evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFIED = PROJECT_ROOT / "results" / "verified"
DEFAULT_PAPER = PROJECT_ROOT / "paper" / "technical_draft.md"
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "raw" / "s6" / "consistency_report.json"


def load_json(relative_path: str) -> Any:
    return json.loads((VERIFIED / relative_path).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def close(actual: float, expected: float, tolerance: float = 1e-12) -> bool:
    return abs(float(actual) - expected) <= tolerance


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    paper_path = args.paper.resolve()
    output_path = args.output.resolve()
    paper = paper_path.read_text(encoding="utf-8")
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": detail})

    g5_review = (PROJECT_ROOT / "reviews" / "gate_5_review.md").read_text(encoding="utf-8")
    record(
        "g5_pass_authorizes_s6",
        "Verdict: **PASS**" in g5_review
        and "Reviewed Commit: `4a14dfd88259c2a5186da1056c3994eccef5e5f7`" in g5_review
        and "S5 -> S6 = AUTHORIZED" in g5_review,
        "reviews/gate_5_review.md",
    )

    verification = load_json("verification_report.json")
    record(
        "s5_verification_pass",
        verification.get("status") == "PASS"
        and verification.get("check_count") == 84
        and verification.get("failed_count") == 0,
        {
            "status": verification.get("status"),
            "check_count": verification.get("check_count"),
            "failed_count": verification.get("failed_count"),
        },
    )

    provenance = load_json("provenance.json")
    hash_failures = []
    for relative_path, metadata in provenance["files"].items():
        verified_path = VERIFIED / relative_path
        source_path = PROJECT_ROOT / metadata["source"]
        actual_verified = sha256(verified_path) if verified_path.is_file() else None
        actual_source = sha256(source_path) if source_path.is_file() else None
        if actual_verified != metadata["verified_sha256"] or actual_source != metadata["source_sha256"]:
            hash_failures.append(
                {
                    "path": relative_path,
                    "verified": actual_verified,
                    "source": actual_source,
                }
            )
    record(
        "verified_provenance_hashes",
        not hash_failures and len(provenance["files"]) == 47,
        {"file_count": len(provenance["files"]), "failures": hash_failures},
    )

    registry = (VERIFIED / "result_registry.md").read_text(encoding="utf-8")
    evidence_ids = re.findall(r"^\|\s*(E\d{3})\s*\|", registry, flags=re.MULTILINE)
    expected_evidence_ids = [f"E{i:03d}" for i in range(1, 16)]
    record("evidence_registry_complete", evidence_ids == expected_evidence_ids, evidence_ids)

    freeze = load_json("model_freeze.json")
    record(
        "frozen_model_identity",
        freeze["freeze_id"] == "S5-FREEZE-2024C-V1"
        and freeze["q1"]["model_sha256"]
        == "1DAEB3B97CA30B28A8E1D6748347B79D2B4DDFF1844969172774C3CC8000810F"
        and freeze["q4"]["model_sha256"]
        == "B284879E38401A301DF02FAF564A4CD482623816E9704DCDADFA8E25DF71AABD",
        {"freeze_id": freeze["freeze_id"], "q1": freeze["q1"]["model_sha256"], "q4": freeze["q4"]["model_sha256"]},
    )

    q2 = load_json("q2/quadratic_temperature_metrics.json")
    q3 = load_json("q3/interaction_metrics.json")
    q4_hgb = load_json("q4/hgb_metrics.json")
    q4_ablation = load_json("q4/ablation_metrics.json")
    q4_stress = load_json("q4/stress_metrics.json")
    q5 = load_json("q5/robustness_metrics.json")
    predictions = load_json("prediction_summary.json")

    numeric_checks = {
        "q2_baseline_rmsle": close(q2["baseline_oof"]["rmsle"], 0.36067816977092043),
        "q2_candidate_rmsle": close(q2["candidate_oof"]["rmsle"], 0.20256740993676708),
        "q2_improvement": close(q2["relative_rmsle_improvement"], 0.4383707501193519),
        "q3_additive_log_rmse": close(q3["additive_oof_log_rmse"], 0.34341644624358847),
        "q3_interaction_log_rmse": close(q3["candidate_oof_log_rmse"], 0.32666736812500924),
        "q4_ridge_rmsle": close(q4_hgb["ridge_oof"]["rmsle"], 0.20009714125176314),
        "q4_full_hgb_rmsle": close(q4_hgb["candidate_oof"]["rmsle"], 0.07639668113886144),
        "q4_final_rmsle": close(q4_ablation["selected_oof_rmsle"], 0.07094149465163511),
        "q4_lomo_max": close(q4_stress["maximum_leave_one_material_rmsle"], 0.3798164456198254),
        "q4_loto_max": close(q4_stress["maximum_leave_one_temperature_rmsle"], 0.5749631862585218),
        "q5_oof_pareto": q5["oof_pareto_count"] == 118,
        "q5_fold_regions": q5["fold_supported_region_count"] == 27,
        "q5_bootstrap_regions": q5["bootstrap"]["stable_region_count"] == 42,
        "q5_jaccard": close(q5["observed_region_jaccard"], 0.3953488372093023),
        "q5_unique_forbidden": q5["unique_recommendation_authorized"] is False,
        "attachment2_rows": predictions["q1"]["row_count"] == 80,
        "attachment3_rows": predictions["q4"]["row_count"] == 400,
        "attachment3_truth_unknown": predictions["q4"]["unknown_ground_truth"] is True,
    }
    record("verified_numeric_claims", all(numeric_checks.values()), numeric_checks)

    required_paper_tokens = [
        "E001",
        "E015",
        "0.360678",
        "0.202567",
        "43.84%",
        "0.343416",
        "0.326667",
        "0.070941",
        "0.37982",
        "0.57496",
        "118",
        "27",
        "42",
        "0.39535",
        "附件二、附件三均无公开真值",
        "调整后关联，不是因果效应",
        "不提供唯一最优工况",
    ]
    missing_tokens = [token for token in required_paper_tokens if token not in paper]
    record("paper_contains_required_claims_and_boundaries", not missing_tokens, missing_tokens)

    direct_overclaims = [
        "附件二分类准确率为100%",
        "附件三测试集RMSLE为0.07094",
        "温度修正对所有温度均更优",
        "获得全局唯一最优工况",
        "可可靠外推至任意新材料和新温度",
    ]
    found_overclaims = [phrase for phrase in direct_overclaims if phrase in paper]
    record("paper_has_no_direct_overclaim", not found_overclaims, found_overclaims)

    # Do not mistake hexadecimal substrings in frozen SHA-256 values for Evidence IDs.
    evidence_mentions = sorted(set(re.findall(r"(?<![A-Z0-9])E\d{3}(?!\d)", paper)))
    record(
        "paper_evidence_ids_valid",
        set(evidence_mentions).issubset(set(expected_evidence_ids)) and evidence_mentions,
        evidence_mentions,
    )

    failed = [check for check in checks if check["status"] != "PASS"]
    report = {
        "stage": "S6",
        "paper": paper_path.relative_to(PROJECT_ROOT).as_posix(),
        "generated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "check_count": len(checks),
        "failed_count": len(failed),
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "scope_note": "PASS covers the technical Markdown draft and frozen evidence only; it does not approve figures, official Word formatting, PDF rendering, naming, or platform submission.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.is_file():
        previous_text = output_path.read_text(encoding="utf-8")
        previous = json.loads(previous_text)
        if previous.get("status") != "PASS":
            failed_path = output_path.with_name("failed_consistency_report_evidence_id_regex.json")
            if not failed_path.exists():
                failed_path.write_text(previous_text, encoding="utf-8")
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"S6_CONSISTENCY_{report['status']}: {report['check_count']} checks, {report['failed_count']} failed")
    print(output_path)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
