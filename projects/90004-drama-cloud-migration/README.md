# 90004 · AI短剧产线上云（涅槃）

> 状态：**⏸️ 已暂停**（2026-10-19 老板拍板）｜模式：B（立项即研发）｜立项：2026-10-09 01:13

## 目标

把本地 AI 短剧产线整体上云：AutoDL GPU（ComfyUI 文生图 + Wan2.2 图生视频）+ ECS 编排，
实现「剧本 → 分镜 → 镜头图 → 视频 → TTS 配音 → 合成成片」全自动流水线。

## 产线四步（脚本已固化，ECS `/root/drama-niepan/ep1/`）

1. **分镜文生图**：ComfyUI API，21 镜角色一致性（角色参考图垫图）
2. **图生视频 i2v**：Wan2.2，5s/镜头，云端 GPU 批处理（`gen_videos_comfy.py`）
3. **TTS 配音**：edge-tts 多角色音色映射（`drama_tts.py`，对白时间轴对齐）
4. **合成**：ffmpeg 拼接 + 字幕烧录 + BGM 混音（`compose_ep1_v2.py`）

## 里程碑

- 2026-10-17：EP01 全链验收成片 **83.5s**（21/21 镜头全绿，`涅槃-EP01-重生-v2-wan.mp4` 40.9MB）
- 剧本 EP01-03 已完成（`script/`）

## 暂停原因（2026-10-19 老板拍板）

1. 成片无口型——Wan2.2 i2v 只管画面动、不含 lip-sync，配音与嘴型脱节
2. 立项到出片耗时 8 天，迭代成本过高

## 重启钥匙

加 lip-sync 环节（Wav2Lip / SadTalker / latentsync）接在 i2v 之后即可复活；
云上资产原样封存于 ECS `/root/drama-niepan/`，AutoDL 双实例已关机（数据盘保留，无空转费）。