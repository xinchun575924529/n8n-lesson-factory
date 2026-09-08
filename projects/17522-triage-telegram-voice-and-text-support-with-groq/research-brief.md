# 研发立项报告 · 17522 Triage Telegram voice & text support

- **项目名**：Triage Telegram voice and text support with Groq LLMs and Google Sheets（工作流名：Voice & Text Telegram Support Agent）
- **来源**：n8n 官方模板库 https://n8n.io/workflows/17522/（API 200 活链，2026-09-08 拉取验证）
- **状态**：research（立项报告待审）
- **研究日期**：2026-09-08（Asia/Shanghai）

## 一、用途与输入输出

**用途**：把一个加密货币钱包（CBox）的 Telegram 客服号升级成 AI 分级客服——语音消息先转文字，再统一做意图/情绪/安全风险分类；怒气值高或有安全风险的自动升级人工（并生成语音安抚回复），普通问题由 LLM 按 FAQ 直接作答，全部互动落表留痕。

**输入**：
- Telegram 用户消息（语音 voice / 文本 text / 其他类型）
- FAQ 知识库（写死在 3 个 LLM 节点的 system prompt 里，非外部数据库）

**输出**：
- Telegram 回复（文本 / TTS 语音 wav）
- 升级通知（发回同一 Telegram 群的「人工客服提醒」+ 30 分钟防重复升级锁）
- Google Sheets 三张表留痕：Interactions（互动日志）、Errors（错误日志）、Escalations（升级锁）
- Slack 错误告警频道

**主链路**：Telegram Trigger → 语音? → 下载语音(Groq Whisper 转写) / 文本直取 → LLM 分类(intent/sentiment/security_risk) → Sheets 查升级锁 → 升级? → 锁+通知人工+TTS 语音回复 / 按 intent 三档模型回复(Switch: FAQ 快速模型 / 交易·KYC 中模型 / 安全·交易 大模型 70B) → 记日志

## 二、节点清单（33 节点 = 25 功能 + 8 便签，API 口径 nodeCount=9 是元数据不准）

| 类别 | 节点 |
|---|---|
| 触发/消息 | Voice Message Trigger (telegramTrigger)、Get Voice File、Holding Reply、Notify Human Agent(Telegram account 2)、Send Voice Reply(sendAudio)、Send Reply、Unsupported Message Reply、Fallback Reply |
| 判断/路由 | Has Voice? (if)、Has Text? (if)、Already Escalated? (if)、Escalation Check (if)、Route by Intent (switch, 3 路) |
| LLM/HTTP (全部连 Groq) | Transcribe (whisper-large-v3-turbo)、Classify Intent & Sentiment (llama-3.1-8b-instant)、Fast Model Reply (8b-instant)、Contextual Reply (llama-3.3-70b)、Strong Model Reply (llama-3.3-70b)、Generate Voice Reply TTS (orpheus-v1-english) |
| Code | Fix Audio Filename、Extract Transcript (Voice)、Extract Transcript (Text)、Parse Classification JSON、Evaluate Escalation Lock、Handle API Error、Extract Reply Text、Prepare Log Data |
| Google Sheets | Get row(s) in sheet（查锁）、Set Escalation Lock（写锁）、Log Interaction、Log Error to Sheet |
| Slack | Alert Slack (Error) |
| 错误兜底 | 所有 HTTP/Telegram 下载节点 onError=continueErrorOutput → Handle API Error → Slack 告警 + Sheets 记错 + 用户 Fallback 礼貌回复 |

**设计亮点（教案卖点）**：
1. 30 分钟升级防轰炸锁（Sheets 查写锁，成熟工程做法）
2. 三档模型分级：8b 小模型打杂、70B 大模型处理安全事件——成本意识好
3. 全链路错误兜底网（continueErrorOutput 汇总到统一错误处理）
4. 一个 Groq key 打三样：Whisper 转写 + LLM 分类/回复 + TTS

## 三、凭证缺口与替代方案（能免费不付费）

