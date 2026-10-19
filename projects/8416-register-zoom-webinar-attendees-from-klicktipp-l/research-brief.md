# 立项报告 · 项目 8416（Register Zoom webinar attendees from KlickTipp landing page forms）

- 来源：https://n8n.io/workflows/8416/ （官方模板库，id 8416）
- 定选时间：2026-10-19 19:56（fresh 候选，由飞书群定选）
- 模板节点数：3 功能节点 + 5 StickyNote（httpRequest / switch / stickyNote）
- 状态：research（立项报告已推 GitHub 工厂库）

## 1. 项目是什么

**KlickTipp 落地页表单 → 自动注册 Zoom 网络研讨会 → 回写参会链接到 KlickTipp 联系人档案** 的营销自动化漏斗：

1. 访客在 KlickTipp 落地页填表（含「选哪个研讨会」下拉框）；
2. KlickTipp 出站 webhook 触发 n8n（`KlickTipp Trigger`，社区节点）；
3. `Switch` 按表单字段 `CustomField219989` 的值分流（模板自带两条：「E-Mail Zustellung für Anfänger 新手场」/「E-Mail Zustellung für Experten 专家场」）；
4. 各自走 `Register for webinar A/B`（httpRequest → Zoom API `POST /v2/webinars/{id}/registrants`，OAuth2）拿到 `join_url` 和 `start_time`；
5. 各自走 KlickTipp `subscriber/subscribe` 节点：把 join_url 写入自定义字段、把「未来最近一场 occurrence 的开始时间」转成 Unix 秒写入另一个字段、并打上报名 tag（listId/tagId 一次调用完成，保证营销活动在数据就绪后才启动）。

**典型卖点**：零手工搬运、按选题动态分流、可扩展到更多研讨会场次；字段回写与打 tag 同调用，规避「活动先发、数据后到」的竞态。

## 2. 节点清单（8 个）

| 节点 | 类型 | 说明 |
|---|---|---|
| KlickTipp Trigger | n8n-nodes-klicktipp.klicktippTrigger | ⚠️社区节点，webhook path=zoom_webinar_registration |
| Switch | switch v3.2 | 按 CustomField219989 二分（strict 字符串 equals） |
| Register for webinar A | httpRequest v4.2 | Zoom OAuth2，webinarId 89062978982（示例） |
| Register for webinar B | httpRequest v4.2 | Zoom OAuth2，webinarId 84861299706（示例） |
| Add "Anfänger" webinar data to contact | n8n-nodes-klicktipp.klicktipp v3 | ⚠️社区节点，subscribe+字段+tag 一体 |
| Add "Experten" webinar data to contact | 同上 | 另一 tag/list |
| StickyNote ×5 | stickyNote | 1 个超长社区节点免责+设置说明 + 4 个分区标题 |

模板自带 pinData（KlickTipp Trigger 有一条测试数据）。

## 3. 凭证缺口与免费替代方案（能免费不付费）

| 模板需要 | 付费？ | 替代方案 |
|---|---|---|
| **KlickTipp 账号**（API 凭证 + 社区节点） | 付费 SaaS（14 天试用） | ❌ 不装社区节点。**Trigger→webhook 节点**（模拟落地页提交）；**两个 KlickTipp 写回节点→本地 JSON/多维表（飞书免费）或 Google Sheets 替代**，保留「字段+tag 一次写入」的教学逻辑 |
| **Zoom OAuth2**（webinar:write:registrant） | Zoom Pro 起付费，且需 webinar 许可 | **httpRequest 打到本地 mock**（n8n webhook/Code 节点返回仿真 join_url/occurrences）；或免费方案用 Zoom 普通 meeting API（会议注册也支持，免费账号可开 registration meeting）——推荐 mock，零成本零风控 |
| Switch 节点 | 免费 | 原样保留（v3.2 strict equals 本身有教学点） |

**结论：三关全部可以做到 0 元。** A 单元级纯 JS 移植；B mock 保留全节点全连线；C 真跑用「webhook 触发 + mock Zoom 响应 + 本地 JSON 档案」替身链，DeepSeek 都用不上。

## 4. L2 验证计划建议

- **A 单元级（推荐先做，成本低）**：模板核心 JS 逻辑其实很少——①Switch 条件表达式 `{{$json.CustomField219989}}` 求值；②KlickTipp 节点里那段「从 occurrences 取未来最近一场 → Unix 秒」的内联表达式（**模板最有技术含量的点，值得逐行单测**：occurrences 为空、全部已过期、含 deleted 态、非循环 webinar 回退 start_time 四种分支）。预计 15~20 断言。
- **B mock 全链**：替换 KlickTipp Trigger→webhook 测试触发；Zoom httpRequest→mock endpoint（本机 n8n webhook 返回固定 registrant 响应）；KlickTipp 写回→Code/JSON 落盘断言（join_url 写对字段、tag 打对、Unix 秒正确）。场景：S1 新手场、S2 专家场、S3 表单值不在两个分支（Switch 无输出=静默丢弃，⚠️这本身就是模板坑，值得做成断言）。
- **C 免费真跑**：本地 n8n 起替身链 E2E 真跑一遍（webhook→Switch→mock Zoom→写本地 JSON 档案），零付费。若老板想要真 Zoom/KlickTipp 真跑 = 需要付费账号，不建议，mock 已覆盖教学点。

**推荐路径：A + B + C 全做**（本模板极小，三关成本都低；C 用替身链 0 元）。

## 5. 风险点 / 模板坑预判

1. **社区节点依赖**：klicktippTrigger/klicktipp 是社区节点，本机未装 → 替身化是必选项不是可选项；教学片需讲清「社区节点装不上怎么办」。
2. **Switch 静默丢弃**：表单值不匹配任何分支时无输出无报错，下游全不执行（17522 已踩过同类「上游 0 项下游静默」坑）。
3. **occurrences 内联表达式复杂**：单行表达式里嵌 filter/sort/回退，写错不报错只返回 NaN（Math.floor(undefined)）→ 单测必须覆盖。
4. **Zoom 审批模式**：模板注释明确「manual approval 的 webinar 不返回 join_url，要用 automatic approval」——教学点。
5. **字段 ID 硬编码**：field219990/219991、listId、tagId、webinarId 全是模板作者账号的，用户必须替换——教学片要做「替换清单」。
6. **语言**：模板注释/分支名是德语（E-Mail Zustellung für Anfänger/Experten），教学片需中文化解释。

## 6. 待拍板

1. L2 路径：建议 A+B+C 三关全做（C 用免费替身链），是否同意？
2. 课程定位：这条偏「营销自动化/CRM 集成」向，与既有 lesson 风格一致，默认继续标准 L3（GitHub 课程库+Pages）+L4（获客视频双平台）流水线？