# workflows/ · 级配演示工作流导览

三个级别全部可直接 **Import from File** 导入 n8n，节点连接与表达式完整保留。

| 文件 | 级别 | 说明 | 需要凭证 |
|---|---|---|---|
| `L2A-test-8270-original-47nodes.json` | A | 官方 8270 原版 47 节点（单元验证对象） | 全量（不上线则无需配） |
| `L2B-mock-8270-S1.json` ~ `S5.json` | B | 1:1 拓扑 mock，5 个场景各一 | **零凭证**，导入即用工作流触发器互调跑 |
| `L2C-free-8270.json` | C | 免费替身版 19 节点，真跑全绿 | DeepSeek ×1（见下） |

## ⚠️ 凭证替换（交付必读）

- `L2C-free-8270.json` 的 4 个 DeepSeek HTTP 节点挂载了**占位凭证**：
  - credential id：`fra8VO4w0TLBP9JO`（type `deepSeekApi`，以 HTTP Header Auth 方式引用）
  - ⚠️ **此 id 仅在教案工厂本机有效，学员环境必然失效。**
- 学员替换步骤：
  1. n8n → Credentials → New → 搜索 **Header Auth**（或 DeepSeek）
  2. Name 填 `Authorization`，Value 填 `Bearer sk-你的deepseek-key`
  3. 打开各 DeepSeek 节点 → Credential for Header Auth → 选你新建的凭证，保存
- 仓库内**绝不含明文密钥**；若在任何历史版本发现明文，立即撤销并轮换。

## B 级 mock 用法

1. 依次导入 S1 ~ S5（每个场景独立工作流，触发器为 Execute Workflow Trigger，可在编辑器里直接 Execute 或互相唤测）。
2. 每个场景末尾的 `ASSERT` 节点输出断言结果：
   - S1 正常图文：全链走通、Published 闭环；
   - S2 无 caption：通链降级；
   - S3 3 档照片：**坑①引爆**，断在 `Get File URL`；
   - S4 渲染未完成：**坑②引爆**，断在首个消费节点；
   - S5 Caption 250 字：无闸门直写（坑⑥复现）。
3. 对照 [docs/05](../docs/05-pitfalls-defense.md) 逐个修复，再跑看断言转绿。

## C 级真跑前置

- 本机需 `ffmpeg`（修图/成片替身）与 `python`（渲染脚本由 Code 节点经 child_process 调用；n8n 环境变量需允许 `NODE_FUNCTION_ALLOW_BUILTIN=child_process,fs`）。
- 触发后产物：`edited.png` / `final.mp4` / `records.json` / `publish-queue.json`（输出目录见各节点参数）。