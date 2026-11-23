# 立项报告 · 模板 21826 Triage website form enquiries with OpenAI and Google Sheets

- 来源：https://n8n.io/workflows/21826/ （官方模板库 fresh 候选，2026-11-23 定选 B·立即研发）
- 项目号：21826（模板号）；节点数 40（31 功能节点 + 9 sticky 注释）
- 中文名（建议）：网站表单询盘智能分拣（OpenAI+Google Sheets 版）

## 一、项目是什么
网站联系表单的「智能前台」：表单 POST 到 webhook → 邮箱校验/蜜罐反机器人/重复去重 → AI Agent（带工具调用子工作流取分类清单）给出 分类+置信度+紧急度+摘要+回复草稿 → 阈值校验后四路分流：
1. **urgent/normal**（正常询盘）→ 追加 Google Sheets「Enquiries」+ 紧急件发 Gmail 告警（可选 Slack）+ 可选存 Gmail 回复草稿
2. **review**（不确定/AI 出错）→ Sheets「Review」+ Gmail 提醒人工复核
3. **spam** → Sheets「Spam」（垃圾判定要求更高置信度 0.8）
4. **AI 步骤失败 / 写表失败** → Sheets「Errors」+ Gmail 失败告警

卖点：结构化输出解析器（outputParserStructured）+ 分类白名单校验（AI 只能选清单内 id）+ 蜜罐+去重的反垃圾三板斧 + 错误网兜底（任何一步失败都落 Errors 表并发邮件）。这是典型「小企业询盘分拣」场景，与已上线 lesson-02 TG 客服分流同属分流家族但入口是表单、多了反垃圾维度。

## 二、节点清单（31 功能节点）
- 入口：webhook(When Form Enquiry Arrives, POST /lead-triage) + 3×respondToWebhook（200/400/静默200）
- 预处理：Set Triage Settings(code) → Normalize Form Fields(code) → Route by Form Check(switch)
- 去重+分类清单：removeDuplicates(historySize 10000) + executeWorkflow(Load Allowed Categories，子流=同工作流 executeWorkflowTrigger + Return Category List code) + merge(chooseBranch)
- AI 段：langchain.agent(Categorise Enquiry Agent, maxIterations 4) + lmChatOpenAi(gpt-4o-mini, temp 0) + toolWorkflow(Get Allowed Categories) + outputParserStructured + Check Category Is Allowed(code)
- 分流：If AI Step Failed + Route by Outcome(switch urgent/normal/review/spam)
- 落地：4×googleSheets(append: Enquiries/Review/Spam/Errors) + 3×gmail(紧急告警/复核请求/失败告警) + If+slack(可选) + If+gmail 草稿(可选) + set(Prepare Failure Alert)

## 三、凭证缺口与替代方案（能免费不付费）
| 模板要求 | 替代 | 结论 |
|---|---|---|
| OpenAI(gpt-4o-mini) | **DeepSeek deepseek-chat**（密钥库 state\deepseek-key.json，余额已回正 ¥9.80） | ✅ 零新增成本；lmChatOpenAi 改 baseURL 或换 deepseek 节点 |
| Google Sheets ×4 tab | **本地 JSON 台账**（state\21826-c-data\{enquiries,review,spam,errors}.json，L2 惯例）或飞书多维表格 | ✅ 免费替代成熟（17522/8270 同款做法） |
| Gmail ×3 + 草稿 | **飞书群消息**（教案制作组群，factory-sync.py feishu_send 现成） | ✅ 免费；草稿功能直接砍掉（默认 false 本就不启用） |
| Slack（可选） | 不启用（模板默认 slack_alerts:false） | ✅ 不涉及 |
| 真实网站表单 | curl/mock POST 触发 webhook | ✅ 零成本 |

**结论：本项目可 100% 免费跑通，无任何硬付费环节。**

## 四、L2 验证计划（推荐 A → B → C 三段全做）
- **A 单元级（先做）**：4 个 Code 节点（Set Settings/Normalize/Check Category/Return Category List）+ 去重逻辑 忠实移植断言。重点测 Normalize 的路由判定（invalid/bot/ok 三路）与 Check Category 的 7 种 outcome（aiError/未知分类/无置信度/低置信/疑似垃圾/垃圾/正常+紧急升级）。
- **B mock 全链**：DeepSeek 打 mock（固定返回结构化 JSON），Sheets→本地 JSON，Gmail→写文件，跑场景：正常询盘/紧急件/垃圾邮件/低置信进 Review/AI 失败/重复提交被去重/蜜罐机器人/坏邮箱 400。
- **C 免费真跑**：DeepSeek 真调（单次成本忽略不计）+ 本地 JSON 台账 + 飞书群真推送，全链 E2E。
- **推荐**：本模板业务逻辑集中在 4 个 Code 节点与阈值分流，**建议 A+B 必做，C 做免费版**（DeepSeek 真调+飞书真推）。

## 五、风险点（模板坑预判）
1. **agent+toolWorkflow 自引用子流**（workflowId=$workflow.id）依赖本工作流内 executeWorkflowTrigger，CLI 单测时需拆开；mock 阶段 toolWorkflow 直接替换为固定分类清单。
2. **Merge chooseBranch waitForAll**：executeWorkflow 分支若空返回会断链（17522 已踩过同类坑：上游 0 项下游不执行），mock 要保证子流恒有输出。
3. **removeDuplicates 跨执行去重**依赖 n8n 内部存储，CLI 多次 execute 之间状态隔离要注意（historySize 10000）。
4. **outputParserStructured + DeepSeek**：deepseek-chat 对 JSON schema 约束遵守度需实测，失败时走 continueErrorOutput→Errors 链路（模板已设计兜底，正好当场景测）。
5. Check Category 节点用 `$('Merge Enquiry with Categories').all()` 回捞上游 + pairedItem 对齐，item 顺序错位会导致错配——A 阶段重点断言。
6. 阈值参数在 Set Triage Settings（min_confidence 0.6 / min_spam_confidence 0.8），教案需讲清两阈值的语义差。

## 六、教案化价值
- 与 lesson-02（TG 客服分流）形成「分流家族」对照课：入口不同（webhook 表单 vs TG）、本课多反垃圾三板斧+结构化输出解析器+白名单校验，是 LangChain agent 工具调用（toolWorkflow 自引用）的入门好例子。
- 节点数适中（31）、场景接地气（每个有网站的小企业都需要），适合做中阶课。