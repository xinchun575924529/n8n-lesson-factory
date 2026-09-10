# 第二讲 · 付费墙替身：零成本把 47 节点模板复刻成免费版

> 结论先行：**模板的「逻辑资产」（提示词契约、轮询、状态机、分发编排）和「付费点」（4×OpenAI + fal.run + kie.ai + Blotato）是可以正交替换的。** 本课 C 级工作流 19 个节点，DeepSeek 真 API ×3（视觉任务压缩进文本链）+ ffmpeg 真工件 ×2 + 本地 JSON 台账，10/10 断言真跑全绿，成本≈0。

---

## 1. 替身对照总表

| 原配（付费） | C 级替身（免费） | 真实性 | 关键差异 |
|---|---|---|---|
| OpenAI Vision 分析参考图 | DeepSeek deepseek-chat | ✅ 真 API | 真视觉→文本化描述降级；有 ComfyUI/本地 VLM 可升级 |
| LLM 生成生图提示词 | DeepSeek deepseek-chat（**模板 prompt 原文搬运**） | ✅ 真 API | 无差异，契约完全一致 |
| LLM 生成 VEO3 脚本 | DeepSeek deepseek-chat | ✅ 真 API | 双层 JSON 契约原样保留 |
| GPT-4o 重写 Caption | DeepSeek deepseek-chat | ✅ 真 API | 顺手加了 200 符闸门（修复坑⑥） |
| NanoBanana（fal.run 队列） | ffmpeg gradients 本地合成场景图 | ✅ 真 PNG 工件 | 真 AI 修图→占位合成；AutoDL ComfyUI 可升级真修图 |
| VEO3（kie.ai） | ffmpeg zoompan 3s 1920×1080 | ✅ 真 mp4 工件 | 3s 占位成片；接口契约（resultUrls）保留 |
| Google Sheets ×3 | 本地 `records.json` | ✅ 真文件 | matchingColumns 语义手写等价 |
| Blotato ×9 | `publish-queue.json`（douyin+bilibili 入队） | ✅ 真队列 | 对接自有浏览器发布通道 |
| Telegram 收/发 | mock 回发字段 | mock | 学习版不接真 bot |

## 2. DeepSeek 适配的三处细节（HTTP Request 直连法）

C 级不用 n8n 的 AI 节点，直接 `httpRequest` 打 DeepSeek 兼容接口：

```jsonc
{
  "method": "POST",
  "url": "https://api.deepseek.com/chat/completions",
  "authentication": "genericCredentialType",     // ← 交付版挂 Header Auth 凭证
  "jsonBody": "={ \"model\": \"deepseek-chat\", \"messages\": [ {\"role\":\"system\",\"content\":\"...模板原文 system prompt...\"}, {\"role\":\"user\",\"content\":\"{{ $json.caption }}\"} ], \"response_format\": {\"type\":\"json_object\"} }"
}
```

**三个血泪细节**：

1. **`jsonBody` 表达式必须以 `=` 开头**。写成 `{{ ... }}` 明文，模板引用会原样发给模型——C 级真跑时 DeepSeek 收到一串花括号一脸懵、回了一段反问。**质量级 bug，契约断言全过也抓不到**——所以断言要看内容，不只看结构。
2. **httpRequest 会全量替换 item**。链路每过一次 HTTP 节点，上游数据全丢——下游用 `$('关键节点').item.json` 回捞（坑⑦的真机版，模板靠同一招续命）。
3. **response_format 兜底**：要求 JSON 输出时，解析层仍要做围栏清洗 + 失败回退——LLM 永远当不可信输入。

## 3. ffmpeg 替身：像真的但不是真的

- 修图替身：`gradients` 滤镜按品牌色合成 1280×720 场景图（`8270-c-render-image.py`），输出 `edited.png`。
- 成片替身：`zoompan` 把场景图推 3 秒缓推镜头，1920×1080 H.264（`8270-c-render-video.py`），输出 `final.mp4`。
- **调用坑**：n8n 的 `executeCommand` 节点在 CLI 环境**不可识别**（Unrecognized node type）→ 用 Code 节点 + `child_process.execSync` 调 python 渲染脚本（需 `NODE_FUNCTION_ALLOW_BUILTIN=child_process`）。
- 升级路径：本机/AutoDL 起 ComfyUI，把 NanoBanana 节点 URL 换掉即可修真图——接口契约不变。

## 4. 为什么替身版仍有教学价值

- **契约全部真跑**：双层 JSON、`Format Prompt` 的 stringify、VEO3 body 无引号注入——C 级与 A/B 断言互证，改一边必炸的脆弱性在免费版里一摸一样。
- **工件全部真实**：mp4 能播、JSON 能查、队列能消费——学员拿到的不是"PPT 工作流"。
- **修复有示范**：Caption 闸门（坑⑥修复）只在 C 级存在，是对照学习的活教材。

## 坑点提示

- DeepSeek 的 `deepseek-chat` 无视觉能力；分析参考图这一环要么接受文本降级（本课做法），要么换 `deepseek-vl`/本地模型，别硬塞图片 URL。
- ffmpeg 路径要在 n8n 进程的 PATH 里；Docker 版 n8n 官方镜像**不带 ffmpeg**，需自建镜像。
- 免费版不是交付版：占位合成图/3s 成片只验证流水线，不接真实客户场景。

## 动手练习

1. 把 L2C 工作流里任意一个 DeepSeek 节点的 `jsonBody` 开头的 `=` 删掉，触发一次，读返回内容，说明发生了什么。
2. 在「VEO3 替身」后加一个 Code 节点校验 `resultUrls[0]` 以 `.mp4` 结尾，写成断言风格（不符即 throw）。
3. （进阶）把 ffmpeg zoompan 替身换成一个本地 http 生图/生视频服务，保持下游引用的字段名不变，体会"接口契约锁定"的威力。