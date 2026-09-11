# Gate 5 Review — 结果核验、冻结与交接

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_B`
- Gate: `G5`
- Stage: `S5 — 结果核验、冻结与交接`
- Review Round: `1`
- Reviewed Commit: `cb1e9276fc5054e7f912b00e54ab0b4292f3d464`
- S5 Implementation Commit: `474acb71dfc0bcaa27e6cca908c2243efa65660f`
- Pre-release Freeze Commit: `473a8ad8bf04cfa7d62511dadbe620f3a6ba8570`
- Prior G4 Review Commit: `70d6a1436192339c61c749188e104b15cf4bbbb7`
- Verdict: **PASS**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

# 1. Final Verdict

# **PASS — 同意进入 S6 / G6**

经对固定快照 `cb1e9276fc5054e7f912b00e54ab0b4292f3d464` 的独立 G5 审核，当前 S5 已达到“论文和绘图所使用的主要结果可信、可追溯、版本一致，且交接材料足以供后续成员安全使用”的门控要求。

正式授权：

```text
G5 = PASS
Current Stage may advance: S5 -> S6
Next Gate: G6
```

通过依据概括如下：

1. G4 批准的唯一模型栈、参数、输入版本、特征 schema、后处理、标签顺序、输出 schema 和证据身份已经写入完整 freeze manifest；
2. Q2 回退、Q3 晋级以及最终全量 residual-C3 配置均由 S5 独立代码从 selection traces 与 OOF 预测重新计算，而不是直接复制 S4 的结论；
3. Q3 的“嵌套选择管线 OOF 表现”和“最终全量部署配置”已经分配不同 Evidence ID，避免把 `S=0.550330` 错写成固定 residual-C3 的外层分数；
4. 官方测试正式推理只在 G4 PASS、freeze 完成和真实磁盘 ledger 显示零历史成功释放后执行；
5. ledger、release manifest、模型/输出哈希和 verified copies 对同一 release ID 保持一致，成功释放数为 1，第二次 release guard 会硬失败；
6. `results/verified/` 已建立结果登记表和 artifact manifest，官方测试预测被明确标记为无标签部署输出，不作为性能证据；
7. figure/writing handoff 已给出数据文件、Evidence ID、单位、可安全结论、禁止措辞和必须披露的限制；
8. 未发现未解决的 Critical 或 Major 问题。

本 PASS 表示可以进入论文技术一致性、图表制作和最终提交准备阶段；不表示可以重新训练模型、重新释放官方测试，或根据无标签预测外观返回 O2/O3/S4 调整方案。

---

# 2. Review Scope and Evidence Status

本轮按照 `.agents/roles/reviewer_agent.md` 与 `.agents/roles/main_agent.md` 的 G5 要求，重点核查：

```text
projects/rehearsal_2024_B/CURRENT.md
projects/rehearsal_2024_B/reviews/gate_5_submission.md
projects/rehearsal_2024_B/work/10_result_freeze.md
projects/rehearsal_2024_B/work/handoff/figure_handoff.md
projects/rehearsal_2024_B/work/handoff/writing_handoff.md
projects/rehearsal_2024_B/results/verified/result_registry.md
projects/rehearsal_2024_B/results/verified/
projects/rehearsal_2024_B/results/raw/final/test_release_ledger.json
projects/rehearsal_2024_B/results/raw/final/release/release_manifest.json
projects/rehearsal_2024_B/src/s5_validation.py
projects/rehearsal_2024_B/src/s5_release.py
projects/rehearsal_2024_B/configs/s5_output_schema.json
projects/rehearsal_2024_B/logs/experiments.md
projects/rehearsal_2024_B/logs/decisions.md
```

写回前已确认：

```text
main HEAD = cb1e9276fc5054e7f912b00e54ab0b4292f3d464
```

分支未发生漂移，被审核快照中不存在 `reviews/gate_5_review.md`。

证据状态：

- 文档、代码、JSON/JSONL、Git 提交谱系和文件间静态一致性：`VERIFIED_FROM_REPO`；
- S5 独立重算逻辑：已直接静态检查其实现，记为 `VERIFIED_FROM_REPO`；
- 本地运行事实、原始 17 个未入 Git 的 CSV 数值内容以及二进制 joblib 内部对象：由输入哈希、运行日志、release/ledger/validation manifests 和模型文件哈希共同支持，记为 `SUPPORTED_BY_REPO`；
- 本 Reviewer 未在网页环境重新运行 Conda、重新拟合模型或重新读取官方测试 CSV，不声称完成了独立本地执行。

---

# 3. Stage、Gate 与提交谱系

`CURRENT.md`、用户指定 Gate 和 `gate_5_submission.md` 均指向：

```text
Active Project: projects/rehearsal_2024_B
Current Stage: S5
Gate: G5
Requested transition: S5 -> S6
```

提交谱系为：

```text
70d6a143...  G4 PASS
    ↓
