# 练习 · 6 道（含参考答案）

> 建议顺序：先跑一遍 B 级 S1 ~ S5 再做题。带 ⭐ 的是交付级综合题。

---

## E1 · 收图选档
给 L2A 模板插入一个 Code 节点，统一把 `message.photo` 选为最大档，并让 `Get Image File` 与 `Get File URL` 都引用它的输出。

**参考答案**：选 `photos[photos.length - 1]`，输出 `photoFileId` 与 `photoUniqueId` 两个字段；两节点原 `photo[2]/photo[3]` 表达式换成 `{{$json.photoFileId}}`。这样 3 档图不再断链（修坑①），状态机键 `IMAGE NAME` 仍然来自 `photoUniqueId`（file_unique_id），幂等语义不变。

## E2 · 契约破坏试验
把 VEO3 节点 body 改为 `"prompt": "{{ $json.prompt }}"`（加引号），用 B 级 mock 触发，描述结果并解释。

**参考答案**：body 解析失败/服务端报错。因为 `Format Prompt` 已 `JSON.stringify` 加了外层引号并转义，再加引号 = 双重引号包裹，注入后是非法 JSON（字符串外面又套了字符串）。这就是坑④：stringify 与无引号注入是生死搭档。

## E3 · 免费替身改造
把 L2C 中「NanoBanana 替身: 本地合成场景图」换成任意你自己的免费生图方案，要求下游引用字段不变。

**参考答案**：保持输出 `image_url` 与本地文件路径字段不变即可。可选方案：本地 ComfyUI HTTP API、Pillow 脚本合成、内网静态图服务。核心思想：**接口契约锁定，实现可插拔**——这正是替身术的灵魂（第二讲）。

## E4 · 状态机巡检
在 B 级 S1 上连跑两次同键输入，写断言验证：(a) 台账行数仍 1；(b) 末态 `Published`；(c) `updated_at` 变大。

**参考答案**（Code 伪码）：
```javascript
const db = readDb(); const rows = Object.keys(db);
assert(rows.length === 1, '行数幂等');
assert(db[rows[0]].STATUS === 'Published', '末态闭环');
assert(new Date(db[rows[0]].updated_at) > t0, '时间戳前进');
```
同键重复触发被 `matchingColumns`/键覆盖吸收，这就是幂等台账（第三讲）。

## E5 · 轮询加固
改造坑②：写循环轮询（每 60s、最多 8 次），第 3 次才 ready 的 mock 必须通过；8 次未 ready 必须进错误网。

**参考答案**：Loop 内 `Wait 60s → HTTP record-info → IF $json.data?.response?.resultUrls?.[0]`：有则下载放行；无则计数+1 回 Wait；计数 ≥8 走熔断分支：台账置 `ERROR` + 告警 + 用户兜底回执（第五讲第 2、3 节）。

## E6 ⭐ · 综合质检单
为新接的任意模板写一份"质检清单"，要求≥8 条断言，覆盖本课 7 坑中至少 4 类，并标注每条断言属于 A/B/C 哪一级。

**参考答案要点**：
1. 收图/输入层的档位与空值断言（A 级）；
2. LLM 输出契约 + 反例（A 级，围栏清洗/失败回退）；
3. 关键节点 `$('节点名')` 引用完整性扫描（A 级静态、B 级动态）；
4. 1:1 mock 全链场景 ×≥3，含一个"坑引爆"场景（B 级）；
5. 状态机幂等 + 末态断言（B 级）；
6. 长任务轮询超时路径断言（B 级）；
7. 免费替身真跑端到端 + 真实工件存在性（C 级）；
8. 正文质量抽检：LLM 输出不含未渲染的 `{{ }}` 模板明文（C 级，防 `=` 坑）。
质检清单即交付物的一部分——客户买的是"被验证过的自动化"，不是一堆节点。