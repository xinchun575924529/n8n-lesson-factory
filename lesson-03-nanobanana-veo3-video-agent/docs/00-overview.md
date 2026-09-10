# 00 总览 · 47 节点全景拆解

> 模板：n8n 官方 #8270「Generate AI viral videos with NanoBanana & VEO3, shared on socials via Blotato」
> 一句话：**Telegram 发参考图 + 创意 → AI 视觉分析 → 攒提示词 → NanoBanana 修图 → VEO3 成片 → 写 Caption → 九平台分发 → Sheets 台账。**

---

## 1. 双主链地图

模板 47 个节点，其实是**两条链 + 两张大横幅**：

### 左链（收图链 · 图文理解）
```
Telegram Trigger → Set: Bot Token → Telegram: Get Image File(photo[2])
  → Telegram API: Get File URL(photo[3]) → OpenAI Vision 分析参考图
  → Google Drive: Upload Image → Google Sheets: 更新图片描述
  → Generate Image Prompt(LLM) → NanoBanana: Create Image(fal.run)
  → Wait for Image Edit → Download Edited Image → Sheets: Log Image & Caption
```

### 右链（视频链 · 成片分发）
```
Google Sheets: Read CONFIG → AI Agent: Generate Video Script(+Structured Output Parser)
  → Format Prompt(Code, JSON.stringify) → Generate Video with VEO3(kie.ai)
  → Wait 20s → Download Video from VEO3 → Rewrite Caption(GPT-4o)
  → Save Caption to Sheets → Send Video URL via Telegram / Send Final Preview
  → Merge → Blotato ×9 平台 → Update Status to "DONE"
```

### 横切关注点
- **凭证占位**：`Set: Bot Token` 节点集中放 token，但模板留 `YOUR_BOT_TOKEN` 空占位且 token 拼接分散在两个节点 → 坑③
- **状态机**：`IMAGE NAME` 为键，Sheets 三处读写闭环 → 第三讲
- **错误网**：**没有**。渲染失败、结果缺失即全链裸奔 → 第五讲

## 2. 两个"生死契约"（全课最重要）

### 契约一：双层 JSON 提示词
`Structured Output Parser` 让 LLM 输出：
```json
{ "title": "...", "final_prompt": "{ \"description\": ..., \"camera\": ..., \"lighting\": ..., ... }" }
```
`final_prompt` 的值**本身还是一个 JSON 字符串**，内含 description / style / camera / lighting / environment / elements / subject / motion / VFX / audio / ending / text / format / keywords 等 8 个以上顶层键（A 级 U1 逐键验证过）。

### 契约二：stringify 配对无引号注入
- `Format Prompt`（唯一 Code 节点）：`prompt = JSON.stringify(final_prompt)` ——给内容**加上外层引号并转义**；
- `Generate Video with VEO3` 的 body：`"prompt": {{ $json.prompt }}` ——**没有引号**的裸注入。

两个节点一个加引号、一个不加引号，拼起来才是合法 JSON。**改任何一边，全链必炸**（A 级 U2/U3 的反面断言确认过：未转义注入 = 非法 body）。

## 3. 付费点与免费替身全景

| 内部节点 | 去哪 | 按次付费？ | 免费替身（第二讲展开） |
|---|---|---|---|
| OpenAI Vision 分析 | OpenAI | 是 | DeepSeek（视觉任务降级为文本 prompt 模拟） |
| LLM 生图提示词 | OpenAI | 是 | DeepSeek deepseek-chat |
| LLM 视频脚本 | OpenAI | 是 | DeepSeek deepseek-chat |
| Caption 重写 | OpenAI | 是 | DeepSeek deepseek-chat |
| NanoBanana 修图 | fal.run 队列 | 是 | ffmpeg gradients 本地合成 / ComfyUI |
| VEO3 视频渲染 | kie.ai | 是 | ffmpeg zoompan 3s 成片 |
| Google Sheets ×3 | Google | 免费但繁琐 | 本地 records.json |
| Blotato ×9 | Blotato | 是 | publish-queue.json 队列 |

> 勘误提醒：很多教程说 NanoBanana 走 kie.ai——**错了**。A 级实测它走 `queue.fal.run/fal-ai/nano-banana/edit`；kie.ai 只负责 VEO3。付费点是**两处**：fal.run + kie.ai。

## 4. 三级验证结果速览

| 关 | 方法 | 结果 |
|---|---|---|
| L2A | 忠实移植全部可纯计算单元，离线断言 | **44/44 通过**，确认坑①②③④ |
| L2B | 47 节点拓扑 1:1 mock，5 场景 CLI 实跑 | **18/18 通过**，坑①②精确复现，新发现坑⑤⑥⑦ |
| L2C | 免费替身版 19 节点真跑 | **10/10 通过**，修复坑⑥示范（Caption 200 符闸门） |

## 5. 凭证映射表（完整版上线用）

| 节点 | 凭证 | 备注 |
|---|---|---|
| Telegram Trigger / Get Image / Get File URL / Send ×2 | Telegram Bot Token | 以 `Set: Bot Token` 为中心，**两处拼接都要检查** |
| OpenAI ×4 | OpenAI API | 可整组换 DeepSeek（本课 C 级做法） |
| NanoBanana | fal.run API Key | 队列式提交，注意轮询 |
| VEO3 | kie.ai API Key | 渲染 1~3 分钟，20s 单次 Wait 不够 → 第五讲加固 |
| Google Drive / Sheets ×3 | Google OAuth | CONFIG 表 + 日志表 + 状态表共用 |
| Blotato ×9 | Blotato API + 各平台账号绑定 | 免费版用发布队列降级 |

## 坑点提示

- 看模板先找"跨节点引用"：下游大量 `$('节点名')` 回捞数据，**改节点名 = 静默断引用**（坑⑦）。
- `Set: Bot Token` 同时接 Trigger 与日志链两个上游，拓扑上是**双触发隐患**（坑⑤，不同 n8n 版本行为可能不同，列为待真机验证）。

## 动手练习

1. 导入 `workflows/L2A-test-8270-original-47nodes.json`，找出所有 `$('...')` 跨节点引用，画出依赖图。
2. 在 VEO3 body 里手动给 `{{ $json.prompt }}` 加引号，用 mock 数据触发一次，观察 DeepSeek/HTTP 层报什么错——体会契约二的脆弱。