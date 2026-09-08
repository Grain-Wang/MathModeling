# Gate 0 Review — 项目初始化与约束确认

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_B`
- Gate: `G0`
- Stage: `S0 — 项目初始化与约束确认`
- Review Round: `1`
- Reviewed Commit: `2afba29b3cae4d6e500e0b4faa25aa3130953672`
- Verdict: **PASS**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

## 1. Final Verdict

# **PASS — 同意进入 S1 / G1**

经对固定快照 `2afba29b3cae4d6e500e0b4faa25aa3130953672` 的独立静态审核，当前 S0 已达到 `.agents/roles/main_agent.md` 与 `.agents/roles/reviewer_agent.md` 对 G0 的核心要求：

1. 唯一活动项目已经切换并明确为 `projects/rehearsal_2024_B`；
2. 选中赛题确认为 2024 年 B 题《WLAN组网中网络吞吐量建模》；
3. 本地题目正文、13 个训练 CSV 和题目点名的 4 个测试 CSV 已完成只读清点、结构检查与逐文件 SHA-256 登记；
4. 2024 年官方邀请函、格式规范、提交手册和论文模板已归档并把关键约束迁入项目；
5. `math_modeling` 环境已有实际导入冒烟测试证据，并按当前 CPU/RAM/无已验证 GPU 的资源边界规划；
6. 已知输入异常、数据泄漏风险、测试集隔离规则和远程数据不可见限制均已显式记录，没有在 S0 静默修复或掩盖；
7. 六项 S0 强制交付物全部存在，`CURRENT.md` 保持 `PENDING REVIEW`，没有提前进入 S1 或启动正式建模。

当前没有未解决的 Critical 或 Major 问题。因此正式授权：

```text
G0 = PASS
Current Stage may advance: S0 -> S1
Next Gate: G1
```

本 PASS 只表示项目已经具备正确、可控的开题起点，不表示 17 个 CSV 已完成逐字段质量审计，也不表示已知错位、全空列、`nss=0` 或 schema 差异已经得到处理。

---

## 2. Review Scope and Limitation

本轮重点读取并核对：

```text
.agents/roles/reviewer_agent.md
.agents/roles/main_agent.md
projects/rehearsal_2024_B/CURRENT.md
projects/rehearsal_2024_B/problem/manifest.md
projects/rehearsal_2024_B/work/00_project_brief.md
projects/rehearsal_2024_B/logs/decisions.md
projects/rehearsal_2024_B/logs/experiments.md
projects/rehearsal_2024_B/logs/ai_usage.md
projects/rehearsal_2024_B/reviews/gate_0_submission.md
projects/rehearsal_2024_C/CURRENT.md
competition/2024/README.md
environment/README.md
```

写回本审核前已确认：

```text
main HEAD = 2afba29b3cae4d6e500e0b4faa25aa3130953672
```

没有发生分支漂移。

17 个 CSV 按用户要求被 Git 忽略，因此网页端 Reviewer 无法从远程快照重新打开其原始内容。本轮对数据完整性与异常记录的判断依据是仓库内的 manifest、实验日志、验证命令、逐文件大小和 SHA-256，证据状态为 `SUPPORTED_BY_REPO`，不是 Reviewer 独立重跑。该限制已被提交方主动披露，并为 S1 重新校验设置了明确边界，因此不构成 G0 阻断。

---

## 3. G0 Checklist

| G0 验收项 | 结果 | Reviewer 判断 |
|---|---|---|
| 活跃项目唯一明确 | PASS | B 项目标记 ACTIVE；C 项目标记 INACTIVE / PAUSED；模板项目无活动声明 |
| 赛题选择正确 | PASS | 项目、manifest、brief 和 submission 均指向 2024 B 题《WLAN组网中网络吞吐量建模》 |
| 题目正文存在并可检查 | PASS | DOCX 已纳入 Git，大小、SHA-256、标题、三问和附录读取结果均有记录 |
| 数据和附件完整 | PASS WITH VISIBILITY LIMIT | 本地 13 个训练 CSV、4 个测试 CSV 均登记为可读；远程不含 CSV，须在 S1 本机复核 |
| 官方规则已读取并记录 | PASS | 2024 邀请函、格式规范、提交手册和模板均有本地原件、大小和哈希；关键匿名、格式和提交规则已迁入 brief |
| 选题优势与风险已迁入 | PASS | 题目适配机理特征+数据驱动路线；异常、schema、泄漏、外推和资源风险均有编号 |
| 开发环境可用 | PASS | `math_modeling` / Python 3.11.11 及核心包导入 smoke=PASS；CPU-first 路线现实 |
| `CURRENT.md` 初始化 | PASS | 项目、题号、阶段、Gate、禁止事项和下一步均明确，未提前宣称通过 |
| 未确认推断是否被冒充事实 | PASS | 对数据真实性、异常含义和后续处理均保留限制，没有把 S0 基础清点写成完整数据审计 |
| 阶段提交范围 | PASS | 本提交只增加 B 项目 S0 产物，并将原 C 项目标为暂停，没有生成正式模型或结果 |

---

## 4. Positive Findings

### 4.1 输入清单具有较强可追溯性

**Status: SUPPORTED_BY_REPO**

`problem/manifest.md` 对 1 个题目 DOCX 和 17 个 CSV 逐项记录：

- 文件名与用途；
- 文件大小；
- SHA-256；
- 打开状态；
- 行列规模；
- `test_id` 数量；
- 已知异常；
- 原始数据只读与迁移说明。

同时明确只能够声明“本地清单完整且可读”，不能在缺少官方压缩包总哈希时宣称与官方发布包逐字节一致。这一表述边界正确。

### 4.2 已知异常没有在 S0 被静默处理

**Status: VERIFIED_FROM_REPO**

当前已经定位并登记：

- `training_set_2ap_loc2_nav82.csv` 末两行字段错位；
- `training_set_3ap_loc30_nav86.csv` 三个 AP0 RSSI 列全空；
- 三条 `nss=0`；
- `num_ppdu` / `num_ampdu`、重复 `error%` 和额外空预测列等 schema 差异。

项目没有在原始数据中删行、填补或改写，而是把处理决策推迟到 S1 并要求保留原始行号、理由和处理前后数量。这是正确的阶段边界。

### 4.3 数据泄漏和测试集使用边界提前识别

**Status: VERIFIED_FROM_REPO**

项目已识别同一 `test_id` 下多 AP 行共享场景信息，普通按行随机切分会造成泄漏；同时规定四个测试集不能用于特征选择、调参、模型选择或内部泛化指标。该风险已在正式建模之前迁入 brief、CURRENT 和 submission。

### 4.4 官方规则与项目状态一致

**Status: VERIFIED_FROM_REPO**

`competition/2024/` 已归档邀请函、格式规范、提交手册和论文模板，并记录原件大小和 SHA-256。项目简报已经迁入匿名、摘要、文件命名、附件、引用及原件不可覆写等关键约束。

### 4.5 环境证据足以支持进入 S1

**Status: SUPPORTED_BY_REPO**

日志记录 `math_modeling` 环境的核心依赖导入测试为 PASS，并明确当前机器为 8 核 / 16 线程 CPU、13.8 GiB RAM、无已验证 GPU。S1 主要任务是题意拆解和数据审计，不要求完成全新环境 clean rebuild，因此当前证据足够。

---

## 5. Issue Classification

### Critical

**None.**

未发现错误赛题、决定性附件缺失、项目对应错误比赛、明确违反官方规则或环境完全不可用等 G0 Critical。

### Major

**None.**

当前远程不包含 CSV 是用户明确的数据管理策略，而不是提交方遗漏；manifest、日志、哈希和本地复核命令已提供可接受的替代证据。该限制必须在 S1 持续受控，但不需要因此阻止开题。

### Minor / P2 — S1 早期修复

1. **远程数据恢复说明应单独固化。** 建议在 S1 初期增加一个被 Git 跟踪的 `problem/data/README.md` 或等价文档，记录授权获取方式、离线备份责任、17 个期望文件名和“开始审计前必须全量重新校验 manifest SHA”的步骤。不得提交受限制的 CSV 本体。
2. **`CURRENT.md` 的标题用词可更准确。** 当前 `Known Blockers` 先写 `None`，随后列出多项限制和风险。建议改为“当前流程阻断：None；Known Limitations / Risks：……”以避免本地 Agent 将风险误读为不存在。
3. **时间戳与机器时钟应在 S1 统一检查。** 后续运行清单需要固定时区并记录 ISO 8601 时间；若不同机器协作，应避免本地时钟偏差影响证据顺序。
4. **团队责任人尚未落名。** 当前功能角色足以通过 G0，但建议在 G1 前至少明确数据审计、代码、建模和最终提交的责任人。

### Advisory / P3

1. 在比赛前完成一次 `environment.yml` 的全新环境重建测试；
2. 实现仓库级 `scripts/verify_environment.py`；
3. 为原始数据准备不进入 Git 的离线只读备份和恢复演练。

这些事项不是 G0 或 G1 的前置阻断。

---

## 6. Authorization and S1 Boundaries

Reviewer 正式授权：

```text
G0 = PASS
S0 -> S1 = AUTHORIZED
Next Gate = G1
```

进入 S1 后应优先完成：

1. 逐问拆解 Q1–Q3 的输入、输出、未知量、约束、评价方式和依赖关系；
2. 在读取数据前全量复核 17 个 CSV 的文件名、大小与 SHA-256，审计结束后再次复核原件未变；
3. 建立逐字段 schema、单位、列表型 RSSI 解析规则和规范字段映射；
4. 对两行错位、三个全空 RSSI 列和三条 `nss=0` 分别冻结可复现的保留、隔离或缺失处理规则；
5. 明确 `test_id`、loc、nav、AP 数量及文件场景之间的层级，建立泄漏分析；
6. 在调参前设计按 `test_id` / 场景分组的验证候选，并评估留一 loc/nav 场景压力测试；
7. 明确 Q3 使用实测 MCS/NSS 的题面许可不能倒灌为 Q1/Q2 的标签泄漏；
8. 继续封存四个测试集，不用其输入分布反向调整特征、规则或模型。

G1 至少应提交：

```text
work/01_problem_analysis.md
work/02_data_audit.md
work/03_requirement_matrix.md
必要的数据审计脚本及 results/raw/s1/ 证据
reviews/gate_1_submission.md
```

---

## 7. Final Gate Record

```text
Verdict: PASS
Reviewed Commit: 2afba29b3cae4d6e500e0b4faa25aa3130953672
Authorized Transition: S0 -> S1
Next Gate: G1
Critical: 0
Major: 0
Minor: 4
Advisory: 3
```

本审核只新增 `reviews/gate_0_review.md`。Reviewer 未修改 `CURRENT.md`、原始题目、数据、日志、模型、代码或结果；阶段状态应由 Main Agent 拉取本审核后自行更新。