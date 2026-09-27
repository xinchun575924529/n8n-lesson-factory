# 立项报告 · 项目 18552

> Manage rental equipment bookings and returns with DeepSeek, Google Sheets, Gmail, and Discord
> 时间：2026-09-28 07:1x（Asia/Shanghai）｜来源：fresh（老板在教案制作组群 B路定选）

## 1. 项目是什么

**一句话**：设备租赁公司的「预订+归还」全自动管家——用户通过两个 webhook 提交租赁申请/归还报告，AI（DeepSeek Agent）实时查库存表判断有没有货，自动确认预订/回邮件/发群通知；另外每天早上 7 点定时扫一遍订单表，该取货的提醒取货、该还货的催还货、逾期的发逾期通知，并给团队发日报摘要。

**业务场景**（真实可卖）：摄影器材/音响/活动设备租赁门店。这是「AI 管库存 + 免人工回单」的中小企业普惠场景，客户画像清晰（婚庆公司、影棚、设备租赁行）。

## 2. 三条主干流水（~33 节点，功能节点 12 类）

### 主干① 预订受理（webhook /rental/intake）
Webhook → Normalize（生成 booking_id RB-xxx、规整字段、total_qty 计数、status=pending）→ Validate（5 字段非空）→ **AI Availability Agent**（DeepSeek，带 Google Sheets 库存工具 rental_inventory_tool）→ Parse JSON → If available：Append 到 Bookings 表 + Discord 通告 + Gmail 确认信；conflict/partial：Append conflict 行 + Gmail 致歉信 + Discord 呼叫人工。
字段缺失分支：Discord 警告 + Gmail 内部通知。

### 主干② 归还登记（webhook /rental/return）
Webhook → Normalize（return_id RT-xxx、condition 默认 good）→ Validate → Log 到 ReturnsLog 表 → 读全量 Inventory → Match 库存行（found/未found）→ 更新 booked_qty-1（Math.max(0,x)防负数）→ 损坏/丢失（damaged/missing）触发押金复核 deposit_note + 告警。

### 主干③ 每日清扫（scheduleTrigger 0 7 * * *）
读 Bookings 表 → Compute Due Actions（明天取货 pickup/今天还 return/已逾期 late，纯 JS 日期差）→ If 有事干：Split Out → Build Reminder Emails（三类文案）→ Gmail 群发 → Build Stats → Discord 日报；没事干：Discord「All clear」。

## 3. 凭证需求与免费替代方案（能免费不付费）

| 凭证 | 原模板 | 替代方案（我们的现成资产） |
|---|---|---|
| LLM | openAiApi 自定义 endpoint（`deepseek-v4-flash` 是作者自建中转的模型名，**没有任何公开渠道能跑这个名**）→ **必换** | **DeepSeek 官方 API 直连**（key 现成 `state/deepseek-key.json`，baseURL=https://api.deepseek.com，model=deepseek-chat）✅ 零成本（有余额） |
| Google Sheets OAuth2 | Bookings / Inventory / ReturnsLog 三表 + Agent 工具表 | **本地 JSON 文件替代表**（沿用 17522/2682OL L2-C 已验证路径）；C 真跑若想可视化可升级飞书多维表格（N8N教案 bot tenant token 可写） |
| Gmail OAuth2（×4 处） | 确认信/致歉信/提醒信/无效通知 | 免费替代=**本地 outbox JSON 草稿库**（mock 发信全字段留痕）；想要真发信可加 163/QQ 免费 SMTP（lesson 课程可作为增值展开） |
| Discord Bot（×6 处） | Jakserver/form-contact 频道 | **飞书群播报**（N8N教案 bot tenant token 直发教案制作组群，已验证通道） |

**结论：零付费可跑通全链路，核心成本 = DeepSeek 官方 API（极便宜且已在库）。**

## 4. 模板坑预判（写进教案卖点的候选）

