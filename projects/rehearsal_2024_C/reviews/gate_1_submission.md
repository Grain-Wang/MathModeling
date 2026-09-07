# Gate 1 Submission

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_C`
- Gate: `G1`
- Stage: `S1 — 题意拆解与数据审计`
- G0 transition commit: `f6b2637a061630013c3a6b5812441950b7e0eb77`
- Review commit: 调用 Reviewer 时传入本次 S1 提交推送后的 `git rev-parse HEAD` 完整 SHA
- Prepared at: 2026-09-07 +08:00

Reviewer 必须基于远程固定完整 SHA 审核，不能改用随后变化的 branch HEAD。

## Deliverables

- [`work/01_problem_analysis.md`](../work/01_problem_analysis.md)
- [`work/02_data_audit.md`](../work/02_data_audit.md)
- [`work/03_requirement_matrix.md`](../work/03_requirement_matrix.md)
- [`src/s1_data_audit.py`](../src/s1_data_audit.py)
- [`results/raw/s1/data_profile.json`](../results/raw/s1/data_profile.json)
- [`results/raw/s1/dataset_summary.csv`](../results/raw/s1/dataset_summary.csv)
- [`results/raw/s1/categorical_counts.csv`](../results/raw/s1/categorical_counts.csv)
- [`results/raw/s1/numeric_ranges.csv`](../results/raw/s1/numeric_ranges.csv)
- [`results/raw/s1/quality_checks.csv`](../results/raw/s1/quality_checks.csv)
- [`results/raw/s1/waveform_position_profile.csv`](../results/raw/s1/waveform_position_profile.csv)
- [`logs/decisions.md`](../logs/decisions.md)
- [`logs/experiments.md`](../logs/experiments.md)
- [`logs/ai_usage.md`](../logs/ai_usage.md)
- [`CURRENT.md`](../CURRENT.md)

## Reproduction Command

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
conda run -n math_modeling python projects/rehearsal_2024_C/src/s1_data_audit.py
```

预期末行：

```text
S1 audit PASS: ...\projects\rehearsal_2024_C\results\raw\s1
```

脚本是确定性只读审计：以 openpyxl `read_only=True` 打开四个 XLSX，不保存工作簿，不拟合模型；每次运行只重建 `results/raw/s1/` 下六个派生文件。

## Main Claims

1. 五个小问均已逐项给出目标、输入、输出、决策/状态变量、已知量、未知量、约束、依赖和初步验证路径。
2. 题目要求的附件输出、编码、舍入、计数和两组指定样本 ID 已逐条进入需求矩阵。
3. 训练集含 12,400 条、四种材料、四个温度和三种波形；48 个“材料×温度×波形”组合全部有样本。
4. 训练、附件二、附件三的元字段和 1,024 点波形没有缺失或非有限值；测试 ID 完整且唯一。
5. 五个输入文件审计前后 SHA-256 与 manifest 一致，附件四输出槽保持为空。
6. 审计共 154 项检查：0 FAIL、5 WARN；没有训练—测试完全相同的 1,024 点波形。
7. 附件二、三不得参与特征选择、调参、模型选择或内部精度声明；该边界已经在三份 S1 文档与决策日志中冻结。
8. 回答题目五问不要求额外外部数据；真实器件约束属于当前附件不可观测且非题面必需的扩展范围。

## Known Risks and Non-Blocking Findings

1. 题面标称频率为 50,000–500,000 Hz，实测训练集 163 条轻微越界（49,990–501,180 Hz），附件二、三各 2 条达到 501,180 Hz。原值保留，S2 必须规定可行域口径并做边界敏感性。
2. 材料3存在 1 个完全重复组（1 条额外重复记录）。S1 不删除；S2 必须决定去重或同指纹分组，并验证敏感性。
3. 精确指纹未发现训练—测试重合，但尚未定义相移、缩放或近邻波形重复；S2 应冻结近重复/工况分组策略。
4. 损耗和幅值分布明显右偏，IQR 会标记较多高值；这些值不能在无证据时自动删除。
5. 附件三无真实损耗，问题四精度只能来自附件一内部验证；问题五只能解释为数据支持域和题目代理指标下的优化。
6. 当前没有已选择的最终模型、超参数、测试集预测或 `results/verified/` 结果；这些不是 S1 交付物。

## G1 Self-Check Against Reviewer Criteria

| Criterion | Evidence | Main Agent status |
|---|---|---|
| 全部小问题意、变量、约束、目标 | `work/01_problem_analysis.md` | COMPLETE |
| 小问依赖，特别是 Q5 依赖 Q4 | `work/01_problem_analysis.md` 第 2、7 节 | COMPLETE |
| 字段、单位、范围、规模 | `work/02_data_audit.md` 第 2–4 节 | COMPLETE |
| 缺失、异常、重复、量纲 | `work/02_data_audit.md` 第 5–7 节及 raw CSV | COMPLETE |
| 不可观测变量和外部数据 | `work/01_problem_analysis.md` 各问；`work/02_data_audit.md` 第 8 节 | COMPLETE WITH LIMITS |
| 泄漏边界 | `work/02_data_audit.md` 第 7 节；需求矩阵第 2 节 | COMPLETE |
| 需求到输出和验证证据 | `work/03_requirement_matrix.md` | COMPLETE |
| 未漏问/未偷换问题 | R1.1–R5.2 | COMPLETE |

## Verification Commands

```powershell
conda run -n math_modeling python projects/rehearsal_2024_C/src/s1_data_audit.py
git diff --check
git status --short
git ls-files "projects/rehearsal_2024_C/src/*.xlsx"
git check-ignore -v projects/rehearsal_2024_C/src/附件一（训练集）.xlsx
git rev-parse HEAD
```

## Requested Verdict

`PASS`。若 Reviewer 认可题意、数据和验证路径已经清楚，请授权 `S1 → S2`，下一 Gate 为 G2。若发现问题，请按 Critical/Major/Minor 分类并给出可复核的 Required Fixes；Main Agent 不自行宣布 G1 通过。
