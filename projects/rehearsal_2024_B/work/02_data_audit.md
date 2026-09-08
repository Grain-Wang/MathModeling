# S1 Data Audit

## 1. Audit verdict

**PASS_WITH_WARNINGS：本地数据足以进入模型方案设计，但必须携带 A01–A06 处理合同和泄漏边界。**

- [FACT] 审计脚本：[src/s1_data_audit.py](../src/s1_data_audit.py)。
- [FACT] 正式运行基于干净 commit 37fc3562e915562c09ea2a6000feeb1b703765b8，运行前工作树为空。
- [FACT] 17/17 CSV 在审计前后均通过固定文件名、字节数和 SHA-256 校验；input_hashes_unchanged_during_audit=true。
- [FACT] 13 个训练文件 1,252 行；A01 隔离后 1,250 行、482 个完整测试组。4 个测试文件 336 行、136 个完整测试组。
- [FACT] 全部文件可由 pandas 解析；训练集和逐文件均无完全重复行；PER 非空值均位于 [0,1]。
- [FACT] 机器证据位于 [data_profile.json](../results/raw/s1/data_profile.json)、[quality_checks.json](../results/raw/s1/quality_checks.json)和[audit_summary.md](../results/raw/s1/audit_summary.md)。
- [RISK] 原始 CSV 被 Git 忽略，远程 Reviewer 只能核对脚本、manifest、JSON/Markdown 证据，不能在无授权数据副本时重跑。

复现命令：

~~~powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s1_data_audit.py --verify-only
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s1_data_audit.py
~~~

## 2. 输入规模与组结构

| 文件 | 角色 | 行 × 列 | test_id 组 | 组结构/备注 |
|---|---|---:|---:|---|
| test_set_1_2ap.csv | Q1/Q3 测试 | 80 × 47 | 40 | 全部 2 行/组 |
| test_set_1_3ap.csv | Q1/Q3 测试 | 105 × 57 | 35 | 全部 3 行/组 |
| test_set_2_2ap.csv | Q2 测试 | 64 × 46 | 32 | 全部 2 行/组 |
| test_set_2_3ap.csv | Q2 测试 | 87 × 56 | 29 | 全部 3 行/组 |
| training_set_2ap_loc0_nav82.csv | 训练 | 82 × 43 | 41 | 全部 2 行/组 |
| training_set_2ap_loc0_nav86.csv | 训练 | 80 × 43 | 40 | 全部 2 行/组 |
| training_set_2ap_loc1_nav82.csv | 训练 | 78 × 43 | 39 | 全部 2 行/组 |
| training_set_2ap_loc1_nav86.csv | 训练 | 74 × 43 | 37 | 全部 2 行/组 |
| training_set_2ap_loc2_nav82.csv | 训练 | 80 × 43 | 41 | 39 个完整组；test_id 40/41 各仅 1 条错位行 |
| training_set_3ap_loc30_nav82.csv | 训练 | 123 × 55 | 41 | 全部 3 行/组；2 个空占位列 |
| training_set_3ap_loc30_nav86.csv | 训练 | 120 × 55 | 40 | 全部 3 行/组；3 个 RSSI 列全空；2 个空占位列 |
| training_set_3ap_loc31_nav82.csv | 训练 | 126 × 53 | 42 | 全部 3 行/组 |
| training_set_3ap_loc31_nav86.csv | 训练 | 108 × 53 | 36 | 全部 3 行/组 |
| training_set_3ap_loc32_nav82.csv | 训练 | 111 × 53 | 37 | 全部 3 行/组 |
| training_set_3ap_loc32_nav86.csv | 训练 | 60 × 53 | 20 | 全部 3 行/组 |
| training_set_3ap_loc33_nav82.csv | 训练 | 111 × 53 | 37 | 全部 3 行/组 |
| training_set_3ap_loc33_nav88.csv | 训练 | 99 × 53 | 33 | 全部 3 行/组；内容 loc_id 全为 loc4 |

