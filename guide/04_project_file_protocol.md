# 项目文件存放协议

每个项目的文件应保持在：

```text
projects/<project_name>/
```

## 推荐结构

```text
problem/       原题、原始数据和附件
work/          分析、方案、模型合同、交接文件
src/           可复用源代码
experiments/   各类实验入口与配置
results/raw/   未核验实验输出
results/verified/ 已核验正式结果
figures/       图表及其生成脚本
paper/         论文与附录
reviews/       Gate 提交和审核意见
logs/          决策、实验和 AI 使用记录
CURRENT.md     当前唯一状态源
```

## 核心规则

1. `problem/` 中原始文件默认只读。
2. 临时结果只能进入 `results/raw/`。
3. 论文和正式绘图只能引用 `results/verified/`。
4. 审核意见只能写入 `reviews/`。
5. 每个关键模型先写模型合同，再实现代码。
6. 不在根目录堆放临时脚本和结果文件。
7. 文件名应表达内容和阶段，避免 `final2_new_latest`。

## 建议命名

```text
q1_baseline_metrics.csv
q2_main_model_report.md
gate_3_submission.md
gate_3_review.md
```

> 后续可加入归档、清理和大文件管理规则。
