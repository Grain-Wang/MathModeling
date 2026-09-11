# AI Usage Log

| Time (Asia/Shanghai) | Tool / Model | User | Task | Main input / prompt | Output use | Adopted | Human verification |
|---|---|---|---|---|---|---|---|
| 2026-09-08 22:10 | OpenAI Codex | 仓库维护者 | 审查 B 项目可开题性并按仓库协议完成 S0 初始化 | 用户要求检查项目完备性，随后要求按建议依次完成至进入 G0 审查；输入包括 Main Agent/Guide、题目 DOCX、17 个 CSV、2024 官方资料和 C 项目已审核结构 | 切换 ACTIVE_PROJECT、整理原始数据路径、建立 manifest/项目简报/日志/CURRENT/G0 submission，并生成只读验证证据 | Yes | 文件数量、SHA-256、DOCX 三问、CSV 行列/标签边界、环境版本和 Git 状态均由本机命令复核；数据异常不在 S0 擅自修复，待 Reviewer 与 S1 决策 |
| 2026-09-08T22:48:49+08:00 | OpenAI Codex | 仓库维护者 | 拉取 G0 审核并启动 S1 | 用户要求 pull 远程 G0 结果后继续；输入为 G0 review、题目约束、manifest 与本地 17 个 CSV | 接受 G0 PASS，建立恢复说明和 S1 审计器，冻结 A01-A04、泄漏和验证边界 | Yes | py_compile、17 文件全量大小/SHA-256、Git ignore/status 均由本机复核；正式审计将在干净实现 commit 上运行 |
| 2026-09-08T23:14:11+08:00 | OpenAI Codex | 仓库维护者 | 完成 S1 题意拆解、数据审计与 G1 审核包 | 题面、17 个本地 CSV、G0 review、manifest、仓库指南和正式审计 JSON | 形成三份 work 文档、A01-A06 合同、测试封存/OOF/分组验证边界、G1 submission 与 CURRENT | Yes | 正式审计在干净 f4b8b9f 上运行；输入前后哈希、组完整性、测试摘要为空及文档一致性由本机命令复核；未拟合模型或生成测试预测 |
| 2026-09-09T10:39:37+08:00 | OpenAI Codex | 仓库维护者 | 根据 G1/R1 审核意见完成 Round 2 修订 | 用户指定审核 commit e9253ce 并要求按改进计划执行；输入包括 gate_1_review、题面、S1 文档、审计脚本和本地 17 个 CSV | 冻结 Q3 AP/系统两级输出与 signed CDF/ERROR_90 合同；实现严格 AP 身份和跨文件指纹；重跑干净审计；形成 response/submission | Yes | 正式审计基于干净 affff4f；17/17 哈希前后 PASS；identity/q3 JSON 关键计数、测试封存、CSV ignore、Git 差异和门禁状态由本机命令复核；未进入 S2 或拟合模型 |

| 2026-09-09T11:51:36+08:00 | OpenAI Codex | 仓库维护者 | 拉取 G1/R2 PASS 并完成 S2、O1 与 G2 审核包 | 用户指定 review commit fd6e33b 并要求按意见继续；输入包括 G1 review、题目 DOCX、S1 证据、仓库协议和本地训练 CSV | 修正 nav 单位；编写统一方案、三问合同、实验/机器配置；生成严格外/内/LOSO 注册表与 Q3 指标单测；完成 O1 和 G2 submission | Yes | 正式验证来自干净 6b88cd1；输入哈希、严格组、固定标签、分割数量、合成指标、CSV ignore、Git 状态和零训练/零测试数值读取均由本机命令复核 |

| 2026-09-09T14:59:02+08:00 | OpenAI Codex | 仓库维护者 | 根据 G2/R1 REVISE 完成 Round 2 修订 | 用户指定 review commit fe959af 并要求按计划改进；输入包括 gate_2_review、S2 人工/机器合同、split registry、角色与实验协议 | 删除提前测试推理；新增 run-manifest guard；固定 Q1-B1 bounded 上游；生成 primary/LOSO 第三层分割和 409 批血缘；统一 repeat/bootstrap/raw-bounded；锁定合同 SHA；形成 response/submission R2 | Yes | 正式验证来自干净 43a8566；合同/输入哈希、分割计数、两个零交集、泄漏负例、测试门禁、CSV ignore 和零模型/零测试读取均由本机命令复核 |

| 2026-09-09 | OpenAI Codex | 仓库维护者 | 拉取 G2/R2 PASS，完成 S3 Baseline、O2 与 G3 审核包 | 用户指定 review commit 6504c54 并要求继续；输入包括 G2/R2 review、冻结合同/切分、题目、本地 13 个训练 CSV 和 4 个封存测试文件的哈希 | 实现真实入口门禁、312 特征、八个 Baseline、15 outer/13 LOSO、实际 Q1 血缘、bootstrap、独立验证器、Baseline 报告、O2 诊断和 G3 submission | Yes | 正式模型运行来自干净 2222cf5；327 fits、warning=0；独立重算 83 项检查通过；17/17 输入哈希匹配，测试只做字节校验且数值读取/预测=0/0；S4 未启动 |

| 2026-09-09 | OpenAI Codex | 仓库维护者 | 拉取 G3 PASS，完成 S4 主模型、O3 与 G4 审核包 | 用户指定 review commit a543325 并要求进入下一阶段；输入包括 G3 review、冻结合同/切分、S3 Baseline、本地 13 个训练 CSV；官方测试只做哈希 | 实现并运行 Q2/Q3 受限 HGB 候选、nested lineage、LOSO、bootstrap、失败/消融/敏感性证据、独立验证器；冻结 Q1-B1+Q2-B1A+Q3 unified；形成 work/07–09、O3 和 G4 submission | Yes | 正式运行来自 clean 3295667；1,751 fits、0 warnings；独立复算 74 项 PASS；CSV 17 ignored/0 tracked，正式源码无漂移，测试 numeric read/prediction=0/0；未进入 S5 或写 results/verified |

| 2026-09-11 | OpenAI Codex | 仓库维护者 | 拉取 G4 PASS，完成 S5 结果冻结、exactly-once 发布与 G5 审核包 | 用户指定 review commit 70d6a14 并要求按审核进入下一轮；输入包括 G4 review、S3/S4 traces/OOF/metrics、冻结合同、本地 13 个训练 CSV 与 4 个测试 CSV | 实现独立选择/promotion 重算、完整 freeze manifest、真实磁盘 ledger guard、全量冻结模型、唯一官方测试推理、release 后核验、Evidence registry 和图文交接 | Yes | pre-release 测试 numeric read=0；正式 release 4 fits/0 warnings、13 train + 4 test reads；success count=1；10+12 项 release 检查 PASS；第二次 release guard 硬失败；未依据无标签预测反馈调模，未进入 S6 |
