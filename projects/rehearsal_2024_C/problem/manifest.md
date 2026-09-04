# Problem Manifest

- Project: `rehearsal_2024_C`
- Competition: 2024 年“华为杯”第二十一届中国研究生数学建模竞赛
- Selected problem: C 题《数据驱动下磁性元件的磁芯损耗建模》
- Verification time: 2026-09-04 21:35:23 +08:00
- Verification environment: `math_modeling` / Python 3.11.11
- Verification mode: 只读打开、工作表结构检查、SHA-256；未修改原始文件，未读取测试集目标答案。

## File Inventory

| Role | File | Bytes | SHA-256 | Open check | Structure |
|---|---|---:|---|---|---|
| 题目 | [数据驱动下磁性元件的磁芯损耗建模.docx](数据驱动下磁性元件的磁芯损耗建模.docx) | 743,935 | `3268B0B7A1A3CCC5E72CC1490F7389063A7DF35E35D307228E952504054E1EC8` | PASS | 标题、五个问题、参考文献和备注可读取 |
| 附件一：训练集 | [附件一（训练集）.xlsx](../src/附件一（训练集）.xlsx) | 107,702,460 | `C16AEE712BC0AD480B5285F17FA7FA57A5E22A1901D4A6ADB0A1EB83ECFB7FFC` | PASS | 材料1 `3401×1028`；材料2 `3001×1028`；材料3 `3201×1028`；材料4 `2801×1028` |
| 附件二：波形分类测试集 | [附件二（测试集）.xlsx](../src/附件二（测试集）.xlsx) | 890,928 | `B46A4BF69331A41D4CF6190C97906914619C76335BEF43EF37BA148CD99FC66C` | PASS | 测试集 `81×1028`，含表头，即 80 个样本 |
| 附件三：损耗预测测试集 | [附件三（测试集）.xlsx](../src/附件三（测试集）.xlsx) | 4,341,620 | `8C403B8D7717E42567EC7C6DEC204FEFF87023B83D45B87EC0C983C53A2D929A` | PASS | 测试集 `401×1029`，含表头，即 400 个样本 |
| 附件四：结果表 | [附件四（Excel表）.xlsx](../src/附件四（Excel表）.xlsx) | 14,973 | `D8FDFFDF63839F7B40D5DD87BE6923AF04AD1D52180072A47C5B4DF70832C1C8` | PASS | Sheet1 `401×3`；Sheet2、Sheet3 各 `1×1` |

## Completeness Assessment

- 题目正文：存在且可读。
- 题目要求的附件一至附件四：全部存在且可读。
- 附件一声明的四种材料：全部存在。
- 附件二与附件三样本数量和附件四结果表容量相符。
- 已发现缺失：`None`。
- 未核验项：尚未逐列审计数据类型、缺失值、重复值、异常值和标签分布；这些属于 S1，而非 S0。

## Path and Immutability Notes

四个 XLSX 当前位于项目内的 `src/`，这是历史位置，与“`src/` 只存代码”的文件协议不完全一致。为避免在初始化阶段移动或损坏 102.71 MiB 原始训练集，本次不移动文件；在完成受控复制/移动方案并同步 `.gitignore` 前，它们按原始只读附件处理。任何清洗、填表或格式转换必须写入 `results/raw/`，不得覆写上表原件。

## Applicable Competition Materials

- [2024 年官方资料索引](../../../competition/2024/README.md)
- [规则与时间线速查](../../../competition/2024/rules/2024_rules_and_timeline.md)
- [论文提交检查清单](../../../competition/2024/submission/2024_submission_checklist.md)
