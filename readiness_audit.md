# MathModeling 赛前可用性审计

- 审计日期：2026-09-04
- 审计目标：判断仓库能否立刻开始一轮往年华为杯赛题模拟，并按 S0–S6 / G0–G6 完成闭环。
- 审计方式：实际读取角色文件、13 份 Guide、Reference 文档、模板/环境/脚本状态、Competition、项目结构与 Git 状态；对 Conda 环境做导入冒烟测试，并只读打开现有 DOCX/XLSX 资料。

## Overall Verdict: NOT READY

仓库已经具备较完整的**流程设计**：Main Agent、Reviewer Agent、Guide 和首批 Reference 均有实质内容；但关键的**执行资产**仍为空或缺失。当前无法满足 Main Agent 的 G0 起点要求，也无法执行 Reviewer 所规定的固定 commit 远程审核流程，因此不应直接进入 S1 或开始正式建模。

这不是需要大规模重构的问题。补齐比赛规则、可恢复环境、项目初始化、模板、Git/LFS 和 Agent 入口后，仓库可较快达到 `READY WITH MINOR FIXES`；首轮应选择现有资料完整且已验证可读取的 `projects/rehearsal_2024_C/`。

## 检查结果总览

| 检查项 | 状态 | 实际证据 | 对开赛的影响 |
|---|---|---|---|
| `.agents/` | PARTIAL | `main_agent.md` 与 `reviewer_agent.md` 均完整；`skills/` 为 0 个文件；`prompts/` 只有 Reference Curator；根 `AGENTS.md` 仅 38 bytes | 角色制度可读，但没有自动入口、主执行 Prompt、Gate 调用 Prompt 或已测试 Skill |
| `guide/` | PASS（文档层） | 13/13 个 Guide 非空，覆盖环境、Skill、建项目、文件协议、Main、Reviewer、实验、核验、绘图、论文交接、AI 日志和提交 | 主题覆盖完整；多处引用的模板和脚本尚未实现 |
| `reference/` | PASS FOR FIRST DATA-DRIVEN RUN | 20 份方法文档全部具有 13 节结构；数据处理 4、统计 5、机器学习 4、时间序列 4、优化 1、评价 2 | 足够支持 2024 C 的数据驱动 Baseline 与验证；尚不是全题型库 |
| `templates/project_template/` | FAIL | 目录完全为空 | `guide/03_create_new_project.md` 的“复制模板”无法执行 |
| `environment/` | FAIL | `environment.yml`、`requirements.txt`、`README.md` 均为 0 bytes；`verify_environment.py` 为空 | 无法从仓库恢复或验证 `math_modeling` 环境 |
| 当前 Conda 环境 | PARTIAL | `math_modeling` 存在，Python 3.11.11；NumPy、pandas、SciPy、scikit-learn、matplotlib、openpyxl 可用；statsmodels、seaborn、XGBoost、LightGBM、CVXPY、OR-Tools、SymPy、PyTorch 未安装 | 可做基础表格分析，但仓库未声明最小依赖，部分 Reference 和优化/时序路线不可直接运行 |
| `competition/` | FAIL | `rules/`、`submission/`、`official_templates/` 均为空；`ai_policy/` 不存在；无 Competition README | Main Agent 的 S0/G0 无法确认官方规则、AI 合规、模板和提交要求 |
| `projects/` 顶层结构 | PARTIAL | 三个项目均有题目要求的 10 个顶层区域，但 `CURRENT.md` 全部为 0 bytes | 多项目并存且无明确 ACTIVE_PROJECT；启动协议无法执行 |
| 项目深层结构 | FAIL | 每个项目均缺少 Main Agent 标准中的 `problem/data`、`problem/attachments`、`manifest.md`、`work/models`、`work/handoff`、六类实验目录和三类日志等 18 项 | S0 交付物、模型合同、实验分类和交接路径不能直接落地 |
| 可用往年题 | PARTIAL | `rehearsal_2024_C` 的题目 DOCX 与 4 个 XLSX 均可打开；另外两个项目无题目资料 | 有唯一现实候选，但附件位置和项目状态尚未规范化 |
| Git / Reviewer Gate | FAIL | 当前分支 `master` 无 `HEAD` commit、无 remote，所有内容未跟踪 | Reviewer 要求的固定 SHA、远程读取、冻结分支和写回审核均无法执行 |
| 大文件管理 | FAIL | `.gitignore` 为空；Git LFS 已安装但无 `.gitattributes`；训练集为 107,702,460 bytes（102.71 MiB） | 按 Guide 执行 `git add .` 会纳入大文件，普通 GitHub push 将被 100 MiB 单文件限制阻断 |
| 复用脚本 | FAIL | `create_project.py`、`verify_environment.py`、`collect_results.py`、`final_check.py` 均为 0 bytes | 创建、环境验证、结果汇总和最终检查目前只有文件名，没有可执行能力 |

## Critical Missing

### C1. Competition 官方约束完全缺失

