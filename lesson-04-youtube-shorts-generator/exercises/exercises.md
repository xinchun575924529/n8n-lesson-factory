# 练习与参考答案（16419 · 共 6 题）

> 做题顺序建议按讲次推进。答案附在每题之后（折叠前先自己想）。

---

## 练习 1（对应 00 讲）：实拉照妖

**题目**：用 `https://api.n8n.io/api/workflows/templates/16419` 拉取模板，数出业务节点与便签贴各多少，与官网页面标称值对比；再找出 `Set Audio Url` 的取值表达式，列出它依赖的上游节点链。

**参考答案**：
- 实拉 25 节点 = 18 业务 + 7 便签（Sticky Note/1/2/3/4/5/8，还跳号）；官网标 32 属页面口径虚标
- `Set Audio Url` 依赖：`Upload audio`(FTP 的 path) + `$binary`(实际指向 `Text-to-Speech` 的二进制输出)；中间插入任何清洗节点，`$binary` 即漂
- 教训：**以 API 实拉为准；跨节点取值只信显式字段**

## 练习 2（对应 01 讲）：给 Parser 加真约束

**题目**：原模板的 Structured Output Parser schema 没有 required/maxLength。请写出修复后的 JSON Schema，并说明"提示词级约束"与"结构级约束"的差别。

**参考答案**：
```json
{
  "type": "object",
  "required": ["title", "script", "keywords"],
  "properties": {
    "title": {"type": "string", "maxLength": 60},
    "script": {"type": "string"},
    "keywords": {"type": "array", "minItems": 3, "maxItems": 3,
      "items": {"type": "string", "pattern": "^[a-z ]+$"}}
  }
}
```
- 提示词级 = 模型的"愿望"，可被模型状态/上下文打败；结构级 = schema/代码闸门，**不通过就不存在输出**
- 词数（≤150）schema 表达不了，需产稿后 Code 断言（这也正是 L2C `Gate: Script` 做的事）

## 练习 3（对应 02 讲）：替身迁移

**题目**：把 L2C 的 DeepSeek 换成你常用的另一家 OpenAI 兼容端（如 Moonshot/智谱），需要改动哪几处？为什么当时选择 HTTP 节点 + Header Auth 而不是 LangChain OpenAI 节点？

**参考答案**：
- 改动 3 处：① 凭证（Header Auth 的 Key）② 请求节点 baseURL ③ 模型名（`deepseek-chat`→ 对端模型）
- 选 HTTP+Header Auth 的理由：通用性——任何 OpenAI 兼容端零改动可换；不依赖 n8n 版本对 LangChain 节点的 schema 透传行为
- `response_format=json_object` 若对端不支持，退路是 system prompt 强约束 + 产稿后 `JSON.parse` 断言闸

## 练习 4（对应 03 讲）：手写竖屏取值

**题目**：给定 Pexels 单条 video 的 JSON（含 `video_files` 混排多分辨率），写出取"最高清竖屏文件"的 n8n 表达式；再补一条 ffprobe 校验命令。

**参考答案**：
```js
// 取值级
$json.video_files
  .filter(f => f.width < f.height)
  .sort((a, b) => b.height - a.height)[0].link
```
```bash
# 文件级
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 footage.mp4
# 输出 width,height；width >= height 即拒收
```
- 军规：搜索参数与文件本体分离的 API，校验必须落在文件级

## 练习 5（对应 04 讲）：发布修参 diff

**题目**：原版 `Upload a video` 要变成"面向美国市场的教育类 Shorts，先私测后公开"，列出全部要改的参数及值。

**参考答案**：
- `categoryId`: `17` → `27`（Education）
- `regionCode`: `IT` → `US`
- `description`: 新增（脚本摘要 + `#shorts` + 频道尾版）
- `privacyStatus`: 新增 `unlisted`（首发私测）→ 人工过审 → `public`
- tags：新增（keywords 三项 + shorts）
- 校验：成片 9:16、≤60s、h264+aac（第三讲台账已断言）

## 练习 6（对应 05 讲）：给轮询环补失败出口

**题目**：不改用 ffmpeg 的前提下，给 fal 轮询环设计"失败出口 + 熔断"，画出分支逻辑并说明各自挡住的损失。

**参考答案**：
```
Check Video Merge Status
 → if: status === COMPLETED → Fetch Final Video
 → else if: status ∈ {FAILED, CANCELLED} → Error 输出（挡：永久空转烧 API 费）
 → else → 计数器+1
      → if: 次数 > 40 → Error 输出（挡：fal 侧卡死时无限等待，40×30s=20min 熔断）
      → else → Wait 30s 回环
```
- 计数器放 Function/Code 节点写入 `$json.poll_count` 随 item 流动
- Error 输出统一接告警（邮件/IM），错误网才算闭环

---

> **附加挑战**：把本课的 11 坑加固清单整理成你团队的 n8n Code Review checklist（5~8 条），提交到你们的工程规范仓库。