# 01 · 入口与安全：Telegram Trigger、白名单、反爬

## 三种入口形态
- **telegramTrigger（本模板）**：n8n 以长轮询 webhook 模式接 Telegram；n8n 必须可被公网访问（或走云入口反代）。
- 手动 Webhook 节点：你自建 `/webhook/xxx` 后用 Telegram `setWebhook` 指向它（2682OL 交付同款）。
- 命令工具：TG BotFather 只是建 bot；**入口行为全在 n8n 侧**。

## 白名单的正确姿势（含本模板 🔴 坑#2）
模板的 AllowList 是一个 `set` 节点，把 `<chat id>` 存成 **string**；`If1` 用 `from.id == allow` 比对。

### 🚨 坑：模板靠「宽松校验」侥幸跑通，你一动它就炸
- Telegram 的 `message.from.id` 在 webhook JSON 里是 **number**；模板却把 allow 存成 **string**（`"<chat id>"`）。
- 它今天能跑，只因为 If1 里一个不显眼的开关：`looseTypeValidation = true`（宽松类型校验）。
- **亲手实测（2026-09-19 本机 n8n 2.33.3，两条对照工作流）**：

| 配置 | 输入：`from_id=114514`(number) vs `allow="114514"`(string) | 结果 |
|---|---|---|
| `looseTypeValidation: true`（模板现状） | 类型自动放宽 | ✅ 放行（`PASS`） |
| `looseTypeValidation: false` | 严格类型校验 | ❌ **节点抛错**：`Wrong type: '114514' is a string but was expecting a number`，整条执行 error 终止 |

- ⚠️ 注意第二行**不是**「被拦截、静默不回」，是**直接报错**——用户发来消息，机器人执行红叉，连「我没权限」都不会回。这比静默更糟。
- **什么时候会炸**：在 UI 里重选字段、升级 If 节点版本、把这套逻辑复制到自己的新工作流、或者让别人帮你「优化」一下。**它一直在等一个不小心。**
- **修复**（二选一，推荐第 1 个）：
  1. AllowList 把值存成 **number**（字段类型选 Number，或值直接写 `114514` 不带引号）——从此不依赖任何开关；
  2. 保留 string，但**显式**确认 If1 的 `looseTypeValidation = true`（别让它变成「隐形依赖」）。
- **L2A 实锤证据**：白名单 `114514`（数字）通过、`999999` 拦截 ✅。

### 多用户白名单（交付版推荐）
用 `{{ $('Listen for incoming events').item.json.message.from.id }}` 与数组 `allow` 做 `contains` 比较：
```js
// Code 节点（推荐）替代硬编码 set + if
const me = $input.first().json.message.from.id;
const allow = [114514, 222222];   // 你 + 家人/同事
if (!allow.includes(me)) return []; // 直接丢弃：不给陌生人任何信号
return $input.all();
```
> 返回空数组 = 完全静默。模板用 If 的 false 分支什么都不接，效果一致。

## webhook 部署玄学（⚪ 环境坑，本机反复踩）
- n8n 2.33 的 `webhookTrigger` 节点，**节点名字必须字面等于 `Webhook`**、`responseMode` 用 `lastNode`、`parameters` 里**不能有 `options: {}`** ——三者缺一，路由注册不上，Express 直接 404 `Cannot POST`。
- `publish:workflow` **第一次只登记版本**，要**重启一次 n8n 计划任务**（或停-起）路由才真正挂上。
- 刚重启完 n8n，webhook 路由是先于 DB ready 挂上的——此时 POST 会拿 **503 "Database is not ready"**（不是路径错）。**healthz 200 后再等 20-30 秒**再测。
- 排查顺序：sqlite `webhook_entity` 表有行 ≠ 路由生效；看 stdout 日志 `Activated workflow` 才是金标准。

## 影子流量与 429/452（交接常识）
- 公网 bot 会被扫：401/404 正常回包，**451 = 地区政策，429 = 你太快，452 是 TG 自定义限流**。
- 治 429/452 五板斧（2682OL 实战沉淀）：**退避 + 抖动、合流去重、入口限速、拥塞兜底文案、夜间静默窗**。
- 反爬不是本课教学重点，但**上线前请把 429 兜底写好**，否则高峰期用户收到"死亡沉默"。