# L2-A 单元级验证报告 · 3442 全自动AI视频生成与多平台发布

- **日期**：2026-09-14
- **范围**：4 个 Code 节点语义忠实移植执行 + 全部关键节点静态契约断言（12 单元 / 57 断言）
- **结果**：**57/57 全过 ✅**
- **生成器**：`scripts/build-l2-test-3442.py`；原始断言明细 `state/l2-test-3442-A.json`

## 单元覆盖

| 单元 | 内容 | 断言 |
|---|---|---|
| U1 | Create List：split 语义 4 场景（含最大坑） | 4 |
| U2 | Validate list formatting IF 校验强度 | 3 |
| U3 | Calculate Token Usage 求和/字段保留/缺 usage 防御 | 5 |
| U4 | List Elements 跨节点引用契约 + 成组语义 | 5 |
| U5 | List Elements1 sound_urls quirk + Creatomate 消费面 | 3 |
| U6 | 两处失败检查 IF（只查 failed） | 3 |
| U7 | Set API Keys 4 键结构与注入方式 | 4 |
| U8 | Creatomate 渲染 body 契约（5视频+5字幕+1音频） | 4 |
| U9 | upload-post 五平台 multipart 契约 | 8 |
| U10 | Sheets 队列状态机 + 触发器 | 5 |
| U11 | LLM 链路（gpt-4o-mini/o3-mini/whisper/描述生成） | 4 |
| U12 | 本地文件环节（Drive 可删证据） | 3 |

## 🔥 挖到的模板坑（教案卖点）

1. **【最大坑】Create List 按字面 `\n` 两字符切分，不是换行**：jsCode `text.split('\\n')` 切的是字面反斜杠+n。LLM 若自由发挥输出真换行 → 整条变 1 个 item。这就是为什么 system prompt 里死命强调 NO quotation marks、分隔符 `\n`——DeepSeek 替换后此约束必须原样保留，否则下游全断。
2. **Validate IF 校验过弱**：只查 `length > 1`，不是 `== 5`。拆出 2~4 条也放行 → 下游 Creatomate 5 段模板按位置硬配直接错位。教案应建议改 `== 5`。
3. **失败轮询只有 failed 判定，没有 processing 超时分支**：固定 Wait 3min/10min 后若任务仍在渲染 → 走 false 分支读 `output.image_url`（不存在）→ 静默断链。Kling 高峰期必踩。
4. **List Elements1 quirk**：`items.map` 里每项都取 `.first()` → 5 个完全相同的音频 URL（实际只有一条口播，Creatomate 也只用 `sound_urls[0]`，无害但写法迷惑）。
5. **Set 节点明文集中存 4 个 API Key**：坏实践（应用 Credentials），本厂版直接删。
6. **缺 usage 字段即抛 TypeError**：换 LLM 时必须确认返回 OpenAI 兼容的 `usage` 结构（DeepSeek 兼容 ✅）。
7. **成本字段硬编码**：Update Sheet 里 fluxCost=0.075 / klingCost=2.3 是字面量，换引擎需手改——本厂免费版直接删成本列。
8. **Facebook page_id 硬编码**、YouTube 标题截 70 字符：平台特化细节，本厂只留抖音+B站时整段砍掉。

## 对 C 阶段的输入（替代方案落点确认）

- DeepSeek 兼容 usage 结构，Token 统计节点可平移（o3-mini 的 reasoning token 丢失，教案注明）
- whisper 转写节点（Get Audio from Video）用途只是给发布描述供文本 → 可删，直接用 5 条字幕拼
- Drive 4 节点纯中转（最终读的是本地 writeBinaryFile 落盘的文件）→ 免费版全删，本地路径直通
- 发布段 5 个 upload-post 节点 → 免费版砍成「写入发布队列 JSON」，由本厂浏览器通道消费

## 下一步

L2-B mock 全链（场景：正常流 / 图像失败重试 / 视频失败重试 / 字幕格式拦截 / 弱校验错位演示），等拍板开工。