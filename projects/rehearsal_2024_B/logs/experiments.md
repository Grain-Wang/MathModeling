# Experiment Log

本日志记录环境检查、数据审计和模型实验。S0/S1 只允许输入、题意和数据合同验证，不产生建模结论。

| Time (Asia/Shanghai) | ID | Stage | Purpose | Inputs | Method / Command | Result | Status |
|---|---|---|---|---|---|---|---|
| 2026-09-08 22:10 | X0001 | S0 | 核对题目、数据附件、哈希、结构和当前运行环境 | 1 个 DOCX、13 个训练 CSV、4 个测试 CSV、math_modeling 环境 | DOCX ZIP/XML 只读解析；pandas 只读解析；SHA-256；核心依赖导入；CPU/RAM/GPU 查询 | DOCX 标题与 3 问可读；17/17 CSV 可解析；训练 1,252 行、测试 336 行；无文件内完全重复行；smoke=PASS；已知异常已登记 | PASS_WITH_KNOWN_INPUT_RISKS |
| 2026-09-08T22:48:49+08:00 | X0002 | S1 | 审计器预检与原始输入复核 | 17 个本地 CSV、src/s1_data_audit.py | py_compile；--verify-only；逐文件名/大小/SHA-256；git diff --check | 脚本编译通过；input_verification=PASS；17/17 文件匹配；未写审计结果 | PASS |
| 2026-09-08T23:14:11+08:00 | X0003 | S1 | G1/R1 正式逐字段数据审计 | commit f4b8b9f；13 个训练 CSV、4 个封存测试 CSV | 审计前后文件名/大小/SHA-256；训练 schema/数值/RSSI/异常/分组审计；测试仅结构与非空计数 | 前后 17/17 PASS 且哈希不变；训练 1,252→1,250 行、482 个行数完整组；测试 336 行；A01–A06 登记；测试数值摘要为空 | PASS_WITH_WARNINGS |
| 2026-09-08T23:15:54+08:00 | X0004 | S1 | G1/R1 提交前一致性检查 | S1 文档、脚本、JSON/MD、Git 索引与本地输入 | py_compile；--verify-only；JSON 断言；必需文件；diff --check；CSV ignore/track；活动项目唯一性 | required_files=PASS；csv_policy=PASS；s1_json_assertions=PASS；B 为唯一 ACTIVE；无校验失败 | PASS |
| 2026-09-09T10:48:56+08:00 | X0005 | S1 | G1/R2 正式身份、重复与 Q3 两级目标审计 | 干净 commit affff4f；13 个训练 CSV、4 个封存测试 CSV | 编译与 verify-only；输入前后文件名/大小/SHA-256；严格 AP 身份；跨文件规范化 SHA-256 行/组指纹；系统目标可构造性 | 17/17 前后 PASS 且哈希不变；训练 1,252→1,250 行、482/482 eligible 严格组；测试 136/136；跨文件行/组簇 0；Q3 训练 AP/系统 1,250/482，测试 185/75；测试数值分布仍封存 | PASS_WITH_WARNINGS |
| 2026-09-09T10:44:03+08:00 | X0006 | S1 | G1/R2 提交前全套一致性检查 | Round 2 文档、脚本、5 个机器证据文件、Git 索引与本地输入 | py_compile；--verify-only；正式提交谱系、严格身份、重复、Q3、测试封存 JSON 断言；必需文件；CSV ignore/track；活动项目；diff --check | required_files、formal_audit_lineage、strict_identity、duplicate_scope、q3_contract、sealed_test、csv_policy、active_project、diff_check 全部 PASS | PASS |
| 2026-09-09T10:52:09+08:00 | X0007 | S1 | 新增 source_file 非空断言后的最终 G1/R2 校验 | 正式审计 commit affff4f、Round 2 全部交付物 | 重跑 X0006 全套断言，并显式检查 eligible、官方测试、Q3 测试及逐测试文件的 null_source_file_row_count | formal_audit_lineage、source_test_ap_identity、strict_identity、duplicate_scope、q3_contract、sealed_test、csv_policy、active_project、diff_check 全部 PASS | PASS |

## X0001 Environment Snapshot

- OS: Microsoft Windows 11 专业版，64 位，版本 10.0.26200
- CPU: AMD Ryzen 7 8745H，8 核 / 16 逻辑处理器
- RAM: 13.8 GiB 可见内存
- GPU: nvidia-smi 未检测到，按 CPU 路线规划
- Conda environment: math_modeling
- Python: 3.11.11
- NumPy: 2.4.4
- pandas: 3.0.2
- SciPy: 1.17.1
- scikit-learn: 1.7.1
- matplotlib: 3.11.0
- Full import smoke: PASS

