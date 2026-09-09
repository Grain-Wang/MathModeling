# Decision Log

本日志记录会影响题意、数据、方法、验证和交付的决策。状态使用 ACTIVE、SUPERSEDED 或 REVERSED。

| Time (Asia/Shanghai) | ID | Stage | Decision | Rationale and evidence | Impact | Status |
|---|---|---|---|---|---|---|
| 2026-09-08 22:10 | D0001 | S0 | 唯一 ACTIVE_PROJECT 切换为 projects/rehearsal_2024_B，原 C 项目暂停 | 用户明确要求按计划初始化 B 项目并进入 G0 审查 | 后续赛题成果只写入 B；C 保留既有 S6 状态但不继续执行 | ACTIVE |
| 2026-09-08 22:10 | D0002 | S0 | 采用 competition/2024/ 中归档的第二十一届官方材料 | B 题属于同一届竞赛；本地官方邀请函、格式规范、提交手册和模板均有哈希与来源记录 | 格式、匿名、命名和提交要求以官方原件/网页为准 | ACTIVE |
| 2026-09-08 22:10 | D0003 | S0 | 将 17 个原始 CSV 从 src/ 受控移动至 problem/data/ | 文件协议规定原题和原始数据归入 problem/；移动前后文件数量一致，内容哈希保持不变 | src/ 留给代码；原始 CSV 只读，派生数据不得回写 | ACTIVE |
| 2026-09-08 22:10 | D0004 | S0 | 原始 CSV 继续由 /projects/**/*.csv 忽略，并以 manifest 记录可复核元数据 | 用户明确要求 CSV 不上传远程；所有 17 个数据文件当前均命中忽略规则 | 远程仓库不含原始数据；换机前必须按 manifest 取得并校验数据 | ACTIVE |
| 2026-09-08 22:10 | D0005 | S0 | 使用现有 math_modeling Conda 环境，S0 不安装新依赖 | Python 3.11.11 及核心建模/文档包导入冒烟测试通过 | S1 可直接执行数据审计；新增依赖须由后续模型需求论证 | ACTIVE |
| 2026-09-08 22:10 | D0006 | S0 | S0 不修改已知异常记录，处理规则推迟到 S1 冻结 | 原件应保持不可变；论坛 B 题专家允许剔除两条错位数据，但本项目仍需记录可复现规则 | S1 派生数据中处理，保留原始行号、理由和数量审计 | ACTIVE |
| 2026-09-08 22:10 | D0007 | S0 | 在 G0 对固定 commit 给出 PASS 前不进入 S1 | Main/Reviewer 协议要求阶段门控；Main Agent 不得自行宣布通过 | 当前仅允许完成 S0 验证、提交与审核准备 | ACTIVE |
| 2026-09-08T22:48:49+08:00 | D0008 | S1 | 接受 G0/R1 PASS 并进入 S1，下一门禁为 G1 | 远程审核 commit 0fac4e0 明确授权 S0 -> S1，Critical=0、Major=0 | 只开展题意拆解和数据审计；G1 PASS 前不进入正式建模 | ACTIVE |
| 2026-09-08T22:48:49+08:00 | D0009 | S1 | problem/data/README.md 作为唯一可跟踪的数据恢复说明，原始 CSV 继续全量忽略 | 闭环 G0 Minor 1；README 记录 17 个文件名、授权来源边界与哈希复核命令 | .gitignore 只放行该 README，不放行任何 CSV | ACTIVE |
| 2026-09-08T22:48:49+08:00 | D0010 | S1 | A01 按 source_file + test_id 组隔离 test_id 40、41 | 两条 ap_1 记录字段错位，且这两个 test_id 各自本来就只有该 1 行，属于不完整 2 AP 组 | 隔离两个不完整组共 2 行，派生训练候选由 1,252 行变为 1,250 行；原件不改 | ACTIVE |
| 2026-09-08T22:48:49+08:00 | D0011 | S1 | A02 保持原始缺失，不用反向链路或对称关系臆造三个全空 RSSI 列 | 缺少可验证的等价关系；伪填补会引入结构性偏差 | S2 仅可采用缺失指示、缺失感知预处理或移除不可用方向，并做消融 | ACTIVE |
| 2026-09-08T22:48:49+08:00 | D0012 | S1 | A03 的三条 (NSS,MCS)=(0,0) 暂保留，不改成 NSS=1 | 三条记录的 PER、时延和吞吐量均非空，具备失败状态/哨兵的内部一致性 | S2 必须报告包含与排除三条记录的敏感性，再冻结 Q2 标签策略 | ACTIVE |
| 2026-09-08T22:48:49+08:00 | D0013 | S1 | 固定按 source_file + test_id 分组验证和逐问泄漏边界 | 同一 test_id 的多 AP 行共享场景；题面只明确许可 Q3 使用实测 MCS/NSS | 测试集封存；Q1 禁事后字段；Q2 仅可用 OOF Q1 预测；Q3 不把许可扩展到 PER | ACTIVE |
| 2026-09-08T22:58:30+08:00 | D0014 | S1 | A05 的两个 other_air_time 超测试时长值按字段无效处理，不扩张为整行删除 | 题面单位为秒且 test_dur=60；两值为 1181768.274 和 1341524.319，明显不满足观测时长边界，而对应目标仍在正常量级 | 该字段本就禁止进入 Q1-Q3；派生分析置缺失，S2 如相关则做整组排除敏感性 | ACTIVE |
| 2026-09-08T22:58:30+08:00 | D0015 | S1 | A06 保留文件名 training_set_3ap_loc33_nav88.csv，但以内容 loc_id=loc4 作为字段值 | 该文件 99 行的 loc_id 均为 loc4，与文件名 token loc33 不一致，无法从本地证据判定官方意图 | 不改原件；source_file 作为独立场景键，报告该来源标签不确定性 | ACTIVE |
| 2026-09-08T23:14:11+08:00 | D0016 | S1 | 官方测试集只输出 schema、dtype、缺失/非空和组结构证据，不汇总任何数值或 RSSI 取值分布 | G0 Reviewer 要求保持测试封存；分布摘要可能间接影响特征与规则选择 | 训练侧承担所有分布审计；测试侧只在模型冻结后用于推理与格式校验 | ACTIVE |
| 2026-09-08T23:14:11+08:00 | D0017 | S1 | S1 交付物完成后停在 G1，未获 PASS 前不进入 S2 | 阶段门禁要求 Main Agent 不得自审通过 | 当前仅固定本地审核快照；远程推送等待用户明确授权 | ACTIVE |
| 2026-09-09T09:48:26+08:00 | D0018 | S1 | 用户明确授权向 origin/main 推送完整 G1 审核快照 | 用户明确回复允许推送 | 允许远程发布当前 S1/G1 commits；仍不得在 G1 PASS 前进入 S2 | ACTIVE |

