# 立项报告 · 3442 全自动AI视频生成与多平台发布

- **项目编号**：3442
- **官方名称**：Fully automated AI video generation & multi-platform publishing
- **工作流内名**：AI-Powered Short-Form Video Generator with OpenAI, Flux, Kling, and ElevenLabs and upload to all social networks
- **来源**：https://n8n.io/workflows/3442/ （官方模板库，可拉取 ✅，2026-09-11 实测 200）
- **定选方式**：fresh 候选 → B·立即研发（2026-09-11 05:17，ou_5051…）

## 一、这是干什么的

「全自动短视频工厂」的教科书级样板：每天定时从 Google Sheet 里取一个选题（idea），然后一条龙自动跑完：

1. **选题进料**：ScheduleTrigger（每天7点）→ Google Sheets 读 `production=for production` 的行（idea + environment_prompt）
2. **文案**：OpenAI gpt-4o-mini 生成 5 条 POV 字幕（钩子→行动→爽点结构）→ Code 拆成 5 个 item → IF 校验格式
3. **图片**：OpenAI o3-mini 把 5 条字幕扩写成 Flux 提示词 → Code 汇总 token 用量 → PiAPI 调 `Qubico/flux1-dev` 文生图（540×960 竖图）→ 轮询+失败重试（Wait 3min/5min + IF）
4. **视频**：PiAPI 调 `kling`（v1.6 pro 模式，5秒，zoom=5 运镜）图生视频 → Wait 10min 轮询+失败重试
5. **配音**：OpenAI 生成 15 秒口播稿 → ElevenLabs TTS 生成 mp3 → 传 Google Drive 并开共享
6. **合成**：Merge 按位置配对 视频+字幕+音频 → Creatomate 模板渲染成片 → 轮询取回 → 存 Google Drive
7. **回写**：更新 Google Sheet（production=done、publishing=for publishing、token 成本明细）
8. **发布**：OpenAI 读视频生成描述 → 经 **upload-post.com** 一个接口并发上传到 TikTok / Instagram / YouTube / Facebook / LinkedIn → Discord webhook 通知

## 二、节点清单（51 个 = 7 便签 + 44 功能）

| 环节 | 节点 | 类型 |
|---|---|---|
| 触发 | Once Per Day | scheduleTrigger |
| 进料/回写 | Load Google Sheet, Update Google Sheet | googleSheets ×2 |
| LLM ×5 | Generate Video Captions / Generate Image Prompts / Generate Script / Get Audio from Video(转写) / Generate Description for Videos | langchain.openAi（gpt-4o-mini、o3-mini） |
| Code ×4 | Create List, Calculate Token Usage, List Elements, List Elements1 | code |
| PiAPI 图像 | Generate Image, Get image, Check for failures, Wait 3min, Wait 5min | httpRequest ×2 + if + wait ×2 |
| PiAPI 视频 | Image-to-Video, Get Video, Fail check, Wait 10min, Wait to retry | httpRequest ×2 + if + wait ×2 |
| 配音 | Generate voice, Upload Voice Audio, Set Access Permissions | httpRequest + googleDrive ×2 |
| 合成 | Match captions with videos, Pair Videos with Audio, Render Final Video, Wait1, Get Final Video, Get Raw File, Upload Final Video, Set Permissions | merge ×2 + httpRequest ×3 + wait + googleDrive ×2 |
| 发布 | Write video, Read Video from Google Drive, Upload to Tiktok/Instagram/Youtube/Facebook/Linkedin | writeBinaryFile + readBinaryFile + httpRequest ×5 |
| 其他 | Set API Keys（4个key集中存 Set 节点）、Notify me on Discord、Validate list formatting、Sticky ×7 | set / discord / if / stickyNote |

## 三、凭证缺口与替代方案（能免费不付费）

