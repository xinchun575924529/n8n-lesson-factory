# 立项报告 · 模板 16419

- **项目名**: Generate YouTube shorts from prompts with OpenAI, ElevenLabs and Pexels(表单一句话 → 自动产竖屏短视频并发 YouTube)
- **来源**: https://n8n.io/workflows/16419/ (官方模板库, API 可拉取, 12 个功能节点 + 4 便签)
- **定选时间**: 2026-09-13 14:59, 模式未知以 research-active-16419.json 为准, 车间会话 label=研发·16419

## 用途 (它干什么)

表单提交一段话(Prompt) → OpenAI Agent 产出 {标题, ≤150词口播稿, 英文检索关键词}(结构化输出) → 双路并行:
- 上路: ElevenLabs TTS 合成口播 mp3 → FTP 上传(BunnyCDN) → 记录 audio_url
- 下路: Pexels 按关键词搜 55–65s 竖屏素材视频
→ Merge 汇合 → **Fal.run ffmpeg-api** 云端音画合成 → 每 30s 轮询合成状态 → 完成后下载 mp4 → YouTube 上传(categoryId=17)。

## 节点清单 (12 功能节点)

| # | 节点 | 类型 |
|---|------|------|
| 1 | On form submission | formTrigger |
| 2 | Set vars | set |
| 3 | Generate voiceover (AI Agent) | langchain.agent |
| 4 | OpenAI Chat Model (gpt-5.4) | langchain.lmChatOpenAi |
| 5 | Structured Output Parser | langchain.outputParserStructured |
| 6 | Voiceover vars | set |
| 7 | Text-to-Speech (eleven_v3) | httpRequest |
| 8 | Upload audio | ftp |
| 9 | Set Audio Url | set |
| 10 | Pexels 搜素材 | httpRequest |
| 11 | Merge | merge (combineAll) |
| 12 | Merge Audio with Video / Check Status / Wait 30s / Fetch Final / Fetch File | httpRequest + wait + if (Fal.run 队列轮询环) |
| 13 | Upload a video | youTube |

## 凭证缺口与替代方案 (能免费不付费)

| 原凭证 | 作用 | 替代方案 | 成本 |
|--------|------|----------|------|
| OpenAI (gpt-5.4) | 产脚本/标题/关键词 | **DeepSeek deepseek-chat**(工厂已在用, 余额直连) | 极低成本 ✅ |
| ElevenLabs (eleven_v3) | TTS 口播 | **edge-tts 晓晓**(免费, 教䁈01 已用) 或 Docker 内外网 Doubao; 英文口播选 edge-tts en-US-AriaNeural 等 | 0 ✅ |
| FTP/BunnyCDN | 临时存放 mp3 供 Fal 拉取 | 本地 n8n 自带 webhook/静态目录 + 公网可达性? Fal 拉件需公网 URL → **改用本地 ffmpeg 合成则整环不需要** | 0 |
| Fal.run ffmpeg-api (付费队列) | 音画合成 | **本机 ffmpeg**(工厂 L4 已验证的 zoompan/concat 管线) → 下载 pexels 视频 + 本机 ffmpeg -i video -i audio | 0 ✅ |
| Pexels API | 免费图库视频 | 保留, 免费注册即有 key (20k req/月) | 0 ✅ |
| YouTube OAuth2 | 上传 | 换成 **抖音草稿/不发** 或保留为"可选发布开关"(工厂发布走 publish-video.py 抖音+B站) | — |

**结论: 全凭证均可免费替代, 项目可 0 成本跑通。核心改造点: fal.run 合成环 → 本机 ffmpeg; ElevenLabs → edge-tts; OpenAI → DeepSeek; YouTube 上传换工厂既有发布管线。**

## L2 验证计划

- **A 单元级 (推荐起步)**: 逐节点 mock 单测——① DeepSeek 结构化输出(JSON 三字段稳定性) ② edge-tts 合成 ③ Pexels API 关键词搜索返回竖屏视频 ④ 本机 ffmpeg 音画合成(替换 fal.run 三个节点) ⑤ IF/Wait 轮询环是否直接删除即可。推荐度 ⭐⭐⭐
- **B mock 级**: 假数据打全链路结构, 不走真 API。模板本身逻辑轻(就一条流水线+一个轮询环), B 级性价比低, 可跳过。
- **C 真跑级**: 接真 DeepSeek/Pexels 各跑一次出 1 条真竖屏 mp4。**推荐 A → C 直跳**, 因为这个模板价值恰在端到端, 且改造后全是本地件。
- 风险点: ①AI 输出 JSON 偶发不稳定 → 结构化 parser + DeepSeek 回退重试; ②Pexels 中文关键词搜不到 → 系统提示已强约束英文关键词, A 级验证要测边界词; ③fal.run 轮询环删除后流程改直线, 需改连线(属于"改造环节", 不算修改原模板原则——L2 在导入副本上改)。

## 风险点汇总

1. Pexels 素材版权问题(免费 API 允许商用, 风险低)
2. edge-tts 英文口播也免费, 不受限
3. 抖音/YouTube 发布走工厂既有 publish-video.py 链路, 复用 9/13 刚修好的双平台脚本
4. gpt-5.4 是模板作者写的未来模型名, DeepSeek 替换天然规避

--- 
*生成: 研发·16419 车间会话, 2026-09-13 15:16, 等用户拍板 L2 A→C 推进。*