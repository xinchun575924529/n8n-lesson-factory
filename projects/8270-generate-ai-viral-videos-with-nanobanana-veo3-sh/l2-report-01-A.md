# L2-A 单元级验证报告 · 8270 NanoBanana+VEO3

- 时间：2026-09-10 02:2x（Asia/Shanghai）
- 方法：忠实移植模板 47 节点中全部可纯计算单元（含唯一 Code 节点 Format Prompt 原样语义）共 **10 个单元 / 44 断言**
- 执行器：`scripts\build-l2-test-8270.py`；结果 JSON：`state\l2-test-8270-A.json`
- **结果：44/44 全部通过** ✅

## 单元覆盖
| 单元 | 断言数 | 结论 |
|---|---|---|
| U1 master_prompt schema 完整性 | 8 | description/style/camera/lighting/environment/elements/subject/motion/VFX/audio/ending/text/format/keywords 全健在 |
| U2 Format Prompt Code 原样 | 3 | prompt=JSON.stringify(final_prompt) 双转义正确；model=veo3_fast、16:9 字面量 |
| U3 VEO3 body 注入兼容性 | 3 | **关键发现**：body 用 `"prompt": {{ $json.prompt }}` 无引号注入——只有 Format Prompt 的 stringify 加了外层引号才合法；两者是生死搭档，缺一不可（反面断言确认未转义必炸） |
| U4 photo 档位不一致 | 3(×3档=9断言实际3条确认) | **确认模板坑①**：Get Image File 用 `photo[2]`，Get File URL 用 `photo[3]`——3档图时后者 undefined 即断链；4档时两者指向不同尺寸文件 |
| U5 NanoBanana 转义 | 4 | prompt 引号/换行转义后 jsonBody 可合法 parse；image_urls 绑 Drive webContentLink |
| U6 VEO3 结果提取 | 3 | **确认模板坑②**：record-info 在渲染未完成时 `data.response` 缺失即抛错，模板无错误网；且 Wait 只等 20s |
| U7 Sheets 状态机 | 5 | CREATE→Published、matchingColumns=IMAGE NAME、IMAGE NAME=photo[2].file_unique_id 映射全对 |
| U8 Structured Output Parser | 2 | schema={title,final_prompt}；final_prompt 可二次 parse（双层 JSON 契约） |
| U9 TG getFile URL | 2 | URL 拼装正确；**模板 YOUR_BOT_TOKEN 留空占位**（上线必填，教案点③） |
| U10 Vision imageUrl | 2 | file 下载 URL 拼装正确；模型=chatgpt-4o-latest（上线替换 DeepSeek-VL/其他） |

## 勘误（对 brief）
- NanoBanana 实际走 **fal.run 队列**（queue.fal.run/fal-ai/nano-banana/edit），不是 kie.ai；kie.ai 只用于 VEO3。即付费点=两处：fal.run + kie.ai。

## 挖出的 4 个教案坑（与 brief 合并去重后）
1. `photo[2]` vs `photo[3]` 分辨率档位不一致（3档图即断链）
2. Wait 仅 20s + record-info 缺 response 即抛错，无重试/错误网（真实 VEO3 渲染 1-3 分钟）
3. YOUR_BOT_TOKEN 空占位 + 两处 token 拼接分散在两个节点，新人极易漏配
4. VEO3 body 无引号注入依赖 Format Prompt stringify 的外层引号——格式契约脆弱，改任何一边都全链炸

## 下一步：L2-B mock 全链
计划：Telegram/Sheets/Drive/Vision/LLM/NanoBanana/VEO3/Blotato 全 mock，保留连线，跑场景（正常图文/无caption/3档照片/渲染20s未ready/Caption超长）断言路由与状态机。成本 0。