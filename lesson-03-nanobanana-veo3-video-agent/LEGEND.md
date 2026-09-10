# LEGEND · 仓库约定与命名规范

本仓库沿用 n8n 教案工厂的同一套约定，读任何一课前先花 1 分钟看这里。

## 目录约定

| 路径 | 内容 | 只读/可改 |
|------|------|-----------|
| `workflows/` | 可直接导入 n8n 的 JSON | 导入后随便改，源文件勿动 |
| `docs/` | 五讲正文，`00` 是总览 | 只读 |
| `exercises/` | 练习与参考答案 | 可写笔记 |
| `script/` | 短视频口播稿 | 只读 |
| `site/` | GitHub Pages 静态站源码 | 由 Pages 工作流发布 |

## 工作流命名

`L2<级别>-<语义>-8270[-后缀].json`

- **级别**：`test`＝原版单测对象 / `mock`＝全 mock 验证链 / `free`＝免费替身版
- **8270**：n8n 官方模板编号
- 后缀 `S1..S5`：B 级场景编号（见 docs/05 场景矩阵）

## 三级验证口径（A → B → C）

| 级别 | 验什么 | 用什么 | 花费 |
|------|--------|--------|------|
| A 单元级 | 每个可纯计算单元的逻辑与契约 | 离线断言（本机 44 项） | 0 |
| B 全链 mock | 拓扑、路由、状态机、坑点可复现 | 1:1 保留节点名/连线，外部依赖换 Code 桩 | 0 |
| C 免费真跑 | 真实 API + 真实工件 + 真实闭环 | 付费节点全部换免费替身 | ≈0 |

## 凭证标注

- 交付工作流中 DeepSeek 凭证引用占位 id **`fra8VO4w0TLBP9JO`**（type `deepSeekApi`，挂为 HTTP Header Auth）。
- ⚠️ 该 id 只在工厂本机有效。**学员导入后必须**：Credentials → 新建 DeepSeek/Header Auth → 在工作流中替换引用。
- 仓库内任何文件都不会包含明文 API Key；发现明文即视为事故，立刻撤销并轮换。

## 状态机与台账口径

- 键：`IMAGE NAME`（＝参考图 `file_unique_id`），幂等 upsert。
- 流转：`CREATE → Published`（完整版写 Google Sheets；免费版写本地 `records.json`）。
- 发布：`publish-queue.json` 为免费版替代 Blotato 的落地队列，一条记录一个平台一个状态。