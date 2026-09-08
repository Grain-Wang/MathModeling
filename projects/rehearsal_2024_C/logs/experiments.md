# Experiment Log

本日志按阶段追加记录：S0–S2 条目不包含模型训练；S3 起记录实际训练与 OOF 预测。附件二、三始终不得用于调参或结果选择。

| Time (Asia/Shanghai) | ID | Stage | Purpose | Inputs | Method / command | Result | Status |
|---|---|---|---|---|---|---|---|
| 2026-09-04 21:35 | X0001 | S0 | 验证运行环境 | `math_modeling` | 导入 NumPy、pandas、SciPy、scikit-learn、matplotlib、openpyxl 等核心依赖并输出版本 | Python 3.11.11；核心导入 `smoke=PASS` | PASS |
| 2026-09-04 21:35 | X0002 | S0 | 确认题目正文可读 | `problem/*.docx` | `python-docx` 只读解析段落 | 识别为 2024 C 题，含问题一至问题五、参考文献和备注 | PASS |
| 2026-09-04 21:35 | X0003 | S0 | 确认附件完整并可打开 | `src/*.xlsx` | openpyxl `read_only=True`；记录工作表、行列和 SHA-256 | 附件一至四全部打开；结构与题目描述相符 | PASS |
| 2026-09-04 21:35 | X0004 | S0 | 确认 2024 官方资料可用 | `competition/2024/` | PDF 解析、OLE 文件头、大小、SHA-256 和本地链接检查 | 2 个 PDF、2 个 DOC 及导航文件通过检查 | PASS |
| 2026-09-07 | X0005 | S1 | 首次全量数据审计并校准检查语义 | 题目 DOCX、附件一至四 | `conda run -n math_modeling python projects/rehearsal_2024_C/src/s1_data_audit.py`；openpyxl 只读流式扫描 | 原件哈希稳定；发现题面频率范围小幅偏差；初版错误地把范围偏差列为 Major，且把附件四表头算作已填值 | INVALID — audit rule fixed, data untouched |
| 2026-09-07 | X0006 | S1 | 完成可复核的结构、质量、重复和泄漏审计 | 同 X0005 | 修正检查后重新运行同一命令；输出到 `results/raw/s1/` | 154 checks；0 FAIL、5 WARN；12,400+80+400 条记录元字段/波形无缺失或非有限；训练—测试完全波形重合为 0；输入前后 SHA-256 一致 | PASS |
| 2026-09-07 | X0007 | S2 | 验证总体方案、模型合同与冻结配置的结构可执行性 | `work/04_solution_plan.md`、5 份 Q 合同、共享合同、`work/05_experiment_plan.md`、冻结 JSON | 检查 14 个合同必需章节、JSON 解析和输入哈希、Markdown 链接；在 `math_modeling` 导入计划 API | 5/5 Q 合同结构 PASS；config/hash/link PASS；scikit-learn 1.7.1 API PASS；检测 16 逻辑 CPU；未拟合模型 | PASS |
| 2026-09-07 | X0008 | S2 | 验证 G2 Round 2 合同修订闭环 | 修订后的总体方案、共享/Q4/Q5 合同、实验计划、冻结 JSON、response/submission | 检查 5×14 必需章节、5 个输入哈希、8 个 `sha256_utf8_lf` 合同哈希、Q5 门槛、8 份文档链接、旧策略残留、Git 大文件边界和 diff | 全部 PASS；原始 XLSX 跟踪数 0；未新增 `src/`/`results/`，未训练模型或生成预测 | PASS |

