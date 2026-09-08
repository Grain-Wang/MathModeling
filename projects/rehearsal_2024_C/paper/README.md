# Paper Workspace

## Current status

- Stage: `S6 — 论文技术一致性与提交准备`
- G5: `PASS`
- Current manuscript: [`technical_draft.md`](technical_draft.md)
- Submission readiness: `NOT YET`；该 Markdown 是技术底稿，不是官方模板成稿。

## Source boundary

论文数字只能来自 `../results/verified/`，并通过 `../results/verified/result_registry.md` 的 E001–E015 追溯。不得从 `results/raw/` 选择数字，不得改写冻结模型或附件二、三的正式预测。

## Remaining conversion chain

```text
technical_draft.md
→ 补齐正式图表和参考文献
→ 迁入 competition/2024 官方 Word 模板副本
→ 匿名与格式检查
→ 导出并人工打开最终 PDF
→ 计算 MD5、按队伍编号命名
→ G6 审核
```

正式模板原件位于 `competition/2024/official_templates/2024_paper_template.doc`，只读；使用时必须复制到本目录，不能覆盖官方原件。

## Automated check

从仓库根目录运行：

```powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_C/src/check_s6_consistency.py
```

该检查只覆盖技术底稿与冻结证据的一致性，不覆盖插图、Word 排版、PDF 渲染、文件命名或平台上传。
