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

S0 — 项目初始化与约束确认（交付物已完成，等待 G0 审核）

## Last Gate

Gate：G0 / Review Round 1

Verdict：PENDING REVIEW

Review File：尚未生成；Reviewer 只能新增 reviews/gate_0_review.md

Reviewed Commit：待 S0 提交固定并推送后填写/传入

## Approved Artifacts

- None。当前尚无 Reviewer PASS。
- 本地题目与数据已经过 S0 只读清点，但尚未获准进入 S1。

## Current Goal

冻结题目、17 个 CSV、2024 年官方约束、运行环境、已知数据风险和项目状态，提交 G0 独立审核。

## Current Tasks

1. 将本轮 S0 文档固定到单一 Git commit。
2. 推送固定 commit，向 Reviewer 提供完整 SHA。
3. 等待 Reviewer 对 reviews/gate_0_submission.md 给出 PASS / REVISE / BLOCK。

## Known Blockers

- None：本机开展 S1 所需题面和 17 个数据文件均存在且可读取。
- 远程可复现限制：CSV 按仓库策略被 Git 忽略；远程 Reviewer 依赖 manifest 的文件名、大小、SHA-256 和结构证据，其他机器需另行取得原始数据。
- 数据完整性风险已登记但未在原件中修复：training_set_2ap_loc2_nav82.csv 两行错位、training_set_3ap_loc30_nav86.csv 三个 RSSI 列全空、3 条 nss=0。
- 团队成员姓名和最终职能分工尚未提供；当前按功能角色记录。
- environment.yml 尚未在全新环境中做 clean rebuild；当前机器冒烟测试已通过。

## Forbidden Now

- 在 G0 PASS 或用户书面批准前进入 S1、设计正式模型或运行调参。
- 覆写、清洗或向测试集填值；所有派生数据必须写入 results/raw/。
- 使用四个官方测试集做特征选择、调参、模型选择或伪造泛化指标。
- 把已知异常静默删除、填补或当作不存在。
- 修改 competition/2024/ 官方材料或 Reviewer 审核文件。
- 把当前 S0 可用性结论表述为数据已通过逐字段 S1 审计。

## Next Gate

G0 — 项目初始化与约束确认审核

Verdict：PENDING REVIEW

Submission：[reviews/gate_0_submission.md](reviews/gate_0_submission.md)

## Last Updated

时间：2026-09-08 22:10 +08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充