# 第五讲 · 坑与防御（11 个实证坑 + 2 个工具坑 + 加固清单）

> 本讲是全课压轴：**11 个模板坑 + 2 个工具层坑，全部实证在案**（L2A 90 断言 / L2C 16 闸门逐条验证）。
> 读法：每条给「现象 → 根因 → 引爆条件 → 加固 → 验证出处」。

---

## 1. 模板坑全表

| # | 位置 | 一句话 | 危险度 |
|---|---|---|---|
| ① | Pexels 取值 | `video_files[0]` 盲取——orientation 只在搜索级生效，必出横屏 | ★★★ |
| ② | fal 轮询环 | 只有 COMPLETED 分支——失败任务 30s 永久空转烧钱 | ★★★ |
| ③ | Check Status 请求 | 状态 URL 末尾空格 + Content-Type 塞 query | ★★ |
| ④ | Voiceover vars | `channelName='XXX'` 硬编码进片尾句（社死级） | ★★★ |
| ⑤ | Text-to-Speech | ElevenLabs 只给 form-urlencoded body，必 400 | ★★ |
| ⑥ | Structured Parser | 无 required/maxLength——"60 字符/150 词"是注释级 | ★★ |
| ⑦ | Set Audio Url | 依赖 `$binary` 隐式回捞 + 作者 BunnyCDN 桶硬编码 + FTP 输出无 binary | ★★★ |
| ⑧ | keywords | 中文关键词必 0 结果，无代码兜底 | ★★ |
| ⑨ | 口径/时长 | 60s 与 150 词不一致、素材窗与音频时长无校验 | ★★ |
| ⑩ | YouTube Upload | `categoryId=17`/`regionCode=IT` 硬编码、无 `#shorts`/`privacyStatus` | ★★ |
| ⑪ | 轮询环内引用 | `$('Node').item` 多 item 报错/断链 | ★★ |

## 2. 逐坑拆解

### 坑① video_files[0] 盲取（★★★）
- **现象**：搜索带 `orientation=portrait`，取素材却 `video_files[0].link`，成片横屏。
- **根因**：orientation 过滤的是"这条素材拍的是竖是横"，`video_files` 数组是**文件级分辨率**，两回事；`[0]` 通常是 UHD 原始档。
- **引爆**：任何竖屏 Shorts 场景原样跑模板。
- **加固**：取值级 `filter(f=>f.width<f.height)` + 文件级 ffprobe 校验（第三讲双闸）。
- **验证**：L2A-U7 对实拉样本跑模板表达式，100% 命中横屏档。

### 坑② fal 轮询环无失败出口（★★★）
- **现象**：合成任务 FAILED 后，工作流每 30 秒轮询一次，**永不退出**。
- **根因**：if 节点只给了 COMPLETED 出口，FAILED/CANCELLED 全走 false 回环。
- **引爆**：fal 任务失败（余额不足/素材不合法/队列超时）。
- **加固**：换同步 ffmpeg（L2C 做法，环消失）；或补 FAILED 分支 + 最大轮询熔断。
- **验证**：模板结构静态分析（L2A-U9）+ L2C 拆环后真跑。

### 坑③ 状态 URL 末尾空格 + Content-Type 塞 query（★★）
- **现象**：轮询请求偶发 404/415。
- **根因**：URL 字符串末尾空格未 trim；`Content-Type` 被拼进 query 而非 header。
- **加固**：URL trim；Content-Type 回 header 参数位；用请求节点的 options 而非手写串。
- **验证**：L2A-U9 参数扫描断言。

### 坑④ channelName='XXX' 硬编码（★★★·社死级）
- **现象**：每条成片结尾念出"XXX"。
- **根因**：`Voiceover vars` 片尾句拼接用了字面量，变量抽取没做完。
- **加固**：channelName 收进 Set vars，片尾句 `=` 表达式引用。
- **验证**：L2A-U5 片尾句拼装断言。

### 坑⑤ ElevenLabs form-urlencoded 必 400（★★）
- **现象**：TTS 请求 400。
- **根因**：HTTP 节点 body 配的是表单参数，ElevenLabs 要 JSON。
- **加固**：`sendBody=json`；或换 edge-tts（L2C，坑消失）。
- **验证**：L2A-U6 节点配置扫描。

