from pathlib import Path

PROTOCOL = ".agents/protocols/optimization_protocol.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one marker, found {count}")
    return text.replace(old, new, 1)


main_path = Path(".agents/roles/main_agent.md")
main = main_path.read_text(encoding="utf-8")

if PROTOCOL not in main:
    main = replace_once(
        main,
        "## 9.2 必须完成\n\n1. 提出全题总体技术路线；",
        "## 9.2 必须完成\n\n进入 S2 的 O1 总体方案优化节点时，主 Agent **必须读取并遵守**：\n\n```text\n.agents/protocols/optimization_protocol.md\n```\n\n完成 O1 并形成 `work/optimization/o1_solution_optimization.md` 后，才可提交 G2。\n\n1. 提出全题总体技术路线；",
        "main S2 trigger",
    )
    main = replace_once(
        main,
        "work/05_experiment_plan.md\n```",
        "work/05_experiment_plan.md\nwork/optimization/o1_solution_optimization.md\n```",
        "main S2 artifact",
    )
    main = replace_once(
        main,
        "- 已明确什么情况下继续改进，什么情况下回退 Baseline。",
        "- 已明确什么情况下继续改进，什么情况下回退 Baseline；\n- 已按照优化协议完成 O1，且决策为 `PROCEED_TO_G2`。",
        "main G2 acceptance",
    )
    main = replace_once(
        main,
        "## 10.2 必须完成\n\n1. 建立可运行的数据处理流程；",
        "## 10.2 必须完成\n\n全题 Baseline 跑通后，主 Agent 必须进入 O2 失败诊断节点，并 **读取、遵守**：\n\n```text\n.agents/protocols/optimization_protocol.md\n```\n\n完成 `work/optimization/o2_baseline_diagnosis.md`、选定有限的 S4 改进方向后，才可提交 G3。\n\n1. 建立可运行的数据处理流程；",
        "main S3 trigger",
    )
    main = replace_once(
        main,
        "work/06_baseline_report.md\nlogs/experiments.md\n```",
        "work/06_baseline_report.md\nwork/optimization/o2_baseline_diagnosis.md\nlogs/experiments.md\n```",
        "main S3 artifact",
    )
    main = replace_once(
        main,
        "- 已记录 Baseline 的主要不足。",
        "- 已记录 Baseline 的主要不足；\n- 已按照优化协议完成 O2，且决策为 `PROCEED_TO_G3`。",
        "main G3 acceptance",
    )
    main = replace_once(
        main,
        "## 11.2 必须完成\n\n1. 识别 Baseline 的主要失败模式；",
        "## 11.2 必须完成\n\n主模型和主要验证完成后，主 Agent 必须进入 O3 优化收益审计与冻结决策节点，并 **读取、遵守**：\n\n```text\n.agents/protocols/optimization_protocol.md\n```\n\n只有在 `work/optimization/o3_freeze_decision.md` 的决定为 `FREEZE_CANDIDATE` 时，才可提交 G4；若为 `ONE_BOUNDED_ITERATION` 或 `BACKTRACK`，必须先按协议继续处理。\n\n1. 识别 Baseline 的主要失败模式；",
        "main S4 trigger",
    )
    main = replace_once(
        main,
        "work/09_evidence_report.md\n```",
        "work/09_evidence_report.md\nwork/optimization/o3_freeze_decision.md\n```",
        "main S4 artifact",
    )
    main = replace_once(
        main,
        "- 仍有足够时间进行结果冻结和论文检查。",
        "- 仍有足够时间进行结果冻结和论文检查；\n- 已按照优化协议完成 O3，且决策为 `FREEZE_CANDIDATE`。",
        "main G4 acceptance",
    )
    main_path.write_text(main, encoding="utf-8")

reviewer_path = Path(".agents/roles/reviewer_agent.md")
reviewer = reviewer_path.read_text(encoding="utf-8")

