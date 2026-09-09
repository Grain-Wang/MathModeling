# CURRENT

## Project

- 项目名称：rehearsal_2024_B
- ACTIVE_PROJECT：projects/rehearsal_2024_B
- 项目状态：ACTIVE
- 题目：2024 年中国研究生数学建模竞赛 B 题《WLAN 组网中网络吞吐量建模》
- 类型：往年题模拟
- 题目版本：本地 DOCX SHA-256 `C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594`

## Current Stage

S4 — 主模型改进与证据构建。G3 Round 1 已 PASS，S3→S4 已授权；当前只执行 O2 与 G3 限定的 Q2、Q3 两个方向。

## Last Gate

- Gate：G3 / Review Round 1
- Verdict：PASS
- Review File：[reviews/gate_3_review.md](reviews/gate_3_review.md)
- Reviewed Commit：`e352c4233bb6a974e974ab697481b712a9c83d0b`
- Review Commit：`a5433257bf94ab651a53b86244d8a86edc72f9e4`
- Authorization：S3→S4；Next Gate=G4
- Findings：Critical=0，Major=0，Minor=3，Advisory=2

## Approved S4 Boundary

### Q2

- 四个冻结无权重 HGB 配置，primary 不含 Q1。
- 若完整 unweighted primary OOF 仍发生预定义类别坍缩，只允许一次 `sqrt(N/(K*n_k))`、cap=5 的固定权重候选。
- with-Q1 只作同配置依赖消融；上游仍唯一为 Q1-B1 bounded。
- 晋级：macro-F1 至少 +0.02，至少 2/3 repeats 改善，accuracy 降幅不超过 0.01。

### Q3

- 四个 direct + 四个 physics-residual HGB，使用冻结 nested-upstream registry。
- 最佳统一结构只作一次 2 AP/3 AP 分模对照。
- 晋级：相对最佳 primary Baseline 的 S 至少改善 5%，至少 2/3 repeats 改善，并通过 AP/system bias 护栏。
- system 始终严格等于 bounded AP 预测之和，禁止独立 system head。

## Current Goal

完成 S4 正式训练侧运行、独立复算、对比/消融/敏感性/鲁棒性证据及 O3；若 O3=`FREEZE_CANDIDATE`，形成 G4 审核包并停在 G4 等待 Reviewer。

## Current Tasks

1. 从干净实现 commit 运行完整 S4：15 primary outer folds、13 source-blind LOSO、冻结 4/8 候选与条件对照。
2. 生成 `results/raw/main/` 逐行预测、选择 trace、实际 lineage、Bootstrap 与唯一 final candidate。
3. 用独立验证器重算指标、预算、Q3 system sum 和 provenance manifest。
4. 完成 work/07、08、09 与 O3 freeze decision。
5. O3 仅在 `FREEZE_CANDIDATE` 时提交 G4。

## Current Process Blockers

- 无技术阻塞。
- G4 尚未审核；S5 和官方测试最终推理不得启动。

## Implementation Decisions

- `basic__ap_count` 保持 numeric binary 2/3，所有 S4 候选一致；不与旧 Baseline 混用新表示。
- A03 只称 `evaluation-exclusion diagnostic`；本阶段不声称删组重训鲁棒性。
- 唯一全量配置只根据 45 个 primary downstream-inner 记录按冻结词典序决定；outer promotion 决定是否保留权重/AP-count split，测试数据不参与。
- Baseline 正式快照 `2222cf5` 保持不变，S4 输出只写 `results/raw/main/`。

## Known Limitations / Risks

- Q2 support=1–2 的类别即使偶然命中也不能形成强可学习性结论。
- Q2 与 Q3 的 LOSO 可能显著弱于 primary，必须完整披露。
- Q3 residual 的 rate-missing 行使用当前训练边界内 Q3-B1 回退。
- AP-count 分模减少每个子模型的训练池；未达到同一阈值即回退统一结构。
- G2 遗留的 release-ledger exactly-once 门禁必须在 G4/S5 正式测试入口前完成。

## Forbidden Now

- Q1-HGB、替换下游 Q1-B1、扩大 4/4/8 网格或新增算法族。
- 第二种权重公式、额外 AP-count 分模、独立 system head。
- 改变固定 17 类、split registry、Q3 指标、bounded 主口径或 AP-count 表示。
- 在 G4 PASS 与 S5 freeze manifest 完整前解析、推理或人工查看官方测试 CSV 数值或预测。
- 将任何 CSV 加入 Git，覆盖 `results/raw/baseline/`，或写入 `results/verified/`。
- 修改 Reviewer 文件或已批准合同来迎合结果。

## Next Gate

- Gate：G4
- Status：NOT READY
- Preconditions：S4 正式结果、comparison/ablation/sensitivity/robustness、work/07–09、O3=`FREEZE_CANDIDATE`
- Requested transition：S4→S5（仅由未来 G4 PASS 授权）

## Last Updated

- 时间：2026-09-09
- 负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充
