# AI Usage Log

| Time (Asia/Shanghai) | Tool / Model | User | Task | Main input / prompt | Output use | Adopted | Human verification |
|---|---|---|---|---|---|---|---|
| 2026-09-08 22:10 | OpenAI Codex | 仓库维护者 | 审查 B 项目可开题性并按仓库协议完成 S0 初始化 | 用户要求检查项目完备性，随后要求按建议依次完成至进入 G0 审查；输入包括 Main Agent/Guide、题目 DOCX、17 个 CSV、2024 官方资料和 C 项目已审核结构 | 切换 ACTIVE_PROJECT、整理原始数据路径、建立 manifest/项目简报/日志/CURRENT/G0 submission，并生成只读验证证据 | Yes | 文件数量、SHA-256、DOCX 三问、CSV 行列/标签边界、环境版本和 Git 状态均由本机命令复核；数据异常不在 S0 擅自修复，待 Reviewer 与 S1 决策 |