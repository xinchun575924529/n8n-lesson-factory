# L2-B mock 全链验证报告 · 模板 21826 网站表单询盘智能分拣

- 日期：2026-11-27 ｜ 执行：研发·21826 会话
- 工作流：`L2Mock218260001`（29 节点，保留模板全节点名+全连线，仅外部依赖换 mock）
- 生成器：`scripts/build-l2-mock-21826.py` → `workflows/wf-l2mock-21826.json`
- 驱动器：`scripts/run-l2-mock-21826.py`（逐场景清目录→写指针→CLI execute→读台账断言）
- mock 口径：OpenAI agent→场景预制输出（含 AI 失败模拟）；Google Sheets→本地 JSON 台账（enquiries/review/spam/errors.json）；Gmail→sent-mail.json；webhook→Scenario Loader；Slack 默认关（配了违规侦测 slack-FIRED.json）

## 结果：9/9 场景全过

| 场景 | 验证点 | 结果 |
|---|---|---|
| S1 正常询盘 | 200 即时响应 + Enquiries 落表 + 无邮件（普通件不打扰） | ✅ |
| S2 紧急询盘 | support(priority high) → urgent 分支 → Enquiries + urgent 告警邮件 | ✅ |
| S3 垃圾(0.85) | 达 0.8 阈值 → Spam 落表 + 无邮件 | ✅ |
| S4 低置信(0.5) | <0.6 → Review 落表 + 复核请求邮件 | ✅ |
| S5 AI 失败 | error 无 output → Review(needs_review) + Errors 落表 + 复核邮件（双链路兜底） | ✅ |
| S6 重复提交 | 同 fingerprint(email\|消息) 第二次被 removeDuplicates 跨执行丢弃 | ✅ |
| S7 蜜罐机器人 | 静默 200，全链路零落账 | ✅ |
| S8 坏邮箱 | 400 拒绝 + error 文案，全链路零落账 | ✅ |
| S9 写表失败 | Sheets 异常 → error 分支 → Prepare Failure Alert → 失败告警邮件（Enquiry not saved） | ✅ |

## 踩坑实录（教案素材）
1. **Merge 输入接反（已修）**：模板接线=Dedup→Merge input0、Load Categories→Merge input1，useDataOfInput=1 取「Input 1」(=index0 询盘数据)。接反后 Check Category 读到 categories 分支，`cfg.min_confidence`  undefined 直接炸——**merge chooseBranch 的 useDataOfInput 是 1 起始的 UI 编号**。
2. **removeDuplicates 跨执行历史真实持久（CLI 也生效）**：首次错误运行把测试指纹写进历史，后续同指纹场景全被静默丢弃（表现为「执行成功但零落账」极难排查）。**教训：去重节点测试数据必须每次唯一指纹；验证去重功能本身则同指纹跑两次**（S6 正是此法）。
3. respondToWebhook 在 CLI 无真实 HTTP 上下文 → mock 换成写 response.json 的 Code 节点（名字保留）。
4. Agent 双输出（main+error）在 mock 合并为单路 error 数据，Check Category 的 `item.json.error && !item.json.output` 判定语义不变。

## 与 A 阶段衔接
A 的 36 断言管 Code 节点逻辑正确性；B 的 9 场景管全链连线/分流/兜底/去重正确性。两阶段交叉验证无冲突。