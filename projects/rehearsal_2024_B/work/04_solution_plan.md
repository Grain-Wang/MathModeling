# S2 Unified Solution Plan

## 1. Metadata and boundary

- Project：rehearsal_2024_B
- Stage：S2 — 总体方案与模型合同
- Authorized by：G1 Round 2 PASS，review commit fd6e33b4fa9a7f2de4764ff52272cd62ff52a45b
- Next Gate：G2
- Status：方案冻结候选；尚未拟合任何预测模型

本阶段只定义可执行路线、切分、评价和失败回退。G2 PASS 前不运行正式 Baseline、模型比较、调参或官方测试预测。

## 2. Unified technical line

~~~text
17 CSV 固定哈希与严格身份
        |
        +--> A01 整组隔离，得到 1,250 AP 行 / 482 系统组
        |
        +--> 统一的拓扑感知 RSSI 特征引擎 Phi
        |       - focal AP / associated STA 对齐
        |       - 同组 peer 链路的置换不变聚合
        |       - PD、ED、NAV 门限裕量
        |       - 折内缺失处理、编码与缩放
        |
        +--> Q1：发送机会分析 + seq_time 回归
        |       - OOF seq_time 作为唯一合法下游训练输入
        |
        +--> Q2：联合 (NSS,MCS) 分类
        |       - 基本信息 + RSSI + 可选 Q1 OOF
        |       - 固定 17 类和缺类回退
        |
        +--> Q3：AP throughput
                - 基本信息 + RSSI + Q1 OOF/推理
                - 真实 (NSS,MCS) 特许 -> 题面 PHY Rate
                - 物理容量代理 + 受约束残差
                - 组内 AP 预测求和 -> system throughput
                - AP/system 两级 signed CDF 与 ERROR_90
~~~

三问共享同一数据身份、同一特征引擎、同一外层切分注册表和同一非线性候选族。模型头因目标类型不同而使用回归或分类损失，但不是互不相干的算法堆叠。

## 3. Approved facts and task sizes

| Task | Training unit | Eligible size | Official output size | Unit / label |
|---|---|---:|---:|---|
| Q1 seq_time | AP row | 1,250 | 185 | s |
| Q2 joint class | AP row | 1,250 | 151 | 17 个固定 (NSS,MCS) 类 |
| Q3 AP throughput | AP row | 1,250 | 185 | Mbps |
| Q3 system throughput | strict group | 482 | 75 | Mbps，组内 AP 求和 |

- AP 行键：source_file + test_id + ap_id。
- 系统组键和不可拆分验证原子：source_file + test_id。
- A01 两个不完整组共 2 行不进入训练或模型选择。
- loc_id、source_file、MAC、名称和原始 AP/STA ID 只作键、分层或列对齐，不作可记忆模型特征。
- 官方测试集只做哈希、schema、身份和最终推理/导出；其数值分布、空白目标和预测均不能驱动选择。

## 4. NAV unit resolution

题目正文区分两种概念：

1. NAV 时段：MAC 头指示其他节点静默的持续时间；
2. NAV 门限：AP 是否完成接收并更新 NAV 的 RSSI 判决门限。

题目数据介绍 4.1.3 明确写明 nav (dBm): NAV门限。故本项目数据列 nav 的唯一合同为 dBm 门限，不是 μs 时长。训练侧批准证据中的档位为 -82、-86、-88 dBm。

S2 使用的机制量为：

$$
m^{NAV}_{ij}=Q_{0.50}(RSSI^{mean}_{AP_j\to AP_i})-NAV_i，
$$

大于 0 表示该 peer 链路的典型平均天线 RSSI 高于 NAV 门限。该量是判决裕量和预测特征，不被写成已确认的因果效应。

## 5. Shared feature engine

令第 g 个完整测试组中 AP i 的原始可用信息为 x_ig，统一特征为：

$$
z_{ig}=\Phi(x_{ig},\{x_{jg}:j\ne i\})。
$$

### 5.1 Deterministic parsing

每个 RSSI 单元按 S1 解析合同转为数值序列；不从官方测试分布学习规则。每个可用序列计算：

- median、q10、q90、IQR；
- valid_count；
- missing_indicator。

