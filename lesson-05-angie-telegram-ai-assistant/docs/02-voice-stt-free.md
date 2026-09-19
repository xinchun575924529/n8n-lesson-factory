# 02 · 语音链路 + STT 零成本替身

## 模板的语音路径
```
Voice or Text (set) → If (text 为空 → 判语音) → Get Voice File (telegram, resource=file)
  → Speech to Text (langchain.openAi, operation=transcribe) → 文本进 Agent
```
- `If` 用 `text` 是否为空分流；**这条假设只有"要么文字要么语音"**。若用户发**图片/贴纸/语音+文字混合**，分流可能走歪——交付版建议加第三个分支。
- `Get Voice File` 输出是 **binary**；后接 openAi 转写期待二进制，**文本分支千万别直连转写**，否则会炸。**实测**：L2B 文字分支直连 STT，n8n 抛不到 binary 直接挂（修复=直接抄模板拓扑，不截短）。

## 零成本 STT：Vosk 自托管（本课实测替身）
- 模型：**vosk-model-small-cn-0.22**（42 MB，CPU 即可实时转 16kHz 中文）。
- 服务：本套件附 `workflows/` 引用的 `free-stack.py`（state 资产），监听 `127.0.0.1:8766`，提供 OpenAI 兼容 `/v1/audio/transcriptions` 接口——因此 **Speech to Text 节点凭证仍按 OpenAI 形态配置**，只把 BASE_URL 指到本地。
- 成本：0；隐私：本地离线；延迟：42MB 模型单句 ≈1-2 秒。

## 造测试语音：edge-tts（免费）
```powershell
& "$env:USERPROFILE\AppData\Local\easyclaw\ai\tool_cache\resources\tools\win\python-3.11.9\Scripts\edge-tts.exe" `
  --voice zh-CN-XiaoxiaoNeural --text "我今天有哪些任务要做" --write-media test-voice.mp3
```
- 一节课的 15264 B `test-voice.mp3`，能稳定驱动 L2C 五场景全过。**没有真人录音也能造测试集。**

## 三条再也不要踩一次的环境坑（⚪）
1. **n8n 节点里的 `localhost` 是 IPv6 优先**——自托管服务只绑 IPv4 时，`http://localhost:8766` 会被 resolve 成 `::1` 再失败。**改写成 `127.0.0.1`**，世界清净。
2. **端口 8765 在本机被 kailoader 抢占**（首次绑定返回 426），5678 是 n8n 本体、10088 是本地 invoke 网关。自托管选 **8766**，实测安稳。
3. **readWriteFile 节点撞上文件白名单**：要读本地音频/JSON 时它会拒绝，**改用 Code 节点 `fs.readFileSync`**（前提 `NODE_FUNCTION_ALLOW_BUILTIN` 含 `fs`），或走 binary 链。

## 语音入口的产品层建议
- 响应时延要给人一个"我在听"的信号：收到语音立即回一个"🎤 正在转写…"再异步处理（Telegram 无需等待，可持续发）。
- 转写结果建议**回显一次**：`识别结果："……"（置信度 xx%）`，用户可在错得离谱时及时纠正。
- 长语音（>60s）先切片再转写，否则 Vosk 内存暴涨；Telegram Bot API 下载文件上限 20MB 也要提防。