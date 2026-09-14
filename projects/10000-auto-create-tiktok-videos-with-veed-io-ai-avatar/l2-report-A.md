# L2-A 单元级验证报告 · 模板 10000（AI数字人短视频自动工厂）

- 日期：2026-09-14 15:37 (Asia/Shanghai)
- 测试工作流：`L2Test100000001`「L2-A 单测 10000 TikTok VEED (9单元)」，CLI execute 一次性跑通
- 结果：**47 / 47 PASS，0 FAIL**（首次执行即全过）
- 生成器：`scripts\build-l2-test-10000.py`；工作流源稿：`workflows\wf-l2-test-10000.json`

## 单元覆盖（9 单元 47 断言）

| 单元 | 移植对象 | 断言数 |
|---|---|---|
| U1 | Extract Photo and Theme（photoUrl 取最大尺寸 / theme 三级兜底 caption→text→'viral content'） | 7 |
| U2 | Convert .mpga to .mp3（Code 节点逐字移植：改名/mime/保留原属性/无二进制透传/默认文件名） | 7 |
| U3 | tmpfiles.org URL 改写正则（FAL 节点内联） | 5 |
| U4 | Perplexity 热点提示词构造 | 3 |
| U5 | GPT 脚本提示词 + ElevenLabs TTS 请求构造（url/headers/body） | 7 |
| U6 | FAL.ai 渲染请求体（image/audio URL 改写 + 480p + 鉴权头） | 4 |
| U7 | VEED 轮询 URL + Wait 配置 | 2 |
| U8 | Google Sheets 列映射 + STATUS 回写 | 5 |
| U9 | Workflow Configuration 语义 + Send video + Blotato 9 平台扇出 + Merge1 | 7 |

## 挖出的模板坑（教案素材，6 个已断言固化）

1. **[U3] tmpfiles 正则只认 `http://` 且路径必须数字开头**：上游若返回 `https://` 或已含 `/dl/` 的链接，改写静默不生效 → FAL 拿到不可下载的 URL。第三方免费服务返回值一变就断链。
2. **[U4] Perplexity 提示词直接拼 `message.caption`**：用户只发文字不发 caption 时拼出字面 `undefined`，不走 'viral content' 兜底（兜底只存在于 theme 字段）。
3. **[U5] `config.scriptMaxDuration=30` 是死配置**：prompt 里「30-second」是硬编码文本，改配置节点毫无作用。
4. **[U6] FAL Authorization 发裸 key**：官方文档要求 `Key <apikey>` 格式，模板疑似 bug（未真跑验证，C 阶段/mock 均按模板原样断言）。
5. **[U6] 分辨率 480p 硬编码**，想高清只能改节点表达式。
6. **[U8] Sheets 的 IDEA 列取 `message.caption`**：text-only 输入时 IDEA=undefined 入表，主题兜底字段 theme 同样没被用到。

## 结构性风险（非单元可测，B 阶段重点）

- **Wait 写死 10 分钟**，无轮询/超时/错误网；VEED 渲染失败则流程静默卡死。
- **Blotato 是社区节点**（本机未装），10 节点分发扇出经 Merge1(chooseBranch, 9输入) 合流后回写 Sheets。
- 无 caption 场景（只发文字）会连环触发坑 2 + 坑 6。
- 模板依赖 6 个外部付费/免费服务，**错误处理为零**（无 Error Trigger、无重试）。

## 下一步
L2-B mock 全链：保留 35 节点全名全连线，外部节点全部 mock（Telegram/Perplexity/GPT×2/ElevenLabs/tmpfiles×2/FAL×2/Sheets×2/Blotato×10），场景覆盖：S1 正链（照片+caption）/ S2 只发文字（坑2+坑6复现）/ S3 无照片 / S4 VEED 轮询失败 / E1 GPT 输出缺 message.content。
等老板审核本报告后开工 B。