Main Agent 在 S0 强制要求读取适用的官方规则、AI 规则、论文模板和提交要求；Reviewer G0 也将其列为通过条件。当前三个 Competition 子目录为空，`competition/ai_policy/` 甚至不存在，因此无法证明合规，也无法通过 G0。

最小修复：为 2024 往年模拟补入可追溯的官方规则、AI 使用规定、提交说明和论文模板；增加 `competition/README.md`，明确该目录严格只读、文件来源、适用年份和各子目录职责。

### C2. 环境不能由仓库恢复，也不能按仓库脚本验证

`environment/environment.yml`、`requirements.txt`、`environment/README.md` 和 `scripts/verify_environment.py` 都为空。虽然本机已有同名 Conda 环境并可导入基础数据包，但这只是机器当前状态，不是可复现证据；冒烟测试还发现 `statsmodels` 等常见路线依赖缺失。

最小修复：从实际可用环境整理一份最小、带版本范围的 `environment.yml`，明确哪些包是核心、哪些是按题型可选；实现非破坏性的环境检查脚本，至少检查 Python、NumPy、pandas、SciPy、scikit-learn、matplotlib、openpyxl，并根据首轮路线决定是否把 statsmodels 加入核心依赖。

### C3. Reviewer Gate 的 Git 前提不成立，且现有大文件会阻断普通 GitHub push

Reviewer Agent 明确要求固定完整 commit SHA、远程 GitHub 仓库、冻结分支和审核写回。当前仓库没有首个 commit，也没有 remote。训练集 102.71 MiB，超过 GitHub 普通 Git 仓库的 100 MiB 单文件限制；Git LFS 虽已安装，但没有任何跟踪规则。参见 [GitHub 官方大文件说明](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)。

最小修复：先确定原始赛题数据策略——使用 Git LFS 跟踪 XLSX，或在 Git 中只保存 manifest、哈希和受控下载位置；随后补齐 `.gitignore`/`.gitattributes`，创建首个 commit、配置 remote，并实际验证一次固定 SHA 可被 Reviewer 读取。不要在策略确定前执行 `git add .`。

### C4. 没有可启动的 ACTIVE_PROJECT / S0 状态

三个项目的 `CURRENT.md` 全为空，仓库又没有其他活跃项目指示。Main Agent 明确禁止在多项目情况下自行猜测；`rehearsal_2024_C` 也缺少 `problem/manifest.md`、`work/00_project_brief.md` 和三份日志。因此即使题目文件存在，也不能按角色协议直接从 S1 开始。

最小修复：明确选择 `projects/rehearsal_2024_C/`，将其 `CURRENT.md` 初始化为 S0，并创建题目清单、项目简报、决策/实验/AI 日志；完成 G0 submission 后再进入 S1。

## Major Missing

### M1. 项目模板和创建脚本均为空

`templates/project_template/` 没有任何文件或目录，`scripts/create_project.py` 为 0 bytes。Guide 的项目创建流程不可执行，也无法保证新项目与 Main Agent 的标准结构一致。

建议：只做小范围脚手架补齐。模板应至少包含 `CURRENT.md`、`problem/{data,attachments,manifest.md}`、`work/{models,revisions,handoff}`、六类 `experiments/` 子目录、`results/{raw,verified}`、`figures/{scripts,data,final}`、`paper/`、`reviews/` 和三份日志；创建脚本只负责复制、替换项目名并拒绝覆盖现有项目。

### M2. Agent 角色完整，但启动入口与 Skill 状态不完整

`.agents/roles/` 的两份角色文件足够详细；但根 `AGENTS.md` 没有指示自动读取 Main Agent，`.agents/prompts/` 缺少 Main 启动 Prompt 和 Reviewer Gate Prompt，`.agents/skills/` 没有 Skill、清单、版本或演练记录。现有 Reference Curator Prompt 与具体赛题模拟不是同一用途。

建议：让根 `AGENTS.md` 只承担最小路由和权限说明；新增可复制使用的 Main 启动与 Reviewer Gate Prompt。Skill 不必为凑数量安装，但必须二选一：列出并测试首轮所需 Skill，或明确记录“首轮无硬性 Skill 依赖、使用普通 Python 工具链”。

### M3. 现有项目与 Main Agent 的标准深层路径不一致

三个项目只有顶层骨架，缺少模型合同、交接和实验分类目录。`rehearsal_2024_C` 的 4 个原始 XLSX 位于 `src/`，而 `guide/04_project_file_protocol.md` 和 Main Agent 都规定原始题目数据应位于 `problem/`，`src/` 用于代码。

建议：在首轮项目内补齐缺失深层目录；将附件按受控方式归入 `problem/data/` 或 `problem/attachments/`，在 manifest 记录原文件名、大小、哈希与可打开状态。移动前保留备份，之后将原始文件视为只读。

### M4. 结果汇总和最终检查脚本为空

`collect_results.py` 与 `final_check.py` 目前无法支撑 S5/G5 和 S6/G6。它们不阻止完成 S0，但会阻止完整演练闭环。

建议：可在首轮开始后实现，但最迟在进入 S3 前定义接口，在进入 S5 前完成最小可执行版本。

