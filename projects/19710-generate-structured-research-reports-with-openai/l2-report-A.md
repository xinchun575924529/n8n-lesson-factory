# L2-A 单元级验证报告 · 19710 AI Personal Research Assistant

- 时间：2026-09-28 07:2x（Asia/Shanghai）
- 工作流：`L2Test197100001`（L2A-UnitTest-19710-ResearchAssistant，未激活）
- 生成器：`scripts\build-l2-test-19710.py` ｜ 执行：`state\19710-a-run.json`
- **结果：30/30 全部通过 ✅**

## 覆盖范围

模板 4 个 Code 节点忠实移植（逻辑一字未改，仅包函数注入 mock 上下文）：

| 节点 | 断言数 | 要点 |
|---|---|---|
| A. Parse Search Queries | 7 | 正常/围栏/空白正常解析；3 个坑实锤全抛错 |
| B. Prepare Search Results | 6 | URL 编码、HTML 剥标签、缺 snippet 兜底、零结果 |
| C. Clean Website Content | 4 | extract 提取；pages 空/无 query 静默空串；回环配对 |
| D. Research Report Formatter | 13 | 8 章节切片、大小写、缺章、乱序、输出结构；2 个坑实锤 |

## 坑实锤（教学卖点）

1. **A4/A5/A6：Parse Search Queries 裸 JSON.parse 无 try**——LLM 加一句开场白、返回空、返回单引号伪 JSON，三种常见脏输出全部直接崩执行。教案必须讲 try/catch + 正则提取 JSON 数组的加固写法。
2. **D9：章节切片完全依赖 `###` 前缀**——LLM 若改用 `##` 或加粗标题，8 个字段全部静默变空串（不报错，Sheets 里存一堆空列）。这是本模板最大脆弱点，prompt 必须锁死 `###` 格式。
3. **D10：AI 输出为空时抛错信息友好**（`AI research report is empty.`）——难得的一处好设计，可对比讲。
4. **C2/C3：Wikipedia 查不到词条时静默产空 content**——不会报错，空内容直接进合并，稀释最终报告质量；教学时讲「过滤空 content」加固。
5. **D12 反直觉安全**：章节乱序时 extractSection 的 nextHeadings 是「所有后续章节」的并集，乱序不会吞内容（实测 Executive Summary 在 Source References 提前时仍正确截止）——比看起来健壮。

## 下一步

B 关 mock 全链（等老板确认或直接按 A+B+C 拍板推进）。