| 2026-09-09T10:36:00+08:00 | D0019 | S1 | 接受 G1/R1 REVISE，项目保持 S1，不进入 S2 | 审核 commit e9253ce 对 reviewed commit 512e461 判定两项 Major：Q3 合同遗漏和身份/重复证据不足 | 只做局部 S1 修订、正式重审证据与 G1 Round 2 提交 | ACTIVE |
| 2026-09-09T10:36:00+08:00 | D0020 | S1 | Q3 同时冻结 AP throughput 和严格组内所有 AP throughput 之和的系统目标 | 题面明确要求所有 AP 吞吐之和；复审要求两级输出、键、单位和数量独立登记 | AP 键为 source_file + test_id + ap_id，系统键为 source_file + test_id；训练 1,250/482，测试 185/75 | ACTIVE |
| 2026-09-09T10:36:00+08:00 | D0021 | S1 | Q3 主指标采用题面有符号相对误差；ERROR_90 用最近秩且不插值；零分母预先排除并单列 | 题面公式没有绝对值，CDF 定义为 P(X≤x)，模型精度为 1-ERROR；必须在见到模型结果前唯一化算法 | AP/系统分开计算；并列保留；精度不裁剪；绝对相对误差 CDF 和通用回归指标仅作辅助 | ACTIVE |
| 2026-09-09T10:36:00+08:00 | D0022 | S1 | 完整组必须同时满足预期行数、精确 AP ID 集合/次数和复合行键唯一 | 单纯组内行数不能排除重复某 AP、缺少另一 AP 的伪完整组 | 原始训练 482/484 严格有效；A01 后训练 482/482、官方测试 136/136、Q3 测试 75/75 通过 | ACTIVE |
| 2026-09-09T10:36:00+08:00 | D0023 | S1 | 重复审计区分文件内全列完全重复与同 AP 数分层的跨文件规范化行/组 SHA-256 指纹 | 原逐文件 duplicated 结论不能支持整个训练集无跨文件等价观测 | 当前文件内重复 0、跨文件行簇 0、组簇 0；未来发现的等价簇不删除且整簇绑定同一折 | ACTIVE |
| 2026-09-09T10:36:00+08:00 | D0024 | S1 | S2 初期强制执行 leave-one-source-file-out，并在首次训练前冻结 Q2 全局标签集和稀有类缺折规则 | G1 Minor-01/02 指出普通 grouped K-fold 不能验证 source 场景外推，且稀有联合类别会使折间标签集合变化 | 场景外推结果不得选择性省略；macro-F1 使用固定标签集并披露 support、失败/回退和 A03 敏感性 | ACTIVE |

