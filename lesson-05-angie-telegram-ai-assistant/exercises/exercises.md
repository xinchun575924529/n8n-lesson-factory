# 练习与参考答案（2462 · 共 6 题）

> 做题顺序建议按讲次推进。答案附在每题之后（折叠前先自己想）。

---

## 练习 1（对应 00 讲）：实拉照妖

**题目**：用 `https://api.n8n.io/api/workflows/templates/2462` 拉取模板，数出总节点数，并把它们分成「主轴」与「AI 侧翼」两组，各有哪些？

**参考答案**：
- 实拉 **15 节点**：telegramTrigger×1、set×2、if×2、telegram×2、openAi(STT)×1、agent×1、lmChatOpenAi×1、memoryBufferWindow×1、baserowTool×2、googleCalendarTool×1、gmailTool×1
- **主轴（9 个）**：Listen → AllowList → If1 → Voice or Text → If → Get Voice File → Speech to Text → Agent → Telegram 回复
- **AI 侧翼（6 个）**：OpenAI Chat Model / Simple Memory / Tasks / Contacts / Google Calendar / Gmail——靠 `ai_languageModel` / `ai_memory` / `ai_tool` 连线挂在 Agent 上，**不占主流程执行序列**
- 教训：**画 mock / 换 LLM 时别把侧翼当主线节点数**；95% 的 TG 助理模板都是这根轴的变形

## 练习 2（对应 01 讲）：亲手复现白名单地雷

**题目**：搭两条对照工作流验证「字符串 vs 数字」：Code 节点输出 `{from_id:114514, allow:"114514"}` → If 节点（number equals，`leftValue=from_id`、`rightValue=allow`），分别开/关 `looseTypeValidation`，各观察什么？

**参考答案**：
| 配置 | 结果 | 证据 |
|---|---|---|
| `looseTypeValidation: true`（模板现状） | ✅ 放行 | 走到 true 分支 |
| `looseTypeValidation: false` | ❌ **整条执行报错** | `NodeOperationError: Wrong type: '114514' is a string but was expecting a number` |
- 关键认知：关掉宽松校验**不是静默拦截，是节点直接抛错**，用户连「我没权限」都收不到
- 修复军规：**AllowList 存 number**（字段类型选 Number / 值不带引号），从此不依赖任何开关
- 陷阱操作：在 UI 里重选字段、升级节点版本、复制到新工作流——都会把这个开关重置成「隐形依赖」

## 练习 3（对应 02 讲）：零成本 STT 替身

**题目**：把模板的 OpenAI Whisper 换成自托管 Vosk，需要动哪几处？为什么 Speech to Text 节点的凭证**不用改形态**？

**参考答案**：
- 动 3 处：① 起 `free-stack.py`（监听 `127.0.0.1:8766`，加载 vosk-model-small-cn-0.22）② 凭证 BASE_URL 指向本地 ③ 测试语音用 edge-tts 产出（无需真人录音）
- 不用改形态的理由：free-stack.py 提供 **OpenAI 兼容 `/v1/audio/transcriptions`**，节点还以为自己在调 OpenAI——**替身链的设计目标就是"换引擎零删改"**
- 环境坑三连：`localhost` 在 n8n 里是 IPv6 优先（改 `127.0.0.1`）；端口 8765 被 kailoader 抢（用 8766）；`readWriteFile` 拒读本地文件（改 Code 节点 `fs.readFileSync`）

## 练习 4（对应 03 讲）：两个高危坑修复

**题目**：写出 Simple Memory 的修复配置（让"每个 TG 用户一份自己的记忆"），并说明 `toolCode` 为什么必须升 typeVersion=1.3。

**参考答案**：
```
memoryBufferWindow.Session ID Type = "Define below"（fromInput）
sessionKey = {{ $('Listen for incoming events').item.json.message.from.id }}
```
- 原配置 `sessionKey=angie_session_default`（常量）⇒ **所有用户共享一份记忆**，隐私级灾难（L2A 故意复现坐实）
- `toolCode`：typeVersion=1 与 Agent v3 输出契约不一致——工具确实执行、HTTP 200，但 Agent 等不到观测值，**只好幻觉自答**；升 1.3 后 L2A 三工具（calculator / google_calendar / task_list）obs 全部命中
- 注意：**模板本体 15 节点里没有 toolCode**——这是你自己画工具时必撞的坑

## 练习 5（对应 04 讲）：提示词三层试验

**题目**：模板系统提示词里的 `filter out promotional emails` 为什么管不住 DeepSeek？写出修复版并说明它属于哪一层加固。

**参考答案**：
- 原因：祈使句 + 无后果描述 = 模型眼里的"建议"；L2B-S5 实测促销邮件照样被列进摘要（还贴心标注 "some promotional offers"）
- 修复（L3 层死约束，L2C 复测有效 ✅）：
```
STRICTLY EXCLUDE promotional, marketing, or advertising emails from any summary —
do not list them, do not mention they exist, not even to say they were skipped.
```
- 三层试验法：L1 句法（措辞）→ L2 结构（清单）→ L3 死约束（STRICTLY/NEVER/ALWAYS，拿对抗样本验）
- 口诀：多数"模型不听话"是提示词没到 L3 层，别急着怪模型

## 练习 6（对应 05 讲）：webhook 假发布排障

**题目**：工作流 publish 显示成功，但 `POST /webhook/xxx` 返回 404 `Cannot POST`。列出排障顺序，并说明每一步各自排除什么。

**参考答案**：
1. **先分清"路由没到"还是"逻辑没到"**：sqlite 查 `webhook_entity` 有行 ≠ 路由生效；stdout 出现 `Activated workflow` 才是金标准
2. **检查节点三件套**：节点名必须字面 `Webhook` / `responseMode=lastNode` / parameters 里**不留 `options:{}`**——缺一路由注册不上
3. **publish ×2 或重启 n8n**：`publish:workflow` 第一次只登记版本，路由要重启计划任务才挂上
4. **healthz 200 后等 20-30s 再测**：刚重启完 POST 会拿 503 "Database is not ready"（不是路径错）
- 损失挡位：不查清路由层就改逻辑 = 白忙一晚上

---

> **附加挑战**：把 docs/05 的 10 坑排障图谱整理成你团队的 n8n Code Review checklist（5~8 条），落地到工程规范仓库。