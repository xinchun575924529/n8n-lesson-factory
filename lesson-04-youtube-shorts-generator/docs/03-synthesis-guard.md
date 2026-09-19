# 第三讲 · 素材与合成的防线（坑①②③⑪）

> 本讲是全模板**对生产最危险**的一段：素材取值 + fal.run 轮询合成。结论先行：
> **"搜索级参数"救不了横屏（坑①），"轮询环"会把失败任务永久空转烧钱（坑②）——两处都必须拆掉重建。**

---

## 1. 坑①：`video_files[0]` 盲取 = 必出横屏

**Pexels 返回结构**（搜索命中后每个 video 对象）：
```json
{
  "width": 4096, "height": 2160,
  "video_files": [
    {"id": 123, "quality": "uhd", "width": 4096, "height": 2160, "link": "…横屏原始…"},
    {"id": 124, "quality": "hd",  "width": 2048, "height": 1080, "link": "…"},
    {"id": 125, "quality": "sd",  "width": 640,  "height": 360,  "link": "…"}
  ]
}
```

**模板的写法**：搜的时候加 `orientation=portrait`，取的时候直接 `video_files[0].link`。

**双重错**：
1. `orientation` **只在搜索级生效**（过滤"这条视频拍的是不是竖的"），但 `video_files` 数组里是每个文件自己的分辨率——**取第一个文件与该视频是否竖屏毫无关系**，`[0]` 通常是最大尺寸（横屏原始档）
2. 就算搜索滤过，若素材本身横拍，`[0]` 依然横屏

**实测**（L2A-U7）：对实拉样本跑模板表达式，100% 命中横屏档。

**加固（两道闸，缺一不可）**：
- **取值级**：`video_files.filter(f => f.width < f.height).sort((a,b)=>b.height-a.height)[0]`——先滤竖、再挑最高清
- **文件级**：下载后 `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 footage.mp4`，`width >= height` 即拒收换源（L2C 已示范）

> 教训升华：**凡是"搜索参数"与"文件本体"分离的 API，校验必须落在文件级**。这是可搬去任何素材管线的通用军规。

## 2. 坑②③⑪：fal.run 轮询环三连环

**原版结构**：
```
Merge Audio with Video (POST 提交 fal 任务，拿 request_id/status_url)
  → Wait 30 Seconds
  → Check Video Merge Status (GET status_url)
  → Check Merge Status (if: status === "COMPLETED")
       ├─ true → Fetch Final Video
       └─ false → 回 Wait 继续转
```

**坑②：失败任务永久空转**
if 节点**只有 COMPLETED 有出口**；fal 任务状态为 `FAILED`/`CANCELLED` 时会走 false 分支**永远转下去**——每 30 秒一跳，烧着队列名额和 API 调用费，没人知道。

**坑③：status_url 的隐形炸弹**
模板给状态请求拼 URL 时，示例里 URL **末尾有个空格**，且把 `Content-Type` 塞进了 query 参数而非 header。两个都属"复制即炸"：某些网关容忍，某些直接 404/415。

**坑⑪：环内 `.item` 引用断链**
环里用 `$('Merge Audio with Video').item` 回捞提交时的 body 参数——多 item 批次下 `.item` 解析报错或指错 item，环直接断。

**加固（L2C 的拆法）**：
- **换成同步 ffmpeg**：失败 = 非零退出 = 节点红，**无环可转**。这是本课替身方案里收益最大的一处。
- 若必须留 fal（要它的云端 GPU）：轮询环加"失败分支"（FAILED→Error 输出）、加"最大轮询次数"（如 40 次=20 分钟熔断）、URL 拼装去空格、Content-Type 回 header。

## 3. 时长防线：素材窗 vs 音频长（坑⑨ 延伸）

**问题**：模板没有任何"素材时长够不够盖住音频"的校验。素材 12s、音频 55s → 合成按短轨切，成片 12s 哑一半。

**L2C 三段防线**：
1. 入库前 `ffprobe` 取素材长 `FOOTAGE_SEC`，断言 `FOOTAGE_SEC ≥ min(AUDIO_SEC, 60)` 或确认可按 `-t 60` 截
2. 合成用 `-t 60 -shortest` 双保险（上限 60s、跟短轨走）
3. 合成后 `ffprobe` 回读 `VIDEO_SEC`，断言 `|VIDEO_SEC - AUDIO_SEC| ≤ 2s`

L2C 实测台账：`AUDIO_SEC=52.632`、`VIDEO_SEC=52.636`、差值 0.004s。

## 4. 台账（ledger.json）

L2C 每一步把断言写进 `ledger.json`：

```json
{"PROMPT":"...", "TITLE":"...", "KEYWORDS":["...","...","..."],
 "WORDS":112, "AUDIO":"voice.mp3", "AUDIO_SEC":52.632,
 "FOOTAGE_SOURCE":"mixkit-51500", "VIDEO":"lesson-16419-c.mp4",
 "VIDEO_SPEC":"1080x1920@h264+aac", "VIDEO_SEC":52.636,
 "STATUS":"DONE", "all_passed":true}
```

**台账的意义**：出了问题一行定位；质量闸门逐项留痕；mock 项显式标记永不洗白。

## 动手练习

1. 用 Pexels 任一搜索 JSON 样本，手写"滤竖屏 + 挑最高清"的表达式，与模板 `video_files[0]` 的结果对比。
2. 给 fal 轮询环补一个 FAILED 分支与最大轮询熔断（画连线即可，不用真跑），说明它们各自挡住什么损失。