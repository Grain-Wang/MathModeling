# Gate 4 Review — 主模型改进与证据构建

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_C`
- Gate: `G4`
- Stage: `S4 — 主模型改进与证据构建`
- Review Round: `1`
- Reviewed Commit: `2309b1e361701be9818544fa18740cd8f5694f2e`
- Verdict: **PASS**
- Reviewer Role: `Reviewer Agent / 独立阶段门控审核员`

---

# Final Verdict

## PASS — 同意进入 S5 / G5

经过对固定快照 `2309b1e361701be9818544fa18740cd8f5694f2e` 的审核，S4 已满足 G4 核心要求：

1. 改进均来自 S3 Baseline 暴露出的真实失败模式，而非无边界搜索；
2. Q2、Q3、Q4、Q5、Q1 均有对应实验、比较、消融或稳健性证据；
3. 主模型替换规则提前冻结，并按同折、同指标重新验证；
4. Q4 最终模型经过消融后冻结，没有为了复杂度而保留无收益特征；
5. Q5 即使稳定性改善仍未达到 Jaccard 门槛，仍保持禁止唯一推荐；
6. 未发现附件二、附件三参与调参、模型选择或阈值制定；
7. 独立复算报告显示 23/23 检查通过。

因此：

```text
G4 = PASS
Current Stage may advance: S4 -> S5
Next Gate: G5
```

本 PASS 仅代表主模型与证据链达到结果冻结前要求，不代表测试集预测、论文最终结果或最终提交已经通过。

---

# Review Findings

## 1. S4 改进路线合理

S4 没有重新扩大模型空间，而是按照 S3 失败信号执行：

- Q2：温度外推误差；
- Q4：Ridge 表达能力不足；
- Q5：最终模型稳定性不足；
- Q3：交互效应缺失；
- Q1：完美 OOF 后进行必要压力测试。

这一策略符合“失败驱动改进”。

## 2. Q2 温度修正 PASS

采用固定二次乘性温度修正：

- OOF RMSLE：0.360678 → 0.202567；
- 改善约 43.84%；
- 25°C、90°C 留一温度压力明显改善；
- 50°C 局部劣化已披露。

没有通过无限增加交互项追求训练拟合，因此保留了模型解释性。

## 3. Q4 主模型 PASS

HGB 与 Ridge 使用同一外层折、同一指标公平比较：

- Ridge RMSLE：0.200097；
- 完整 HGB RMSLE：0.076397；
- 18 特征 HGB RMSLE：0.070941。

最终采用：

```text
HGB + amplitude_and_condition (18 features)
```

消融逻辑合理：删除 shape 特征后性能进一步提升，因此没有保留无收益复杂度。

低 Bm 子组也进行了检查，未发现替换规则违规。

## 4. Q3 PASS WITH LIMITATIONS

两两交互模型：

- log-RMSE：0.343416 → 0.326667；
- 改善 4.88%；
- 500/500 Bootstrap 完成。

但共同支持范围仍有限，且部分水平比较稳定性不足。

允许进入 S5，但论文中必须保持：

```text
调整后关联
```

不能写成因果影响。

## 5. Q5 PASS WITH REQUIRED LIMITATION

Q5 是本阶段最重要的审查点。

积极部分：

- 使用最终 Q4 HGB；
- 严格 OOF 谱系闭合；
- 500/500 Bootstrap 完成；
- 稳定区域数量增加。

但：

```text
模型区域 vs 观测区域 Jaccard = 0.39535
阈值 = 0.50
```

因此：

```text
unique_recommendation_authorized = false
```

该处理正确。

进入 S5 后仍禁止：

- 给出唯一最优工况；
- 隐藏 Jaccard 失败；
- 用敏感性结果替代主门槛。

## 6. Q1 保持简单模型合理

Q1 完成：

- 相位变化；
- 幅值变化；
- 留一材料；
- 辅助字段消融。

Logistic 保持为最终模型符合“收益优先于复杂度”的原则。

## 7. 复现与证据链

`results/raw/main/verification_report.json`：

- check_count = 23；
- failed_count = 0；
- implementation_commit = `6accab2c0d9dbd8fbc0d362d9c60f9161f1e1901`；
- Q2/Q3/Q4/Q5/Q1 核心检查全部 PASS。

---

# Issue Classification

## Critical

None.

## Major

None.

## Minor

1. S5 前仍需明确测试集释放流程，保持附件二、三一次性冻结预测。
2. Q5 最终论文表述必须严格保留“不提供唯一推荐”的限制。
3. Q4 外推压力结果需要进入论文局限性部分。

以上均不阻断 S5。

---

# Authorization

Reviewer 授权：

```text
G4 = PASS
S4 -> S5 = AUTHORIZED
Next Gate = G5
```

S5 阶段重点：

1. 冻结最终模型与全部超参数；
2. 生成附件二、附件三正式预测；
3. 完成最终结果核验；
4. 生成论文级图表和结论；
5. 进入 G5 最终证据审核。

本审核文件仅新增审核记录，不修改模型、代码、结果或 CURRENT 状态。