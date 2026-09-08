# Project Brief — rehearsal_2024_B

## 1. Project Identity

- Active project: projects/rehearsal_2024_B
- Competition: 2024 年“华为杯”第二十一届中国研究生数学建模竞赛往年题模拟
- Problem: B 题《WLAN组网中网络吞吐量建模》
- Current stage: S0 — 项目初始化与约束确认
- Next gate: G0
- Initialization date: 2026-09-08
- Selection authority: 用户在当前会话明确要求按计划完成 B 项目初始化并进入 G0 审查；原 C 项目已标记为 INACTIVE / PAUSED。

## 2. Selection Rationale

1. 用户已明确把本项目设为新的唯一 ACTIVE_PROJECT。
2. 本机已有可读取的 B 题正文、13 个训练 CSV 和题目点名的 4 个测试 CSV。
3. 题目把 WLAN 接入机理、RSSI 序列特征、发送机会、MCS/NSS 和吞吐量串成三问，适合演练机理特征与数据驱动模型结合。
4. 当前 math_modeling 环境已具备 pandas、NumPy、SciPy、scikit-learn 和 matplotlib，数据规模约 23.56 MiB，CPU 足以完成 S1 审计和基础建模。
5. 原始数据存在公开确认过的异常，适合检验仓库的数据审计、异常登记和 Gate 机制，但任何清洗必须透明且可复现。

## 3. Problem Scope

| Question | Core task | Required output | Official test input |
|---|---|---|---|
| Q1 | 分析拓扑、业务、门限和节点间 RSSI 对 AP 发送机会的影响，给出影响强弱顺序并预测 seq_time | 参数影响排序、解释证据、每 AP 的 seq_time 预测 | test_set_1_2ap、test_set_1_3ap |
| Q2 | 结合传输方式、SINR、门限和 Q1 发送机会，预测最常用的 MCS/NSS | 每 AP 的 predict mcs、predict nss | test_set_2_2ap、test_set_2_3ap |
| Q3 | 结合 Q1/Q2 分析建立每 AP 与系统吞吐量模型；题面允许把实测 MCS/NSS 作为本问输入 | 每 AP 吞吐量、系统吞吐量、误差 CDF 与 90% 分位精度 | test_set_1_2ap、test_set_1_3ap |

三问必须形成同一条数据流：基础信息与 RSSI → 信道竞争/发送机会 → 速率状态 → 吞吐量。S2 前不得把三个互不相干的算法当作统一解答。

## 4. Confirmed Inputs

- 题目 DOCX 1 个，SHA-256 为 C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594；标题、问题1–3、数据字段说明、精度定义和附录均可读取。
- 训练 CSV 13 个，共 1,252 行；测试 CSV 4 个，共 336 行。
- 所有 17 个 CSV 均能由 pandas 3.0.2 只读解析，基础检查未发现完全重复行。
- 数据现统一位于 problem/data/，完整逐文件清单、大小和哈希见 [problem/manifest.md](../problem/manifest.md)。
- CSV 根据用户要求不进入 Git；远程仓库仅保存 manifest，不保存原始数据。

## 5. Official Constraints

适用资料为 [competition/2024/](../../../competition/2024/README.md) 中归档的官方邀请函、论文格式规范、提交手册和论文模板。模拟按以下约束执行：

1. 使用官方论文模板；最终论文为单个未压缩 PDF，首页封面、统一摘要页和正文顺序不得擅改。
2. 除首页外，正文、图表、页眉页脚、附件内容和附件文件名不得出现学校、姓名、学号、队伍编号等身份信息。
3. 摘要不超过两页，并覆盖建模思路、主要方法、模型、结果、结论和创新点。
4. PDF 文件名为“赛题编号 + 队伍编号”；MD5 固定后不得再修改对应 PDF。
5. 可选附件使用 RAR，命名同上且不超过 50 MB；只有题目要求或确有助于评审且正文已说明时才上传。
6. 引用文献和他人程序必须注明来源；不得抄袭、购买论文或隐瞒程序来源。
7. 正式约束冲突时，以 competition/2024/ 的官方原件和官方网页为准，本项目摘要只作导航。
8. 原始题目和 CSV 不得覆写；测试集只用于冻结模型后的正式预测，不得用于特征选择、调参或模型选择。
9. AI Usage Log 是仓库的可追溯要求；最终提交前须再次核对当届适用的官方 AI 使用规则，不把未核验的 AI 输出当作事实。

## 6. Working Roles

| Responsibility | Current owner | Boundary |
|---|---|---|
| 题目选择、活动项目和最终方向 | 用户/参赛团队 | 对题号、目标、外部协作和最终提交负责 |
| S0 初始化与主流程 | Main Agent（当前由 Codex 执行） | 生成项目文档与证据，不自行宣布 Gate 通过 |
| 数据、模型、代码与实验 | G0 后由 Main Agent 编排；具体成员待团队指定 | 先完成 S1，再在 G2 模型合同通过后实现大规模模型 |
| 图表与论文 | 待团队指定 | 只能引用 results/verified/ 的核验结果 |
| Gate 审核 | 独立 Reviewer Agent | 基于固定远程 commit 审核，只新增 reviews/ 审核文件 |

