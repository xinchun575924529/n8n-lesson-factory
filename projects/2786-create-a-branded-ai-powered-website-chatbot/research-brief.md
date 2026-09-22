# 立项报告 · 模板 2786：Create a branded AI-powered website chatbot

> 生成：2026-09-22 19:4x（Asia/Shanghai）｜来源：https://n8n.io/workflows/2786/
> 模式：B 立即研发 ｜ 状态：research

## 一、这是什么

给任意网站嵌一个**自有品牌的 AI 聊天机器人**（@n8n/chat 前端 + n8n Chat Trigger webhook 后端），由 AI Agent 充当「创始人助理」：
- 与访客多轮对话（20 轮窗口记忆，按 sessionId 隔离）；
- **查日历空闲**（读未来 14 天 Outlook 日历 → 算出营业时间内的空档）；
- **自动预约**（创建 Teams 在线会议邀请，发给客户邮箱）；
- **兜底线索转人工**（客户暂不预约时，收集姓名/公司/邮箱/需求，发一封排版精美的 HTML 告警邮件给老板）。

典型场景：中小公司官网的「AI 前台」，约见销售/咨询。

## 二、节点清单（21 个，含 6 张便签）

主链：Chat Trigger(disabled, webhook/public) → If(chatInput 存在?) → 是→AI Agent → Respond to Webhook；否→Respond With Initial Message（固定欢迎语）
Agent 挂载：OpenAI Chat Model(gpt-4o) ＋ Window Buffer Memory ＋ 3 个工具
子流（Execute Workflow Trigger → Switch by route）：
1. route=availability：Get Events(MS Graph calendarView 未来2~16天) → freeTimeSlots(Code 算空档, 营业时间 08:00-17:30 Europe/London) → varResponse(Set)
2. route=message：Send Message1(Microsoft Outlook 发 HTML 告警邮件，模板紫黑品牌风) → varMessageResponse(Set)
3. Make Appointment(toolHttpRequest)：POST Graph /me/events 建 Teams 会议

## 三、凭证缺口与替代方案（能免费不付费）

| 缺口 | 原方案 | 替代方案 | 成本 |
|---|---|---|---|
| OpenAI gpt-4o | 付费 | **DeepSeek deepseek-chat**（直连，余额现成） | ✅ 免费/极廉 |
| Microsoft Outlook OAuth2（日历读+建会议+发邮件）×3 处 | 需 M365 账号+OAuth | **mock**：B 关用 webhook mock 返固定日历数据；真跑替代=①日历→本地 JSON/飞书多维表格 ②告警邮件→**飞书群推送**（现成链路） ③建会议→写预约记录表+飞书通知 | ✅ 免费 |
| 前端品牌聊天页 | 外部 HTML 宿主 + @n8n/chat CDN | 本地 http.server 起静态页，嵌 n8n chat webhook | ✅ 免费 |

**结论：全流程可 0 元跑通；C 真跑也无需 Microsoft，用「本地日历数据 + 飞书通知」替代 Outlook 三件套。**

## 四、L2 验证计划（推荐路径）

- **A 单元级（起步，推荐）**：freeTimeSlots 空闲计算 Code 是本项目最硬核的逻辑（便签自认要改时区/营业时间）→ 忠实移植 + 10+ 断言（全天忙/全天闲/跨天/间隙/边界）；If/Switch/varResponse 分支逻辑同测。预估 15~20 断言。
- **B mock 全链**：Chat Trigger 链路 mock AI 工具三件套（availability/message/appointment），场景化断言：欢迎语分支、预约流、转人工流、不约只问流；DeepSeek 真连做 LLM。
- **C 真跑（可省凭证）**：DeepSeek + 本地日历 JSON + 飞书群告警 真跑一条「访客咨询→查档→成约」闭环。
- **推荐**：A+B 必做，C 用免费替代链真跑（无需老板补任何凭证）。

## 五、风险点

1. **Chat Trigger 默认 disabled**：导入后需启用并记得 public=true、responseMode=responseNode，否则前端拿不到回复。
2. **If 节点非 chatInput 分支回固定欢迎语**：@n8n/chat 首条握手消息（不含 chatInput）走 false 分支——删除 If 会让首页报错，教学点。
3. **freeTimeSlots 硬编码 Europe/London + 08:00-17:30**：本地化必须改，且业务时间串带 "Z" 与日历 timezone 混用易错（典型坑，成课卖点）。
4. **Make Appointment 时区字符串硬编码 Europe/London、时长硬编 30 分钟**。
5. **AI Agent systemMessage 超长且写死「Wayne / nocodecreative.io」**：品牌化改编点。
6. **Switch 只有 availability/message 两分支，无 default**：route 异常会静默丢（可加兜底）。
7. **gpt-4o 模型快照名** gpt-4o-2024-08-06 换 DeepSeek 时要清掉自定义 model 字段。
8. Outlook 邮件收件人 `user@example.com` 占位必改。
9. varResponse 用 `.toJsonString()` 输出 array→工具回执为 JSON 字符串，Agent 解析依赖 prompt 纪律。

## 六、课程化方向（lesson-07 候选）

- 改编为中文场景：「给公司官网装一个 AI 前台」——DeepSeek 换脑、飞书替 Outlook、本地日历 JSON；
- 卖点：Chat Widget 前端嵌入（@n8n/chat CDN 三行代码）、Agent 三工具编排、空闲时段算法单测；
- 横屏 1920×1080 视频管线照旧（build-v1-landscape + intro-factory + publish-video 双平台）。