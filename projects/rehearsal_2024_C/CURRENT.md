# CURRENT

## Project

项目名称：`rehearsal_2024_C`

ACTIVE_PROJECT：`projects/rehearsal_2024_C`

## Selected Problem

题号与名称：2024 年中国研究生数学建模竞赛 C 题《数据驱动下磁性元件的磁芯损耗建模》

比赛类型：往年题模拟

## Current Stage

S4 — 主模型改进、消融与稳健性证据（执行中）

## Last Gate

Gate：G3 / Review Round 1

Verdict：`PASS`

Review File：[`reviews/gate_3_review.md`](reviews/gate_3_review.md)

Reviewed Commit：`17cefbfe7bda13fa97f2eb19decc1abd02529597`

Review Commit：`076a7a3070dbd4b10c164b15bd4e02cf460368c4`

## Approved Artifacts

- S0–S2 已批准文档、合同、冻结配置和数据审计产物；
- `work/06_baseline_report.md`；
- `src/` 中 S3 特征、Q1–Q5 Baseline 与独立复算实现；
- `experiments/baseline/` 的 8 份实验描述；
- `results/raw/s3/` 和 `results/raw/baseline/` 的 S3 原始证据；
- `reviews/gate_3_submission.md`。

上述结果已通过 G3，但仍保持 `raw` 状态；只有后续 G5 才能升级为正式核验证据。

## Current Goal

从 G3 已确认的真实失败信号出发，在不改变 `s2-r2-v1` 固定外层折、指标、阈值和候选上限的前提下，完成有限 S4 改进、同折比较、消融、敏感性与稳健性证据，并提交 G4。

## Current Tasks

1. 关闭 G3 三项 Minor：修正日志历史表述、补齐 OOF/full 空交与 Jaccard 双空集直接测试、让新 manifest 记录仓库相对命令。
2. Q2：二次乘性温度修正，同折比较并重点报告 25°C/90°C 留一温度。
3. Q4：HGB 与 Ridge 同折比较；只有总体 RMSLE 相对改善≥2%且主要子组恶化≤10%才替换，并检查低 `B_m`。
4. Q5：消费最终 Q4 胜者的严格 OOF，完成 500 次 `condition_group` 重采样及频率/峰值敏感性。
5. Q3：三组预定义两两交互、共同支持与 500 次工况组 Bootstrap，只作调整后关联解释。
6. Q1：相位/幅值不变性、留一材料和特征/辅助字段消融；若 Logistic 稳定饱和则不强行升级树模型。

## Known Blockers

- 无流程阻断；G3 已 PASS。
- Q5 当前模型/观测 Pareto 区域 Jaccard=0.0962<0.50，且 Bootstrap 尚未完成，因此仍禁止唯一推荐。

## Forbidden Now

- 使用附件二、附件三参与特征选择、调参、模型选择或 Q5 域/阈值制定。
- 改动固定外层折、主指标、搜索空间或采用阈值迎合结果。
- 无边界扩展模型族，或隐藏负结果、Q5 Jaccard/稳定性失败。
- 把 `results/raw/` 当作 verified 论文证据，或在 G5 前写入 `results/verified/`。
- 在 Q5 双 Pareto、折支持、Bootstrap、Jaccard 任一门槛未通过时给出唯一推荐。
- 覆写题目 DOCX、四个原始 XLSX或任何 Reviewer 审核文件。

## Next Gate

G4 — 主模型改进、比较和证据审核

Verdict：`NOT SUBMITTED`

## Last Updated

时间：2026-09-08 +08:00

负责人：Main Agent（当前会话由 Codex 执行）；参赛团队具体责任人待补充