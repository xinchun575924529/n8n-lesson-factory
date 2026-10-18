# 立项报告 · 模板 20683 · Send daily AI-scored job alerts with Apify Jobs, Claude, Google Sheets, Telegram and Gmail

- **项目编号**：20683（n8n 官方模板号）
- **来源**：https://n8n.io/workflows/20683/
- **API**：`https://api.n8n.io/api/workflows/templates/20683`（200，含 workflow，活链 ✅）
- **定选时间**：2026-10-18 14:18:40（fresh 候选）
- **节点数**：21 个（15 个功能节点 + 6 个 StickyNote）
- **节点类型**：scheduleTrigger / set / httpRequest×2 / googleSheets×2 / code×3 / if×3 / telegram / gmail

## 项目是什么（一句话）

每天定时从 Apify 抓「过去 24h 新发布」的招聘岗位，去重（对照 Google Sheet 已见 ID），交给 Claude 按个人简历打 0-10 分，Top N 推送到 Telegram / Gmail，并回写 Sheet 台账。

## 流程结构（4 段）

1. **Schedule & Fetch**：Daily Schedule（9:00）→ Search Settings（Set，14 个参数集中配置）→ Fetch Jobs（HTTP POST Apify actor `pk07007~ats-jobs-api/run-sync-get-dataset-items`，query 带 `maxTotalChargeUsd` 消费封顶）
2. **Keep only new jobs**：Get Seen IDs（Sheets 读全表）→ Filter & Prep（Code：去重已见/批内重复，拼 LLM prompt）→ Any New Jobs?（IF count>0）
3. **Score & Log**：Score with Claude（HTTP POST api.anthropic.com/v1/messages，httpHeaderAuth）→ Merge Scores（Code：解析 JSON 数组、合并、按分排序、标 sent=topN；解析失败抛错不静默）→ Log to Sheet（append，onError=continueRegularOutput）
4. **Send Alerts**：Build Message（Code：Telegram 纯文本 3900 字符截断 + Gmail HTML）→ Telegram Enabled? / Gmail Enabled?（双 IF 开关）→ Send Telegram / Send Gmail
   - 无新岗位分支：No New Jobs Message → 同样走两个发送开关

## 凭证缺口与替代方案（能免费不付费）

| 原凭证 | 用途 | 替代方案 | 成本 |
|---|---|---|---|
| **Apify API token** | 抓招聘（ats-jobs-api actor，按次计费） | **C 真跑用 Apify 免费额度**（$5/月免费额度，run-sync maxTotalChargeUsd=1 封顶可控）；B 用 mock 数据 | ~$0（免费额度内） |
| **Anthropic (Claude)** | 岗位打分 | **DeepSeek deepseek-chat 直替**（同为 messages API，改 URL+model+header） | ~¥0 |
| **Google Sheets OAuth2** | 已见 ID + 台账 | **本地 JSON 文件**（state\clients\...\jobs-seen.json）或飞书多维表（N8N教案 bot tenant token 模式） | ¥0 |
| **Telegram bot** | 推送通道 1 | 本厂已有 TG bot 基建（@s2682ol_notify_bot，SG 服务器有 TG 通路）；mock 阶段用 Set | ¥0 |
| **Gmail OAuth2** | 推送通道 2 | **飞书群推送**（教案制作组 bot）或本地 HTML 文件落盘 | ¥0 |

**结论：凭证全部可替代，唯一真实外部依赖是 Apify（有免费额度，可先 mock 后真跑）。**

## 模板自带亮点（可作教案卖点）

- `maxTotalChargeUsd` 消费封顶参数——防 Apify 烧钱失控，好设计
- Merge Scores 解析失败**抛错不静默**（不重跑不漏岗，下次自动重试未打分的岗）
- Telegram 3900 字符截断 + "+N more" 兜底（TG 消息上限 4096）
- 双通道独立开关（sendTelegram/sendGmail）
- 台账驱动去重（Sheet 即状态库）

## 疑似坑（L2 重点验证）

1. **Apify actor 输出字段假设**：Code 里硬编码 `j.id / j.title / j.company / j.city || j.country / j.applyUrl`——`ats-jobs-api` 真实返回字段名是否一致待真跑验证（Apify actor 输出 schema 以页面为准，mock 时按假设造数据）
2. **无新岗位时 Get Seen IDs 读空表**：Sheets 读空表可能 0 项输出 → Filter & Prep 的 `$('Get Seen IDs').all()` 需确认空安全（模板用了 `.all().map(...)` 空数组应 OK，但 Sheets 节点 0 行时是否照常触发下游待验）
3. **Claude JSON 解析正则 `txt.match(/[[sS]*]/)`**——API 拉回来的模板 JSON 里 `\s` 被转义丢了（显示成 `[sS]`），导入后需确认 jsCode 里实际是 `/[\s\S]*?/`（中转义问题，L2-A 必查）
4. **prompt 里 `\n` 同样被转义**（API 返回体显示成 `\\n`）——同上
5. **scheduleTrigger 9:00 无时区设置**——默认跟随 n8n 实例时区，本机=Asia/Shanghai OK，课程里要点名
6. **countries=["India"] 默认值**是模板作者示例，学员需改成自己的目标地区

## L2 验证计划建议

- **A 单元级（推荐先做）**：3 个 Code 节点（Filter & Prep / Merge Scores / Build Message）忠实移植单测
  - Filter & Prep：去重（已见/批内重）、prompt 拼装、count=0
  - Merge Scores：正常 JSON 数组解析、乱文本容错（抛错路径）、排序+topN 标记
  - Build Message：TG 3900 截断、HTML 转义、无岗位分支文案
  - 预计 25-35 断言
- **B mock 全链（推荐做）**：Fetch Jobs→mock 岗位集（含重复/已见）、Score with Claude→mock 打分响应、Sheets→本地 JSON、Telegram/Gmail→Set 落盘；场景=正常日/无新岗/Claude 返回乱码/全部已见/超长列表截断
- **C 真跑（可选，需拍板）**：Apify 免费额度真抓 1 次（关键词 software engineer / India，maxSpend $1 封顶）+ DeepSeek 真打分 + 本地 JSON 台账 + TG/飞书真推送。成本≈$0，但**本机直连 Apify 需确认网络可达**（api.apify.com 海外，可能需 WARP）
- **推荐路径：A → B → C**（三关全做，C 用免费额度）

## 风险点

- Apify 网络可达性（海外 API，本机需 WARP；云 ECS 上海不通）→ C 关前置验证
- Apify actor 输出 schema 与模板假设不符 → B 关 mock 按假设造数据时标注，C 关真跑定案
- 转义丢字符坑（`\s`→`sS`）→ 导入即查 jsCode 原文

---
*产出：研发·20683 会话 · 2026-10-18*