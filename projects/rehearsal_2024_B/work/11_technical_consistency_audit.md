# S6 技术一致性审计

状态：**IN PROGRESS — evidence/software boundary PASS，paper/figures pending**

## 1. Entry authorization

G5 review commit `3862fee66a3c1ca362202b8d5d9e8b5d7eb2137b` 对
`cb1e9276fc5054e7f912b00e54ab0b4292f3d464` 给出 PASS，明确授权 S5→S6，下一门禁为 G6。

## 2. Frozen technical chain

| Layer | Frozen identity | Audit status |
|---|---|---|
| Q1 | Q1-B1 Ridge；bounded v1 | PASS |
| Q2 | Q2-B1A LogisticRegression(C=1.0)；17 类固定顺序；不使用 Q1 | PASS |
| Q3 | Q3-M1-HGB-UNIFIED；physics-residual C3；system=sum(bounded AP) | PASS |
| Validation | grouped repeated outer CV + source-blind LOSO；Q3 `S=max(AP ARE90, system ARE90)` | PASS |
| Release | `S5-A4AA45A0491C-20260911T110151+0800`；exactly once | PASS |

完整 freeze SHA-256 为
`A4AA45A0491C35C1D816164AADABB20998E9984D7521AFDE55D01A8B027E5E6D`，pre-release commit 为
`473a8ad8bf04cfa7d62511dadbe620f3a6ba8570`。

## 3. G5 post-release hardening

`results/verified/post_release_binding_attestation.json` 已在不读取官方测试 CSV、
不运行推理的条件下通过 29/29 项：

- 13 个训练文件逐一与 freeze 的 bytes/SHA-256 一致，聚合哈希一致；
- S2/S4 配置、split registry、两个 feature schema、output schema 与 freeze/prior manifests 一致；
- Q1 OOF 与 G4 验证清单一致；
- release manifest、ledger、3 个 joblib 和 4 个 JSONL 的身份一致；
- release execution head 是 frozen source commit 的后代；
- 所有输出行的 release/model/config/feature bundle 身份一致；
- Q2 argmax、NSS/MCS 拆分，Q1→Q3 同行 bounded 值和 AP→system 组件集合一致；
- joblib 仅检查外层 metadata，未调用任何 pipeline 方法。

## 4. Evidence-to-figure handoff

`package_for_deliver/figure_handoff_2024_B/` 与对应 ZIP 已形成 verified-only 输入快照。
当前可交付 F1–F4 以及 F5 的 Q1 准确性部分。F5 特征重要性仍未迁入 verified，配图同学不得直接从 raw 取数。

禁止事项保持不变：官方测试预测无标签，不得作为性能证据；不得手抄数值；不得把 Q3 pipeline OOF 分数写成固定 C3 分数；不得声称所有 source 一致鲁棒；bootstrap 只能解释为 OOF group-resampling uncertainty。

## 5. Pending paper/figure audit

以下项目尚未发生，因此本审计不能标记 COMPLETE，也不能提交 G6：

- 正式作图前由用户确认具体 plotting skill；
- 生成可复现绘图脚本、最终图数据快照、SVG/PDF/PNG，并校验图中数值与 Evidence ID；
- 完成论文源文件，逐式核查题意、符号、单位、算法、实验、结果和局限；
- 执行模板、页数、匿名、文件命名、PDF 字体/可复制文本和最终提交清单检查；
- 在 final-delivery manifest 登记最终图数据、论文源文件和最终 PDF SHA-256。

## 6. Current conclusion

S6 的机器证据底座和配图输入交接已经就绪，适合移交给配图与论文队友并行工作；项目整体仍为 **G6 NOT READY**。
