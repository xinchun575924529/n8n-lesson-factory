# 19849 立项报告：Show NASA APOD and nearest asteroid data in Home Assistant dashboards

## 项目名（建议）
NASA 每日天文图 + 最近小行星 推送到 Home Assistant 仪表盘

## 来源
- n8n 官方模板 https://n8n.io/workflows/19849/（id 19849，fresh 候选）
- 定选时间：2026-10-08 14:42（来源 fresh）

## 用途
每天 06:00（或手动触发）并行跑两条分支：
- **APOD 分支**：从 science.nasa.gov 的 WP JSON feed 拉「每日天文一图」（无需 API key），提取标题/图片/日期/280 字以内的解说，upsert 到 Home Assistant 实体 `sensor.nasa_apod`。
- **Asteroid 分支**：调 NASA NeoWS 近地天体 feed（未来 3 天窗口），按 miss distance 排序找出最近的小行星，upsert 到 `sensor.nasa_asteroid`（名称/日期/距离 km 与地月距离倍数/直径/速度/是否潜在危险/窗口内总数）。

卖点：智能家居仪表盘装饰型用例，节点少（7 个功能节点），适合入门课；NASA 两个数据源全免费。

## 节点清单（7 功能节点 + 4 sticky note）
1. `When 6AM Daily` — scheduleTrigger（typeVersion 1.3，每天 6 点）
2. `Manual Test Trigger` — manualTrigger
3. `Fetch NASA APOD Data` — httpRequest 4.4，GET science.nasa.gov/wp-json/wp/v2/apod-basic?per_page=1，retryOnFail 3 次
4. `Set APOD Fields` — set 3.4，5 个表达式赋值（title 去 HTML 标签、explanation 清洗截 280 字、image_url 按 media_type 分支取 hdurl/thumbnail_url）
5. `Send APOD to Home Assistant` — homeAssistant 节点，state upsert `sensor.nasa_apod`
6. `Fetch Asteroid Feed` — httpRequest 4.4，GET api.nasa.gov/neo/rest/v1/feed（Query Auth api_key，start/end_date 用 Luxon `$now.toFormat`）
7. `Set Asteroid Data` — set 3.4（count + raw_objects 透传）
8. `Find Nearest Asteroid` — code 2，遍历按日期分组的 NEO 数据、排序取最近者，输出格式化字段
9. `Send Asteroid to Home Assistant` — homeAssistant 节点，upsert `sensor.nasa_asteroid`

（实际功能节点 9 个含 2 个触发器；定选卡片 nodeCount=7 未计 sticky。）

## 凭证缺口与替代方案
| 原需求 | 说明 | 替代/结论 |
|---|---|---|
| NASA API key（Query Auth `api_key`） | api.nasa.gov 免费注册；另有 `DEMO_KEY` 公共演示 key（30 req/h/IP，够教学） | **零成本可得；C 真跑可用 DEMO_KEY 兜底** |
| Home Assistant（base URL + 长期令牌） | 本机/云上都没有 HA 实例 | **B mock 掉；C 真跑用本地 HTTP 接收端（n8n webhook / python http.server）替换 homeAssistant 节点，验证 payload 正确性**；教学文档说明真 HA 配置步骤即可 |
| APOD feed | science.nasa.gov WP JSON，无需 key | 直连即可。⚠️ 模板注记：NASA 已于 2026-10 退役旧 api.nasa.gov APOD 端点，此 feed 是官方迁移后的新源 |

**结论：全链路零付费可行。**

## L2 验证计划（推荐 A + B + C 全做）
- **A 单元级**：忠实移植 `Find Nearest Asteroid` Code 节点 + `Set APOD Fields`/`Set Asteroid Data` 表达式逻辑，构造 APOD/NEO 样例 JSON 断言（标题去标签、280 截断、media_type=video 时取 thumbnail_url、NEO 排序取最近、hazardous 布尔透传、空数组防护）。预计 ~20 断言。
- **B mock 全链**：保留模板全名全连线，mock 掉 2 个 NASA HTTP（固定样例数据）+ 2 个 homeAssistant 节点（改 webhook/Set 落盘校验），场景：正常日、APOD 为视频、NEO 空窗口（无小行星 → Code 节点 `closest` undefined 会抛错，**这是模板潜在坑，B 必须覆盖**）。
- **C 真跑**：NASA 两个 API 真调（APOD feed 免 key + NeoWS 用 DEMO_KEY），HA 替换为本地接收端，验证真实数据下端到端输出。成本 0 元。
- **推荐**：A 起步，B 覆盖异常分支，C 低风险真跑（NASA 免费）。

## 风险点 / 模板坑预判
1. **NEO 空窗口崩溃**：3 天窗口若无小行星（极少见但可能），`allAsteroids[0]` = undefined → 访问 `.name` 抛错。模板无守卫。
2. **APOD 新 feed 字段漂移**：science.nasa.gov WP JSON 的字段（title 可能是 `{rendered: ...}` 对象而非字符串）需实测验证——sticky note 说免 key，但 WP REST 的 title/explanation 通常包一层 `rendered`，模板的 `String($json.title)` 若拿到对象会变 `[object Object]`。**C 真跑重点验证**。
3. **HA 实体易失**：API upsert 的 sensor 在 HA 重启后消失（sticky note 已自述），教学需讲清。
4. **scheduleTrigger 时区**：工作流 settings 无 timezone，默认按 n8n 实例时区；教学包需说明。
5. **DEMO_KEY 限流**：30 req/h，C 真跑注意别频繁手动触发。
6. homeAssistant 节点 typeVersion 1 较老，导入本机 n8n 2.33 无碍但 B 替换时直接整节点换掉。

## 下一步
等老板拍板 L2 验证路径（建议 A+B+C），然后从 A 单元级开工。