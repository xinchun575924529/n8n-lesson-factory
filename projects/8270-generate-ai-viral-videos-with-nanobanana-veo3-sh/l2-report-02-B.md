# L2-B mock 全链验证报告 · 8270 NanoBanana+VEO3

- 时间：2026-09-10 02:4x（Asia/Shanghai）
- 方法：模板 47 节点拓扑 1:1 保留（节点名/连线/表达式语义），全部外部依赖换 Code mock；5 场景 × 独立工作流（L2Mock8270S1~S5）n8n CLI 实跑
- 生成器：`scripts\build-l2-mock-8270.py`；结果：`state\8270-mock-S*.txt` + `state\l2-mock-8270-B.json`
- **结果：18/18 断言全过** ✅

## 场景矩阵
| 场景 | 输入 | 预期 | 实测 |
|---|---|---|---|
| S1 正常图文(4档+caption) | 全链通 | ✅ Published、VEO3 body 注入合法、成片 URL 回 TG、状态机 CREATE→Published | 4/4 + 通用2 |
| S2 纯图无 caption | caption 空仍通链 | ✅ 通链 Published | 3/3 |
| S3 3档照片 | **坑①引爆**：断链点在 `Telegram API: Get File URL`（photo[3]）而非 Get Image File（photo[2]）——两节点档位写死不一致 | ✅ 精确复现 | 3/3 |
| S4 渲染未完成 | **坑②引爆**：record-info 无 response，断链点在首个消费 `Send Video URL via Telegram`（`Cannot read properties of undefined (reading 'resultUrls')`） | ✅ 精确复现 | 3/3 |
| S5 Caption 250 符 | 模板无 200 符闸门，超长直写 Sheets | ✅ 复现 | 3/3 |

## mock 过程中挖到的新坑（3 个，全是教案素材）
5. **双 trigger 分支合流点 `Set: Bot Token`**：它同时接 Telegram Trigger 和 Log 链两个上游——本机 v1 顺序执行下右链按 1 行推进，但拓扑上是双触发隐患（不同 n8n 版本行为可能不同），教案里列为「待真机验证」
6. **Format Prompt 重建 json 丢上下文**：模板下游全靠 `$('节点名')` 跨节点重引补数据——改任何节点名都静默断引用（教学高危坑）
7. **查错链实录**：manuscript断链会「顺流而下」一路污染到终点才暴露，断点定位靠逐节点查 runData——反向证明错误网必要性

## 环境坑（工厂级，已记入 SOP）
- EasyClaw tool_cache 里的 n8n 2.37.10 被 9/9 C盘瘦身清残（bin 缺失）；**CLI 一律回退用 `AppData\Roaming\npm\n8n`（2.33.3）**，与守护同版本同库无 schema 冲突
- **CLI execute 新导入工作流必坑**：executeWorkflowTrigger 必须 typeVersion=1 且 settings 为空，否则报玄学错 "No active execution found"（老工作流躺着正常，新建全踩）
- Debug 副产品：MiniTest8270A001/A002 两个最小测试流留在库里（无害，等服务端删除入口）

## 结论
8270 主链逻辑（提示词生成契约→VEO3 提交→轮询→Caption→记账→分发→状态机）在 mock 下完全走通；4 大真坑（photo档位/20s单次轮询/token占位/双JSON契约）全部在 mock 中可稳定复现，教案素材质量很高。

## 下一步
L2 全绿。C 真跑决策等你拍板：①投 kie.ai+fal.run 真渲染（按次付费），还是 ②免费版 C（DeepSeek+ComfyUI 修图半链），还是 ③跳 C 直接 L3 教案。