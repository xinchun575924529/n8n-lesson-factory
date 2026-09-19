# 00 总览 · 节点全景拆解（实拉版）

> 模板：n8n 官方 #16419「Generate YouTube Shorts from Prompts with OpenAI」
> 一句话：**表单收 prompt → AI 写 60s 口播稿 → ElevenLabs 配音 → Pexels 找竖屏素材 → fal.run 合成音视频 → YouTube 自动上传。**

---

## 0. 先上照妖镜：32 ≠ 25

官网页面标称 **32 节点**，`https://api.n8n.io/api/workflows/templates/16419` 实拉只有 **25 个**：

- **18 个业务节点**（真实干活）
- **7 个便签贴**（Sticky Note、1/2/3/4/5/8——编号还跳号）

这不是事故，是模板的"营销口径"——**学 n8n 模板的第一条军规：永远以 API 实拉为准**。本课从头到尾用实拉数据说话。

## 1. 主链地图

```
On form submission (表单收 prompt)
  → Set vars (初始化 channelName 等变量)
  → Generate voiceover (AI Agent: OpenAI Chat Model + Structured Output Parser)
       产出 {title, script, keywords}
  → Voiceover vars (拼装口播稿 + 片尾句)
  → Text-to-Speech (HTTP → ElevenLabs，form-urlencoded)
  → Upload audio (FTP → BunnyCDN 桶)
  → Set Audio Url (拼 audio_url，依赖 $binary)
  → Pexels (HTTP 搜竖屏素材，orientation=portrait)
  → Fetch Video File from URL (下载素材 mp4)
  → Merge Audio with Video (HTTP → fal.run ffmpeg-merge)
  → Wait 30 Seconds → Check Video Merge Status (HTTP 轮询)
       ↺ Check Merge Status (if) 未完成回环 Wait
  → Fetch Final Video (拿 fal 成片 URL)
  → YouTube: Upload a video
```

两条"生死契约"贯通全链（下方第 2 节）；一条强隐式依赖：`Set Audio Url` 依赖上上游的 `$binary`（坑⑦）；一处贯穿性写法：state 不落库，全靠 item 数据在链上流动（无状态机——这也是它跟 #8270 最大的结构差异）。

## 2. 两个"生死契约"（全课最重要）

### 契约一：Agent + Parser 的 schema 形同虚设
`Generate voiceover` 产出的 `{title, script, keywords}` 由 Structured Output Parser 约束，但：
- schema **没写 required**——缺键不报错
- **没写 maxLength**——"60 字符标题 / 150 词脚本"只写在 system prompt 里，是**提示词级**愿望，不是结构级约束（坑⑥）
- 下游 `Voiceover vars` 直接拿来拼片尾句，超长/缺词会在**合成环节**才炸

**生产姿势**：Parser 出稿后立刻过一道断言闸门（长度/必填/词数），不过即重 roll 或人工审。L2A 的 U2 单元 90 断言里专门有一组"schema 形同虚设"的反面验证。

### 契约二：audio_url 的 `$binary` 隐式链
`Set Audio Url` 拼的 URL 依赖 `Upload audio`(FTP) 的输出 + **更上游的 `$binary`**（坑⑦）。连锁反应：
- 作者在 FTP 节点里把 BunnyCDN 桶名/PATH 硬编码，换桶 = 改两处
- FTP 节点**本身不输出 binary**（只回路径元数据），`$binary` 实际捞的是 TTS 节点的
- 任何一环中间插一个清洗类节点，`$binary` 指向就漂了，audio_url 静默变空串 → 下游合成拿到无声素材

**生产姿势**：URL 只从**明确字段**传（`$('Upload audio').first().json.path` 这种显式引用），不碰 `$binary` 隐式回捞。

## 3. 付费点与免费替身全景

| 内部节点 | 去哪 | 按次付费？ | 免费替身（第二讲展开） |
|---|---|---|---|
| Generate voiceover (Agent) | OpenAI gpt-4o 系 | 是 | DeepSeek `deepseek-chat` + `response_format=json_object` |
| Text-to-Speech | ElevenLabs | 是 | edge-tts（en-US-AriaNeural 等任意音） |
| Upload audio | FTP → BunnyCDN | 是 | **整段删除**——本地文件路径直传 |
| Pexels 素材搜索 | Pexels API | 免费档需 Key | Mixkit vertical 列表页（免 Key）+ ffprobe 校验 |
| Merge Audio with Video | fal.run 队列 | 是 | 本机 ffmpeg（无轮询环，失败即报错退出） |
| Upload a video | YouTube API | 免费但 OAuth 繁琐 | mock 发布节点（留 `mock=true` 痕迹） |

> 实测锤点：Pexels **没有 Key 就是 401**（不是限流是直接拒），免费替身不是降级是**绕开**；fal 轮询环换成 ffmpeg 后，"失败任务永久空转"这个坑**连根消失**（执行命令失败直接红，不会无声打转）。

## 4. 三级验证结果速览

| 关 | 方法 | 结果 |
|---|---|---|
| L2A | 忠实复刻全部可纯计算单元，离线断言 | **90/90 通过**（schema 完整性 / audio_url 契约 / Pexels 取值 / 片尾句拼装 / YouTube 硬编码扫描 / 节点数核查） |
| L2B | —— | **生产拍板跳过**：A 已覆盖纯计算层、C 已覆盖真实依赖层，mock 层边际价值不足 |
| L2C | 付费点全替身 13 节点真跑 | **16 闸门 + 6/6 模型合规观测全过**，产出 1080×1920 / 52.636s / h264+aac 成片 |

## 5. 凭证映射表（完整版上线用）

| 节点 | 凭证 | 备注 |
|---|---|---|
| On form submission | n8n Form（内建） | 公网表单记得开 n8n 的 Form 访问控制 |
| Generate voiceover → OpenAI Chat Model | OpenAI API | 可整组换 DeepSeek（本课 C 级做法，占位凭证 id `fra8VO4w0TLBP9JO`） |
| Text-to-Speech | ElevenLabs API Key | header `xi-api-key`；**body 必须 form-urlencoded**（坑⑤） |
| Upload audio | FTP 账号 | BunnyCDN Storage 的 FTP 凭据；桶名在节点参数里硬编码（坑⑦） |
| Pexels | Pexels API Key | 免费档有 Key 也要逐月看配额 |
| Merge Audio with Video / Check Status / Fetch Final | fal.run API Key | 队列式提交：Submit → 拿 request_id → 轮询 status_url |
| Upload a video | YouTube OAuth2 | `categoryId`/`regionCode` 硬编码在节点参数里（坑⑩），换号换区必查 |

## 坑点提示

- 模板所有跨节点取值都是 `$('节点名')` 字符串引用——**改节点名 = 静默断引用**，导入后第一件事是通读而不是重命名。
- 全链**零错误网**：TTS 失败、FTP 失败、fal 失败都没有兜底分支，上一环红、下一环把脏数据当正常输入继续跑。第五讲的 11 坑里一半是这类"裸奔"。
- `Check Merge Status` 的 if 环**没有失败出口**（坑②）——这是全模板对生产最危险的一处，会烧着钱空转。

## 动手练习

1. 导入 `workflows/original-16419-official.json`，数一遍业务节点与便签贴各多少，跟官网页面对照——把"虚标"坐实。
2. 找到 `Set Audio Url`，把它的取值表达式抄下来，回答：它依赖了几个上游节点？如果中间插入一个 `NoOp`，哪个引用会漂？