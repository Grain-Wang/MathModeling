# S1 Requirement Matrix

## 1. Purpose and status

本矩阵把题面要求、模型输入/输出、内部验证和证据文件连接起来。模型族均为 S2 待比较候选，不代表已选定；G1 Round 2 PASS 前不得进入 S2。

状态含义：

- DEFINED：S1 已冻结需求和验收证据。
- DEFERRED_TO_S2：G1 PASS 后通过预注册比较决定。
- UNKNOWN：现有题面或授权材料未提供，不自行补造。

## 2. Functional requirements

| ID | 题面/治理要求 | 输入与键 | 必交输出 | 验证/验收证据 | 主要风险 | 状态 |
|---|---|---|---|---|---|---|
| R01 | Q1 分析各参数对 AP 发送机会的影响并排序 | 基本信息、RSSI、AP 结构；禁全部事后字段 | 有方向、强弱、稳定性和不可识别项说明的排序 | 严格分组折重要性、特征族消融、方向检查 | 把关联写成因果；常量字段误称无影响 | DEFINED |
| R02 | Q1 预测 seq_time | AP 键 source_file + test_id + ap_id | test_set_1 的 185 个逐 AP seq_time | Group MAE/RMSE/R²、边界、分层；下游只用 OOF/推理预测 | AP 行跨折；RSSI 预处理泄漏 | DEFINED |
| R03 | Q2 预测最常用联合类别 (MCS,NSS) | 基本信息、RSSI，可选 Q1 OOF；禁真实标签、PER 和真实 seq_time | test_set_2 的 151 组 predict mcs/nss | 固定全局标签集 exact accuracy、macro-F1、balanced accuracy、分量准确率、support 和混淆矩阵 | 稀有类缺折、非法组合、Q1 训练内预测泄漏 | DEFINED |
| R04-AP | Q3 预测每 AP throughput | AP 键 source_file + test_id + ap_id；真实 nss/mcs 特许；禁 PER 等事后字段 | test_set_1 的 185 个逐 AP throughput，Mbps | 1,250 个 eligible 训练 AP 目标可构造、无缺失 | 真实 seq_time 泄漏；零真实值相对误差无定义 | DEFINED |
| R04-SYS | Q3 给出系统吞吐量 | 系统键 source_file + test_id；仅在严格完整组内聚合 | 75 个系统 throughput，等于同组全部 AP 预测之和，Mbps | 482 个训练系统目标可构造；2 AP 196 组、3 AP 286 组；测试 40+35 组 | 缺 AP、重复 AP 或跨文件聚合 | DEFINED |
| R04-METRIC-AP | Q3 AP 级误差 CDF 和 90% 精度 | 只用 AP 粒度有定义真实值 | signed r=(预测-实测)/实测；经验 CDF；最近秩 ERROR_90；accuracy_90=1-ERROR_90 | 5 个零分母预先排除并披露；1,245 个正分母；绝对误差单列 | 用绝对值替换题面有符号公式；结果后改分位规则 | DEFINED |
| R04-METRIC-SYS | Q3 系统级误差 CDF 和 90% 精度 | 只用严格系统组；真实和预测分别组内求和 | 独立 signed CDF、最近秩 ERROR_90、accuracy_90 | 482 个系统分母均正；与 AP 指标分开报告 | 混合两级样本；用通用回归指标代替题面指标 | DEFINED |
| R05 | 可按 AP 数分别或统一建模 | 2 AP/3 AP schema 与掩码 | 明确选择及同切分对照 | 分层指标、复杂度和稳定性 | 不同列数硬拼；总体平均掩盖 3 AP 退化 | DEFERRED_TO_S2 |
| R06 | 所有组和导出身份严格正确 | 系统键 source_file + test_id；AP 键再加 ap_id | 行数、精确 AP 集合/次数、复合键唯一均通过 | identity_checks.json；eligible 482/482、测试 136/136 strict pass | 重复某 AP 且缺另一个 AP 仍伪装行数完整 | DEFINED |
| R07 | 原始输入不可改写且 CSV 不上传 | 17 个本地 CSV + manifest | 只提交脚本、哈希和非 CSV 证据 | 审计前后 17/17 哈希 PASS；git ls-files 无 CSV | 换机缺数据；迎合损坏输入修改 manifest | DEFINED |
| R08 | A01–A06 处理可复现 | 精确来源键和异常字段 | 原始/eligible 数量、原因、处理和敏感性合同 | quality_checks.json、决策日志 | 静默删行/填补；把 UNKNOWN 当事实 | DEFINED |
| R09 | 重复检查作用域和防泄漏策略明确 | eligible 训练；同 AP 数分层 | 文件内全列重复和跨文件规范化行/组 SHA-256 指纹 | 当前文件内 0 行、跨文件行簇 0、组簇 0；未来整簇同折 | 跨文件等价观测导致验证乐观 | DEFINED |
| R10 | 官方测试集封存 | 四个测试集 | 仅最终推理和格式校验 | 当前只输出 schema、dtype、缺失/非空、严格身份 | 预览数值分布后调规则或模型 | DEFINED |
| R11 | 结果可复现 | 固定 commit、环境、命令、哈希 | 机器 JSON、摘要和实验日志 | 干净 commit 正式审计；运行前后输入哈希 | 远程无 CSV；环境尚未 clean rebuild | DEFINED |
| R12 | 外部数据可追溯 | 当前无外部数据 | 若后用则记录 URL、许可、版本/哈希、日期和无外部数据消融 | provenance 与对照结果 | 许可不明或外部答案泄漏 | DEFINED |
| R13 | 论文符合 2024 官方提交规范 | 官方模板、规则、提交清单 | 匿名正文、摘要、PDF、命名与最终 MD5 | competition/2024 提交检查 | 身份泄露、格式错误、MD5 后变更 | DEFINED |

