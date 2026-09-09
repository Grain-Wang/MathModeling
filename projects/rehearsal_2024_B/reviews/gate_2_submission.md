# Gate 2 Submission

## Submission Metadata

- Project: rehearsal_2024_B
- Gate: G2
- Stage: S2 — 总体方案与模型合同
- Prior Gate Verdict: G1 Round 2 PASS
- Prior Review Commit: fd6e33b4fa9a7f2de4764ff52272cd62ff52a45b
- Formal Contract-Validation Commit: 6b88cd1eb6a4776b12b77b859f01d7b8cfaf9a39
- O1 Decision: PROCEED_TO_G2
- Review Target: 推送完成后的 origin/main 完整 SHA，由交接消息提供
- Expected Review: reviews/gate_2_review.md

## Requested Review Scope

1. 统一技术路线是否完整回答 Q1、Q2、Q3，并以可审计的 OOF Q1 预测闭合 Q1→Q2/Q3 数据流。
2. 三份模型合同是否完整冻结 Problem、Inputs、Outputs、Variables and Units、Assumptions、Mathematical Definition、Objective、Constraints、Parameters、Training / Solving Procedure、Baseline、Evaluation、Failure Conditions 与 Expected Artifacts。
3. 是否严格以 source_file+test_id 为原子分组；所有可学习预处理是否限定在当前训练折；嵌套选择和跨问 cross-fitting 是否无泄漏。
4. 强制 LOSO、Q2 固定 17 类/缺类回退、Q3 AP/系统两级有符号指标和系统严格求和是否充分。
5. 候选规模、时间盒、成功/停止条件和回退是否足够约束后续实验。
6. O1 的 PROCEED_TO_G2 是否有充分证据；是否可授权 S2→S3。

## Deliverables

- [Unified solution plan](../work/04_solution_plan.md)
- [Q1 model contract](../work/models/q1_model_contract.md)
- [Q2 model contract](../work/models/q2_model_contract.md)
- [Q3 model contract](../work/models/q3_model_contract.md)
- [Experiment plan](../work/05_experiment_plan.md)
- [Machine-readable experiment contract](../configs/s2_experiment_plan.json)
- [O1 solution optimization](../work/optimization/o1_solution_optimization.md)
- [Contract-validation script](../src/s2_contract_validation.py)
- [Contract-validation summary](../results/raw/s2/contract_summary.md)
- [Complete contract-validation evidence](../results/raw/s2/contract_validation.json)
- [Frozen split registry](../results/raw/s2/split_registry.json)

## Key Assertions

- NAV 数据列已按题目 4.1.3 唯一解释为 dBm 阈值，不是 μs 静默时长；机制特征使用 RSSI 与 pd/ed/nav 阈值的 dB 差。
- A01 后训练总体为 1,250 个 AP 行、482 个严格组；Q1/Q3 AP 输出 185 行，Q2 输出 151 行，Q3 系统输出 75 组。
- 外层评估固定为 3 个随机种子的 5 折 GroupKFold，共 15 折和 1,446 个组分配。
- 每个外层训练集固定 3 折内层选择，共 5,784 个组分配；预处理、Q1 cross-fitting 与下游训练均限制在相应训练边界。
- 场景外推必须另报 13 折 leave-one-source_file-out，不得用普通 grouped CV 代替。
- Q2 固定为 17 个按数值排序的 nss|mcs 联合标签；某训练折缺类时该类概率为 0，并用全局标签 macro-F1、support 与失败回退披露。
- Q3 题面 PHY-rate 表已固定；主指标按有符号相对误差、经验 CDF、最近秩 ERROR_90 和未裁剪 accuracy_90 执行，同时报告绝对相对误差与常规回归指标。
- Q3 系统预测恒等于同一严格组内 AP 预测之和；不设置独立系统头。
- 主要非线性候选统一为 HGB，固定 4 点小网格；Q3 只比较直接头与物理残差头，总候选预算为 8。
- 正式合同校验来自干净提交 6b88cd1e；输入校验前后均 PASS 且哈希不变。
- 正式校验计数：eligible rows/groups 1,250/482，外层折 15，外层/内层分配 1,446/5,784，LOSO 13，Q2 全局标签 17，Q3 合成指标测试 PASS。
- Split registry core SHA-256: E1DE3911D78140DB8F3A3342F7982959EB28FBA85DCFB3AF09AE990BBAC5D704。
- model_fit_count=0；official_test_numeric_read_count=0。没有调参、模型比较或官方测试预测。
- 所有原始 CSV 继续由 /projects/**/*.csv 忽略，未进入 Git；S2 机器证据使用 JSON/JSONL/Markdown，不新增 CSV。

## Reproduction

在仓库根目录、已有 math_modeling Conda 环境中：

```powershell
conda run -n math_modeling python -m py_compile projects/rehearsal_2024_B/src/s2_contract_validation.py
conda run -n math_modeling python projects/rehearsal_2024_B/src/s2_contract_validation.py --verify-only
```

完整写出命令只应在工作区干净且 HEAD 为正式校验提交时执行：

```powershell
conda run -n math_modeling python projects/rehearsal_2024_B/src/s2_contract_validation.py
```

## Known Limitations

- 原始 CSV 不随仓库上传；Reviewer 需按 problem/data/README.md 与 manifest 在本地恢复并验证。
- 团队成员实名责任分配尚待提供，不影响当前技术合同，但必须在最终交付前补齐。
- environment.yml 尚未完成全新环境 clean rebuild；当前 math_modeling 环境的已记录导入 smoke 为 PASS。
- Q2 含极稀有联合类；合同已经冻结缺类行为、固定标签指标、A03 敏感性和仅在 O2 证据触发时允许的一次有界权重候选。
- 普通主 CV 不代表新 source 场景外推；13 折 LOSO 是不可省略的单独证据。

## Boundary

G2 Reviewer 给出 PASS 前：

- Current Stage 保持 S2，S2→S3 未获授权；
- 不拟合正式 Baseline，不比较模型性能，不调参；
- 不读取官方测试集数值分布，不生成官方测试预测；
- Main Agent 不创建或修改 reviews/gate_2_review.md；
- 若结论为 REVISE 或 BLOCK，只在 Reviewer 指定边界内修订并重新提交。