if PROTOCOL not in reviewer:
    reviewer = replace_once(
        reviewer,
        "## 15.1 应读取的核心交付物\n\n```text\nwork/04_solution_plan.md",
        "## 15.1 应读取的核心交付物\n\nG2 审核时，Reviewer Agent **必须读取并遵守**：\n\n```text\n.agents/protocols/optimization_protocol.md\n```\n\n并读取：\n\n```text\nwork/04_solution_plan.md",
        "reviewer G2 protocol",
    )
    reviewer = replace_once(
        reviewer,
        "work/03_requirement_matrix.md\n```",
        "work/03_requirement_matrix.md\nwork/optimization/o1_solution_optimization.md\n```",
        "reviewer G2 artifact",
    )
    reviewer = replace_once(
        reviewer,
        "- 是否过早追求复杂模型？",
        "- 是否过早追求复杂模型？\n\n### O1 优化协议合规性\n\n- O1 报告是否基于当前方案、模型合同和数据证据？\n- 是否比较了收益、时间、风险、验证和回退？\n- 是否设置了明确成功标准与停止条件？\n- O1 决策是否为 `PROCEED_TO_G2`？",
        "reviewer G2 checks",
    )
    reviewer = replace_once(
        reviewer,
        "- Baseline、验证和失败判断均已定义。",
        "- Baseline、验证和失败判断均已定义；\n- O1 报告完整且符合优化协议，决策为 `PROCEED_TO_G2`。",
        "reviewer G2 pass",
    )
    reviewer = replace_once(
        reviewer,
        "## 16.1 应读取的核心交付物\n\n```text\nsrc/",
        "## 16.1 应读取的核心交付物\n\nG3 审核时，Reviewer Agent **必须读取并遵守**：\n\n```text\n.agents/protocols/optimization_protocol.md\n```\n\n并读取：\n\n```text\nsrc/",
        "reviewer G3 protocol",
    )
    reviewer = replace_once(
        reviewer,
        "Gate submission 中的运行命令和日志\n```",
        "Gate submission 中的运行命令和日志\nwork/optimization/o2_baseline_diagnosis.md\n```",
        "reviewer G3 artifact",
    )
    reviewer = replace_once(
        reviewer,
        "- 报告中的数字能否在结果中找到？",
        "- 报告中的数字能否在结果中找到？\n\n### O2 优化协议合规性\n\n- O2 是否先排除实现错误、数据问题和泄漏，再归因于模型能力？\n- 瓶颈是否由真实 Baseline 证据支持？\n- S4 主要改进是否被限制为少量高价值方向？\n- 每个改进是否有时间盒、验证标准和回退版本？\n- O2 决策是否为 `PROCEED_TO_G3`？",
        "reviewer G3 checks",
    )
    reviewer = replace_once(
        reviewer,
        "- 后续创新失败时仍有完整底座。",
        "- 后续创新失败时仍有完整底座；\n- O2 报告完整且符合优化协议，决策为 `PROCEED_TO_G3`。",
        "reviewer G3 pass",
    )
    reviewer = replace_once(
        reviewer,
        "## 17.1 应读取的核心交付物\n\n```text\nwork/07_failure_analysis.md",
        "## 17.1 应读取的核心交付物\n\nG4 审核时，Reviewer Agent **必须读取并遵守**：\n\n```text\n.agents/protocols/optimization_protocol.md\n```\n\n并读取：\n\n```text\nwork/07_failure_analysis.md",
        "reviewer G4 protocol",
    )
    reviewer = replace_once(
        reviewer,
        "Baseline 相关材料\n```",
        "Baseline 相关材料\nwork/optimization/o3_freeze_decision.md\n```",
        "reviewer G4 artifact",
    )
    reviewer = replace_once(
        reviewer,
        "- 结论是否可以被论文安全表述？",
        "- 结论是否可以被论文安全表述？\n\n### O3 优化协议合规性\n\n- O3 是否审计了真实收益、证据公平性和剩余时间？\n- 是否明确了最终候选模型、配置、结果版本和停止条件？\n- 是否仍存在无边界调参或未完成的竞争路线？\n- O3 决策是否为 `FREEZE_CANDIDATE`？\n- 如果曾决定 `ONE_BOUNDED_ITERATION`，该动作是否已经完成并重新形成 O3 结论？",
        "reviewer G4 checks",
    )
    reviewer = replace_once(
        reviewer,
        "- 已达到停止扩张、进入结果冻结的条件。",
        "- 已达到停止扩张、进入结果冻结的条件；\n- O3 报告完整且符合优化协议，决策为 `FREEZE_CANDIDATE`。",
        "reviewer G4 pass",
    )
    reviewer_path.write_text(reviewer, encoding="utf-8")

for path in (main_path, reviewer_path):
    text = path.read_text(encoding="utf-8")
    assert text.count(PROTOCOL) == 3
    for artifact in (
        "o1_solution_optimization.md",
        "o2_baseline_diagnosis.md",
        "o3_freeze_decision.md",
    ):
        assert artifact in text

print("optimization protocol role integration: PASS")
