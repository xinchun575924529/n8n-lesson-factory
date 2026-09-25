# 19457 立项报告：每日 AI 市场早报（Telegram / Discord / Postgres）

- 来源：https://n8n.io/workflows/19457/ （官方模板，fresh 批次，2026-09-25 定选 by 老板）
- 更新时间新鲜（2026-09-19 打标），质量上乘：5 数据源归一化 + 健康度检查 + AI JSON 输出 schema 校验 + 三路投递，工程化程度高，教学价值好。

## 用途
工作日 07:45 定时跑：拉取 5 个金融数据源 → 每个源独立 Code 节点归一化（ok/error/empty/invalid 四态 + 错误消毒）→ 5 路 merge → 汇总健康度喂给 AI Agent 生成结构化英文市场早报（market_regime/assets/events_today/top_news/drivers/opportunities/watch_next）→ JSON schema 校验 → 三路投递：Telegram 消息、Discord embed、Postgres 入库（public.briefings 表）。

## 节点清单（17 功能节点 + 8 便签）
1. scheduleTrigger `When Weekdays at 7:45 AM`（cron `45 7 * * 1-5`）
2. set `Setup Workflow Configuration`（report_timezone=Europe/Berlin、model_provider=openai、model_name=gpt-5.6-luna）
3. httpRequest ×5：Twelve Data（K线7标的）、CoinGecko（BTC/ETH）、FRED（美10Y国债DGS10）、QuantGist（宏观日历）、Marketaux（财经新闻）
4. code ×5：Normalize * Output（同一套错误消毒 sanitizeError + 四态状态机，几乎同构）
5. merge `Merge Source Data`（5 输入）
6. code `Prepare Data for AI Model`（汇总+source health）
7. agent `AI Market Briefing Agent`（提示词约 2500 字英文，纪律性强：禁止编造、因果谨慎词）
8. lmChatOpenAi `OpenAI Chat Model GPT-5.6 Luna` ⚠️**假模型**
9. code `Validate AI Output`（JSON 解析+market_regime 枚举校验+字段兜底）
10. code `Build Telegram Message` → telegram `Send to Telegram`
11. code `Create Database Insert Query` → postgres `Insert into Postgres`
12. code `Build Discord Embed` → discord `Send to Discord`

## 凭证缺口与替代方案（能免费不付费）
| 原凭证 | 性质 | 替代方案 |
|---|---|---|
| OpenAI gpt-5.6-luna | ⚠️不存在的假模型，必换 | **DeepSeek-chat**（现成 key，state/deepseek-key.json），提示词原样兼容 |
| Twelve Data API key | 免费注册即得（8 req/min 足够1标的批量查） | 免费自建 ✅ |
| CoinGecko header auth | 免费 demo key；公开端点其实免 key | 免 key 直接去鉴权 ✅ |
| FRED API key | 免费注册即得 | 免费自建 ✅ |
| Marketaux API key | 免费层 100 req/天 | 免费自建 ✅ |
| **QuantGist API** | ⚠️小众付费服务，**唯一硬缺口** | 替代：FRED 已覆盖宏观日历大头，或 mock/删此源降 4 源；推荐 L2 阶段 mock 替换 |
| Telegram Bot | 免费 BotFather | 可用现成 @s2682ol_notify_bot（296795 资产）或新建免费 bot ✅（⚠️本机连 TG 需 WARP） |
| Discord webhook | 免费 | 自建测试服务器 webhook ✅ |
| Postgres | 需数据库 | 替代：免费 Supabase/neon 云 PG，或验证阶段改写 json 文件/sqlite；推荐 L2 用文件落盘替代 |

## L2 验证计划（推荐 A→B，C 视拍板）
- **A 单元级（免费，先做）**：忠实移植 5 个 Normalize Code 节点 + Validate AI Output + Prepare Data，用构造样本（含 error/empty/invalid 各态）跑断言——同 lesson-01 的 31 断言模式，预计 30+ 断言。
- **B mock 全流程（低成本）**：5 数据源全部 mock 返回，DeepSeek 真调生成早报，校验→格式化→落盘文件（替代 TG/Discord/PG 投递）。验证链路完整性。
- **C 真跑（可选拍板）**：4 个免费源真注册 key 真跑 + QuantGist mock + 真发 Telegram/Discord + PG 云免费实例。需 WARP（TG）、约 15 分钟注册 4 个 key。
- **推荐路径：A + B**（B 里 DeepSeek 真调=AI 核心环节已真；C 的真源对课程增量价值有限，可留作 L3 课程练习）。

## 风险点
1. **gpt-5.6-luna 假模型**——模板作者未来占位，必须替换 DeepSeek，提示词要求"只返回 JSON"，DeepSeek 需验证 JSON 稳定性（已有 lesson-05 经验）。
2. **QuantGist 是唯一付费源**——课程设计需明确标注"可裁剪源"。
3. **Telegram 本机需 WARP**——生产部署走云上 ECS（新加坡/上海均可直连 TG）。
4. five normalize 节点同构冗余——课程可讲"模板工程化冗余 vs DRY"取舍。
5. Marketaux/DGS10 在周末/假日无新数据——empty 态处理是模板亮点，正好教学。
6. FRED/Marketaux 注册需邮箱——建议用老板常用邮箱，key 管理走 state/。

## 状态机
backlog → research ✅（本报告）→ lesson（待 L2 审过）