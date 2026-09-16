# L2-A 单元级验证报告 · 模板 16419（一句话 → YouTube Shorts 竖屏短视频工厂）

- **日期**：2026-09-16 20:5x (Asia/Shanghai)
- **范围**：11 单元 / **90 断言**——表单与变量映射、AI 提示词与输出解析契约、TTS/FTP/素材搜索/合成/上传全链的表达式与结构语义忠实移植
- **测试工作流**：`L2Test164190001`「L2-A 单测 16419 YouTubeShorts (11单元)」，n8n CLI execute **success**
- **结果**：**90 / 90 PASS，0 FAIL**
- **生成器**：`scripts/build-l2-test-16419.py`；源稿 `workflows/wf-l2-test-16419.json`；断言明细 `state/l2-test-16419-A.json`
- **模板 JSON**：`state/factory/templates/template-16419.json`（25 节点 = 14 功能 + 4 set/agent 子节点 + 6 便签 + 1 触发器族）

## 单元覆盖

| 单元 | 移植对象 | 断言 |
|---|---|---|
| U1 | 表单 → Set vars（summary=$json.Prompt / channelName='XXX' / keepOnlySet） | 7 |
| U2 | Agent 输入装配（`Summary: …\nChannel: …`） | 5 |
| U3 | systemMessage 硬规则（150 词 / 前三词钩子 / 禁开场白 / 英文关键词 / 收尾自检） | 10 |
| U4 | Structured Output Parser 手写 Schema 契约（title/script/keyword） | 8 |
| U5 | Voiceover vars 映射 + undefined 传播（n8n 表达式代理语义） | 6 |
| U6 | ElevenLabs TTS 请求构造（硬编码 voiceId / eleven_v3 / header / 鉴权） | 8 |
| U7 | FTP 上传路径 + Set Audio Url 拼接（$binary 元数据依赖） | 8 |
| U8 | Pexels 搜索 URL + `videos[0].video_files[0]` 盲取 | 10 |
| U9 | Merge combineAll 语义 + 30s 轮询环结构（IF 只有 COMPLETED 分支） | 10 |
| U10 | fal.run 合成请求 + 状态查询 URL/头细节 | 9 |
| U11 | Fetch Final / Fetch File / YouTube 上传（跨分支 item 引用 + 硬编码平台参数） | 9 |

## 🔥 挖到的模板坑（教案卖点，11 条已断言固化）

1. **【最值钱】`video_files[0]` 盲取 → 竖屏等于白搜**：Pexels 的 `orientation=portrait` 只在**搜索级**生效，返回的 `video_files` 里混着 sd/hd/uhd 各档（不同 width/height），模板直接取第 0 个 → 很可能拿到 960x540 横屏，塞进 Shorts 工厂输出方形/横屏片。本厂版在合成前加了**文件级 h>w 校验**（C 版实测）。
2. **轮询环只有 `COMPLETED` 分支**：`Check Merge Status` 的 IF 只判 `status === 'COMPLETED'`，fail/error 一律走 false → Wait 30s → 再查，**无最大轮次、无失败出口**：一个失败任务就是 30s 一轮的永久空转（C 版直接删环改直线：本地 ffmpeg 同步出片）。
3. **状态查询 URL 末尾多一个空格**（模板原文 `.../requests/{{ ... }}/status `），且把 `Content-Type` 塞进 **queryParameters**（应是 header）→ 网关严格时 404/鉴权头缺失。
4. **频道名 `XXX` 硬编码**：Set vars 里 `channelName='XXX'`，而 systemMessage 的收尾句是 `Follow {{ $json.channelName }} for more` → 不改就是每条视频片尾念 "Follow XXX for more"（事故级）。
5. **TTS 请求体形态错**：只给 `bodyParameters`（n8n 默认 form-urlencoded），ElevenLabs `/v1/text-to-speech` 要 JSON → 复刻必 400。替代方案（edge-tts）天然规避。
6. **Parser 的 60 字/150 词约束是"注释级"**：手写 Schema 里**没有 `required`、没有 `additionalProperties:false`、没有 maxLength/字数校验**，约束只写在 `description` 里给人读 → 模型漏字段/超长照样通，下游按位置消费即崩。
7. **`audio_url` 三重脆弱**：① 依赖 `$binary.data.fileName/fileExtension`（响应没带就拼出 `/PATH/undefined.undefined`）② FTP Upload 节点输出**没有 binary**，下游却引用 `$binary` → 高风险断链 ③ 域名写死作者 BunnyCDN 桶 `n3wstorage.b-cdn.net/test/`，复刻者不改就是往别人桶里写、对外 404。
8. **中文关键词必然 0 结果**：`encodeURIComponent(keyword)` 把中文转成 `%E5%9F%8E%E5%B8%82…`，Pexels 英文索引搜不到；模板靠 systemMessage "English only" 兜（U3 已断言该条），但**没有代码兜底**。
9. **时长口径自相矛盾**：开头说 "punchy 60-second script"，硬规则却是 "Maximum 150 words"（英文 150 词 ≈ 55-60s，勉强自洽）；且素材窗是 55-65s，与音频实际长度**无任何校验关联** → 音频超 65s 时素材早播完（黑屏/卡尾）。
10. **YouTube 上传参数硬编码**：`categoryId=17`（Sports）、`regionCode=IT`（意大利，作者地区），未设 `privacyStatus`、标题无 `#shorts`、无 vertical 比例强制 → "Shorts 工厂"其实只是普通上传。
11. **环内/跨分支 `$('Node').item` 引用**：状态查询与 YouTube 标题都用 `.item` 定位，多 item 时报 `Can't determine which item to use`；穿 Wait 环后 item linking 亦易断 → 标题/描述变 undefined。

## 对 C 阶段的输入

- 可全删：FTP/BunnyCDN 双节点（本地 ffmpeg 不需要公网音频 URL）、fal.run 三节点 + Wait + IF（整环删除）、YouTube 节点（走本厂 publish-video.py 抖音+B站通道）
- 可平替：OpenAI(gpt-5.4，模板里的未来模型名) → DeepSeek（真调，`response_format=json_object`）；ElevenLabs → edge-tts（免费）
- **必补**：素材文件级竖屏校验、成片规格断言（1080x1920）、音频/成片时长对齐——C 版已实现
- 缺凭证实证：Pexels API 无 key → **HTTP 401**（C 版实测，需人工注册免费 key 或换免 key 素材源）

## 下一步

L2-B mock 全链按老板拍板**跳过**（模板逻辑=一条直线 + 一个轮询环，B 级性价比低），直接进 **L2-C 免费替代真跑**（见 `l2-report-16419-03-C免费版.md`）。