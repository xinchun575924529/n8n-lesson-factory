# 04 · 系统提示词工程：让模型"说到做到"

## 模板系统提示词（脱敏缩写，原文在 workflows/2462-original-template.json）
```
Today is {{ $now }}.
You are Angie, a helpful personal assistant.
Tools available: Task list (baserow), Contacts (baserow), Google Calendar, Gmail.
When summarizing email, filter out promotional messages.
...（约 300 字）
```
做得对的地方：
- **日期注入** `Today is {{ $now }}` —— "今天/明天"才有锚点；
- **工具清单明确**，减少模型乱编不存在的工具；
- **人格一句话**（helpful personal assistant），不端着。

## 🟡 坑#4："filter out promotional" ≈ 没写（实测打脸）
L2B-S5：邮件列表里混一封促销邮件，模板原文只说 `filter out promotional messages`，结果 DeepSeek **照样把它列进摘要**，还加了句 "some promotional offers"。
**原因**：祈使句 + 无后果描述，模型把它当"建议"。
**修复（L2C 复测有效 ✅）**：改用 **死约束 + 负向行为也禁止**：
```
STRICTLY EXCLUDE promotional, marketing, or advertising emails from any summary —
do not list them, do not mention they exist, not even to say they were skipped.
```
L2C 复跑：摘要里只剩正常邮件，模型甚至没有那句"我已跳过推广"的废话 ✅。

## 三条可直接抄的加固模式
1. **禁止幻觉兜底**：`If a tool returns empty or errors, say "I couldn't check X" — never invent the answer.`（治 toolCode 坑的"最后一道护栏"）
2. **输出预算**：`Answer in under 120 Chinese characters unless the user asks for detail.`（Telegram 阅读体验）
3. **工具失败话术**：`When Gmail/Calendar is unreachable, apologize once and offer to retry later.`（配 docs/01 的拥塞兜底）

## 提示词逐层试验法（备课方法学）
| 层 | 改什么 | 看什么 |
|---|---|---|
| L1 句法 | 措辞/语气 | 单条输出 |
| L2 结构 | 加小节、加清单 | 10 条输出的一致性 |
| L3 死约束 | STRICTLY/NEVER/ALWAYS | 对抗样本（促销邮件、空工具返回）是否被驯服 |
不要在 L1 层就下结论"这个模型不行"——多数"不听话"在 L3 层都能治。