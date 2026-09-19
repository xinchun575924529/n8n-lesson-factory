# 05 · 排障图谱：10 坑照妖镜 + 怪癖大赏

## 模板本体 4 坑（必修）
| # | 现象 | 根因 | 药方 | 验证 |
|---|---|---|---|---|
| 1 | 甲的悄悄话乙能问到 | memory `sessionKey=angie_session_default` 硬编码 | 改 fromInput + from.id | L2A ✅（故意复现后修复） |
| 2 | 白名单逻辑一动就炸 | AllowList 存 string，全靠 If1 `looseTypeValidation=true` 侥幸放行 | 存 number，不依赖开关 | 对照流实测：loose ✅ 放行 / strict ❌ 抛 `Wrong type` 错 |
| 3 | 自建工具跑了但答案瞎编 | toolCode typeVersion=1 与 Agent v3 不兼容（模板本体不含此节点） | 一律升 1.3 | L2A ✅（3 工具 obs 全命中） |
| 4 | 促销邮件照列 | 提示词太软 | STRICTLY EXCLUDE 死约束 | L2B warn → L2C ✅ |

## 环境/部署 6 怪癖（⚪，非模板缺陷但必踩）
| # | 怪癖 | 拆招 |
|---|---|---|
| 5 | 重启后 `n8n` 命令 MODULE_NOT_FOUND（tool_cache 残影） | 用全路径 `C:\Users\Administrator\AppData\Roaming\npm\n8n.cmd` |
| 6 | `publish:workflow` 第一次"假发布"，webhook 404 | publish ×2 或重启 n8n 计划任务 |
| 7 | 重启后立刻测 webhook 得 503 Database is not ready | healthz 200 后再等 20-30s |
| 8 | webhook 节点改名后路由消失 | 节点名必须字面 `Webhook`；responseMode=`lastNode`；parameters 里**别留 `options:{}`** |
| 9 | `localhost:8766` 连不通自托管 STT | IPv6 优先：改写 `127.0.0.1`；端口避开 8765/5678/10088 |
| 10 | readWriteFile 拒读本地文件 | 走 Code 节点 `fs.readFileSync`（需 `NODE_FUNCTION_ALLOW_BUILTIN` 含 fs） |

## 怪癖大赏（笑了就记住）
- 🥇 **"publish 已成功"但 404**：路由注册和版本登记是两件事，CLI 不告诉你。
- 🥈 **"白名单配置正确"但动一下就炸**：字符串和数字之间隔着一条靠"宽松校验"硬跨过去的鸿沟。
- 🥉 **"工具都执行了"但 Agent 说"我不知道"**：typeVersion 差 0.3，obs 蒸发。

## 排障 SOP（照做省一晚）
1. **先分清是路由没到还是逻辑没到**：sqlite `webhook_entity` 有行 + stdout 有 `Activated workflow` 才谈逻辑。
2. **执行详情页三看**：输入 json、错误堆栈、（Agent 流）Tool 节点的观测字段是否为空。
3. **二跑对照**：改一处立刻双跑，断言数对不上的那一刻就是你引入新 bug 的那一刻。
4. **把测试断言写在最终输出上**（见 docs/03 第 4 条观察），别赌工具调用顺序。