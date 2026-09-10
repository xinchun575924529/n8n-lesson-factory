# 第四讲 · 发布矩阵：一个 Blotato 扇出九个平台

> 结论先行：**模板最后用 Merge 把成片合流，交给 Blotato 九个节点一次扇出 YouTube / TikTok / Instagram / Facebook / LinkedIn / Threads / Bluesky / Pinterest / X。** 付费时它是一键全网的魔法；免费时用 `publish-queue.json` 把"该发什么"落地，交给自有发布通道消费。

---

## 1. Blotato 扇出段拆解

```
Merge（成片URL + Caption + 标题）
  ├─ Youtube    ├─ Tiktok      ├─ Instagram
  ├─ Facebook   ├─ Linkedin    ├─ Threads
  ├─ Bluesky    ├─ Pinterest   └─ Twitter (X)
  → Update Status to "DONE"
```

- 每个平台一个 Blotato 节点：视频 URL + caption + 平台账号 id。
- Blotato 的价值 = 替你维护九个平台的 OAuth 与上传细节；代价 = 订阅费 + 平台绑定。
- 九节点是**全并行扇出**：任一平台失败不影响兄弟节点，但模板没有错误网，失败只静默留在执行日志里 → 第五讲。

## 2. Merge 节点的脾气

- Merge 默认 **Wait for All**：等齐两条输入才放行——渲染链与收图链速度差一个量级，这里天然是合流点。
- B 级踩坑实录：双 Trigger 上游 + 合流的拓扑在不同 n8n 版本行数推进行为不同（坑⑤），**凡 Merge 都要在行数断言里点名检查**（S1~S5 的通用断言就是这么来的）。

## 3. 免费版降级：publish-queue.json

C 级不接 Blotato，把发布意图落成队列文件（真实工件）：

```json
[
  {"id":"dy-20260910-001","platform":"douyin","video":".../final.mp4",
   "caption":"...","title":"...","status":"queued"},
  {"id":"bili-20260910-001","platform":"bilibili","video":".../final.mp4",
   "caption":"...","title":"...","status":"queued"}
]
```

- 消费方：自有浏览器发布通道（cookie 已登录的抖音/B站），逐条取队列 → 发布 → 回写 `status: published`。
- 与 Blotato 语义对齐：**平台 × 状态 × 幂等 id**，将来换回 Blotato 只换消费层。

## 4. Caption 是发布矩阵的弹药

`Rewrite Caption with GPT-4o` 给视频写平台向文案，模板只有一步生成、没有闸门。B 级 S5 实测 **250 字直接进台账和发布体**（坑⑥）——多数平台 caption 上限在 150~2200 字不等，但短视频平台前 200 字决定折叠。C 级加了 200 符闸门：

```javascript
let cap = llmCaption || '';
const gated = cap.length > 200 ? cap.slice(0, 197) + '...' : cap;
return [{ json: { ...item, caption_raw: cap, caption_gated: gated } }];
```

- 保留 `caption_raw` 备查，`caption_gated` 进台账与发布队列——**修复留痕**比自己悄悄改掉更专业。
- 多平台差异化 caption（抖音带话题、B站带简介）是天然的进阶练习。

## 5. 回发用户：Telegram 双通知

分发前模板先 `Send Video URL via Telegram`（成片链接）+ `Send Final Video Preview`（预览），让发起人即时验收——这个"先回执再分发"的顺序值得抄：用户拿到东西的时间最短，分发失败也不影响用户体验。

## 坑点提示

- 平台发布是**外部副作用**，重试前先查队列/台账该键是否已 `published`，别靠记忆。
- Blotato 每个 platform 的必填字段不同（Pinterest 要 board，LinkedIn 分个人/组织）——模板九节点参数别盲抄，逐个 field 核。
- 免费队列要防"幽灵成功"：消费端发布完必须回读平台页面二次确认再置 `published`（本厂 SOP 的浏览器实拍检查就是这招）。

## 动手练习

1. 在 B 级 mock 的 Merge 后加断言：两个输入各 1 行、输出 1 行——亲手验证行数语义。
2. 给 C 级 `publish-queue.json` 增加 `attempts` 字段，写消费端伪代码：同一 id 最多重试 3 次。
3. （进阶）把 caption 闸门改成"按平台长度表截断"：`{douyin:55, bilibili:2000, x:280}`，并写两项断言。