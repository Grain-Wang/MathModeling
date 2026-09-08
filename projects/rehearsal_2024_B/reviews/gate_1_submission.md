# Gate 1 Submission

## Stage

S1 — 题意拆解与数据审计

## Review Snapshot

- Repository: Grain-Wang/MathModeling
- Branch: main
- Active Project: projects/rehearsal_2024_B
- G0 review commit: 0fac4e099cffdafab32af0aa9af9f8969f087dbe
- Clean implementation commit used by the formal audit: f4b8b9f70e049d497edf56a3bdac43669da932a6
- Review commit: 由调用 Reviewer 时传入包含本文件、S1 文档、脚本、日志和结果证据且已推送至 origin 的 git rev-parse HEAD 完整 SHA
- Review round: 1
- Prepared at: 2026-09-08T23:12:47+08:00
- Freeze rule: Reviewer 必须审核调用时提供的固定完整 SHA，不得改用变化中的分支 HEAD。
- Data visibility: 17 个原始 CSV 按用户要求被 Git 忽略；Reviewer 可审核固定哈希、审计代码与非 CSV 结果，取得授权同哈希数据后可重跑。

## Required deliverables

- [work/01_problem_analysis.md](../work/01_problem_analysis.md)
- [work/02_data_audit.md](../work/02_data_audit.md)
- [work/03_requirement_matrix.md](../work/03_requirement_matrix.md)
- [src/s1_data_audit.py](../src/s1_data_audit.py)
- [results/raw/s1/data_profile.json](../results/raw/s1/data_profile.json)
- [results/raw/s1/quality_checks.json](../results/raw/s1/quality_checks.json)
- [results/raw/s1/audit_summary.md](../results/raw/s1/audit_summary.md)
- [problem/data/README.md](../problem/data/README.md)
- [logs/decisions.md](../logs/decisions.md)
- [logs/experiments.md](../logs/experiments.md)
- [logs/ai_usage.md](../logs/ai_usage.md)
- [CURRENT.md](../CURRENT.md)

## Reproduction and verification

~~~powershell
conda run --no-capture-output -n math_modeling python -m py_compile projects/rehearsal_2024_B/src/s1_data_audit.py
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s1_data_audit.py --verify-only
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s1_data_audit.py
git diff --check
git ls-files "projects/rehearsal_2024_B/**/*.csv"
git status --short
git rev-parse HEAD
~~~

正式审计已经实际执行，关键断言为：

~~~text
audit implementation HEAD = f4b8b9f70e049d497edf56a3bdac43669da932a6
git status before outputs = clean
input verification before = PASS
input verification after = PASS
input hashes unchanged = true
expected CSV = 17
actual CSV = 17
raw training rows = 1252
eligible training rows = 1250
eligible incomplete AP groups = 0
test rows structurally audited = 336
test numeric summaries emitted = false
anomalies registered = A01, A02, A03, A04, A05, A06
audit status = PASS_WITH_WARNINGS
~~~

## Main claims for review

1. Q1–Q3 的目标、逐 AP 输出数量、输入时点、依赖关系、物理边界、评价候选和未知项已经逐问拆解。
2. Q1 禁止全部事后字段；Q2 只可使用 Q1 折外预测；Q3 只将题面明确许可扩展到真实 MCS/NSS，不使用 PER 或真实 seq_time。
3. 训练/验证的原子组固定为 source_file + test_id；同一次测试的 2/3 个 AP 行不跨折。
4. 17 个本地 CSV 的文件名、大小和 SHA-256 在审计前后完全一致；原始文件未改写。
5. RSSI 的列表/标量解析、单位、字段族、结构缺失、整列缺失、schema alias 与输出占位列已形成机器可读合同。
6. A01 隔离两个本来就不完整的单行组，共 2 行；1,252 行变为 1,250 行，剩余 482 组均完整。
7. A02–A06 分别冻结缺失、哨兵风险、schema、超时长字段和文件名/loc_id 不一致的处理与后续敏感性要求。
8. 官方测试集只保留结构、dtype、缺失/非空和组大小证据，没有输出其数值或 RSSI 分布。
9. 当前未使用外部数据；若后续使用，必须记录来源、许可、版本/哈希、日期并提供无外部数据消融。
10. S1 没有拟合模型、调参、生成正式测试预测或自行宣布 G1 通过。

## G0 Minor closure

| G0 Minor | Closure |
|---|---|
| 跟踪数据恢复说明 | 已新增 problem/data/README.md；.gitignore 只放行该 README，CSV 继续忽略 |
| CURRENT 区分阻断与风险 | 已拆为 Current Process Blockers 和 Known Limitations / Risks |
| ISO 8601 时区时间 | S1 新记录和机器证据统一使用 +08:00 ISO 8601 |
| 团队责任人实名 | 尚未由用户提供；已明确当前功能角色与最终提交必须由人类队员负责，保留为非阻断 Minor |

## Known limitations and unresolved risks

1. Reviewer 若只有远程仓库而无授权 CSV，只能验证代码、hash manifest 与结果证据，不能独立重跑原始行审计。
2. 缺少官方数据压缩包稳定 URL、总哈希和发布方逐文件校验，不能声称本地文件与官方包逐字节一致。
3. 官方评分函数、最终预测数值格式和 (NSS,MCS)=(0,0) 的业务语义未给出，均保持 UNKNOWN。
4. training_set_3ap_loc33_nav88.csv 的文件名 token loc33 与内容 loc4 不一致，官方意图未知；原件未修改。
5. 训练中 test_dur、pkt_len、pd、ed 恒定，不能从本样本估计这些因素的经验影响。
6. 团队成员实名和离线备份责任人仍待用户补充；environment.yml clean rebuild 仍为 advisory。
7. 正式模型、验证切分清单、随机种子和基线实验必须等 G1 PASS 后在 S2 预注册，当前没有越过门禁。

## Requested verdict

PASS / REVISE / BLOCK。

Main Agent 请求 Reviewer 对调用时提供的固定远程完整 SHA 进行 G1 Round 1 独立审核。只有 G1 PASS 或用户明确书面批准后，项目才可由 S1 进入 S2；Reviewer 应新增 reviews/gate_1_review.md，不得修改 Main Agent 的交付物。
