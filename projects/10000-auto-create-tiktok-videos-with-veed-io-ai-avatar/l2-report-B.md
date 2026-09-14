# L2-B mock 全链验证报告 · 模板 10000（AI数字人短视频自动工厂）

- 日期：2026-09-14 16:1x (Asia/Shanghai)
- 工作流：`L2Mock10000S1/S2/S3/S4/E1`（每个 30 节点：模板 27 节点全名全连线保留 + Mock TG 输入 + ASSERT 断言；Wait 从 10 分钟改 1 秒）
- 生成器：`scripts\build-l2-mock-10000.py`；源稿 `workflows\wf-l2-mock-10000-{s1..e1}.json`
- 结果：**5/5 场景 CLI 实跑 success，33/33 断言全过**

## 场景结果

| 场景 | 内容 | 断言 | 结果 |
|---|---|---|---|
| S1 | 正链：照片+caption → 全链 18 节点走通 | 18 | ✅ 主题提取/图片抓取/tmpfiles双上传/GPT脚本+文案/TTS/mpga转mp3/FAL请求体/台账五列/TG回传/Blotato+9平台全发布/状态DONE 全验证 |
| S2 | 只发文字（无 caption） | 4 | ✅ **坑2复现**：Perplexity prompt 拼出字面 `undefined`；**坑6复现**：台账 IDEA=undefined 入库；链仍走完 |
| S3 | 有 caption 无照片 | 4 | ✅ photoUrl='' → **FAL 拿到空 image_url 且无任何校验**，流程照样走完（真跑必失败却假装成功） |
| S4 | VEED 渲染失败 | 5 | ✅ Download 返回 FAILED 无 video 字段 → **台账/发布/回写全部静默断链**，无任何错误网捕获 |
| E1 | GPT 输出缺 message | 2 | ✅ ElevenLabs text=undefined 无校验继续走（真跑会拿 undefined 合成语音） |

## 新挖结构坑（B 阶段独有）

7. **[S3] 零输入校验**：无照片时 FAL image_url='' 直接提交渲染，模板没有任何 IF/校验节点拦截。
8. **[S4] 渲染失败 = 全链静默死亡**：Download 无 video 字段 → Sheets 映射取 `.video.url` 即 TypeError；无 Error Trigger、无重试、无告警。配合「Wait 死等 10 分钟」，超时和失败都无声。
9. **[E1] GPT 输出无 schema 校验**：message.content 缺失直接传进 TTS。
10. **[S1 顺带验证] Merge1(chooseBranch, 9输入)**：9 平台全成功时取 Tiktok 分支数据回写台账，行为正确但隐晦（任何单平台失败不影响其他 8 个，也不会被察觉）。

## 过程踩坑（工具层面，记入 SOP）
- Code 节点 runOnceForAllItems 模式下 **`$binary` 不可用**，要用 `items[0].binary`。
- 断言里动态遍历节点名用 `$(name)`（变量形式），不存在 `$('...')` 占位这种写法——会直接报 `Referenced node doesn't exist`。
- mock 生成器里 Python 字符串拼 JS 注意花括号配平（`return [{json:{...}}]` 三层闭合），SyntaxError 报 `Unexpected token ']'` 即少一层 `}`。

## A+B 汇总
- A 单元 47/47 ✅（9 单元）
- B 全链 33/33 ✅（5 场景）
- 模板坑累计 **10 个**（A 出 6 + B 出 4），全部断言固化

## 下一步
L2-C 免费真跑版：Telegram→( mock 触发) / Perplexity→DeepSeek / GPT×2→DeepSeek 真调 / ElevenLabs→edge-tts 真出音频 / FAL VEED→降级 ffmpeg 合成（AI图+音频）/ tmpfiles→本地 http 或免传 / Sheets→本地 JSON / Blotato→抖音+B站浏览器通道（或先 mock）。等老板审核后开工。