# Experiment Log

本日志记录环境检查、数据审计和模型实验。S0 只允许输入与环境验证，不产生建模结论。

| Time (Asia/Shanghai) | ID | Stage | Purpose | Inputs | Method / Command | Result | Status |
|---|---|---|---|---|---|---|---|
| 2026-09-08 22:10 | X0001 | S0 | 核对题目、数据附件、哈希、结构和当前运行环境 | 1 个 DOCX、13 个训练 CSV、4 个测试 CSV、math_modeling 环境 | DOCX ZIP/XML 只读解析；pandas 只读解析；SHA-256；核心依赖导入；CPU/RAM/GPU 查询 | DOCX 标题与 3 问可读；17/17 CSV 可解析；训练 1,252 行、测试 336 行；无完全重复行；smoke=PASS；已知异常已登记 | PASS_WITH_KNOWN_INPUT_RISKS |

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