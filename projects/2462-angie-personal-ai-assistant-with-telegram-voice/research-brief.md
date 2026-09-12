# 立项报告 · 2462 Angie 个人 AI 助理（Telegram 语音+文字）

## 项目名片
- **项目名**：Angie, personal AI assistant with Telegram voice and text
- **中文名**（暂定）：Angie：Telegram 语音+文字个人 AI 助理
- **来源**：n8n 官方模板库 https://n8n.io/workflows/2462/ （API 拉取于 2026-09-12 14:21）
- **定选来源**：fresh 候选 → B 模式（入库+立即研发），requestedAt 2026/9/12 13:45
- **节点数**：15（定选信息报 8 大类节点类型）
- **定位**：AI 应用 / Telegram Bot / LangChain Agent 入门课

## 用途（一句话）
用户用 Telegram 给机器人发文字或语音，AI 助理（带记忆）自动调用 Gmail、Google 日历、Baserow 任务/联系人四个工具回答问题，再把答案以文字发回 Telegram——一个「会用工具的私人聊天助理」经典范式。

## 节点清单（15）
主链：
1. **Listen for incoming events**（telegramTrigger）— 收消息触发
2. **AllowList**（set）— 硬编码白名单 `<chat id>` 占位
3. **If1**（if）— 白名单鉴权：from.id == allow
4. **Voice or Text**（set）— 提取 text 与 sessionId
5. **If**（if）— text 为空 → 判定语音
6. **Get Voice File**（telegram, resource=file）— 下载语音文件
7. **Speech to Text**（langchain.openAi, transcribe）— Whisper 转写
8. **Angie, AI Assistant**（langchain.agent v3.1）— 核心 Agent，系统提示词含日期注入与 4 工具使用规范
9. **Telegram**（telegram, sendMessage）— Markdown 回复
AI 侧翼（接入 Agent）：
10. **OpenAI Chat Model**（lmChatOpenAi）— 主 LLM
11. **Simple Memory**（memoryBufferWindow，window=10）— 会话记忆（⚠️ 硬编码 sessionKey=angie_session_default）
12. **Tasks**（baserowTool, tableId 372174）— 任务表工具
13. **Contacts**（baserowTool, tableId 372177）— 联系人工具
14. **Google Calendar**（googleCalendarTool）— 日历查询工具（timeMin 用 $fromAI）
15. **Get many messages in Gmail**（gmailTool）— 邮件读取工具

## 凭证缺口与替代方案（能免费不付费）
| 模板凭证 | 用途 | 替代方案 | 成本 |
|---|---|---|---|
| telegramApi | 收/发消息、下载语音 | 免费 BotFather 建测试 bot | **免费** |
| openAiApi ×2（STT + Chat） | Whisper 转写、LLM | Chat → **DeepSeek 直连**（已有 key，余额9.9元，deepseek-chat）；STT → **Groq Whisper**（免费档，17522 已验证此判断）或保留 OpenAI 节点 mock 转写 | 近免费 |
| baserowApi ×2 | 任务/联系人表 | Baserow 官方云有免费档（baserow.io 注册即可），或自建 docker / mock 本地 JSON | **免费** |
| googleCalendarOAuth2Api | 日历工具 | 自有 Google 账号 OAuth（免费），或 L2 阶段 mock | **免费** |
| gmailOAuth2 | 邮件工具 | 同上 Google OAuth（免费），或 L2 阶段 mock | **免费** |

**结论：全链可做到近零成本**。新增成本仅 DeepSeek 直连接口费（分毛级）。Google OAuth 是免费但需人工在 GCP 建客户端（约 15 分钟）——L2 可先 mock，L3/C 阶段再补真连接。

## L2 验证计划（三选 / 推荐）
- **A 单元级（推荐起步）**：把 4 个纯逻辑节点（AllowList set、If1 鉴权、Voice or Text set、If 语音判定）忠实移植单元测试，重点覆盖：白名单通过/拦截、文字分支、语音分支（text 空→走 Get Voice File）。预计 15-20 断言。
- **B mock 级**：全链保留结构，Telegram/OpenAI/Gmail/Calendar/Baserow 全换 mock 节点，C 场景（文字问答 / 语音问答 / 白名单拦截）跑通 Agent 编排语义（Agent 节点可挂 DeepSeek chat 真调+假工具）。
- **C 真跑**：需 Telegram 测试 bot、Groq/OpenAI STT key、Google OAuth、Baserow 表——**全免费可集齐**，但配置链最长。
- **推荐路径：A → B → C 分段**，A 无风险立即做；B 是本模板教学价值核心（Agent 工具调用演示）；C 走到哪步由拍板决定（Google OAuth 是唯一需要人工配置的环节）。

## 风险点预判
1. **Agent 节点类工具链**是本项目新地形：此前 17522/8270 都没验证过 `ai_tool`/`ai_memory` 子连接在 mock 下的行为，B 阶段可能踩坑（也是教学卖点之一）。
2. **memoryBufferWindow 硬编码 sessionKey**：`Voice or Text` 提取了 sessionId 却没用上，多用户会串记忆——模板缺陷，可在教案中作为「找茬点」。
3. **白名单是硬编码 set 节点**：`<chat id>` 占位需用户自填，导入即用会全拦截/全放行，注意演示。
4. **STT 转写后无语音回复**：只回文字（17522 是语音回语音，本模板更简单）。
5. 模板元数据 `aiBuilderAssisted: true`（AI 生成模板），官方人工审核度未知，导入后需核对连线。

## 阶段规划
- L2：A 单元级 → B mock（推荐）→ C 真跑（待拍板范围）
- L3：GitHub 教案仓库 lesson-05 / 06（按工厂编号顺延）+ 多维表台账登记
- L4：横屏视频 + sau 双/三平台发布（抖音/B站/视频号）

*立项生成：研发·2462 车间会话，2026-09-12 14:21 Asia/Shanghai*