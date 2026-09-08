# Decision Log

本日志记录会影响题意、数据、方法、验证和交付的决策。状态使用 ACTIVE、SUPERSEDED 或 REVERSED。

| Time (Asia/Shanghai) | ID | Stage | Decision | Rationale and evidence | Impact | Status |
|---|---|---|---|---|---|---|
| 2026-09-08 22:10 | D0001 | S0 | 唯一 ACTIVE_PROJECT 切换为 projects/rehearsal_2024_B，原 C 项目暂停 | 用户明确要求按计划初始化 B 项目并进入 G0 审查 | 后续赛题成果只写入 B；C 保留既有 S6 状态但不继续执行 | ACTIVE |
| 2026-09-08 22:10 | D0002 | S0 | 采用 competition/2024/ 中归档的第二十一届官方材料 | B 题属于同一届竞赛；本地官方邀请函、格式规范、提交手册和模板均有哈希与来源记录 | 格式、匿名、命名和提交要求以官方原件/网页为准 | ACTIVE |
| 2026-09-08 22:10 | D0003 | S0 | 将 17 个原始 CSV 从 src/ 受控移动至 problem/data/ | 文件协议规定原题和原始数据归入 problem/；移动前后文件数量一致，内容哈希保持不变 | src/ 留给代码；原始 CSV 只读，派生数据不得回写 | ACTIVE |
| 2026-09-08 22:10 | D0004 | S0 | 原始 CSV 继续由 /projects/**/*.csv 忽略，并以 manifest 记录可复核元数据 | 用户明确要求 CSV 不上传远程；所有 17 个数据文件当前均命中忽略规则 | 远程仓库不含原始数据；换机前必须按 manifest 取得并校验数据 | ACTIVE |
| 2026-09-08 22:10 | D0005 | S0 | 使用现有 math_modeling Conda 环境，S0 不安装新依赖 | Python 3.11.11 及核心建模/文档包导入冒烟测试通过 | S1 可直接执行数据审计；新增依赖须由后续模型需求论证 | ACTIVE |
| 2026-09-08 22:10 | D0006 | S0 | S0 不修改已知异常记录，处理规则推迟到 S1 冻结 | 原件应保持不可变；论坛 B 题专家允许剔除两条错位数据，但本项目仍需记录可复现规则 | S1 派生数据中处理，保留原始行号、理由和数量审计 | ACTIVE |
| 2026-09-08 22:10 | D0007 | S0 | 在 G0 对固定 commit 给出 PASS 前不进入 S1 | Main/Reviewer 协议要求阶段门控；Main Agent 不得自行宣布通过 | 当前仅允许完成 S0 验证、提交与审核准备 | ACTIVE |