团队姓名和具体分工尚未提供；当前功能角色足以进入 G0，但建议在 G1 前补充。

## 7. Compute Environment

- OS: Microsoft Windows 11 专业版，64 位，版本 10.0.26200
- CPU: AMD Ryzen 7 8745H，8 核 / 16 逻辑处理器
- Visible RAM: 13.8 GiB
- GPU: 未检测到 nvidia-smi；不得假设存在 A800 或 CUDA
- Conda environment: math_modeling
- Python: 3.11.11
- Verified versions: NumPy 2.4.4、pandas 3.0.2、SciPy 1.17.1、scikit-learn 1.7.1、matplotlib 3.11.0
- Full import smoke: PASS（同时覆盖 openpyxl、xlrd、PyMuPDF、python-docx、OpenCV、PyYAML、jsonschema 等仓库声明依赖）
- Rebuild limitation: environment.yml 可用，但尚未在一台全新机器/全新环境做 clean rebuild

当前样本量不大，主要成本来自列表型 RSSI 的解析、特征工程、分组验证和稳健性实验；优先按 CPU 可完成路线设计。

## 8. Known Risks

| ID | Risk | Initial control | Stage |
|---|---|---|---|
| R01 | CSV 被 Git 忽略，远程克隆不含 17 个原始数据文件 | manifest 固定名称/大小/SHA-256；换机时从授权来源取得并逐文件校验 | 全程 |
| R02 | 缺少官方数据压缩包总哈希和稳定来源 URL，无法证明本地文件逐字节等同官方发布包 | G0 只声明“本地完整可读”；S1 前补来源/离线备份，禁止夸大真实性 | S0–S1 |
| R03 | training_set_2ap_loc2_nav82.csv 的 test_id 40/41 两行字段错位、目标为空 | 原件保留；S1 冻结隔离规则并记录过滤前后行数 | S1 |
| R04 | training_set_3ap_loc30_nav86.csv 三个 AP0 RSSI 列全空 | S1 分析缺失机制；使用缺失指示、删列或场景化策略必须经合同固定 | S1–S2 |
| R05 | 三条 nss=0 与题面 NSS1/NSS2 不一致 | 检查是否为无有效速率哨兵；不得静默改写 | S1 |
| R06 | 题面 num_ppdu 与表头 num_ampdu、重复 error% 列及两份额外空预测列导致 schema 不统一 | 建立规范字段映射和分问输入白名单 | S1 |
| R07 | RSSI 字段既有长列表也有标量/缺失，长度不一致且含噪声采样 | 保留原字段；比较稳健汇总、分位数、门限越界比例等机理特征 | S1–S2 |
| R08 | 同一 test_id 的多个 AP 行共享场景信息，普通随机按行切分会泄漏 | 以完整 test_id/场景为最小分组单位，切分规则在调参前冻结 | S1–S2 |
| R09 | loc/nav 场景分布有限，随机验证可能高估新拓扑/新位置泛化 | 同时设计分组验证与留一 loc/nav 场景验证，测试集不参与选模 | S1–S4 |
| R10 | Q3 允许使用实测 MCS/NSS，但该权限不能倒灌到 Q1/Q2 或造成目标泄漏 | 建立 Q1/Q2/Q3 分问特征白名单与 lineage | S1–S2 |
| R11 | “影响强弱”容易被模型重要度偷换为因果结论 | 区分预测贡献、条件关联和机理解释，使用多方法稳定性而非单一重要度 | S2–S4 |
| R12 | 题面误差定义和 90% CDF 精度需明确符号、绝对值及系统聚合口径 | S1 明确公式疑点，S2 冻结唯一评估合同 | S1–S2 |
| R13 | 当前无可验证 GPU、内存 13.8 GiB | 使用流式解析和 CPU 统计/树模型 Baseline；复杂模型需证明收益和预算 | 全程 |

## 9. Stage Cadence

| Stage | Relative time | Immediate objective |
|---|---:|---|
| S0 / G0 | 0–1 h | 冻结题目、附件、官方规则、环境、风险和状态 |
| S1 / G1 | 1–5 h | 三问题意拆解、逐字段审计、异常规则和需求矩阵 |
| S2 / G2 | 5–10 h | 统一技术路线、分问模型合同、验证与实验计划 |
| S3 / G3 | 10–28 h | 三问 Baseline 闭环与可重复运行 |
| S4 / G4 | 28–60 h | 针对失败模式改进、对比、消融、敏感性和稳健性 |
| S5 / G5 | 60–75 h | 结果核验、冻结、证据登记和图文交接 |
| S6 / G6 | 75 h–提交 | 论文技术一致性、官方格式和提交检查 |

## 10. S0 Exit Condition

当前 S0 文档和验证证据完成后，仍需：

1. 仅提交本轮活动项目切换与 B 项目 S0 文件；
2. 将固定 commit 推送至 origin；
3. 由独立 Reviewer 对完整 SHA 审核 reviews/gate_0_submission.md；
4. 只有 Reviewer 给出 G0 PASS 或用户明确书面批准，才能把 CURRENT 推进到 S1。

Main Agent 本轮不创建 gate_0_review.md，也不提前实现正式模型或运行调参。