不把列表长度直接解释为信号强弱。

### 5.2 Focal/peer alignment

利用 ap_id、sta_id 只做列对齐：

- AP_i 接收 AP_j：ap_from_ap_j，j≠i；
- AP_i 接收关联 STA_i：sta_to_ap_i；
- 关联 STA_i 接收目标 AP_i：sta_from_ap_i；
- 关联 STA_i 接收其他 AP_j 或 STA_j：j≠i。

对 peer 链路使用 strongest、weakest、mean、available_count、missing_fraction 聚合，使 2 AP 与 3 AP 进入同一固定维度空间。原始身份编号不进入模型。

### 5.3 Mechanism-derived features

- CCA/PD 裕量：peer AP max-ant RSSI 分位数减 pd；
- CCA/ED 裕量：peer AP max-ant RSSI 分位数减 ed；
- NAV 裕量：peer AP mean-ant RSSI 分位数减 nav；
- desired-to-strongest-peer RSSI 差；
- 高于各门限的 peer 数、比例与最强裕量；
- AP 数、协议、eirp、同组 peer eirp 差和 TCP peer 数；
- test_dur、pkt_len、pd、ed 只保留作公式与外推警告，因为训练中为常量。

这些量把题面载波侦听、NAV 和干扰关系编码成可验证预测特征，但不宣称从观测数据识别出因果机制。

### 5.4 Learned preprocessing

- 数值缺失：训练折中位数 + 缺失指示；
- protocol 和 AP 数：one-hot，未知类别忽略；
- Ridge/LogisticRegression：训练折拟合标准化；
- 树模型：使用相同输入字段和缺失指示，不使用全数据统计；
- 任一外层/内层/LOSO 分割均重新拟合上述步骤。

A02 的结构性全空方向保留缺失指示，不合成反向链路。

## 6. Q1 route

目标为 seq_time，表示 60 s 测试中 AP 发送数据帧序列总时长。

### Baseline

- Q1-B0：训练折中位数 DummyRegressor；
- Q1-B1：Ridge，alpha=1.0，共享特征管道。

### Main candidate

HistGradientBoostingRegressor 表达门限裕量、协议、AP 数和 RSSI 间的低阶非线性交互。候选只来自机器配置中的 4 个固定组合，禁用内置随机 early stopping，避免内部随机样本切分破坏组边界。

预测物理边界为 0≤seq_time≤test_dur；验证同时保存 raw 与 bounded 预测并报告裁剪比例。

### Sending-opportunity analysis

影响结论采用三类 held-out 证据交叉验证：

1. 特征族消融造成的 MAE/RMSE 变化；
2. 验证折内按完整组置换的特征族重要性；
3. Ridge 系数或受控响应曲线的方向、折间秩和符号稳定性。

只写“预测贡献/条件关联”。若方向在三个重复中不足两个一致，或排名稳定性不足，标为不稳定，不生成强排序。

## 7. Q2 route

目标是一个固定联合类别 c=(NSS,MCS)，不是两个无约束独立输出。

### Fixed label space

按 NSS、MCS 数值升序冻结 17 类：

~~~text
0|0
1|0, 1|4, 1|5, 1|6, 1|7, 1|9
2|2, 2|3, 2|4, 2|5, 2|6, 2|7, 2|8, 2|9, 2|10, 2|11
~~~

任一新观察标签使流程硬失败。某训练折缺少的类别在该折概率补零且不能被预测；概率向量始终重索引到 17 类。macro-F1 对固定 17 类计算，zero_division=0，并披露每类 support 和缺类列表。

### Baseline and main

- Q2-B0：训练折多数联合类；
- Q2-B1：C=1 的多项 LogisticRegression；
- 主候选：HistGradientBoostingClassifier，多分类 log loss。

输入为共享基本/RSSI特征和可选的 Q1 交叉拟合 seq_time。Q1 训练内拟合值、真实 seq_time、真实 nss/mcs、PER 和其他事后字段全部禁止。

A03 的 0|0 在主分析保留；另做对应完整组排除敏感性。只有 O2 发现少数类完全坍缩时，才允许一次上限为 5 的平方根逆频率权重候选。

## 8. Q3 route

