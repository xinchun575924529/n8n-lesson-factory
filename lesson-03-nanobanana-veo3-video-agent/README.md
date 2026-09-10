# n8n 实战课 · 用 NanoBanana + VEO3 + Blotato 构建「一句话成片并全网分发」视频工厂

> 一个真实的 47 节点官方模板，拆解成 A / B / C 三级递进的 5 讲课程：你在 Telegram 里发一张参考图 + 一句话创意，AI 视觉分析 → 生成提示词 → NanoBanana 修图 → VEO3 渲染视频 → 写发布文案 → 一键分发 9 个平台，全程台账留痕。
> 更重要的是：本课不只教你"跑通模板"，还教你**不花一分钱把它验证透、替身透、修稳**。

---

## 学完你将掌握什么

### 技术点
1. **多档位图片收图路**：Telegram `photo` 数组的多分辨率陷阱——`photo[2]` 取文件、`photo[3]` 取 URL，3 档图即断链。学会"模板照妖"第一课。
2. **双层 JSON 提示词契约**：LLM 用 Structured Output Parser 输出 `{title, final_prompt}`，`final_prompt` 本身还是一个完整 JSON（相机/灯光/环境/主体/动效/VFX/音频全健）；`Format Prompt` 的 `JSON.stringify` 加外层引号与 VEO3 body 的无引号注入是生死搭档。
3. **付费墙替身术（零成本验证）**：Vision/LLM 四处 → DeepSeek 等价替换；NanoBanana(fal.run) → ffmpeg 本地合成；VEO3(kie.ai) → ffmpeg zoompan；Sheets → 本地 JSON；Blotato ×9 → 发布队列 JSON。**核心逻辑 1:1 保留，成本归零。**
4. **轮询渲染的防御设计**：模板 `Wait 20s` 单次轮询 + `record-info` 无 `response` 即裸奔抛错——本课给出"循环轮询 + 超时熔断 + 错误网"的加固方案。
5. **状态机台账**：Google Sheets `matchingColumns=IMAGE NAME` 幂等 upsert，`CREATE → Published` 状态闭环，免费版用本地 `records.json` 等价复现。
6. **发布矩阵**：Blotato 一个接口分发 YouTube / TikTok / Instagram / Facebook / LinkedIn / Threads / Bluesky / Pinterest / X 九平台，免费版降级为 `publish-queue.json` 对接自有发布通道。

### 业务点
1. **AI 短视频量产流水线**：从"参考图 + 一句话"到全网分发的完整自动化，可直接服务代运营、电商短视频、UGC 仿拍等场景。
2. **交付级质检思维**：A（44 项单测）→ B（18 项场景断言）→ C（10 项真跑断言）三关全绿才交付的方法论，是可以搬去任何项目的"验厂"姿势。

---

## 前置需要

| 类别 | 要求 |
|------|------|
| 账号（完整版） | Telegram Bot Token / OpenAI（或 DeepSeek）/ fal.run（NanoBanana）/ kie.ai（VEO3）/ Google Drive + Sheets / Blotato |
| 账号（免费学习版） | **只需 DeepSeek API Key**（其余全部本地替身），零付费跑通核心逻辑 |
| 时间 | 60 分钟（5 讲 + 练习） |
| 版本 | n8n 1.x 及以上；免费版替身需本地 ffmpeg（或任意视频合成手段） |

> 💡 **本课的隐藏主线是"分级验证"**：跟着 workflows/ 目录的 L2A → L2B → L2C 三个工作流各跑一遍，你会收获比模板本身更值钱的东西——一套把任何天价模板拆穿、验透、降本的工程方法。

---

## 课程结构地图

```
n8n-lesson-03-nanobanana-veo3-video-agent/
├── README.md                  ← 你在这里
├── LEGEND.md                  ← 仓库约定与命名规范
├── workflows/
│   ├── README.md              级配演示工作流导览（凭证替换指引）
│   ├── L2A-test-8270-original-47nodes.json   ← A 级：原版 47 节点（单测对象）
│   ├── L2B-mock-8270-S1..S5.json             ← B 级：1:1 拓扑 mock × 5 场景
│   └── L2C-free-8270.json                    ← C 级：免费替身版（真跑全绿）
├── docs/
│   ├── 00-overview.md         全局拆解（47 节点地图 + 双主链 + 双 JSON 契约 + 凭证映射）
│   ├── 01-intake.md           第一讲·收图路（photo 多档位坑 + Google Drive 过桥）
│   ├── 02-paywall-substitutes.md 第二讲·付费墙替身（DeepSeek/ffmpeg/本地 JSON 零成本复刻）
│   ├── 03-state-machine.md    第三讲·状态机（CREATE→Published 幂等台账）
│   ├── 04-publish-matrix.md   第四讲·发布矩阵（Blotato 九平台 + 免费队列降级）
│   └── 05-pitfalls-defense.md 第五讲·坑与防御（7 个实证坑 + 加固清单）
├── script/
│   └── short-video.md         抖音 60s 口播稿 + 素材清单
├── exercises/
│   └── exercises.md           6 道练习（含参考答案）
└── site/
    ├── index.html             GitHub Pages 静态预览站
    └── app.js
```

每讲统一结构：**先结论 → 再拆解 → 坑点提示 → 动手练习**。

## 立即动手（三条路任选）

| 路线 | 导入 | 花费 | 你会看到 |
|------|------|------|----------|
| A·读模板 | `workflows/L2A-test-8270-original-47nodes.json` | 0 | 47 节点全景，对照 docs/00 看懂每一处 |
| B·跑 mock | `workflows/L2B-mock-8270-S1.json`（+S2~S5） | 0 | 零凭证跑通全链，亲眼看坑①②③⑤还原 |
| C·真跑免费版 | `workflows/L2C-free-8270.json` | 0（只烧 DeepSeek 免费/低价额度） | 真实 API + 真实成片工件 + 真实状态机闭环 |

1. n8n 界面右上角 → **Import from File**
2. 按 [`workflows/README.md`](workflows/README.md) 把 DeepSeek 凭证换成你自己的（交付版默认引用占位凭证 id `fra8VO4w0TLBP9JO`，学员必须替换）
3. 按对应 docs 讲次操作按钮触发

## 质检报告

- **A 级 单元验证**：10 个单元 / **44 断言全过**（master_prompt schema 完整性、双转义合法性、双档位坑确认、状态机映射核对了）
- **B 级 mock 全链**：5 场景 / **18 断言全过**（正常图文、无 caption、3 档照片引爆坑①、渲染未完成引爆坑②、Caption 超长复现）
- **C 级 免费真跑**：**10 断言全过**（DeepSeek 真 API ×3 + ffmpeg 真成片 + 状态机闭环 + 发布队列落地）

## 快捷链接

- 模板公开页：[n8n.io/workflows/8270](https://n8n.io/workflows/8270/)
- REST API 获取原始模板 JSON：`https://api.n8n.io/api/workflows/templates/8270`
- **累计挖出 7 个模板/实战真坑**（A 级 4 个 + B 级 3 个，C 级附赠修复示范），全部收录于 [第五讲](docs/05-pitfalls-defense.md)