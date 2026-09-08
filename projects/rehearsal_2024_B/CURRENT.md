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

S1 — 题意拆解与数据审计（交付物完成，G1 本地审核包就绪）

## Last Gate

Gate：G0 / Review Round 1

Verdict：PASS

Review File：[reviews/gate_0_review.md](reviews/gate_0_review.md)

Reviewed Commit：2afba29b3cae4d6e500e0b4faa25aa3130953672

Review Commit：0fac4e099cffdafab32af0aa9af9f8969f087dbe

## Approved Artifacts

- S0 的 problem/manifest.md、work/00_project_brief.md、三份日志、CURRENT 和 G0 submission。
- 本地题目与 17 个 CSV 的只读清点、逐文件 SHA-256 和基础结构证据。
- competition/2024/ 中适用的官方规则、格式规范、提交手册和模板。
- math_modeling 当前机器环境的导入冒烟结果。
- G0 Reviewer 授权的 S1 工作边界。

## Current Goal

将完整 S1 交付物固定到单一 Git commit，在获得明确远程推送授权后推送 origin/main，并以完整 SHA 请求 G1 Round 1 独立审核。

## Current Tasks

1. 完成最终一致性检查并提交 S1 文档、脚本、结果、日志、CURRENT 和 G1 submission。
2. 等待用户明确授权 git push origin main；此前不产生远程写入。
3. 推送后向 Reviewer 提供固定完整 SHA，等待 reviews/gate_1_review.md。
4. G1 PASS 前不进入 S2。

## Current Process Blockers

- 远程 G1 审查尚未开始：当前会话的安全审批要求用户明确授权向 origin/main 推送；本地工作可继续且 S1 审核包已就绪。

## Known Limitations / Risks

- CSV 被 Git 忽略，远程 Reviewer 不能重跑原始数据审计；必须依赖脚本、manifest、结果 JSON 和本地哈希证据。
- 原始数据授权获取位置/稳定 URL 尚未记录；当前只确认团队本机副本与 manifest SHA-256 一致。
- A01–A06 的错位、全空列、(NSS,MCS)=(0,0)、schema、other_air_time 超时长和 loc 标签不一致必须沿用冻结合同。
- 团队责任人姓名尚未提供；当前只记录功能角色，最终提交必须由人类队员负责。
- environment.yml 尚未 clean rebuild；当前机器 smoke=PASS。
- 官方评分函数和最终预测文件格式未在题面明确给出。

## Forbidden Now

- 在 G1 PASS 或用户书面批准前进入 S2、冻结主模型方案或运行正式模型比较/调参。
- 覆写原始 DOCX/CSV，或将清洗结果写回 problem/data/。
- 让同一 source_file + test_id 的不同 AP 行跨训练/验证折。
- 使用四个官方测试集的数值分布或输出进行特征选择、调参、规则调整或模型选择。
- Q1 使用 nss、mcs、per、num_ampdu、ppdu_dur、other_air_time、seq_time、throughput 等事后统计。
- Q2 使用真实 nss/mcs 或其派生量作输入；Q3 将题面只授权的真实 MCS/NSS 扩张到 PER 等其他事后字段。
- 静默删除异常、修改原件，或把统计关联写成因果。
- Main Agent 自行新增或修改 reviews/gate_1_review.md。

## Next Gate

G1 — 题意拆解与数据审计审核

Verdict：PENDING REVIEW（本地包完成；尚未推送远程）

Submission：[reviews/gate_1_submission.md](reviews/gate_1_submission.md)

待审核实现证据 commit：f4b8b9f70e049d497edf56a3bdac43669da932a6

最终 Reviewed Commit：待包含全部 G1 交付物的本地 commit 创建并获准推送后，由调用 Reviewer 时传入

## Last Updated

时间：2026-09-08T23:13:34+08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
