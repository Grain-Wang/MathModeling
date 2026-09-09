# S1 Problem Analysis

## 1. Scope and evidence

- [FACT] 题目为 2024 年中国研究生数学建模竞赛 B 题《WLAN组网中网络吞吐量建模》。
- [FACT] 本文只冻结问题、数据和评价合同，不选择最终模型、不调参、不生成正式测试预测。
- [FACT] 直接证据为题面 DOCX、[输入清单](../problem/manifest.md)、[数据审计](02_data_audit.md)和 [S1 机器证据](../results/raw/s1/audit_summary.md)。
- [FACT] 观测行为“某次测试中的某个 AP”；AP 行键为 source_file + test_id + ap_id，系统组键为 source_file + test_id。
- [FACT] “完整组”同时满足预期行数、精确 AP 身份集合/次数和复合行键唯一，不再只按行数判断。

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
           +--> Q3: 每 AP throughput
                    |
                    +--> 同组所有 AP throughput 求和 = 系统 throughput
                    |
                    +--> AP/系统两级 signed-error CDF 与 90% 精度
~~~

- [FACT] Q2 要求结合 Q1 对发送机会的分析。
- [FACT] Q3 要求结合 Q1/Q2；题面明确允许真实 MCS/NSS 作为 Q3 输入。
- [RISK] 下游训练直接使用 Q1 训练内拟合值会泄漏，只能使用折外预测。
- [RISK] Q3 的 MCS/NSS 许可不能反向授权 Q1/Q2，也不能扩展到 PER、num_ampdu、ppdu_dur、other_air_time 或真实 seq_time。

## 3. 问题 1：发送机会影响分析与 seq_time 预测

### 3.1 目标与输出

- [FACT] 解释网络拓扑、业务、门限和节点间 RSSI 等参数对 AP 发送机会的影响并排序。
- [FACT] 发送机会以 AP 发送帧序列总时长 seq_time 表征，单位 s。
- [FACT] test_set_1_2ap 有 80 行、test_set_1_3ap 有 105 行，共输出 185 个逐 AP seq_time。
- [INFERENCE] test_dur=60 s 时 seq_time 的物理候选边界为 [0,test_dur]；是否裁剪须由 S2 分组验证预注册后决定。

### 3.2 输入边界

- [FACT] 候选基本信息为 test_dur、protocol、pkt_len、pd、ed、nav、eirp，以及列表型 RSSI 的折内稳健统计和相对门限特征。
- [INFERENCE] AP 数作为分模条件或统一模型结构变量；MAC、test_id、source_file、loc_id 不直接作为可记忆类别。
- [FACT] nss、mcs、per、num_ampdu、ppdu_dur、other_air_time、seq_time、throughput 和 predict/error 占位列全部禁用。
- [RISK] test_dur、pkt_len、pd、ed 在训练候选中恒定，不能从本样本识别其经验影响；不可写成“没有影响”。
- [RISK] 影响排序属于预测贡献/条件关联，不得偷换成因果结论。

### 3.3 评价

- [UNKNOWN] 题面未给出 Q1 官方评分函数。
- [INFERENCE] 内部报告完整组切分下的 MAE、RMSE、R²，并按 AP 数、loc、nav、protocol 分层。
- [INFERENCE] 影响排序候选证据为跨折置换重要性、特征族消融和方向一致性，具体方法留待 S2/G2。
- [RISK] RSSI 列表长度代表采样数量，不能直接当作信号强度。

## 4. 问题 2：最常用 (MCS, NSS) 预测

### 4.1 目标与输出

- [FACT] 预测 AMC 过程中使用次数最多的联合类别 (MCS,NSS)，不是瞬时 PHY Rate 序列。
- [FACT] test_set_2_2ap 有 64 行、test_set_2_3ap 有 87 行，共输出 151 组 predict mcs/nss。
- [FACT] 训练候选 NSS 分布为 0:3、1:26、2:1221；(2,11) 有 604/1250 行，类别明显不平衡。

