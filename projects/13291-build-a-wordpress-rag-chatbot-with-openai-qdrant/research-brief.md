# 立项报告 · 模板 13291

## 项目名
**Build a WordPress RAG chatbot with OpenAI, Qdrant or MongoDB Atlas**
（WordPress 博客内容 RAG 智能问答机器人）

## 来源
- n8n 官方模板库：https://n8n.io/workflows/13291/
- 定选时间：2026-10-29 09:25（fresh 候选，老板定选）
- 节点数：20（含 12 个 stickyNote 说明便签，实际功能节点约 24 个）

## 用途（一句话）
把 WordPress 站点全部文章抓取→清洗→向量化存入 Qdrant，再对外提供一个带 Header 鉴权的 webhook 聊天接口：先意图/语言路由（smalltalk / info / rag × it/en），RAG 分支走向量检索→Cohere 重排→LLM 生成结构化 JSON（标题+URL+摘要），并把对话日志写入 Google Cloud Storage。

## 架构（两条工作流合一）
1. **WF1 索引流水线**（Manual Trigger）：WP Get all post → Code 清洗 HTML/实体解码/拼 title+excerpt+content → Text Splitter(1200/150) → Default Data Loader(带 title/url/postId/slug 元数据) → OpenAI Embeddings → Qdrant insert
2. **WF2 问答服务**（Webhook POST /wp-ai-chatbot, headerAuth）：Code-Request_Parsing（校验 message≤2000 字符）→ OpenAI Intent Router（json_schema 输出 intent+language）→ Switch 五路（smalltalk_it / smalltalk_en / RAG_it / RAG_en / info）→ RAG 分支：Qdrant load(topK 60)+Cohere Reranker(topN 20) → Build context（按 URL 去重、按 score 排序、截 35 条 280 字 snippet）→ AI Agent（意大利语/英语双 prompt，结构化输出）→ Code-Response_Parsing（URL 重写、type 归一、剥 follow_up）→ Respond to Webhook(JSON)；之后 Set date → GCS Object_Log 落日志

## 节点清单（功能节点）
- n8n-nodes-base：wordpress(getAll)、code×6、webhook、switch、respondToWebhook、set、crypto、googleCloudStorage、manualTrigger、stickyNote×12
- langchain：vectorStoreQdrant×3、embeddingsOpenAi×2、documentDefaultDataLoader、textSplitterRecursiveCharacterTextSplitter、rerankerCohere×2、outputParserStructured×2、lmChatOpenAi(gpt-5)×2、agent×2、openAi(gpt-5-mini 意图路由)

## 凭证缺口与替代方案（能免费不付费）
| 原凭证 | 用途 | 免费替代 |
|---|---|---|
| OpenAI API（gpt-5 / gpt-5-mini / embeddings） | 意图路由 + 双 Agent + 向量化 | 聊天 → **DeepSeek deepseek-chat**（工厂标配，真调实证多课）；embeddings → **硅基流动 SiliconFlow 免费 BAAI/bge-m3**（OpenAI 兼容端点，embedding 免费） |
| Qdrant Cloud | 向量库 | **Qdrant Cloud 免费 1GB 集群**（免费层够 1 个站点用）或本机 docker qdrant |
| Cohere Reranker | 检索重排 | Cohere 有免费 trial key；也可**去掉 reranker 直接按 score 排序**（B/C 关验证影响小，推荐 C 用免费 key，教案里标注可选） |
| WordPress 账号密码 | 拉文章 | **任意公开 WP 站 REST API**（/wp-json/wp/v2/posts 免鉴权，测试用公开博客即可），零成本 |
| Google Cloud Storage | 对话日志 | **本地 JSON 文件 / 飞书多维表格**（工厂惯例：GCS→本地文件落盘） |
| Header Auth | webhook 鉴权 | 保留，自建凭证即可 |

## L2 验证计划
- **A 单元级（推荐先做）**：6 个 Code 节点忠实移植单测——stripHtml/实体解码、Request_Parsing（非法输入拦截）、Intent Router 的 Switch 五路分流、Build context（URL 去重/排序/截断）、Response_Parsing（markdown 包裹 JSON 容错、URL 重写、follow_up 剥离）、Smalltalk_response 假结果卡构造。预计 35+ 断言。
- **B mock 全链**：WP→静态 JSON，embeddings→假向量，Qdrant→mock 检索结果，Cohere→mock 排序，LLM→mock 结构化输出；场景：smalltalk_it / smalltalk_en / rag_it / rag_en / info / 非法请求 / 空检索结果。
- **C 免费真跑**：公开 WP 站真拉文章 + 硅基流动 bge-m3 真 embedding + Qdrant Cloud 免费集群真存真检 + DeepSeek 真生成 + 日志落本地文件。0 元。
- **推荐路径：A → B → C 全做**（本模板链路长、双分支双语言，C 真跑能验证 embedding 维度匹配和 Qdrant 集合 schema 这两个最容易踩坑的点）。

## 风险点（预判坑）
1. **gpt-5 / gpt-5-mini 模型名**：DeepSeek 无此型号，必须替换 deepseek-chat；Intent Router 用的是 langchain.openAi 节点（非 lmChatOpenAi），json_schema textFormat 在 DeepSeek 上不支持 → 需改为 prompt 约束 JSON + Code 节点容错解析（Response_Parsing 已有容错先例）。
2. **意大利语/英语双语分支**：中文课程版需决定：保留双语教学（推荐，体现路由价值）还是改中文单语。
3. **embedding 维度**：bge-m3=1024 维 vs OpenAI 1536 维，Qdrant 集合维度必须与实际 embedding 模型一致，混用必炸。
4. **Switch 左值表达式** `$json.output[0].content[0].text.intent`：DeepSeek 返回结构与 OpenAI responses API 不同，路由取值路径要改写。
5. **Build context 里引用 `$items("Code-Request_Parsing")`**：节点名带连字符，表达式引用在 2.x 可用但移植时注意名字别改。
6. **AI Agent typeVersion 3 + hasOutputParser**：DeepSeek 替换时输出解析器兼容性要在 B 关验证。
7. **Qdrant Search prompt 直引 Webhook body**：`{{ $('Webhook').item.json.body.message }}`，webhook 节点在 CLI 单测时无历史数据，mock 时需提供。

## 下一步
等老板拍板 L2 验证路径（建议 A 起步 → B → C），随后开工 A 单元级。