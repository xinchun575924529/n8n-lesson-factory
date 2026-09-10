# 第三讲 · 状态机：一张表的 CREATE → Published

> 结论先行：**这条流水线跨了「秒级收图」和「分钟级渲染」两个时间尺度，靠 `IMAGE NAME` 键的幂等 upsert 把多步写入收敛成一条状态记录。** 看懂它，就拿到了所有"长任务流水线"的通用台账模板。

---

## 1. 状态机三处落点

| 节点 | 时机 | 动作 |
|---|---|---|
| `Google Sheets: Update Image Description` | 收图 + Vision 完成后 | upsert：键 `IMAGE NAME = photo[2].file_unique_id`（坑①提醒：这个键绑在第三档上），写品牌/配色/描述 |
| `Google Sheets: Log Image & Caption` | NanoBanana 修图下载后 | 同行补写修图链接、初版 caption |
| `Update Status to "DONE"` | Blotato 九平台分发后 | 状态置 `Published`，闭环 |

关键配置：`matchingColumns = ["IMAGE NAME"]` —— n8n Sheets 节点按此列做 upsert 匹配，**同键重复触发不会产生重复行**（幂等）。

## 2. 为什么必须是幂等的

- 轮询型长任务天然会重试：VEO3 渲染 1~3 分钟，任何超时重跑都会重放收图段。
- Blotato 分发是扇出 9 平台，中途失败重跑时前几平台已发——状态机保证"最终态只写一次"，分发层自己查重。
- 用户可能重发同一参考图（同 `file_unique_id`）：幂等键让它覆盖更新而不是刷屏。

## 3. C 级等价实现（records.json）

免费版没有 Google，用本地 JSON 文件把同一语义手写一遍：

```javascript
// 保存台账（Sheets 替身）核心逻辑
const fs = require('fs');                       // 需 NODE_FUNCTION_ALLOW_BUILTIN=fs
const path = '.../records.json';
const db = fs.existsSync(path) ? JSON.parse(fs.readFileSync(path,'utf8')) : {};
const key = item.IMAGE_NAME;                    // 等价 matchingColumns
db[key] = { ...(db[key]||{}), ...item, STATUS: item.STATUS || 'CREATE',
            updated_at: new Date().toISOString() };
fs.writeFileSync(path, JSON.stringify(db, null, 2));
```

- `db[key]` 先读后写 = upsert；键相同即覆盖 = 幂等。
- 状态字段只有一条流：`CREATE → Published`，**不允许回退**，回退即事故（听后边第五讲的错误网怎么兜）。

## 4. 状态机的读侧：CONFIG 行

右链第一步是 `Google Sheets: Read Video Parameters (CONFIG)`——同一张表里的参数行（模型档位、画幅、默认风格）也走 `IMAGE NAME` 体系。配置与数据同表的设计可以抄，但建议**配置行加固定键前缀**（如 `CONFIG::default`），免得与业务键撞名。

## 5. B 级 mock 的验证方法（抄走）

S1 场景断言：
1. 左链结束读台账 → 存在键且 `STATUS=CREATE`；
2. 右链结束再读 → 同键 `STATUS=Published`；
3. 全程行数不变（幂等无重复行）。

S5 反向断言：Caption 250 字超长时，模板**无闸门直写台账**——状态机会忠实地记录一条"本不该成功"的 Published，这就是坑⑥要修的地方。

## 坑点提示

- Sheets 节点 `matchingColumns` 区分大小写与空格：模板全用 `IMAGE NAME`，你自己加列时照抄大小写。
- 文件的 JSON 台账要防并发写：CLI 串行没事，webhook 高并发时换 SQLite/Postgres 节点。
- `file_unique_id` 做键很稳，但用户换图重发即新键——"同一视频多次迭代"类业务要自己设计迭代键（如 `unique_id + 版本号`）。

## 动手练习

1. 在 B 级 S1 mock 上手工触发两次同键输入，断言台账行数仍为 1，体会幂等。
2. 给 C 级 `records.json` 增加 `STATUS` 合法性检查：只允许 `CREATE`/`Published`/`ERROR` 三值，非法值 throw。
3. （进阶）设计"重发同一图但改 caption"的场景：状态该不该退回 CREATE？给出你的状态迁移图并说明理由。