| 2026-09-09T11:30:19+08:00 | D0025 | S2 | 接受 G1/R2 PASS 并由 S1 进入 S2，下一门禁为 G2 | 审核 commit fd6e33b 对 reviewed commit 9f0a209 判定 Critical=0、Major=0，并明确授权 S1→S2 | 允许设计统一方案、模型合同、实验计划和 O1；G2 PASS 前仍禁止正式训练 | ACTIVE |
| 2026-09-09T11:30:19+08:00 | D0026 | S2 | 将数据列 nav 唯一解释为 NAV 门限，单位 dBm，而不是 NAV 静默时长 | 题目正文 2.4 区分 NAV 时段与 NAV 门限；数据介绍 4.1.3 明确写 nav (dBm): NAV门限，且样本档位为 -82/-86/-88 | 修正 work/02 的 μs 冲突；保留脚本与 data_profile 的 dBm 口径；后续构造 mean RSSI - nav 门限裕量 | ACTIVE |

| 2026-09-09T11:51:36+08:00 | D0027 | S2 | 采用共享机制特征引擎、简单 Baseline 与统一 HGB 主候选家族，禁止无计划算法堆叠 | 1,250 行/482 组属于小样本；共享 RSSI 摘要、peer 聚合和阈值裕量可闭合三问，并让复杂度受 4 点网格约束 | Q1/Q2 各最多 4 个 HGB 配置；Q3 只比较直接/物理残差两种结构、最多 8 个配置；其他候选须由 O2/O3 证据触发 | ACTIVE |
| 2026-09-09T11:51:36+08:00 | D0028 | S2 | 冻结 source_file+test_id 的 3×5 外层、逐外层 3 折内层和 13 折 LOSO 注册表，并冻结 Q2 全局 17 类 | 正式合同校验在干净 6b88cd1 上得到 1,446 个外层、5,784 个内层分配和 13 个 LOSO；Q2 折间可能缺类 | 所有问题共享外层分配；预处理只在当前训练折拟合；缺类概率置零并以固定标签 macro-F1/report support 评估 | ACTIVE |
| 2026-09-09T11:51:36+08:00 | D0029 | S2 | Q3 以物理效率 Baseline 为锚，仅比较直接 HGB 与非负残差 HGB；系统预测严格等于 AP 预测之和 | 题面提供 PHY rate 表且要求 AP/系统两级结果；独立系统头会破坏可加一致性 | 以 AP/系统绝对相对误差 90 分位最大值选择，保留题面有符号指标为主报告并执行偏差护栏 | ACTIVE |
| 2026-09-09T11:51:36+08:00 | D0030 | S2 | O1 决策为 PROCEED_TO_G2 | 三问、数据流、单位、目标、约束、Baseline、嵌套验证、LOSO、候选预算、停止条件和回退均已冻结；合同校验 PASS 且零模型拟合/零测试数值读取 | 允许提交 G2；G2 PASS 前仍不得进入 S3 | ACTIVE |

