# 第一讲 · 收图路：Telegram 多档照片的隐形地雷

> 结论先行：**用户发一张图，Telegram 给你的是同一图的 3~5 个分辨率副本（数组），模板两个节点各取一档且互不一致——3 档照片一进来就断链。** 这一讲把收图链拆干净，并给出通用加固写法。

---

## 1. 收图链逐节点

```
Telegram Trigger: Receive Video Idea
  → Set: Bot Token (Placeholder)          ← 集中放 token（但留了空占位）
  → Telegram: Get Image File              ← photo[2].file_unique_id 取文件
  → Telegram API: Get File URL            ← photo[3].file_path 拼下载 URL
  → OpenAI Vision: Analyze Reference Image
  → Google Drive: Upload Image            ← 拿 webContentLink 给下游当 image_urls
```

用户消息里带 caption（创意文字）与 photo（参考图）。caption 直通下游做创意种子；photo 是**数组**：`message.photo = [256px, 512px, 640px, 800px, 1280px]`（档位数量随图片尺寸变化）。

## 2. 坑①复盘：photo[2] vs photo[3]

- `Get Image File` 用 `photo[2]`：拿第三档文件的 `file_unique_id`，同时充当状态机的 `IMAGE NAME`；3 档图时是最后一档，合法。
- `Get File URL` 用 `photo[3]`：拿第四档；**3 档图时 `photo[3]` 是 undefined → 该节点直接断链**；4 档图时两个节点取的是**不同分辨率**（语义分裂）。

B 级 S3 场景精确复现：**断链点在 `Telegram API: Get File URL`，而不是 `Get Image File`**——因为前者档位更高先 undefined。这个「断在谁手上」的细节，是教 Debug 的绝佳素材：不要猜，看 runData。

### 推荐加固写法
```javascript
// Code 节点统一选档：永远取最大档
const photos = $json.message.photo;
const best = photos[photos.length - 1];
return [{ json: { ...$json, photoFileId: best.file_id, photoUniqueId: best.file_unique_id } }];
```
一处选档、全链复用，顺带消灭"两个节点各自索引"的分裂。

## 3. Bot Token 的两个坑（坑③）

- 模板 `YOUR_BOT_TOKEN` 留空占位——导入即忘配。
- token 拼接分散在 `Set: Bot Token` 与 `Telegram API: Get File URL` 两处，改一处漏一处。
- 加固：n8n 的 Telegram 节点用凭证而非手拼 URL；必须手拼时，把 token 放环境变量 `{{$env.TG_BOT_TOKEN}}`。

## 4. Google Drive 过桥的意义

Vision 与 NanoBanana 都要**公网可访问的图片 URL**。Telegram 下载流是二进制，Drive 上传后取 `webContentLink`（需允许任何知道链接的人查看）就是那座桥。免费学习版可跳过 Drive：用本地 file:// 或内网 http 静态服务顶替，逻辑等价。

## 5. 无 caption 也能通链（S2 验证）

caption 为空时模板不炸——LLM 分支自己降级发挥。但注意：如果你给 caption 加闸门（第五讲的 200 符修复），**空 caption 跳过校验**才对，别误伤正常路。

## 坑点提示

- `file_unique_id` ≠ `file_id`：前者是跨 bot 稳定 ID（当台账键很合适），后者是同 bot 内下载凭证（会过期）。
- Telegram 节点拿到的 `photo` 在 `channels`/`posts` 等消息类型下字段路径不同——上线前用真实消息 dump 一遍结构。

## 动手练习

1. 给自己的 bot 分别发一张小图（3 档）与一张大图（5 档），在 Trigger 输出里数 `photo.length`，对照坑①说出 3 档图会断在哪个节点。
2. 把课上加固的"统一选档" Code 节点插进 L2A 模板，替换两处索引，确认两链都引用 `photoFileId`。
3. （进阶）给收图链加一条判断：用户没发图只发文字时，走"无参考图直生成"分支并打标，想想状态机键该用什么替代 `file_unique_id`。