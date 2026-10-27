# Lesson 18: 商品链接一键生成 UGC 风格竖屏广告视频

> 基于 n8n 官方模板 [#21388](https://n8n.io/workflows/21388/)

## 是什么

粘贴一个商品链接，AI 自动：
1. 抓取商品页面 → 提取标题/描述/正文
2. DeepSeek 生成 hook + 口播稿 + caption + 3 条视觉提示词
3. 拆成 3 个变体并行渲染 5 秒竖屏视频（9:16）
4. 汇总到审批卡片 → 人工选一个变体
5. 自动发布到 Instagram Reels

## 课程包内容

| 文件 | 说明 |
|------|------|
| `template-21388-original.json` | n8n 官方模板原版（OpenAI + Sisif + Slack + IG） |
| `workflow-zh-deepseek.json` | 中文版：DeepSeek 替换 OpenAI，Slack 审批→飞书/手动 |
| `docs/setup-zh.md` | 中文搭建教程 |
| `docs/l2-test-report.md` | 88 断言验证报告（A+B+C） |
| `scripts/build-l2-test.py` | L2-A 单元级测试生成器 |
| `scripts/build-l2-mock.py` | L2-B mock 全链测试生成器 |
| `scripts/build-l2c.py` | L2-C 免费真跑工作流生成器 |

## 模板 3 大坑（实锤）

1. **prompts < 3 条静默少出变体**：Split Into Variants 用 `slice(0,3)` 无守卫
2. **Start Poll Counter 丢字段**：无 `includeOtherFields`，未赋值字段被丢弃
3. **Reject 无显式处理**：审批 Reject 后流程静默终止

## 免费替身链

| 模板节点 | 免费替身 |
|----------|---------|
| OpenAI gpt-4o-mini | DeepSeek deepseek-chat（现成 key） |
| Sisif.ai 视频渲染 | 本地 ffmpeg 占位视频（或后续挂 Seedance） |
| Slack sendAndWait | 飞书群审批卡片 + 人工回执 |
| Instagram Graph API | Mock（需海外企业验证，另案） |