474acb71...  S5 freeze/release 实现
    ↓
473a8ad8...  pre-release verified freeze
    ↓
cb1e9276...  唯一 release、后验核验、交接与 G5 submission
```

从 implementation commit 到 pre-release freeze 只增加冻结证据；从 pre-release freeze 到本次审核提交只增加正式 release、ledger、verified copies、交接文档和阶段日志，没有看到 S5 release 源码、模型选择规则或冻结配置在官方测试释放后被修改。

---

# 4. Independent Result Reconstruction

## 4.1 独立性

`src/s5_validation.py` 没有导入 S3/S4 生产侧的 `evaluate_q2` 或 `evaluate_q3`。它自行实现：

- fixed-17 Macro-F1；
- nearest-rank ARE90；
- AP 到 system 的分组与求和；
- Q2 四配置词典序选择；
- Q3 八候选词典序选择；
- repeat-level promotion；
- 两级 bias guard；
- unified / AP-count 最终取舍。

因此，它不是简单读取 `promotion_decision.json` 后再次输出 PASS。

## 4.2 重算结果

机器结果中六项判断全部为真：

```text
q2_fallback_reconstructed = true
q2_full_configuration_is_C3 = true
q2_weighted_gain_below_threshold = true
q3_apcount_is_not_final = true
q3_full_configuration_is_residual_C3 = true
q3_unified_promotion_reconstructed = true
```

由逐行证据重新得到：

```text
Q2 weighted gain = 0.019001737503400118 < 0.02
Q2 final model = Q2-B1A

Q3 nested unified pipeline S = 0.5503296083233881
relative gain vs Q3-B1 = 31.6028%
Q3 final deployment configuration = Q3-physics_residual-C3
Q3 AP-count split = comparison only, not final
```

该结果与 G4 审核、S4 promotion decision、freeze manifest 和 result registry 一致。

---

# 5. Freeze Manifest Audit

Freeze manifest 状态为：

```text
status = FROZEN
selection_closed = true
test_data_used_for_selection = false
freeze SHA-256 =
A4AA45A0491C35C1D816164AADABB20998E9984D7521AFDE55D01A8B027E5E6D
```

sidecar 中记录的 SHA-256 与上述值一致。

冻结对象包括：

- Q1/Q2/Q3 模型 ID 与完整参数；
- Q1/Q3 后处理版本；
- 13 个训练输入的文件大小与 SHA-256；
- 4 个官方测试输入的文件大小、行数、角色与 SHA-256；
- S3/S4 特征 schema；
- Q2 固定 17 类顺序；
- split registry；
- S2/S4 配置；
- S5 输出 schema 和行序规则；
- release contract；
- 关键源文件 SHA-256；
- G4 review 身份和哈希；
- Q3 pipeline evidence 与 final configuration evidence 的身份边界。

冻结模型栈为：

```text
Q1: Q1-B1 Ridge(alpha=1, solver=lsqr), bounded v1
Q2: Q2-B1A LogisticRegression(C=1), no Q1
Q3: Q3-M1-HGB-UNIFIED
    final deployment config = physics-residual C3
    lr=0.05, max_iter=200, leaves=15,
    min_samples_leaf=20, l2=1,
    early_stopping=false, random_state=202409,
    no AP-count split
