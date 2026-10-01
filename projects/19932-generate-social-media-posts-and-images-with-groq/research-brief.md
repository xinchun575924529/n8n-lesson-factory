# 立项报告 · 19932 Generate social media posts and images with Groq, OpenAI and Google Drive

- **项目号**：19932（n8n 官方模板，B 模式立即研发）
- **定选时间**：2026-10-01 12:00（飞书 ou_505161df…）
- **来源**：https://n8n.io/workflows/19932/ · 模板 API 200 OK
- **工作流名**：AI Post Generation（13 功能节点 + 5 sticky note）

## 一、项目是干什么的

表单收集用户一句话创意 + 图片尺寸 → AI 生成社媒三件套（Instagram / LinkedIn / X 文案）+ AI 配图 + 一张精美 HTML 结果页，回显给用户。本质是「**一句话 → 社媒发帖全家桶**」的图片版内容生成流水线。

## 二、节点清单（13 功能节点）

| # | 节点 | 类型 | 作用 |
|---|------|------|------|
| 1 | Form Submission Trigger | formTrigger | 表单：input（必填）+ Resolution 下拉（1024x1024/1024x1536/1536x1024） |
| 2 | Prompt Creation Agent | langchain.agent | 把用户输入转成图片生成提示词 |
| 3 | Language Model Processor | lmChatGroq | Agent 1 的 LLM（openai/gpt-oss-120b） |
| 4 | Output Structuring Parser | outputParserStructured | schema `{prompt}` |
| 5 | AI Image Generator | langchain.openAi (image) | gpt-image-1-mini 生图，尺寸取表单 |
| 6 | Upload to Google Drive | googleDrive | 图传 Drive 指定文件夹 |
| 7 | Post Content Generator | langchain.agent | 生成 IG/LinkedIn/X 三条文案 |
| 8 | Chat Model Execution | lmChatGroq | Agent 2 的 LLM |
| 9 | Output Parsing Agent | outputParserStructured | schema `{instagram, linkedin, twitter (x)}` |
| 10 | HTML Generation Agent | langchain.agent | 文案+图链接 → 精美 HTML 页 |
| 11 | Groq Chat Model Execution | lmChatGroq | Agent 3 的 LLM |
| 12 | Structured Output Parser | outputParserStructured | schema `{"html file code"}` |
| 13 | Display Final Result | form (completion) | showText 回显 HTML |

主链：Form → Agent1(生提示词) → OpenAI 生图 → Drive 上传 → Agent2(三平台文案) → Agent3(HTML) → Form 结果页。

## 三、凭证缺口与免费替代方案（结论：全部可免费替代 ✅）

| 原凭证 | 用途 | 替代方案 | 成本 |
|---|---|---|---|
| Groq ×3 | 三个 Agent 的 LLM | **DeepSeek deepseek-chat**（工厂惯例，直连有余额） | ~免费 |
| OpenAI (gpt-image-1-mini) | 生图 | **Seedream（image-gen 技能）** 或 AutoDL ComfyUI；B/C 阶段可 mock 成占位图 | 免费 |
| Google Drive OAuth2 | 图片托管 | **本地文件 + 公网可访问链接替代**（课程演示用 webhook 静态托管/base64 内嵌进 HTML，更优雅零依赖） | 免费 |

**凭证替代结论：零付费可行。** 三个 Groq 模型节点统一换 DeepSeek，架构不变（agent+parser 结构原样保留，教学价值不打折）。

## 四、L2 验证计划（推荐 A+B+C 全做，均免费）

- **A 单元级**：3 个 outputParser schema 解析 + prompt 组装表达式（`$json.output.prompt`、`$('Form Submission Trigger').item.json.Resolution` 跨节点引用）+ HTML agent 输入拼接 → 预计 15-20 断言。
- **B mock 全链**：Form 提交 mock → mock LLM 返回 → mock 图片（固定 PNG）→ mock Drive 上传（本地写文件+假链接）→ 全链连通性 + 断链/空输出场景。
- **C 免费替身真跑**：DeepSeek 真调 ×3 + Seedream 真生图 + 本地托管图片链接 + Form 端到端真实提交 → 产出真实三平台文案+图+HTML 页。
- **推荐路径**：A → B → C 全做（本模板节点少、链路短，C 成本低）。

## 五、风险点

1. **HTML 回显 XSS 风险**：`showText` 直接渲染 LLM 生成的 HTML——教学时要讲清楚，生产环境需消毒；可作课程卖点（模板没说的坑）。
2. **gpt-image-1-mini 尺寸参数**：模板把表单 Resolution 直接喂给 OpenAI size，1024x1536/1536x1024 是 gpt-image 系专属尺寸；换 Seedream 后要重映射尺寸枚举。
3. **Drive webViewLink 权限**：模板直接用 `webViewLink` 做公开图片链接，但默认上传不开放共享权限 → 真实使用时链接 403（模板隐藏坑，替身版用本地托管规避）。
4. **Agent 无 error branch**：三个 Agent 任一失败全链断，无错误网；替身版可补。
5. **`twitter (x)` 键名带空格括号**：表达式 `$json.output['twitter (x)']` 是少数派写法，单测要覆盖防回归。

## 六、等老板拍板

- L2 是否按推荐 A→B→C 全做？
- C 阶段生图用 Seedream（推荐，image-gen 技能现成）还是 AutoDL ComfyUI（要开机烧时租）？