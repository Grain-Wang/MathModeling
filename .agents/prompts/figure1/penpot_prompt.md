# 任务：将现有 Figma MCP 工作流完整迁移到 Penpot MCP，并使用 Penpot 美化图 1

你现在执行一项端到端迁移任务：

1. 检查当前 Codex MCP 配置；
2. 备份现有配置；
3. 安装并配置本地 Penpot MCP；
4. 验证 Penpot MCP 可读、可写；
5. 验证成功后再移除或禁用 Figma MCP；
6. 更新项目中与图 1 有关的 Figma 工作流文档；
7. 使用 Penpot MCP 重建和美化图 1；
8. 导出 SVG、PDF 和 PNG；
9. 不覆盖原始 Draw.io 和 SVG 文件。

当前仓库根目录是当前工作目录。

主要输入文件：

- projects/rehearsal_2024_B/figures/fig01_overall_workflow.drawio
- projects/rehearsal_2024_B/figures/fig01_overall_workflow.svg
- projects/rehearsal_2024_B/results/verified/figure_data/fig01_overall_workflow.json
- projects/rehearsal_2024_B/work/10_result_freeze.md
- projects/rehearsal_2024_B/results/verified/result_registry.md

---

## 一、执行原则

必须遵守：

1. 先备份，后修改。
2. 在 Penpot MCP 完成读写验证以前，不得删除 Figma MCP。
3. 不得删除已有 Figma 文件、Figma 页面或历史导出物。
4. 不得打印、记录或提交任何 MCP 密钥、访问令牌或 OAuth 信息。
5. 优先使用本地 Penpot MCP，不使用需要额外额度的 Figma 工作流。
6. 不要直接假设 Codex MCP 配置文件路径，先使用命令定位实际配置。
7. 不要擅自使用 sudo；只有确实缺少系统依赖时才报告。
8. 不改变图 1 的任何事实、数字、模型名称和依赖关系。
9. 每一步都要实际执行和验证，不要只输出操作建议。
10. 遇到必须由用户在浏览器中完成的操作时，只暂停一次，并给出最少的明确步骤。

---

## 二、阶段 A：检查当前环境

执行并记录：

- pwd
- git status --short
- node --version
- npm --version
- nvm --version
- codex --version
- codex mcp --help
- codex mcp list，或当前版本等价命令

检查：

1. 当前是否已经配置 Figma MCP；
2. Figma MCP 的配置名称；
3. Codex 当前使用的实际配置文件位置；
4. 是否已经存在名为 penpot 的 MCP；
5. 当前 Node.js 是否可用于 Penpot MCP；
6. 端口 4400 和 4401 是否已被占用。

同时在当前仓库中搜索，但排除 `.git`、`node_modules` 和二进制文件：

- Figma
- figma
- FIGMA
- figame
- use_figma
- FIGMA_SELECTION_URL
- FIGMA_POLISHED_FRAME_URL

只记录与本项目科研绘图工作流有关的引用，不要修改无关内容。

把检查结果写入：

projects/rehearsal_2024_B/figures/penpot_migration_log.md

---

## 三、阶段 B：备份 MCP 配置

找到 Codex 实际 MCP 配置文件后：

1. 创建带时间戳的备份；
2. 保留文件权限；
3. 在迁移日志中记录备份路径；
4. 不要在日志中写入任何令牌内容。

如果配置由多个文件组成，备份所有相关文件。

不要在此阶段移除 Figma MCP。

---

## 四、阶段 C：准备兼容的 Node.js 环境

Penpot MCP 优先使用 Node.js 22。

如果当前 Node.js 不是 20 或 22：

1. 检查 nvm 是否可用；
2. 使用 nvm 安装 Node.js 22；
3. 仅让 Penpot MCP 服务使用 Node.js 22；
4. 不要永久修改当前项目默认 Node.js 版本；
5. 不要卸载现有 Node.js 24。

验证：

- node --version
- npx --version

---

## 五、阶段 D：启动本地 Penpot MCP

使用官方本地方式启动：

npx -y @penpot/mcp@stable

默认服务应为：

- Penpot 插件服务：http://localhost:4400
- 插件清单：http://localhost:4400/manifest.json
- MCP 服务：http://localhost:4401/mcp

不要简单地在当前前台运行后阻塞全部工作。

请采用当前环境中可靠的后台方式，例如：

- tmux；
- 或 nohup；
- 或 setsid；
- 或创建可重复运行的启动脚本。

创建：

tools/penpot_mcp/start_penpot_mcp.sh
tools/penpot_mcp/stop_penpot_mcp.sh
tools/penpot_mcp/status_penpot_mcp.sh
tools/penpot_mcp/README.md

要求：

