# 仓库总览

本仓库用于华为杯研究生数学建模的日常演练与正式比赛。

## 目录职责

```text
.agents/      Agent 的 Skill、角色说明和复用 Prompt
guide/        仓库操作规范
competition/  官方规则、题目模板和提交要求，默认只读
reference/    建模与数据处理速查资料，默认只读
templates/    新项目模板，默认只读
environment/  Conda 环境与依赖说明
scripts/      跨项目复用脚本
projects/     各次演练和正式比赛的实际工作区
```

## 基本原则

1. 所有具体赛题成果只能写入 `projects/<project_name>/`。
2. `competition/` 是官方要求的优先可信来源，不得随意修改。
3. `reference/` 只用于辅助选型，不能替代题意分析和实验验证。
4. 主 Agent 与审核 Agent 分别遵守：
   - `.agents/roles/main_agent.md`
   - `.agents/roles/reviewer_agent.md`
5. 每次开始工作，先读取当前项目的 `CURRENT.md`。

## 推荐启动顺序

```text
确认 ACTIVE_PROJECT
→ 读取角色说明
→ 读取 CURRENT.md
→ 读取最近一次审核
→ 按当前阶段执行
```

> 后续可在此补充仓库分支策略、负责人和常用入口。