- [FACT] 原始 2 AP 训练部分为 394 行；隔离 A01 后为 392 行、196 组。3 AP 训练部分为 858 行、286 组。
- [FACT] test_id 会在不同 source_file 中重复，故全局唯一键不是 test_id，而是至少 source_file + test_id；行键再加 ap_id。
- [RISK] source_file 同时编码 AP 数、loc 和 nav，若将其直接作为模型类别，会让模型记忆场景；仅作为分组、溯源和压力测试键。

## 3. 字段字典与规范化合同

机器证据保存了 57 个联合字段的逐文件覆盖、dtype、全空列和缺失数。下表给出建模所需的族级合同。

| 字段/字段族 | 含义与单位 | 审计类型 | S1 使用合同 |
|---|---|---|---|
| test_id | 一次测试编号，无量纲 | 组标识 | 与 source_file 组成切分组，不作原始特征 |
| test_dur | 一次测试时长，s | 数值 | 训练中恒为 60；只作边界/归一化候选 |
| loc_id | 场景位置标识 | 类别/场景键 | 用于分层和外推压力测试；默认不直接记忆 |
| protocol | tcp/udp | 类别 | 基本输入 |
| pkt_len | 包长，byte | 数值 | 训练中恒为 1500，当前效应不可识别 |
| bss_id、ap_name、ap_mac、ap_id | BSS/设备/AP 标识 | 标识/类别 | MAC 不作特征；AP 标识只用于构造组内相对拓扑 |
| pd、ed、nav | 门限，dBm | 数值 | 基本输入；pd=-82、ed=-62 在训练中恒定，nav 有 -82/-86/-88 |
| eirp | 等效全向辐射功率，dBm | 数值 | 基本输入，训练范围 9–29 |
| ap_from_ap_x_*_ant_rssi | AP 接收 AP_x 的 RSSI，dBm | 列表或标量 | 派生稳健统计、门限差和可用掩码，不直接喂原字符串 |
| sta_to_ap_x_*_ant_rssi | STA 到 AP_x 的 RSSI，dBm | 列表或标量 | 同上 |
| sta_from_ap_x_*_ant_rssi | STA 接收 AP_x 的 RSSI，dBm | 列表或标量 | 同上，可构造服务信号/干扰差 |
| sta_from_sta_x_rssi | STA 间 RSSI，dBm | 列表或标量 | 同上；非适用方向保留缺失掩码 |
| sta_mac、sta_id | STA 标识 | 标识 | 只作对齐与拓扑构造，不直接记忆 |
| nss、mcs | 最常用空间流数/MCS | 离散标签 | Q2 标签；Q3 仅按题面许可使用真实值 |
| per | 丢包率，[0,1] | 事后统计 | Q1/Q2/Q3 均禁用 |
| num_ampdu | CSV 聚合数；题面称 num_ppdu | 事后统计 | 派生表统一名仍需保留 source alias；三问输入均禁用 |
| ppdu_dur | 平均帧时长，s | 事后统计 | 三问输入均禁用 |
| other_air_time | 其他帧发送与接收占用时间，s | 事后统计 | 三问输入均禁用；A05 两值置缺失 |
| seq_time | 帧序列总时长，s | Q1 标签 | Q1 标签；下游只能用 OOF/推理预测 |
| throughput | 实测吞吐量，Mbps | Q3 标签 | 仅作 Q3 标签 |
| predict *、error%、error%.1 | 待填输出/误差占位 | 输出 | 永不作为特征；原表头不修改 |

- [FACT] test_set_1_* 的重复 error% 表头被 pandas 解析为 error% 和 error%.1。
- [FACT] 两个 loc30 训练文件比其他训练表多 predict throughput、error% 两个全空列。
- [INFERENCE] 规范化只发生在派生数据；原始字段名和文件保持逐字节不变。

## 4. RSSI 编码与缺失机制