### 4.2 输入和标签边界

- [FACT] 基本候选输入仍为业务、门限、RSSI 和分组拓扑。
- [INFERENCE] 可比较联合多分类与分层分类，但必须报告联合完全命中，避免组合出未观察类别。
- [INFERENCE] 如使用 Q1 信息，训练只能使用 Q1 折外 seq_time，推理使用 Q1 预测。
- [FACT] 真实 nss/mcs 及其派生 PHY Rate、PER、事后统计、真实 seq_time、throughput 均禁作输入。
- [RISK] 三条 (NSS,MCS)=(0,0) 暂保留；S2 必须做保留/排除敏感性。
- [RISK] (2,2) 仅 1 行、(0,0) 仅 3 行；S2 必须固定全局联合标签全集、排序、缺类回退和按固定标签集计算 macro-F1 的规则。

### 4.3 评价

- [UNKNOWN] 题面未给出 Q2 官方分类计分规则。
- [INFERENCE] 内部核心为联合 exact-match accuracy、固定标签集 macro-F1、balanced accuracy，并补充 MCS/NSS 分量准确率、每类 support 和混淆矩阵。

## 5. 问题 3：AP 与系统吞吐量及正式精度

### 5.1 两级目标、键和数量

- [FACT] AP 级真实/预测量分别为 y_i 和 yhat_i，单位 Mbps，键为 source_file + test_id + ap_id。
- [FACT] 系统吞吐量是同一完整测试组所有 AP 吞吐量之和：
  - y_g = sum over AP in g of y_i；
  - yhat_g = sum over AP in g of yhat_i；
  - 单位仍为 Mbps，键为 source_file + test_id。
- [FACT] eligible 训练有 1,250 个 AP 目标、482 个严格完整系统目标，其中 2 AP 组 196 个、3 AP 组 286 个。
- [FACT] Q3 测试需产生 185 个 AP 预测和 75 个系统预测；2 AP 测试 40 组、3 AP 测试 35 组。
- [FACT] 训练 AP throughput 有 5 个零值；482 个系统吞吐量均大于零，范围 77.33–618.67 Mbps。
- [FACT] test_set_1_* 的真实 seq_time/throughput 为空；真实 nss/mcs/per 非空，但题面只许可 Q3 使用真实 nss/mcs。

### 5.2 输入边界

- [FACT] 可用基本输入为业务、门限、RSSI、拓扑，加题面许可的真实 nss/mcs。
- [INFERENCE] 使用发送机会时，训练必须使用 Q1 折外 seq_time，推理使用 Q1 test_set_1 预测。
- [INFERENCE] 由于 test_set_1 已给真实 MCS/NSS，不为了形式依赖而以较差 Q2 预测替代；Q2 贡献可通过机理解释、误差分层和敏感性体现。
- [FACT] per、num_ampdu、ppdu_dur、other_air_time、真实 seq_time、throughput 和全部预测占位列禁作输入。

### 5.3 题面主评价合同

对 AP 级和系统级分别执行以下相同流程，不混合两种粒度：

1. [FACT] 题面 error 采用有符号相对误差且不取绝对值。以无量纲小数计算：
   - r_i = (yhat_i - y_i) / y_i；
   - 展示百分数 error_i(%) = 100 × r_i。
2. [FACT] 经验 CDF 定义为 F(x) = count(r_i <= x) / n。
3. [INFERENCE] 为获得唯一可执行的逆经验 CDF，ERROR_90 固定为：将有定义的 r_i 升序排列，取一基序号 k=ceil(0.90n) 的第 k 项；不插值。
4. [INFERENCE] 并列值全部保留，ERROR_90 仍取固定最近秩位置的数值，不在看到结果后改变算法。
5. [FACT] 题面模型精度写为 1-ERROR；本项目固定：
   - accuracy_90 = 1 - ERROR_90；
   - accuracy_90(%) = 100 × (1 - ERROR_90)；
   - 不裁剪负值或超过 100% 的显示值，避免隐藏题面有符号口径的后果。
