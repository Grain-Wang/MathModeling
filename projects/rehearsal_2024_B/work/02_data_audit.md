# S1 Data Audit

## 1. Audit verdict

PASS_WITH_WARNINGS：本地数据足以支持 S2 方案设计，但在 G1 Round 2 通过前仍停留在 S1；A01–A06、严格身份、重复簇和泄漏合同必须继续执行。

- [FACT] 审计脚本：[src/s1_data_audit.py](../src/s1_data_audit.py)。
- [FACT] 正式审计基于干净实现提交 affff4fa6ef2d9a5431adac6e7341c993b946f4d 运行；机器元数据必须显示该 HEAD 且运行前工作树为空。
- [FACT] 17/17 CSV 在审计前后均通过固定文件名、字节数和 SHA-256 校验，且输入哈希在运行中不变。
- [FACT] 13 个训练文件共 1,252 行、484 组；A01 隔离后 1,250 行、482 个严格完整组。4 个测试文件共 336 行、136 个严格完整组。
- [FACT] 完整组定义为：预期行数正确、精确 AP 身份集合及次数正确、复合行键 source_file + test_id + ap_id 唯一且身份字段非空合法。
- [FACT] 机器证据：
  - [data_profile.json](../results/raw/s1/data_profile.json)：文件结构、训练分布与运行元数据；
  - [quality_checks.json](../results/raw/s1/quality_checks.json)：完整质量、异常、泄漏和验证合同；
  - [identity_checks.json](../results/raw/s1/identity_checks.json)：严格身份和重复指纹；
  - [q3_target_contract.json](../results/raw/s1/q3_target_contract.json)：Q3 两级目标可构造性和正式指标合同；
  - [audit_summary.md](../results/raw/s1/audit_summary.md)：人类可读摘要。
- [RISK] 原始 CSV 被 Git 忽略，远程 Reviewer 只能核对脚本、manifest 和非 CSV 证据，无法在没有授权数据副本时重跑。

复现命令：

~~~powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s1_data_audit.py --verify-only
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s1_data_audit.py
~~~

## 2. 输入规模与组结构

| 数据范围 | AP 行 | source_file + test_id 组 | 严格有效组 | 严格无效组 |
|---|---:|---:|---:|---:|
| 原始训练 | 1,252 | 484 | 482 | 2 |
| A01 后 eligible 训练 | 1,250 | 482 | 482 | 0 |
| 官方测试合计 | 336 | 136 | 136 | 0 |
| Q3 测试 test_set_1 | 185 | 75 | 75 | 0 |

| 分层 | eligible 训练 AP 行 / 组 | 官方测试 AP 行 / 组 |
|---|---:|---:|
| 2 AP | 392 / 196 | 144 / 72 |
| 3 AP | 858 / 286 | 192 / 64 |

四个测试文件分别通过严格身份检查：

| 文件 | AP 行 | 严格组 |
|---|---:|---:|
| test_set_1_2ap.csv | 80 | 40 |
| test_set_1_3ap.csv | 105 | 35 |
| test_set_2_2ap.csv | 64 | 32 |
| test_set_2_3ap.csv | 87 | 29 |

- [FACT] test_id 会在不同 source_file 中重复；系统键必须是 source_file + test_id，AP 行键必须再加 ap_id。
- [FACT] A01 位于 training_set_2ap_loc2_nav82.csv：test_id 40、41 各只有一条错位 ap_1 行，故按整组隔离 2 行；原 CSV 不改。

## 3. 严格身份审计

每个范围均执行以下可机读断言：

1. source_file、test_id、ap_id 非空；
2. ap_id 符合 ap_数字 格式；
3. source_file + test_id + ap_id 复合键唯一；
4. 2 AP 组恰含 ap_0、ap_1 各一次；
5. 3 AP 组恰含 ap_0、ap_1、ap_2 各一次；
6. 预期组内行数同时正确。

| 范围 | 空 source_file | 空 test_id | 空 ap_id | 非法 ap_id | 重复复合键 | AP 集合/次数或行数异常组 | strict_pass |
|---|---:|---:|---:|---:|---:|---:|---:|
| 原始训练 | 0 | 0 | 0 | 0 | 0 | 2 | No，原因仅为 A01 |
| eligible 训练 | 0 | 0 | 0 | 0 | 0 | 0 | Yes |
| 官方测试合计 | 0 | 0 | 0 | 0 | 0 | 0 | Yes |
| Q3 测试 | 0 | 0 | 0 | 0 | 0 | 0 | Yes |

- [FACT] 因此“482 个完整训练组”是三重身份结论，不是仅凭行数得出。
- [RISK] 后续任何 join、组内特征、系统吞吐量聚合和导出都必须先复用同一严格身份断言。

## 4. 重复范围与稳定内容指纹

- 文件内检查：对每个训练 CSV 的全部原始列执行完全重复检查，13 个文件合计 0 行。
- 跨文件检查：只在相同 AP 数分层内比较 eligible 训练观测；取该分层各文件共有的语义字段，排除 source_file、test_id 和 predict/error 占位列，统一缺失表示和稳定数值文本，并把 RSSI 标量与单元素列表规范到相同表示。
- 行指纹：对规范化字段的确定性 UTF-8 JSON 计算 SHA-256。
- 组指纹：按 ap_id 排序组合组内行指纹，再计算 SHA-256。

