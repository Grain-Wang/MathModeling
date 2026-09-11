# 绘图规范

## 数据来源

正式论文图默认只能使用：

```text
results/verified/
```

探索性图可以使用 `results/raw/`，但不得直接进入最终论文。

## 每张图应记录

- 图编号和目的；
- 数据文件；
- 生成脚本；
- 横纵轴含义；
- 单位；
- 图例说明；
- 对应 Evidence ID；
- 导出格式。

## 基本要求

1. 一张图回答一个明确问题。
2. 坐标轴、单位和图例完整。
3. 不截断坐标轴制造夸大效果。
4. 比较图使用一致尺度。
5. 有随机性时考虑误差条或区间。
6. 图中数字与 `verified` 结果一致。
7. 保留可重新生成的脚本。

## 文件建议

```text
figures/scripts/
figures/data/
figures/final/
```

最终优先导出：

```text
PDF / SVG + PNG
```

## 交接依据

读取：

```text
work/handoff/figure_handoff.md
```

## 注意事项
1. 所有的图片绘制都需要具体到使用哪一个skill,不可以不使用skill直接画图，画图前要和我确实一下，具体使用哪种skill，一句话给出原因
2. 具体的图片类型要求见同目录下面的guide\figures_guide.md
3. 配色参考guide\figure_color_guide.md