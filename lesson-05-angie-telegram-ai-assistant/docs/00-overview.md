# 00 · 总览：15 节点的一根主轴

模板页：https://n8n.io/workflows/2462/（40.3 万人次浏览，AI Builder 生成）

## 一句话
Telegram 收到文字或语音 → 白名单鉴权 → 语音转文字 → **带记忆的 Agent 编排 4 个工具**（任务表 / 联系人表 / Google 日历 / Gmail）→ 文字答案发回 Telegram。

## 节点地图（骨架）
```
[Listen for incoming events] telegramTrigger
   → [AllowList] set                      ← 硬编码白名单 <chat id> 占位
   → [If1] if                             ← from.id == allow ? 否则静默
   → [Voice or Text] set                  ← 提取 text 与 sessionId
   → [If] if                              ← text 为空 → 判定语音
      ├ 语音→ [Get Voice File] telegram(file) → [Speech to Text] openAi(transcribe)
      └ 文字→ 直接进入
   → [Angie, AI Assistant] langchain.agent v3.1   ← 大脑（系统提示词见 docs/04）
   → [Telegram] telegram.sendMessage      ← Markdown 回文
AI 侧翼（接在 Agent 上，不占主轴）
   [OpenAI Chat Model] lmChatOpenAi       ← 主 LLM（课程换 DeepSeek）
   [Simple Memory] memoryBufferWindow     ← 会话记忆 window=10（🔴 硬编码坑见 docs/03）
   [Tasks] baserowTool                    ← 任务表（tableId 372174）
   [Contacts] baserowTool                 ← 联系人表（tableId 372177）
   [Google Calendar] googleCalendarTool   ← 日历（timeMin 用 $fromAI）
   [Get many messages in Gmail] gmailTool ← 邮件读取
```

## 你要安装的三个世界观
1. **主轴只有一条**：入口 → 鉴权 → 双模态统一成文本 → Agent → 工具 → 回复。其他 90% 的 TG 助理类模板都是这根轴的变形（2682OL 真人客服也一样）。学会它=学会一个品类的发动机。
2. **"AI 侧翼"不占主线**：Model / Memory / 4 个 Tool 都挂在 Agent 上，靠连线类型（`ai_languageModel` / `ai_memory` / `ai_tool`）注入，不在主流程执行序列里。画 mock / 换 LLM 时千万别把它们当主线节点数。
3. **白名单是入口的第一道闸**：它不是锦上添花，是让你敢把助理丢进公开 Telegram 的前提。**这模板的白名单有一个类型级的隐性地雷：它靠 If 节点的"宽松校验"侥幸跑通，你一旦重构就会当场爆炸**——先修再用（见 docs/01 坑#2）。

## 验证战绩速览（三级全过）
| 关 | 方法 | 断言/场景 | 结果 |
|---|---|---|---|
| L2-A 单元 | 复刻 4 个逻辑节点 + 假工具真 Agent | 7 checks × 2 跑 | ✅ 14/14 |
| L2-B 集成 | 14 功能节点 1:1 拓扑 mock + 真 DeepSeek | 5 场景 | ✅ 全过（S5 初始一 warn，已定位） |
| L2-C 免费替身 | edge-tts 真语音 → Vosk → Agent → 真 HTTP 工具 | 5 场景 | ✅ 全过 |

工作流与报告全文见 `workflows/`；复现环境所有坑见 `docs/05`。