### M5. 根 README 与 `.gitignore` 为空

仓库没有面向成员的启动入口，也没有缓存、临时结果、环境文件、Office 临时文件和大数据的版本策略。结合 Guide 中的 `git add .` 建议，这一缺口有直接操作风险。

建议：根 README 只需提供启动顺序、ACTIVE_PROJECT 规则、常用命令和 Gate 入口；`.gitignore` 与 Git LFS/数据策略应一起设计，避免互相冲突。

### M6. 计算资源假设与当前机器不一致

Main Agent 的 G2 标准硬编码“单张 A800”，但当前系统未检测到 `nvidia-smi`。这会让可完成性审核基于不存在的资源。

建议：把角色中的硬编码资源改为“以 `work/00_project_brief.md` 中实际声明并验证的计算资源为准”，A800 仅作为可选上限或示例。

## Minor Improvements

1. Reference 对 2024 C 已够用，但 `reference/modeling/` 与 `reference/visualization/` 为空，优化只有 LP/MILP；后续可补非线性回归、类别编码、模型校准、Monte Carlo、ODE、鲁棒/多目标优化和论文图规范。
2. 13 份 Guide 的主题完整，但多份结尾仍写“后续可增加”；在对应脚本落地后，应把占位说明改为经验证的实际命令和失败处理。
3. 为 `contest_2026_X`、`rehearsal_2024_A` 等空项目增加 `INACTIVE`/占位说明，避免 Agent 把它们误认为可启动项目；不必删除目录。
4. 为比赛原始资料和官方文件记录 SHA-256、来源 URL/发布日期和校验日期，使 S0 与远程 Reviewer 能核对版本。
5. 明确绘图最终字体、尺寸、色彩和导出检查规则，但可在首轮 G4 前补充，不阻塞 S0。

## 开始往年题模拟前必须补齐的最小修改清单

按以下顺序完成即可，不需要重构现有角色和 Guide：

1. **锁定首轮项目**：明确 `ACTIVE_PROJECT = projects/rehearsal_2024_C`；初始化 `CURRENT.md` 为 S0。
2. **规范题目资料**：补 `problem/data/`、`problem/attachments/` 和 `problem/manifest.md`；登记并只读保护已验证可打开的题目与 4 个附件。
3. **补齐 Competition S0 材料**：放入 2024 年适用的官方规则、AI 规定、提交说明、论文模板，并添加只读索引。
4. **建立可恢复环境**：填写 `environment.yml` 与环境 README，实现 `verify_environment.py`，从新环境或当前环境执行一次通过的冒烟测试并保存结果。
5. **补最小项目脚手架**：填充 `templates/project_template/` 和 `create_project.py`；至少保证 Main Agent 强制路径、日志和六类实验目录可生成且不覆盖已有项目。
6. **打通 Git/Gate**：确定 XLSX 使用 LFS 还是外部受控存储，补 `.gitignore`/`.gitattributes`；创建首个 commit 和 remote，确认能够获得完整 SHA 并供 Reviewer 读取。
7. **补 Agent 入口**：根 `AGENTS.md` 路由至 Main Agent；添加 Main 启动 Prompt 与 Reviewer Gate Prompt；记录首轮 Skill 是否有硬依赖及其测试状态。
8. **完成一次 G0 干跑**：生成 `work/00_project_brief.md`、三份日志、`reviews/gate_0_submission.md`，运行环境检查并由 Reviewer 按固定 SHA 做一次静态审核。

只有第 1–8 项完成后，才建议把 Verdict 提升为 `READY WITH MINOR FIXES` 并进入 S1。Reference 扩充、最终绘图美化、复杂模型依赖和高级自动化都可以延后。

## 第一轮演练项目建议

推荐：`projects/rehearsal_2024_C/`（2024 年 C 题“数据驱动下磁性元件的磁芯损耗建模”）。

理由：

- 是当前唯一同时具备真实题目和附件的往年项目；
- 题目 DOCX 已只读打开并识别到 2024 年 C 题标题；
- 训练集和三个附件均为有效 XLSX：训练集含“材料1–材料4”，两个测试集各有“测试集”工作表，附件四含 3 个工作表；
- 当前环境已有 pandas、scikit-learn、matplotlib 和 openpyxl，修复环境清单后可快速建立数据审计与回归 Baseline；
- 现有 Reference 已覆盖缺失/异常/泄漏、线性回归、随机森林、梯度提升、评价指标与敏感性，和该题的首轮工作高度匹配。

不推荐 `rehearsal_2024_A` 或 `contest_2026_X` 作为本轮起点：两者目前只有空骨架，没有题目、数据或初始化状态。

## 审计结论

当前状态是“设计规范已成形，执行仓库尚未装配”。最有效的下一步不是扩充更多算法文档，而是完成 Competition、Environment、Template、Git/LFS 和 `rehearsal_2024_C` 的 S0 初始化。完成最小清单并通过一次 G0 干跑后，即可安全开始第一轮往年题模拟。
