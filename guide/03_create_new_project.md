# 创建新项目

## 项目命名

建议：

```text
rehearsal_<year>_<problem>
contest_<year>_<problem>
```

例如：

```text
projects/rehearsal_2025_C/
projects/contest_2026_B/
```

## 创建流程

1. 从 `templates/project_template/` 复制项目模板。
2. 将选定题目和附件放入 `problem/`。
3. 建立或更新 `problem/manifest.md`。
4. 初始化 `CURRENT.md`。
5. 写明项目类型、题号、负责人和当前阶段。
6. 做一次初始 Git 提交。

## 初始提交建议

```bash
git add .
git commit -m "init project: <project_name>"
git tag <project_name>-start
```

## 创建后检查

- 项目目录唯一；
- 题目与附件齐全；
- 原始数据未被修改；
- `CURRENT.md` 指向 S0；
- 日志文件已创建；
- 没有把赛题文件放在仓库根目录。

> 后续可加入 `scripts/create_project.py` 的用法。
