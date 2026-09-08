# Final Fix Log

> S6 只允许修复论文、图表、技术一致性与提交合规问题；不得改动冻结模型、采用阈值、正式预测或 verified 证据。

| ID | Time | Status | Issue | Resolution / required action | Verification |
|---|---|---|---|---|---|
| FX-S6-001 | 2026-09-08 | CLOSED | 首次一致性检查把模型 SHA-256 中的 `E384`、`E970` 误识别为 Evidence ID | Evidence ID 正则加入字母数字边界；保留首次失败报告；未修改任何 scientific artifact | 修正后 `9/9 PASS` |
| FX-S6-002 | 2026-09-08 | OPEN | 正式图表尚未生成 | 等待用户确认 Scientific Illustrator、数值绘图 Skill 和配色方案，再按 handoff 生成 | 图源、PDF/SVG/PNG、脚本和 Evidence ID 齐全后关闭 |
| FX-S6-003 | 2026-09-08 | OPEN | 参考文献尚未核验 | 按正文实际用到的 Steinmetz、梯度提升、分组验证和 Pareto 方法查证原始/权威来源 | 文内引用与参考文献逐项对应后关闭 |
| FX-S6-004 | 2026-09-08 | OPEN | 技术底稿尚未迁入 2024 官方模板 | 复制官方模板到 `paper/` 后排版；不得覆盖 `competition/2024/` 原件 | 封面、摘要页、正文、匿名、页码和字体检查后关闭 |
| FX-S6-005 | 2026-09-08 | OPEN | 最终 PDF 和附件包未冻结 | 完成 PDF 导出、人工打开检查、文件名、MD5、附件匿名与大小检查 | 生成提交清单和哈希后关闭 |

## Immutable Boundary

S6 开始时冻结边界仍为 `S5-FREEZE-2024C-V1`。若任何修复意外要求改变模型、数据切分、预测值、E001–E015 或 `results/verified/`，必须停止并重新申请 Gate 授权，不能把它记录成普通排版修复。
