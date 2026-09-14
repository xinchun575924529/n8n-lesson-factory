# L2-C 免费替代真跑报告 · 模板 10000（AI数字人短视频自动工厂）

- 日期：2026-09-14 18:4x (Asia/Shanghai)
- 工作流：`L2Cstm10000001`「L2-C 免费真跑 10000」（12 节点，CLI 实跑 success）
- 生成器：`scripts\build-l2c-10000.py`；源稿 `workflows\wf-l2c-10000.json`
- 结果：**12/12 断言全过，零付费，产出真实 mp4 成片**

## 替代落位（对照模板原节点）
| 模板 | C 版 | 真假 |
|---|---|---|
| Search Trends with Perplexity | DeepSeek deepseek-chat | ✅ 真调 |
| Generate Script with GPT-4 | DeepSeek | ✅ 真调 |
| ElevenLabs Voice Synthesis | edge-tts 晓晓 +8%（本地） | ✅ 真出 267KB/44.5s mp3 |
| Convert .mpga to .mp3 | 不需要（edge-tts 直出 mp3） | 链路简化 |
| tmpfiles 双上传 | 本地路径直给 ffmpeg | 简化（VEED 才需要公网 URL） |
| FAL.ai VEED Fabric 数字人 | ffmpeg 图片+音频合成 1920x1080 | ✅ 真出 1.82MB/46.4s mp4（降级：无对口型数字人） |
| Generate Caption with GPT-4 | DeepSeek | ✅ 真调（含 #hashtag） |
| Save/Update Google Sheets | 本地 JSON 台账 ledger.json | ✅ 真写盘 |
| Blotato 9 平台 | mock（9 posted） | mock（发布通道=本厂抖音/B站浏览器通道，属 L4 范畴） |

## 真实工件（state\10000-c-data\）
- `script.txt` 667B（DeepSeek 写的 30s 口播稿：健身房新手三大误区，带钩子带关注引导）
- `voice.mp3` 267KB / 44.5s（edge-tts 晓晓）
- `lesson-10000-c.mp4` **1.82MB / 46.4s / 1920x1080 h264+aac 48kHz**（与音频时长差 1.9s，zoompan 类 -shortest 正常尾差）
- `ledger.json` 台账 1 行（IDEA=主题、五列齐、STATUS=DONE）

## 断言清单（12）
脚本非空>20字 / 趋势非空 / 音频>10KB / 音频>3s / 成片>200KB / 成片时长≈音频(±2s) / 成片>3s / 文案含# / 台账行 DONE / 台账URL VIDEO一致 / 台账持久化可读 / 9平台(mock)

## 关键坑（沿 8270 经验）
- CLI 跑 child_process 必须 `NODE_FUNCTION_ALLOW_BUILTIN` 加 `child_process`
- FFmpeg/ffprobe 在 WinGet Links（PATH 内），edge-tts 绝对路径带空格要双引号

## 结论
**A(47/47) + B(33/33) + C(12/12) 三关全绿，累计 92 断言、10 个模板坑全部固化。**
C 版证明：除 VEED 数字人渲染外，整条「AI 口播视频工厂」链路可零成本复刻。

## 下一步
等老板拍板进 L3 教案仓库（README+docs+workflow.json+exercises+短视频脚本+Pages 站点，参照 lesson-03 规格，预计 lesson-04）。