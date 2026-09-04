# 主 Agent 工作流程

主 Agent 的完整约束见：

```text
.agents/roles/main_agent.md
```

## 启动步骤

1. 确认 `ACTIVE_PROJECT`。
2. 读取 `main_agent.md`。
3. 读取当前项目 `CURRENT.md`。
4. 读取最近一次 Gate 审核。
5. 读取当前阶段所需文件和 Guide。
6. 只处理当前阶段允许的任务。

## 阶段流程

```text
S0 项目初始化
S1 题意与数据审计
S2 总体方案与模型合同
S3 全题 Baseline
S4 主模型与证据
S5 结果冻结与交接
S6 论文一致性与提交
```

每阶段均执行：

```text
完成交付物
→ 创建 gate_<N>_submission.md
→ commit / push
→ 等待审核
→ PASS / REVISE / BLOCK
```

## 关键纪律

- 主 Agent 不能自行宣布 Gate 通过。
- 未通过当前 Gate，不进入下一阶段。
- 发现根本问题时先记录，再调整方案。
- 所有重要结论必须有文件和实验依据。
- 每次阶段变化后更新 `CURRENT.md`。

> 后续可增加常用启动 Prompt 和阶段命令。
