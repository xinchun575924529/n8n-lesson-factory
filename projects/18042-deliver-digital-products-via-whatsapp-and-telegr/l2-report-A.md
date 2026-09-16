# L2-A 单元级验证报告 · 18042 Sales PDF bot

- 时间：2026-09-16 21:2x (Asia/Shanghai)
- 工作流：`L2Test180420001`「L2A-UnitTest-18042-SalesPDFBot」（generate: scripts\build-l2-test-18042.py，CLI AppData n8n 2.33.3 execute）
- 结果：**27/27 全部通过**

## 覆盖范围（忠实移植）

| 单元 | 断言数 | 要点 |
|---|---|---|
| Extract WhatsApp Message (Code) | 4 | phone trim / message lower·trim / 状态回执无 messages 不炸 / 畸形 body 不炸 |
| Extract Telegram Message (Code) | 4 | chat_id 数字→字符串、first_name 缺省 'friend'、无 text 不炸、畸形 body 不炸 |
| Extract Stripe Payment Details (Code) | 6 | 正常成交解析、amount/100、币种大写、非 completed 事件只回 skip、无 phone/无 data 兜底 |
| IF 分支逻辑 ×4 | 10 | WA/TG 有效性（isNotEmpty）、渠道识别（equals telegram）、Payment Validity 路由如实复刻、Pending 双路（无记录→首次入库 / sent_link→催单） |
| Set Build Payment Reminder | 3 | 字段映射、ISO timestamp、不带 first_name |

## 🚨 本阶段确认/新发现的模板坑（教案卖点）

1. **【重磅·新】Check Payment Validity 连线接反**：skip=true（无效付款/无手机号）的**真分支**连到「Retrieve Client From Sheets（正常交付链）」，假分支才接「Send Fallback Notification」。按模板字面接线，无效付款会走进交付链、有效付款被当无效——交付逻辑整体反转。断言 IF7/IF8 已如实复刻此语义。
2. **【新】Retrieve Client From Sheets 无 alwaysOutputData**：查无买家时输出 0 项，下游「Determine Communication Channel」静默断链，买家永远收不到货且无告警（对照：Retrieve Unpaid Clients 恰好开了 alwaysOutputData）。这正是 17522 踩过的"上游 0 项输出断链"同款坑。
3. lookupValue `=={{ $json.phone }}` 带多余 `==` 前缀（Sheets 筛选失配嫌疑，B 阶段验证）。
4. Stripe webhook 无签名校验，任何人 POST 伪造 checkout.session.completed 即可白嫖发货。
5. 催单 webhook（GET 验证）与 WhatsApp intake（POST 事件）共用 path=`whatsapp-verify`，靠 method 区分，配置时极易混淆。
6. 交付匹配只靠 phone 单字段：TG 客户登记时 phone=''，除非 Stripe checkout 页强制填手机号且客户填一致，否则永远查不到买家 → 叠加坑#2 直接静默失败。

## 下一步

L2-B mock 全链：webhook×4 → code/if → 本地 JSON 台账替 Sheets → mock 发送节点 → respondToWebhook，场景 S1-S6+E1（见 research-brief），其中复现#1/#2 的断链/反转现场作为教学对照组。