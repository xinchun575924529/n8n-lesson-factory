# L2-A 单元测试报告 · 模板 21826 网站表单询盘智能分拣

- 日期：2026-11-27 ｜ 执行：研发·21826 会话
- 工作流：`L2Test218260001`（L2A-UnitTest-21826-FormTriage），CLI `n8n execute` 实跑，status=success
- 生成器：`workflows/_l2test-21826-code.js`（jsCode 单一源码）→ `workflows/wf-l2test-21826.json`

## 结果：36/36 全过，0 失败

| 组 | 对象 | 断言数 | 覆盖 |
|---|---|---|---|
| S | Set Triage Settings | 4 | 四表配置/双阈值 0.6<0.8/蜜罐默认 website+Slack 草稿默认关/截断 4000+占位凭证 |
| R | Return Category List | 5 | 6 分类/id 唯一/必备键/恰好一个 spam 且 priority=none/priority 取值域 |
| N | Normalize Form Fields | 11 | ok/缺email/坏email/缺message/蜜罐bot/email归一/超长截断/空白折叠/空body不炸/蜜罐关闭开关/fingerprint 去重键 |
| C | Check Category Is Allowed | 16 | normal/分类priority升级urgent/urgency升级urgent/spam 0.85/疑似spam 0.70/低置信0.50/未知分类拦截/空输出/AI失败/缺置信度/越界钳制1.7→1/非法urgency回退/needs_review改写/spam=0.80边界/conf=0.60边界/wants_draft开关 |

## 移植忠实性说明
4 个 Code 节点 jsCode 原文放入包装函数，仅垫 `$input`/`$('节点名')` 引用（Check Category 依赖的 `Merge Enquiry with Categories`/`Load Allowed Categories` 用夹具数据垫片，逻辑零改动）。

## 关键行为实锤（教案卖点）
1. **双阈值语义**：spam 判定要求 ≥0.8（比普通放行 0.6 更严），0.70 的垃圾只进 Review——「宁可人看，不可错杀」。
2. **白名单拦截**：AI 选出清单外 id（如 billing）一律 Review 并记录 suggested，防止 LLM 自由发挥。
3. **双路升级 urgent**：分类 priority=high（sales_inquiry/support）或 urgency=high 任一即 urgent。
4. **越界防护**：confidence 1.7 钳制到 1.0；urgency 非法值回退 normal；空 body 不炸返回 400 路线。
5. **反垃圾三板斧**：蜜罐（默认 website 字段，可关）+ email/message 校验 + fingerprint(email|消息小写) 跨执行去重。
6. **AI 失败兜底**：error 无 output → Review + ai_error=true，进 Errors 表链路。

## 已知边界（B 阶段注意）
- removeDuplicates 节点为内置黑盒未单测，B 阶段用场景验证跨执行去重。
- Merge waitForAll 遇子流空输出会断链（17522 同类坑），B 阶段 mock 保证恒有输出。