## 3. Q3 executable metric contract

AP 和系统两级必须分别执行，不混合样本：

1. 误差小数 r_i = (yhat_i - y_i) / y_i，error_i(%) = 100r_i，方向为有符号且不取绝对值；
2. F(x) = count(r_i ≤ x) / n；
3. 将有定义的 r_i 升序，ERROR_90 取一基序号 ceil(0.90n) 的值，不插值；
4. 并列观测全部保留，仍按固定最近秩位置取值；
5. accuracy_90 = 1 - ERROR_90，百分数为 100(1-ERROR_90)，不裁剪；
6. y_i=0 从相对 CDF/ERROR_90 排除并披露数量，另报绝对误差；
7. 绝对相对误差 CDF、MAE、RMSE、R²、偏差只作辅助，不得替代题面主指标。

系统真实值和预测值分别由同一严格 source_file + test_id 组的全部 AP 值求和。任何身份检查失败的组不得静默进入系统指标。

## 4. Data-to-question mapping

| 数据族 | Q1 | Q2 | Q3 | 理由 |
|---|---:|---:|---:|---|
| protocol、eirp、nav 等变化基本量 | Allow | Allow | Allow | 题面测试基本信息 |
| test_dur、pkt_len、pd、ed | Allow with caveat | Allow with caveat | Allow with caveat | 当前训练恒定，只可作边界/公式量 |
| AP 数与组内相对拓扑 | Allow | Allow | Allow | 题面允许按 AP 数分模 |
| 原始 ID、MAC、source_file、loc_id | Key/stratum only | Key/stratum only | Key/stratum only | 直接作为类别会记忆场景或设备 |
| RSSI 折内稳健统计、门限差、SINR 候选 | Allow | Allow | Allow | 题面强调节点间 RSSI、门限和 SINR |
| nss、mcs | Forbid | Label only | Allow actual | 真实值只获 Q3 明确特许 |
| Q1 seq_time 预测 | Target | OOF optional | OOF/inference optional | 训练内预测禁止向下游传递 |
| per | Forbid | Forbid | Forbid | Q3 特许未覆盖 PER |
| num_ampdu、ppdu_dur、other_air_time | Forbid | Forbid | Forbid | 事后统计，测试推理时不可用 |
| true seq_time | Label only | Forbid | Forbid | Q3 只能使用预测替代 |
| throughput | Forbid | Forbid | AP/system label | 目标及严格组求和目标 |
| predict、error 占位列 | Forbid | Forbid | Forbid | 输出占位，不是推理输入 |

## 5. Validation matrix

