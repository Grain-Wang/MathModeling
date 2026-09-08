# Experiment Log

本日志记录环境检查、数据审计和模型实验。S0 只允许输入与环境验证，不产生建模结论。

| Time (Asia/Shanghai) | ID | Stage | Purpose | Inputs | Method / Command | Result | Status |
|---|---|---|---|---|---|---|---|
| 2026-09-08 22:10 | X0001 | S0 | 核对题目、数据附件、哈希、结构和当前运行环境 | 1 个 DOCX、13 个训练 CSV、4 个测试 CSV、math_modeling 环境 | DOCX ZIP/XML 只读解析；pandas 只读解析；SHA-256；核心依赖导入；CPU/RAM/GPU 查询 | DOCX 标题与 3 问可读；17/17 CSV 可解析；训练 1,252 行、测试 336 行；无完全重复行；smoke=PASS；已知异常已登记 | PASS_WITH_KNOWN_INPUT_RISKS |

| 2026-09-08T22:48:49+08:00 | X0002 | S1 | 审计器预检与原始输入复核 | 17 个本地 CSV、src/s1_data_audit.py | py_compile；--verify-only；逐文件名/大小/SHA-256；git diff --check | 脚本编译通过；input_verification=PASS；17/17 文件匹配；未写审计结果 | PASS |

| 2026-09-08T23:14:11+08:00 | X0003 | S1 | 正式逐字段数据审计 | commit f4b8b9f；13 个训练 CSV、4 个封存测试 CSV | 审计前后文件名/大小/SHA-256；训练 schema/数值/RSSI/异常/分组审计；测试仅结构与非空计数 | 前后 17/17 PASS 且哈希不变；训练 1,252 -> 1,250 行、482 完整组；测试 336 行；A01-A06 已登记；测试数值摘要为空 | PASS_WITH_WARNINGS |

| 2026-09-08T23:15:54+08:00 | X0004 | S1 | G1 提交前一致性检查 | S1 全部文档、脚本、JSON/MD 证据、Git 索引与本地输入 | py_compile；--verify-only；JSON 断言；必需文件；diff --check；CSV ignore/track；活动项目唯一性 | required_files=PASS；csv_policy=PASS；s1_json_assertions=PASS；B 为唯一 ACTIVE；无校验失败 | PASS |

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

X0001 只证明文件可打开、规模与基础结构可清点、当前环境可运行。缺失模式、字段语义、异常值、数据泄漏和验证切分必须在 S1 另行审计。
