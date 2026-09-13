# 2462 Angie · L2-A 单元级验证报告（2026-09-13）

## 结论：✅ 通过（7/7 断言），并挖出 1 个模板级地雷

验证方式：本机 n8n 2.33.3 真实例、DeepSeek 真调用（凭证 `DeepSeek-as-OpenAI`，OpenAI 兼容模式，零新增费用）、webhook 触发全链真跑、结果落库回读取证。不外发（无 Telegram 收发）。

## 测试链路

`webhook 触发 → U1 纯逻辑断言 → 构造测试输入 → AI Agent（DeepSeek + Memory + 3 工具）→ U2 结果断言`

- U1（5 断言）：白名单 chat id 数字比对（本人通过/陌生人拦截）；语音/文字分流（text 空 → 语音支路）；模板 memory 硬编码 `sessionKey=angie_session_default` 缺陷识别在案
- U2（7 断言）：3 个工具全部被调用、观测值完整回传模型、最终答案融合三工具结果

实测输出（节选）：

```
987654321 × 123456789 = 121932631112635260   ← calculator 工具
14:00 weekly-product-sync / 16:30 1on1        ← google_calendar 工具
reply-customer-email / submit-weekly-report   ← task_list 工具
```

工具调用步骤完整记录：`calculator({input:"987654321 * 123456789"})` / `google_calendar({input:"today"})` / `task_list({input:"today"})`，observation 全部非空。

## 🚨 头号地雷（教案核心素材）

**模板 Agent 节点 typeVersion 3.1（V3 执行器）在本机 n8n 2.33.3 上，工具调用结果回传给模型时观测值恒为空字符串 `""`。**

证据链（三遍复现）：
1. 模型确实发起了工具调用（intermediateSteps 有 tool/input 完整记录）
2. 工具节点确实执行且返回了正确数据（执行库 runData 里 `response` 字段完好，埋点 throw 也被捕获）
3. 但模型收到的 observation 是 `""`——连 calculator 这种内置工具也一样
4. 模型只能"看到空调用"，回答谎称"结果是空的"（甚至硬算对了 18 位乘法来挽尊）
5. **Agent 降到 typeVersion 2.2（V2 执行器）后同配置全绿**

影响面：凡在 2.33.3 上按模板默认 v3.1 搭 Agent + 工具链的，全部中招。修复姿势：Agent 节点改 v2.2（或等官方修/升级 n8n 验证）。

## 顺手挖到的次级坑

1. **calculator 浮点精度**：987654321×123456789 真实值 1219326311126352**69**，工具算的是 …**5260**（JS double 精度天花板）——大数计算别信 calculator
2. **toolHttpRequest 工具节点在 2.33.3 的 Agent 链路不可用**：`has a "supplyData" method but no "execute" method`（Agent 以 execute 方式调起工具节点，该节点没实现 execute）
3. **toolCode 裸 JSON 导入必须带 `language: "javaScript"`**：UI 有默认值但裸 JSON 没有，缺了它静默走 python 分支拿到空代码，工具永远返回 ""
4. **toolCode 节点名必须用 ASCII**：CJK 节点名会导致工具注册名被清洗成 `_`，模型调了个寂寞
5. CLI `import:workflow` + `publish:workflow` 后必须重启 n8n 主实例才生效（本机 SOP 已有此条，本次再次验证）；webhook 激活到可访问有约 30-60s 延迟

## 产物

- 测试工作流：`L2AUnit246200001`「2462-单元单测(L2A)-真实模型不外发」（本机，webhook `l2a2462unit`）
- 假数据服务：`L2AMock24620001`（webhook `l2a2462mock?t=cal|tasks`，供 HTTP 类工具真调）
- 工作流 JSON：本目录 `l2a-unit-test.json`、`l2a-mock-server.json`
- 凭证：`DeepSeek-as-OpenAI`（id `DSasOpenAICred001`，baseURL api.deepseek.com/v1）

## 下一步（L2-B 建议，等拍板）

B 阶段 = 模板全链 mock 版贯通：Telegram 收发先不外发，用 webhook 模拟 TG 消息入参 + 捕获回复内容；Baserow/Google/Gmail 四工具用本报告同款假数据服务或 mock 节点替换；重点验证「语音/文字分流 → STT → Agent → 工具 → 回复」全链数据形状与模板原设计一致。成本仍为零。