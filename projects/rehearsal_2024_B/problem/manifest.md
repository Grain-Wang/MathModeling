# Problem Manifest

- Project: rehearsal_2024_B
- Competition: 2024 年“华为杯”第二十一届中国研究生数学建模竞赛
- Selected problem: B 题《WLAN组网中网络吞吐量建模》
- Verification time: 2026-09-08 22:10 +08:00
- Verification environment: math_modeling / Python 3.11.11 / pandas 3.0.2
- Verification mode: 只读打开、DOCX XML 结构检查、CSV 解析与基础行列检查、SHA-256；未修改原始文件，未向测试集填值。
- Scope boundary: 本清单是 S0 输入完整性证据，不替代 S1 的逐字段数据审计。

## File Inventory

| Role | File | Bytes | SHA-256 | Open check | Structure |
|---|---|---:|---|---|---|
| 题目 | [WLAN组网中网络吞吐量建模.docx](WLAN组网中网络吞吐量建模.docx) | 218,659 | C9BF05EC66D1FD7C7D59712A5EFD00D23B37A90D6A30A16CD8A203CDD6AEA594 | PASS | 230 个非空段落；标题、问题1–3、数据说明和附录可读取 |
| 测试集 Q1/Q3，2 AP | [test_set_1_2ap.csv](data/test_set_1_2ap.csv) | 229,577 | A797C24918C7549AE2BE2A5B13D1059B4803C944BF17D41E314C2DD9D72223B2 | PASS | 80 行 × 47 列；40 个 test_id |
| 测试集 Q1/Q3，3 AP | [test_set_1_3ap.csv](data/test_set_1_3ap.csv) | 3,486,596 | 774B0E8FFCA2CED5B2849DA4719D2D9A7E0CF969753C8740F2FB1E36511F12B3 | PASS | 105 行 × 57 列；35 个 test_id |
| 测试集 Q2，2 AP | [test_set_2_2ap.csv](data/test_set_2_2ap.csv) | 1,265,585 | 1020D75AB0EA6369E243B87100A2B2E6BFDCFCC2C5E7BCCAC356FD07F099925B | PASS | 64 行 × 46 列；32 个 test_id |
| 测试集 Q2，3 AP | [test_set_2_3ap.csv](data/test_set_2_3ap.csv) | 2,795,529 | 8312A393D3957BE1AF2BD333BBB3158F2FA5753378CEC1B81A151E7F21CFAB67 | PASS | 87 行 × 56 列；29 个 test_id |
| 训练集，2 AP loc0/nav82 | [training_set_2ap_loc0_nav82.csv](data/training_set_2ap_loc0_nav82.csv) | 245,805 | 9F255CA192FDF1F99CC441E6321DA0EF7D4D1B2FFE9B58870533B74AE34D068E | PASS | 82 行 × 43 列；41 个 test_id |
| 训练集，2 AP loc0/nav86 | [training_set_2ap_loc0_nav86.csv](data/training_set_2ap_loc0_nav86.csv) | 378,917 | 4FB41351844354FC92483496B1CAAC9F95BA1E93E0C1276DE8232AB429250321 | PASS | 80 行 × 43 列；40 个 test_id |
| 训练集，2 AP loc1/nav82 | [training_set_2ap_loc1_nav82.csv](data/training_set_2ap_loc1_nav82.csv) | 409,486 | 7F2E41CFACDE6BECFD0BF6E5F66DE9E39EB5FF1199FF664A1180882E9FA404B4 | PASS | 78 行 × 43 列；39 个 test_id |
| 训练集，2 AP loc1/nav86 | [training_set_2ap_loc1_nav86.csv](data/training_set_2ap_loc1_nav86.csv) | 352,700 | 07831A66D218EF6BB23D2504CE2CC382104F9E48CDCC716A37D30D412B99D8AD | PASS | 74 行 × 43 列；37 个 test_id |
| 训练集，2 AP loc2/nav82 | [training_set_2ap_loc2_nav82.csv](data/training_set_2ap_loc2_nav82.csv) | 345,269 | 3C9F76FC140D6DDF900F515D16FBABEDE182152DBC09919CE29CA0103624A08F | PASS_WITH_ANOMALY | 80 行 × 43 列；41 个 test_id；末两行字段错位 |
| 训练集，3 AP loc30/nav82 | [training_set_3ap_loc30_nav82.csv](data/training_set_3ap_loc30_nav82.csv) | 828,587 | A539D3C29A80DA3CA002B6A9C0E49B7D7BC501A17C965192309C0229E2A0035B | PASS | 123 行 × 55 列；41 个 test_id |
| 训练集，3 AP loc30/nav86 | [training_set_3ap_loc30_nav86.csv](data/training_set_3ap_loc30_nav86.csv) | 761,332 | 8DA8932B49FDFEA4E5521B045F0D407F74721E7401CC4156EA8AA6B5BE8FBCC8 | PASS_WITH_ANOMALY | 120 行 × 55 列；40 个 test_id；3 个 AP0 RSSI 列全空 |
| 训练集，3 AP loc31/nav82 | [training_set_3ap_loc31_nav82.csv](data/training_set_3ap_loc31_nav82.csv) | 912,194 | ADCD55978E14288539FE239AEBF7292D1AD961CD82813B4493E00934CCCB6FFB | PASS | 126 行 × 53 列；42 个 test_id |
| 训练集，3 AP loc31/nav86 | [training_set_3ap_loc31_nav86.csv](data/training_set_3ap_loc31_nav86.csv) | 783,574 | 1E44346B859058B9E7B0C59026E9E06F9F44CE093952ACE88F787807644A44EC | PASS | 108 行 × 53 列；36 个 test_id |
| 训练集，3 AP loc32/nav82 | [training_set_3ap_loc32_nav82.csv](data/training_set_3ap_loc32_nav82.csv) | 3,691,461 | B07ABD7E401090F5B6667A61708FDE75D48FF0BD0158AB9E4D31565CBC369112 | PASS | 111 行 × 53 列；37 个 test_id |
| 训练集，3 AP loc32/nav86 | [training_set_3ap_loc32_nav86.csv](data/training_set_3ap_loc32_nav86.csv) | 2,023,495 | EF0C5478D00BEB47C04332A84569CD54F34CA2A047A722E97F27CB8E47B716DA | PASS | 60 行 × 53 列；20 个 test_id |
| 训练集，3 AP loc33/nav82 | [training_set_3ap_loc33_nav82.csv](data/training_set_3ap_loc33_nav82.csv) | 2,720,436 | BEAB6D49A62A089F5A0996C572E98DA3D50560B0F9F1F7D12284BF41353C1D26 | PASS | 111 行 × 53 列；37 个 test_id |
| 训练集，3 AP loc33/nav88 | [training_set_3ap_loc33_nav88.csv](data/training_set_3ap_loc33_nav88.csv) | 3,251,013 | 4DCE45EC10ED08DB154C979CD122CEAFC428E0B772D1A33E2D2AC6E1D3B9174E | PASS | 99 行 × 53 列；33 个 test_id |

