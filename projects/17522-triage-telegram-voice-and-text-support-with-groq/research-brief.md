# 17522 立项报告（重跑版 Rerun）

- **项目**：Triage Telegram voice and text support with Groq LLMs and Google Sheets
- **来源**：https://n8n.io/workflows/17522/ （模板 API 2026-09-14 重取，模板仍在架、节点无变化）
- **定选**：B 路立即研发（fresh 候选）；**2026-09-14 老板指令重跑**：生产线调整后（横屏 1920×1080 改版 + sau 发布执行器上线），全链路重新生成 lesson-02。
- **用途**：Telegram 客服分级机器人——语音/文字进线 → Groq Whisper 转写 → LLM 意图/情绪/安全风险分类 → 30 分钟升级防重锁 → 按意图分流（FAQ 快答/交易·KYC 上下文答/安全·交易强模型答）→ 升级人类客服（第二个 TG bot + TTS 语音安抚）→ Sheets 三表落账 + Slack 错误告警。

## 节点清单（40 节点，含 8 个 stickyNote）

**Intake**：Voice Message Trigger(telegramTrigger) → Has Voice?(if) → Get Voice File → Fix Audio Filename(code) → Transcribe (Whisper)(http→groq whisper-large-v3-turbo) → Extract Transcript (Voice)(code) ｜ Has Text?(if) → Extract Transcript (Text)(code) → Unsupported Message Reply
**Classify**：Classify Intent & Sentiment(http→groq llama-3.1-8b-instant) → Parse Classification JSON(code)
**Escalation**：Get row(s) in sheet(Escalations) → Evaluate Escalation Lock(code, 30min 窗) → Already Escalated?(if) → Holding Reply / Escalation Check(if: angry|frustrated|security_risk) → Set Escalation Lock(sheets) → Notify Human Agent(telegram bot2) → Generate Voice Reply (TTS)(http→groq orpheus wav) → Send Voice Reply to User
**Routing**：Route by Intent(switch: faq / tx+kyc / security+trading) → Fast Model Reply (FAQ)/Contextual Reply (Tx·KYC)/Strong Model Reply (Security·Trading) → Extract Reply Text(code) → Send Reply to User → Prepare Log Data(code) → Log Interaction(sheets)
**Error Net**：Handle API Error(code) → Alert Slack (Error) / Log Error to Sheet / Fallback Reply to User

## 凭证缺口与替代方案（结论沿用首次研发，已全绿验证）

| 原凭证 | 替代 | 状态 |
|---|---|---|
| Telegram bot ×2 | 免费 BotFather 自建（296795 项目已有两 bot 先例） | ✅ 免费 |
| Groq API（转写+3×LLM+TTS） | LLM→DeepSeek（直连免费额度）；转写首跑仍 Groq 免费档 / 或伪造 STT mock；TTS→edge-tts 晓晓 | ✅ |
| Google Sheets | 本地 JSON（locks/interactions/errors） | ✅ |
| Slack | 飞书群推送（tenant token 直连 OpenAPI） | ✅ |

零硬成本。

## L2 验证计划

- **A 单元级**：首次已 32/32 全过（L2Test175220001）。
- **B mock 全链**：首次已 42/42 全过（L2Mock175220001，S1–S6+E1 场景）。
- **C 真跑（免费替身链）**：DeepSeek 替换 Groq×4 + edge-tts 替换 TTS + 本地 JSON + 飞书推群；真 TG bot 收发。
- **推荐（重跑目的）**：**A+B+C 全做**，C 是真验收硬要求（上次 L5 客户线遗留结论）；A/B 有现成生成器可快速重建，C 是本跑主战场。

## 风险点（模板 4 大坑，首挖已记录）

1. Sheets 空锁表返回 0 项 → 下游静默断链（需空行/mock 占位）。
2. Log Interaction 列映射 bug（content 列→sentiment、userName 列→transcript；升级链无 escalated 字段）。
3. 错误网只罩 intake/LLM 链，Telegram 发送节点裸奔（失败无兜底）。
4. 沙箱 Code 节点用 fs 须自带 `const fs=require('fs')`；升级链 SendVoice→Prepare→Log 连线需修正（原版跳过 Prepare Log Data）。

## 里程碑（重跑）

L2 A/B/C 全绿 → L3 教案仓库重建（lesson-02 仓库已存在，需按横屏新规范刷新）→ L4 横屏 1920×1080 视频 + sau 三平台发布。