1. 启动脚本使用 Node.js 22；
2. PID 和日志放在用户缓存目录或 `/tmp`，不要提交运行时 PID；
3. 重复启动时能够识别已有服务；
4. 停止脚本只停止 Penpot MCP 自己的进程；
5. 状态脚本检查进程和 4400、4401 端口；
6. 日志中不得包含敏感凭据。

启动后验证：

- 4400 端口处于监听状态；
- 4401 端口处于监听状态；
- `http://localhost:4400/manifest.json` 可访问；
- MCP 端点有响应；
- 服务日志没有立即退出或持续报错。

如果 Chromium 浏览器阻止 HTTPS 页面访问 localhost，不要改变系统安全设置；在日志中建议改用 Firefox，或让用户显式允许本地网络访问。

---

## 六、阶段 E：把 Penpot MCP 添加到 Codex

先检查当前 Codex CLI 支持的 MCP 命令，不要猜测语法。

优先使用当前 Codex 版本原生的 MCP 添加命令，把服务器命名为：

penpot

服务器地址：

http://localhost:4401/mcp

如果当前 Codex 原生命令不支持 HTTP MCP 添加，再使用官方推荐的通用方式：

npx -y add-mcp -g -n penpot http://localhost:4401/mcp

完成后验证：

- Penpot 出现在 MCP 服务列表中；
- 地址指向 localhost:4401/mcp；
- 没有重复的 penpot 配置；
- Figma MCP 此时仍保留；
- 配置文件语法有效。

如果当前 Codex 会话不能动态加载新 MCP：

1. 把当前阶段写入：
   projects/rehearsal_2024_B/figures/penpot_migration_checkpoint.md
2. 明确写出下一步应该从哪个阶段继续；
3. 只要求用户重启一次 Codex；
4. 重启后读取 checkpoint，禁止重复安装和重复修改配置。

---

## 七、阶段 F：唯一一次人工浏览器检查点

完成服务器和 Codex 配置后，暂停并只向用户输出下面这些操作：

1. 打开或登录 https://design.penpot.app
2. 创建或打开一个设计文件，建议命名为：
   rehearsal_2024_B_figures
3. 在 Penpot 中选择：
   Plugins → Load from URL
4. 输入：
   http://localhost:4400/manifest.json
5. 运行插件并点击：
   Connect to MCP server
6. 保持 Penpot 标签页、目标文件和插件窗口打开
7. 回复：
   Penpot 已连接

在用户回复“Penpot 已连接”以前：

- 不移除 Figma MCP；
- 不尝试写入 Penpot；
- 不重复安装；
- 不要求用户执行终端命令。

---

## 八、阶段 G：验证 Penpot MCP 读写能力

用户回复“Penpot 已连接”后继续。

先执行只读验证：

1. 列出当前 Penpot 文件中的页面；
2. 获取当前聚焦页面的信息；
3. 列出当前页面中的顶层对象；
4. 获取页面尺寸或画布信息；
5. 不进行任何修改。

然后执行一个可逆的轻量写入测试：

1. 创建一个临时页面：
   99_MCP_Test
2. 创建一个小型测试矩形和一段测试文字；
3. 读取回来确认对象存在；
4. 删除整个 99_MCP_Test 页面。

只有当完整的“创建—读取—删除”测试成功后，才认定 Penpot MCP 可写。

如果写入失败：

- 保留 Figma MCP；
- 不修改项目中的 Figma 工作流文档；
- 记录错误；
- 尝试重新连接插件一次；
- 再失败则停止，不破坏旧配置。

---

## 九、阶段 H：成功后移除 Figma MCP

只有 Penpot MCP 的读写验证成功后，才执行：

1. 使用 Codex 当前版本支持的命令移除或禁用 Figma MCP；
2. 不撤销用户的 Figma 账号授权；
3. 不删除任何 Figma 云端文件；
4. 不删除已有 Figma 导出图；
5. 不修改与其他项目相关的 Figma 配置。

完成后验证：

- `penpot` MCP 存在；
- Figma MCP 不再处于 Codex 活跃 MCP 列表；
- Codex MCP 配置语法有效；
- 原始备份仍存在。

在迁移日志中记录：

- 删除或禁用的 MCP 名称；
- Penpot MCP 地址；
- 验证时间；
- 不包含任何凭据。

---

## 十、阶段 I：更新项目中的 Figma 工作流引用

仅更新与本项目图 1 美化流程有关的文件。

如果存在：

- fig01_figma_beautification_spec.md
- fig01_figma_delivery.md
- 含 Figma MCP 操作说明的图 1 文档

则：

1. 不直接删除旧文件；
2. 保留旧文件作为历史记录；
3. 创建对应的 Penpot 版本：

