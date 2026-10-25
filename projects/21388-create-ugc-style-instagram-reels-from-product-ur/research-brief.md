# 立项报告 · 21388

- **项目名**: Create UGC-style Instagram Reels from product URLs with OpenAI, Sisif, and Slack
- **中文名**: 商品链接一键生成 UGC 风格竖屏广告视频
- **来源**: https://n8n.io/workflows/21388/ (官方模板, fresh 候选, 定选 2026-10-25)
- **节点**: 33 个(含 6 个便签), 功能节点 14 类
- **状态**: research (L0 立项完成)

## 用途

粘贴一个商品页 URL → 抓页面标题/描述/正文 → LLM 写出钩子+口播脚本+Instagram 文案+3 条视觉提示词 → Sisif 逐条渲染 5 秒 9:16 竖屏视频(轮询 15s×40 次) → Slack 人工三选一/拒绝 → 选中的视频创建 Instagram Reel 容器 → 轮询处理完成 → 发布 Reel。

卖点: DTC 品牌/社媒运营零拍摄批量测广告素材; 带人工审核关卡; 双轮询计数器结构(渲染轮询+IG 处理轮询)是典型工程模式。

## 节点清单(功能)

1. Product URL Form (formTrigger) / Product URL Webhook (webhook POST) — 双入口
2. Settings (set: product_url / ig_user_id / graph_version)
3. Fetch Product Page (httpRequest, text)
4. Extract Page Text (code: og 标签+正文清洗 6000 字截断)
5. Write Hook And Script (langchain chainLlm + outputParserStructured: hook/script/caption/prompts×3)
6. OpenAI Chat Model (gpt-4o-mini)
7. Split Into Variants (code: 拆 3 条 prompt)
8. Loop Over Variants (splitInBatches)
9. Create Sisif Video (httpRequest POST sisif.ai/api/videos/generate/, Bearer)
10. Wait Before Status Check (wait 15s) → Check Video Status → Is Video Ready? / Did Generation Fail?
11. Start/Track Poll Counter (set×2, attempt<40) — 渲染轮询环
12. Collect Variant (set)
13. Build Slack Message (code) → Any Variant Ready? → All Variants Failed (stopAndError)
14. Ask For Approval In Slack (slack sendAndWait, customForm 下拉)
15. Was A Variant Approved? → Pick Approved Variant (code)
16. Create Instagram Reel Container (httpRequest graph.facebook.com, facebookGraphApi 凭证)
17. Start/Track Instagram Poll + Wait 30s + Check Container Status + Is Container Finished? (attempt<40)
18. Publish Instagram Reel (httpRequest media_publish) / Instagram Processing Timed Out (stopAndError)

## 凭证缺口与替代方案(能免费不付费)

| 原凭证 | 性质 | 替代 |
|---|---|---|
| OpenAI (gpt-4o-mini) | 付费 | ✅ **DeepSeek deepseek-chat**(现成 key, prompt 原文保留, outputParser 照用) |
| Sisif API key (文生视频) | 付费(唯一硬成本) | L2-A/B mock; L2-C 免费替身=本地 ffmpeg 生成带文字占位竖屏视频(同 lesson-03 路线, 零付费验证全链); 真渲染可后续挂 Seedance |
| Slack OAuth2 (sendAndWait) | 海外平台 | ✅ **飞书群交互替代**: tenant token 发消息到教案制作组群 + 文件回传选择(或简化为本地 JSON 人工决策文件, B 关 mock) |
| Facebook Graph API (IG 发布) | 海外账号+企业验证 | mock(B 关模拟容器创建/轮询/发布); 真发布属海外业务另案 |
| Fetch Product Page | 免费 | 真跑可用(公开商品页) |

**结论: 全链可零付费验证; 唯一付费点 Sisif 有成熟免费替身路线(参照 lesson-03/8270 的 ffmpeg 占位视频方案)。**

## L2 验证计划

- **A 单元级(推荐先做这个)**: 忠实移植 6 个 Code/Set 节点(Extract Page Text/Split Into Variants/Build Slack Message/Pick Approved Variant/两个轮询计数器)+ If 判定逻辑, 断言: og 提取/6000 截断/prompts<3 条容错/轮询 attempt 递增与 40 上限/READY|ERROR|REFUNDED|TIMED_OUT 四态/Reject 分支/选中无 video_url 抛错。预计 30+ 断言。
- **B mock 全链**: 保留全节点名, Sisif/Slack/IG 三个外部族全 mock(Sisif mock 出 READY/ERROR/TIMED_OUT 三剧本; Slack sendAndWait mock 成读本地决策文件; IG mock 容器+FINISHED), 场景: S1 全部成功、S2 部分失败(2/3 READY)、S3 全失败→stopAndError、S4 人工 Reject、S5 IG 处理超时→stopAndError。
- **C 免费真跑**: DeepSeek 真调(写广告脚本) + 真实商品页抓取 + ffmpeg 占位竖屏视频真渲染 + 飞书群真实推送审核卡片; IG 发布保持 mock。零付费。

**推荐路径: A → B → C 全做(本项目外部依赖多, C 关的 DeepSeek+ffmpeg 替身是课程核心卖点)。**

## 风险点(预判)

1. **Sisif 轮询环双 Wait 结构**: 渲染轮询和 IG 轮询各一套 counter, `$('Wait Before Status Check').item.json` 回捞写法在 n8n 2.x 表达式里要验证(8270 项目已踩过 `$('节点').item` 回捞坑)。
2. **Slack sendAndWait 是阻塞型节点**: 替代为飞书时交互模型不同(飞书无原生 sendAndWait), 需改「发卡片+人工回执文件」两段式, 这是课程改编重点也是教案卖点。
3. **Fetch Product Page 裸抓**: 对 JS 渲染型商城(Shopify 部分主题)抓不到正文, 模板自己也在便签里承认; 课程里要讲清边界。
4. **stopAndError 分支**: n8n 2.x 中 stopAndError 会标记整个 execution failed, mock 验证时要断言「到达该节点」而非「执行成功」。
5. **IG 容器轮询只查 status_code**: 不处理 ERROR 状态, 40 次后统一超时, 健壮性一般——可列为模板改进点。
6. **outputParserStructured 依赖 LLM 按 schema 输出**: DeepSeek 兼容性已在 lesson-10/11/13 验证过, 风险低。

## 立项信息

- 定选人: ou_505161df2dcf20cbd42e367100f950b2
- 定选时间: 2026-10-25 10:45 (fresh 候选)
- 下一步: 等老板拍板 L2 验证路径 → A 单元级起步