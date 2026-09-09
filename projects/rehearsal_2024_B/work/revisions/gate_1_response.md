# Gate 1 Round 2 Response

## 1. Review metadata

- Gate：G1
- Response Round：2
- Round 1 Reviewed Commit：512e461033c8378f1e591912b4992d8486bde396
- Round 1 Review Commit：e9253ce15a7b296298cf68c61b65357b55f1a1ed
- Round 1 Verdict：REVISE
- Formal Audit Implementation Commit：03ac99d91004fca2123011a3db29043d5612568c
- Formal Audit Time：2026-09-09T10:36:50+08:00
- Current Stage：S1
- S1 → S2：NOT AUTHORIZED，等待 G1 Round 2 独立审核

Round 1 审核见 [gate_1_review.md](../../reviews/gate_1_review.md)。本轮只修复 M1-01、M1-02 并登记三个 Minor 的后续约束；未拟合模型、调参或生成官方测试预测。

## 2. Outcome summary

| 审核项 | 修订结果 | 核心证据 |
|---|---|---|
| M1-01 Q3 输出与评价遗漏 | 已修订 | AP 185、系统 75；两级 signed CDF、ERROR_90、accuracy_90 合同已冻结 |
| M1-02 身份与重复证据不足 | 已修订 | eligible 482/482、测试 136/136 严格组通过；文件内重复 0、跨文件行/组簇 0 |
| Minor-01 Q2 稀有类别 | 已登记 S2 强制预注册 | 固定全局标签集、排序、缺类规则、固定标签 macro-F1、support、A03 敏感性 |
| Minor-02 场景外推 | 已升级为 S2 必做 | leave-one-source-file-out 不再是可选实验 |
| Minor-03 实名与 clean rebuild | 保留非阻断待办 | 团队实名待用户提供；正式比赛前 clean rebuild |

## 3. M1-01 response：Q3 系统吞吐量、CDF 与 90% 精度

### 3.1 Required Fix mapping

| Required Fix | 实现 |
|---|---|
| 1. 提取完整 Q3 要求 | [问题分析](../01_problem_analysis.md) §5 和 [需求矩阵](../03_requirement_matrix.md) R04-AP、R04-SYS、R04-METRIC-AP、R04-METRIC-SYS 分别登记 AP 目标、系统目标、两级 CDF 和 90% 精度。 |
| 2. 明确系统聚合 | 题面文字明确“所有 AP 吞吐之和”，因此登记为 FACT：同一严格 source_file + test_id 组内，真实 AP throughput 求和得到真实系统量，预测 AP throughput 求和得到预测系统量，单位 Mbps。 |
| 3. 冻结粒度与数量 | eligible 训练为 1,250 个 AP 目标与 482 个系统目标，其中 2 AP 196 组、3 AP 286 组；Q3 测试为 185 个 AP 输出与 75 个系统输出，其中 40 个 2 AP 组、35 个 3 AP 组。 |
| 4. 冻结误差、CDF、分位和零值 | 主误差 r=(预测-实测)/实测；F(x)=count(r≤x)/n；ERROR_90 为升序后一基第 ceil(0.90n) 项，不插值；并列保留；accuracy_90=1-ERROR_90 且不裁剪；真实值为 0 时排除相对 CDF 并披露，绝对误差单列。 |
| 5. 同步材料与机器审计 | 已更新 work/01–03、src/s1_data_audit.py、logs/decisions.md，并新增 q3_target_contract.json；正式审计验证系统目标可构造性和零分母。 |

### 3.2 Acceptance Criteria evidence

- Q3 不再等同于 185 个 AP 回归值；独立包含 75 个系统求和输出。
- AP 键为 source_file + test_id + ap_id，系统键为 source_file + test_id，单位均为 Mbps。
- 两级使用同一唯一可执行主指标，但分别构造样本和 CDF，不混合粒度。
- eligible 训练 AP 目标无缺失：5 个零分母、1,245 个正分母。
- 482 个系统目标无缺失、零分母为 0，范围 77.33–618.67 Mbps。
- 有符号题面口径可能导致 accuracy_90 超过 100% 或为负；合同规定不裁剪，并同时报告绝对相对误差 CDF、偏差及 MAE/RMSE/R²辅助诊断。
- 绝对相对误差和通用回归指标不能替代题面 signed CDF、ERROR_90 和 accuracy_90。

机器证据：[q3_target_contract.json](../../results/raw/s1/q3_target_contract.json)。

## 4. M1-02 response：严格身份、复合键与跨文件重复

### 4.1 Required Fix mapping

