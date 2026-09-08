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

S1 — 题意拆解与数据审计（进行中）

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

完成 Q1–Q3 逐问拆解、17 个 CSV 的可复现逐字段审计、异常处理合同、数据泄漏边界和“题目要求 → 模型输出 → 验证证据”矩阵，随后提交 G1 独立审核。

## Current Tasks

1. 增加 problem/data/README.md，固化远程数据恢复和审计前哈希检查。
2. 实现并固定 src/s1_data_audit.py，先在干净实现 commit 上运行。
3. 生成 results/raw/s1/ 的 JSON/Markdown 审计证据，审计前后复核原件 SHA-256。
4. 完成 work/01_problem_analysis.md、work/02_data_audit.md、work/03_requirement_matrix.md。
5. 关闭可在 S1 处理的 G0 Minor，更新日志并创建 reviews/gate_1_submission.md。

## Current Process Blockers

- None。G0 已 PASS，本机输入和环境允许执行 S1。

## Known Limitations / Risks

- CSV 被 Git 忽略，远程 Reviewer 不能重跑原始数据审计；必须依赖脚本、manifest、结果 JSON 和本地哈希证据。
- 原始数据授权获取位置/稳定 URL 尚未记录；当前只确认团队本机副本和 SHA-256。
- 已知两行错位、三个全空 RSSI 列、三条 nss=0 和 schema 差异必须在 S1 明确处理，原件不得改写。
- 团队责任人姓名尚未提供；当前只记录功能角色。
- environment.yml 尚未 clean rebuild；当前机器 smoke=PASS。

## Forbidden Now

- 在 G1 PASS 或用户书面批准前进入 S2、冻结主模型方案或运行正式模型比较/调参。
- 覆写原始 DOCX/CSV，或将清洗结果写回 problem/data/。
- 让同一 source_file + test_id 的不同 AP 行跨训练/验证折。
- 使用四个官方测试集的分布或输出进行特征选择、调参、规则调整或模型选择。
- Q1 使用 nss、mcs、per、num_ampdu、ppdu_dur、other_air_time、seq_time、throughput 等事后统计。
- Q2 使用真实 nss/mcs 或其派生量作输入；Q3 将题面只授权的真实 MCS/NSS 扩张到 PER 等其他事后字段。
- 静默删除异常或把统计关联写成因果。

## Next Gate

G1 — 题意拆解与数据审计审核

Verdict：NOT SUBMITTED

Submission：待 S1 交付物和证据完成后创建 reviews/gate_1_submission.md

## Last Updated

时间：2026-09-08T22:35:42+08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
