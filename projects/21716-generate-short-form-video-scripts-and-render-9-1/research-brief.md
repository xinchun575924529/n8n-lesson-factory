# 立项报告 · 模板 21716

- **模板名**：Generate short-form video scripts and render 9:16 clips with OpenAI and Creatomate
- **来源**：https://n8n.io/workflows/21716/ （API 实拉 workflow 20 节点，官方页标 6）
- **定选**：2026-10-28 B 模式立即研发（fresh 候选，ou_505161df 老板定选）

## 一、这是什么

「短视频脚本生成 + 渲染派发」的 **API 服务型工作流**（webhook 驱动，非定时）。对外暴露一个 POST webhook `/tykairo-shorts-factory-v1`（headerAuth），按 `action` 四路分流：

1. **draft**：校验入参（topic 5–400 字符/platform 白名单/language/audience/tone）→ 拼好 messages → 调 OpenAI chat/completions（gpt-4o-mini, json_object）生成脚本（title/hook_a/hook_b/supporting_text/cta/description/voiceover + 4 个场景 storyboard + hashtags + seo_keywords）→ Code 严格校验 schema + 截断清洗 → 组装三平台发布 kit（YouTube/TikTok/Instagram）→ respond 200。
2. **render**：双闸门校验（`approved===true && rights_confirmed===true`，人工审核护栏）→ 校验 template_id/文本长度 → POST Creatomate `/v2/renders`（1080x1920 竖屏）→ 校验返回 job id → respond。
3. **status**：render_id UUID 正则校验 → GET Creatomate `/v2/renders/{id}` → 返回 videoUrl（succeeded）/错误状态。
4. **audit**：纯本地确定性「起飞前检查」（字数估算时长 65–105 词、标题 ≤95 字符、绝对化用语正则、hook≠title）→ respond 清单，**零成本**。
5. **Other**：错误归一化 → 400。

亮点：validation 护栏做得相当完整（入参白名单、人工双闸门、错误码分级 400/502、schema 严格校验、三平台 kit 组装），是「教 API 工作流设计」的好素材。

## 二、节点清单（20 个，实拉）

| 节点 | 类型 | 作用 |
|---|---|---|
| When Video Request Received | webhook v2.1 | POST + headerAuth + responseNode 模式 |
| Check Action and Budget Validity | Code v2 | 四 action 校验+组包（核心，~60 行） |
| Route by Video Task | Switch v3.2 | 4 路 + fallback Other |
| Post to OpenAI for Hook Variations | httpRequest 4.2 | OpenAI 直调（generic httpHeaderAuth） |
| Build SEO Kit from Script | Code v2 | schema 校验+三平台 kit 组装 |
| Respond with Storyboard and SEO Kit | respondToWebhook | 200/400/502 表达式 |
| Post to Creatomate for Rendering | httpRequest 4.2 | POST /v2/renders |
| Verify Render Job Submission | Code v2 | 校验 job id |
| Respond with Render Job ID | respondToWebhook | |
| Fetch Creatomate Render Status | httpRequest 4.2 | GET /v2/renders/{id} |
| Check Video Readiness | Code v2 | succeeded/failed/processing 三分支 |
| Respond with Final Video URL | respondToWebhook | |
| Handle and Normalize Input Errors | Code v2 | 错误归一化 |
| Respond with Validation Error | respondToWebhook | |
| Execute Preflight Script Check | Code v2 | audit 透传 |
| Respond with Preflight Checklist | respondToWebhook | |
| Sticky Note ×6 | stickyNote | 文档（作者 TYKAIRO） |

## 三、凭证缺口与免费替代方案

| 原依赖 | 费用 | 替代方案 | 成本 |
|---|---|---|---|
| **OpenAI API**（gpt-4o-mini） | 付费 | **DeepSeek deepseek-chat**（OpenAI 兼容端点，把 URL 换成 `https://api.deepseek.com/v1/chat/completions`、model 换 deepseek-chat、header 换 Bearer key；`response_format:json_object` DeepSeek 也支持） | 已有 key，≈0 |
| **Creatomate API**（渲染引擎，核心付费点） | 按渲染分钟付费，免费额度极薄 | **B/C 阶段 mock 本地 http 服务**（127.0.0.1 起 mock server 返回假 render job / status）；**C 免费真跑替身=本机 ffmpeg 字幕条渲染链**（lesson-01~16 已固化 compose 管线，可产出真 9:16 mp4），Creatomate 本体留 mock | 0 |
| webhook headerAuth | — | 本机 n8n 自带，直接建 headerAuth 凭证 | 0 |

**结论：全链可 0 元走通**——OpenAI→DeepSeek（真调），Creatomate→mock（B）/本地 ffmpeg 替身（C 可选真跑视频渲染）。

## 四、L2 验证路径建议

- **A 单元级**：3 个 Code 节点忠实移植（校验组包 / SEO kit 组装 / 渲染&状态校验+错误归一化），断言覆盖四 action 正例+全部 fail 分支（topic 过短/平台非法/双闸门缺失/template_id 非法/UUID 正则/未知 action/schema 缺字段/4 场景缺失/词数告警）。预估 40+ 断言。
- **B mock 全链**：保留全节点全连线；OpenAI→DeepSeek 真调（或本地 mock 双轨），Creatomate POST/GET→本地 mock server；场景 S1=draft 全流程（DeepSeek 真出脚本）、S2=render 提交、S3=status succeeded、S4=status failed、S5=audit、E1~E4=各校验失败分支（400 错误归一化）。
- **C 真跑**：DeepSeek 真调免费；Creatomate 付费→替代=本地 mock；可选加分项=ffmpeg 本地渲染替身真出 9:16 mp4（复用 intro-factory/compose 管线）。
- **推荐**：**A + B 全做，C 做 DeepSeek 真调 + mock 渲染**（与 lesson-13/16 同路径），是否加 ffmpeg 真渲染替身由老板拍板。

## 五、风险点

1. **webhook responseMode=responseNode**：分支众多时容易漏 respond（本模板每条分支都有 respond，OK）；headerAuth 凭证名需在 mock 里建。
2. **DeepSeek 兼容细节**：`response_format:{type:'json_object'}` 需 user prompt 里含 "JSON" 字样才生效（模板 prompt 已含 "Return ONLY a JSON object"，天然兼容）；gpt-4o-mini→deepseek-chat 替换无碍。
3. **JSON.stringify($json.requestBody) 的表达式坑**：jsonBody 以 `=` 开头（模板已合规），替换 URL/model 时别破坏。
4. **Switch v3.2 renameOutput 5 出口**（含 fallback Other），mock 移植时出口顺序要对齐。
5. **Audit 的阿拉伯语绝对化正则**（模板里有 `اغتنم الفرصة مضمونة`）——移植保留，属作者防伪声明细节，是教学素材。
6. **无 LLM 幻觉大坑型节点**（不像 lesson-08 营业时间心算），主要教学价值在 API 设计+护栏；L4 课程卖点可打「短视频自动化工厂的最小闭环」。

## 六、排期

- L0 立项（本报告）✅
- L2 A 单元级 → 汇报 → 老板审核
- L2 B mock 全链 → 汇报 → 审核
- L2 C 免费真跑（DeepSeek + mock/可选 ffmpeg）→ 审核
- L3 GitHub 课程库 + Pages
- L4 获客视频（走 intro-factory + publish-video.py 本机双平台）