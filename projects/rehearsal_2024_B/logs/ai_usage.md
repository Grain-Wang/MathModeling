# AI Usage Log

| Time (Asia/Shanghai) | Tool / Model | User | Task | Main input / prompt | Output use | Adopted | Human verification |
|---|---|---|---|---|---|---|---|
| 2026-09-08 22:10 | OpenAI Codex | 仓库维护者 | 审查 B 项目可开题性并按仓库协议完成 S0 初始化 | 用户要求检查项目完备性，随后要求按建议依次完成至进入 G0 审查；输入包括 Main Agent/Guide、题目 DOCX、17 个 CSV、2024 官方资料和 C 项目已审核结构 | 切换 ACTIVE_PROJECT、整理原始数据路径、建立 manifest/项目简报/日志/CURRENT/G0 submission，并生成只读验证证据 | Yes | 文件数量、SHA-256、DOCX 三问、CSV 行列/标签边界、环境版本和 Git 状态均由本机命令复核；数据异常不在 S0 擅自修复，待 Reviewer 与 S1 决策 |
| 2026-09-08T22:48:49+08:00 | OpenAI Codex | 仓库维护者 | 拉取 G0 审核并启动 S1 | 用户要求 pull 远程 G0 结果后继续；输入为 G0 review、题目约束、manifest 与本地 17 个 CSV | 接受 G0 PASS，建立恢复说明和 S1 审计器，冻结 A01-A04、泄漏和验证边界 | Yes | py_compile、17 文件全量大小/SHA-256、Git ignore/status 均由本机复核；正式审计将在干净实现 commit 上运行 |
| 2026-09-08T23:14:11+08:00 | OpenAI Codex | 仓库维护者 | 完成 S1 题意拆解、数据审计与 G1 审核包 | 题面、17 个本地 CSV、G0 review、manifest、仓库指南和正式审计 JSON | 形成三份 work 文档、A01-A06 合同、测试封存/OOF/分组验证边界、G1 submission 与 CURRENT | Yes | 正式审计在干净 f4b8b9f 上运行；输入前后哈希、组完整性、测试摘要为空及文档一致性由本机命令复核；未拟合模型或生成测试预测 |
