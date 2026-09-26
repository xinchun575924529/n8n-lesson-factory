# 立项报告 · 19710 Generate structured research reports with OpenAI, Wikipedia, Google Sheets, and Slack

- 模板 ID：19710 ｜ 来源：https://n8n.io/workflows/19710/
- 定选时间：2026-09-26 11:26（老板在飞书教案制作组群定选，source=fresh）
- 节点数：12 功能节点（另有 17 张 sticky note 教学注释，天然适合做课程）
- 定选时的 nodeTypes：webhook / set / if / openAi×2 / code×4 / httpRequest×2 / splitInBatches / merge / googleSheets / slack / respondToWebhook

## 项目是什么

**AI 个人研究助理**：Webhook 收一个研究主题（`{"topic": "..."}`）→ 校验 → OpenAI 生成 5 个搜索查询 → 逐条查 Wikipedia API → 抓取词条正文 → 合并 → OpenAI 综合分析成结构化研究报告（8 个固定章节：Executive Summary / Key Findings / Important Facts / Benefits / Challenges / Latest Trends / Future Outlook / Source References）→ Code 节点按 `###` 标题切成 JSON → 存档 Google Sheets（appendOrUpdate，按 Topic 匹配）→ Slack 发完成通知 → Webhook 返回完整结构化报告。

用途卖点：把「人工上网查资料写调研」变成一条自动化流水线；教学价值高（webhook 双向响应、splitInBatches 循环、merge 聚合、LLM 两阶段用法、正则切片）。

## 节点清单（12）

| # | 节点 | 类型 | 作用 |
|---|------|------|------|
| 1 | Webhook | webhook | POST /research-assistant，responseNode 模式 |
| 2 | Receive Research Topic | set | 提取 body.topic |
| 3 | Validate Research Topic | if | topic 非空校验（空则静默断链——**坑#1**） |
| 4 | z（命名烂——**坑#2**） | langchain.openAi | 生成 5 个搜索查询（gpt-4o-mini） |
| 5 | Parse Search Queries | code | 剥 ```json 围栏后 JSON.parse（裸奔无 try——**坑#3**） |
| 6 | Search Web | httpRequest | Wikipedia search API（srlimit=5） |
| 7 | Prepare Search Results | code | 清洗 snippet HTML、拼词条 URL |
| 8 | Process Search Results | splitInBatches | 逐条循环（默认 batch=1，5 查询×5 结果=最多 25 轮） |
| 9 | Extract Website Content | httpRequest | Wikipedia extracts API 取正文 |
| 10 | Clean Website Content | code | 用 `$('Process Search Results').item` 回环配对（**坑#4**：依赖 splitInBatches 上下文，改结构即断） |
| 11 | Merge Research Data | merge | 默认 append 聚合（参数为空——**坑#5**：merge 空参行为随版本变） |
| 12 | AI Research Engine | langchain.openAi | 综合分析成 8 章节报告（gpt-4o-mini） |
| 13 | Research Report Formatter | code | 正则按 `###` 切 8 段（**坑#6**：LLM 不输出 `###` 前缀则全空，且无兜底） |
| 14 | Update row in sheet | googleSheets | appendOrUpdate 按 Topic 匹配（**坑#7**：同 Topic 会覆盖旧报告） |
| 15 | Send a message | slack | 完成通知（**坑#8**：通知文不带报告摘要，纯打卡） |
| 16 | Return Research Response | respondToWebhook | 返回最后一个 item（**坑#9**：loop 完成后 respondToWebhook 的回连线指向 splitInBatches 主输出再循环，结构怪异需实跑验证） |

（编号含全部功能节点；sticky note 17 张不计）

## 凭证缺口与替代方案（能免费不付费）

| 模板需求 | 缺口 | 替代方案（已定调） |
|---|---|---|
| OpenAI API ×2（gpt-4o-mini） | 无 OpenAI key，付费 | **DeepSeek deepseek-chat**（直连，余额 9.9 元，教案组老规矩）；langchain.openAi 节点改 baseURL=https://api.deepseek.com + DeepSeek key，或换 httpRequest 直连 |
| Wikipedia API | 无凭证、免费、公开 | **保留真调**（英文站；本机直连可达，不需要代理——验证时实测确认，不通则换 zh.wikipedia 或 mock） |
| Google Sheets OAuth | 无 Google 账号凭证 | **本地 JSON 存档**（state\19710-data\reports.json）或飞书多维表格；C 真跑阶段由客户自选 |
| Slack OAuth + 频道 | 无 Slack 工作区 | **飞书群通知**（N8N教案 bot tenant token 直发，现成） |

结论：**全链可免费跑通**——DeepSeek 是唯一的边际成本（一次真跑约几分钱），Wikipedia 免费公开，Sheets/Slack 均有零成本替代。

## L2 验证计划（推荐 A+B+C 全做，同 17522 标准）

- **A 单元级（推荐先行）**：4 个 Code 节点（Parse Search Queries / Prepare Search Results / Clean Website Content / Research Report Formatter）忠实移植 + 断言单测。重点打坑：#3 裸 JSON.parse、#6 `###` 正则切片空兜底、#4 item 回环配对。预估 25~30 断言。
- **B mock 全链**：保留模板结构，OpenAI→mock 固定返回、Wikipedia→mock 响应、Sheets→本地 JSON、Slack→记录式 mock；场景：正常流 / 空 topic / LLM 返回带围栏 / LLM 输出无 `###` 标题 / Wikipedia 零结果。预估 5~6 场景。
- **C 真跑（替换版）**：DeepSeek 真调 ×2 + Wikipedia 真调 + 本地 JSON 存档 + 飞书群通知，webhook 发真 topic（如 "honey production"）回收结构化报告。成本≈0。

推荐路径：**A → B → C 全做**。A 先行因 4 个 Code 节点是模板全部业务逻辑，坑最密；B 验结构与连线；C 证明免费替代链真能出报告。

## 风险点

1. 坑#6（正则切章节）是最大教学点也是最大脆弱点：DeepSeek 对 `###` 标题的遵循度需实测，可能要在 prompt 里强化「必须用 ### 标题」。
2. Wikipedia 英文站在本机直连通常可达，但若抽风需降级 zh.wikipedia 或挂进程级代理（**严禁系统代理**，铁律）。
3. loop 内 25 轮 HTTP + 最终长 prompt，DeepSeek 上下文窗口（64K）够用但需控制 extract 截断（模板没截断——**坑#10**：词条正文可能几万字直接灌进 prompt）。
4. webhook responseNode 模式 + splitInBatches 回环的组合在 n8n 2.x 有版本行为差异，B 阶段重点验证「webhook 调用方能拿到完整报告」。
5. Sheets appendOrUpdate 语义=同 Topic 覆盖，教学时要讲清与 append 的区别。

## 下一步

等老板拍板 L2 路径（建议 A 起步）。A 通过后再依次 B、C，每关出报告送审。