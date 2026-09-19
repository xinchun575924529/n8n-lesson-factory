# n8n 实战课 · 一句话生成 YouTube Shorts 竖屏短视频工厂

> 模板：n8n 官方 #16419「Generate YouTube Shorts from Prompts with OpenAI」。
> 你在表单里丢一句 prompt，AI 写 60 秒口播稿 → ElevenLabs 配音 → Pexels 找竖屏素材 → AI 合成音视频 → 一键传 YouTube。
> **本课定位：英文 / 出海线试销课。** 不只教你跑通模板，更教你**不花一分钱把它验证透、替身透、修稳**：A 单元级 90 断言 + C 免费真跑 16 断言全绿，实产 1080×1920 / 52.6s 竖屏成片。

> ⚡ **照妖开场**：官网页面标称 **32 节点**，API 实拉只有 **25 个**（18 业务节点 + 7 便签贴）。这节课从"节点数都敢虚标"开始——永远以 API 实拉为准，别信页面截图。

---

## 学完你将掌握什么

### 技术点
1. **表单触发 + AI Agent 产稿双件套**：OpenAI Chat Model 挂 Structured Output Parser 输出 `{title, script, keywords}`；但 parser 没写 required/maxLength——"60 字符标题 / 150 词脚本"只是**注释级约束**（坑⑥）。生产环境必须自建断言闸门，别指望 schema 自觉。
2. **TTS 外链的脆弱三连环**：ElevenLabs 只配了 form-urlencoded body（HTTP 节点缺 JSON 头必 400，坑⑤）→ FTP 上传 → 音频 URL 依赖 `$binary` + 作者 BunnyCDN 桶硬编码（坑⑦）。任何一环脱节，下游合成静默拿到空音频。
3. **搜索级 vs 文件级的竖屏真相**：Pexels 的 `orientation=portrait` **只在搜索级生效**；模板盲取 `video_files[0]` 必然出横屏（坑①）。唯一可靠阀门 = 下载后 ffprobe 做**文件级**竖屏校验。
4. **轮询环的空转风险**：fal.run 合成状态轮询只有 COMPLETED 分支——失败任务每 30 秒永久打转（坑②）；叠加状态 URL 末尾空格、Content-Type 塞 query（坑③）与 `.item` 多 item 断链（坑⑪），模板原样上生产等于埋雷。
5. **付费点替身术（零成本验证）**：OpenAI→DeepSeek(json_object)、ElevenLabs→edge-tts、Pexels(无 key 实测 401)→Mixkit 竖屏页+ffprobe 校验、fal 轮询环→本机 ffmpeg 无环设计、FTP+BunnyCDN 整段删除、YouTube→mock 队列。**核心逻辑 1:1 保留，成本归零。**

### 业务点
1. **出海短视频量产流水线**：一句英文 prompt → 60 秒竖屏 Shorts，直接服务 YouTube Shorts / TikTok 出海内容线。
2. **交付级质检思维**：A（11 单元 90 断言）→ C（13 节点免费真跑 16 闸门 + 6 模型合规）全绿才交付的方法论，是可搬去任何模板的"验厂"姿势。

---

## 前置需要

| 类别 | 要求 |
|------|------|
| 账号（完整版） | OpenAI / ElevenLabs / Pexels API Key / fal.run / FTP+BunnyCDN / YouTube OAuth |
| 账号（免费学习版） | **只需 DeepSeek API Key**（其余全部本地替身），零付费跑通核心逻辑 |
| 时间 | 60 分钟（5 讲 + 练习） |
| 版本 | n8n 1.x 及以上；免费版替身需本地 ffmpeg + ffprobe（或任意视频合成手段） |

> 💡 本课隐藏主线仍是"分级验证"：跟着 `workflows/` 目录的 L2A → L2C 各跑一遍，你会收获比模板本身更值钱的东西——一套把天价模板拆穿、验透、降本的工程方法。（B 级 mock 按生产拍板跳过，理由见 [docs/00](docs/00-overview.md) 第 4 节。）

---

