# 第四讲 · 发布矩阵（YouTube 上传修参 + 出海多平台扩展）

> 结论先行：原版 `Upload a video` 是个"能传上去就算赢"的裸节点——**categoryId=17、regionCode=IT 硬编码（坑⑩），标题/描述/#shorts/隐私状态全无讲究**。本讲给 Shorts 发布的正确姿势，以及从单平台到出海矩阵的扩展法。

---

## 1. 坑⑩：YouTube 节点的三处硬编码

| 参数 | 模板值 | 问题 |
|---|---|---|
| `categoryId` | `17`（Sports） | 与内容无关，硬编码 |
| `regionCode` | `IT`（意大利） | 作者自己地区，全球学员中招 |
| metadata | 仅 title（接过 Agent 输出） | 无 description、无 tags、**无 `#shorts`**、无 `privacyStatus` |

**后果**：原样跑出来的视频分类是"体育"、推流地区是意大利、缺 `#shorts` 标签进不了 Shorts 流量池、默认 public 直接把半成品公之于众。

**修参清单**：
- `title`：Agent 出的 title（≤60 字符，坑⑥ 闸门已保）
- `description`：模板缺 —— 补 `脚本摘要 + #shorts + 频道固定尾版`
- `categoryId`：按内容定（教育 27 / 科技 28 / 娱乐 24）
- `regionCode`：目标市场（出海英文课 → `US`）
- `privacyStatus`：先 `unlisted`（私测）→ 人工审 → 改 `public`
- **Shorts 入池硬指标**：竖屏 9:16、≤60s、标题或描述含 `#shorts`——三者缺一不可

## 2. mock 降级与 publish-queue

免费版不接 OAuth 时用 mock 发布节点：

```json
{"video": "lesson-16419-c.mp4", "platform": "youtube", "mock": true,
 "title": "…", "publish_status": "mocked", "ts": "2026-09-16T…"}
```

进 `publish-queue.json` 台账。**MockGate 铁律**：mock 项单独标记，闸门统计永不计入真实通过。要真传时同一队列可被后续工作流消费（回填 `publish_status=published` + 平台返回的视频 ID）。

## 3. 出海矩阵扩展（Shorts / TikTok / Reels）

单平台上传跑通后，矩阵化只是把"发布"抽象成队列消费者：

```
lesson-16419-c.mp4 + meta
  ├→ YouTube Shorts  (OAuth, privacyStatus=unlisted→public)
  ├→ TikTok          (Content Posting API，海外主体)
  └→ Instagram Reels (Graph API，business 账号)
```

- 三平台 metadata 各异，建议在 publish-queue 里给每条记录三套字段（title/caption/hashtags 各自适配）
- 与姊妹课 #8270 的 Blotato 思路一致：**一处产出、多平台分发、一处台账**。不同点是本课面向出海英文线，平台组合换成海外三件套。
- 发布回执（视频 ID / URL）回写台账，复盘时按 `FOOTAGE_SOURCE × 关键词` 维度看流量——让素材实验数据说话。

## 4. 上线检查单（release checklist）

- [ ] categoryId / regionCode 按市场改定
- [ ] description 补齐摘要 + `#shorts` + 尾版
- [ ] privacyStatus 首发 `unlisted`，人工过审转 `public`
- [ ] 成片 `ffprobe` 复核：9:16、≤60s、h264+aac
- [ ] publish-queue 台账有回执闭环节点
- [ ] 失败告警（邮件/IM）接到发布节点错误出口

## 动手练习

1. 把原版 `Upload a video` 的参数照"修参清单"补齐，导出 JSON 对比 diff，确认没有遗漏硬编码。
2. 给 publish-queue 设计一个"消费者"工作流草图：读队列 → 按平台分发 → 回执回写。写出它需要的三个凭证与两张表结构。