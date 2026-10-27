# L2-C 免费真跑报告 · 模板 21388

> 日期：2026-10-27 | 结果：**16/16 全绿**

## 替身链

| 模板节点 | L2-C 替身 | 验证内容 |
|----------|----------|---------|
| Write Hook And Script (OpenAI) | **DeepSeek deepseek-chat**（真实 API 调用，response_format=json_object） | hook/script/caption/prompts 四字段齐全 |
| Ad Script Parser | Code 节点解析 DeepSeek JSON 响应 | choices[0].message.content → JSON.parse → output 结构正确 |
| Create Sisif Video + Check Status | **ffmpeg 预生成 3 个 720x1280 占位视频**（蓝/绿/红底 + 文字） | 文件真实存在且 >10KB |
| Ask For Approval (Slack) | Code 自动选第一个 READY 变体 | 审批→Pick 链路正常 |
| IG Container/Check/Publish | Mock（同 L2-B） | 发布链路正常 |

## 验证结果

- **DeepSeek 输出**：hook "I did not expect this to actually work."（12词内），script 3 句，caption 含 # 标签，3 条 visual prompts 长度合规
- **Split Into Variants**：prompts 正确切 3 条，variant/hook/script/caption 传递无误
- **轮询循环**：Sisif 一轮即 READY（占位视频），IG 一轮即 FINISHED
- **Build Slack**：ready_count=3，message 组装正确
- **Pick → IG Publish**：video_url 指向本地占位视频，publish success=true

## L2 三阶段汇总

| 阶段 | 内容 | 断言 | 结果 |
|------|------|------|------|
| A 单元级 | 19 套件覆盖全部模板逻辑 | 47/47 | ✅ |
| B mock 全链 | 5 场景（成功/部分失败/全失败/拒绝/超时） | 25/25 | ✅ |
| C 免费真跑 | DeepSeek + ffmpeg 真跑全链 | 16/16 | ✅ |
| **合计** | | **88/88** | **✅** |

## 下一步
L3 课程包 + 获客视频