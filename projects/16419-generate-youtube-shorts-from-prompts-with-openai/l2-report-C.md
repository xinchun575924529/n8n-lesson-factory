# L2-C 免费替代真跑报告 · 模板 16419（一句话 → 竖屏 Shorts 短视频工厂）

- **日期**：2026-09-16 20:53 (Asia/Shanghai)
- **工作流**：`L2Cstm164190001`「L2-C 免费真跑 16419」（13 节点，n8n CLI execute **success**）
- **生成器**：`scripts/build-l2c-16419.py`；源稿 `workflows/wf-l2c-16419.json`
- **结果**：**16 / 16 断言全过（0 FAIL），6 / 6 模型硬规则合规观测全过，零付费，产出真实竖屏成片**

## 替代落位（对照模板原节点）

| 模板 | C 版 | 真假 |
|---|---|---|
| OpenAI Chat Model `gpt-5.4`（未来模型名，不可用） | DeepSeek `deepseek-chat` + `response_format=json_object` | ✅ 真调 |
| AI Agent + Structured Output Parser | 同一份 systemMessage 原文 + JSON 输出约束，代码侧 `JSON.parse` | ✅ 真调（模板 systemMessage 逐字保留，仅替换 `{{ $json.channelName }}` 占位） |
| ElevenLabs TTS `eleven_v3`（付费） | **edge-tts en-US-AriaNeural +8%**（本地） | ✅ 真出 315,792B / 52.632s mp3 |
| Upload audio（FTP/BunnyCDN，作者私有桶） | **整段删除**（本地 ffmpeg 不需要公网音频 URL） | 链路简化 |
| Pexels API 视频搜索 | **真实测 401**（无 key）→ 免 key 公开素材库 Mixkit vertical 列表页 + **文件级竖屏校验** + curl 真下载 | ✅ 真搜索真下载 |
| fal.run `ffmpeg-api/merge-audio-video` + 状态轮询环 + Wait 30s | **本机 ffmpeg**（scale/crop 到 1080x1920 + 音频 + `-shortest`） | ✅ 真合成，轮询环整段删除 |
| Fetch Final / Fetch File from URL | 本地文件直通 | 简化 |
| Upload a video（YouTube OAuth2） | mock（未真发） | 发布=本厂 publish-video.py 抖音+B站通道（L4 范畴） |
| （模板无）台账 | 本地 JSON 台账 `ledger.json` | ✅ 真写盘 |

## 真实工件（`state/16419-c-data/`）

| 文件 | 事实 |
|---|---|
| `script.txt` | 642 B，DeepSeek 写的 **112 词**英文口播稿（"Europe is quietly…" 开场，结尾 `Follow N8N工厂 for more`） |
| `voice.mp3` | 315,792 B / **52.632 s**（edge-tts `en-US-AriaNeural`） |
| `footage.mp4` | 10,547,980 B / **720x1280 竖屏**（Mixkit video 51500 的 `-720` 档，列表页 8 个候选中第 1 个通过文件级 h>w 校验） |
| `lesson-16419-c.mp4` | **31,250,387 B / 52.636 s / 1080x1920 / h264 + aac / 4.75 Mbps**（成片=竖屏 Shorts 规格） |
| `ledger.json` | 1 行台账：PROMPT/TITLE/KEYWORD/WORDS/AUDIO/FOOTAGE_SOURCE/VIDEO/VIDEO_SPEC/AUDIO_SEC/VIDEO_SEC/STATUS=DONE |

**DeepSeek 实际产出**：title=`Europe's 4-Day Work Week Is Spreading`（37 字符）、keyword=`office workers leaving building`（4 词，纯英文）。

## 断言清单（16，全过）

结构闸门：三字段齐 / Pexels 401 实证 / 候选列表 ≥3 / 素材 >200KB / **素材文件级竖屏 h>w** / 音频 >20KB / 音频 >5s / 成片 >500KB / **成片 1080x1920** / 时长≈音频(±2s) / h264 / aac / 台账 DONE / 台账可重读 / YouTube mock / 成片 ≤62s

模型硬规则合规观测（6/6 OK，模板 prompt 有效）：script 112 词 ≤150 ✅｜title 37 字符 ≤60 ✅｜keyword 1-4 词纯 ASCII ✅｜结尾句 = `Follow N8N工厂 for more` ✅（**中文频道名在英文稿里也被正确收尾**）｜无 emoji/hashtag ✅｜首三词非被禁开场 ✅

## 关键坑与发现

- **Pexels 必须自己注册免费 key**：无 key 真调 = `401`（模板把 key 放在 `httpHeaderAuth` 凭证里，复刻者不知道就一路 401 到死）。已实测替代通路：Mixkit `free-stock-video/vertical` 列表页免 key、CDN 直链可下载。
- **文件级竖屏校验必须有**：Mixkit `-360` 预览档全是 640x360 横屏，`-720/-1080` 档才保留原比例（本片 51500 `-720` = 720x1280 竖屏）。这印证了 A 级断言 U8——**只看搜索参数不看文件尺寸，必然出横屏**。
- **n8n Code 里 `helpers.httpRequest` 的报错取值**：状态码在 `e.httpCode`（不是 `e.response.statusCode`），首次跑断言因此 FAIL，已修正。
- **素材清晰度取舍**：720x1280 上采样到 1080x1920（清晰度有损）。工程建议：取 `-1080` 档（约 108MB）或直接接自己的素材库/AutoDL 生成素材。
- **轮询环删除=最大简化**：本地 ffmpeg 同步出片，52s 素材 ≈ 10 秒内合成完，模板那套「POST 队列 → 每 30s 查状态 → 取结果」整段不需要；也因此**永久空转风险直接消失**。

## 结论

**A(90/90) + C(16/16) 两关全绿（B 级按拍板跳过），累计 106 断言、11 个模板坑固化。**
C 版证明：整条「一句话 → 竖屏 Shorts」链路除 Pexels key（免费自注册）与 YouTube 上传（付费账号）外，**可零成本端到端跑通并产出真实 1080x1920 成片**。

## 下一步

等老板拍板进 L3 教案仓库（README + docs + workflow.json + exercises + 短视频脚本 + Pages 站点，参照 lesson-03 规格）。