```

实际 HGB preprocessing 也已按代码忠实冻结为训练侧中位数插补、缺失指示、StandardScaler 和 protocol one-hot，没有继续沿用与代码不符的旧文字规格。

---

# 6. Q3 Evidence Identity Boundary

G4 要求在 S5 中关闭的最重要表达风险已经完成：

```text
E-Q3-PIPE-001
Q3_NESTED_SELECTION_PIPELINE_PERFORMANCE
```

表示：每个外层训练边界内部执行冻结候选选择规则后的 unified pipeline 外层 OOF 表现，`S=0.550330`。

```text
E-Q3-CONFIG-001
Q3_FINAL_FULL_DATA_CONFIGURATION
```

表示：汇总 45 条 primary inner records 后，为最终全量部署选择 `Q3-physics_residual-C3`。

这两个 Evidence ID 在 freeze manifest、verified metrics、result registry 和 writing handoff 中均被明确区分。

因此，S6 可以写：

> 嵌套选择的统一 HGB 管线将 primary S 降至 0.5503；按全部训练侧内层证据冻结后，最终全量配置为 physics-residual C3。

不得写：

> 固定 residual-C3 本身的外层交叉验证 S 为 0.5503。

也不得把全部 31.60% 提升只归因于 residualization。

---

# 7. Exactly-once Official-Test Release Audit

## 7.1 Guard implementation

release guard 从实际磁盘状态读取：

- freeze manifest 和 sidecar；
- G4 review；
- 冻结源文件；
- release ledger；
- release directory 是否冲突；
- 四个官方测试文件身份；
- feedback targets。

它不再只信任调用者手填的 `prior_release_count=0`。

若检测到：

```text
successful release > 0
RUNNING attempt > 0
release directory already exists
freeze mismatch
G4 review mismatch
official input identity mismatch
feedback target nonempty
```

则在正式数值解析前拒绝执行。

## 7.2 Ledger and release consistency

ledger 记录：

```text
schema = s5_exactly_once_ledger_v1
successful_release_count = 1
attempt count = 1
attempt status = SUCCEEDED
release ID = S5-A4AA45A0491C-20260911T110151+0800
```

release manifest 记录：

```text
execution head = 473a8ad8bf04cfa7d62511dadbe620f3a6ba8570
freeze hash = A4AA45A0...
model fits = 4
training CSV numeric reads = 13
official-test CSV numeric reads = 4
warnings = 0
feedback targets = []
test predictions used for model feedback = false
```

ledger 与 release manifest 对四个官方输入哈希、三个模型文件哈希、四个预测文件哈希和 release manifest 哈希保持一致。

第二次 `--preflight-only` 会由于已有成功释放而抛出：

```text
ContractBoundaryError:
a successful official-test release already exists
```

因此当前 exactly-once 成功释放门禁达到 G4 规定的最低充分要求。

---

# 8. Official Output Verification

正式输出数量为：

```text
Q1 AP predictions: 185
Q2 AP predictions: 151
Q3 AP predictions: 185
Q3 system predictions: 75
```

后验验证检查了：

- 每类文件行数、字段顺序和行序；
- Q1 键唯一、raw 有限、bounded 位于 `[0,test_dur]`；
- Q2 键唯一、标签属于固定 17 类、概率顺序固定、概率有限非负且和为 1；
- Q3 AP 键唯一、raw 有限、bounded 非负；
- Q3 system 数量为 75；
- 每个 system prediction 等于对应 bounded AP predictions 的严格和；
- raw release 与 verified copies 的 SHA-256 一致。

四个输出的每行均标记：

```text
scope = OFFICIAL_TEST_UNLABELED
```

且 result registry、writing handoff、figure handoff 均禁止把这些输出表述为官方测试精度证据。

---

# 9. Verified Registry and Handoffs

## 9.1 Result registry

`result_registry.md` 已为论文核心结论登记 Evidence ID、Claim、Source File、核验命令、Verified 状态和限制说明。核心条目包括：

```text
E-Q1-001
E-Q2-001
E-Q3-PIPE-001
E-Q3-CONFIG-001
E-Q3-UNC-001
E-Q3-LOSO-001
E-Q3-TRADE-001
E-FREEZE-001
E-RELEASE-001
E-RELEASE-SUM-001
```

没有看到把无标签 official prediction 注册为性能指标的情况。

## 9.2 Writing handoff

写作交接已明确：

- 三问统一技术主线；
- 每问最终模型和输入边界；
- 核心指标的精确定义；
- 可写入摘要的数字与 Evidence ID；
- Q3 pipeline/configuration 身份边界；
- Q2 长尾失败、Q3 最差 source、Bootstrap 范围、A03 和 AP-count 取舍等必须披露项；
- 禁止因果化、普遍鲁棒化和官方测试准确率表述。

## 9.3 Figure handoff

绘图交接已为建议图给出：

- 图的目的；
- Evidence ID；
- verified 数据文件；
- 横纵轴与单位；
- 推荐标题；
- 误差条/区间说明；
- 禁止误导的裁轴和措辞。

尚未在 S5 生成正式图不构成阻断，因为 G5 要求的是可执行交接，不是提前完成 S6 图表；且 handoff 已明确只有迁入 verified 的数据才能作图。

---

# 10. Issue Classification

```text
Critical: 0
Major:    0
Minor:    3
Advisory: 2
```

## Minor-01 — release 时刻对全部冻结输入的机器绑定仍可加强

**Priority: P2 — G6 前补强，不得重新执行官方测试推理**

Freeze manifest 已包含 13 个训练文件、配置、split、schema 和 Q1 OOF 证据的身份；提交谱系也未显示这些 tracked 文件在 freeze 后改变。

但静态代码显示，正式 `release_guard()` 在 release 时直接强校验的主要是：

- freeze 本身；
- G4 review；
- `source_files`；
- ledger/release directory；
- 四个 official test 文件。

随后 `read_training()` 会检查严格身份、1,250 行与 482 组，但没有在该 release 入口再次逐文件比较 freeze 中 13 个训练 SHA；底层通用 guard 也主要检查 phase、文件名和必需字段，而不重新打开全部冻结 artifact 做 hash binding。

没有证据表明训练数据实际发生过变化：freeze 与 release 只相隔约一分钟，Git 提交链也保持一致。因此这属于证据加固项，不是当前结果错误证据。

S6/G6 前建议新增一个**不读取官方测试 CSV、不重新推理**的 `post_release_binding_attestation.json`，至少核查当前快照中的：

```text
13 training file hashes == freeze manifest
S2/S4/output-schema hashes == freeze manifest
split/schema/Q1-OOF hashes == freeze/prior manifests
release model/output hashes == ledger/release manifest
release execution head is descendant of frozen source commit
```

该补强不得通过第二次正式 release 完成。

## Minor-02 — release 输出与冻结语义的后验断言仍可更完整

**Priority: P2 — G6 前补强**

当前验证已经覆盖结构、概率闭合、物理边界和 AP→system 求和，但还可以在不重新读取官方输入的情况下，对已经提交的 JSONL/joblib 增加：

- 所有行的 `release_id` 与 ledger 唯一成功 ID 一致；
- Q1/Q2/Q3 `model_id`、Q3 `configuration_id`、feature bundle hash 与 freeze 一致；
- Q2 `predicted_joint_label` 等于概率 argmax，`predict_nss/predict_mcs` 与标签拆分一致；
- Q1 与 Q3 对相同 row key 的 `q1_seq_time_bounded` 完全一致；
- system `component_row_keys` 与其 AP 组件集合完全一致；
- joblib 外层 metadata 中的模型 ID、label order、configuration ID、eta 与 freeze/release manifest 一致。

现有生成代码直接写入这些字段，抽样静态检查也未发现不一致，因此该项不阻断 G5。

## Minor-03 — registry/handoff 文档尚未进入最终机器 manifest

**Priority: P2 — G6 最终交付 manifest 中关闭**

`artifact_manifest.json` 已锁定所有主要机器结果，但有意不包含：

```text
result_registry.md
figure_handoff.md
writing_handoff.md
```

这些文件本身目前内容清楚且与 verified 数字一致。不过进入终稿后，为防止 Evidence ID、图表说明和论文数字在 S6 中静默漂移，建议由 G6 final-delivery manifest 记录：

- result registry SHA；
- figure/writing handoff SHA；
- 最终图表数据快照 SHA；
- 论文源文件和最终 PDF SHA。

同时将文档中短写的 pre-release commit `473a8ad` 统一为完整 SHA：

```text
473a8ad8bf04cfa7d62511dadbe620f3a6ba8570
```

---

# 11. Advisory

## Advisory-01 — 数据来源 provenance 仍只能证明“与本地 S0 manifest 一致”

仓库已如实披露没有官方压缩包 URL 和 archive-level SHA。S6 不得写成“已核对官方原始压缩包”；只能写明 17 个本地文件从 S0 到 S5 的逐文件 identity 一致。

## Advisory-02 — exactly-once ledger 未设计并发文件锁

当前单进程演练流程中，`RUNNING` 状态、release directory 冲突和成功计数已能 fail closed。若未来多人/多进程可能同时启动 release，应再增加 OS 文件锁或原子 lock file。该项不属于当前单人演练 Gate 要求。

---

# 12. G5 Checklist

| G5 验收项 | Reviewer 结论 |
|---|---|
| 主要结果逐项核验 | PASS |
| 独立重算模型选择和 promotion | PASS |
| `results/verified/` 与 raw 区分 | PASS |
| 核心数字可追溯 | PASS |
| 最终模型、参数和代码身份明确 | PASS |
| 训练输入与 schema 已冻结 | PASS |
| Q3 pipeline/config Evidence 分离 | PASS |
| 官方测试只成功释放一次 | PASS |
| release/ledger/output 哈希一致 | PASS |
| 无标签预测未冒充性能证据 | PASS |
| result registry 完整 | PASS |
| figure handoff 无需猜测 | PASS |
| writing handoff 无需编造结论 | PASS |
| 复现/后验核验命令明确 | PASS |
| 可以停止模型修改 | **YES** |

---

# 13. S6 Authorization and Hard Boundaries

Reviewer 授权进入 S6，完成论文、图表、技术一致性和最终提交准备，但必须遵守：

1. **不得再次运行官方测试 release 或模型推理。**
2. 可从已冻结的 `official_*.jsonl` 做确定性的格式转换、合并和填表；这类操作必须保存映射脚本和输入/输出哈希，不能重新读取 official CSV 来改变预测。
3. 论文和图表只能使用 `results/verified/` 与 registry 中 `Verified=YES` 的 Evidence ID。
4. 不得改变模型、参数、标签顺序、特征 schema、postprocess、Q3 system-sum 规则或 Evidence identity。
5. 任一模型/数据/指标修改都会使相应 Evidence ID 失效，并需要回到适当 Gate 重新审核。
6. Q2 必须保留长尾与 source-blind 局限；不得用总体 accuracy 掩盖 fixed-17 Macro-F1。
7. Q3 必须区分 nested pipeline performance 与 residual-C3 deployment configuration。
8. Q3 不得声称所有 source 一致鲁棒；必须披露最差 held-out source `S=2.159764`。
9. Bootstrap 只能表述为 OOF group-resampling uncertainty，不能扩大为全流程重训练置信区间。
10. official test 预测无标签，不得写 accuracy、误差或相对获奖论文的性能结论。

G6 应重点核查：

```text
题目要求
= 数学定义
= 最终实现
= verified 数字
= 图表
= 论文措辞
= 最终提交文件
```

并检查匿名、页数、格式、引用、AI 使用记录以及最终输出表与冻结 JSONL 的逐键映射。

---

# 14. Reviewer Conclusion

```text
Verdict: PASS
G5: PASS
S5 -> S6: AUTHORIZED
Next Gate: G6
```

当前项目已经具备进入论文工程阶段的可信证据底座。后续工作的重点应从性能扩张切换为：

- Evidence ID 驱动的图表和写作；
- 结果与公式的技术一致性；
- 官方输出格式的确定性转换；
- 限制条件的诚实披露；
- 最终提交合规性。

本审核只新增 `reviews/gate_5_review.md`，不得由 Reviewer 修改 `CURRENT.md`、模型、配置、结果、图表或论文正文。