- [FACT] 审计器接受两种合法编码：有限数值标量，或非空有限数值列表。
- [FACT] 17 个文件共扫描到 32,565 个列表单元、2,568 个标量单元、7,123 个空单元和 4 个非法文本单元。
- [FACT] 列表长度从 1 到 521 不等，表明每次测试/方向的采样数不固定。
- [FACT] 4 个非法文本和 12 个超出 [-120,0] dBm 的数值全部集中在 A01 两条错位行。
- [INFERENCE] RSSI 特征需要在折内以 median、分位数、IQR、可用率等固定统计压缩；列表长度最多作为采样可靠性辅助量，不能当作信号强弱替代。
- [INFERENCE] 多数 ap_from_ap_x 和 sta_from_sta_x 的 AP 数比例缺失与“自身链路/不适用方向”一致，属于结构性缺失候选；必须保留方向掩码，不能全局均值填补。
- [FACT] A02 是额外的整列整场景缺失，不属于上述每组一个方向的常规结构模式。
- [RISK] 缺失本身可能携带拓扑信息；所有缺失处理器必须只在训练折拟合，并以消融检查是否依赖数据采集伪迹。

## 5. 训练集描述统计

以下统计只使用 A01 隔离后的 1,250 行训练候选；官方测试集未参与分布分析。

| 项目 | 结果 |
|---|---|
| AP 数 | 2 AP：392 行；3 AP：858 行 |
| protocol | tcp 675；udp 575 |
| nav | -82: 709；-86: 442；-88: 99 |
| loc_id | loc0 162；loc1 152；loc2 78；loc30 243；loc31 234；loc32 171；loc33 111；loc4 99 |
| nss | 0: 3；1: 26；2: 1221 |
| mcs | 0–11，缺少 1；mcs=11 为 604 行 |
| per | min 0，median 0.11，max 1；无越界 |
| seq_time | min 0.40，median 32.03，max 52.02 s |
| throughput | min 0，median 83.995，max 240.48 Mbps；5 行为 0 |
| ppdu_dur | 0.000764463–0.004435589 s |
| num_ampdu | 4–21 |
| other_air_time | median 14.7232 s；两个异常值使 max 达 1,341,524.319 s |

- [FACT] test_dur=60、pkt_len=1500、pd=-82、ed=-62 在训练候选中方差为 0。
- [RISK] 常量字段在本数据上无法获得经验影响排序；论文不能把模型重要性为零解释成系统上没有影响。
- [RISK] NSS 极端不平衡；Q2 必须使用 macro/平衡指标与联合类别指标。
- [RISK] throughput=0 使普通 MAPE 不可定义。
- [INFERENCE] other_air_time 大于 test_dur 的两个值违反题面单位与观测窗口边界，按 A05 字段级无效处理；其余大量 seq_time + other_air_time > 60 的记录不直接判错，因为两个统计口径是否有重叠/重复计数尚无充分证据。

## 6. 异常登记与冻结处理

| ID | 证据 | 冻结处理 | 对样本量/模型的影响 |
|---|---|---|---|
| A01 | training_set_2ap_loc2_nav82.csv 源内索引 78/79，test_id 40/41、ap_1；4 个非法 RSSI 文本、12 个正 RSSI 数值、标签块为空；两组均只有 1 行 | 原件不改；隔离两个不完整 source_file + test_id 组 | 删除 2 行，1,252 → 1,250；剩余组完整 |
| A02 | training_set_3ap_loc30_nav86.csv 的 ap_from_ap_0_sum/max/mean_ant_rssi 各 120/120 为空 | 不反向复制、不对称臆造；保留缺失与可用掩码 | S2 使用缺失感知方案或删不可用方向并做消融 |
| A03 | 3 条 (NSS,MCS)=(0,0)，但 PER、seq_time、throughput 非空 | 原值保留；不改成 NSS=1 | S2 比较保留/排除后再冻结 Q2 类别合同 |
| A04 | num_ppdu/num_ampdu 别名、重复 error%、空预测列 | 仅派生表规范化；所有输出占位列禁作特征 | 不改原始 schema |
| A05 | loc31/nav82 索引 86 为 1,181,768.274 s；loc31/nav86 索引 14 为 1,341,524.319 s，均 test_dur=60 | other_air_time 字段置缺失且禁作输入；目标行暂保留 | 如候选模型受影响，S2 增加整组排除敏感性 |
| A06 | training_set_3ap_loc33_nav88.csv 的 99 行 loc_id 全为 loc4 | 不改文件名/内容；loc4 作字段值，source_file 作独立场景键 | 官方意图保持 UNKNOWN，分层报告需披露 |

