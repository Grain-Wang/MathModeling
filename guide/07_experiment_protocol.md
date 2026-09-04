# 实验执行规范

## 实验分类

```text
experiments/baseline/
experiments/main/
experiments/comparison/
experiments/ablation/
experiments/sensitivity/
experiments/robustness/
```

按题型使用，不要求机械做全套。

## 每次实验至少记录

- 实验 ID；
- 目的；
- 使用数据；
- 模型与版本；
- 参数配置；
- 随机种子；
- 执行命令；
- 输出路径；
- 运行时间；
- 主要结果；
- 是否有效。

## 基本纪律

1. 原始数据不覆盖。
2. 路径尽量使用相对路径。
3. 随机过程固定种子。
4. 训练、验证、测试或回测划分明确。
5. 不使用测试集反复调参。
6. 不只保留最好一次运行。
7. 失败实验也记录原因。
8. 实验输出先进入 `results/raw/`。

## 推荐日志

```text
logs/experiments.md
```

## 推荐实验编号

```text
EXP-Q2-BASE-001
EXP-Q2-ABL-001
```

> 后续可增加配置文件模板和自动实验登记脚本。
