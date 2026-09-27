# L2-C 真跑报告 · 19710 AI Personal Research Assistant

- 时间：2026-09-28 07:4x（Asia/Shanghai）
- 工作流：`L2C19710real0001`（L2C-Real-19710-ResearchAssistant，未激活，CLI 驱动）
- 生成器：`scripts\build-l2c-19710.py` ｜ 执行日志：`state\19710-c-run.log`（裸 prompt 版）/ `state\19710-c-run2.log`（加固版）
- **结论：✅ 通过 —— 免费替代链真实 E2E 跑通：DeepSeek×2 真调 + DBpedia 真调 + 本地 JSON 存档 + 飞书群真实推送（notifyCode=0），加固后 8 章节结构化报告齐出。**

## 凭证替代实测结论

| 模板 | 替代 | 实测 |
|---|---|---|
| OpenAI gpt-4o-mini ×2 | DeepSeek deepseek-chat 直连 | ✅ 两阶段（造查询+综合报告）都可用，单次全链成本几分钱 |
| Wikipedia API | **国内直连不通（000），WARP 也挂（DNS endpoint 路由异常复发）** → DBpedia lookup（可达、免费、无 key） | ✅ 可达可用；⚠️ 公共端点数据集被裁剪（无 abstract），正文只能靠 lookup comment，内容偏浅；检索相关性弱（"honey production" 配到 Kentucky/Record producer 这类松散实体） |
| Google Sheets | 本地 JSON（appendOrUpdate 语义复刻） | ✅ 5 轮循环写 5 行（Topic=词条标题，B 关坑实锤再现） |
| Slack | 飞书群（N8N教案 bot tenant token） | ✅ 真实发出 5 条（notifyCode=0，刷屏坑也顺带实锤） |

## 两轮真跑对比（教学金矿）

| | 第 1 轮（模板原 prompt） | 第 2 轮（prompt 加一行锁 `###` 格式） |
|---|---|---|
| 执行 | 成功 | 成功 |
| 8 章节字段 | **全空**（DeepSeek 不主动用 `###` 前缀，坑 D9 在真实环境复现） | **全部非空**（executiveSummary 366 字符等） |
| 落库 | Result 有全文、Summary 等列全空=脏数据静默入库 | 全字段完整 |

**一句话教案卖点**：同一个模板，GPT-4o-mini 的隐性输出习惯是它能"跑"的最后一根稻草；换任何其他模型，prompt 不锁 `###` 就静默产空。这一行 prompt 加固 = 本课最值钱的知识点。

## C 阶段新增坑（真跑才暴露）

1. **Wikipedia 国内不可达**——模板在中国的学员环境里开箱即死，必须讲替代源（本课用 DBpedia）或海外节点；这是本课对中国学员的第一大坑。
2. **n8n httpRequest jsonBody 大坑**：`={"model":...}` 对象字面量表达式 与 `=JSON.stringify(...)` 都被 parseJsonParameter 拒（"not valid JSON"）；唯一稳的姿势=**上游 Code 节点预构 JSON 字符串，jsonBody 写 `={{ $json.reqBody }}`**。
3. DBpedia 公共 SPARQL 端点数据集裁剪（无 abstract/comment 谓词），`data/<X>.json` 也不含 abstract——选替代源时必须实测字段，不能信文档。
4. 百度百科/豆瓣系服务端抓取全触发反爬挑战（__PARIS_CHALLENGE__），server-side fetch 不可行。

## 偏离模板清单（如实申报）

- Webhook → CLI execute 驱动（Set 静态注入 topic="honey production"）
- Wikipedia 两节点 → DBpedia lookup 两个 httpRequest + 2 个形状适配 Code
- AI 综合 prompt 加了 12K 字符截断守护 + `###` 格式强制行（第 2 轮）
- Sheets→本地 JSON、Slack→飞书、respondToWebhook→本地 final.json（loop 回连结构保留）
- 其余 Set/If/Parse/Prepare/Clean/Merge/Formatter/splitInBatches 全部忠实原样

## L2 总结论

A 30/30 + B 17/17 + C 真实 E2E 通过。模板逻辑可跑但「糙」：报告按词条逐条生成、只处理第一个查询、Topic 列错置、静默失败点 4 处——全套坑已实锤收录，教案素材充足。**建议进 L3 课程库。**