6. [INFERENCE] y_i=0 时相对误差无定义：保留样本训练和绝对误差，但从相对误差 CDF/ERROR_90 中排除并披露排除数。当前 AP 级排除 5 个、可用 1,245 个；系统级排除 0 个、可用 482 个。
7. [INFERENCE] 另报告 |r_i| 的经验 CDF和相同最近秩 90% 分位作为稳健辅助诊断，明确不得替代题面有符号主指标。
8. [INFERENCE] MAE、RMSE、R²是辅助指标，不能替代 AP/系统两级 CDF、ERROR_90 和 accuracy_90。

- [RISK] 有符号误差会使系统性低估得到负 ERROR_90 或超过 100% 的“精度”；因此必须同时展示 signed CDF、偏差和绝对相对误差 CDF，不能只报一个好看的精度数。
- [RISK] 系统预测必须在严格身份完整的组上求和，不能对缺 AP、重复 AP 或跨 source_file 的行静默聚合。

## 6. 共同验证、重复和外推合同

- [FACT] 原始训练有 1,252 行、484 组，其中 A01 两组身份不完整；隔离后 1,250 行、482/482 组通过三重严格检查。
- [FACT] 四个测试集 336 行、136/136 组通过严格检查；Q3 测试 185 行、75/75 组通过。
- [FACT] 复合键 source_file + test_id + ap_id 无空值、非法 ap_id 或重复。
- [FACT] 文件内全列完全重复训练行为 0；同 AP 数规范化后跨文件重复行指纹簇为 0、重复组指纹簇为 0。
- [INFERENCE] 若未来派生数据出现等价重复簇，整簇必须绑定到同一验证折，不能跨训练/验证。
- [INFERENCE] 主验证采用 GroupKFold 或重复分组留出，groups 为 source_file + test_id，所有预处理在训练折内拟合。
- [INFERENCE] leave-one-source-file-out 是 S2 强制压力测试；leave-one-loc_id-out 在样本允许时执行，并按 AP 数、loc、nav、protocol 分层。
- [FACT] 四个官方测试集只做 schema、dtype、缺失/非空和严格身份检查，不输出数值分布、不参与选择。
- [RISK] 普通 grouped K-fold 仍共享 source 场景，主插值指标和场景外推指标必须分别报告。

## 7. 交付与成功判据

| 问题 | 必交输出 | 内部可验收证据 | 当前状态 |
|---|---|---|---|
| Q1 | 参数影响强弱与方向；185 个 seq_time | 分组回归、跨折重要性/消融、边界检查 | S1 已定义，待 S2 |
| Q2 | 151 组 predict mcs/nss | 固定标签集联合/macro 指标、混淆矩阵、A03 敏感性 | S1 已定义，待 S2 |
| Q3-AP | 185 个逐 AP throughput | signed/absolute CDF、ERROR_90、accuracy_90、MAE/RMSE/R²、零值披露 | S1 已定义，待 S2 |
| Q3-System | 75 个按完整组求和的系统 throughput | 独立的 signed/absolute CDF、ERROR_90、accuracy_90 和系统级辅助指标 | S1 已定义，待 S2 |

## 8. 仍待确认事项

- [UNKNOWN] Q1/Q2 官方评分函数和最终预测文件数值格式。
- [UNKNOWN] 官方原始压缩包稳定来源、总哈希和发布方逐文件哈希。
- [UNKNOWN] training_set_3ap_loc33_nav88.csv 的官方位置标签原意是 loc4 还是 loc33。
- [UNKNOWN] 三条 (NSS,MCS)=(0,0) 的业务语义。
- [UNKNOWN] 团队成员实名责任分配；当前仓库工作由 Main Agent/Codex 执行，最终提交必须由人类队员负责。
