# Gate 0 Submission

## Stage

S0 — 项目初始化与约束确认

## Review Snapshot

- Repository: Grain-Wang/MathModeling
- Branch: main
- Active Project: projects/rehearsal_2024_B
- Base commit before this S0 initialization: 0580eb1e873a91fdfa8493fc51b1e8e28bef4558
- Review commit: 由调用 Reviewer 时传入包含本文件及全部 S0 产物、已推送至 origin 的 git rev-parse HEAD 完整 SHA
- Review round: 1
- Prepared at: 2026-09-08 22:10 +08:00
- Freeze rule: Reviewer 必须审核固定完整 SHA，不得改用变化中的分支 HEAD。
- Data visibility: 17 个原始 CSV 依用户要求被 Git 忽略，不存在于远程快照；其本地只读校验元数据和限制见 manifest。

## Deliverables

S0 强制交付物：

- [problem/manifest.md](../problem/manifest.md)
- [work/00_project_brief.md](../work/00_project_brief.md)
- [logs/decisions.md](../logs/decisions.md)
- [logs/experiments.md](../logs/experiments.md)
- [logs/ai_usage.md](../logs/ai_usage.md)
- [CURRENT.md](../CURRENT.md)

适用的仓库与官方材料：

- [Main Agent protocol](../../../.agents/roles/main_agent.md)
- [2024 official materials index](../../../competition/2024/README.md)
- [2024 rules and timeline](../../../competition/2024/rules/2024_rules_and_timeline.md)
- [2024 submission checklist](../../../competition/2024/submission/2024_submission_checklist.md)
- [environment README](../../../environment/README.md)

活动项目唯一性证据：

- rehearsal_2024_C/CURRENT.md 已标记 INACTIVE / PAUSED；
- rehearsal_2024_B/CURRENT.md 是唯一 ACTIVE_PROJECT 声明。

## Verification Commands

环境冒烟：

~~~powershell
conda run -n math_modeling python -c "import sys, numpy, pandas, scipy, sklearn, matplotlib, openpyxl, xlrd, fitz, docx, cv2, bibtexparser, jsonschema, yaml, dotenv, requests, conda_lock; print('smoke=PASS'); print(sys.version)"
~~~

本地输入存在性与可解析性：

~~~powershell
$root = 'projects/rehearsal_2024_B/problem/data'
$files = @(Get-ChildItem -LiteralPath $root -Filter '*.csv' -File)
if ($files.Count -ne 17) { throw "Expected 17 CSV files, found $($files.Count)" }

conda run --no-capture-output -n math_modeling python -c "from pathlib import Path; import pandas as pd; p=Path(r'projects/rehearsal_2024_B/problem/data'); fs=sorted(p.glob('*.csv')); assert len(fs)==17; frames=[pd.read_csv(f, low_memory=False) for f in fs]; assert sum(len(x) for f,x in zip(fs,frames) if f.name.startswith('training_'))==1252; assert sum(len(x) for f,x in zip(fs,frames) if f.name.startswith('test_'))==336; print('inputs=PASS')"
~~~

原件哈希、忽略规则和活动项目：

~~~powershell
Get-FileHash -Algorithm SHA256 projects/rehearsal_2024_B/problem/WLAN组网中网络吞吐量建模.docx
Get-ChildItem projects/rehearsal_2024_B/problem/data/*.csv | Get-FileHash -Algorithm SHA256
git check-ignore -v -- projects/rehearsal_2024_B/problem/data/test_set_1_2ap.csv
rg -n -S 'ACTIVE_PROJECT：projects/' projects/*/CURRENT.md
git status --short
git rev-parse HEAD
~~~

S0 已实际执行上述等价的只读检查；环境输出 smoke=PASS，输入输出见 logs/experiments.md 和 problem/manifest.md。

## Main Claims

1. 用户已明确将唯一 ACTIVE_PROJECT 切换为 projects/rehearsal_2024_B；原 C 项目仅暂停并保留既有成果。
2. 本机题目确认为 2024 年 B 题《WLAN组网中网络吞吐量建模》；DOCX 标题、三问、数据说明和附录可读取。
3. 本机共有 13 个训练 CSV 和题目点名的 4 个测试 CSV；17/17 均能解析，逐文件大小和 SHA-256 已固定到 manifest。
4. 已知的两行错位、全空 RSSI 列、NSS=0 和 schema 差异均已显式登记；S0 没有覆写或静默清洗原件。
5. 2024 年官方邀请函、论文格式规范、提交手册和模板已经读取并把关键约束迁入项目简报。
6. math_modeling 环境当前机器实测可用；Python 3.11.11 和核心依赖完整冒烟通过，按 8 核 / 16 线程 CPU、13.8 GiB RAM、无已验证 GPU 规划。
7. 六个 S0 强制交付物已建立；当前状态保持 PENDING REVIEW，未进入 S1。

## Known Limitations

1. 17 个 CSV 按用户要求不上传远程；Reviewer 无法从远程快照重新读取原始行，只能审核 manifest、命令、日志和风险边界。
2. 当前没有官方数据压缩包总哈希、稳定下载 URL 或发布方逐文件哈希，不能证明本地文件与官方包逐字节一致。
3. 本轮仅完成 S0 基础结构核验，未完成 S1 的逐字段缺失/异常/单位/泄漏审计。
4. environment.yml 尚未做全新环境 clean rebuild，仓库级 verify_environment.py 仍未实现；当前机器实际冒烟已通过。
5. 团队成员姓名和实际分工尚未提供，目前只记录功能角色。
6. 数据来源的授权获取与离线备份路径需由用户/团队维护，manifest 不替代原始数据备份。

## Unresolved Risks

1. training_set_2ap_loc2_nav82.csv 的两个错位记录必须在 S1 形成可复现隔离规则。
2. training_set_3ap_loc30_nav86.csv 的三个全空 AP0 RSSI 列需要缺失机制判断。
3. 三条 nss=0、num_ppdu/num_ampdu 口径及重名输出列需要在 S1 建立 schema 合同。
4. 多 AP 行共享 test_id 场景，后续必须按 test_id/场景分组验证，避免按行随机切分泄漏。
5. 四个官方测试集没有可用于内部选模的 Ground Truth，必须保持封存，直到模型完全冻结后再生成正式预测。

## Requested Verdict

PASS / REVISE / BLOCK。

Main Agent 请求 Reviewer 对调用时提供的固定远程完整 SHA 进行 G0 Round 1 独立审核。只有 G0 PASS 或用户明确书面批准后，项目才可由 S0 进入 S1；审核结论应新增到 reviews/gate_0_review.md，Main Agent 不得自行写入或修改该文件。