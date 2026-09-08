# S1 Requirement Matrix

## 1. Purpose

本矩阵把题面要求、模型输入/输出、内部验证和证据文件连接起来。模型族均为 S2 待比较候选，不代表已经选定。

状态含义：

- DEFINED：S1 已明确需求与验收证据。
- DEFERRED_TO_S2：需在 G1 PASS 后通过基线/消融实验决定。
- UNKNOWN：题面或现有授权材料未提供，不能自行补造。

## 2. Functional requirements

| ID | 题面/治理要求 | 输入边界 | 必交输出 | S2 初始候选，不冻结 | 验证/验收证据 | 主要风险 | S1 状态 |
|---|---|---|---|---|---|---|---|
| R01 | Q1 分析各参数对 AP 发送机会的影响并排序 | 业务、门限、RSSI 稳健统计、AP 结构；禁用全部事后字段 | 有方向、强弱、稳定性和不可识别项说明的排序 | 机理派生特征 + 可解释树模型/正则模型；置换、消融、方向检查 | 分组折上的重要性分布；去除特征族后的指标变化；常量字段单列 | 把关联写成因果；常量字段被误称为不重要 | DEFINED |
| R02 | Q1 预测 seq_time | 与 R01 相同 | test_set_1 的 185 个逐 AP seq_time | 常数/规则基线、线性/树回归；2/3 AP 分模与统一表示对照 | Group MAE、RMSE、R²；分 AP 数/loc/nav/protocol；0–test_dur 边界 | AP 行跨折；RSSI 列表处理泄漏；测试集调参 | DEFINED |
| R03 | Q2 结合发送机会预测最常用 (MCS,NSS) | 基本信息 + RSSI；可选 Q1 OOF 预测；禁用真实 nss/mcs、PER、真实 seq_time 等 | test_set_2 的 151 组 predict mcs/nss | 联合多分类与分层分类对照；类别权重作为候选 | 联合 exact accuracy、macro-F1、balanced accuracy、分量准确率、混淆矩阵 | 类别不平衡；组合出非法类别；使用 Q1 训练内预测 | DEFINED |
| R04 | Q3 结合 Q1/Q2 分析预测 throughput | 基本信息、RSSI、真实 nss/mcs 特许、Q1 OOF/推理预测；禁 PER 和其他事后字段 | test_set_1 的 185 个逐 AP throughput | 机理基线、线性/树回归；有无 Q1 预测对照 | Group MAE、RMSE、R²；零值绝对误差；分层外推；OOF 链路审计 | 真实 seq_time 泄漏；把 MCS/NSS 特许扩展到 PER；MAPE 零分母 | DEFINED |
| R05 | 可按 AP 数分别或统一建模 | 2 AP/3 AP schema 与掩码 | 明确选择及对照结果 | 分模；统一模型 + AP 数/集合聚合，两者都评估 | 同一分组切分下总体与分层指标、复杂度和稳定性 | 不同列数硬拼；只报总体平均掩盖 3 AP 退化 | DEFERRED_TO_S2 |
| R06 | 输出必须与原测试行一一对应 | source_file + test_id + ap_id 对齐键 | 不改行序、列名可追溯的预测表 | 单独 export 层 | 行数、键唯一性、空值、有限数、范围、输入哈希检查 | 排序/连接错位；覆盖原始 CSV | DEFINED |
| R07 | 原始输入不可改写且 CSV 不上传 | 17 个本地 CSV + manifest | 脚本、哈希和非 CSV 证据进入 Git | 只读加载；派生物写 results | 审计前后 17/17 SHA-256 PASS；git ls-files 无 CSV | 换机缺数据；误更新哈希迎合损坏文件 | DEFINED |
| R08 | 异常处理必须可复现 | A01–A06 | 行键、原因、前后数量、字段/整组策略 | 敏感性与消融在 S2 实现 | quality_checks.json + decisions log + S2 对照实验 | 静默删行/填补；把未知语义当事实 | DEFINED |
| R09 | 测试集封存 | 四个官方测试集 | 仅最终预测和格式校验 | 无模型候选 | 代码审计证明没有用测试分布做选择 | 预览分布后手工改规则形成间接泄漏 | DEFINED |
| R10 | 结果可复现 | 固定 commit、环境、随机种子、参数 | 运行命令、环境和机器可读结果 | 统一实验入口在 S2 建立 | Git SHA、ISO 8601 时间、环境版本、输入/输出哈希 | 本机可跑但远程无原始数据；环境未 clean rebuild | DEFINED |
| R11 | 外部数据可追溯 | 当前无外部数据 | 如后用则记录 URL/版本/许可/哈希/日期 | 必须有无外部数据消融 | provenance 文件与对照结果 | 许可不明或外部信息泄漏测试答案 | DEFINED |
| R12 | 论文满足 2024 官方提交规范 | 官方模板、规则和提交清单 | 匿名正文、摘要、PDF、命名与最终 MD5 | 后续写作阶段执行 | competition/2024/submission checklist | 身份泄露、模板错误、MD5 后变更 | DEFINED |

## 3. Data-to-question mapping

