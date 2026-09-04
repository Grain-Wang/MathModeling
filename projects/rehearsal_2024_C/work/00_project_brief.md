# Project Brief — rehearsal_2024_C

## 1. Project Identity

- Active project: `projects/rehearsal_2024_C`
- Competition: 2024 年“华为杯”第二十一届中国研究生数学建模竞赛往年题模拟
- Problem: C 题《数据驱动下磁性元件的磁芯损耗建模》
- Current stage: S0 — 项目初始化与约束确认
- Next gate: G0
- Initialization date: 2026-09-04

## 2. Selection Rationale

1. 用户已明确指定本项目为唯一 ACTIVE_PROJECT。
2. 它是仓库中唯一同时具备真实题目和全部数据附件的往年项目。
3. 题目覆盖分类、经验方程修正、因素分析、回归预测和多目标优化，适合验证 S0–S6 / G0–G6 全流程。
4. 当前 `math_modeling` 环境已具备 pandas、NumPy、SciPy、scikit-learn、matplotlib 和 openpyxl，可支持 S1 数据审计和基础模型；复杂方法是否增加依赖，必须在 S2 后按模型合同决定。

## 3. Problem Scope

| 问题 | 核心任务 | 预期输出 |
|---|---|---|
| 问题一 | 从 1,024 点磁通密度序列提取形状特征，识别正弦波、三角波和梯形波 | 分类模型、有效性分析、附件二分类、附件四第 2 列及指定样本结果 |
| 问题二 | 在材料 1、正弦波条件下，为 Steinmetz 方程引入温度修正 | 原方程与修正方程、统一误差比较 |
| 问题三 | 分析温度、励磁波形、材料的独立作用及两两交互作用 | 影响方向、影响程度、最低损耗条件及统计证据 |
| 问题四 | 建立跨材料、温度、频率和波形的磁芯损耗预测模型 | 泛化验证、附件三预测、附件四第 3 列及指定样本结果 |
| 问题五 | 兼顾最小磁芯损耗和最大传输磁能代理量 `频率 × 磁通密度峰值` | 明确变量/约束的多目标优化模型、Pareto 或等价权衡及推荐工况 |

## 4. Confirmed Inputs

- 题目 DOCX 1 个，附件 XLSX 4 个，均已只读打开并记录 SHA-256。
- 训练集含材料 1–4 四个工作表，共 12,400 条数据记录（不含四行表头），每条含 1,024 点周期波形及工况/标签字段。
- 附件二含 80 个分类测试样本；附件三含 400 个损耗预测测试样本；附件四为统一结果表。
- 完整清单与校验值见 [`problem/manifest.md`](../problem/manifest.md)。

## 5. Official Constraints

适用材料为 [`competition/2024/`](../../../competition/2024/README.md) 中的官方邀请函、论文格式规范、提交手册和论文模板。首轮模拟采用以下约束：

1. 使用官方论文模板；最终论文为未压缩 PDF，封面、统一摘要页和正文顺序不变。
2. 除封面外，正文和附件不得出现学校、姓名、学号、队伍编号等身份信息。
3. 摘要不超过两页，覆盖思路、方法、模型、结果、结论和创新点。
4. 以相对 76 小时赛程模拟 2024 年时间线；各阶段仍须通过 Gate 后才能前进。
5. 原始题目和四个 XLSX 不得覆写；附件四必须先复制到结果区后再填充。
6. 测试集不得参与特征选择、调参或模型选择；正式指标只能来自可复现的验证集/交叉验证。

## 6. Working Roles

| Responsibility | Current owner | Boundary |
|---|---|---|
| 项目选择与最终方向确认 | 用户/参赛团队 | 对题号、目标和最终提交负责 |
| S0 初始化与主流程编排 | Main Agent（当前由 Codex 执行） | 生成项目文档和证据，不代替团队确认最终科学结论 |
| 数据、模型与代码 | 待团队指定；S1 前由 Main Agent 编排 | 核心模型须先写模型合同再实现 |
| 图表与论文 | 待团队指定 | 只能使用 `results/verified/` 中已核验结果 |
| Gate 审核 | Reviewer Agent | 基于冻结 commit 独立审核，不修改主成果 |

团队成员姓名与实际分工尚未提供；G1 前应补充，但不阻断 G0 的仓库初始化审核。

## 7. Compute Environment

- OS: Windows
- Conda environment: `math_modeling`
- Python: 3.11.11
- Verified core versions: NumPy 2.4.4、pandas 3.0.2、SciPy 1.17.1、scikit-learn 1.7.1、matplotlib 3.11.0、openpyxl 3.1.5
- Import smoke test: PASS（2026-09-04）
- GPU: 未检测到 `nvidia-smi`，按 CPU 可完成路线规划；不得假设存在 A800。
- Rebuild limitation: `environment.yml` 已可解析，但尚未在全新环境做干净重建。

## 8. Known Risks

| ID | Risk | Initial control | Stage |
|---|---|---|---|
| R01 | 训练集 102.71 MiB、每行 1,024 点，重复全量读取会浪费时间和内存 | S1 建立只读分块/缓存策略，缓存不得覆盖原件 | S1 |
| R02 | 同一工况或相近波形随机拆分可能产生数据泄漏 | 比较随机、分组和工况外推验证；切分规则先于调参冻结 | S1–S2 |
| R03 | 问题二的经验方程拟合可能受对数变换、异方差和温度共线影响 | 保留经典 Steinmetz Baseline，检查残差和分温度外推 | S2–S4 |
| R04 | 问题三的“影响”容易被误写成因果 | 使用有条件的关联/效应表述，报告交互与不确定性 | S2–S5 |
| R05 | 问题四跨材料/工况泛化可能显著弱于同分布验证 | 预先定义分组验证与简单 Baseline，禁止测试集调参 | S1–S4 |
| R06 | 问题五依赖问题四代理模型，外推优化可能给出虚假极值 | 约束在观测域内，做可行性、敏感性与 Pareto 稳定性检查 | S2–S5 |
| R07 | 原始 XLSX 位于 `src/`，与文件协议不一致 | S0 保持只读；后续受控迁移并同步 `.gitignore` 与 manifest | S1 前 |
| R08 | 当前无 GPU | 优先选择 CPU 可完成的统计模型和树模型，复杂模型必须给出时间预算 | 全程 |

## 9. Stage Cadence

| Stage | Relative time | Immediate objective |
|---|---:|---|
| S0 / G0 | 0–1 h | 冻结题目、规则、环境、风险和状态 |
| S1 / G1 | 1–5 h | 题意拆解、数据审计、需求矩阵 |
| S2 / G2 | 5–10 h | 总体方案、模型合同、实验计划 |
| S3 / G3 | 10–28 h | 五问 Baseline 闭环 |
| S4 / G4 | 28–60 h | 主模型、公平对比、消融、敏感性和鲁棒性 |
| S5 / G5 | 60–75 h | 结果核验、冻结、图表与写作交接 |
| S6 / G6 | 75 h–提交 | 论文技术一致性与最终提交检查 |

## 10. S0 Exit Condition

当前文档准备完成后，仍需把 S0 产物冻结到新的 Git commit，并由 Reviewer Agent 对固定 SHA 给出 G0 `PASS`。在此之前不得把 `CURRENT.md` 推进到 S1，也不得开始正式模型选择或调参。
