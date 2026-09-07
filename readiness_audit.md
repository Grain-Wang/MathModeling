# MathModeling 赛前可用性审计

- 审计日期：2026-09-07（依据远程 G0 审核结果更新）
- 审计目标：判断仓库能否立即开始一轮往年华为杯赛题模拟，并按 S0–S6 / G0–G6 完成闭环。
- 审计方式：实际读取角色、Guide、Reference、模板、环境、脚本、Competition、项目与 Git 状态；使用 `math_modeling` Conda 环境执行依赖导入测试，并核验现有 DOCX/XLSX 资料。

## Overall Verdict: READY WITH MINOR FIXES

仓库的流程设计已经成形，13 份 Guide、Main Agent、Reviewer Agent 和首批方法速查均有实质内容。与上一版审计相比，两个基础问题已经改善：`environment/` 已依据本机实际可用的 `math_modeling` 环境补齐并通过导入冒烟测试；Git 初始提交、远程仓库和大文件忽略策略也已经建立。

2024 年官方规则、提交手册、论文格式规范和论文模板已归档到 `competition/2024/`。用户已唯一指定 `projects/rehearsal_2024_C`；Reviewer 已对远程固定快照 `c99ca0f7f7a238fac501836cd06dfd0b6aaabebe` 给出 G0 `PASS`。项目已完成 S1 三份强制文档和可重复的只读数据审计；Reviewer 对固定快照 `96313b5...` 给出 G1 PASS，现已获准进入 S2。仓库级自动化仍有下列非阻断缺口。

## 检查结果总览

| 检查项 | 状态 | 实际证据 | 对开赛的影响 |
|---|---|---|---|
| `.agents/` | PARTIAL | `main_agent.md`、`reviewer_agent.md` 内容完整；`skills/` 无文件；`prompts/` 只有 Reference Curator Prompt；根 `AGENTS.md` 仅为极简占位 | 角色规则可人工读取，但缺少 Main 启动、Reviewer Gate 调用入口及 Skill 状态说明 |
| `guide/` | PASS（文档层） | 13/13 个 Guide 非空，覆盖环境、项目创建、Agent 工作流、Gate、实验、核验、绘图、论文交接、AI 日志和最终提交 | 主题覆盖完整；其中引用的部分模板和脚本尚未实现 |
| `reference/` | PASS FOR FIRST DATA-DRIVEN RUN | 共 20 份方法文档；覆盖数据处理、统计、机器学习、时间序列、线性/整数优化、评价和敏感性分析 | 足以支撑 2024 C 的数据审计、Baseline 和验证，但不是全题型知识库 |
| `templates/project_template/` | FAIL | 模板目录为空 | 无法按 Guide 复制出符合协议的新项目 |
| `environment/` | PASS WITH QUALIFICATION | `environment.yml`、`requirements.txt`、`README.md` 已非空；YAML 解析通过；实际环境导入测试为 `smoke=PASS` | 当前机器可立即运行基础数据建模；尚未在全新环境做干净重建测试 |
| 环境自动验证 | FAIL | `scripts/verify_environment.py` 仍为 0 bytes | README 中有可执行人工冒烟命令，但仓库尚无标准化一键验证报告 |
| `competition/` | PASS（2024） | `competition/2024/` 已归档官方邀请函、提交手册、论文格式规范和论文模板，并记录来源、大小与 SHA-256 | 2024 往年题模拟所需的规则、格式和提交资料已具备 |
| `projects/` 顶层结构 | PASS FOR ACTIVE PROJECT | ACTIVE_PROJECT 唯一；G0、G1 均 PASS，当前阶段 S2、下一 Gate G2；另外两个项目未激活 | 启动歧义与 S2 前置 Gate 均已解除 |
| 项目深层结构 | PASS THROUGH S1 | 活动项目已有 S0 manifest/简报、G0 PASS、三份 S1 强制文档、审计脚本与 raw 证据，且 G1 已 PASS | 当前可执行 S2；模型合同和实验计划应在本阶段建立 |
| 可用往年题 | PASS | 2024 C 题 DOCX 与 4 个 XLSX 已全量只读审计；154 项检查 0 FAIL/5 WARN，输入前后 SHA-256 一致 | 数据足以进入方案设计；轻微频率越界、1 条重复和验证泄漏风险已登记 |
| Git / Reviewer Gate | PASS | G0、G1 均按远程固定 SHA 审核为 PASS；`gate_1_review.md` 已写回 | Gate 机制可执行；G2 PASS 前不得进入 S3 |
| 大文件管理 | PASS | 本地 4 个 XLSX 均命中 `.gitignore`；Git 跟踪的 XLSX 数为 0 | 大型赛题数据保留在本地，不进入提交历史；后续应以 manifest/哈希描述其来源与完整性 |
| 复用脚本 | FAIL | `create_project.py`、`verify_environment.py`、`collect_results.py`、`final_check.py` 均为空 | 项目创建、环境核验、结果汇总和最终检查仍不能自动执行 |

