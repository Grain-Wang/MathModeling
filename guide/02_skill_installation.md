# Skill 下载与安装

## 存放位置

所有 Skill 统一放在：

```text
.agents/skills/<skill_name>/
```

不要把 Skill 散落到项目目录或仓库根目录。

## 安装流程

1. 确认 Skill 来源和用途。
2. 阅读原始说明、许可证和依赖。
3. 下载到 `.agents/skills/`。
4. 将依赖安装到 `math_modeling` 环境。
5. 在演练项目中执行最小测试。
6. 测试通过后再标记为可用于正式比赛。

## 每个 Skill 建议记录

```text
来源：
版本或 commit：
用途：
依赖：
测试命令：
测试结果：
已知限制：
```

## 使用规则

- 使用前先读 Skill 自带说明。
- 未经演练验证的 Skill 不应成为正式比赛关键路径。
- Skill 生成的内容仍需人工或 Gate 审核。
- 不允许 Skill 修改 `competition/` 官方材料。

> 后续可增加 Skill 清单、版本锁定和自动测试规范。
