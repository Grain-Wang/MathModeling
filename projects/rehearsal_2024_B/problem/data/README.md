# Local Raw Data Recovery

本目录用于存放 rehearsal_2024_B 的 17 个原始 CSV。CSV 按用户要求由仓库根目录的 /projects/**/*.csv 规则忽略，不上传 Git 或远程仓库；本 README、problem/manifest.md 和审计代码必须被跟踪。

## Authorization and Source

- 数据必须由参赛团队从有权使用的原始赛题包或团队受控离线备份取得。
- 当前本地副本来源位置、官方下载 URL 和官方压缩包总哈希尚未记录。
- 在补齐来源前，只能声明“本地文件与 S0 manifest 一致”，不能声明“与官方发布包逐字节一致”。
- 不得将受限 CSV 上传到公共仓库、聊天附件或未经授权的网盘。

## Expected Files

1. test_set_1_2ap.csv
2. test_set_1_3ap.csv
3. test_set_2_2ap.csv
4. test_set_2_3ap.csv
5. training_set_2ap_loc0_nav82.csv
6. training_set_2ap_loc0_nav86.csv
7. training_set_2ap_loc1_nav82.csv
8. training_set_2ap_loc1_nav86.csv
9. training_set_2ap_loc2_nav82.csv
10. training_set_3ap_loc30_nav82.csv
11. training_set_3ap_loc30_nav86.csv
12. training_set_3ap_loc31_nav82.csv
13. training_set_3ap_loc31_nav86.csv
14. training_set_3ap_loc32_nav82.csv
15. training_set_3ap_loc32_nav86.csv
16. training_set_3ap_loc33_nav82.csv
17. training_set_3ap_loc33_nav88.csv

逐文件大小和 SHA-256 的唯一人工可读清单见 [../manifest.md](../manifest.md)。

## Restore Procedure

1. 从授权来源取得上述 17 个文件，不重命名、不另存和不编辑。
2. 放入 projects/rehearsal_2024_B/problem/data/。
3. 确认文件总数恰好为 17，且没有额外 CSV。
4. 在仓库根目录运行：

~~~powershell
conda run --no-capture-output -n math_modeling python projects/rehearsal_2024_B/src/s1_data_audit.py --verify-only
~~~

5. 只有输出 input_verification=PASS 后才能开始 S1 审计或后续实验。
6. 如任一文件名、大小或 SHA-256 不匹配，立即停止；不得自动“修复”、拼接或覆盖 manifest。
7. 审计完成后脚本会再次复核哈希，证明原件未被改写。

## Offline Backup Responsibility

- 责任角色：参赛团队的数据负责人；具体姓名待补。
- 至少保留一份不在仓库内、只读或受权限控制的离线备份。
- 备份恢复演练和授权来源需在 G1 前尽量补充；负责人姓名缺失目前为 G0 Reviewer 认可的非阻断 Minor。

## Immutability

problem/data/ 只放原始 CSV。清洗表、规范字段、特征、预测和审计派生物必须写入 results/raw/ 或后续受控目录，禁止覆盖本目录文件。