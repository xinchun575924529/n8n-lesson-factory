# 立项报告 · 模板 10000

## 项目名
**「AI数字人短视频自动工厂」——Auto-create TikTok videos with VEED.io AI avatars, ElevenLabs & GPT-4**

## 来源
- n8n 官方模板库：https://n8n.io/workflows/10000/ （id 10000）
- 拉取接口：https://api.n8n.io/api/workflows/templates/10000（200，workflow.nodes 齐全）
- 定选方式：fresh 候选，B·立即研发（2026-09-11 05:29，by ou_505161df…）

## 用途
Telegram 收一张照片+一句主题 → Perplexity 查 TikTok 热点 → GPT-4 写 30s 口播脚本 → ElevenLabs 合成配音 → FAL.ai 的 VEED Fabric 把照片做成对口型说话的数字人视频 → GPT-4 写文案+话题标签 → 存 Google Sheets 台账 → Blotato 一键多发 TikTok/YouTube → Telegram 回传成片。

一句话：**发张照片就能长出一条 AI 数字人口播视频并自动发布**，典型 UGC/带货号量产套路。与我们 AI 短视频制作组的产线方向高度同构，教案卖点强。

## 节点清单（功能节点 17 + 便签 10 = 27）
| 节点 | 类型 | 作用 |
|---|---|---|
| Telegram Trigger | telegramTrigger | 收照片+主题 |
| Workflow Configuration | set | 集中放 API Key（elevenLabsKey/voiceId/falKey/时长/perplexityModel）|
| Extract Photo and Theme | set | 取最大 file_id + caption 当主题 |
| Search Trends with Perplexity | perplexity | 查相关 3 条热点 |
| Generate Script with GPT-4 | openAi(gpt-4o-mini) | 写 30s 脚本 |
| ElevenLabs Voice Synthesis | httpRequest | TTS 输出 mpga 二进制 |
| Convert .mpga to .mp3 | code | 改二进制属性名/文件名/mime |
| Upload Audio to Public URL | httpRequest | tmpfiles.org 传音频得公网URL |
| Get Photo File from Telegram | telegram | 下载照片文件 |
| Build Public Image URL | httpRequest | tmpfiles.org 传照片得公网URL |
| FAL.ai Video Generation | httpRequest | queue.fal.run/veed/fabric-1.0 提交渲染 |
| Wait for VEED | wait | **等 10 分钟** |
| Download VEED Video | httpRequest | 按 request_id 拉结果 |
| Generate Caption with GPT-4 | openAi(gpt-4o-mini) | 写 caption+5-8 标签 |
| Save to Google Sheets | googleSheets append | 台账 |
| Send a video | telegram sendVideo | 回传成片 |
| Upload Video to BLOTATO / Tiktok / Youtube | blotato 社区节点 ×3 | 多发平台 |
| Update Status to DONE | googleSheets update | 台账回写 |
| 便签 ×10 | stickyNote | 逐步 setup 教程（含广告引流）|

## 凭证缺口与替代方案（能免费不付费）
| 模板需要 | 付费性 | 替代 |
|---|---|---|
| Telegram bot token | 免费 | 就有现成测试 bot（17522 套路复用）；也可换飞书触发 |
| Perplexity | 付费/限量 | **DeepSeek**（联网非必需，热点改写可离线造）或 mock |
| OpenAI GPT-4 ×2 | 付费 | **DeepSeek 直连**（余额 9.9 元，不耗积分）✅ |
| ElevenLabs TTS | 付费 | **edge-tts 晓晓 +8%**（本厂标配，免费）✅ |
| FAL.ai / VEED Fabric 数字人 | **付费且无可替代**（对口型渲染）| B 阶段 mock；C 免费版可降级为「AI图+TTS+ffmpeg 合成成片」（8270 C 同款套路），真数字人列为付费升级项 |
| Google Sheets | 免费但需 OAuth | **本地 JSON / 飞书多维表** ✅ |
| Blotato（8平台分发，社区节点） | 付费 | **本厂抖音+B站浏览器发布通道**（dlg-upload.py 已验证）；mock 社区节点 |
| tmpfiles.org | 免费 | 保留（C 里可换本地 http.server） |

结论：**除 VEED 数字人渲染外全部可免费替代**；真跑推荐「免费降级版 C」，数字人渲染 mock，教程里说明付费升级路径。

## L2 验证计划
- **A 单元级**：Code 节点只有 1 个（mpga→mp3），但可做表达式单元（photoUrl 提取/配置读取/tmpfiles URL 正则改写）+断言。**单元数偏少，A 偏薄** → 建议 A 做 10+ 断言覆盖所有 Set 表达式坑。
- **B mock 全链**：mock Telegram/Perplexity/GPT/ElevenLabs/FAL/Sheets/Blotato 全外部节点，跑场景（正链/无 caption/渲染超时/下载失败）。
- **C 免费真跑**：DeepSeek×2 + edge-tts + 本地 JSON 台账 + ffmpeg 出片（8270 C 版完全可复刻）；FAL/Blotato/Telegram 留 mock 或降级。
- **推荐路径：A + B + C（本厂已成熟复用）**。若只做一关，B 场景覆盖价值最大（Wait 10min、tmpfiles URL 改写 regex、Blotato 合流都是坑位）。

## 风险点（预勘）
1. **Wait for VEED 写死 10 分钟**（queue 轮询粗暴），VEED 超时/失败无错误网。
2. **tmpfiles.org URL 改写正则**：`http://tmpfiles.org/xx/f` → `https://tmpfiles.org/dl/xx/f`，第三方服务随时可变（免费依赖的风险点，教案好素材）。
3. **Blotato 是社区节点**，本机未装，导入即缺节点需处理（mock 或替换）。
4. **fabric-1.0 分辨率硬编码 480p**，参数不可配。
5. **Save to Google Sheets 的 documentId/sheetId 是 '=' 占位**，导入必断。
6. ElevenLabs httpRequest 响应是二进制 file，转到回调名 `audio` 但 Code 里读 `binary.audio`——属性名链条是坑（A 可测）。
7. 法文混杂（"ta propriété binaire actuelle"），模板作者笔记风格，与 8270 同款。
8. 便签内有 LinkedIn/YouTube 引流广告，教案需说明可忽略。

## 下一步
等用户拍板 L2 路径（推荐 A+B+C 全做，复用 8270/17522 成熟套路）。