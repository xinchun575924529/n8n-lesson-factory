# 立项报告 · 项目 20211

## 基本信息
- **项目名**：Build and deploy tested workflows from chat with Claude Sonnet（内部名 **The Alchemist / 炼金术士**）
- **来源**：n8n 官方模板库 https://n8n.io/workflows/20211/
- **定选时间**：2026-10-04 15:46（fresh 候选，B 立即研发）
- **节点数**：16 功能节点（另含 3 张 stickyNote 说明卡）

## 用途（一句话）
聊天窗口里输入一句「我想自动化什么」，AI 自动**理解需求 → 生成 n8n 工作流 JSON → 校验/测试 → 通过 n8n API 直接部署**到你的实例——"一句话进，一个测过的流程出"。

## 工作流结构
- **主通道（顶行）**：Chat Trigger（公开聊天页）→ Read Request（解析目标 URL/告警 webhook/邮箱/Slack 频道，SSRF 私网拦截，日限流计数）→ Check Mock Webhook → Initialize Case（构建贯穿全程的 state 对象）→ Run Section（executeWorkflow **递归调用自身**，按 stage 分发）→ Decide Next Step（决策：下一节/回炉修复/收尾回复）
- **8 个子节（Section Router 按 stage 分流）**：
  1. Understand：目标 → 规格 spec
  2. Build：spec → 工作流 JSON
  3. Check：草稿校验（调节点目录核 schema）
  4. Review：仅 blueprint 类，第二个 LLM 评审 + 修复轮
  5. Test：仅 monitor 类，mock 测试 + 真实冒烟
  6. Deploy：n8n API 创建并可激活工作流
  7. Node Catalog：拉 n8n-nodes-base / langchain 节点目录与输出 schema
  8. Test Mock：内置 webhook 模拟 HTTP 响应
- **两类产物**：Monitor（监控类，测过自动激活）/ Blueprint（蓝图类，评审后不激活交付）

## 节点类型清单
chatTrigger、code（多个大体量 JS）、httpRequest、executeWorkflow（递归自调用）、if、switch、wait、set、noOp、webhook、stickyNote

## 凭证缺口与替代方案
| 原模板需要 | 用途 | 免费替代 | 结论 |
|---|---|---|---|
| **Anthropic Claude Sonnet**（3 处：Spec/Build/Review） | LLM 理解与生成 | **DeepSeek deepseek-chat**（现成 key，直连不耗积分） | ✅ 可替换；风险=生成工作流 JSON 的稳定性比 Sonnet 弱，prompt 需加 JSON 强约束 |
| **n8n API credential**（Create/Activate Workflow） | 部署到本实例 | 本机 n8n REST API（`http://localhost:5678/api/v1`，API key 自建免费） | ✅ 零成本 |
| Chat Trigger 公开聊天页 | 用户入口 | 本机自带，无需凭证；可开 Basic Auth | ✅ |

**结论：全链可 0 元跑通（DeepSeek + 本机 n8n API）。**

## L2 验证计划（推荐）
- **A 单元级**：移植 Read Request / Initialize Case / Decide Next Step 三大 Code 节点（含 SSRF 拦截表、日限流、递归状态机逻辑）做断言单测。这批 JS 是模板精华（IPv4 各种进制形态/IPv6 展开/私网拦截），单测价值高。
- **B mock 全链**：保留全节点全连线，Anthropic 节点换 mock（固定返回 spec/草稿 JSON），n8n API 换 mock webhook，跑"monitor 一句话 → 部署"与"blueprint 一句话 → 交付"双场景。
- **C 真跑（0 元版）**：DeepSeek 真调（Spec/Build 两段）+ 本机 n8n API 真创建（建到测试区、不激活），跑一条真实 blueprint 请求验证闭环。
- **推荐路径：A → B → C 全做**（本项目是"AI 造工作流"旗舰模板，递归自调用 + SSRF 防护 + 双 LLM 评审都是教学卖点，值得三关全验）

## 风险点（预判）
1. **递归 executeWorkflow 自调用**：模板要求"每次编辑后重新 Publish，否则子节跑旧版"——L2 验证时 import 后必须 publish 才测得通，是首个大坑候选。
2. **DeepSeek 替 Claude 的生成质量**：Build 节输出的是可部署的工作流 JSON，DeepSeek 可能出现非法 JSON/编造节点类型；模板靠 Node Catalog + Check 环节兜住，C 阶段要重点看这个兜底在 DeepSeek 下是否够硬。
3. **typeVersion 兼容**：模板钉在 n8n-nodes-base 2.39.7 / langchain 2.39.8，本机是 2.33.3（守护）+ 2.37.10（CLI 残留）——chatTrigger typeVersion 1.1、executeWorkflow 1.2 在本机是否齐全需先探。
4. **静态数据依赖**：日限流用 `$getWorkflowStaticData`，CLI 手动执行不持久化，单测要绕。
5. **超时可配置**：TIME_BUDGET_MINUTES 12min、workflow timeout 20min——LLM 真跑耗时长，C 阶段注意执行窗口。

---
*研发·20211 车间 · 2026-10-04*