| AP 分层 | 行数 / 组数 | 唯一行指纹 | 唯一组指纹 | 跨文件重复行指纹簇 | 跨文件重复组指纹簇 |
|---|---:|---:|---:|---:|---:|
| 2 AP | 392 / 196 | 392 | 196 | 0 | 0 |
| 3 AP | 858 / 286 | 858 | 286 | 0 | 0 |
| 合计 | 1,250 / 482 | 1,250 | 482 | 0 | 0 |

- [FACT] “重复为 0”现在明确区分文件内全列完全重复和跨文件规范化等价重复。
- [INFERENCE] 若未来派生数据发现重复簇，不静默删除；整簇绑定到同一验证折，考虑删除时必须报告敏感性。

## 5. 字段、单位与训练侧分布

- seq_time、ppdu_dur、other_air_time、test_dur：s。
- throughput：Mbps；PER：无量纲且训练非空值均在 [0,1]。
- RSSI、pd、ed、eirp：dBm；pkt_len：byte；nav：μs。
- nss、mcs 是 Q2 标签；只有 Q3 可按题面特许使用真实 nss/mcs。
- test_dur、pkt_len、pd、ed 在 eligible 训练中恒定，无法从当前样本经验识别其影响。
- Q2 eligible 标签：NSS 为 0:3、1:26、2:1221；联合类别存在一例 (2,2) 和三例 (0,0)，S2 必须固定全局标签集、缺类规则和 A03 敏感性。

训练 RSSI 解析共得到列表 25,797 个、标量 2,120 个、缺失 5,699 个、非法文本 4 个；非法和 12 个范围越界值均来自 A01 错位行。测试集只报告结构和非空计数，不输出数值分布。

## 6. A01–A06 冻结处理

| ID | 证据 | 冻结动作 |
|---|---|---|
| A01 | 两个不完整 2 AP 组、共 2 行 | 在派生训练中按组隔离，原件不改 |
| A02 | training_set_3ap_loc30_nav86.csv 三个 RSSI 列全空 | 保留缺失，不臆造反向链路；S2 做缺失处理消融 |
| A03 | 三条 (NSS,MCS)=(0,0) 且目标非空 | 暂保留，不改为 NSS=1；S2 报保留/排除敏感性 |
| A04 | schema alias、空预测列、重复 error 表头 | 只在派生层规范化；所有输出占位列禁作特征 |
| A05 | 两个 other_air_time 远超 60 s | 对该字段视为无效；目标行保留，必要时做整组敏感性 |
| A06 | 文件名 loc33 与内容 loc4 不一致 | 原件不改；用内容 loc4，source_file 保留为场景键，官方原意 UNKNOWN |

当前没有触发 A07；A07 仅在跨文件规范化重复簇数量大于 0 时登记。

## 7. Q3 两级目标可构造性

| 粒度 | 键 | eligible 训练数量 | Q3 测试输出数量 | 单位 |
|---|---|---:|---:|---|
| 每 AP throughput | source_file + test_id + ap_id | 1,250 | 185 | Mbps |
| 系统 throughput | source_file + test_id | 482 | 75 | Mbps |

- [FACT] 题面明确系统吞吐量为同一完整组所有 AP 吞吐量之和。真实和预测都必须在严格组内分别求和。
- [FACT] 482 个训练系统目标均可构造、无缺失、均大于 0，范围 77.33–618.67 Mbps。
- [FACT] AP 目标无缺失，其中 5 个为 0、1,245 个大于 0。

AP 与系统两级分别执行唯一指标合同：

1. 主误差为有符号相对误差 r = (预测 - 实测) / 实测，百分数为 100r；
2. 经验 CDF 为 F(x)=count(r≤x)/n；
3. ERROR_90 为 r 升序后的一基第 ceil(0.90n) 项，不插值；
4. 并列值全部保留，固定位置取值；
5. accuracy_90 = 1 - ERROR_90，百分数乘 100，不裁剪；
6. 实测为 0 时从相对 CDF 和 ERROR_90 排除、披露数量，并单独报告绝对误差；
7. 绝对相对误差 CDF、MAE、RMSE、R²只作辅助，不能替代题面主指标。

该合同在看到模型结果前冻结；有符号误差可能使精度超过 100% 或为负，必须原样披露并辅以偏差和绝对相对误差诊断。

## 8. 泄漏、验证与测试封存

- 原子切分组为 source_file + test_id；同组所有 AP 行不得跨折。
- 主内部比较候选为 GroupKFold 或重复分组留出，所有预处理在训练折内拟合。
- leave-one-source-file-out 是 S2 强制压力测试；leave-one-loc_id-out 在可行时补充。
- Q1 预测传给 Q2/Q3 时，训练阶段必须为折外预测。
- Q1 禁用全部事后字段；Q2 禁真实标签和事后字段；Q3 只额外许可真实 nss/mcs，不扩展到 PER 等字段。
- 官方测试集只用于最终推理与导出；当前只审计 schema、dtype、缺失/非空和身份，不用数值分布选择规则或模型。

## 9. 充分性与剩余风险

- [FACT] 完成 A01 隔离后，三个问题的训练目标、严格组、身份键和 Q3 系统目标均可构造。
- [FACT] 没有 Critical 数据失败，结论为 PASS_WITH_WARNINGS。
- [UNKNOWN] Q1/Q2 官方评分函数、最终预测文件格式、A03 业务语义和 A06 官方位置原意。
- [RISK] 环境尚未 clean rebuild；团队实名责任分配尚待人类队员补充。
- [BOUNDARY] 本审计没有拟合模型、调参或生成官方测试预测；G1 Round 2 PASS 前不得进入 S2。