| Required Fix | 实现 |
|---|---|
| 1. 复合身份断言 | 对 source_file、test_id、ap_id 执行非空检查；ap_id 合法格式检查；source_file + test_id + ap_id 唯一性检查。 |
| 2. 精确 AP 集合 | 原始训练、A01 后 eligible 训练、官方测试合计、Q3 测试和每个测试文件均检查预期行数、精确 AP ID 集合及每个 ID 恰出现一次。 |
| 3. 机器可读输出 | identity_checks.json 输出空/非法身份数、重复复合键数及示例、异常组数及示例、严格有效组数和 strict_pass。 |
| 4. 重复范围 | 文件内对每个训练文件全部原始列做完全重复；跨文件在同 AP 数分层内，对共有语义字段做规范化 SHA-256 行指纹和按 ap_id 排序的组指纹。 |
| 5. 重跑审计与哈希 | 从干净 03ac99d 提交正式运行；17/17 输入在运行前后均 PASS，input_hashes_unchanged_during_audit=true。 |

### 4.2 Strict identity results

| 范围 | AP 行 | 组 | 严格有效 | 严格无效 | 空/非法 ID | 重复复合键 |
|---|---:|---:|---:|---:|---:|---:|
| 原始训练 | 1,252 | 484 | 482 | 2，均为 A01 | 0 | 0 |
| eligible 训练 | 1,250 | 482 | 482 | 0 | 0 | 0 |
| 官方测试 | 336 | 136 | 136 | 0 | 0 | 0 |
| Q3 测试 | 185 | 75 | 75 | 0 | 0 | 0 |

四个测试文件分别为 40/40、35/35、32/32、29/29 组 strict pass。A01 的两个原始异常组仍按既定合同整组隔离，其他组没有 AP 身份缺失、替换或重复。

### 4.3 Duplicate results and policy

- 文件内全部原始列完全重复：0 行。
- 2 AP 跨文件规范化：392 个唯一行指纹、196 个唯一组指纹，重复行簇 0、重复组簇 0。
- 3 AP 跨文件规范化：858 个唯一行指纹、286 个唯一组指纹，重复行簇 0、重复组簇 0。
- 指纹排除 provenance 键和 predict/error 占位列；缺失值、稳定数字、RSSI 标量与单元素列表采用确定性规范化；使用 UTF-8 JSON 的 SHA-256。
- 若未来发现等价簇，不静默删除；整个簇绑定到同一验证折，考虑删除时必须报告敏感性。当前结果为 0，因此没有触发 A07。

机器证据：[identity_checks.json](../../results/raw/s1/identity_checks.json)；完整质量合同见 [quality_checks.json](../../results/raw/s1/quality_checks.json)。

## 5. Minor issue disposition

### Minor-01

[问题分析](../01_problem_analysis.md) §4 和 [需求矩阵](../03_requirement_matrix.md) V01 已要求在 S2 首次训练前固定 Q2 联合标签全集与排序、缺类失败/回退、固定标签集 macro-F1、每类 support 以及 A03 保留/排除敏感性。

### Minor-02

leave-one-source-file-out 已在问题分析、数据审计、需求矩阵 V02 和机器 validation_contract 中设为 S2 强制压力测试；不得根据结果好坏选择性省略。

### Minor-03

团队实名仍需用户提供，环境 clean rebuild 安排在正式比赛前。两项维持 Reviewer 定义的非阻断 Minor，不伪造完成状态。

## 6. Formal audit and verification

正式审计命令：

~~~powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s1_data_audit.py --verify-only
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s1_data_audit.py
~~~

正式结果：

~~~text
input_verification=PASS
expected_csv=17 actual_csv=17
audit_status=PASS_WITH_WARNINGS
raw_training_rows=1252
eligible_training_rows=1250
test_rows=336
strict_groups=482 train, 136 test
cross_file_duplicate_clusters=0 row, 0 group
~~~

机器元数据显示 git_head=03ac99d91004fca2123011a3db29043d5612568c，git_status_porcelain_before_outputs 为空。官方测试证据仍仅包含结构、非空计数和身份检查，没有数值分布摘要。

## 7. Changed artifacts

- [01_problem_analysis.md](../01_problem_analysis.md)
- [02_data_audit.md](../02_data_audit.md)
- [03_requirement_matrix.md](../03_requirement_matrix.md)
- [s1_data_audit.py](../../src/s1_data_audit.py)
- [audit_summary.md](../../results/raw/s1/audit_summary.md)
- [data_profile.json](../../results/raw/s1/data_profile.json)
- [quality_checks.json](../../results/raw/s1/quality_checks.json)
- [identity_checks.json](../../results/raw/s1/identity_checks.json)
- [q3_target_contract.json](../../results/raw/s1/q3_target_contract.json)
- [decisions.md](../../logs/decisions.md)
- [experiments.md](../../logs/experiments.md)
- [CURRENT.md](../../CURRENT.md)

## 8. Requested disposition

请对新的远程固定 SHA 执行 G1 / Review Round 2。Main Agent 不自行宣布 PASS；在 reviews/gate_1_review_r2.md 明确授权前，项目保持 S1，S1 → S2 为 NOT AUTHORIZED。
