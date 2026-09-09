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

S1 — 题意拆解与数据审计；G1 Round 1 结果为 REVISE，正在完成 Round 2 修订。

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
- G1/R1 未授权进入 S2，要求在 S1 内修复 M1-01 与 M1-02。

## Current Goal

完成 G1 Round 2 修订：

1. 恢复并冻结 Q3 的系统吞吐量、AP/系统两级误差 CDF、ERROR_90 和 accuracy_90；
2. 补齐精确 AP 身份集合、复合键唯一和跨文件规范化重复指纹审计；
3. 在干净实现 commit 上重跑正式审计；
4. 提交并推送 Round 2 响应包，然后等待独立复审。

## Current Tasks

1. 完成 work/01–03、src/s1_data_audit.py 与机器证据同步。
2. 更新 decisions、experiments、ai_usage 和正式审计 commit 谱系。
3. 编写 work/revisions/gate_1_response.md。
4. 编写 reviews/gate_1_submission_r2.md 并推送固定 SHA。
5. 停留在 S1，等待 reviews/gate_1_review_r2.md。

## Current Process Blockers

- 科学门禁：M1-01 与 M1-02 在 Round 2 正式证据和复审 PASS 前仍阻断进入 S2。
- 外部流程阻塞：None。用户已授权推送 origin/main。

## Known Limitations / Risks

- 原始 CSV 被 Git 忽略，远程 Reviewer 无授权副本时只能核对脚本、manifest、JSON/Markdown 和本地哈希证据。
- 原始数据授权获取位置或稳定 URL 尚未记录；当前只确认团队本机副本与 manifest 哈希一致。
- A01–A06 的错位、全空列、(NSS,MCS)=(0,0)、schema、other_air_time 超时长和 loc 标签不一致必须继续遵循冻结合同。
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

G1 — 题意拆解与数据审计

Review Round：2

Verdict：NOT SUBMITTED

Planned Response：work/revisions/gate_1_response.md

Planned Submission：reviews/gate_1_submission_r2.md

Expected Review：reviews/gate_1_review_r2.md

Formal Audit Implementation Commit：FORMAL_AUDIT_COMMIT_TO_BE_FILLED

## Last Updated

时间：2026-09-09T10:33:25+08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