### 8.1 Q1/Q2 linkage

Q3 使用：

- 共享 z_ig；
- 对训练行为严格交叉拟合的 Q1 seq_time，推理时使用 Q1 预测；
- 题面明确许可的真实 nss/mcs；
- 题面 20 MHz 映射表得到的 PHY Rate R_i。

Q3 不以 Q2 预测替代 test_set_1 已给出的真实 nss/mcs。它通过 AMC/PHY Rate 关系使用 Q2 所建模的速率状态知识。

### 8.2 Physics baseline

定义容量代理：

$$
p_i=\frac{\widehat{s}_i}{test\_dur_i}R(nss_i,mcs_i)。
$$

在每个训练折内估计唯一效率系数：

$$
\widehat{\eta}
=\operatorname{clip}_{[0,1]}
\frac{\sum_i p_i y_i}{\sum_i p_i^2}，
\qquad
\widehat y_i^{phy}=\widehat{\eta}p_i。
$$

若分母为 0 则 Q3-B2 失败并回退 Q3-B1。0|0 没有题面 PHY Rate，主分析保留该行并设置 rate_missing，另做完整组排除敏感性。

### 8.3 Main candidate

比较两个受限架构：

1. direct HGB：直接预测 throughput，并把 p_i、Q1 预测和 PHY Rate 作为特征；
2. residual HGB：预测物理基线残差，
   yhat_i=max(0,yhat_i_phy+f_3(z_i,p_i))。

系统预测没有独立模型头，始终满足：

$$
\widehat Y_g=\sum_{i\in g}\widehat y_i。
$$

因此 AP 输出和系统输出在代数上完全一致。任何严格身份失败的组不得聚合。

### 8.4 Metric

AP 和系统分别计算题面 signed error、经验 CDF、最近秩 ERROR_90 和 accuracy_90。模型选择不直接最大化可能奖励系统性低估的 signed accuracy，而最小化两级绝对相对误差 90% 分位的较大者，并以 signed median bias 作约束；题面 signed 指标仍是必须报告的主结果。

## 9. Cross-fitting and leakage control

对每个外层验证折：

1. 只用外层训练组拟合特征学习步骤；
2. 在外层训练组内部按固定 3-fold registry 产生 Q1 cross-fitted 预测；
3. 用这些预测训练 Q2/Q3；
4. 用整个外层训练组重拟合 Q1，预测外层验证组；
5. Q2/Q3 对外层验证组给出预测；
6. 保存键、repeat、fold、真实值、预测、缺类和预处理哈希。

外层验证组从不进入上游 Q1、下游模型、插补器、编码器、超参数选择或效率系数估计。

## 10. Validation and model promotion

- 主估计：3×5 repeated GroupKFold，组为 source_file + test_id；
- 内层选择：每个外层训练集固定 3-fold GroupKFold；
- 强制外推：13 个 leave-one-source-file-out；
- 置信区间：按完整组 bootstrap 1,000 次；
- 分层：AP 数、loc、nav、protocol，仅用于诊断；
- 官方测试：所有选择冻结后一次推理，不产生验证分数。

主候选必须超过对应结构 Baseline 的预注册阈值；否则回退 Baseline。任何额外候选须由 O2 的实际失败证据授权，不能在 S2 预先无限扩张。

## 11. Computational feasibility

数据仅 1,250 AP 行、482 组，固定特征维度和最多 16 个主配置。HGB、Ridge 和 LogisticRegression 均可在当前 CPU 环境运行；不依赖 GPU，单张 A800 充分。估算的模型拟合量由 15 个外层折、每折 3 个内层折和固定候选预算控制。若单问主候选计算超过计划时间盒 2 倍，停止扩张并回退已跑通 Baseline。

工程上复用一个 feature builder、一个 split registry、一个指标库和三个薄模型头，主要由一名建模/代码成员可维护。

## 12. Stage deliverables and stop point

S2 冻结：

- 本总体方案；
- 三份模型合同；
- 实验计划与机器配置；
- 训练组外/内层切分注册表；
- Q3 合成指标测试；
- O1 方案优化决定；
- G2 submission。

在 G2 Reviewer 给出 PASS 前停止，不进入 S3，不拟合预测模型。