| 2026-09-09T14:54:01+08:00 | D0031 | S2 | 接受 G2/R1 REVISE 并保持 S2，禁止进入 S3 | review commit fe959af 对 5bf0126 判定 M2-01/M2-02 两项 Major，S2→S3 未授权 | 只允许修订合同、split/lineage、合成门禁证据和 Round 2 提交 | ACTIVE |
| 2026-09-09T14:54:01+08:00 | D0032 | S2 | 删除 S3 官方测试 Baseline 推理；唯一释放点为 G4 PASS 后、S5 freeze manifest 完整后的一次最终推理 | 提前预测即使无标签也可能以范围、类别或物理外观反馈 O2/O3/S4 | protected phases 的 run manifest 若含四个测试文件即硬失败；最终释放后写 ledger 且禁止反馈 | ACTIVE |
| 2026-09-09T14:54:01+08:00 | D0033 | S2 | Q2/Q3 上游统一固定为 Q1-B1 Ridge(alpha=1.0) 的 seq_time_bounded，postprocess=q1_clip_0_test_dur_v1 | 固定上游身份可避免 Q1 胜者选择与下游选参双重耦合，同时保持 Q1→下游技术链 | Q1-HGB 只回答 Q1；每批下游预测必须保存模型、版本和 fit-group hash 血缘 | ACTIVE |
| 2026-09-09T14:54:01+08:00 | D0034 | S2 | 为 S4 下游 inner-CV 冻结第三层 3-fold Q1 cross-fitting，并统一 repeated-CV、bootstrap 和 raw/bounded 口径 | outer-train 预生成 OOF 可能让 inner-validation 标签进入 inner-training 特征；重复预测也不能当独立样本 | primary/LOSO 各 11,568 个 nested 分配；bounded 为晋升口径，raw 仅审计；LOSO 选择保持 source-blind | ACTIVE |

| 2026-09-09 | D0035 | S3 | 接受 G2/R2 PASS 并由 S2 进入 S3，下一门禁为 G3 | 审核 commit 6504c54 对 facedf1 明确给出 Critical=0、Major=0，并授权 S2→S3 | 只运行冻结八个 Baseline、15 外层折、13 LOSO、训练侧 dry-run 和 O2；官方测试继续封存 | ACTIVE |
| 2026-09-09 | D0036 | S3 | Ridge(alpha=1.0) 固定使用确定性 LSQR 求解器，逐行证据写为 gzip JSONL | 312 个高相关派生特征令默认求解器产生 LinAlgWarning；LSQR 不改变模型族或 alpha，压缩不改变证据语义 | 正式运行要求 warning_count=0；所有逐行键、概率、预测和血缘仍完整保留 | ACTIVE |

| 2026-09-09 | D0037 | S3 | O2 决策为 PROCEED_TO_G3，仅选择 Q2 finite HGB 与 Q3 direct/physics-residual HGB 两个受限 S4 方向 | 八个 Baseline、15 个 outer folds、13 个 LOSO 与独立重算均闭环；真实瓶颈集中在 Q2 稀有类/场景外推和 Q3 3 AP/物理外推取舍 | 形成 G3 submission；在 Reviewer 给出 G3 PASS 前不启动 S4，也不读取官方测试数值 | ACTIVE |