- [FACT] 关于 A01，竞赛讨论中的 B 题专家回复允许自行剔除异常数据：https://www.shumo.com/forum/forum.php?mod=viewthread&tid=107845
- [FACT] 关于 A02，该文件问题被列入 B 题专家普遍问题汇总：https://www.shumo.com/forum/forum.php?mod=viewthread&tid=107966
- [RISK] 外部论坛回复只是处理许可/佐证，不替代本项目的逐行规则、样本量审计或敏感性分析。

## 7. 测试集封存检查

| 测试集 | 提供字段 | 空白字段 | 允许用途 |
|---|---|---|---|
| test_set_1_2ap / 3ap | 基本输入、RSSI、nss、mcs、per | num_ampdu、ppdu_dur、other_air_time、seq_time、throughput、预测/误差列 | Q1/Q3 最终推理；Q3 仅使用题面明确许可的真实 nss/mcs，不使用 per |
| test_set_2_2ap / 3ap | 基本输入、RSSI | nss、mcs 及所有事后/输出列 | Q2 最终推理 |

- [FACT] 四个测试文件组大小全部正确，预测列和对应未知标签均为空。
- [FACT] 审计器只记录行列、组大小、dtype、缺失和非空计数，未输出测试特征分布。
- [RISK] 即使测试集中某字段非空，也不自动意味着可作为模型输入；以题面任务时点和显式许可为准。

## 8. 层级、泄漏与验证候选

- [FACT] 切分原子：source_file + test_id；同组全部 AP 行必须同折。
- [INFERENCE] 主验证候选：GroupKFold 或重复分组留出；RSSI 聚合、缺失处理、编码、缩放和特征选择全部在训练折内拟合。
- [INFERENCE] 场景压力测试：leave-one-source-file-out；样本允许时 leave-one-loc_id-out；并按 AP 数、loc、nav、protocol 报告。
- [FACT] Q1 的事后字段全部禁用；Q2 只可接收 Q1 折外预测；Q3 只接受真实 nss/mcs 的题面特许和 Q1 折外/推理预测。
- [RISK] 先全数据生成 RSSI 统计阈值、填补量或目标编码再切分仍属于泄漏。
- [RISK] 官方测试集不得用于阈值选择、特征筛选、异常规则调整、调参或模型选择。

## 9. 各问数据充分性

| 问题 | 结论 | 限制 |
|---|---|---|
| Q1 | [FACT] 有 1,250 行完整分组训练候选和 185 行目标测试输入，可开始方案设计 | [RISK] 多个门限/业务字段恒定，影响排序只能覆盖样本中有变化的因素 |
| Q2 | [FACT] 训练 nss/mcs 完整，151 行测试标签为空且基本输入存在 | [RISK] 类别严重不平衡，A03 语义未知 |
| Q3 | [FACT] 训练 throughput 完整，test_set_1 提供题面许可的 nss/mcs，可开始方案设计 | [RISK] 必须用 Q1 OOF 链路；零吞吐量影响相对误差；PER 虽非空仍禁用 |

## 10. 数据来源、责任与剩余限制

- [FACT] 当前不需要外部数据，也未使用预训练模型或外部数据集。
- [FACT] 数据恢复步骤和 17 个期望文件名见 [problem/data/README.md](../problem/data/README.md)。
- [UNKNOWN] 官方压缩包稳定 URL、总哈希和逐文件发布方校验值尚未取得，因此只能证明本地副本与 S0 manifest 一致。
- [UNKNOWN] 团队数据审计、代码、建模和最终提交责任人的实名尚未提供；当前仓库执行者为 Main Agent/Codex，最终提交必须由人类队员确认并操作。
- [RISK] 在另一机器复现前必须先取得授权数据副本并运行 --verify-only；任何哈希不一致都应停止，而不是更新 EXPECTED 常量迎合新文件。
