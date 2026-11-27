# L2-C 免费真跑验证报告 · 模板 21826 网站表单询盘智能分拣

- 日期：2026-11-27 ｜ 执行：研发·21826 会话
- 工作流：`L2Cstm21826001`（L2C-Free-21826-FormTriage，29 节点，mock 底版换三件真货）
- 生成器：`scripts/build-l2-c-21826.py` → `workflows/wf-l2c-21826.json`
- 驱动器：`scripts/run-l2-c-21826.py`
- **真跑口径**：OpenAI→**真 DeepSeek**（deepseek-chat，运行时读 state/deepseek-key.json，JSON 模式，temp 0）；Gmail→**真飞书群推送**（N8N教案 app → 教案制作组群，运行时读 state/feishu-creds.json）；Google Sheets→本地 JSON 台账（state/21826-c-data/）；Slack 不启用。**全程零付费环节，DS 成本 ≈3 次调用（分毫级）**。

## 结果：6/6 场景全过

| 场景 | DeepSeek 实际判定 | 结果 |
|---|---|---|
| C1 售前询盘（50 席位+今天想定） | **sales_inquiry / urgency high** → Enquiries 落表 + 紧急飞书推送（New sales inquiry (high urgency): Bob Li） | ✅ |
| C2 客户故障投诉（今天就要修） | **support / urgency high** → Enquiries + 紧急飞书推送（New support (high urgency): Carol） | ✅ |
| C3 明显垃圾（SEO 推销） | **spam 且置信≥0.8** → Spam 落表，零打扰 | ✅ |
| C4 蜜罐机器人 | 静默 200 零落账（未调 DS） | ✅ |
| C5 坏邮箱 | 400 零落账（未调 DS） | ✅ |
| C6 去重（同 C1 指纹二次提交） | removeDuplicates 跨执行丢弃，未进 AI | ✅ |

## 关键证据
- 台账：state/21826-c-data/{C1..C6}/{enquiries,spam,review,errors,sent-mail}.json 逐场景可查
- 飞书群实收：[21826-C][urgent] 两条真实推送（C1/C2 告警），内容与模板 alert_subject/alert_text 格式一致
- DeepSeek 对模板 JSON schema 输出约束遵守度：3/3 次返回合法 JSON，分类 id 全部命中白名单，urgency 取值合法（L1 风险点③实测排除）

## 与 A/B 的关系
- A（36 断言）= Code 逻辑正确性；B（9 场景）= 连线/分流/兜底/去重；C（6 场景）= 真实 LLM + 真实推送通道闭环。
- DeepSeek 替换 OpenAI 无损：模板的双阈值/白名单机制对 LLM 不确定性天然容错（低置信自动进 Review）。

## 结论
**模板 21826 在 100% 免费替代栈上全链验证通过**，可进 L3（GitHub 教案仓库）阶段。