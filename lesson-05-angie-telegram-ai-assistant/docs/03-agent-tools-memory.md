# 03 · Agent × 工具 × 记忆：编排与两个高危坑

## 核心节点一览
- **Angie, AI Assistant**（`@n8n/n8n-nodes-langchain.agent` v3.1）：
  - `model` ← OpenAI Chat Model（课程换 DeepSeek，OpenAI 兼容直连）
  - `memory` ← Simple Memory（window = 10）
  - `tools` ← 4 个：Tasks / Contacts（Baserow）、Google Calendar、Gmail
- 系统提示词：日期注入 + 每个工具的使用规范 + 促销邮件过滤（模板原文，见 docs/04 找茬）

> ⚠️ 先澄清一个常见误读：**模板本体 15 个节点里没有任何 `toolCode` 节点**（它用的是 baserowTool / googleCalendarTool / gmailTool 三个现成工具节点）。下面这个坑是**你在本课 L2 复刻、或自建自定义工具时必然撞上**的（已用工作流实测确认）。

## 🟡 坑#3（自建工具坑，L2 复刻实测）：toolCode typeVersion=1 与 Agent v3 不兼容（幻觉自答）
**症状**：工具确实跑了（你能在 n8n Executions 里看到 logging/HTTP 200），但 Agent 系统提示里的 `{{ $json.obs }}` / tool observation **恒为空字符串**，Agent 只好"凭印象"应答。
**根因**：`@n8n/n8n-nodes-langchain.toolCode` 的 **typeVersion=1**（老接口）与 Agent v3 的输出契约不一致；v1 还按旧字段回，Agent v3 等不到新一轮 obs。
**修复**：凡是画 toolCode，**无脑 typeVersion=1.3**（保留 name/language/description/jsCode，仅升版本号）。L2A 用 1.3 复跑 3 个工具命中证据：calculator / google_calendar / task_list 均返回真实 obs 并被写入答案 ✅。
> 口诀：**画 toolCode 必 1.3**。

## 🔴 坑#1：Simple Memory 硬编码 sessionKey = 全员共享记忆（安全级）
**模板原文**：`memoryBufferWindow` 的 `sessionKey` 写成常量 `angie_session_default`。
**后果**：**所有用户共用一份会话记忆**。甲问"记住我基金账号 6666"，乙再问就 100% 命中——**隐私级灾难**。L2A 里我们故意复现并记录在案 ✅。
**修复**：
```
memoryBufferWindow.Session ID Type = "Define below"（fromInput）
sessionKey  = {{ $('Listen for incoming events').item.json.message.from.id }}
```
让"每个 TG 用户一份自己的记忆"。若想做"家庭/小组共享记忆"，再把 key 换成 `chat.id` 显式声明边界。

## 工具调用的 4 个观察
1. **Window=10 记忆**对私人助理够用，但**Agent 可能在 10 轮内"忘记"旧任务**——重要事实（例如用户身份、偏好）请用额外 set 注入 system，不要指望 memory。
2. **Google Calendar** 用 `$fromAI("timeMin", …)`，**第一次调用时它的值可能为 null**——交付版加一个默认值（例如今天 00:00）。
3. **Baserow 工具**走云免费档没问题，但表 ID 硬编码——**多环境部署时（dev/stage/prod）必须变量化**。
4. **测试断言不要落在"工具是否被调用"上**——共享记忆下 Agent 可能凭记忆作答，obs 恒未调用但答案仍对；断言应落在**最终输出内容**（比如答案里出现了具体任务名）。

##  Replica 的最小工程清单
- [ ] LLM 凭证：DeepSeek key（OpenAI 兼容），`https://api.deepseek.com/v1`
- [ ] STT 凭证：Vosk 127.0.0.1:8766（OpenAI 兼容 transcribe）
- [ ] 记忆：sessionKey = fromInput(from.id)
- [ ] 工具：toolCode 全升 1.3，4 个工具默认凭证齐全（Baserow/Gmail/Calendar 可先 mock）
- [ ] 回复：Markdown、长度预算 ≤350 字、命中率高的表情做亲和度