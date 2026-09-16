# 立项报告 · 18042 Deliver digital products via WhatsApp and Telegram after Stripe payment

- **项目名（中文）**：收款后自动发货机：Stripe 收款→WhatsApp/Telegram 秒发数字产品
- **来源**：https://n8n.io/workflows/18042/ （模板 API 200，nodes 在 workflow.nodes 内，9 功能节点 + 11 便签）
- **用途**：海外数字产品售卖自动交付机器人。客户从 WhatsApp 或 Telegram 发起咨询 → 工作流记录客户到 Google Sheets → 回复 Stripe 付款链接 → Stripe 付款成功 webhook 触发 → 按客户手机号查表、识别来源渠道 → 通过原渠道回发 PDF 下载链接。另有未付款提醒链路（查未付款客户→WhatsApp 催单）和无效付款兜底（发人工处理提示）。

## 节点清单（9 功能节点 + 11 便签注释）

| # | 节点 | 类型 | 作用 |
|---|------|------|------|
| 1 | When WhatsApp Message Received | webhook | 收 WhatsApp 云 API 事件（path=whatsapp-verify, POST） |
| 2 | When Telegram Message Received | webhook | 收 Telegram webhook（path=telegram-incoming） |
| 3 | When Stripe Payment Posted | webhook | 收 Stripe event（path=stripe-payment） |
| 4 | When Payment Reminder Triggered | webhook(v2.1) | 催单/验证回执 (应答 hub.challenge) |
| 5 | Extract WhatsApp Message / Extract Telegram Message / Extract Stripe Payment Details | code ×3 | 解析三路 payload（WA: phone+message；TG: chat_id+first_name；Stripe: checkout.session.completed→phone/amount） |
| 6 | Check … Validity ×3 / Determine Communication Channel / Check Payment Status Pending | if ×5 | 三路有效性、渠道识别、催单状态分支 |
| 7 | Add WA/TG Client to Sheets、Retrieve Client From Sheets、Retrieve Unpaid Clients | googleSheets ×4 | 客户登记表读写 |
| 8 | Send WA Payment Link、Deliver PDF via WhatsApp、Send Fallback Notification | httpRequest ×3 | 走 Facebook Graph API v19 发 WhatsApp 文本 |
| 9 | Send Telegram Payment Link、Deliver PDF via Telegram | telegram ×2 | 发 TG 付款链接/PDF 链接 |
| 10 | Acknowledge ×4 | respondToWebhook ×4 | 回 OK / hub.challenge |

## 凭证缺口与替代方案（免费优先）

| 模板需要 | 缺口评估 | 替代方案 |
|---|---|---|
| WhatsApp Cloud API（Meta 企业号 phone_number_id + access token） | ❌ 需要 Meta 开发者+企业认证，国内基本不可用 | **B 阶段 mock；C 阶段砍掉 WA 链只留 TG 链** |
| Telegram bot token | ✅ 免费，BotFather 立得（已有 2462 双 bot 经验） | 新建专用测试 bot 或复用 |
| Google Sheets OAuth2 | ⚠️ 需 Google 账号+API 授权，能用但繁琐 | **本地 JSON 台账**（state\18042-data\clients.json），与 17522/8270 同口径 |
| Stripe webhook + 付款链接 | ⚠️ 注册可用测试模式，但国内收款受限+webhook 需公网回调 | **B/C 阶段用 mock 的 checkout.session.completed payload 直接打本地 webhook**；C 真跑可用 Stripe 测试 key CLI 触发（可选，不强制） |
| PDF 下载链接 | — | 占位 URL 即可 |

**结论：本项目 L2 可全程零成本完成**（A 单测 + B mock）；C 阶段 TG 链可免费真跑（TG bot + 本地 JSON + mock Stripe payload），WA 链建议直接标注"教学演示、需企业资质"。

## L2 验证计划

- **A 单元级（推荐先做）**：3 个 Extract Code 节点 + 5 个 IF 判断逻辑 → 忠实移植断言（WA/TG/Stripe 正常+异常 payload 各组用例），目标 100% 过
- **B mock 全链**：webhook→code→if→（json 台账替代 sheets）→mock 发送节点→respondToWebhook，场景：S1 WA 咨询入表+发付款链接、S2 TG 咨询入表+发付款链接、S3 Stripe 成功付款→TG 交付、S4 Stripe 成功→WA 交付、S5 无 phone 无效付款→fallback、S6 未付款催单、E1 非 checkout.session.completed 事件跳过
- **C 真跑（免费版）**：真 TG bot 走通「咨询→付款链接→mock Stripe payload 打 webhook→TG 收到 PDF 链接」全链；WA 链 mock
- **推荐路径：A → B → C（C 只做 TG 链）**，全程零成本

## 风险点

1. **国内 Stripe 不实用**：C 阶段付款事件只能 mock，教案需明示"Stripe 测试模式/需海外主体收款"
2. **WA 链教学价值打折**：Meta 企业资质门槛高，教案里应以 TG 为主、WA 讲原理
3. **模板本身小坑已见**：
   - `Retrieve Client From Sheets` 的 lookupValue 写成了 `=={{ $json.phone }}` 带多余 `==` 前缀——Sheets 筛选会失配（疑似模板 bug，查证后收录教案坑集）
   - Stripe webhook 无签名校验（生产必须验签，教学可讲）
   - 客户匹配靠 phone 单字段，TG 用户若不留 phone 则交付失配（依赖"checkout 时填手机号"约束，脆弱）
   - 催单链路的 Reminder webhook 与 WhatsApp intake 共用 path `whatsapp-verify`（GET 验证 vs POST 事件，靠 method 区分，易混淆）
4. googleSheets 节点 typeVersion 混用 4 与 4.7、webhook 1 与 2.1——导入本机 2.33 可能有兼容性警告

## 立项信息

- 入库路径：projects/18042-deliver-digital-products-via-whatsapp-and-telegr/
- 定选：B 立即研发，2026-09-16 20:29 by ou_505161df…，来源 fresh