## Inventory Summary

- 输入文件：18 个，总计 24,700,215 bytes（约 23.56 MiB）。
- 题目：1 个 DOCX，标题与 3 个问题全部存在。
- 训练集：13 个 CSV，共 1,252 行。
- 测试集：4 个 CSV，共 336 行；题目明确点名的 test_set_1_2ap、test_set_1_3ap、test_set_2_2ap、test_set_2_3ap 全部存在。
- 17/17 CSV 均可由 pandas 读取；基础检查未发现完全重复行。
- 2 AP 数据每个正常 test_id 预期 2 行，3 AP 数据每个正常 test_id 预期 3 行；除下述已知错位记录外，基础组大小一致。

## Completeness Assessment

- 本地题目正文：存在且可读。
- 本地训练集和题目点名的四个测试集：存在且可读。
- 训练集包含 2 AP 与 3 AP、多个 loc/nav 场景；测试集覆盖问题1/3与问题2所需的 2 AP 和 3 AP 输入。
- 本机进入 S1 所需原始资料：具备。
- 已发现缺失文件：None。
- 真实性限制：当前没有官方原始压缩包的总哈希、稳定下载 URL 或发布方逐文件校验值，故只能声明“本地清单完整且可读”，不能声明与官方包逐字节一致。
- 未核验项：逐字段语义、缺失机制、异常分布、单位一致性、潜在泄漏和验证切分属于 S1，不在 S0 宣布通过。