| 原模板凭证 | 缺口 | 替代方案 | 费用 |
|---|---|---|---|
| Telegram Bot ×2（客服号+内部通知号） | ❌ 无 | BotFather 免费建 2 个 bot（脚本可代建/用户提供 token） | 免费 |
| Groq API（转写+LLM+TTS） | ❌ 无 Groq key | Groq 注册免费额度即可真跑；**或** Whisper→DeepSeek 不支持语音需换：LLM 分类/回复全部 **DeepSeek 直连**（project 现有 deepseek-key.json，OpenAI 兼容接口，改 URL+model 名即可），转写用 Groq 免费档或 edge-tts 反向不可用——语音转写建议保留 Groq 免费档（whisper 每体量大免费），或走 A/B 路径 mock | Groq 免费档 / DeepSeek 按量(极低价) |
| Google Sheets ×3 表 | ❌ 无 Google OAuth | **方案一：本地 JSON 文件**（state 目录读写，Code 节点替代，零成本推荐）；方案二：飞书多维表「N8N客服台账」复用现成 tenant_token 脚本经验 | 均免费 |
| Slack OAuth | ❌ 无 Slack 工作区 | **飞书机器人推群**（复用现成「N8N教案」机器人 token 经验，curl 即推）或本地 log + GitHub Issue | 免费 |
| Groq TTS (orpheus) | 含在 Groq | 保留 Groq 免费档；或 edge-tts（本地免费，本项目教案01 已验证管线） | 免费 |
| 模型名 llama-* / crisper | — | DeepSeek 替换：分类/FAQ 用 `deepseek-chat`，安全/交易大模型用 `deepseek-reasoner` 或同 chat；`response_format json_object` DeepSeek 兼容 | — |

> 推荐组合（免费优先）：**Telegram 免费 bot + Groq 免费档做转写/TTS + DeepSeek 做 LLM + 本地 JSON 替 Sheets + 飞书机器人替 Slack**。若连 Groq 都不想注册，B 路径全 mock 零外部依赖。

## 四、L2 验证计划（A单元级 / B mock / C真跑）

- **A 单元级**：把 8 个 Code 节点忠实移植到 `L2Test175220001`，断言覆盖——Fix Audio Filename 的 binary key 归一、Extract Transcript 两条支路、Parse Classification 的 ```json 清洗与 fallback、Evaluate Escalation Lock 的 30min 窗口（含过期/无值）、Prepare Log Data 的 escalating 判定、Handle API Error 的逐级 chatId 回退。沿用 18238 的 build-l2-test.py 生成器套路，预计 30+ 断言。零外部凭证，今天可跑。
- **B mock**：Code 节点 mock Groq 三个响应（分类 JSON / FAQ reply / 70B reply）+ Sheets 读写改 JSON 文件 → 整链真引真 n8n 跑通消息流（Telegram 触发可用 Set 节点注入假 message 模拟）。只需结构正确，不花一分钱，能验证整图拓扑无断线。
- **C 真跑**：需 Telegram bot ×2 + Groq key（免费注册）+ Sheets 替代已就位；真发一条 Telegram 语音+一条文本看全链。

**推荐：A + B**（与教案01同规，免费、当日可交付、教案素材足）；C 留作加分项，等用户拍板是否注册 Groq。

## 五、风险点

1. **转写依赖**：DeepSeek 无语音接口，C 路径必须 Groq（或其他 Whisper 服务）；教案需把「语音转写」讲成可插拔环节。
2. **Parse Classification JSON 的 fallback 静默**：分类失败默认 faq/neutral 会把真安全事件降级——教案可点出这是有意容错也是隐患。
3. **Notify Human Agent 用了第二个 Telegram 账号**（发给人工坐席），替代方案需同样"双通道"语义，飞书群可天然充当。
4. **triage 领域是加密钱包**：文案全英文、FAQ 长，本地化短视频脚本时需中文化再造，避免照抄 CBox 场景。
5. **meta.templateId 数字坑**：导入本地前记得转字符串（教案01 踩过）。
6. nodeCount 元数据(9)与实际(33)不符，教案里以实际节点图为准。

## 六、建议下一步（等待审核的第一个决策）

1. **拍板 L2 路径**：A+B（推荐，零费用）还是 A+B+C（需你注册 Groq 免费 key + 建 2 个 Telegram bot）？
2. **拍板替代方案**：Sheets→本地 JSON（推荐）还是飞书多维表？Slack→飞书群机器人（推荐）？
3. 审核通过后我即开工：建 `L2Vrf175220001` 导入（修 meta.templateId）→ A 路径单测 → 报告推群待审。