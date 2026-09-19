# 第一讲 · 产稿与配音链（坑④⑤⑥⑦⑨）

> 本讲把前半链拆穿：**On form submission → Set vars → Generate voiceover(Agent+Parser) → Voiceover vars → Text-to-Speech(ElevenLabs) → Upload audio(FTP) → Set Audio Url**。
> 结论先行：这一段集中了全模板 **5 个坑**，而且全是"静默型"——不炸不报警，只给你脏数据。

---

## 1. 链路与产物

| 节点 | 干什么 | 输出关键字段 |
|---|---|---|
| On form submission | 表单收用户 prompt | `Prompt` |
| Set vars | 初始化变量 | `channelName` 等 |
| Generate voiceover | Agent+Parser 产稿 | `{title, script, keywords}` |
| Voiceover vars | 拼口播稿全文 | `voiceover`（script + 片尾句） |
| Text-to-Speech | ElevenLabs 合成 mp3 | binary `data` |
| Upload audio | FTP 上传到 BunnyCDN | `path` |
| Set Audio Url | 拼公网 audio_url | `audio_url` |

## 2. 坑⑥：Parser 是"注释级"约束

**现象**：标题 60 字符、脚本 150 词，写在 system prompt 里，Structured Output Parser 的 schema **没有 required、没有 maxLength**。

**实测**（L2A-U2）：把"写 300 词"的指令喂进去，Parser 照收不误——schema 层完全不拦。

**引爆条件**：任何一次模型发挥失常（或上游 prompt 被改），下游合成时长超 60s，YouTube Shorts 直接超限。

**加固**：Parser 后加一道 Code 断言闸（必填键 + 词数 ≤150 + 标题 ≤60 字符），不过即重 roll（L2C 里已示范，见 `workflows/L2C-free-16419.json` 的 `Gate: Script`）。

## 3. 坑④/⑨：`channelName='XXX'` 硬编码 + 双口径不一致

**坑④ 现象**：`Voiceover vars` 拼的片尾句里 `channelName='XXX'` 是**字面硬编码**，作者忘了抽变量。
**后果**：学员原样跑，每条成片结尾都念一遍"XXX"，直接社死。

**坑⑨ 现象**：同一模板两处口径——system prompt 说"60 秒"，schema 注释说"150 词"。英文 150 词常速 ≈ 65s+，**两者对不上**。
**后果**：按"150 词"写稿必然超时；按"60 秒"写词数又没锚点。模板作者自己也没想清楚。

**加固**：片尾句抽成 Set 节点变量（channelName 从 vars 读）；时长统一用"词数 ≈ 语速×秒数"换算锚定（edge-tts `+8%` 语速下 112 词 ≈ 52.6s，留 7s 余量给片尾）。

## 4. 坑⑤：ElevenLabs 只给 form-urlencoded（HTTP 400）

**现象**：`Text-to-Speech` 节点的 body 用的是**表单参数**（bodyParameters），没设 `Content-Type: application/json`。
**实测**：ElevenLabs 官方接口对此直接回 **400**（它要的是 JSON body）。
**加固**：改 `sendBody=json`（或明确 JSON Content-Type），把 text/model_id/voice_settings 走 JSON；免费版换成 edge-tts 后此坑自然消失。

## 5. 坑⑦：audio_url 的 `$binary` 隐式依赖

**现象**：
- `Set Audio Url` 拼 URL 时依赖 `$binary`（向上回捞二进制）
- FTP 节点的 BunnyCDN 桶名/PATH **硬编码**
- FTP 节点本身**不输出 binary**

**连锁后果**：
1. 换 BunnyCDN 桶要改两处，漏一处就是 404
2. `$binary` 实际捞到的是 TTS 节点的输出，中间插任何清洗节点即漂
3. audio_url 静默变空串 → 下游 fal 合成拿到**无声素材**，成片哑了也不报错

**加固**：audio_url 一律从显式字段传（如 `$('Upload audio').first().json.path` + 桶域名变量化）；免费版删 FTP 段后，直接传本地文件路径，链式依赖归零。

## 6. 坑点小结（本讲 5 坑）

| # | 位置 | 类型 | 危险度 |
|---|---|---|---|
| ④ | Voiceover vars | channelName 硬编码进片尾句 | 社死级 |
| ⑤ | Text-to-Speech | form-urlencoded 必 400 | 功能级 |
| ⑥ | Structured Parser | 无 required/maxLength | 质量级 |
| ⑦ | Set Audio Url | `$binary` 隐式 + BunnyCDN 硬编码 | 静默级 |
| ⑨ | system prompt vs schema | 60s 与 150 词口径不一致 | 质量级 |

## 动手练习

1. 在导入的原版里找到 `Voiceover vars`，把 `XXX` 出现的位置标出来，回答：作者原意是从哪个节点取 channelName？他少写了哪一步？
2. 用任意 OpenAI 兼容端给 Parser 的 schema 加上 `"required": ["title","script","keywords"]` 和 `maxLength`，重跑一次产稿，对比有无闸门时的输出差异。