## Known Input Risks

### A01 — training_set_2ap_loc2_nav82.csv 末两行字段错位

- 受影响：pandas 行索引 78、79，即 test_id 40、41 的 ap_1 记录。
- 现象：本应为 RSSI 的字段出现 471f、sta_1 等标识符，nss、mcs、per、num_ampdu、ppdu_dur、other_air_time、seq_time、throughput 均为空。
- 影响：两个 test_id 只剩 1 条结构正常记录，不能按完整 2 AP 样本直接训练。
- 外部佐证：数模论坛 B 题专家回复“异常数据可以自行剔除”：https://www.shumo.com/forum/forum.php?mod=viewthread&tid=107845
- S0 决策：不改原件；S1 必须冻结剔除/隔离规则并记录前后行数。

### A02 — training_set_3ap_loc30_nav86.csv 三个 RSSI 列全空

- 全空列：ap_from_ap_0_sum_ant_rssi、ap_from_ap_0_max_ant_rssi、ap_from_ap_0_mean_ant_rssi。
- 影响：该场景不能直接使用上述三个方向特征；需在 S1 判定缺失机制和候选替代/缺失指示策略。
- 外部佐证：该文件的数据问题被收入 B 题专家“普遍问题汇总”：https://www.shumo.com/forum/forum.php?mod=viewthread&tid=107966
- S0 决策：记录但不填补，不用对称 RSSI 擅自替代。

### A03 — 三条 NSS=0

题面 PHY Rate 表只列 NSS1/NSS2，但本地训练集中有三条 nss=0：

- training_set_2ap_loc1_nav86.csv：test_id 7 / ap_1；
- training_set_3ap_loc33_nav82.csv：test_id 3 / ap_2；
- training_set_3ap_loc33_nav82.csv：test_id 21 / ap_0。

S1 必须判断其是否为“无有效速率/失败状态”哨兵或异常记录；不得在 S0 静默改为 1。

### A04 — 表头与模式不完全统一

- training_set_3ap_loc30_nav82.csv 和 training_set_3ap_loc30_nav86.csv 多出全空 predict throughput、error% 列。
- 测试集保留待填预测列，test_set_1_* 中 error% 重名，pandas 会将第二列解析为 error%.1。
- 题面 4.2 使用 num_ppdu 描述聚合个数，CSV 表头为 num_ampdu；S1 必须依据附录和数据语义明确统一口径。

## Path and Immutability Notes

- 17 个 CSV 原位于 src/；2026-09-08 S0 按仓库文件协议受控移动至 problem/data/。
- 移动前 SHA-256 即上表值；迁移后必须重新校验为相同值。
- 原始 DOCX 和 CSV 均按只读输入管理；清洗、特征表、填值结果和预测必须写入 results/raw/，不得覆盖原件。
- /projects/**/*.csv 忽略规则覆盖 problem/data/，因此 CSV 不会进入 Git 或远程仓库。
- 远程协作方必须从授权来源取得同名数据，并按上表 SHA-256 校验；不得用 manifest 链接存在性误判远程包含原始文件。

## Applicable Competition Materials

- [2024 年官方资料索引](../../../competition/2024/README.md)
- [规则与时间线速查](../../../competition/2024/rules/2024_rules_and_timeline.md)
- [论文提交检查清单](../../../competition/2024/submission/2024_submission_checklist.md)
- [官方论文模板](../../../competition/2024/official_templates/2024_paper_template.doc)