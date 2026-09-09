# 立项报告 · 8270 Generate AI viral videos with NanoBanana & VEO3, shared on socials via Blotato

- 项目 ID：8270
- 来源：https://n8n.io/workflows/8270/
- 节点数：15 功能节点（+便签若干）
- 定选时间：2026-09-09 20:08（fresh 候选，B·立即研发）
- 定选人：ou_505161df2dcf20cbd42e367100f950b2

## 项目是什么
Telegram 机器人接单：用户给机器人发一张产品图+一句创意说明，工作流自动：
1. 用 **NanoBanana（Google Gemini 图像编辑，经 kie.ai API）** 把产品图修成广告级场景图
2. 用 OpenAI（AI Agent + Structured Output Parser）按 master prompt schema 生成 VEO3 结构化视频提示词
3. 调 **kie.ai VEO3 API** 生成视频（异步 taskId → Wait 20s 轮询 record-info 取 resultUrls）
4. GPT-4o 重写 200 字以内社媒 Caption
5. 标题/Caption/视频URL 存 Google Sheets，状态机 CREATE→Published
6. **Blotato 一键分发 8 大海外平台**（YouTube/TikTok/LinkedIn/Facebook/Instagram/Threads/Bluesky/Pinterest/Twitter-X）
7. Telegram 回发视频 URL + 成片预览

典型用途：UGC 风产品广告短视频批量生产 + 全平台自动发布，「一条龙AI爆款视频流水线」。

## 节点清单
1. Telegram Trigger: Receive Video Idea（telegramTrigger，入口）
2. Set Master Prompt（set，注入 json_master 视频提示词 schema）
3. AI Agent: Generate Video Script（langchain.agent，生成 VEO3 提示词）
4. OpenAI Chat Model（gpt-4.1-mini）
5. Think（toolThink）
6. Structured Output Parser（outputParserStructured）
7. Generate Video with VEO3（httpRequest POST api.kie.ai/veo/generate）
8. Wait for VEO3 Rendering（wait 20s）
9. Download Video from VEO3（httpRequest GET api.kie.ai/veo/record-info）
10. Rewrite Caption with GPT-4o（langchain.openAi）
11. Save Caption Video to Google Sheets（googleSheets appendOrUpdate）
12. Send Video URL via Telegram（telegram）
13. Send Final Video Preview（telegram sendVideo）
14. Upload Video to BLOTATO + 8平台发布节点（@blotato/n8n-nodes-blotato 社区节点 ×9）
15. Merge（chooseBranch, 9 输入）
16. Update Status to "DONE"（googleSheets）
（另有 NanoBanana 修图链节点：Edit Image / Download Edited Image / Update Image Description / Read CONFIG 表，模板详情层字段未完取全，导入后核对）

## 凭证缺口与替代方案（能免费不付费原则）
| 模板需 | 用途 | 替代方案 |
|---|---|---|
| Telegram Bot | 入口+回发 | ✅ 可复用我方测试 TG bot / 飞书群互换；单元测试可 mock |
| OpenAI (gpt-4.1-mini/gpt-4o) | 提示词生成+Caption | ✅ DeepSeek deepseek-chat 直连（已有 key，余额~9.9元），AI Agent 换 lmChatDeepSeek / OpenAI 节点改 baseURL=https://api.deepseek.com/v1 |
| kie.ai API（NanoBanana+VEO3） | 图修+视频渲染 | ⚠️ **付费第三方中转**（按次计费，无免费额度保证）。L2 阶段：VEO3 调用 mock；本机等价能力=AutoDL ComfyUI Z-Image/Qwen 修图（免费）+ Seedance/README 口径说明 |
| Google Sheets | 台账 | ✅ 换本地 JSON（17522 同款）或飞书多维表「N8N教案台账」现成 |
| Blotato API + 8 账号 | 分发 | ✅ 换本厂自研：抖音(浏览器 dlg-upload)+B站(浏览器通道)双发；9 个 blotato 社区节点 mock |

## L2 验证计划
- **A 单元级（推荐起步，零外部依赖）**：Code 忠实移植核心计算单元做断言——master_prompt schema 注入、结构化输出解析（title/final_prompt 提取与转义）、VEO3 请求体拼装（prompt/model/aspectRatio/imageUrls）、resultUrls 提取、Sheets 状态机字段映射（CREATE→Published）、Caption <200 符约束校验。预计 25-35 断言。
- **B mock 全链**：Telegram/Sheets/LLM/kie.ai/Blotato 全 mock，跑 正常图/无caption/VEO3超时/渲染失败 等场景断言路由。
- **C 真跑**：需 kie.ai key（NanoBanana+VEO3 按次付费，VEO3 单次约 ¥1-4）+ OpenAI→DeepSeek + Telegram bot。**确认是否投入 voucher 前请拍板**；也可用免费版 C=DeepSeek(提示词)+ComfyUI(修图,免费)+Seedance 或仅跑通前半链。

**推荐：A 起步 → B 全链（均为零成本）→ C 视关键产出价值再投。**

## 风险点
1. **kie.ai 非官方 API**（第三方中转 Gemini/VEO3）：计费与可用性不受 n8n 控制，文档视频 15 节点里渲染是最贵一环
2. **Blotato 社区节点**（@blotato/n8n-nodes-blotato）本机 n8n 未装，导入会缺类型 → B 阶段逐节点 mock 成 httpRequest/NoOp，或先装社区节点但不配凭证
3. **Telegram photo[2]** 硬编码取第 3 档分辨率，低清图可能 undefined → 单测覆盖照片尺寸档位缺失场景
4. **Wait 20s 轮询只等一次**：VEO3 渲染常 1-3 分钟，20 秒后 record-info 可能未 ready → 模板缺陷点，做坑教学素材；B mock 可复现
5. **Sheets 列名法文混杂**（TITRE/CAPTION VIDEO）：台账中文化时注意映射
6. AI Agent prompt 里引用 `Google Sheets: Update Image Description` 的 IMAGE DESCRIPTION（NanoBanana 修图前 VL 看图描述步）——链路跨分支引用，单测需等价 mock 输入

## 下一步
等拍板：L2 按 A→B 推进？C 是否投入 kie.ai 付费额度（或免费替代版 C）？