# Telegram 语音/文字 AI 私人助理：白名单 + 4 工具 + 会话记忆 全栈实战
> 出处：https://n8n.io/workflows/2462/（Angie, personal AI assistant with Telegram voice and text，**40.3 万人次浏览**，AI Builder 生成模板）

一个会被几万人收藏的模板长什么样：你在 Telegram 里发文字**或语音**，AI 助理（带会话记忆）自动调 Gmail、Google 日历、任务表、联系人表 4 个工具回答你，再把答案发回 Telegram——「会用工具的私人助理」最经典范式。这套打法是 2682OL 式真人 AI 客服项目的**同款发动机**（消息入口 → 白名单 → Agent → 工具 → 回复）。
我们把模板 15 节点完整复制出来做了 L2 三级验证（A 单元 / B 集成 / C 免费替身链，**三关全过**），并抓出 **4 个必须先治的坑**（1 个会泄露用户隐私的安全级缺陷、1 个靠"侥幸"才没炸的隐性地雷）。交付版直接治好，可商用。

## 你将学到（6 讲每讲配可跑工作流）
1. **00 总览**：15 节点骨架地图；一条「消息 → 鉴权 → 双模态统一 → Agent + 4 工具 → 回复」主轴
2. **01 入口与安全**：Telegram Trigger / webhook 部署玄学 / **白名单「我是主人却被拒之门外」类型坑** / 影子流量与 429/452 反爬常识
3. **02 语音与 STT 替身**：Get Voice File → Speech to Text 全链；**零成本替身链 = edge-tts 造真语音 + Vosk 自托管中文识别**（一个端口、一个 IPv6 大坑各断你一晚）
4. **03 Agent × 工具 × 记忆**：LangChain Agent v3.1 编排；**toolCode v1 不兼容的"幻觉自答"级坑**；**记忆 sessionKey 硬编码 = 所有用户共享一份记忆（安全级）**
5. **04 系统提示词工程**：日期注入、工具使用规范、**促销邮件"嘴上说不要身体很诚实"怎么治**（STRICTLY EXCLUDE 死约束，L2C 实测有效）
6. **05 排障图谱**：10 坑照妖镜合集 + 环境怪癖大赏（第三个最玄学，部署过 webhook 的都懂）

## 这是 4 个"必修才准交付"的坑（剧透式目录，正文有药方）
| # | 坑 | 级别 | 一句话后果 |
|---|---|---|---|
| 1 | Simple Memory 硬编码 `sessionKey=angie_session_default` | 🔴 安全 | **所有用户共享一份记忆**，甲跟助理说的悄悄话乙全问得出来 |
| 2 | AllowList 拿 **string** 存 `<chat id>`，全靠 If1 `looseTypeValidation=true` 侥幸放行 | 🔴 隐性地雷 | 一旦重配/重导/照抄，If 直接抛 `Wrong type`，**整条执行报错**，用户消息石沉大海 |
| 3 | 自建/复刻工具时 `toolCode` typeVersion=1（L2 复刻实测，模板本体不含此节点） | 🟡 兼容 | 工具被执行、有返回值，**Agent 却收不到观测，开始幻觉现编答案** |
| 4 | "filter out promotional" 提示太软 | 🟡 健壮 | DeepSeek 嘴上说已过滤，**促销邮件照样列进你的晨报** |

修复方法全写在正文，且**每一个都在真实 DeepSeek 引擎下复跑验证过**（不是理论）。

## AI 引擎方案（成本直减 99%+，L2C 实测真链）
| 模板角色 | 原案 | 工厂实测替身 | 成本 |
|---|---|---|---|
| 主 LLM | OpenAI gpt-4o | **DeepSeek deepseek-chat**（OpenAI 兼容直连） | 分毛/次 |
| 语音转写 STT | OpenAI Whisper | **Vosk small-cn 0.22 自托管**（42MB 离线模型）/ Groq Whisper（免费档） | 0 |
| 造测试语音 | 人工录音 | **edge-tts 一键产出真 mp3** | 0 |
| 工具后端 | Baserow 云 + Google OAuth | **本机 127.0.0.1:8766 免费数据层**（L2C）→ 换真源零删改 | 0 |
| Telegram | 同原案 | BotFather 建测试 bot | 0 |

## 现场实测证据（不是复述官方话术）
- L2-A 单元单测：7 checks × 双跑 = **14/14 全过**（白名单通过/拦截、双模态分流、3 工具全命中）
- L2-B 集成测试：模板 14 功能节点 **1:1 拓扑 mock + 真 DeepSeek 驱动**，5 场景全过（含两步记忆 "ZQXK-8888" 问答回环）
- L2-C 免费替身链：**edge-tts 造的真 mp3 → Vosk 离线识别 → Agent 真调 2 个 HTTP 工具 → 文字答案**，5 场景全过；促销邮件加固后正确跳过
- 完整证据、测试工作流、报告全文见 `workflows/` 与 `docs/`

## 仓库地图
```
.
├── README.md                 本文件
├── LEGEND.md                 图例与代号（L1-L5 / A-E 门 / 🔴-⚪）
├── docs/
│   ├── 00-overview.md            节点地图与一条主轴
│   ├── 01-entry-security.md      TG 入口 / webhook 玄学 / 白名单 / 反爬
│   ├── 02-voice-stt-free.md      语音链路 + STT 零成本替身
│   ├── 03-agent-tools-memory.md  Agent 编排 / toolCode 1.3 / 记忆安全
│   ├── 04-prompt-hardening.md    系统提示词工程与 "嘴硬" 治理
│   └── 05-pitfalls-defense.md    10 坑排障图谱 + 怪癖大赏
├── exercises/exercises.md    5 个逐级动手练习（成品判据明确）
├── script/short-video.md     1 分钟短视频讲稿（获客版）
├── workflows/
│   ├── README.md               4 个 JSON 使用说明与安全红线
│   ├── 2462-original-template.json      原模板 15 节点
│   ├── L2A-unit-test.json               单元测试流（7 checks 自评分）
│   ├── L2B-integration-mock.json        1:1 拓扑集成流（真 DeepSeek + 假工具）
│   └── L2C-free-replacement.json        免费替身链（真能跑全链路）
└── site/                     GitHub Pages 静态站（自动部署）
```

**License**: MIT（教程内容可自由转载，模板版权归 n8n 官方）

---
*本项目由「n8n 工厂店」教研车间产出 · L2 三级验证完成于 2026-09-14 · L3 教案封装 2026-09-18*