## 环境专项核验

本次使用的环境是现有 Conda 环境 `math_modeling`，不是根据文件名推测出的环境。核验结果如下：

- Conda 25.5.1，Python 3.11.11；
- 核心科学计算：NumPy 2.4.4、pandas 3.0.2、SciPy 1.17.1、scikit-learn 1.7.1；
- 绘图与文件处理：matplotlib 3.11.0、openpyxl 3.1.5、xlrd 2.0.2、PyMuPDF 1.28.0、python-docx 1.2.0、OpenCV 4.13.0；
- 配置和资料工具：PyYAML、jsonschema、python-dotenv、requests、bibtexparser、conda-lock；
- 以上包的实际导入测试全部通过，输出 `smoke=PASS`；
- `environment/environment.yml` 已固定当前直接依赖版本，不包含机器专属 `prefix`；`requirements.txt` 仅作为 pip 兼容参考；
- 当前未包含 statsmodels、seaborn、XGBoost、LightGBM、CVXPY、OR-Tools、SymPy 和 PyTorch。它们是按题型选择的可选能力，不应在未确定路线前盲目加入；
- 尚未在一台干净机器或全新 Conda 环境中重建，因此目前证明的是“当前环境可用、声明文件可解析”，还不是完整的跨机器复现证明。

## Critical Missing

`None`。此前的 ACTIVE_PROJECT 与 S0 初始化缺口已补齐。

`None`。G0、G1 已由独立 Reviewer 在远程固定快照上给出 PASS，当前没有阻止 S2 的 Critical 缺失。

## Major Missing

### M1. 项目模板和创建脚本为空

`templates/project_template/` 没有可复制内容，`scripts/create_project.py` 为 0 bytes。Guide 中的新项目创建流程无法执行，也无法保证后续项目自动符合 Main Agent 的目录协议。

### M2. 环境恢复尚缺自动验证和干净重建证据

环境声明和人工冒烟测试已经完成，但 `scripts/verify_environment.py` 为空，也未用 `environment.yml` 创建一个全新测试环境。建议实现只读检查脚本，输出 Python/依赖版本、核心导入结果和可选能力；随后至少完成一次干净重建或 CI 重建。

### M3. Agent 启动入口与 Skill 状态不完整

两份角色文件可用，但根 `AGENTS.md` 没有完整路由，缺少 Main 启动 Prompt 和 Reviewer Gate Prompt；`.agents/skills/` 没有清单、版本或测试记录。Skill 不必为凑数量安装，但应明确首轮是否有硬依赖，并留下验证结论。

### M4. 现有项目与标准深层路径不一致

活动项目的 S0 文档已经建立，但原始 XLSX 仍位于 `src/`，而文件协议规定原始题目数据应进入 `problem/data/` 或 `problem/attachments/`。manifest 已登记这一偏差并将原件设为只读；模型合同、实验分类和交接目录应在进入相应阶段前建立。移动大文件前须保留受控备份并同步 `.gitignore` 与 manifest。