projects/rehearsal_2024_B/figures/fig01_penpot_beautification_spec.md
projects/rehearsal_2024_B/figures/fig01_penpot_delivery.md

4. 将术语准确替换：
   - Figma File → Penpot File
   - Frame → Board
   - Figma MCP → Penpot MCP
   - use_figma → Penpot MCP 工具
   - Figma styles → Penpot styles/tokens
5. 移除 Figma 链接占位符；
6. 不修改科研事实和图内容要求。

不要在整个仓库中进行不加判断的全局字符串替换。

---

## 十一、阶段 J：在 Penpot 中重建图 1

读取并交叉核对：

- fig01_overall_workflow.drawio
- fig01_overall_workflow.svg
- fig01_overall_workflow.json
- 10_result_freeze.md
- result_registry.md

在 Penpot 当前文件中创建两个页面：

1. 00_Drawio_Reference
2. 01_Penpot_Polished

如果页面已存在，不重复创建，先检查其中内容。

### 参考页面

在 `00_Drawio_Reference` 中：

- 尝试使用本地 Penpot MCP 的导入能力导入：
  projects/rehearsal_2024_B/figures/fig01_overall_workflow.svg
- 导入对象命名为：
  fig01_drawio_reference
- 锁定参考对象；
- 不把该对象作为最终交付图。

如果 Penpot MCP 不能直接导入 SVG：

- 不要求用户重新画；
- 直接读取本地 SVG/XML 和 Draw.io 文件；
- 以其结构为依据重建；
- 在迁移日志中说明未导入参考图的原因。

### 美化页面

在 `01_Penpot_Polished` 中创建 Board：

fig01_overall_workflow_polished

建议尺寸：

- 横向；
- 约 1600 × 1000 px；
- 根据内容可适当调整；
- 四周保留统一安全边距。

不要将整张 SVG 作为最终图。

必须用 Penpot 原生对象重建：

- Board；
- Text；
- Rectangle；
- Group；
- Line；
- Arrow；
- 颜色 token；
- 文字样式；
- 可复用卡片组件；
- 必要的 Flex Layout 或 Grid Layout。

对象和图层必须使用语义化名称。

---

## 十二、图 1 的结构

采用：

横向五阶段 + 上下双区域 + 三问分支 + 冻结闸门

上方：

训练侧：开发、验证与冻结

下方：

官方测试侧：封存、释放与推理

主要阶段：

1. 输入与数据边界；
2. 数据审计；
3. 特征处理和训练侧验证；
4. Q1、Q2、Q3 建模及真实依赖；
5. G4 冻结、S5 释放和最终推理输出。

必须明确表现：

- 13 个训练文件；
- 4 个官方测试文件；
- 官方测试在冻结前保持封存；
- A01 隔离两个不完整组、共 2 行；
- 可用训练数据为 1,250 个 AP 行、482 个完整组；
- 共享机制特征和 RSSI 特征；
- 需要拟合的预处理只在训练折内拟合；
- 按 `source_file + test_id` 分组；
- 主验证为 3 次重复 × 5 折；
- 另有 13 次 LOSO；
- 官方测试不参与模型选择。

Q1：

- Q1-B1 Ridge；
- 输出限制在 `[0, test_dur]` 内的时长预测。

Q2：

- Q2-B1A LogisticRegression；
- 输出固定 17 类顺序概率；
- 最终 Q2 不使用 Q1 预测。

Q3：

- Q3-M1-HGB-UNIFIED；
- 全量部署配置是物理基准加残差 HGB；
- 配置名为 Q3-physics_residual-C3；
- 输出非负的每 AP 吞吐量。

Q1 与 Q3：

- 训练阶段：
  登记过的 Q1 折外预测 OOF → Q3；
- 部署阶段：
  在全部合格训练行上拟合的 Q1 模型 → Q3 推理；
- 两种依赖必须使用不同线型或明确标签；
- Q2 不得与 Q1 建立依赖。

系统吞吐量：

- 同一完整组内 AP 预测值严格求和；
- 得到系统吞吐量；
- 不存在独立的系统吞吐量预测头。

冻结与发布：

- G4 冻结以后；
- 才能进行唯一一次 S5 官方测试释放；
- 官方测试无真实标签；
- 不得填写官方测试准确率或误差；
- 不得画官方测试结果返回选模流程的箭头。

---

## 十三、视觉规范

风格：

- 正式学术论文；
- 简洁；
- 低饱和度；
- 接近白色背景；
- 无渐变；
- 无重阴影；
- 无玻璃拟态；
- 无卡通图标；
- 无无意义装饰；
- 黑白打印时仍可辨认。

颜色 token：

