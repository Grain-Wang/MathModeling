"""Build eight non-rendered, evidence-bound paper figure resources.

No raw CSV, official-test prediction, model fit, or inference is used.  The
only raw result reads are existing G1/S3/G4 audited artifacts whose byte
identities are independently checked before migration to verified/.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
VERIFIED = PROJECT / "results" / "verified"
FIGURE_DATA = VERIFIED / "figure_data"
BASE = PROJECT / "results" / "raw" / "baseline"
MAIN = PROJECT / "results" / "raw" / "main"
S1 = PROJECT / "results" / "raw" / "s1"
G1_REVIEWED = "9f0a209f55351aff306aa7ecd6d38486fcf43352"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def require(ok: bool, explanation: str) -> None:
    if not ok:
        raise AssertionError(explanation)


def git_blob(revision: str, path: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{revision}:{repo_path(path)}"],
        cwd=REPO, text=True,
    ).strip()


def tracked_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path)], cwd=REPO, text=True
    ).strip()


def gz_rows(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def source(path: Path) -> dict[str, Any]:
    return {"path": repo_path(path), "sha256": sha256(path), "bytes": path.stat().st_size}


def fig(
    number: int, slug: str, title: str, kind: str, evidence: list[str],
    sources: list[Path], data: Any, caption_rule: str, requirements: list[str],
) -> tuple[str, dict[str, Any]]:
    filename = f"fig{number:02d}_{slug}.json"
    return filename, {
        "figure_number": number,
        "filename_stem": filename.removesuffix(".json"),
        "title": title,
        "kind": kind,
        "status": "RESOURCE_READY_NOT_RENDERED",
        "evidence_ids": evidence,
        "sources": [source(path) for path in sources],
        "data": data,
        "caption_rule": caption_rule,
        "requirements": requirements,
        "output_contract": {
            "source": "editable source for diagrams; generation script for numeric plots",
            "exports": ["PDF", "SVG", "PNG"],
            "numeric_plotting_skill_or_diagram_skill": "confirm with project owner before drawing",
        },
    }


def check_upstream() -> dict[str, Any]:
    freeze_path = VERIFIED / "freeze_manifest.json"
    freeze = load(freeze_path)
    sidecar = (VERIFIED / "freeze_manifest.sha256").read_text(encoding="ascii").split()[0].upper()
    require(sha256(freeze_path) == sidecar, "freeze sidecar mismatch")
    require(freeze["selection_closed"] is True, "selection is not closed")
    for frozen_source in freeze["source_files"]:
        path = REPO / frozen_source["path"]
        require(sha256(path) == frozen_source["sha256"],
                f"frozen source drift: {frozen_source['path']}")

    s1_quality = S1 / "quality_checks.json"
    require(tracked_blob(s1_quality) == git_blob(G1_REVIEWED, s1_quality),
            "G1-reviewed S1 quality audit drift")
    g1_text = (PROJECT / "reviews" / "gate_1_review_r2.md").read_text(encoding="utf-8")
    require("Verdict: **PASS**" in g1_text and G1_REVIEWED in g1_text,
            "G1 R2 PASS review not found")

    baseline_run = load(BASE / "run_manifest.json")
    baseline_records = {item["path"]: item for item in baseline_run["output_artifacts"]}
    importance = BASE / "q1_feature_family_importance.json"
    record = baseline_records[repo_path(importance)]
    require(sha256(importance) == record["sha256"] and importance.stat().st_size == record["bytes"],
            "Q1 importance drift from S3 run manifest")
    require(load(BASE / "post_run_validation.json")["status"] == "PASS",
            "S3 validation not PASS")

    validation = MAIN / "validation_manifest.json"
    require(sha256(validation) == freeze["prior_validation"]["g4_validated_artifact_manifest_sha256"],
            "G4 artifact validation manifest drift")
    consumed = {item["path"]: item for item in load(validation)["consumed_artifacts"]}
    for name in ("q3_ap_oof_predictions.jsonl.gz", "q3_system_oof_predictions.jsonl.gz"):
        path = MAIN / name
        require(repo_path(path) in consumed and sha256(path) == consumed[repo_path(path)]["sha256"],
                f"G4-validated OOF drift: {name}")
    require(load(MAIN / "post_run_validation.json")["status"] == "PASS",
            "S4 validation not PASS")

    old_manifest = load(VERIFIED / "artifact_manifest.json")
    old_records = {item["path"]: item for item in old_manifest["artifacts"]}
    for name in (
        "q1_metrics.json", "q2_baseline_metrics.json", "q2_candidate_metrics.json",
        "q3_baseline_metrics.json", "q3_candidate_metrics.json",
        "group_bootstrap_intervals.json", "stratified_metrics.json",
        "verified_metrics.json", "selection_reconstruction.json", "freeze_manifest.json",
    ):
        path = VERIFIED / name
        require(repo_path(path) in old_records and sha256(path) == old_records[repo_path(path)]["sha256"],
                f"previously verified artifact drift: {name}")
    return freeze


def main() -> int:
    freeze = check_upstream()
    quality_path = S1 / "quality_checks.json"
    importance_raw = BASE / "q1_feature_family_importance.json"
    importance_verified = VERIFIED / "q1_feature_family_importance.json"
    if importance_verified.exists():
        require(sha256(importance_verified) == sha256(importance_raw),
                "verified Q1 importance conflicts with audited source")
    else:
        shutil.copyfile(importance_raw, importance_verified)
    quality = load(quality_path)
    importance = load(importance_verified)
    q1 = load(VERIFIED / "q1_metrics.json")["models"]["Q1-B1"]
    q2_base = load(VERIFIED / "q2_baseline_metrics.json")
    q2_cand = load(VERIFIED / "q2_candidate_metrics.json")
    q3_base = load(VERIFIED / "q3_baseline_metrics.json")
    q3_cand = load(VERIFIED / "q3_candidate_metrics.json")
    bootstrap = load(VERIFIED / "group_bootstrap_intervals.json")
    verified_claims = load(VERIFIED / "verified_metrics.json")["claims"]
    q3_unified = q3_cand["models"]["Q3-M1-HGB-UNIFIED"]
    q3_apcount = q3_cand["models"]["Q3-M1-HGB-APCOUNT"]
    q3_b1 = q3_base["models"]["Q3-B1"]

    ap_rows = [row for row in gz_rows(MAIN / "q3_ap_oof_predictions.jsonl.gz")
               if row["scope"] == "PRIMARY" and row["repeat"] == 0
               and row["model_id"] == "Q3-M1-HGB-UNIFIED"]
    system_rows = [row for row in gz_rows(MAIN / "q3_system_oof_predictions.jsonl.gz")
                   if row["scope"] == "PRIMARY" and row["repeat"] == 0
                   and row["model_id"] == "Q3-M1-HGB-UNIFIED"]
    require(len(ap_rows) == 1250 and len(system_rows) == 482, "Q3 primary repeat-0 coverage mismatch")
    require(len({row["row_key"] for row in ap_rows}) == 1250, "Q3 AP row keys not unique")
    require(len({row["group_id"] for row in system_rows}) == 482, "Q3 system keys not unique")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in ap_rows:
        grouped[row["group_id"]].append(row)
    for row in system_rows:
        components = grouped[row["group_id"]]
        require(set(row["component_row_keys"]) == {item["row_key"] for item in components},
                "Q3 AP-to-system component set mismatch")
        require(len(components) == row["ap_count"], "Q3 system AP count mismatch")
        require(math.isclose(math.fsum(item["throughput_bounded"] for item in components),
                             row["system_throughput_bounded"], abs_tol=1e-9),
                "Q3 AP-to-system prediction sum mismatch")
    require(math.isclose(
        sum(abs(row["throughput_bounded"] - row["truth_throughput"]) for row in ap_rows) / 1250,
        q3_unified["primary_repeat_metrics"][0]["bounded"]["per_ap"]["mae"],
        rel_tol=0, abs_tol=1e-9,
    ), "Q3 AP repeat-0 MAE mismatch")

    labels = freeze["q2_label_order"]
    matrices = q2_base["models"]["Q2-B1A"]["primary_confusion_matrices"]
    require(len(matrices) == 3 and [row["repeat"] for row in matrices] == [0, 1, 2],
            "Q2 confusion repeat identity mismatch")
    require(all(row["labels"] == labels and len(row["matrix"]) == 17
                and all(len(line) == 17 for line in row["matrix"])
                and sum(map(sum, row["matrix"])) == 1250 for row in matrices),
            "Q2 fixed-17 confusion matrix mismatch")

    specs = []
    specs.append(fig(1, "overall_workflow", "WLAN 三问总体技术路线", "editable_diagram",
        ["E-FREEZE-001", "E-Q3-CONFIG-001"], [VERIFIED / "freeze_manifest.json"],
        {"nodes": [
            {"id": "input", "label": "13 个训练文件；4 个官方测试文件封存"},
            {"id": "audit", "label": f"S1 严格身份 / A01 整组隔离：{quality['training_rows_eligible_after_A01_group_isolation']} AP / {quality['eligible_training_strict_complete_group_count']} 组"},
            {"id": "feature", "label": "共享机制与 RSSI 特征，折内拟合预处理"},
            {"id": "split", "label": "按 source_file + test_id 分组；primary 3×5 + 13 LOSO"},
            {"id": "q1", "label": "Q1-B1 Ridge → bounded 时长"},
            {"id": "q2", "label": "Q2-B1A Logistic → 固定 17 类概率"},
            {"id": "q3", "label": "Q3 物理基准 + 残差 HGB → 非负 AP 吞吐"},
            {"id": "sum", "label": "同组 bounded AP 严格求和 → 系统吞吐"},
            {"id": "release", "label": "G4 冻结后唯一 S5 release；无标签，不评性能"},
        ], "edges": [
            ["input", "audit"], ["audit", "feature"], ["feature", "split"],
            ["split", "q1"], ["split", "q2"], ["split", "q3"],
            ["q1", "q3"], ["q3", "sum"], ["q1", "release"],
            ["q2", "release"], ["sum", "release"],
        ], "edge_note": "Q1→Q3 的训练侧连接仅使用注册的 Q1 OOF；Q2 不使用 Q1。"},
        "方法路线示意图，不代表因果发现；测试集仅在冻结后作一次无标签部署推理。",
        ["所有箭头必须对应真实数据依赖", "以可编辑矢量源文件交付", "不得把测试集连到模型选择"] ))

    specs.append(fig(2, "data_quality", "数据质量与处理边界", "numeric_panels",
        ["E-DATA-001"], [quality_path],
        {"raw_training_ap_rows": quality["training_rows_raw"],
         "eligible_training_ap_rows": quality["training_rows_eligible_after_A01_group_isolation"],
         "isolated_A01_rows": quality["A01_isolated_rows"],
         "eligible_complete_groups": quality["eligible_training_strict_complete_group_count"],
         "within_file_exact_duplicate_rows": quality["within_file_training_exact_duplicate_row_count"],
         "cross_file_duplicate_row_fingerprints": quality["cross_file_duplicate_row_fingerprint_count"],
         "cross_file_duplicate_group_fingerprints": quality["cross_file_duplicate_group_fingerprint_count"],
         "A02_missing_RSSI_columns_rows_each": next(item for item in quality["anomalies"] if item["id"] == "A02")["missing_rows_per_column"],
         "A03_retained_joint_0_0_rows": next(item for item in quality["anomalies"] if item["id"] == "A03")["row_count"],
         "A05_other_air_time_exceeds_test_dur": quality["other_air_time_over_test_dur_count"],
         "A06_filename_content_mismatch_files": quality["filename_content_scenario_mismatch_count"]},
        "训练侧数据审计；A01 隔离 2 行，其他异常按冻结规则保留或置无效，不表示全部异常均被删除。",
        ["原始与 eligible 规模同轴展示", "明确 A01 是整组隔离", "不绘制官方测试数值分布"] ))

    specs.append(fig(3, "q3_structure", "Q3 物理残差与 AP→系统结构", "editable_diagram",
        ["E-Q3-CONFIG-001", "E-FREEZE-001"],
        [VERIFIED / "freeze_manifest.json", PROJECT / "src" / "s5_release.py"],
        {"configuration_id": freeze["models"]["q3"]["configuration_id"],
         "model_id": freeze["models"]["q3"]["model_id"],
         "nodes": [
             {"id": "q1", "label": "Q1-B1 bounded seq_time"},
             {"id": "phy", "label": "PHY rate(MCS,NSS)"},
             {"id": "proxy", "label": "physical proxy = bounded seq_time / test_dur × PHY rate"},
             {"id": "eta", "label": "训练侧最小二乘 η ∈ [0,1]"},
             {"id": "fallback", "label": "PHY 缺失 → Q3-B1 fallback"},
             {"id": "base", "label": "physical base"},
             {"id": "hgb", "label": "统一残差 HGB C3"},
             {"id": "ap", "label": "max(0, base + residual) → AP Mbps"},
             {"id": "system", "label": "Σ 同组 bounded AP → system Mbps"},
         ], "edges": [["q1", "proxy"], ["phy", "proxy"], ["proxy", "base"],
                     ["eta", "base"], ["fallback", "base"], ["base", "ap"],
                     ["hgb", "ap"], ["ap", "system"]],
         "frozen_parameters": freeze["models"]["q3"]["parameters"]},
        "Q3 部署配置结构图；C3 是全量部署配置，不应把 nested pipeline OOF 分数标成 C3 固定分数。",
        ["fallback 只在物理 rate 不可用时启用", "AP 非负后再求和", "所有形状和箭头可编辑"] ))

    system_points = [{"group_id": r["group_id"], "source_file": r["source_file"],
                      "ap_count": r["ap_count"], "truth_mbps": r["truth_system_throughput"],
                      "prediction_mbps": r["system_throughput_bounded"]} for r in system_rows]
    specs.append(fig(4, "q3_core_result", "Q3 系统吞吐核心验证结果", "numeric_scatter",
        ["E-Q3-OOF-001", "E-Q3-PIPE-001"],
        [MAIN / "q3_system_oof_predictions.jsonl.gz", VERIFIED / "q3_candidate_metrics.json"],
        {"validation_scope": "PRIMARY_GROUPED_OOF_REPEAT_0", "n_groups": 482,
         "points": sorted(system_points, key=lambda r: r["group_id"]),
         "system_mae_mbps": q3_unified["primary_repeat_metrics"][0]["bounded"]["system_sum"]["mae"],
         "pipeline_primary_selection_score_repeat_mean": q3_unified["primary_point_estimate_repeat_mean"]["selection_score"]},
        "训练侧第 0 次 primary grouped OOF：482 个真实系统吞吐与预测吞吐，非官方测试集性能。",
        ["绘制 y=x 参考线", "轴单位 Mbps", "第 0 次重复不是唯一验证轮次；总指标采用三次重复均值"] ))

    ap_points = [{"row_key": r["row_key"], "group_id": r["group_id"],
                  "source_file": r["source_file"], "ap_count": r["ap_count"],
                  "truth_mbps": r["truth_throughput"],
                  "prediction_mbps": r["throughput_bounded"],
                  "residual_mbps": r["throughput_bounded"] - r["truth_throughput"]} for r in ap_rows]
    specs.append(fig(5, "prediction_diagnostics", "Q3 预测残差与 Q2 固定类别诊断", "numeric_panels",
        ["E-Q3-OOF-001", "E-Q2-CONF-001"],
        [MAIN / "q3_ap_oof_predictions.jsonl.gz", VERIFIED / "q2_baseline_metrics.json"],
        {"q3_ap_scope": "PRIMARY_GROUPED_OOF_REPEAT_0", "q3_ap_n": 1250,
         "q3_ap_points": sorted(ap_points, key=lambda r: r["row_key"]),
         "q3_ap_mae_mbps": q3_unified["primary_repeat_metrics"][0]["bounded"]["per_ap"]["mae"],
         "q2_labels": labels, "q2_confusion_by_repeat": matrices,
         "q2_matrix_axis": "rows=true label; columns=predicted label",
         "q2_matrix_n_per_repeat": 1250},
        "Q3 AP 残差来自训练侧第 0 次 OOF；Q2 三张混淆矩阵分别对应三次重复，不能当成 3750 个独立样本。",
        ["Q3 残差=预测−真实，零线必须可见", "Q2 保留固定 17 类含稀有类", "Q2 热图每次重复单独标注 n=1250"] ))

    q2_claim = verified_claims["Q2_FINAL_ROLLBACK"]
    q3_comparison = [
        {"model_id": model_id, "primary_score": model["primary_point_estimate_repeat_mean"]["selection_score"],
         "loso_score": model["loso_overall"]["selection_score"]}
        for model_id, model in (("Q3-B1", q3_b1),
                                ("Q3-M1-HGB-UNIFIED", q3_unified),
                                ("Q3-M1-HGB-APCOUNT", q3_apcount))
    ]
    specs.append(fig(6, "model_selection", "三问冻结选择与对照", "numeric_panels",
        ["E-Q1-001", "E-Q1-IMP-001", "E-Q2-001", "E-Q3-PIPE-001", "E-Q3-TRADE-001"],
        [VERIFIED / "q1_metrics.json", importance_verified,
         VERIFIED / "verified_metrics.json", VERIFIED / "q2_candidate_metrics.json",
         VERIFIED / "q3_baseline_metrics.json", VERIFIED / "q3_candidate_metrics.json"],
        {"q1_bounded_primary_mae_s": q1["primary_point_estimate_repeat_mean"]["bounded"]["mae"],
         "q1_feature_families": importance["feature_families"],
         "q2_baseline_macro_f1_fixed_17": q2_claim["baseline_macro_f1_fixed_17"],
         "q2_weighted_gain": q2_claim["weighted_gain"],
         "q2_promotion_threshold": q2_claim["promotion_threshold"],
         "q2_candidate_primary_metrics": {
             model_id: model["primary_point_estimate_repeat_mean"]
             for model_id, model in q2_cand["models"].items()},
         "q3_comparison": q3_comparison,
         "q3_relative_gain_vs_Q3_B1": verified_claims["Q3_NESTED_SELECTION_PIPELINE_PERFORMANCE"]["relative_gain_vs_Q3_B1"]},
        "Q1 特征组差异仅是 held-out predictive contribution；Q2 weighted 增益低于精确 +0.02 门槛；Q3 比较的是 nested pipeline，不是固定 C3 分数。",
        ["不同量纲分面展示，勿用双纵轴混排", "Q2 阈值标注精确数值", "Q3 低分更优；不暗示显著性检验"] ))

    loso_sources = q3_unified["loso_by_source"]
    require(len(loso_sources) == 13, "Q3 LOSO source count mismatch")
    worst = max(loso_sources, key=lambda row: row["selection_score"])
    require(math.isclose(worst["selection_score"], 2.159764, abs_tol=1e-6),
            "worst Q3 source value mismatch")
    specs.append(fig(7, "robustness_uncertainty", "Q3 不确定性与来源外推边界", "numeric_panels",
        ["E-Q3-UNC-001", "E-Q3-LOSO-001", "E-Q3-TRADE-001"],
        [VERIFIED / "group_bootstrap_intervals.json", VERIFIED / "q3_candidate_metrics.json"],
        {"unified_bootstrap": bootstrap["q3"]["Q3-M1-HGB-UNIFIED"],
         "unified_primary_score": q3_unified["primary_point_estimate_repeat_mean"]["selection_score"],
         "unified_loso_score": q3_unified["loso_overall"]["selection_score"],
         "apcount_loso_score": q3_apcount["loso_overall"]["selection_score"],
         "unified_loso_by_source": loso_sources, "worst_source": worst},
        "Bootstrap 是固定 OOF 的 group-resampling uncertainty，不含重训练/重选参；展示最差 held-out source，不声称逐来源一致鲁棒。",
        ["统一从零起始的可比尺度", "最差 source S 不可裁掉", "bootstrap n=1000 仅重采样组"] ))

    specs.append(fig(8, "deployment_decision", "冻结模型的部署与风险处置", "editable_diagram",
        ["E-FREEZE-001", "E-Q2-001", "E-Q3-CONFIG-001", "E-RELEASE-001"],
        [VERIFIED / "freeze_manifest.json", VERIFIED / "verified_metrics.json",
         VERIFIED / "final_release_verification.json"],
        {"selected_stack": {"q1": freeze["models"]["q1"]["model_id"],
                            "q2": freeze["models"]["q2"]["model_id"],
                            "q3": freeze["models"]["q3"]["model_id"]},
         "nodes": [
             {"id": "scenario", "label": "已授权的 WLAN 场景输入"},
             {"id": "q1", "label": "Q1 bounded 时长"},
             {"id": "q2", "label": "Q2 固定 17 类 NSS/MCS 概率；保留 Logistic"},
             {"id": "q3", "label": "Q3 unified residual-C3 AP 吞吐"},
             {"id": "system", "label": "系统吞吐=同组 bounded AP 求和"},
             {"id": "risk", "label": "低支持类别/场景外推风险；人工核查，不反向调模"},
         ], "edges": [["scenario", "q1"], ["scenario", "q2"],
                     ["scenario", "q3"], ["q1", "q3"],
                     ["q3", "system"], ["q2", "risk"], ["system", "risk"]],
         "release_status": load(VERIFIED / "final_release_verification.json")["status"]},
        "部署解释流程图，不是网络配置优化方案；官方无标签测试输出只证明单次部署产物，不证明精度或收益。",
        ["节点与条件可编辑", "保留稀有类及最差 source 风险提示", "不得增加未求解的网络调参建议"] ))

    FIGURE_DATA.mkdir(parents=True, exist_ok=True)
    records = []
    for filename, payload in specs:
        path = FIGURE_DATA / filename
        dump(path, payload)
        records.append({"figure_number": payload["figure_number"],
                        "path": repo_path(path), "sha256": sha256(path),
                        "bytes": path.stat().st_size,
                        "evidence_ids": payload["evidence_ids"]})
    manifest = {
        "status": "EIGHT_FIGURE_RESOURCES_READY_NOT_RENDERED",
        "figure_count": len(records),
        "figures": records,
        "source_gates": {"G1_reviewed_commit": G1_REVIEWED,
                         "G4_validation_manifest_sha256": freeze["prior_validation"]["g4_validated_artifact_manifest_sha256"],
                         "freeze_manifest_sha256": sha256(VERIFIED / "freeze_manifest.json")},
        "new_verified_q1_importance": source(importance_verified),
        "official_test_csv_numeric_read_count": 0,
        "official_test_prediction_artifacts_read": 0,
        "model_inference_count": 0,
        "images_rendered": 0,
    }
    require(len(records) == 8 and [row["figure_number"] for row in records] == list(range(1, 9)),
            "eight-figure resource coverage mismatch")
    dump(FIGURE_DATA / "figure_resource_manifest.json", manifest)
    print("status=EIGHT_FIGURE_RESOURCES_READY_NOT_RENDERED")
    print("figures=8")
    print("official_test_csv_numeric_read_count=0")
    print("images_rendered=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
