# 20558 L2 验证报告（A+B+C 三关全绿 ✅）

模板：https://n8n.io/workflows/20558/ （工作日 AI 新闻晨报 → Slack，You.com + TypeSafe Jev）

## L2-A 单元级：✅ 23/23 全过

- 工作流 `L2Test205580001`（48 节点 / 15 用例 / 23 断言），生成器 `scripts/build-l2-test-20558.py`，驱动 `run-l2a-20558.py`，结果 `scripts/l2a-20558-result.json`
- 覆盖三个逻辑单元（模板无 Code 节点，逻辑全在表达式）：
  - **Prepare article**：urlKey 剥离 query/hash、description/page_age 缺失 `?? ''` 兜底
  - **Jev 过滤阈值**（移植为 Set 布尔表达式）：0.79/0.80、1.29/1.30 边界、answers 整体缺失、score 缺失——`?.`/`??` 可选链在本机 n8n 表达式中工作正常
  - **Format Slack brief IIFE**：`**`→`*`、标题降级、`[[1,2]]` 引用→Slack 链接、越界引用丢弃、单复数 meta

### 🕳️ A 关挖出的坑（教案素材）
1. **模板 IIFE 里的反引号模板字面量 `${...}` 在 Code 节点 jsCode 里被 n8n 当表达式起始符** → `Missing } in template expression`。移植 Code 节点必须改字符串拼接。
2. **本机 n8n 2.33.3 的 Set 表达式解析器不认 `{{ }}` 内的 `${}` 模板字面量** → `NodeOperationError: invalid syntax`。**即：该模板原样导入本机 2.33.3 会在 Format 节点直接崩**，必须把 `` `<${url}|[${i}]>` `` 改成 `'<' + url + '|[' + i + ']>'`。（新版 n8n Cloud 无此问题，属版本兼容坑。）

## L2-B mock 全链：✅ S1 10/10 + S2 去重通过

- 工作流 `L2Mock205580001`（15 节点，模板全节点全连线保留；You.com search/Jev/You research/Slack 四外部件换 mock），生成器 `build-l2-mock-20558.py`，驱动 `run-l2-mock-20558.py`，结果 `l2b-20558-result.json`
- S1 正常链：2 主题 × 5 篇（含常青 tracker、列表文、题外话、低分观点、同 URL 镜像）→ 精确过滤，A 组 3 篇 / B 组 2 篇，格式化引用链接全对，被滤 URL 零残留
- S2 去重：第二次执行同一流 → removeDuplicates 跨执行记忆全滤，下游零产出 ✅

### 🕳️ B 关挖出的坑（教案素材）
3. **removeDuplicates `removeItemsSeenInPreviousExecutions` 只跨执行去重，同一次执行内的重复 urlKey 照样放行**（a5 镜像篇进了 S1 输出）——模板语义就是如此，指望它管内去重会误判。
4. **去重历史不随 import:workflow 覆盖清空**：复跑前必须先把节点切 `clearDeduplicationHistory` 跑一次（模板自带警告的实操版，已固化进 runner）。
5. runOnceForEachItem 模式 Code 节点必须返回单对象 `{json:...}`，返回数组报 `A 'json' property isn't an object`。

## L2-C 免费真跑：✅ 全绿（2026-11-01 充值后重跑通过）

- 工作流 `L2Cstm20558001`（16 节点）：HN Algolia 免费 API 换 You.com、DeepSeek 换 Jev+Research、飞书群换 Slack；生成器 `build-l2c-20558.py`，驱动 `run-l2c-20558.py`（含去重历史预清），结果 `l2c-20558-result.json`
- 真跑：HN 真搜 12 篇 → DeepSeek 真评 12 篇（1 篇 0.85/0.9/2 过阈值：Mistral 4 发布，Reuters 源）→ DeepSeek 写真晨报 → **飞书群推送 code 0** ✅
- 推送成品实测：`*AI model releases: morning brief*` + `_1 new article since yesterday_` + 带 `<url|[1]>` 引用的 bullet，格式与模板 Slack mrkdwn 完全一致
- 🕳️ C 关新增坑：
  6. Google News RSS 本机被墙超时；Bing News RSS 返 HTML 反爬页（RSS 解析器 Invalid attribute name）；**HN Algolia API（免 key）是本机唯一通畅的英文新闻源**
  7. HTTP 节点 `includeInputData` 在本机不可靠（topic 丢成 null）→ Code 节点用 `$('Config').first().json.topics` 按输入顺序对齐
  8. **jsonBody 外层 `={{ }}` 里嵌套 `{{ }}` 占位符会静默失败**（DeepSeek 返回体无 choices，评分全落兜底 0 且不报错）→ prompt 内容必须用 JS 拼接构造；判 C 关失败先查余额（402 会走 onError 静默过）
- 首跑曾遇 DeepSeek 402 余额不足（账户 -0.02），充值 50 后一把过