| 数据族 | Q1 | Q2 | Q3 | 理由 |
|---|---:|---:|---:|---|
| protocol、eirp、nav 等有变化基本量 | Allow | Allow | Allow | [FACT] 题面称为测试基本信息 |
| test_dur、pkt_len、pd、ed | Allow with caveat | Allow with caveat | Allow with caveat | [FACT] 当前训练中恒定；可用于边界/公式但不能学习样本内影响 |
| AP 数与组内相对拓扑 | Allow | Allow | Allow | [FACT] 题面允许按 AP 数分模；[INFERENCE] 统一模型需显式结构 |
| 原始 ID/MAC/source_file/loc_id | Key/stratum only | Key/stratum only | Key/stratum only | [RISK] 直接使用会记忆场景或设备 |
| RSSI 列表的折内稳健统计、门限差、SINR 候选 | Allow | Allow | Allow | [FACT] 题面强调节点间 RSSI、门限和 SINR 关系 |
| nss、mcs | Forbid | Label only | Allow actual | [FACT] Q3 唯一明确特许；Q1/Q2 使用会泄漏 |
| Q1 seq_time 预测 | Target | OOF optional | OOF/inference optional | [RISK] 训练内拟合值禁止传给下游 |
| per | Forbid | Forbid | Forbid | [FACT] Q3 许可未覆盖 PER |
| num_ampdu、ppdu_dur、other_air_time | Forbid | Forbid | Forbid | [FACT] 事后统计，测试推理时为空 |
| true seq_time | Label only | Forbid | Forbid | [FACT] Q3 测试时为空；只能用预测替代 |
| throughput | Forbid | Forbid | Label only | 目标泄漏边界 |
| predict *、error* | Forbid | Forbid | Forbid | 空占位/结果字段 |

## 4. Validation matrix

| Evidence ID | Split unit | Used for | Metrics/diagnostics | Freeze point |
|---|---|---|---|---|
| V01 | source_file + test_id grouped K-fold/repeated holdout | 主内部比较 | Q1/Q3: MAE, RMSE, R²；Q2: exact accuracy, macro-F1, balanced accuracy | S2 预注册后固定 |
| V02 | leave-one-source-file-out | 场景外推压力 | 同 V01 + 相对退化率 | S2 |
| V03 | leave-one-loc_id-out，样本允许时 | 位置外推 | 同 V01；A06 单独披露 | S2 |
| V04 | 按 AP 数、loc、nav、protocol 分层 | 弱点定位 | 样本数、点估计、折间波动 | S2 |
| V05 | A03 保留/排除；A05 对应整组保留/排除 | 异常敏感性 | 主要指标差值与预测变化 | S2 |
| V06 | 下游有/无 Q1 OOF 预测 | 依赖贡献 | Q2/Q3 主要指标与计算成本 | S2 |
| V07 | 分模与统一模型 | 结构选择 | 分层指标、稳定性、复杂度 | S2 |
| V08 | 最终导出 dry-run | 提交正确性 | 行数、键、顺序、空值、范围、哈希 | S4/S6 |

- [FACT] 所有预处理必须位于折内；同一测试组的 AP 行不能跨折。
- [INFERENCE] 模型比较必须共享完全相同的切分清单，避免切分噪声被误认为模型改进。
- [UNKNOWN] 官方评分函数未给出；内部指标组合不应被表述为官方计分规则。

## 5. Anomaly acceptance matrix

| ID | 当前动作 | S2 必做对照 | 允许自动修改原件 |
|---|---|---|---:|
| A01 两条错位/不完整组 | 隔离 test_id 40、41，共 2 行 | 无需恢复；报告样本量 | No |
| A02 三个 RSSI 列全空 | 保留缺失和掩码 | 缺失感知 vs 去除该方向 | No |
| A03 三条 (0,0) | 暂保留 | 保留 vs 排除 | No |
| A04 schema 差异 | 派生层规范化 | 输出列排除断言 | No |
| A05 两个 other_air_time 超时长 | 字段置缺失、行暂保留 | 对应整组保留 vs 排除（如相关） | No |
| A06 filename loc33 / content loc4 | 内容 loc4 + source_file 双键 | loc4 分层结果单列 | No |

## 6. Gate G1 acceptance checklist

- [x] Q1–Q3 的输入、输出、依赖、禁用字段、未知量和候选评价方式已逐项定义。
- [x] 17 个 CSV 在正式审计前后通过固定哈希；原件未改变。
- [x] 字段族、单位、RSSI 列表解析、缺失机制和 schema 差异已记录。
- [x] A01–A06 有精确证据与冻结处理合同。
- [x] 训练/测试层级、分组验证、场景压力测试和 OOF 链路已定义。
- [x] 四个官方测试集保持封存，未用于分布驱动的选择。
- [x] 审计代码与 JSON/Markdown 证据可跟踪，CSV 继续被忽略。
- [ ] 团队成员实名责任分配：用户尚未提供；作为 G0 已认可的非阻断 Minor 保留。
- [ ] 官方评分函数和发布包校验：现有材料未给出，保持 UNKNOWN。

## 7. Stage boundary

G1 PASS 前禁止：

- 选择或宣称最终主模型；
- 开展正式模型比较、调参或测试集预测；
- 修改 A01–A06 合同而不更新决策日志和审计证据；
- 使用测试集分布反向调整任何规则；
- 进入 S2 之外的论文结论撰写。

G1 PASS 后，S2 应先预注册 V01–V07 的切分、种子、指标和基线，再运行任何比较实验。