### M5. 结果汇总和最终检查脚本为空

`collect_results.py` 与 `final_check.py` 无法支撑 S5/G5 和 S6/G6。它们不阻止完成 S0，但会阻止整轮模拟形成完整闭环。

### M6. 根 README 仍缺少成员启动入口

根 README 没有清晰说明 ACTIVE_PROJECT、启动顺序、环境恢复命令、Gate 入口和大文件策略。仓库规则目前分散在多份 Guide 中，新成员很难从一个入口开始。

### M7. 计算资源假设与当前机器不一致

Main Agent 的 G2 标准硬编码“单张 A800”，但当前系统未检测到 `nvidia-smi`。资源约束应以 `work/00_project_brief.md` 中实际声明并验证的设备为准，A800 只能作为可选上限或示例。

## Minor Improvements

1. `reference/` 对 2024 C 已够用，但 `reference/modeling/` 与 `reference/visualization/` 为空，优化类只有 LP/MILP；可按后续赛题需求补充，不阻塞首轮 S0。
2. 在环境经过干净重建后，可使用现有 `conda-lock` 为目标平台生成锁文件，提高正式比赛期间的可复现性。
3. 为两个空项目增加 `INACTIVE` 或占位说明；当前 ACTIVE_PROJECT 已唯一明确，因此这不再阻塞首轮演练。
4. 当前 manifest 已记录本地题目和附件的 SHA-256、文件名、大小与校验日期；后续如找到稳定的原始下载地址，可追加来源 URL。
5. 在 G4 前补充最终图的字体、尺寸、色彩、分辨率和导出检查标准。

## 推荐在开始往年题模拟前必须补齐的最小修改清单

G1 已 PASS，当前没有进入 S2 前必须补齐的阻断项。S2 必须至少完成：

1. 覆盖 Q1–Q5 且说明数据流的统一总体方案；
2. 每问可执行的模型合同，含 Baseline、评价、约束和失败条件；
3. 在调参前冻结切分、指标、随机种子、计算预算和回退规则的实验计划；
4. 形成固定 SHA 的 G2 submission，等待 Reviewer PASS 后再进入 S3。

建议尽早但不阻塞当前项目 G1 的仓库级修复：实现非破坏性的 `scripts/verify_environment.py`；增加 Main 启动 Prompt、Reviewer Gate Prompt 和 Skill 依赖声明。

模板、项目创建脚本、结果收集脚本和最终检查脚本仍应补齐，才能把仓库整体提升为完整的 `READY`；但它们可在首轮既有项目进入相应阶段前逐步完成。

## 建议选择的第一轮演练项目

已确定 `projects/rehearsal_2024_C/`，即 2024 年 C 题“数据驱动下磁性元件的磁芯损耗建模”。

理由：

- 它是当前唯一同时具备真实题目和附件的往年项目；
- 题目 DOCX 和 4 个 XLSX 已实际读取验证；
- 现有 `math_modeling` 环境已具备 pandas、SciPy、scikit-learn、matplotlib、openpyxl 和 OpenCV，可立即承担数据审计、特征处理、回归 Baseline 与可视化；
- 当前 Reference 已覆盖缺失/异常/泄漏、线性回归、随机森林、梯度提升、评价指标和敏感性分析，与该题首轮路线匹配。

不建议选择 `rehearsal_2024_A` 或 `contest_2026_X`：两者目前只有空骨架，没有可验证的题目、数据或初始化状态。

## 审计结论

仓库仍为 `READY WITH MINOR FIXES`：2024 年官方资料、基础环境、Git/Gate 基线和 `rehearsal_2024_C` 的 S0–S1 产物均已具备，G0/G1 已 PASS，当前可执行 S2。待仓库级模板/自动脚本补齐且完整 S0–S6 闭环经过演练后，再评为完整 `READY`。