1. **模型名死坑**：`deepseek-v4-flash` 不是任何官方模型名（作者自家中转），直接导入必 404 → 必须换 deepseek-chat + 改 baseURL。
2. **库存只减不加**：确认预订只 Append Booking，**从不给 Inventory 的 booked_qty +1**；归还时才 -1 ⇒ 同一设备可被并发超卖，available_qty 永远等于 total_qty。这是模板最大逻辑缺陷，教案里必修（AI Agent 工具层加 update，或 Parse 后补一条 Update 节点）。
3. **partial 误杀**：Agent 判定 partial（部分有货）也落到 conflict 分支，且给租客发「没货」信——实际可能主件有货，体验差，教案可升级成 partial→人工复核分支。
4. **LLM JSON 解析裸奔**：`JSON.parse(output.replace(code fences))` 失败就静默 fallback 成 conflict——租客会被无端拒单；需加固（outputParser / 重试）。
5. **硬编码收件人**：两处 Email Invalid Notice 的 sendTo 是 `user@example.com` 占位（作者忘改）。
6. **daily sweep 时区**：cron `0 7 * * *` 跟随实例时区，日期差用 UTC 零点对齐——国内学员改 conf 时注意（教案给 Asia/Shanghai 修正版）。
7. **IF loose typeValidation**：已知 n8n 2.x 坑（严格模式下 `found` 布尔比较会抛 Wrong type），沿用 B 验证时逐个标注。
8. Agent 工具一次性全量读表：库存行多时 token 浪费 + tool 结果截断风险（小店场景无碍，教案可提优化）。

## 5. L2 验证计划

- **L2-A 单元级**（推荐先做）：忠实移植 5 个 Code/Set/If 逻辑块（Compute Due Actions / Build Reminder Emails / Build Reminder Stats / Normalize Booking+Return / Match Inventory Item）→ 单测断言 ~30 条。重点断言：日期差 pickup/return/late 三种 action 分类、total_qty 解析、`Math.max(0, booked-1)` 防负、damaged 触发 damage_alert、Normalize 的 booking_id 前缀格式。
- **L2-B mock 全链**：保留全名全连线，17 个外部节点换 mock（4×Gmail、6×Discord、4×Sheets、1×SheetsTool mock 回固定库存、1×LLM mock 回固定 JSON），场景驱动：
  - S1 正常预订 available→确认链
  - S2 库存不足 conflict→致歉+呼人工
  - S3 字段缺失→告警链
  - S4 归还 good→库存回滚
  - S5 归还 damaged→押金复核+损坏告警
  - S6 归还未知物品（found=false）
  - S7 日清有 due→三提醒发信+日报
  - S8 日清无事→All clear
- **L2-C 免费真跑**：DeepSeek 真调（真 Agent + 真工具，工具源改本地 JSON stock 文件）+ 本地 JSON 替代表 + outbox 邮件草稿 + 飞书群播报真实发群。与 8270/17522 同配方，零付费。

## 6. 风险点

- **低**：全链路无付费墙，DeepSeek 余额可控（单场景 1-2 次调用）。
- **中**：AI Agent 工具调用链路在 CLI 单测下无法直接验（B/C 阶段用场景驱动覆盖）；Agent prompt 里给了 tool 用法白名单，DeepSeek deepseek-chat 工具调用能力已多次验证（双 bot/工厂 L2-C 均用），风险可控。
- **低**：33 节点规模，B mock 工作量大（~17 mock 节点），属体力活。

## 7. 教案卖点初判

- **L2-C 后成为「AI 运营管家」线旗舰课**：从「表单受理 → AI 决策 → 自动履约」全闭环，比 lesson-02（客服）更贴近「赚钱生意」。
- 库存超卖缺陷（坑#2）修复版本身就是一节干货（原版缺陷 vs 我们的加固版对比教学）。
- 每日清扫那段纯 JS 日期计算非常适合教「零 AI 也可行的确定性自动化」，与 AI Agent 段形成「确定性+智能」对比教学。

---

**状态**：待老板拍板 → 进 L2-A。