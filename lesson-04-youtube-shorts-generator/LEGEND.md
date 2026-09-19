# LEGEND · 仓库约定与命名规范

本仓库沿用 n8n 教案工厂的同一套约定，读任何一课前先花 1 分钟看这里。

## 目录约定

| 路径 | 内容 | 只读/可改 |
|------|------|-----------|
| `workflows/` | 可直接导入 n8n 的 JSON | 导入后随便改，源文件勿动 |
| `docs/` | 五讲正文，`00` 是总览 | 只读 |
| `exercises/` | 练习与参考答案 | 可写笔记 |
| `script/` | 短视频口播稿 | 只读 |
| `site/` | GitHub Pages 静态站源码 | 由 Pages 工作流发布 |

## 工作流命名

`original-16419-official.json` / `L2<级别>-<语义>-16419.json`

- **original**：官方 API 实拉解包版，只读参考，**不要直接上生产**（11 个坑未修）
- **级别**：`test`＝A 级单元验证工作流（CLI execute 用） / `free`＝C 级免费替身版（界面手跑用）
- **16419**：n8n 官方模板编号

## 分级验证口径（A → C，本课 B 级跳过）

| 级别 | 验什么 | 用什么 | 花费 |
|------|--------|--------|------|
| A 单元级 | 每个可纯计算单元的逻辑与契约 | 离线断言（11 单元 90 项） | 0 |
| ~~B 全链 mock~~ | 拓扑、路由、坑点复现 | —— | **已跳过**：A 覆盖纯计算、C 覆盖真依赖，mock 层边际价值不足（生产决策留档） |
| C 免费真跑 | 真实 API + 真实工件 + 质量闸 | 付费节点全部换免费替身 13 节点 | ≈0 |

## 凭证标注

- 交付工作流中 DeepSeek 凭证引用占位 id **`fra8VO4w0TLBP9JO`**（挂为 HTTP Header Auth，baseURL `https://api.deepseek.com`）。
- ⚠️ 该 id 只在工厂本机有效。**学员导入后必须**：Credentials → 新建 Header Auth（`Authorization: Bearer <你的 DeepSeek Key>`）→ 在工作流中替换引用。
- 仓库内任何文件都不包含明文 API Key；发现明文即视为事故，立刻撤销并轮换。

## 质量闸与台账口径

- L2C 的 `ledger.json` 是本课的"台账"：每个断言逐项记录 `{gate, ok, detail}`，终态要求 `all_passed=true`。
- **MockGate 约定**：免费版缺真实凭证（如 YouTube OAuth）时，对应环节降级为 mock 且**必须留 `mock=true` 痕迹**；闸门统计时 mock 项单独标记，永不计入"真实通过"。
- 时长口径：TTS 目标 ≈60s（edge-tts `rate=+8%` 下 112 词 ≈ 52.6s 为正常区间）；ffmpeg 合成以 `-t 60 -shortest` 双保险截齐；`VIDEO_SEC` 与 `AUDIO_SEC` 差值 >2s 即判异常。