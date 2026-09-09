# CURRENT

## Project

项目名称：rehearsal_2024_B

ACTIVE_PROJECT：projects/rehearsal_2024_B

项目状态：ACTIVE

## Selected Problem

题号与名称：2024 年中国研究生数学建模竞赛 B 题《WLAN组网中网络吞吐量建模》

比赛类型：往年题模拟

题目版本：本地 DOCX SHA-256 C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594

## Current Stage

S1 — 题意拆解与数据审计；G1 Round 1 的两项 Major 已修订，G1 Round 2 提交包已完成并等待独立复审。

S1 → S2：NOT AUTHORIZED。

## Last Gate

Gate：G1 / Review Round 1

Verdict：REVISE

Review File：[reviews/gate_1_review.md](reviews/gate_1_review.md)

Reviewed Commit：512e461033c8378f1e591912b4992d8486bde396

Review Commit：e9253ce15a7b296298cf68c61b65357b55f1a1ed

## Approved Artifacts

- G0/R1 已 PASS，S0 交付物和进入 S1 的授权保持有效。
- G1/R1 认可 A01–A06、测试集封存、逐问白名单、OOF 链路和 source_file + test_id 分组方向。
- G1/R1 未授权进入 S2，并要求修复 M1-01 与 M1-02；这些修订现已形成 Round 2 待审包。

## Completed Round 2 Fixes

1. Q3 已覆盖 185 个 AP throughput、75 个严格系统组 throughput，以及 AP/系统两级 signed CDF、ERROR_90 和 accuracy_90。
2. 完整组已采用预期行数、精确 AP ID 集合/次数、复合键唯一三重检查。
3. 重复审计已区分文件内全列完全重复与跨文件规范化 SHA-256 行/组指纹。
4. 正式审计基于干净 commit 03ac99d91004fca2123011a3db29043d5612568c：17/17 输入哈希前后 PASS 且不变；eligible 482/482、测试 136/136 严格组通过；跨文件重复行/组簇均为 0。
5. work/revisions/gate_1_response.md 与 reviews/gate_1_submission_r2.md 已完成。

## Current Goal

提交并推送 G1 Round 2 固定快照，然后等待 Reviewer 新增 reviews/gate_1_review_r2.md。

## Current Tasks

1. 完成最终一致性校验和日志。
2. 提交并推送 Round 2 固定 SHA。
3. 等待 G1 Round 2 独立审核；PASS 前不进入 S2。

## Current Process Blockers

- 科学门禁：G1 Round 2 Reviewer 尚未给出 PASS。
- 外部流程阻塞：None。用户已授权推送 origin/main。

## Known Limitations / Risks

- 原始 CSV 被 Git 忽略，远程 Reviewer 无授权副本时只能核对脚本、manifest、JSON/Markdown 和本地哈希证据。
- 原始数据授权获取位置或稳定 URL 尚未记录；当前只确认团队本机副本与 manifest 哈希一致。
- A01–A06 必须继续遵循冻结合同。
- 团队成员实名责任分配尚未提供；最终提交须由人类队员负责。
- environment.yml 尚未 clean rebuild；当前机器导入 smoke=PASS。
- Q1/Q2 官方评分函数和最终预测文件格式未在现有题面材料中明确。
- 题面 Q3 使用有符号相对误差，可能产生超过 100% 或为负的 accuracy_90，必须按合同原样披露并辅以绝对误差诊断。

## Forbidden Now

- 在 G1 Round 2 PASS 或用户书面改变门禁前进入 S2、拟合正式模型、调参或生成测试预测。
- 覆写原始 DOCX/CSV，或把派生数据写回 problem/data。
- 让同一 source_file + test_id 组的 AP 行跨训练/验证折。
- 使用官方测试集数值分布或输出选择特征、阈值、规则、超参数或模型。
- Q1 使用事后统计；Q2 使用真实 nss/mcs 或其派生量；Q3 将真实 MCS/NSS 特许扩展到 PER 等字段。
- 静默删除异常或重复簇、修改原件，或把统计关联写成因果。
- Main Agent 新增或修改 reviews/gate_1_review_r2.md。

## Next Gate

Gate：G1 / Review Round 2

Verdict：PENDING REVIEW

Response：[work/revisions/gate_1_response.md](work/revisions/gate_1_response.md)

Submission：[reviews/gate_1_submission_r2.md](reviews/gate_1_submission_r2.md)

Expected Review：reviews/gate_1_review_r2.md

Formal Audit Implementation Commit：03ac99d91004fca2123011a3db29043d5612568c

Reviewed Commit：由 Reviewer 使用推送后的 origin/main 完整 SHA

## Last Updated

时间：2026-09-09T10:39:37+08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