### 坑⑥ Parser 无强约束（★★）
- **现象**：标题超 60 字符/脚本超 150 词照样放行。
- **根因**：schema 缺 required 与 maxLength，限制只写在 system prompt（提示词级 ≠ 结构级）。
- **加固**：产稿后接 Code 断言闸（必填 + 词数 ≤150 + 标题 ≤60），不过即重 roll（L2C `Gate: Script`）。
- **验证**：L2A-U2 schema 完整性 + 反面用例。

### 坑⑦ audio_url 的 `$binary` 隐式链（★★★）
- **现象**：audio_url 静默为空，成片无声。
- **根因**：取值依赖 `$binary` 跨节点隐式回捞；BunnyCDN 桶/PATH 硬编码；FTP 节点本身不输出 binary。
- **加固**：显式字段引用 + 桶名变量化；替身方案删 FTP 段后此坑连根消失（L2C）。
- **验证**：L2A-U4 外链契约专项。

### 坑⑧ 中文关键词必 0 结果（★★）
- **现象**：素材搜索零命中，流程空转。
- **根因**：Pexels/Mixkit 是英文库，中文关键词无结果，模板无兜底。
- **加固**：prompt 强约束英文关键词 ×3 + 闸门正则校验 + 全灭回落默认素材（第二讲第 8 节）。
- **验证**：L2A-U3 keywords 约束断言。

### 坑⑨ 双口径不一致 + 时长无校验（★★）
- **现象**：system prompt 说"60 秒"、schema 注释说"150 词"；素材 12s 配 55s 音频照样合成。
- **根因**：两处口径没人对齐；合成环节无长短轨断言。
- **加固**：词数锚定时长（`+8%` 语速下 112 词≈52.6s）；`-t 60 -shortest`；合成后 `|VIDEO_SEC-AUDIO_SEC|≤2s` 台账断言。
- **验证**：L2A-U2/U10 + L2C 台账（差 0.004s）。

### 坑⑩ YouTube 硬编码（★★）
- **现象**：视频归"体育"类、推流到意大利、无 `#shorts`、默认 public。
- **根因**：categoryId=17、regionCode=IT 字面量；metadata 字段缺失。
- **加固**：第四讲修参清单（分类/地区/描述/隐私四件套）。
- **验证**：L2A-U10 节点参数扫描。

### 坑⑪ 环内 `.item` 断链（★★）
- **现象**：多 item 批次下轮询环报错或指错对象。
- **根因**：`$('Node').item` 在环里对多 item 解析不唯一。
- **加固**：用 `$json`（当前 item）而非 `.item` 回捞；批次先收敛到单 item 再进环。
- **验证**：L2A-U9。

## 3. 工具层坑（2 个，跑验证时发现）

| 坑 | 真相 | 正确姿势 |
|---|---|---|
| n8n Code 节点里 `this.helpers.httpRequest` 的报错状态码 | **在 `e.httpCode`，不在 `e.response.statusCode`** | 异常处理读 `e.httpCode` |
| n8n CLI 与主实例 broker 端口冲突 | 主实例占 5689 时，CLI execute 僵死 | CLI 前设 `N8N_RUNNERS_BROKER_PORT=5690`（Windows: `$env:N8N_RUNNERS_BROKER_PORT="5690"`） |

## 4. 上线加固清单（checklist）

- [ ] Parser 后接断言闸：必填/词数/标题长/关键词英文
- [ ] 素材双闸：取值滤竖屏 + 文件级 ffprobe
- [ ] 时长三防：FOOTAGE≥min(AUDIO,60) → `-t 60 -shortest` → 合成后 2s 差断言
- [ ] 合成失败有红有响（ffmpeg 同步 或 fal 环补 FAILED+熔断）
- [ ] audio 源显式字段传递，不碰 `$binary` 回捞
- [ ] channelName 变量化，片尾句走表达式
- [ ] YouTube 四件套：categoryId/regionCode/description(#shorts)/privacyStatus
- [ ] ledger.json 台账逐项留痕，mock 项显式标记
- [ ] 全链错误网：至少接一条错误输出到 IM/邮件

## 动手练习

1. 从 11 坑里任选 3 个，写出"如果不修，上线一周内最可能被谁（哪个外部条件）触发"。
2. 把 checklist 转成你团队 Code Review 的 5 条 rule，说说每条对应哪一坑。