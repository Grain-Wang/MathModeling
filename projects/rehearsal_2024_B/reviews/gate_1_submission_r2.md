# Gate 1 Submission — Review Round 2

## Submission Metadata

- Project：rehearsal_2024_B
- Gate：G1
- Stage：S1 — 题意拆解与数据审计
- Review Round：2
- Prior Verdict：REVISE
- Prior Review Commit：e9253ce15a7b296298cf68c61b65357b55f1a1ed
- Formal Audit Implementation Commit：03ac99d91004fca2123011a3db29043d5612568c
- Response：[work/revisions/gate_1_response.md](../work/revisions/gate_1_response.md)
- Expected Review：reviews/gate_1_review_r2.md
- Review Target：推送完成后的 origin/main 完整 SHA，由交接消息提供

## Requested Review Scope

1. M1-01：Q3 是否已完整覆盖 185 个 AP 吞吐量、75 个严格组系统吞吐量，以及 AP/系统两级 signed CDF、ERROR_90 和 accuracy_90。
2. M1-02：身份审计是否证明 eligible 482/482、测试 136/136 组通过行数、精确 AP 集合/次数、复合键唯一三重检查。
3. 重复审计是否清楚区分文件内全列完全重复和跨文件规范化 SHA-256 行/组指纹，并提供可执行的未来同簇同折策略。
4. 正式审计是否来自干净 03ac99d 提交，17/17 输入哈希是否前后通过且不变。
5. 是否可授权 S1 → S2。

## Key Assertions

- Formal audit：PASS_WITH_WARNINGS，Critical=0。
- Raw training：1,252 行、484 组，其中 A01 两组无效。
- Eligible training：1,250 行、482/482 严格有效组。
- Official tests：336 行、136/136 严格有效组。
- Q3 tests：185 AP 行、75/75 严格系统组。
- 复合身份字段空/非法数 0，重复复合键 0。
- 文件内完全重复训练行 0；跨文件规范化重复行指纹簇 0、组指纹簇 0。
- AP throughput 训练目标 1,250 个，其中零值 5 个；系统目标 482 个，零值 0。
- 官方测试集保持分布封存；没有拟合模型、调参或测试预测。
- 原始 CSV 未进入 Git，且仍命中忽略规则。

## Evidence

- [Round 2 response](../work/revisions/gate_1_response.md)
- [Problem analysis](../work/01_problem_analysis.md)
- [Data audit](../work/02_data_audit.md)
- [Requirement matrix](../work/03_requirement_matrix.md)
- [Audit summary](../results/raw/s1/audit_summary.md)
- [Identity evidence](../results/raw/s1/identity_checks.json)
- [Q3 target and metric evidence](../results/raw/s1/q3_target_contract.json)
- [Complete quality evidence](../results/raw/s1/quality_checks.json)
- [Audit script](../src/s1_data_audit.py)

## Boundary

G1 Round 2 审核结果出来前：

- Current Stage 仍为 S1；
- S1 → S2 为 NOT AUTHORIZED；
- 不拟合正式模型、不调参、不生成官方测试预测；
- Main Agent 不创建或修改 reviews/gate_1_review_r2.md。
