# Q1 Model Contract — 励磁波形分类

## Problem

从一个周期的 1,024 点磁通密度序列识别正弦波、三角波和梯形波；验证分类合理性，并在模型冻结后给附件二 80 个样本生成类别编码。

## Inputs

- 训练：附件一的 $B_{0:1023}$ 与波形标签。
- 最终预测：附件二的 $B_{0:1023}$。
- 主模型只使用共享合同中的 `wave-v1` 形状特征。
- 温度、频率、材料不进入主分类输入，只允许在 S4 消融中作为“辅助字段增量”诊断。

## Outputs

- 每个样本的三类概率与类别 $\hat c$；
- 编码：1=正弦波、2=三角波、3=梯形波；
- OOF 预测、混淆矩阵、逐类指标与分材料/温度/频率误差；
- 附件二 80 个冻结分类、三类数量、指定 10 个 ID 的正文表格数据；
- 附件四副本第 2 列。

## Variables and Units

| Variable | Meaning | Unit |
|---|---|---|
| $B_j$ | 第 $j$ 个磁通密度点 | T |
| $x$ | `wave-v1` 形状特征 | 混合；标准化在折内完成 |
| $y$ | 三类真实波形标签 | category |
| $p_k(x)$ | 类别 $k$ 的预测概率 | [0,1] |
| $\hat c$ | 最大概率类别的数字编码 | {1,2,3} |

## Assumptions

1. 三类差异主要存在于波形形状，不应依赖材料或测试集采样分布代理。
2. 幅值缩放和循环相位不应改变类别，因此主形状特征需尽量具备尺度/相位稳健性。
3. 附件一标签可信；类别不完全均衡但每类样本充足。
4. 分组 OOF 误差比随机行切分更接近新工况分类风险。

## Mathematical Definition

Baseline 为多项逻辑回归：

\[
p_k(x)=\frac{\exp(w_k^Tx+b_k)}{\sum_{r=1}^{3}\exp(w_r^Tx+b_r)},\qquad
\hat c=\arg\max_k p_k(x),
\]

通过带 $L_2$ 正则的多类交叉熵估计参数。主候选为 HistGradientBoostingClassifier，以浅树的加法模型拟合多类对数损失；随机森林仅作为一个非线性挑战者，不做模型堆叠。

## Objective

训练目标为折内多类对数损失；模型选择目标为外层 OOF Macro-F1 最大，并要求所有类别 Recall 可接受。附件二输出只取冻结模型的最大概率类别。

## Constraints

1. 主输入不含温度、频率、材料、样本序号和损耗。
2. 使用 `near_shape_group` 的 StratifiedGroupKFold；同组不跨折。
3. 特征缩放只在训练折拟合。
4. 附件二不得参与阈值、特征或超参数选择。
5. 三类编码固定，不因模型内部类别排序改变。

## Parameters

| Model | Frozen finite search |
|---|---|
| Logistic baseline | `C ∈ {0.1,1,10}`，`class_weight ∈ {None,balanced}`，最大迭代 2,000 |
| HistGradientBoosting main | `learning_rate ∈ {0.05,0.1}`，`max_leaf_nodes ∈ {15,31}`，`min_samples_leaf ∈ {20,50}`，`l2_regularization ∈ {0,1}`，最大迭代 300 |
| RandomForest challenger | 400 trees，`max_depth ∈ {None,12}`，`min_samples_leaf ∈ {1,4}`，`max_features ∈ {sqrt,0.7}` |

主候选最多 12 个预先抽取组合，固定 `random_state=20240920`；不扩展到 XGBoost/深度网络，除非后续新 Gate 明确批准。

## Training / Solving Procedure

1. 读取共享特征表和固定外层折。
2. 在每个外层训练部分做 3 折分组内层选择；每个候选保存配置和内层分数。
3. 生成全部 12,400 条 OOF 概率和类别，不用训练内分数替代。
4. 按主指标和进入条件选择 Baseline 或一个非线性候选。
5. 用附件一全量重拟合胜者，冻结模型/特征 schema/类别编码和文件哈希。
6. 只运行一次附件二预测，校验 ID、值域、数量和附件四关联。

## Baseline

`wave-v1` 形状特征 + StandardScaler + 多项逻辑回归。另记录多数类准确率，但多数类不是可接受的任务模型。

## Evaluation

- 主指标：外层 OOF Macro-F1；
- 辅助：Accuracy、Balanced Accuracy、逐类 Precision/Recall/F1、混淆矩阵；
- 子组：材料、温度、频率分箱和 $B_m$ 分箱；
- 稳健性：留一材料压力测试、相位循环平移与幅值缩放不变性；
- 比较：同一 OOF 样本上的簇 Bootstrap 95% 指标差区间；
- 辅助字段消融：形状-only 与形状+温度/频率/材料比较，只用于判断代理依赖，不自动采用后者。

## Failure Conditions

- 任一类别缺失于验证折或同组跨折；
- Macro-F1 未显著优于多数类/简单形状 Baseline；
- 某类 Recall <0.90，或关键子组 Recall 比总体低超过 0.10；
- 相位平移或幅值缩放导致类别大量改变（>1%）；
- 非线性候选对 Logistic 的 Macro-F1 提升不为正，或任一类别 Recall 下降超过 0.02；
- 使用辅助字段后提升但留一材料表现明显下降，说明学到数据代理；
- 产生非有限概率、类别编码错位或运行超预算。

失败时优先修正特征/分组并回退 Logistic 或透明形状规则，不增加无依据复杂度。

## Expected Artifacts

- `results/raw/s3/q1/baseline_oof_predictions.csv`
- `results/raw/s3/q1/baseline_metrics.json`
- `results/raw/s3/q1/confusion_matrix.csv`
- `results/raw/s4/q1/model_comparison.csv`
- `results/raw/s4/q1/invariance_checks.csv`
- 冻结后 `results/raw/s4/q1/attachment2_predictions.csv`
- 冻结后附件四副本及指定样本/类别计数表
