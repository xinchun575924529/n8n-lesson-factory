# 19457 L2 验证报告（A 单元级 + B mock 全流程）

日期：2026-09-25 ｜ 执行：研发·19457 会话 ｜ 结论：**A+B 双绿，建议进 L3**

## A 单元级：53/53 全过 ✅
忠实移植 7 个 Code 节点原 jsCode（5×Normalize + Prepare + Validate），Node 22 harness 注入 `$input`/`$()` 桩运行（零改动本机 n8n）。覆盖：
- 5 源四态机（ok/error/empty/invalid）+ change_percent 计算 + FRED 过滤 `.` 值 + Marketaux source+title 去重 + cleanText 空白折叠
- 错误消毒 sanitizeError：401/403/429/5xx/apikey 文案归一化
- Prepare：5 源汇总、core_source_failures 只计核心源、缺失分支合成 error 占位
- Validate：非法 JSON 抛错、market_regime 枚举拒绝 `euphoric`、对象型 regime `{label:'Risk-Off'}`→`risk_off`、非数组字段兜底、assets/drivers/watch_next 规范化映射

### 发现 4 个模板怪癖（非阻断，已在断言中固化为行为文档，L3 课程可讲）
1. **裸 `{message:'Credentials not found'}` 不判 error**——failed 检测只看 error/errors/status==='error'/code+message，裸 message 会落到 invalid。真实 n8n 凭证错误经 httpRequest `onError: continueRegularOutput` 输出 `{error:{...}}` 结构，能命中，所以实际无害。
2. **sanitizeError 不读 `r.code`**——`{code:500,message}` 打出 'HTTP 500: ...' 靠的是 message 里的数字，code 字段本身不进 HTTP 前缀。
3. **`{statusCode:500}` 单独出现会漏检**——failed 检测不含 statusCode，会被当成 ok（零事件）。属真实漏检面，但 API 真挂时 httpRequest 层会先产出 error 字段兜住。
4. **`all_sources_completed` 恒为 true**——Prepare 先给缺失分支合成 error 占位再做 every 检查，该字段无判别力（看 core_source_failures 才有意义）。

## B mock 全流程：通过 ✅（DeepSeek 真调）
mock 5 源数据（SPY/QQQ/GLD/TLT、BTC/ETH、DGS10、PCE 日历、3 条新闻）→ 归一化 5/5 ok → Prepare → **DeepSeek-chat 真调**（替换假模型 gpt-5.6-luna；response_format=json_object，4025 tokens）→ Validate 通过（market_regime=mild_risk_on）→ Telegram 文本 + Discord embed + Postgres INSERT 三件产物全部生成。

**AI 输出质量抽检**：价格/涨跌幅与 mock 输入完全一致（SPY 667.20 +0.92% ✓、BTC $113,200 +1.8% ✓），PCE 事件时间用配置的 report_timezone 表达，missing_sources 如实声明数据覆盖边界，无编造——模板的"纪律性提示词"在 DeepSeek 上复现成功。

产物：`state/factory/19457-l2/out/`（b-prepared.json / b-ai-raw.txt / b-brief-validated.json / b-telegram.txt / b-discord.json / b-insert.sql），harness 与 fixtures：`state/factory/19457-l2/harness.js`

## 凭证结论复核
- 假模型 gpt-5.6-luna → **DeepSeek-chat 替换验证成功**（B 关实证）
- Twelve Data / FRED / Marketaux 免费 key，CoinGecko 免 key；QuantGist 付费 → L3 课程按「可裁剪源」处理（mock/降 4 源均不影响主链路，已验证缺失分支合成机制）
- TG/Discord/PG 投递在 B 关以产物文件替代；真发留 C（可选）或学员练习

## 建议
进 L3（GitHub 课程库 + 全套教案）。课程号按机制自动增号（取 max+1）。是否还需要 C 真跑（4 免费源注册真调 + 真发 TG/Discord）请老板一并拍板；研发组意见：**不需要**，B 已覆盖 AI 真调核心，C 的增量是注册流程演示，可做成课后练习。