## Boundary

X0001 只证明文件可打开、规模与基础结构可清点、当前环境可运行。X0002–X0006 只验证 S1 题意、数据和交付合同。尚未拟合模型、调参或生成官方测试预测。

| 2026-09-09T11:50:06+08:00 | X0008 | S2 | 正式 S2 合同、切分与 Q3 指标校验 | 干净 commit 6b88cd1；13 个训练 CSV；17 个输入仅做哈希校验 | py_compile；输入前后 verify；A01 后严格身份；3×5 外层和嵌套 3 折注册；13 折 LOSO；Q2 固定标签；Q3 合成单测 | PASS；1,250 行/482 组；15 外层折；1,446/5,784 外/内分配；13 LOSO；17 标签；registry SHA E1DE3911…；model_fit=0；test numeric reads=0 | PASS |

| 2026-09-09T11:56:04+08:00 | X0009 | S2 | G2 提交前全套一致性检查 | S2 方案/三问合同/O1、机器配置、正式结果、日志、Git 索引与本地原始输入 | 14 个合同必备标题；O1 决策；JSON/切分计数；占位符/Parquet；gate_2_review 边界；CSV track/ignore；diff --check；verify-only | headings、O1、formal evidence、CSV policy、placeholder、review boundary、diff 和 contract validation 全部 PASS；无模型拟合、无官方测试数值读取 | PASS |

| 2026-09-09T14:54:01+08:00 | X0010 | S2 | G2/R2 机器合同 v2 预检 | 修订后人工合同、配置 v2、13 个训练 CSV 身份；官方测试仅哈希验证 | py_compile；--verify-only；outer/downstream-inner/nested-upstream/LOSO registry；合同哈希；泄漏与测试释放负向 fixture | PASS；primary/LOSO nested assignments 均 11,568；lineage batches=409；合同哈希、Q3、lineage、test guard 全 PASS；model_fit=0、test numeric read=0 | PASS |

| 2026-09-09T14:58:08+08:00 | X0011 | S2 | G2/R2 正式合同、nested lineage 与测试释放门禁审计 | 干净 commit 43a8566；13 个训练 CSV；六份 SHA 锁人工合同；官方测试仅做 S1 哈希校验 | 输入前后 verify；outer/downstream-inner/nested-upstream；source-blind LOSO；409 lineage batches；泄漏和 test guard 负向 fixture | PASS；outer/inner/nested=1,446/5,784/11,568；LOSO=13，inner/nested=5,784/11,568；两类 fit overlap=0；registry SHA 88B108D1…；model_fit/test reads/test predictions=0/0/0 | PASS |

| 2026-09-09T15:03:48+08:00 | X0012 | S2 | G2/R2 提交前全套一致性检查 | Round 2 人工/机器合同、正式结果、response/submission、Git 索引与本地 17 CSV | py_compile；verify-only；正式 metadata/计数/零交集；负向 tests；遗留冲突；合同哈希；gate review 边界；CSV track/ignore；active project；diff --check | 全部 PASS；正式 HEAD=43a8566 且运行前 clean；17 CSV 全忽略/0 tracked；无 gate_2_review_r2；无模型拟合或测试数值读取 | PASS |

| 2026-09-09 | X0013 | S3 | 真实 S3 入口无拟合预检 | G2/R2 PASS、13 个训练 allowlist、四个官方测试注入用例、合同与 split registry | py_compile；s3_baseline.py --verify-only；guard 在任何 CSV 数值解析前执行 | PASS；合法训练 manifest 接受，四个官方测试逐一注入均拒绝；model_fit=0、CSV numeric read=0、official test read/prediction=0/0 | PASS |
| 2026-09-09 | X0014 | S3 | 全量 Baseline 开发试跑与实现调试 | 13 个训练 CSV；冻结 15 outer + 13 LOSO；八个固定 Baseline；开发 bootstrap=1/10 | 共享特征引擎、Q1 折内 OOF、Q2 固定 17 类、Q3 AP→system；开发迭代修正字段路径和固定标签 log-loss | 最终开发闭环 PASS：1,250 行/482 组、312 特征、112 lineage、327 fits、test read/prediction=0/0；默认 Ridge 出现 86 条 LinAlgWarning，已改 LSQR；开发产物不作为正式证据并在干净运行前删除 | DEVELOPMENT_ONLY |
