# Shared Data and Validation Contract

## Problem

为 Q1–Q5 提供唯一的数据读取、派生特征、重复分组、交叉验证与测试集隔离协议，防止各问使用不同口径或发生跨折泄漏。

## Inputs

- `src/附件一（训练集）.xlsx`：唯一监督训练源。
- `src/附件二（测试集）.xlsx`：Q1 冻结后预测输入。
- `src/附件三（测试集）.xlsx`：Q4 冻结后预测输入。
- `src/附件四（Excel表）.xlsx`：只读提交模板。
- `problem/manifest.md` 的五个输入 SHA-256。
- `results/raw/s1/` 的结构和质量审计证据。

## Outputs

- `results/raw/s3/data/feature_table.csv`
- `results/raw/s3/data/feature_schema.json`
- `results/raw/s3/folds/fold_assignments.csv`
- `results/raw/s3/run_manifest.json`
- 各问只引用上述同一 `feature_version` 和 `fold_version`。

## Variables and Units

| Variable | Definition | Unit |
|---|---|---|
| `temperature_C` | 原始温度 | °C |
| `frequency_Hz` | 原始频率，不裁剪 | Hz |
| `core_loss_W_per_m3` | 附件一响应 | W/m³ |
| `B[0:1024]` | 单周期磁通密度 | T |
| `B_m_T` | $\max_j|B_j|$ | T |
| `B_pp_T` | $\max B-\min B$ | T |
| `energy_proxy_Hz_T` | $fB_m$ | Hz·T |
| `material` | 材料1–4 | category |
| `waveform` | 正弦/三角/梯形 | category |

## Assumptions

1. 附件一的行是当前题目目标总体的可用观测；不假设行间独立。
2. 1,024 点按一个周期等间距排列，绝对相位起点未知。
3. 附件二、三的输入字段在预测时可获得，但其目标不可获得。
4. `max(abs(B))` 能作为题目“峰值”的主可执行口径；`B_pp/2` 用于敏感性验证。
5. 频率轻微越界是合法观测候选，不在无证据时改写。

## Mathematical Definition

派生量按 `04_solution_plan.md` 第 2 节。近形状组按“中心化→除以峰峰值→最大值相位对齐→64 块均值→0.02 量化→SHA-256”生成。工况组为：

\[
g=(m,T,w,\lfloor\log_{10}(f)/0.1\rfloor,
\lfloor\log_{10}(B_m)/0.1\rfloor).
\]

完全重复记录必须共享组。全局随机种子固定为 `20240920`；Bootstrap 和 Q5 稳健性分别使用 `20240921`、`20240922`。

## Objective

在模型拟合前生成可重建且互斥的训练/验证折，使所有 OOF 指标只使用未参与相应拟合、变换和调参的数据。

## Constraints

1. 原始 XLSX 只读，输入哈希不匹配立即终止。
2. 特征表必须恰有 12,400 个训练 `row_id`，且与源行一一对应。
3. 任一 `group_id` 只能属于一个外层折。
4. 分类折必须覆盖三类；回归折必须覆盖四材料、三波形和四温度，无法满足时按 5→4→3 折降低。
5. 禁止退回普通随机行切分来获得更好分数。
6. 附件二、三不得出现在 `fold_assignments.csv`。
7. 样本 ID 只作关联键，不能作为模型特征。

## Parameters

| Parameter | Frozen value |
|---|---|
| `feature_version` | `wave-v1` |
| `fold_version` | `group-v1` |
| outer folds | 5，必要时按合同降到 4 或 3 |
| inner folds | 3 |
| near-shape quantization | 0.02；组覆盖失败时 0.01、0.005 |
| log-frequency bin width | 0.10 decade |
| log-$B_m$ bin width | 0.10 decade |

## Training / Solving Procedure

1. 核验 SHA 和工作表 schema。
2. 为训练行生成稳定 `row_id=file|sheet|excel_row`。
3. 计算确定性 `wave-v1` 特征、完整指纹、近形状组和工况组。
4. 在任何评分前生成并保存外层折；检查组互斥和类别/因素覆盖。
5. 每个模型的内层调参只在外层训练部分重建分组折。
6. 学习型缩放/编码全部位于 Pipeline 内。
7. 模型冻结后分别加载附件二或三生成一次预测，且记录模型与配置哈希。

## Baseline

以合法分组折作为唯一 Baseline 验证框架。普通随机切分只允许作为“泄漏乐观程度”诊断，不参与模型选择、论文主指标或附件预测。

## Evaluation

- `row_id` 唯一、源行数、字段范围和有限值断言；
- 每组只属于一折；每折训练/验证索引不相交；
- 外层验证样本恰覆盖训练集一次；
- 同一输入和配置重复运行，特征表与折文件 SHA-256 一致；
- 原始五文件运行前后哈希一致。

回归任务统一使用下列冻结定义，其中 $y_i>0$，预测先按合同检查为正；数值保护仅用于指标函数：

\[
\operatorname{RMSLE}=\sqrt{\frac1n\sum_i\left[\log(1+\max(\hat y_i,0))-\log(1+y_i)\right]^2},
\]

\[
\operatorname{MAPE}=\frac{100\%}{n}\sum_i\frac{|y_i-\hat y_i|}{\max(|y_i|,1\ \mathrm{W/m^3})},
\]

\[
R^2=1-\frac{\sum_i(y_i-\hat y_i)^2}{\sum_i(y_i-\bar y)^2}.
\]

因此 RMSLE 使用自然对数 `log1p`，MAPE 分母下限为 `1 W/m³`，$R^2$ 在原始 W/m³ 尺度计算。模型合同若无明确例外，均引用本节而不得另行改变公式。

## Failure Conditions

- 输入哈希/schema 改变；
- 任一源行丢失、重复映射或特征非有限；
- 同组跨折；
- 3 折仍不能保证任务必要类别覆盖；
- 测试数据进入拟合、特征选择或调参；
- 重复运行产物不一致。

任一失败均阻断后续模型实验，先修复数据/验证流水线。

## Expected Artifacts

- 数据与特征 schema、行级特征表、折分配表；
- 分组统计与泄漏断言报告；
- 输入/输出文件哈希和完整执行命令；
- 原始 XLSX 未改写证明。
