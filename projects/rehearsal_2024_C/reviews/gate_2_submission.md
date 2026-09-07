# Gate 2 Submission

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_C`
- Gate: `G2`
- Stage: `S2 — 总体方案与模型合同`
- G1 transition commit: `b4a3c1be43ffea3e9975adb6866777a5df71e16c`
- Review commit: 调用 Reviewer 时传入本次 S2 提交推送后的 `git rev-parse HEAD` 完整 SHA
- Prepared at: 2026-09-07 +08:00

Reviewer 必须审核远程固定完整 SHA，不得改用随后变化的 branch HEAD。

## Deliverables

- [`work/04_solution_plan.md`](../work/04_solution_plan.md)
- [`work/models/00_shared_data_validation_contract.md`](../work/models/00_shared_data_validation_contract.md)
- [`work/models/q1_model_contract.md`](../work/models/q1_model_contract.md)
- [`work/models/q2_model_contract.md`](../work/models/q2_model_contract.md)
- [`work/models/q3_model_contract.md`](../work/models/q3_model_contract.md)
- [`work/models/q4_model_contract.md`](../work/models/q4_model_contract.md)
- [`work/models/q5_model_contract.md`](../work/models/q5_model_contract.md)
- [`work/05_experiment_plan.md`](../work/05_experiment_plan.md)
- [`experiments/s2_frozen_config.json`](../experiments/s2_frozen_config.json)
- [`logs/decisions.md`](../logs/decisions.md)
- [`logs/experiments.md`](../logs/experiments.md)
- [`logs/ai_usage.md`](../logs/ai_usage.md)
- [`CURRENT.md`](../CURRENT.md)

S1 基础证据仍为：`work/01_problem_analysis.md`、`work/02_data_audit.md`、`work/03_requirement_matrix.md` 和 `results/raw/s1/`。

## Main Claims

1. Q1–Q5 已形成同一条“只读输入→统一特征/折→Baseline→有限候选→OOF 证据→冻结预测→Q5 联合域 Pareto”的技术主线。
2. 每问都有可快速实现的 Baseline、针对性主候选、数学定义、变量和单位、目标、约束、参数、求解过程、评价、失败条件与预期产物。
3. 所有输入均来自题面附件或前序 Q4 冻结模型，不依赖不存在的外部核心变量。
4. `B_m` 主口径冻结为 `max(abs(B))`，`B_pp/2` 为敏感性；频率保留实测值，Q5 主域采用题面 50–500 kHz，实测边界作为敏感性。
5. 完全重复同折；近形状组和工况组算法在拟合前冻结。外层最多 5 折、内层 3 折，覆盖失败只降折数，不退回随机行切分。
6. Q1 主分类只用波形形状；温度、频率、材料只能进入代理依赖消融，不能替代真实形状。
7. Q2 以传统 SE 为 Baseline，主修正是可解释的二次温度乘性因子；只允许一个预定义交互升级。
8. Q3 控制 $f/B_m$ 后估计调整后关联和两两交互，使用 effect coding、共同支持与簇 Bootstrap，禁止因果措辞。
9. Q4 使用 Ridge 对数回归 Baseline、HistGradientBoosting 主候选和 RandomForest 挑战者；不堆叠，未满足增益/子组阈值就回退。
10. Q5 主路线枚举附件一实测联合状态并做非支配排序，每个候选具备 Q4 所需的完整波形；不使用逐变量 min/max 笛卡尔积或无依据启发式算法。
11. 附件二、三继续锁定为相应模型冻结后的单次预测用途。
12. 方案按当前无 GPU 的 16 逻辑 CPU 机器即可执行；S3 Baseline 约 2 小时，S4 候选串行上限 8 小时，单作业硬上限 120 分钟。

## G1 Follow-up Closure

| Reviewer G1 follow-up | S2 executable control | Evidence |
|---|---|---|
| 近重复与分组验证 | 固定 near-shape 签名、condition group、折数回退和同组不跨折断言 | solution §3；shared contract |
| 材料3单条重复 | 主流程保留且同折；S4 做删除敏感性 | solution §3.1；Q2/Q3/Q4 contracts |
| 频率可行域 | 原值保留；Q5 名义域主结果、实测域敏感性 | solution §2.2/§6；Q5 contract |
| `B_m` 定义 | `max(abs(B))` 主口径，`B_pp/2` 敏感性 | solution §2.2；shared/Q2/Q5 contracts |
| Q1 辅助字段代理 | 主模型 shape-only，辅助字段只作消融与留一材料压力 | Q1 contract |
| Q2/Q4 长尾评价 | RMSLE 主指标，MAE/RMSE/MAPE/MdAPE 和分组残差辅助 | solution §5；Q2/Q4 contracts |
| Q5 联合可行域 | 实测行枚举、完整波形输入、跨折 Pareto 稳定性 | solution §6；Q5 contract |

## Baseline and Upgrade Gates

- S3 必须先完成 8 个 Baseline/数据实验，形成五问闭环；任何 Baseline 失败优先修复，不跳到复杂候选。
- Q1 非线性候选必须提高 Macro-F1 且不损害类别 Recall。
- Q2 修正必须降低总体 RMSLE，且至少 3/4 温度不劣化。
- Q3 交互必须有 OOF 增量和 Bootstrap 稳定性，否则回退加性或描述统计。
- Q4 非线性候选须使 RMSLE 相对 Ridge 改善至少 2%，且主要子组不恶化超过 10%。
- Q5 候选跨折 Pareto 入选率低于 50% 时，不给唯一推荐。

## Static Verification Performed

```text
model_contract_structure=PASS count=5
config_and_hashes=PASS
Markdown_links=PASS
sklearn=1.7.1; cpu_count=16; planned_apis=PASS
```

检查内容包括：五份合同的 14 个必需章节、冻结 JSON 可解析、五个输入 SHA 与 S1 profile 一致、本地 Markdown 链接有效，以及 GroupKFold、StratifiedGroupKFold、SplineTransformer、HistGradientBoosting、RandomForest 和 ParameterSampler API 可导入。

## Known Limitations

1. S2 仅冻结设计；`build_features.py`、`run_q1.py` 至 `run_q5.py` 是 G2 PASS 后在 S3 实现的预期 CLI，目前没有宣称它们已经存在。
2. 尚未产生任何训练、OOF、附件预测、Pareto 或 `results/verified/` 模型结果。
3. 近形状分组数量、共同支持比例和实际运行时间只能在 S3 首个数据实验中确认；合同已定义失败和回退路径。
4. Q5 连续搜索默认关闭；实测域枚举本身是完整 Baseline，只有额外条件满足才可提交修订合同扩展。
5. 当前仍无 GPU，但所有主路线均按 CPU 可执行；不以未验证 A800 为前提。

## Reviewer Verification Suggestions

```powershell
$config = Get-Content projects/rehearsal_2024_C/experiments/s2_frozen_config.json -Raw | ConvertFrom-Json
$config.plan_version
Get-ChildItem projects/rehearsal_2024_C/work/models/q*_model_contract.md
git diff --check
git status --short
git rev-parse HEAD
```

Reviewer 应同时读取 G2 协议列出的三份 S1 文档，检查模型是否真实回答原题、所需输入是否存在，以及最后一问是否可执行。

## Requested Verdict

`PASS`。若 Reviewer 认可方案可落地且合同足以安全实现，请授权 `S2 → S3`，下一 Gate 为 G3。若有问题，请按 Critical/Major/Minor 分类并给出可复核的 Required Fixes；Main Agent 不自行宣布 G2 通过。
