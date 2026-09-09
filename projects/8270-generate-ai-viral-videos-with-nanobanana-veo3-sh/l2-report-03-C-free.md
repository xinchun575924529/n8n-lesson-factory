# L2-C 免费替代版真跑报告 · 8270 NanoBanana+VEO3

- 时间：2026-09-10 03:3x（Asia/Shanghai）
- 工作流：`L2Cstm82700001`「8270 L2-C 免费替代版」（19 节点，CLI 真跑）
- 生成器：`scripts\build-l2c-8270.py`；工件：`state\8270-c-data\`（edited.png / final.mp4 / records.json / publish-queue.json）
- **结果：10/10 断言全过** ✅（DeepSeek 真实 API ×3 + ffmpeg 真实工件 ×2，零付费）

## 替换口径（全免费）
| 模板原配 | C 替身 | 真实性 |
|---|---|---|
| OpenAI gpt-4o/4.1-mini ×3处（Vision/UGC提示词/VEO3脚本/Caption 实际4处压成3） | **DeepSeek deepseek-chat 真调**（模板 prompt 原文搬运） | ✅ 真 API |
| NanoBanana(fal.run 付费) | ffmpeg gradients 本地合成场景图（AutoDL ComfyUI Z-Image 登录态失效待恢复后可换真 AI 修图） | ✅ 真 PNG 工件 |
| VEO3(kie.ai 付费) | ffmpeg zoompan 3s 成片 1920×1080 | ✅ 真 mp4 工件 |
| Google Sheets ×3 | 本地 records.json，CREATE→Published 状态机闭环 | ✅ 真文件 |
| Telegram ×2 | mock 回发字段 | mock |
| Blotato ×9 | publish-queue.json（douyin+bilibili 入队，对接本厂浏览器发布通道） | ✅ 真队列 |

## 真跑验证的核心契约
1. **双层 JSON 契约真跑通过**：DeepSeek 按 master schema 输出 `{title, final_prompt}`，final_prompt 二次 parse >8 键（内层相机/灯光/环境/主体/动效/VFX/音频全在）
2. **Format Prompt 模板原 Code 节点 verbatim 计算**：双转义后 VEO3 body 注入合法（与 A/B 断言互证）
3. **免费版修复点1**：Caption 200 符闸门（模板无，模板坑⑥的修复示范：`caption_gated`）
4. **真实产物**：final.mp4（3s 成片）、records.json（Published 闭环）、publish-queue.json（双平台待发布）

## C 阶段新踩坑（录入 SOP）
- **httpRequest 全量替换 item 是 n8n 常态**：链路每过一次 HTTP 节点，上游数据全丢——修复法=下游 Code 用 `$('关键节点').item.json` 回捞（真实模板靠同一招续命，B 坑6 的真机版验证）
- **jsonBody 表达式必须以 `=` 开头**：第一次 caption 节点把 `{{ }}` 明文发给了 DeepSeek，模型对模板引用一脸懵、回了一段反问——质量级 bug，断言全过也抓不着（教训：断言要看内容质量，不只看契约）
- `executeCommand` 节点在 n8n CLI 环境 **不可识别**（Unrecognized node type）→ 替代：Code+`child_process`+execSync（NODE_FUNCTION_ALLOW_BUILTIN 加 child_process）调 python 渲染脚本
- AutoDL 登录态失效（autodl_ctl.py status 报错）→ 真 AI 修图版 C 待用户在 Chrome 重登 autodl.com 后可升级
- 残留测试流 MiniExecCmd00001（无害）

## 结论
免费替代版 C 端到端真跑绿：**模板 4 处 LLM 全部 DeepSeek 等价、渲染工件零成本回填、状态机/台账/发布队列全落地**。8270 「研发验证」三关（A 44/44、B 18/18、C 10/10）全过。

## 下一步
L3 教案仓库（README+docs 6篇+workflow.json 原版+练习+短视频稿+站点），坑点素材：A/B/C 累计 7+ 个。