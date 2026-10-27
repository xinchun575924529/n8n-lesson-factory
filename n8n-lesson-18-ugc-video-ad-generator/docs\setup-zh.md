# 中文搭建教程 · UGC 竖屏广告视频生成器

## 前置条件
- n8n ≥ 2.33（本课用 2.33.3 验证）
- DeepSeek API key（platform.deepseek.com，充 ¥10 够用很久）
- ffmpeg（本地视频生成用，可选）

## 步骤 1：导入模板
1. n8n → Import from URL → 粘贴 `https://n8n.io/workflows/21388/`
2. 或 Import File → 选 `template-21388-original.json`

## 步骤 2：替换 OpenAI → DeepSeek
1. 删 `OpenAI Chat Model` 节点
2. 加 HTTP Request 节点 `DeepSeek API`：
   - URL: `https://api.deepseek.com/v1/chat/completions`
   - Method: POST
   - Headers: `Authorization: Bearer YOUR_KEY`、`Content-Type: application/json`
   - Body (JSON):
```json
{
  "model": "deepseek-chat",
  "messages": [{"role":"user","content":"PROMPT_HERE"}],
  "response_format": {"type":"json_object"},
  "max_tokens": 1000
}
```
3. 加 Code 节点 `Parse DeepSeek`：
```js
const r = $input.first().json;
const parsed = JSON.parse(r.choices[0].message.content);
return [{ json: { output: parsed } }];
```

## 步骤 3：替换 Sisif → ffmpeg（免费版）
Sisif.ai 是付费视频渲染 API。免费替身：本地 ffmpeg 预生成占位视频。

```bash
ffmpeg -f lavfi -i "color=c=blue:s=720x1280:d=5" -vf "drawtext=text='Variant 1'" -c:v libx264 -y variant_1.mp4
```

将 Mock Create Sisif Video 的 Code 节点指向本地文件路径。

## 步骤 4：替换 Slack 审批
模板用 Slack `sendAndWait`（阻塞式）。免费替身：飞书群审批卡片。

Slack 节点 → 换成 HTTP Request 调飞书 OpenAPI 发卡片消息 → 等 webhook 回传审批结果。

## 步骤 5：IG 发布（可选）
Instagram Graph API 需要：
- 海外 Facebook 开发者账号
- IG 商业账号 + 企业验证
- `pages_read_engagement` + `instagram_basic` + `instagram_content_publish` 权限

国内暂不可行，可先用 Mock 或跳过。

## 模板坑提醒
1. **prompts < 3 条** → Split Into Variants 静默只出 2 条，无守卫
2. **Start Poll Counter 丢字段** → 无 `includeOtherFields`，自定义字段被清
3. **PROCESSING 状态** → Collect Variant 归一为 TIMED_OUT，不区分真超时