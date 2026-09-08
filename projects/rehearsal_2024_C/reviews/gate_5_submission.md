# Gate 5 Submission — 结果核验、冻结与交接

## Review Metadata

- Repository: `Grain-Wang/MathModeling`
- Branch: `main`
- Active Project: `projects/rehearsal_2024_C`
- Gate: `G5`
- Stage: `S5 — 结果核验、冻结与交接`
- Review Round: `1`
- Freeze ID: `S5-FREEZE-2024C-V1`
- Prediction CSV Generation Commit: `c4d7121caf028df40788037fe5666ca63e2aa108`
- Prediction Finalization Commit: `c7bd4fc878a04632ed907fb19da67e55a21dc3f7`
- Final Verification Implementation Commit: `f677ce94a9b04bef6552c5201cac618349118232` 及其后仅文档/结果提交
- Reviewed Commit: 调用 Reviewer 时传入本提交推送后的 `git rev-parse HEAD` 完整 SHA
- Prepared at: 2026-09-08 +08:00

Reviewer 必须审核远程固定完整 SHA，不得改用随后变化的 branch HEAD。审核结论请新增为 `reviews/gate_5_review.md`，不得修改模型、代码、结果、本文或 `CURRENT.md`。

## Submitted Deliverables

- `work/10_result_freeze.md`
- `work/handoff/figure_handoff.md`
- `work/handoff/writing_handoff.md`
- `src/run_s5_predictions.py`
- `src/verify_s5_outputs.py`
- `src/test_s5_synthetic.py`
- `experiments/main/EXP-S5-PRED-001.json`
- `experiments/main/EXP-S5-VERIFY-001.json`
- `results/raw/s5/`
- `results/verified/result_registry.md`
- `results/verified/model_freeze.json`
- `results/verified/prediction_summary.json`
- `results/verified/verification_report.json`
- `results/verified/provenance.json`
- `results/verified/data/`
- `results/verified/q1/` 至 `q5/`
- `results/verified/submission/附件四（Excel表）.xlsx`
- `logs/experiments.md`
- `logs/decisions.md`
- `logs/ai_usage.md`
- `CURRENT.md`

## Frozen Model and Prediction Identity

### Q1

- 模型：shape-only multinomial Logistic；
- 模型 SHA-256：`1DAEB3B97CA30B28A8E1D6748347B79D2B4DDFF1844969172774C3CC8000810F`；
- 附件二预测 CSV SHA-256：`3CDFF53B66547E757DCED07A4D13FE492F8EA33B1F72116A789233ED8F0C5DA7`；
- 80条预测：正弦20、三角44、梯形16。

### Q4

- 模型：18特征 `amplitude_and_condition` HGB；
- 模型 SHA-256：`B284879E38401A301DF02FAF564A4CD482623816E9704DCDADFA8E25DF71AABD`；
- 附件三预测 CSV SHA-256：`1C16A4B46788906F6C15EAD2E72112F45F1F021C09512199541D6442C56D8290`；
- 400条预测均正有限，范围535.4564–2,315,612.5707 W/m³。

### Submission Workbook

- verified 副本 SHA-256：`1BB57B6FA0998802313594117ADACC03982075CC66FD85DFE967A92490D8F2F9`；
- 第2列前80项与 Q1 预测一致，81–400保持空白；
- 第3列400项与 Q4 的1位小数预测一致；
- 输出副本序号列为固定整数1–400；
- 原始附件四 SHA-256 保持 `D8FDFFDF63839F7B40D5DD87BE6923AF04AD1D52180072A47C5B4DF70832C1C8`。

## Verification Evidence

从项目目录执行：

```powershell
conda run --no-capture-output -n math_modeling python src/test_s5_synthetic.py
conda run --no-capture-output -n math_modeling python src/verify_s5_outputs.py --config experiments/s2_frozen_config.json
```

`results/verified/verification_report.json`：

- status=`PASS`；
- check_count=84；
- failed_count=0；
- 预测运行 manifest=`PASS`；
- prediction implementation dirty=`false`；
- S4独立复算=23/23 PASS；
- Q1/Q4模型哈希一致；
- Q1 80/80标签、编码、概率和波形谱系复算一致；
- Q4 400/400对数/原尺度/1位小数预测复算一致；
- 附件四工作表、表头、ID及80+400映射一致；
- 五个官方输入哈希未变；
- E001–E015连续完整。