| 原版依赖 | 用途 | 替代方案 | 费用 |
|---|---|---|---|
| OpenAI API（gpt-4o-mini + o3-mini + whisper 转写） | 字幕/提示词/口播稿/描述/转写 | **DeepSeek deepseek-chat 直连**（现成 key，余额充足）；whisper 转写可删（仅用于生成描述，可用标题/字幕文本代替） | ✅ 免费 |
| Google Sheets | 选题队列表 | **本地 JSON 队列**（state\3442-data\ideas.json）或飞书多维表 | ✅ 免费 |
| Google Drive（4节点） | 音频/成片中转+共享链接 | **本地文件系统**（readBinaryFile/writeBinaryFile 节点本来就在用本地盘，Drive 纯属中转，可直接跳过） | ✅ 免费 |
| ElevenLabs TTS | 英文口播 | **edge-tts 晓晓/云希**（已在教案01/02 实战验证） | ✅ 免费 |
| PiAPI（Flux 文生图） | 5 张 540×960 图 | **AutoDL ComfyUI z_image_turbo**（已验证 13 秒/张）或 Seedream（image-gen）；按量开机用完即关 | ✅ 免费/极低成本 |
| PiAPI（Kling 图生视频） | 5 段 5 秒视频 | **豆包/即梦 Seedance（video-gen skill）**或 ComfyUI 图生视频模型；⚠️ 这是本项目**最大成本与质量不确定点** | ⚠️ 待选 |
| Creatomate（模板渲染合成） | 5段视频+音频+字幕合成 | **ffmpeg 本机合成**（compose 管线已成熟，lesson-01/02 复用） | ✅ 免费 |
| upload-post.com（$15/月） | 一键发 5 平台 | **本厂浏览器通道**：抖音 dlg-upload + B站浏览器投稿（均已实战）；FB/IG/LinkedIn/YT 本厂无账号可砍 | ✅ 免费 |
| Discord webhook | 完成通知 | **飞书群推送**（factory-sync.py feishu） | ✅ 免费 |

**结论：整条链可做到零付费**（DeepSeek + edge-tts + AutoDL 图 + ffmpeg + 浏览器发布），唯一待拍板的是**图生视频引擎**（Seedance 现成 vs ComfyUI 自部署折腾）。

## 四、风险点（排雷预习）

1. **内容调性不合**：模板 prompt 是 Andrew Tate 风格的英文「求职 POV」内容（粗口/性暗示都写进 prompt），面向 TikTok 英文受众——教案化必须整段重写 prompt（中文选题/中文口播/国内平台调性），这不是替换节点而是重写内容策略
2. **PiAPI 轮询节奏脆弱**：Wait 3min/10min 是固定等待+失败重试，Kling 渲染慢时整体一轮可能 30min+；mock 阶段要重点演
3. **Merge combineByPosition**：视频/字幕/音频三条链按位置硬配，任何一条链少一个 item 就错位（17522 挖过的同类坑）
4. **Create List 拆字幕**：LLM 返回若带引号/emoji/行数≠5，Validate IF 直接拦停——对 DeepSeek 输出格式要在 mock 里演练
5. **Set API Keys 用 Set 节点明文存 key**：教案要指出这是坏实践（应用 Credentials），本厂版直接删
6. **upload-post 5 平台并发上传**：本厂只保留抖音+B站，节点从 5 砍到 2，且改为浏览器通道（不在这套工作流里）
7. **token 成本统计依赖 OpenAI usage 字段结构**：DeepSeek 返回结构相同（openai 兼容），基本可平移，但 o3-mini 的 reasoning token 统计会丢（无所谓，教案里说明）

## 五、L2 验证计划

- **A 单元级**：忠实移植 4 个 Code 节点（Create List / Calculate Token Usage / List Elements / List Elements1）+ 2 个 IF 判定逻辑，喂构造数据断言。**预计 ~30 断言，零依赖，当天可出**
- **B mock 全链**：全图保留，外部节点全 mock（Sheets→本地JSON、OpenAI→假响应、PiAPI→假任务回包、ElevenLabs→假音频、Creatomate→假渲染、Drive→本地文件、upload-post→假200），场景覆盖：正常流 / 图像失败重试 / 视频失败重试 / 字幕格式校验拦截
- **C 免费版真跑**：DeepSeek×2（字幕+口播稿）+ edge-tts 真音频 + AutoDL z_image_turbo 真图（可选）+ ffmpeg 真合成（拼接占位视频段+真音频+字幕）→ 产出真实 mp4 工件。**图生视频环节 C 阶段用占位视频 mock（标注「生产环境替换为 Seedance」），除非拍板直接接 Seedance**

**推荐路径：A → B → C 全做**（沿用 8270 三关模式；本项目链路比 8270 长，B/C 价值更大）

## 六、决策点（等拍板）

1. L2 验证路径：推荐 **A+B+C 全做**，同意？
2. 图生视频引擎：C 阶段**占位 mock**（最省）还是直接接 **Seedance**（video-gen skill，有真实产出但花积分/时间）？
3. 内容调性：教案是「照抄原版英文求职POV调性」还是「改造成中文通用模板」？推荐：**原版逻辑讲透 + 提示词中文改造**（教案受众是国内用户）