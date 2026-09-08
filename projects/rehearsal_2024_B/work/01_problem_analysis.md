# S1 Problem Analysis

## 1. Scope and evidence

- [FACT] 题目为 2024 年中国研究生数学建模竞赛 B 题《WLAN组网中网络吞吐量建模》。
- [FACT] 本文只拆解问题、数据边界和验证需求，不选择最终模型、不调参、不对四个官方测试集做探索性分布比较。
- [FACT] 直接证据为题面 DOCX、[输入清单](../problem/manifest.md)、[数据审计](02_data_audit.md)及 [S1 机器证据](../results/raw/s1/audit_summary.md)。
- [FACT] 原始观测按“某次测试中的某个 AP”逐行记录；同一 source_file + test_id 下有 2 或 3 行，分别构成完整的 2 AP 或 3 AP 场景。
- [INFERENCE] 建模原子可以是 AP 行，但切分、特征聚合和误差分析必须以完整测试组为边界。

## 2. 三问依赖关系

~~~text
测试基本信息 + 拓扑/RSSI/门限
           |
           +--> Q1: 发送机会影响分析 + seq_time 预测
           |                    |
           |                    +--> 仅以 OOF/推理预测形式传给下游
           |
           +--> Q2: (MCS, NSS) 联合类别预测
           |
           +--> Q3: throughput 预测
                    可使用 Q1 预测；题面明确允许真实 MCS/NSS
~~~

- [FACT] Q2 要求“结合问题 1 中对 AP 发送机会的分析”。
- [FACT] Q3 要求结合问题 1 和问题 2 的分析，但题面同时明确允许将实测真实 MCS/NSS 作为 Q3 输入。
- [RISK] 如果下游训练直接使用 Q1 的训练集内拟合值，会产生堆叠泄漏；只能使用折外预测。
- [RISK] Q3 的 MCS/NSS 许可不能反向授权 Q1/Q2 使用真实标签，也不能扩展到 PER、num_ampdu、ppdu_dur、other_air_time 等其他事后字段。

## 3. 问题 1：发送机会影响分析与 seq_time 预测

### 3.1 目标与输出

- [FACT] 解释网络拓扑、业务流量、门限和节点间 RSSI 等参数对 AP 发送机会的影响，并给出影响强弱顺序。
- [FACT] 发送机会用 AP 发送帧序列的总时长 seq_time 表征，单位为秒。
- [FACT] 对 test_set_1_2ap 的 80 行和 test_set_1_3ap 的 105 行逐 AP 输出预测 seq_time，共 185 个预测值。
- [INFERENCE] 因一次测试时长 test_dur=60 s，seq_time 的物理合理区间应为 0 到 test_dur；最终预测需要边界检查，但截断规则须在验证中比较后再冻结。

### 3.2 可用信息与禁用信息

- [FACT] 候选基本信息包括 test_dur、protocol、pkt_len、pd、ed、nav、eirp，以及可从列表型 RSSI 计算的稳健统计和相对信号/门限关系。
- [INFERENCE] AP 数量应作为分层建模条件或统一模型的显式结构变量；组内 AP/STA 相对关系可由标识符构造，但 MAC、test_id、source_file 和 loc_id 不直接作为可记忆的类别特征。
- [FACT] nss、mcs、per、num_ampdu、ppdu_dur、other_air_time、seq_time、throughput 及 predict/error 占位列均为标签、事后统计或输出，Q1 输入中禁用。
- [RISK] test_dur、pkt_len、pd、ed 在训练候选中均为常数，不能从本样本识别其影响强弱；论文必须把这种“不可识别”与“影响小”区分开。
- [RISK] 影响性排序是样本内预测关联与稳定性结论，不能写成无实验支撑的因果关系。

### 3.3 未知量与评价

- [UNKNOWN] 题面未给出官方评分函数、提交精度或并列处理方式。
- [INFERENCE] 内部验证至少报告按完整测试组切分的 MAE、RMSE、R²，并按 2/3 AP、loc、nav、protocol 分层；必要时增加相对误差，但对接近零目标单独处理。
- [INFERENCE] 影响排序候选证据包括跨折置换重要性、消融增量和方向一致性；最终采用哪一种在 S2/G2 决定。
- [RISK] RSSI 列是长度变化的列表，直接把原字符串或列表长度当作信号强弱会混淆采样数量与信号水平。

## 4. 问题 2：最常用 (MCS, NSS) 预测

### 4.1 目标与输出

- [FACT] 预测 AMC 过程中使用次数最多的联合类别 (MCS, NSS)，而不是瞬时 PHY Rate 序列。
- [FACT] 对 test_set_2_2ap 的 64 行和 test_set_2_3ap 的 87 行逐 AP 输出 predict mcs、predict nss，共 151 组联合预测。
- [FACT] 训练候选中 NSS 分布为 0:3、1:26、2:1221；联合类别明显不平衡，(2,11) 单类有 604/1250 行。

### 4.2 可用信息与禁用信息