| 2026-09-07 16:37 | X0009 | S3 | 验证 S3 源码和退化边界 | S3 源码、8 份实验描述 | `python -m compileall`；`python src/test_s3_synthetic.py` | 编译 PASS；Pareto 支配/并列、重复四分位边界和零范围代表点合成断言 PASS；Ruff 未安装，未临时增加依赖 | PASS |
| 2026-09-07 16:55 | EXP-S3-DATA-001 | S3 | 构建共享特征、身份与固定折 | 附件一；冻结配置；8 份合同；其余输入仅核验哈希 | `python src/build_features.py --config experiments/s2_frozen_config.json`，连续运行两次 | 12,400 行、48 数值特征、4,323 工况组、5+5 折；同组跨折 0；精确重复额外行 1；三项重建 SHA 完全一致 | PASS |
| 2026-09-07 16:59 | EXP-Q1-BASE-001 | S3 | Q1 shape-only 分类基线 | feature table；Q1 folds | `python src/run_q1.py --model logistic --stage baseline --config ...` | 12,400 条 OOF；Macro-F1/Accuracy/Balanced Accuracy=1.000；组泄漏 0 | PASS |
| 2026-09-07 16:59 | EXP-Q2-BASE-001 | S3 | Q2 传统 Steinmetz 基线 | 材料1正弦波 1,067 行；regression folds | `python src/run_q2.py --model steinmetz --stage baseline --config ...` | OOF RMSLE=0.3607、MAPE=32.53%、R²=0.9412；留一温度结果已保存；组泄漏 0 | PASS |
| 2026-09-07 16:59 | EXP-Q3-DESC-001 | S3 | Q3 三因素描述基线 | feature table | `python src/run_q3.py --model descriptive --stage baseline --config ...` | 48 格完整；共同矩形支持 1,766 行（14.24%） | PASS |
| 2026-09-07 16:59 | EXP-Q3-BASE-001 | S3 | Q3 调整后加性关联基线 | feature table；regression folds | `python src/run_q3.py --model additive --stage baseline --config ...` | OOF log-RMSE=0.3434；原尺度 R²=0.6036；最大有限 Gram 条件数 183.45；组泄漏 0 | PASS |
| 2026-09-07 16:59 | EXP-Q4-NULL-001 | S3 | Q4 中位数参照 | feature table；regression folds | `python src/run_q4.py --model median --stage baseline --config ...` | 全局/分组中位数 OOF RMSLE=1.9002/1.8311；组泄漏 0 | PASS |
| 2026-09-07 16:59 | EXP-Q4-BASE-001 | S3 | Q4 嵌套分组 Ridge 基线 | wave-v1；regression folds；中位数参照 | `python src/run_q4.py --model ridge --stage baseline --config ...` | OOF RMSLE=0.2001、MAPE=15.85%、R²=0.9507；优于两种中位数；组泄漏 0 | PASS |
| 2026-09-07 17:00 | EXP-Q5-BASE-001 | S3 | Q5 严格 OOF 实测工况 Pareto 基线 | Q4 OOF/full-fit、谱系、候选身份 | `python src/run_q5.py --mode oof-observed-pareto --stage baseline --config ...` | 12,236 个去重候选；105 OOF Pareto、109 full-fit、130 观测点；候选谱系 12,236/12,236 PASS；Jaccard=0.0962，唯一推荐被拒绝 | PASS WITH S4 STABILITY PENDING |
| 2026-09-07 17:00 | X0010 | S3 | 独立复算全部 S3 证据 | 8 份 manifest；Q1–Q5 CSV/JSON | `python src/verify_s3_outputs.py --config experiments/s2_frozen_config.json` | manifest=8、固定 SHA/环境/洁净断言 PASS；核心指标、105 点 Pareto 和 12,236 条候选谱系复算 PASS | PASS |

## S3 Modeling Results

- 已训练 Baseline：Q1 Logistic、Q2 Steinmetz、Q3 加性 Ridge、Q4 Ridge；另有 Q4 两种中位数参照。
- 已生成预测：仅附件一的分组 OOF 与 full-fit 参考；未生成附件二、三测试预测。
- 已实现最后一问：严格 OOF 实测工况 Pareto 及降级诊断；当前不授权唯一推荐。
- `results/raw/s3/` 与 `results/raw/baseline/` 均为待 G3/G5 审核的原始证据，`results/verified/` 未写入。

## 截至 S2 的历史状态（已由上方 S3 记录取代）

- 截至 S2 已训练模型：`None`
- 截至 S2 已选择超参数：`None`
- 截至 S2 已生成预测：`None`
- 已查看测试集目标答案：`No evidence / not available`
- 当时 `results/raw/s1/` 只含未核验的数据审计证据，S2 只新增文档和冻结配置；`results/verified/` 至今仍不含正式模型结论。

## S4 Stage Events

