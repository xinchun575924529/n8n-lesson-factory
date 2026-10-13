# 立项报告 · 项目 20584

## 基本信息
- **项目名（中文）**：新员工入职编排引擎（webhook 触发，横跨 HR / IAM / IT / SaaS 四系统）
- **英文原名**：Orchestrate employee onboarding via webhook across HR, IAM, IT and SaaS
- **来源**：n8n 官方模板库 https://n8n.io/workflows/20584/（fresh 候选，定选时间 2026-10-13 18:29）
- **API 拉取**：`GET https://api.n8n.io/api/workflows/templates/20584` → 200 ✅（2026-10-13 18:31 实拉成功）
- **节点数**：20 个（16 功能节点 + 4 张 stickyNote 教学便签）；research-active 里登记的 "nodeCount: 6" 是列表页口径，实际以 workflow.nodes 为准

## 用途（一句话）
外部系统（招聘 OA / 表单）POST 一条新员工资料进来，工作流按 HR → IAM → IT → SaaS 的顺序依次调四个系统接口完成入职开通，聚合结果后一次性把「完成 / 部分完成 / 失败」报告回给调用方。

## 节点清单（16 功能节点）
| # | 节点 | 类型 | 作用 |
|---|------|------|------|
| 1 | Webhook - New Hire Request | webhook v2 | POST `employee-onboard` 收新员工 payload（responseMode=responseNode） |
| 2 | Code - Validate & Normalize | code v2 | 校验 firstName/lastName/email/startDate，规整字段，内置 CONFIG（4 个目标 URL） |
| 3 | Wait - Pre HR | wait 1.1 | 等 1 秒 |
| 4 | HTTP Request - HR System | httpRequest 4.2 | POST 员工档案到 HRIS（neverError+fullResponse，continueOnFail） |
| 5 | Code - Process HR Result | code v2 | 判 2xx，提取 hrId，组装 IAM payload |
| 6 | Wait - Pre IAM | wait | 等 1 秒 |
| 7 | HTTP Request - IAM / Identity | httpRequest 4.2 | 建身份/分组/初始权限 |
| 8 | Code - Process IAM Result | code v2 | 提取 userId，组装 IT + SaaS payload |
| 9 | Wait - Pre IT | wait | 等 1 秒 |
| 10 | HTTP Request - IT Provisioning | httpRequest 4.2 | 开邮箱、设备工单、IT 账号 |
| 11 | Code - Process IT Result | code v2 | 确认 ticketId，透传 SaaS payload |
| 12 | Wait - Pre SaaS | wait | 等 1 秒 |
| 13 | HTTP Request - SaaS Apps | httpRequest 4.2 | 开通 Slack/Google Workspace/Notion/GitHub |
| 14 | Code - Build Final Status | code v2 | 聚合四系统结果 → completed/partial/failed |
| 15 | Code - Finalize Response | code v2 | 组装响应体，映射 HTTP 状态码（201/207/502） |
| 16 | Respond to Webhook | respondToWebhook 1.1 | JSON 回包 + X-Request-Id 头 |

连线是标准单线串联，无分支无错误网。

## 凭证缺口与替代方案 ⭐
**结论：零凭证、零成本，本项目是罕见的「开箱即真跑」模板。**

| 系统 | 模板默认 | 替代需求 |
|------|---------|---------|
| HR / IAM / IT / SaaS 四个 HTTP 端点 | **全部默认指向 `https://httpbin.org/post`**（公共回显服务，免费无需 key） | 不需要替代，真跑即用 |
| LLM / 第三方 API key | 无 | — |
| 回调鉴权 | webhook 无鉴权（教学场景可接受，教案里提示生产要加 HeaderAuth） | — |

亮点设计（教案卖点）：
- `allowSimulation` + `simulateStatus` 参数：调用方传 `simulateStatus: 500` 就把 HR 请求打到 `httpbin.org/status/500`，**一行参数模拟任意系统故障**，天然适合做「部分失败 → 207」的教学演示
- neverError + fullResponse + continueOnFail 三件套：任何一步挂了不断链，最后统一汇总
- HTTP 状态码语义化：全成 201 / 部分成 207 / 全灭 502

## L2 验证计划（推荐 A + B + C 全做，成本全零）
- **A 单元级**：5 个 Code 节点忠实移植单测（Validate 必填校验/邮箱正则/simulateStatus 改道；Process HR/IAM/IT 的状态判定与 payload 组装；Build Final Status 的 completed/partial/failed 三态；Finalize 的 201/207/502 映射）。预计 30+ 断言
- **B mock 全链**：保留全节点连线，4 个 HTTP 节点 mock 掉 → 场景 S1 全成功(201) / S2 HR 挂(207) / S3 必填缺失 / S4 非法邮箱 / S5 IAM+SaaS 双挂 / E1 全灭(502)。**注：本模板 B 与 C 几乎等价，因为真实端点就是 httpbin**
- **C 真跑（强烈推荐做）**：激活 webhook 真 POST httpbin.org → 四链路真 HTTP 往返 + simulateStatus=500 故障注入各跑一遍，0 元真凭证级验证

## 风险点 / 模板坑（预判）
1. **httpbin.org 可达性**：本机直连 httpbin 历史可用但偶发慢；C 真跑设 timeoutMs=20000 兜底，挂了换 `httpbingo.org` 或本地起 mock 服务（不影响 B）
2. **Wait 节点×4（各 1 秒）**：CLI 执行会真等 4 秒，可接受；压测大量并发时 wait 会持有执行
3. **`valid=false` 时不短路**：Validate 校验失败后流程**照样往下走**调四个系统（模板无 If 分支拦截）——疑似模板缺陷，L2-A 需实锤，教案可讲「如何加守卫分支」
4. **employeeId 默认 `EMP-'+Date.now()`**：同毫秒两次调用会撞号（教学可忽略）
5. webhook 无鉴权：生产需补 HeaderAuth，教案安全提示点
6. Respond to Webhook 的 responseCode 走表达式 `{{ $json.httpStatus }}`——201/207/502 动态状态码是 n8n 高级用法，B/C 要验证 respondToWebhook 真支持动态码

## 推荐路径
**A → B → C 全做**（全部零成本；C 因 httpbin 天然存在而几乎是白送的真跑）。先 A 起步，逐关汇报。