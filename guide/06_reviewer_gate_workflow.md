# 审核 Agent 门控流程

审核 Agent 的完整约束见：

```text
.agents/roles/reviewer_agent.md
```

## 审核输入

每次审核必须明确：

```text
Repository:
Branch:
Active Project:
Gate:
Reviewed Commit SHA:
Review Round:
```

## 审核流程

```text
主 Agent 完成阶段
→ 固定 commit 并 push
→ 审核期间冻结分支
→ ChatGPT Pro 按 SHA 读取仓库
→ 输出 PASS / REVISE / BLOCK
→ 只新增 reviews/ 中的审核文件
```

## 判定含义

- `PASS`：允许进入下一阶段。
- `REVISE`：路线可保留，但必须先修复 Major 问题。
- `BLOCK`：存在根本问题，必须回退重做。

## 写回路径

```text
projects/<project_name>/reviews/gate_<N>_review.md
```

复审不得覆盖历史文件：

```text
gate_<N>_review_r2.md
gate_<N>_review_r3.md
```

## 注意事项

- 不按变化中的 branch HEAD 审核。
- 不让 Reviewer 修改模型、代码、结果或论文。
- Reviewer 无法实际运行代码时，必须说明静态审核限制。
- 审核结论应给出 Required Fixes 和 Acceptance Criteria。

> 后续可补充 GitHub 网页端标准调用 Prompt。