| Time (Asia/Shanghai) | ID | Stage | Purpose | Inputs | Method / command | Result | Status |
|---|---|---|---|---|---|---|---|
| 2026-09-08 | X0011 | S4 | 拉取并核对 G3 审核、进入 S4 | `reviews/gate_3_review.md` | 核对 review commit `076a7a3…`、Verdict 和 Reviewed Commit | G3=PASS；S3→S4 AUTHORIZED；识别 3 项 Minor 与 5 项强制优先任务 | PASS |
| 2026-09-08 | X0012 | S4 | 校准 Q4 消融胜者到 Q5 的交接 | 初版实现 `50f812c…` 的 Q2/Q4 预运行 | 消融发现18特征优于48特征，同时发现初版未把消融胜者物化为严格 OOF/full-fit 工件；保留追加日志，修复后统一重跑 | SUPERSEDED — authoritative rerun on `6accab2…` |
| 2026-09-08 | X0013 | S4 | 关闭 G3 三项 Minor 并做静态验证 | 日志、Q5 退化分支、manifest 命令 | `test_s3_synthetic.py`、`compileall`、相对命令断言 | 两个新增直接边界测试 PASS；全部 S4 CLI 导入 PASS；相对命令不含本机项目绝对路径 | PASS |
| 2026-09-08 | EXP-Q2-MAIN-001 | S4 | 二次乘性温度修正同折比较 | 1,067 条材料1正弦波；固定 regression folds | `python src/run_s4_q2.py --mode main --config ...` | RMSLE 0.36068→0.20257，改善43.84%；3/4温度不劣化；采用二次温度修正 | PASS |
| 2026-09-08 | EXP-Q2-SENS-001 | S4 | Q2 留一温度、峰值和重复敏感性 | Q2 主模型与 S3 Baseline | `python src/run_s4_q2.py --mode sensitivity --config ...` | LOTO 25/90°C 明显改善；`B_pp/2`相对变化+0.36%；去重变化0；50°C小幅劣化 | PASS |
| 2026-09-08 | EXP-Q4-MAIN-001 | S4 | 18候选 HGB 嵌套分组比较 | 12,400 行；固定外5/内3折；Ridge | `python src/run_s4_q4.py --mode main --config ...` | HGB RMSLE=0.07640，相对 Ridge 改善61.82%；主要子组最大变化-50.64%；RF不触发 | PASS |
| 2026-09-08 | EXP-Q4-ABL-001 | S4 | 工况-only/幅值/完整特征消融并冻结最终模型 | HGB 各折已选参数 | `python src/run_s4_q4.py --mode ablation --config ...` | 2/18/48特征 RMSLE=0.14383/0.07094/0.07640；最终采用18特征工况+幅值 HGB | PASS |
| 2026-09-08 | EXP-Q4-STRESS-001 | S4 | Q4 低Bm、边界/尾部和留一水平压力 | 最终18特征 HGB | `python src/run_s4_q4.py --mode stress --config ...` | 低Bm RMSLE=0.08328；LOMO max=0.37982；LOTO max=0.57496 | PASS WITH EXTRAPOLATION LIMITS |
| 2026-09-08 | EXP-Q5-ROB-001 | S4 | 最终Q4胜者的严格OOF Pareto与500次组Bootstrap | Q4 final OOF/full-fit/lineage | `python src/run_s4_q5.py --mode robustness --config ...` | 118 OOF Pareto；27折支持区域；42 Bootstrap稳定区域；Jaccard=0.39535<0.50；唯一推荐禁用 | PASS WITH NO UNIQUE RECOMMENDATION |
| 2026-09-08 | EXP-Q5-SENS-001 | S4 | Q5 频率、峰值、重复敏感性 | 最终候选表 | `python src/run_s4_q5.py --mode sensitivity --config ...` | 相对主口径 OOF 区域 Jaccard最低0.881；不覆盖主Gate失败 | PASS |
| 2026-09-08 | EXP-Q3-INT-001 | S4 | 三组预定义两两交互同折比较 | 12,400 行；加性 Baseline | `python src/run_s4_q3.py --mode interaction --config ...` | log-RMSE 0.34342→0.32667，改善4.88%；采用交互模型 | PASS |
| 2026-09-08 | EXP-Q3-BOOT-001 | S4 | Q3 工况组簇 Bootstrap | Q3 交互胜者 | `python src/run_s4_q3.py --mode bootstrap --config ...` | 500/500有效；40个两两对比中27个符号稳定度≥0.90 | PASS |
| 2026-09-08 | EXP-Q3-SENS-001 | S4 | Q3 共同支持、峰值和重复敏感性 | Q3交互胜者 | `python src/run_s4_q3.py --mode sensitivity --config ...` | 共同支持14.24%；峰值相对+2.28%；去重+0.004%；仅保留稳定调整关联 | PASS |
| 2026-09-08 | EXP-Q1-ABL-001 | S4 | Q1 真实波形不变性、留一材料和特征/辅助消融 | 附件一；Logistic折模型 | `python src/run_s4_q1.py --config ...` | 相位/幅值一致率1.0；LOMO min F1=1.0；辅助-only F1=0.41976；树模型不运行 | PASS |
| 2026-09-08 | EXP-S4-COMP-001 | S4 | 独立复算与运行谱系总验证 | 11份run manifest；Q1–Q5核心输出 | `python src/verify_s4_outputs.py --config ...` | 23/23 PASS；统一实现SHA=`6accab2…`；环境/洁净/测试附件隔离/主指标/Pareto均通过 | PASS |

## S5 Stage Events

| Time (Asia/Shanghai) | ID | Stage | Purpose | Inputs | Method / command | Result | Status |
|---|---|---|---|---|---|---|---|
| 2026-09-08 | X0014 | S5 | 拉取并核对 G4 审核、进入 S5 | `reviews/gate_4_review.md` | 核对 Verdict、Reviewed Commit、Review Commit 和 S5 授权；读取结果核验/绘图/论文交接协议 | G4=PASS；S4→S5 AUTHORIZED；识别 Q5/Q3/Q4 强制表述限制及绘图 Skill/配色指南缺口 | PASS |