## 课程结构地图

```
n8n-lesson-04-youtube-shorts-generator/
├── README.md                  ← 你在这里
├── LEGEND.md                  ← 仓库约定与命名规范
├── workflows/
│   ├── README.md              级配演示工作流导览（凭证替换指引）
│   ├── original-16419-official.json   ← 官方原版（API 实拉解包，只读）
│   ├── L2A-test-16419.json            ← A 级：11 单元 90 断言单测工作流
│   └── L2C-free-16419.json            ← C 级：免费替身版（真跑全绿）
├── docs/
│   ├── 00-overview.md         全局拆解（实拉节点地图 + 主链 + 双契约 + 凭证映射）
│   ├── 01-intake.md           第一讲·产稿与配音链（Agent+Parser / TTS 三连环 / 坑④⑤⑥⑦⑨）
│   ├── 02-paywall-substitutes.md 第二讲·付费墙替身（DeepSeek/edge-tts/Mixkit/ffmpeg/mock 全案）
│   ├── 03-synthesis-guard.md  第三讲·素材与合成防线（竖屏文件级校验 + 轮询环拆除）
│   ├── 04-publish-matrix.md   第四讲·发布矩阵（YouTube 上传修参 + 出海多平台扩展）
│   └── 05-pitfalls-defense.md 第五讲·坑与防御（11 个实证坑 + 2 个工具坑 + 加固清单）
├── script/
│   └── short-video.md         抖音 60s 口播稿 + 素材清单
├── exercises/
│   └── exercises.md           6 道练习（含参考答案）
└── site/
    ├── index.html             GitHub Pages 静态预览站
    └── app.js
```

每讲统一结构：**先结论 → 再拆解 → 坑点提示 → 动手练习**。

## 立即动手（两条路任选）

| 路线 | 导入 | 花费 | 你会看到 |
|------|------|------|----------|
| A·读+测 | `workflows/original-16419-official.json` + `workflows/L2A-test-16419.json` | 0 | 25 节点全景，跑一遍 90 断言单测 |
| C·真跑免费版 | `workflows/L2C-free-16419.json` | ≈0（只烧 DeepSeek 低价额度） | 真实 API + 1080×1920/52.6s 竖屏成片 + MockGate 拦截演示 |

1. n8n 界面右上角 → **Import from File**
2. 按 [`workflows/README.md`](workflows/README.md) 把 DeepSeek 凭证换成你自己的（交付版默认引用占位凭证 id `fra8VO4w0TLBP9JO`，学员必须替换）
3. L2A 选 CLI `n8n execute --id=...` 或界面手动触发；L2C 点「Start」手动物料生成

## 质检报告

- **A 级 单元验证**：11 单元 / **90 断言全过**（schema 完整性、audio_url 外链契约、Pexels 取值口径、片尾句拼装、YouTube 参数硬编码扫描、官网节点数核查）
- **B 级 mock 全链**：**生产拍板跳过**——A 单元级已覆盖全部可纯计算单元、C 真跑已闭合外部依赖，mock 层边际价值不足
- **C 级 免费真跑**：13 节点 / **16 断言 + 6 模型合规观测全过**（DeepSeek 真调 json_object + edge-tts 真配音 52.6s + Mixkit 真竖屏素材 + ffmpeg 真合成 1080×1920 成片 + MockGate 缺 YouTube 凭证时 100% 拦截）

## 快捷链接

- 模板公开页：[n8n.io/workflows/16419](https://n8n.io/workflows/16419/)
- REST API 拉原始模板 JSON：`https://api.n8n.io/api/workflows/templates/16419`（返回 `{id, name, workflow}` 包装，导入前需解包）
- **累计挖出 11 个模板坑 + 2 个工具层坑**（n8n Code 的 `e.httpCode` / CLI 的 broker 端口冲突），全部收录于 [第五讲](docs/05-pitfalls-defense.md)

---

> 🚀 本仓库由 n8n 教案工厂自动构建：L2 三关验证（2026-09-16）→ L3 课程包打包上线（2026-09-17）。