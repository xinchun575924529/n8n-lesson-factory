# 第二讲 · 付费墙替身（DeepSeek / edge-tts / Mixkit / ffmpeg / mock 全案）

> 结论先行：这个模板挂着 **5 家付费 API**（OpenAI、ElevenLabs、BunnyCDN、Pexels、fal.run）+ 1 家 OAuth 繁琐户（YouTube）。本讲给每一环配免费替身，**核心逻辑 1:1 保留，成本归零**——L2C 已真跑验证（16 闸门全绿）。

---

## 1. 替身总表

| 原节点 | 付费服务 | 免费替身 | 关键参数（L2C 实测） |
|---|---|---|---|
| Generate voiceover | OpenAI | **DeepSeek** `deepseek-chat` | `response_format={"type":"json_object"}` 强制 JSON |
| Text-to-Speech | ElevenLabs | **edge-tts** | `edge-tts --voice en-US-AriaNeural --rate=+8% --write-media voice.mp3` |
| Upload audio | FTP→BunnyCDN | **删除整段** | 本地路径直传，链式依赖归零 |
| Pexels 素材 | Pexels API | **Mixkit vertical 列表页** | 免 Key；下载后 ffprobe 文件级竖屏校验 |
| Merge Audio with Video | fal.run | **本机 ffmpeg** | `-t 60 -shortest`；无轮询环，失败即红 |
| Upload a video | YouTube OAuth | **mock 发布** | 留 `mock=true` +  publish_queue 痕迹 |

> ⚠️ 替身不是"降级"。Pexels 没 Key 实测就是 **401 直接拒**；fal 换 ffmpeg 后**轮询环空转坑连根消失**——好几处替身反而比原版更稳。

## 2. LLM：OpenAI → DeepSeek

**接口形态**：DeepSeek 兼容 OpenAI Chat Completions，`baseURL=https://api.deepseek.com`。

**关键差异**：Structured Output Parser 节点在 DeepSeek 上不一定吃（取决于 n8n 版本对 schema 的透传）。**更稳的姿势**（L2C 采用）：
- 用普通 HTTP Request 节点直调 `/chat/completions`
- 请求体加 `response_format: {"type": "json_object"}`
- system prompt 里把 `{title, script, keywords}` 的键名与示例写死
- 返回后 `JSON.parse` + **断言闸门**（必填/词数/标题长——把坑⑥补上）

**为什么不用 LangChain OpenAI 节点改 baseURL**：可以，但凭证体系要新建"OpenAI 兼容"凭证；HTTP 节点 + Header Auth 更通用，学员换任何兼容端（Moonshot/智谱）都零改动。

## 3. TTS：ElevenLabs → edge-tts

**edge-tts** 是微软 Edge 朗读接口的免费 CLI/库，不用 Key、不翻墙可用。

```bash
edge-tts --voice en-US-AriaNeural --rate=+8% \
  --text "<口播稿>" --write-media voice.mp3
```

**实测口径**（L2C 台账）：112 词英文稿 + `+8%` 语速 → **52.632s**。目标 60s 下留 7.4s 余量，给片尾句与合成对齐用。
**坑⑤自动消失**：不走 HTTP 表单，400 问题不存在。
**中文/其他音色**：`edge-tts --list-voices` 全表可查（出海课用英文音，中文改编可换 `zh-CN-XiaoxiaoNeural`）。

## 4. 音频托管：FTP+BunnyCDN → 整段删除

原版的 FTP 上传只为了"让 fal 能拿到音频 URL"。替身方案里 ffmpeg 本地合成**直接读本地文件路径**——整段删掉，坑⑦ 的 `$binary` 隐式依赖、桶名硬编码**连根拔除**。

## 5. 素材：Pexels → Mixkit vertical + ffprobe 闸门

**Pexels 免费替身**走 [Mixkit 竖屏分类页](https://mixkit.co/free-stock-video/vertical/)：免 Key、可商用、直链 mp4。

**但搜索级参数救不了横屏**——这是坑①的核心教训，所以替身流程是**三段式**：

1. 按 keywords 从 Mixkit 列表页筛候选（L2C 内置若干经人工验证的竖屏源，如 `FOOTAGE_SOURCE=mixkit-51500`）
2. `curl` 真下载 mp4 到本地
3. **ffprobe 文件级校验**：`width < height` 才算竖屏，不满足即换源或报错

> 配套加固：`footage.mp4` 入库前断言"时长 ≥ AUDIO_SEC 或按 `-t 60` 可截"，素材窗与音频时长不匹配的问题（坑⑨ 延伸）在闸门里暴露。

## 6. 合成：fal.run 轮询环 → 本机 ffmpeg

**原版结构**：Submit（拿 request_id）→ Wait 30s → Check Status → if 未完成回环……只有 COMPLETED 有出口。

**替身结构（L2C 实测）**：

```bash
ffmpeg -y -i footage.mp4 -i voice.mp3 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
  -map 0:v -map 1:a -c:v h264 -c:a aac -t 60 -shortest lesson-16419-c.mp4
```

- **无轮询环**：ffmpeg 同步执行，失败 = 进程非零退出 = n8n 节点红，坑② 连根消失
- **强制竖屏**：`scale+crop` 把任何素材钉成 1080×1920
- **双保险截齐**：`-t 60` 硬上限 + `-shortest` 跟短轨走，坑⑨ 的时长漂移被锁死
- **实测产物**：31.25MB / 52.636s / 1080×1920 / h264+aac（台账 `VIDEO_SEC=52.636`、`AUDIO_SEC=52.632`，差值 0.004s）

## 7. 发布：YouTube OAuth → mock 队列

免费版用 `mock` 发布节点替代（`mock=true` + publish_queue 留痕）。**要点**：mock 项在闸门里**单独标记、永不计入真实通过**——这是 MockGate 约定，防止"假绿"。想真传，按第四讲的修参清单接 OAuth。

## 8. 坑⑧：中文关键词必 0 结果

**现象**：keywords 若是中文（或混合语种），Pexels/Mixkit 英文库**必然零结果**，模板无任何兜底。
**加固**（L2C 已示范）：
1. keywords 生成时在 prompt 里强约束"英文单词 ×3"
2. 闸门里检 `keywords.every(k => /^[a-z ]+$/i)`，不过即重 roll
3. 兜底：关键词全灭时回落到通用竖屏素材（如 `FOOTAGE_SOURCE=mixkit-fallback`）

## 动手练习

1. 在 L2C 里把 `Gen Script (DeepSeek)` 的 `response_format` 删掉重跑一次，观察 `JSON.parse` 在什么情况下炸——理解"显式 JSON 模式"的价值。
2. 把 `FOOTAGE_SOURCE` 改成一个横屏素材直链，跑一遍看 ffprobe 闸门怎么拦截——亲手引爆坑①。