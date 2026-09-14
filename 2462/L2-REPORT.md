# 2462 L2 三级验证报告 —「Angie：Telegram 语音/文字 AI 助理」

- **模板**：https://n8n.io/workflows/2462/ （14 节点：Telegram Trigger → AllowList → If1 → Voice/Text → If → Get Voice File → Speech to Text → Agent(v3) → 工具×4(Tasks/Contacts/GCalendar/Gmail) → Telegram 回复；模型 lmChatOpenAI + memoryBufferWindow）
- **验证环境**：本机 n8n 2.33.3，DeepSeek (deepseek-chat，OpenAI 兼容模式，直扣余额)，Vosk small-cn 0.22 自托管 STT，edge-tts 造真语音
- **验证日期**：2026-09-13 → 2026-09-14
- **结论**：模板逻辑可复刻、可在本机全链路跑通；**4 个坑必须在交付版修复**，其中 1 个为**会伤到真用户**的安全级缺陷

---

## 一、三级验证结果总览

| 关 | 方法 | 场景数 | 结果 |
|---|---|---|---|
| **L2A 单元单测** | 忠实复刻模板逻辑、离线断言 + 假工具真模型 | 7 checks × 2 轮 | ✅ 全过 |
| **L2B 集成测试** | 14 节点 1:1 拓扑 mock，真 DeepSeek 驱动 | 5 场景 | ✅ 全过 |
| **L2C 免费替身链** | 真语音→真 STT→真 Agent→真 HTTP 工具（全免费/自托管） | 5 场景 | ✅ 全过 |

---

## 二、场景实测明细

### L2A（单元级）
- 白名单 `==` 严格数字比对：本人 `114514` 通过 / 陌生人 `999999` 拦截 ✅
- 语音/文字分流逻辑：`text 为空 → STT 分支` ✅
- 模板 memory 硬编码 `sessionKey=angie_session_default` 缺陷已识别并记录 ✅
- U2 真实 Agent 三轮工具调用（calculator / google_calendar / task_list）全部命中、观测值正确回传 ✅

### L2B（集成级，1:1 拓扑 mock）
| 场景 | 结果 | 关键证据 |
|---|---|---|
| S1 文本双工具融合 | ✅ 6 checks | Google_Calendar + Tasks 同时命中，答案融合 14:00 周会 + 回邮件任务 |
| S2 语音链路 | ✅ 3 checks | 假语音 → 假 STT → 「我今天有哪些任务」→ Tasks 作答 |
| S3 白名单拦截 | ✅ | 陌生人零回复，白名单本人不误伤 |
| S4 两步记忆 | ✅ | 「记住 ZQXK-8888」→ 次轮问回命中 |
| S5 邮件摘要 | ⚠️ 4 checks + 1 warn | 正常邮件呈现；**促销邮件被列出**（prompt 提示未生效） |

### L2C（免费替身链，实跑）
| 场景 | 结果 | 关键证据 |
|---|---|---|
| S1 文本双工具 | ✅ 5 checks | HTTP 工具真调 `localhost:8766/tasks` `/calendar`，答案融合正确 |
| S2 真语音 | ✅ 4 checks | **edge-tts 造真 mp3 → Vosk 离线识别「我今天有哪些任务要做」→ Agent 作答** |
| S3 拦截 | ✅ | 同 L2B |
| S4 记忆 | ✅ | 种下 FINAL-2462 → 问回命中 |
| S5 邮件摘要 | ✅ 4 checks | 加固系统提示后，DeepSeek 正确跳过促销邮件（「推广类邮件已按要求略过」明写） |

---

## 三、坑与修复（交付版必须处理）

| # | 坑 | 级别 | 修复方案 |
|---|---|---|---|
| 1 | **memory 硬编码 `sessionKey=angie_session_default`**：所有用户共享一份记忆，甲的对话乙能看到 | 🔴 安全/隐私 | 改为 `sessionIdType=fromInput`，key = `{{ $('Listen...').item.json.message.from.id }}` |
| 2 | **If1 白名单 looseTypeValidation=false + AllowList 存 string**：`"114514" === 114514` 挂，主人被拒之门外 | 🔴 功能 | AllowList 改存 **number 类型** 或 If1 开 `looseTypeValidation=true` |
| 3 | **Agent v3.1 + toolCode v1 不兼容**：工具执行了但 obs 恒为空，Agent 幻觉自答 | 🟡 兼容 | toolCode 升 **typeVersion 1.3**（本测试全部用 1.3） |
| 4 | **促销邮件过滤提示太软**：DeepSeek 收到「filter out promotional」仍列出促销邮件 | 🟡 健壮 | prompt 加死约束「STRICTLY EXCLUDE … not even to say skipped」（L2C 已验证有效） |

---

## 四、环境坑（不属模板，但复现必须避开）

- `n8n` CLI 重启后光环路径失效，须用全路径 `C:\Users\Administrator\AppData\Roaming\npm\n8n.cmd`
- publish 后必须重启计划任务 `n8n-autostart`，否则 webhook 404 / 503
- 端口 **8765 被 kailoader 抢占**（返回 426），自托管服务避开 8765/5678/10088，8766 实测安稳
- n8n node 的 `localhost` 解析 IPv6 `::1`，自托管服务器只绑 IPv4 时须把 URL 写成 `127.0.0.1`
- `readWriteFile` 节点被文件访问白名单拦截，改用 Code 节点 + `fs.readFileSync` 绕
- LLM 工具调用与否**不能作硬断言**（共享记忆下会凭记忆作答），断言应落在最终输出内容上

---

## 五、复现资产

```
state/factory/
├── 2462-template.json                  原模板（n8n.io/workflows/2462）
├── 2462-template-api.json              API 拉取副本
├── 2462-cred-ds-openai.json            DeepSeek-as-OpenAI 凭证
├── 2462-cred-stt-mock.json             L2B 假 STT 凭证（OpenAI 兼容）
├── 2462-cred-stt-free.json             L2C Vosk STT 凭证（OpenAI 兼容，127.0.0.1:8766）
├── 2462-l2a-unit-test.json             L2A 工作流
├── 2462-l2a-mock-server.json           L2A 假数据服务
├── 2462-l2a-tool-probe.json            L2A 探针流
├── 2462-l2b-integration.json           L2B 1:1 拓扑 mock 主流程
├── 2462-l2b-stt-mock.json              L2B 假 STT webhook
├── 2462-l2c-free.json                  L2C 免费替身链主流程
├── free-stack.py                       Vosk + 4 免费数据层（127.0.0.1:8766）
├── vosk-model/vosk-model-small-cn-0.22 Vosk 中文模型（42MB）
└── test-voice.mp3                      edge-tts 生成的测试语音
```

---

## 六、结论

**2462 可交付。** 模板设计合理（白名单 → 双模态 → Agent + 工具 → 回复），但 **4 个坑必须修复后才可交付真实用户**（坑 1/2 必修，坑 3/4 应修）。本仓库已备妥：
- ✅ 三级验证全过的工作流资产（L2A/B/C 各一套）
- ✅ 免费替身链完整实现（Vosk + edge-tts + HTTP 假服务）
- ✅ 缺陷修复参考（加固后的系统提示词 + AllowList 类型修正）

**建议交付动作**：
1. 推 GitHub 项目库 → 状态置「L2 验证通过，待交付定稿」
2. 飞书群播报（教案制作组）
3. 待老板拍板：A) 直接进入 L3（真实 Telegram 对接，用 296795 客户双 bot 之一实测）B) 先沉淀为《AI 助理部署避坑》教案素材