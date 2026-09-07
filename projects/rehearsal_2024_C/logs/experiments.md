# Experiment Log

S0 只允许环境和输入完整性检查；S1 只允许题意与数据审计；S2 只冻结方案、合同和实验计划。本日志尚不包含模型训练、测试集调参或结果选择。

| Time (Asia/Shanghai) | ID | Stage | Purpose | Inputs | Method / command | Result | Status |
|---|---|---|---|---|---|---|---|
| 2026-09-04 21:35 | X0001 | S0 | 验证运行环境 | `math_modeling` | 导入 NumPy、pandas、SciPy、scikit-learn、matplotlib、openpyxl 等核心依赖并输出版本 | Python 3.11.11；核心导入 `smoke=PASS` | PASS |
| 2026-09-04 21:35 | X0002 | S0 | 确认题目正文可读 | `problem/*.docx` | `python-docx` 只读解析段落 | 识别为 2024 C 题，含问题一至问题五、参考文献和备注 | PASS |
| 2026-09-04 21:35 | X0003 | S0 | 确认附件完整并可打开 | `src/*.xlsx` | openpyxl `read_only=True`；记录工作表、行列和 SHA-256 | 附件一至四全部打开；结构与题目描述相符 | PASS |
| 2026-09-04 21:35 | X0004 | S0 | 确认 2024 官方资料可用 | `competition/2024/` | PDF 解析、OLE 文件头、大小、SHA-256 和本地链接检查 | 2 个 PDF、2 个 DOC 及导航文件通过检查 | PASS |
| 2026-09-07 | X0005 | S1 | 首次全量数据审计并校准检查语义 | 题目 DOCX、附件一至四 | `conda run -n math_modeling python projects/rehearsal_2024_C/src/s1_data_audit.py`；openpyxl 只读流式扫描 | 原件哈希稳定；发现题面频率范围小幅偏差；初版错误地把范围偏差列为 Major，且把附件四表头算作已填值 | INVALID — audit rule fixed, data untouched |
| 2026-09-07 | X0006 | S1 | 完成可复核的结构、质量、重复和泄漏审计 | 同 X0005 | 修正检查后重新运行同一命令；输出到 `results/raw/s1/` | 154 checks；0 FAIL、5 WARN；12,400+80+400 条记录元字段/波形无缺失或非有限；训练—测试完全波形重合为 0；输入前后 SHA-256 一致 | PASS |
| 2026-09-07 | X0007 | S2 | 验证总体方案、模型合同与冻结配置的结构可执行性 | `work/04_solution_plan.md`、5 份 Q 合同、共享合同、`work/05_experiment_plan.md`、冻结 JSON | 检查 14 个合同必需章节、JSON 解析和输入哈希、Markdown 链接；在 `math_modeling` 导入计划 API | 5/5 Q 合同结构 PASS；config/hash/link PASS；scikit-learn 1.7.1 API PASS；检测 16 逻辑 CPU；未拟合模型 | PASS |

## No Modeling Results Yet

- 已训练模型：`None`
- 已选择超参数：`None`
- 已生成预测：`None`
- 已查看测试集目标答案：`No evidence / not available`
- `results/raw/s1/` 只含未核验的数据审计证据；S2 只新增文档和冻结配置；`results/verified/` 当前不含正式模型结论。
