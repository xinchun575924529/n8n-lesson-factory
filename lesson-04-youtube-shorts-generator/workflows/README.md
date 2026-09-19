# workflows/ · 级配演示工作流导览

三个 JSON 三种用法：**一个用来看，一个用来测，一个用来跑**。

| 文件 | 级别 | 用法 | 会不会真花钱 |
|------|------|------|--------------|
| `original-16419-official.json` | 原版 | **只读参考**。官方 API 实拉解包，11 个坑原样保留——别直接上生产 | 导出不跑=0；真跑=烧 5 家付费 API |
| `L2A-test-16419.json` | A 级 | **单元验证**。11 个单元复刻模板全部可纯计算逻辑，90 项离线断言 | 0（无外部调用） |
| `L2C-free-16419.json` | C 级 | **免费真跑**。13 节点付费点全替身，真实产出 1080×1920 竖屏成片 | ≈0（只烧 DeepSeek 低价额度） |

## 导入与触发

### original（读）
- 导入后对照 `docs/00-overview.md` 的节点地图读每一处配置。
- ⚠️ 你会发现官网标 32 节点、实拉 25（18 业务 + 7 便签）——这不是仓库缺斤短两，是模板页面虚标，第一课从这儿教起。

### L2A（测）
- 触发方式：CLI `n8n execute --id=<导入后的工作流ID>`（节点含 scheduleTrigger 时会拒绝手动跑，CLI 最稳）。
- 期望输出：末节点打印 `A_RESULT`，`assertions_passed=90 / failed=0`。
- 想体会坑：先读 `docs/05-pitfalls-defense.md`，再回来看每个单元断言是"怎么把坑按在地上验证的"。

### L2C（跑）
- 前置（三件套）：
  1. **DeepSeek 凭证**：Credentials → 新建 **Header Auth**（Name=`Authorization`，Value=`Bearer sk-你的key`，baseURL 用 `https://api.deepseek.com`），然后在 `Gen Script (DeepSeek)` 等节点把占位凭证 `fra8VO4w0TLBP9JO` 换成你的。
  2. **ffmpeg + ffprobe**：本机 PATH 可用（合成与竖屏校验靠它）。
  3. **edge-tts**：`pip install edge-tts`（Python 3.8+；配音替身为本地 TTS CLI）。
- 触发：手动点「Start」节点。
- 期望末态：`ledger.json` 全盘 `all_passed=true`，产出目录里有 `voice.mp3`（≈52s）、`footage.mp4`（720×1280 竖屏）、`lesson-16419-c.mp4`（1080×1920 / h264+aac 成片）。
- 没有 YouTube OAuth 时自动走 mock 发布并留痕；有凭证想真传，参照 `docs/04-publish-matrix.md` 的修参清单（categoryId/#shorts/privacyStatus）。

## 常见排错

| 症状 | 先看哪 |
|------|--------|
| DeepSeek 节点 401/403 | 凭证是不是 Header Auth 挂在 `Authorization`、Key 是否带 `Bearer ` 前缀 |
| edge-tts 命令不存在 | `pip install edge-tts` 后重开 n8n（PATH 要刷新） |
| footage ffprobe 报横屏 | Mixkit 素材被换源——重跑或换 `FOOTAGE_SOURCE` 候选（见 docs/03） |
| 合成时长=0 | ffmpeg 日志看 `-shortest` 是否把空音轨截没了（坑⑦ 的免费版防线） |