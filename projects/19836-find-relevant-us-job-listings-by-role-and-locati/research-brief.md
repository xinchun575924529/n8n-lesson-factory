# 立项报告 · 项目 19836

## 项目名
**Find relevant US job listings by role and location with Jobright forms**
（中文建议名：Jobright 表单式美国职位搜索）

- 来源：https://n8n.io/workflows/19836/
- 模板 API：https://api.n8n.io/api/workflows/templates/19836（200，含完整 workflow）
- 定选时间：2026-09-27 08:57（fresh 候选，定选人 ou_505161df…）
- 节点数：8 个功能节点 + 2 便签 = 官方标 5（实际功能 8）

## 用途
零凭证的职位搜索小工具：n8n 原生表单收集「职位名称 + 地点 + 远程偏好」→ 调 Jobright 匿名访客搜索 API → 校验格式化 → 用 n8n Form completion 页渲染最多 5 条职位卡片（标题/公司/地点/工作模式/链接）。失败链路有独立错误页。

卖点：**全模板零凭证、零第三方账号**，是纯 n8n 内置节点（formTrigger/code/httpRequest/form）组合，教学价值在于「表单触发器 + 匿名公开 API + Form completion 渲染 HTML」这条轻量模式。

## 节点清单
| 节点 | 类型 | 作用 |
|---|---|---|
| Job search form | formTrigger 2.2 | 表单入口（3 字段，path=find-relevant-jobs-with-jobright） |
| Build search request | code | 入参校验+组装 Jobright 请求体（workModel 映射 1/2/3） |
| Search Jobright jobs | httpRequest 4.2 | POST jobright.ai/swan/recommend/visitor-list/jobs（count=5，timeout 120s） |
| Validate and format jobs | code | 校验 success/result.jobList，抽取 5 字段+兜底 URL |
| Render job results | code | 渲染 HTML 卡片（escapeHtml + safeUrl 双重防护） |
| Show relevant jobs | form 2.3 completion | showText 显示结果页 |
| Explain search failure | code | 错误分支渲染失败 HTML |
| Show search failure | form 2.3 completion | 错误页 |
| （便签×2） | stickyNote | 说明 + Setup |

所有 code/http 节点均配 `onError: continueErrorOutput` → 错误统一汇入「Explain search failure → Show search failure」，错误网设计完整，是教学加分点。

## 凭证缺口与替代方案
**无任何凭证需求**（模板自述 no-credential）。唯一外部依赖：
- `https://jobright.ai/swan/recommend/visitor-list/jobs` 匿名公开端点
  - ⚠️ 风险：第三方未公开文档的内部 API，可能随时改签名/加鉴权/限流/挂 Cloudflare；国内本机直连可达性未验证（可能被墙或慢）
  - 替代方案：C 真跑时若不可达 → mock 响应体走 B 路径收官；或换公开职位 API（如 Arbeitnow 免费 API / RemoteOK）作为「免费替身链」教学点

## L2 验证计划
- **A 单元级**：4 个 Code 节点忠实移植单测（Build search request 入参校验/workModel 映射/截断；Validate and format jobs 正常+异常响应+兜底 URL；Render job results HTML 转义/safeUrl 协议白名单；Explain search failure 错误消息提取）。预计 20+ 断言，零外网依赖，**推荐先做**。
- **B mock**：mock Jobright 响应（成功 5 条/空列表/失败 errorMsg/HTTP 超时）跑全链，验证错误网分支。可做，价值中等（链路本身简单）。
- **C 真跑**：激活表单 URL，浏览器提交真实表单（Software Engineer / San Francisco / Any）验证 Jobright 端点可用性。零成本，但取决于端点从本机的可达性。
- **推荐路径：A 全做 + C 真跑（零成本）**；B 视 C 的结果定——C 通则 B 可略，C 不通则 B 补位收官。

## 风险点
1. Jobright 匿名端点稳定性不可控（非公开 API，随时可能失效或加鉴权）→ 教案需写「端点失效时的替代教学点」
2. 本机直连 jobright.ai 可达性未验证（海外站，必要时挂 WARP 进程级测试；遵守系统代理禁令）
3. 模板本身极简单（5 节点标称），教案厚度需靠「模式拆解 + 错误网设计 + 替代 API 扩展练习」撑
4. 目标用户是美国求职者场景，国内学员代入感弱 → L3 教案可考虑中文化改编（换成国内可用的职位 API 作练习）
5. formTrigger 生产 URL 需激活工作流，教学时注意 n8n 2.33 热更铁律（import→publish→重启）

## 下一步
等老板拍板 L2 路径（建议 A 单元级起步 + C 真跑探活）。