`results/verified/provenance.json` 登记47个白名单文件，每个 verified 文件与 raw 来源 SHA-256 完全一致。论文和正式绘图不得引用白名单外的 raw 文件。

## Result Registry Coverage

- E001–E003：Q1 OOF/稳健性/附件二冻结预测；
- E004–E005：Q2总体改善与温度局限；
- E006–E007：Q3交互改善、Bootstrap与非因果边界；
- E008–E011：Q4选择、OOF、外推压力与附件三预测；
- E012–E014：Q5 Pareto、稳定区域与唯一推荐禁令；
- E015：附件四映射。

## Core Frozen Conclusions

1. Q1 分组 OOF Macro-F1=1.000，但不外推为附件二真实准确率。
2. Q2 温度修正 RMSLE 0.360678→0.202567，改善43.84%；50°C局部劣化保留。
3. Q3 交互模型较加性模型改善4.88%，500/500 Bootstrap有效；只作调整后关联。
4. Q4 最终18特征 HGB OOF RMSLE=0.070941；留一水平压力限制保留。
5. Q5 有118个 OOF Pareto点、27个折支持区域、42个Bootstrap稳定区域，但主 Jaccard=0.39535<0.50，禁止唯一推荐。
6. 附件二、三没有公开真值，冻结预测不是新的精度证据。

## Controlled Failure and Recovery Disclosure

为避免隐藏失败，S5保留了以下记录：

1. 首次运行在任何预测输出前因附件波形首列表头含单位文字而失败；
2. 修复后成功生成两份预测 CSV，但附件四序号公式被旧检查误当整数，后处理失败；
3. 恢复保护初版因手抄完整 SHA 错误而在读取预测 CSV 前拒绝；
4. 最终恢复从已保存失败清单读取 Git 提交，内存复算两份 CSV，确认恢复前后哈希不变，只完成附件四及冻结清单；
5. 首次独立验证在最后把表头“Evidence ID”误计入 ID 数量而失败，修正为严格解析 E001–E015 后通过；
6. 上述失败均未重新训练、调参、选模或改变预测数值。

失败清单均位于 `results/raw/s5/runs/`，权威 PASS 段以当前 manifest 的起止时间为准。

## Handoff Completeness

`work/handoff/writing_handoff.md` 已包含：

- 五问模型、公式、参数、逐问答案；
- E001–E015映射；
- 可写摘要数字；
- 附件二/三指定样本结果；
- Q2/Q3/Q4/Q5限制与禁止表述。

`work/handoff/figure_handoff.md` 已包含：

- 八图建议；
- 每图目的、数据文件、横纵轴、单位、Evidence ID和禁止误导表达；
- 图1/3/8的 Scientific Illustrator 要求；
- 数值图需具体 Python plotting Skill 的要求。

正式图片没有在本阶段绕过仓库规则生成：`.agents/skills/` 为空，且 `guide/figure_color_guide.md` 缺失；需要用户确认具体 Skill 后执行。G5要求的“绘图人员无需猜测数据含义”交接已完成，最终图片制作与论文一致性检查留在获授权后的后续工作中。

## Known Limitations

- Q1 完美 OOF 不等于未知附件二真值表现；
- Q2 50°C 局部劣化；
- Q3共同矩形支持仅14.24%，13/40对比符号稳定性不足0.90；
- Q4留一材料/温度最大RMSLE为0.37982/0.57496；
- Q5唯一推荐资格失败；
- 附件二、三无公开真值；
- 正式绘图尚待 Skill 与配色规范确认。

## Requested Verdict

请求 `PASS`。若 Reviewer 确认：

1. 模型、代码、参数和预测身份一致；
2. 84项验证足以支持47个白名单文件晋级；
3. E001–E015可追溯且结论强度未越界；
4. 附件四映射正确、原始附件未覆写；
5. 绘图/写作交接足以让后续人员不猜测数据含义；

请授权 `S5 → S6`，下一 Gate 为 G6。否则请按 Critical / Major / Minor 给出 Required Fix 和可复核 Acceptance Criteria。Main Agent 不自行宣布 G5 通过。