- [FACT] 基本候选输入仍为业务/门限/RSSI 与分组拓扑信息。
- [INFERENCE] 可评估联合多分类与分层分类两种表示，但必须以“联合类别完全命中”作为核心结果之一，避免单独预测后组合出训练中不存在的类别。
- [INFERENCE] 如使用 Q1 的发送机会信息，训练阶段只能使用 Q1 折外 seq_time 预测，推理阶段使用对应 Q1 模型预测。
- [FACT] 真实 nss/mcs 及其派生 PHY Rate、PER、其他事后统计、真实 seq_time 和 throughput 禁止作为 Q2 输入。
- [RISK] 三条 (NSS,MCS)=(0,0) 可能是失败状态或异常，S1 不改值；S2 必须比较保留与排除的敏感性后再冻结类别合同。

### 4.3 评价

- [UNKNOWN] 官方分类计分规则未在题面说明。
- [INFERENCE] 内部核心指标采用联合 exact-match accuracy、macro-F1、balanced accuracy，并补充 MCS/NSS 分量准确率和混淆矩阵。
- [RISK] 仅报告普通 accuracy 会被占主导的 NSS=2 和 (2,11) 类掩盖。

## 5. 问题 3：吞吐量预测

### 5.1 目标与输出

- [FACT] 预测 test_set_1_2ap 与 test_set_1_3ap 的逐 AP throughput，共 185 个值，单位 Mbps。
- [FACT] test_set_1_* 已提供每行真实 nss、mcs、per，但题面明确授权 Q3 使用的只有真实 MCS/NSS。
- [FACT] Q3 测试行的 seq_time 和 throughput 为空，因此真实 seq_time 在推理时不可用。

### 5.2 可用信息与禁用信息

- [FACT] 可用基本输入为业务/门限/RSSI/拓扑信息，加题面许可的真实 nss、mcs。
- [INFERENCE] 若使用发送机会，训练阶段必须使用 Q1 折外 seq_time，推理阶段使用 Q1 的 test_set_1 预测。
- [INFERENCE] “结合 Q2”可通过 MCS/NSS 与 SINR/传输方式关系、分层误差分析或与 Q2 预测的敏感性对照体现；由于 test_set_1 已给真实 MCS/NSS，不应为了形式依赖而用较差的 Q2 预测替代真实值。
- [FACT] per、num_ampdu、ppdu_dur、other_air_time、真实 seq_time、throughput 和全部预测占位列禁用。
- [RISK] 训练候选有 5 条 throughput=0，MAPE 在零分母处无定义，不能作为唯一或无保护的指标。

### 5.3 评价与约束

- [UNKNOWN] 官方回归计分规则未给出。
- [INFERENCE] 内部至少报告 MAE、RMSE、R²，以及带明确定义 epsilon 的相对误差作为辅助；零吞吐量样本单列绝对误差。
- [INFERENCE] 吞吐量预测应非负；是否裁剪及上界设定必须以分组验证比较为依据。

## 6. 共同验证与外推合同

- [FACT] 原始训练共有 1,252 行；隔离 A01 两个不完整组后有 1,250 行，且所有剩余 source_file + test_id 组均完整。
- [FACT] 四个官方测试集只做列存在性、缺失模式和输出空白检查，不使用其特征分布选择规则或模型。
- [INFERENCE] 主候选为 GroupKFold 或重复分组留出，groups 使用 source_file + test_id，所有预处理在训练折内拟合。
- [INFERENCE] 压力测试包括 leave-one-source-file-out、条件允许时 leave-one-loc_id-out，以及按 AP 数、loc、nav、protocol 分层汇报。
- [RISK] source_file 与 loc/nav/AP 数高度耦合，普通随机分组验证仍可能乐观；场景留出用于衡量外推落差。
- [RISK] 2 AP 与 3 AP 的 RSSI 列数不同；分别建模与统一的掩码/集合聚合表示都只是 S2 候选，当前不冻结。

## 7. 交付与成功判据

| 问题 | 必交输出 | 内部可验收证据 | 当前状态 |
|---|---|---|---|
| Q1 | 参数影响强弱与方向说明；185 个 seq_time | 分组回归指标、跨折重要性/消融稳定性、物理边界检查 | S1 已定义，待 S2 实现 |
| Q2 | 151 组 predict mcs/nss | 联合与分量指标、macro 指标、混淆矩阵、A03 敏感性 | S1 已定义，待 S2 实现 |
| Q3 | 185 个 throughput | 分组回归指标、零值处理、OOF 链路审计、分层外推结果 | S1 已定义，待 S2 实现 |

## 8. 仍待确认事项

- [UNKNOWN] 官方最终评分函数和预测文件数值格式。
- [UNKNOWN] 原始压缩包的稳定授权来源、总哈希和官方逐文件哈希。
- [UNKNOWN] training_set_3ap_loc33_nav88.csv 文件名与内容 loc_id=loc4 不一致时，官方原意究竟是哪一个位置标签。
- [UNKNOWN] 三条 (NSS,MCS)=(0,0) 的业务语义。
- [UNKNOWN] 数据审计、代码、建模和最终提交的团队成员实名；当前由 Main Agent/Codex 执行仓库工作，最终提交责任必须由人类队员承担。