| Evidence ID | Split unit / scope | Used for | Metrics and mandatory diagnostics | Freeze point |
|---|---|---|---|---|
| V01 | source_file + test_id grouped K-fold 或重复 grouped holdout | 主内部比较 | Q1 通用回归；Q2 固定标签分类；Q3 AP/系统 signed CDF、ERROR_90、accuracy_90 为主，绝对 CDF 和通用回归为辅 | S2 预注册 |
| V02 | leave-one-source-file-out | 强制场景外推压力测试 | 与 V01 同口径，另报相对退化率；不得因结果不佳省略 | S2 必做 |
| V03 | leave-one-loc_id-out，样本允许时 | 位置外推 | 与 V01 同口径；A06 单列 | S2 |
| V04 | AP 数、loc、nav、protocol 分层 | 弱点定位 | 样本数、点估计、折间波动 | S2 |
| V05 | A03 保留/排除；A05 对应整组保留/排除 | 异常敏感性 | 主指标差值和预测变化 | S2 |
| V06 | 下游有/无 Q1 OOF 预测 | 依赖贡献 | Q2/Q3 主指标与计算成本 | S2 |
| V07 | 2/3 AP 分模与统一模型 | 结构选择 | 同切分分层指标、稳定性和复杂度 | S2 |
| V08 | 严格身份和重复簇 | 所有训练/验证切分及系统聚合 | 同组 AP 不跨折；未来等价重复簇整体同折 | 已冻结 |
| V09 | 最终导出 dry-run | 提交正确性 | 行数、键、精确 AP 集合、顺序、空值、有限数、范围、哈希 | S4/S6 |

- 所有预处理必须在训练折内拟合。
- 同一 source_file + test_id 的 AP 行永不跨折。
- 模型比较使用同一切分清单，避免切分噪声冒充改进。
- Q2 全局联合标签全集及排序、缺类失败/回退、固定标签集 macro-F1、每类 support 和 A03 敏感性必须在 S2 首次训练前预注册。
- 官方测试集不能用于特征、阈值、超参数或模型选择。

## 6. Anomaly acceptance matrix

| ID | 当前动作 | S2 必做对照 | 自动修改原件 |
|---|---|---|---:|
| A01 两个不完整组 | 按 source_file + test_id 隔离 2 行 | 报样本量，不恢复伪组 | No |
| A02 三个 RSSI 列全空 | 保留缺失和掩码 | 缺失感知 vs 去除方向 | No |
| A03 三条 (0,0) | 暂保留 | 保留 vs 排除 | No |
| A04 schema 差异 | 派生层规范化 | 输出占位排除断言 | No |
| A05 两个 other_air_time 超时长 | 字段无效、行暂保留 | 如相关则整组保留 vs 排除 | No |
| A06 filename loc33 / content loc4 | 内容 loc4 + source_file 场景键 | loc4 分层单列 | No |
| A07 跨文件等价重复簇 | 当前未触发；若触发登记全簇 | 整簇同折；删除敏感性 | No |

## 7. G1 Round 2 acceptance checklist

- [x] Q1–Q3 输入、输出、依赖、禁用字段和未知量已定义。
- [x] Q3 分为 AP 级 185 个预测和系统级 75 个求和预测，键、单位和训练数量明确。
- [x] AP/系统两级 signed CDF、最近秩 ERROR_90、accuracy_90、零分母和并列规则唯一可执行。
- [x] MAE/RMSE/R²和绝对相对误差仅标为辅助。
- [x] eligible 训练和四个测试集均通过行数、精确 AP 身份集合/次数、复合键唯一三重检查。
- [x] A01 两个异常组单列；其余身份空值、非法值和复合键重复均为 0。
- [x] 重复结论明确区分文件内全列与跨文件规范化行/组指纹，当前三项均为 0。
- [x] 17 个 CSV 正式审计前后固定哈希通过，原件不变且继续被 Git 忽略。
- [x] 测试集保持分布封存，未用于选择。
- [x] leave-one-source-file-out 和 Q2 稀有类合同登记为 S2 初期强制事项。
- [ ] 团队实名责任分配仍待用户提供，属 Reviewer 已列的非阻断 Minor。
- [ ] 全新环境 clean rebuild 尚未完成，安排在正式比赛前。
- [ ] Q1/Q2 官方评分函数和最终预测格式未见于现有材料，保持 UNKNOWN。

## 8. Stage boundary

G1 Round 2 PASS 前禁止：

- 选择最终主模型或开展正式模型比较、调参和测试预测；
- 修改 A01–A06、Q3 指标、身份或重复合同而不更新决策与证据；
- 使用官方测试数值分布反向调整任何规则；
- 自行创建或修改 reviews/gate_1_review_r2.md；
- 宣称已经进入 S2。

G1 Round 2 PASS 后，S2 第一项工作是预注册 V01–V08 的切分、随机种子、Q2 全局标签、Q3 两级指标、基线和失败规则，再运行模型。
