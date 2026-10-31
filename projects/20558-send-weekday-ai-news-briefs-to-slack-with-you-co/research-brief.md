# 20558 立项报告：工作日 AI 新闻晨报推送 Slack（You.com + TypeSafe Jev）

- 模板：https://n8n.io/workflows/20558/
- 来源：fresh 候选定选（2026-10-31 19:23，ou_505161df）
- 节点数：13（8 功能 + 1 触发 + 4 stickyNote）

## 项目是什么

每个工作日早 8 点，按 Config 配置的主题（AI 模型发布 / Agent 工具链 / AI 监管）：
1. You.com 搜索各主题过去一天的新闻（每主题 15 条）；
2. removeDuplicates 按 URL 去重（跨执行记忆）；
3. Jev（TypeSafe 低成本分类模型，~$0.00004/篇）一次调用问三个问题：是否报道新进展 / 是否属于该主题 / 对团队的重要度评分；
4. 过滤（三项阈值）后按主题聚合，You.com Research 写成带引用链接的简短晨报；
5. 推送 Slack 频道 #ai-news。

卖点：双层 AI 过滤（搜索 + 分类器打分）+ 去重 + 引用溯源，官方宣称每天成本 $0.01~0.04。教学点：removeDuplicates 跨执行记忆、Jev noul/score 评估范式、summarize 分组聚合、Set 节点 IIFE 格式化。

## 节点清单

| # | 节点 | 类型 | 作用 |
|---|------|------|------|
| 1 | Every weekday at 8am | scheduleTrigger 1.3 | 周一至周五 08:00 |
| 2 | Config | set | topics/team/caresAbout/materialityThreshold(1.3) |
| 3 | One item per topic | splitOut | 主题拆条 |
| 4 | You.com: search the latest news | @youdotcom-oss 社区节点 | 搜索（count15, freshness=day） |
| 5 | One item per article | splitOut | 文章拆条 |
| 6 | Prepare article | set | 字段整形 + urlKey（去 query/hash） |
| 7 | Skip articles already seen | removeDuplicates v2 | 跨执行去重 |
| 8 | Jev: judge each article | @typesafe-ai 社区节点 | 三问评估（noul×2 + score） |
| 9 | Keep only material news | filter | 0.8/0.8/threshold 阈值过滤 |
| 10 | Material article details | set | 精简字段 |
| 11 | Group articles by topic | summarize | 按主题聚合 title/url |
| 12 | You.com: research what changed | @youdotcom-oss | research 写简报（effort=lite） |
| 13 | Format Slack brief | set | IIFE 格式化 markdown→Slack mrkdwn + 引用编号转链接 |
| 14 | Post brief to Slack | slack 2.7 | 发频道 |

## 凭证缺口与替代方案（能免费不付费）

| 原凭证 | 是否付费 | 替代方案 |
|--------|----------|----------|
| You.com API（search + research 两处） | 付费 | **RSS/免费新闻源 + HTTP Request**（如 Google News RSS / HackerNews Algolia API 免费）替代 search；research 写简报警 **DeepSeek**（本厂标配）替代 |
| TypeSafe Jev | 付费（极便宜） | **DeepSeek 一次调用输出三问 JSON**（reports_new_development/about_topic 转 0-1 置信度 + materiality 0-2 分），prompt 直接复刻模板里的 questionsJson |
| Slack | 免费但需建 app | **飞书群推送**（本厂 tenant token 直发，现成通道） |

结论：**0 元可跑全链**：RSS 免费源 + DeepSeek×2 + 飞书推送。社区节点 @youdotcom-oss / @typesafe-ai 本机未装，mock 处理。

## L2 验证计划

- **A 单元级**：移植 Config / Prepare article / Format Slack brief（IIFE）/ filter 条件 / summarize 配置为单元测试流；重点断言 urlKey 剥离、IIFE 引用编号→链接转换、阈值边界（0.79/0.8/1.29/1.3）。
- **B mock 全链**：保留全节点全连线，You.com/Jev/Slack 换 mock（预制 2 主题×5 文章样本，含重复 URL、常青文、跨主题噪声），验证去重 + 过滤 + 聚合 + 格式化全链。
- **C 免费真跑**：Google News RSS（HTTP Request）+ DeepSeek 评估 + DeepSeek 写简报 + 飞书群推送，真跑一次出晨报。
- 推荐：**A + B + C 全做**（模板小、替代链现成，C 成本为零）。

## 风险点

1. removeDuplicates 跨执行记忆：测试会污染已见历史，模板自带警告（跑真量前要 Clear Deduplication History）——教学坑点。
2. Jev 输出结构 `answers.xxx.noul/score` 是 TypeSafe 私有格式，DeepSeek 替身需自行对齐字段名，filter 表达式里的可选链 `?.` 在 n8n 表达式里兼容性要验证。
3. `Prepare article` 里 `$('One item per topic').item.json.topic` 回捞上游 item——splitOut 后的 item 对齐关系，mock 时易错（老坑：httpRequest 全量替换 item 后下游必须回捞）。
4. Format Slack brief 的 IIFE 正则（`**`→`*`、`[[1,2]]`→链接）转义复杂，移植时易碎，A 关重点覆盖。
5. Google News RSS 替代后返回结构与 You.com（results.web 数组）不同，B/C 的 splitOut 字段路径要适配。
6. scheduleTrigger 用实例时区——教学点（settings.timezone=Asia/Shanghai）。