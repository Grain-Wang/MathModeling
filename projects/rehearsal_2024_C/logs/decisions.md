# Decision Log

本日志记录会影响题意、数据、方法、验证和交付的决策。状态使用 `ACTIVE`、`SUPERSEDED` 或 `REVERSED`。

| Time (Asia/Shanghai) | ID | Stage | Decision | Rationale and evidence | Impact | Status |
|---|---|---|---|---|---|---|
| 2026-09-04 21:35 | D0001 | S0 | 唯一 ACTIVE_PROJECT 确定为 `projects/rehearsal_2024_C` | 用户在当前会话明确指定；该项目具备 C 题正文和附件一至四 | 后续成果只能写入本项目；其他项目保持非活动状态 | ACTIVE |
| 2026-09-04 21:35 | D0002 | S0 | 采用 `competition/2024/` 归档的第二十一届官方材料 | 原件来自中国研究生创新实践系列大赛官方平台，已记录大小和 SHA-256 | 格式、命名、时间线和提交检查以 2024 原件为准 | ACTIVE |
| 2026-09-04 21:35 | D0003 | S0 | 使用现有 `math_modeling` Conda 环境，S0 不安装新包 | Python 3.11.11 和核心数据建模包导入测试通过 | S1 可直接数据审计；新增依赖须经模型需求论证 | ACTIVE |
| 2026-09-04 21:35 | D0004 | S0 | 四个 XLSX 暂留 `src/`，但按原始只读附件管理 | 文件较大且当前 `.gitignore` 精确匹配该位置；初始化时移动会引入不必要风险 | 派生文件写入 `results/raw/`；S1 前评估受控迁移 | ACTIVE |
| 2026-09-04 21:35 | D0005 | S0 | 在 G0 对冻结 commit 给出 PASS 前不进入 S1 | Main/Reviewer 协议要求 Gate 前置 | 当前仅允许完成初始化、验证和审核准备 | ACTIVE |
| 2026-09-07 | D0006 | S1 | 接受 Reviewer 对固定快照 `c99ca0f7f7a238fac501836cd06dfd0b6aaabebe` 的 G0 PASS，并进入 S1 | `reviews/gate_0_review.md` 无 Critical/Major，明确授权 S0 → S1 | 当前工作限定为题意拆解、只读数据审计和需求追踪；下一 Gate 为 G1 | ACTIVE |

## Pending Decisions

1. 团队成员姓名及数据、建模、代码、绘图、写作责任人。
2. 原始 XLSX 是否迁移到 `problem/data/`，以及相应 `.gitignore` 调整方式。
3. S1 数据读取缓存格式与位置。