- page/background：接近白色；
- lane/training：浅蓝灰；
- lane/test：浅中性灰；
- q1/base：低饱和蓝；
- q2/base：低饱和紫；
- q3/base：低饱和绿；
- freeze/base：低饱和橙；
- text/primary：深灰；
- text/secondary：中灰；
- border/default：灰蓝；
- annotation/background：很浅的中性灰。

箭头语义：

- 深灰实线：主流程；
- 蓝色虚线：Q1 OOF → Q3 训练；
- 蓝色实线：全量 Q1 → Q3 部署；
- 灰色虚线边界：官方测试封存；
- G4 使用橙色竖向边界或闸门；
- 箭头必须避开文字和节点；
- 禁止无意义交叉线。

文字：

- 检查 Penpot 中实际可用的中文无衬线字体；
- 优先 Noto Sans SC、Noto Sans CJK SC 或思源黑体；
- 若不可用，选择可完整显示中文的等价字体；
- 不得出现缺字、方框或字体回退混乱；
- 标题、阶段标题、卡片标题、正文、注释只使用有限层级。

布局：

- 使用统一栅格；
- 节点尺寸一致；
- 内边距一致；
- 圆角一致；
- Q1、Q2、Q3 卡片视觉权重接近；
- G4 醒目但不能压过主要方法内容；
- 底部设置精简的限制说明和证据标签。

证据标签：

- E-FREEZE-001
- E-Q3-CONFIG-001
- E-RELEASE-001

---

## 十四、禁止性要求

禁止：

1. 更改任何数字；
2. 更改冻结模型名称；
3. 更改 Q1、Q2、Q3 的真实依赖；
4. 把 Q2 画成依赖 Q1；
5. 增加不存在的因果关系；
6. 把官方测试画成普通验证集；
7. 画官方测试输出返回训练或选模的箭头；
8. 把 Q3-M1-HGB-UNIFIED 的嵌套管线验证表现写成固定 residual-C3 配置独立取得的成绩；
9. 增加神经网络、云服务、GPU 等无关图标；
10. 直接把原 SVG 作为最终图；
11. 只输出一张不可编辑位图；
12. 覆盖原始 `.drawio` 和 `.svg`。

---

## 十五、质量检查

第一版完成后，至少执行两轮：

检查 → 修正 → 再检查

每轮检查：

1. 是否有文字截断；
2. 是否有文字重叠；
3. 是否有对象超出 Board；
4. 是否有箭头穿过节点；
5. 是否有无意义的交叉线；
6. Q1 OOF 和部署 Q1 两种依赖是否一眼可区分；
7. Q2 是否保持独立；
8. Q3 AP 求和关系是否清晰；
9. 官方测试封存是否明确；
10. G4 → S5 的时序是否明确；
11. 官方测试无标签说明是否清晰；
12. 缩小到论文整页宽度以后是否可读；
13. 关闭颜色后是否仍可通过线型和标签理解；
14. 所有数字和模型名是否与事实源一致；
15. 证据编号是否准确。

---

## 十六、导出

优先使用 Penpot MCP 本地导出能力，生成：

- projects/rehearsal_2024_B/figures/fig01_overall_workflow_penpot.svg
- projects/rehearsal_2024_B/figures/fig01_overall_workflow_penpot.pdf
- projects/rehearsal_2024_B/figures/fig01_overall_workflow_penpot.png

要求：

- SVG 保持矢量和文字清晰；
- PDF 保持矢量；
- PNG 至少为 2× 分辨率。

如果 Penpot MCP 不能直接输出 PDF：

1. 先导出最终 SVG；
2. 使用本地 Inkscape CLI 将 SVG 转换为 PDF；
3. 不得栅格化；
4. 在交付文档中记录转换命令。

同时创建：

projects/rehearsal_2024_B/figures/fig01_penpot_delivery.md

记录：

- Penpot 文件名称；
- 页面名称；
- Board 名称；
- Board 尺寸；
- 使用字体；
- 颜色 token；
- 箭头语义；
- 与 Draw.io 原版相比的主要改动；
- Penpot MCP 配置方式；
- 导出方式；
- 当前仍需人工确认的事项；
- 原始文件没有被覆盖的确认。

---

## 十七、最终验收

最后执行并报告：

1. Penpot MCP 服务状态；
2. Codex MCP 列表；
3. Figma MCP 是否已安全移除或禁用；
4. Penpot MCP 是否通过读写验证；
5. 生成的输出文件是否存在；
6. 输出文件大小；
7. Git 状态；
8. 修改和新增文件清单；
9. 是否存在未解决错误；
10. 是否有需要用户在 Penpot 中进行的最后人工检查。

不要只告诉我怎么做。实际完成能够自动完成的全部步骤。