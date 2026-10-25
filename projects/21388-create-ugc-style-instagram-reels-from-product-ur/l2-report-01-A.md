# L2-A 单元级验证报告 · 21388

- **时间**: 2026-10-26 07:2x (Asia/Shanghai)
- **测试工作流**: `L2Test213880001`（53 节点, 19 个断言套件）
- **生成器**: `scripts\build-l2-test-21388.py` → `scripts\wf-21388-l2a-test.json`
- **执行**: AppData n8n 2.33.3 CLI, import + execute 真跑
- **结果**: ✅ **47/47 断言全过, 19/19 套件 ALL_PASS**

## 覆盖范围（模板节点忠实移植）

| 套件 | 断言 | 移植对象 |
|---|---|---|
| settings | 4/4 | Settings (set): form 直取/webhook body 回退双形态、ig_user_id 占位、graph_version v21.0 |
| extract-full | 8/8 | Extract Page Text (code): og:title 优先于 title 标签、description/image 提取、script/style 双清除、空白折叠、正文保留、跨节点 $('Settings') 引用 |
| extract-bare | 4/4 | 同上: title 兜底、缺失字段空串、正文 6000 字截断 |
| split-3 | 4/4 | Split Into Variants (code): 3 变体、编号 1..3、prompt 顺序、hook/script/caption 扇出 |
| split-5 | 1/1 | 同上: 5 条 prompt 被 slice(0,3) 截到 3 条 |
| split-2 | 1/1 | 同上: 仅 2 条 prompt → 只出 2 项（模板无守卫, 定性记录） |
| collect-variant | 5/5 | Collect Variant (set): variant 跨节点回捞、READY 保留 video_url、ERROR 置空、PROCESSING→TIMED_OUT |
| build-slack | 6/6 | Build Slack Message (code): ready_count、variants 携带、ready/failed 文案行、caption 合成 |
| pick-ok | 2/2 | Pick Approved Variant (code): decision→数字提取、选中返回 video_url+caption |
| pick-no-video | 1/1 | 同上: 选中无视频变体抛 'Variant N has no video' |
| approved-true/false | 2/2 | Was A Variant Approved? (if): Reject 走 false、其余走 true |
| is-ready-true/false | 2/2 | Is Video Ready? (if) |
| gen-fail-true/false | 2/2 | Did Generation Fail? (if): ERROR+REFUNDED or 组合 |
| under40-true/false | 2/2 | Under Max Attempts? (if): 39 继续/40 退出 |
| poll-counter | 3/3 | Start/Track Poll Counter (set×2): poll_id 传递、attempt 0→1 经 Wait 节点血缘递增、Start 丢非赋值字段（模板行为） |

## 模板行为定性（非缺陷, 课程素材）

1. **prompts < 3 条时静默少出变体**（split-2 实锤）——模板无守卫, 教案提示 LLM 必须按 schema 出满 3 条。
2. **Start Poll Counter 丢字段**（无 includeOtherFields）——Create Sisif Video 响应里除 id 外的字段到此为止。
3. **非 READY/ERROR/REFUNDED 状态一律归 TIMED_OUT**——PROCESSING 跑满 40 轮也归此桶, 文案不区分真超时与未知状态。

## 踩坑记录

- **跨节点引用时序**: Pick Approved Variant 依赖 `$('Build Slack Message')`, 独立触发分支会先跑 → ExpressionError ' hasn't been executed'。解法: 测试工作流里把 Pick 分支串到 Assert Slack Msg 之后（真实模板中天然有序, 仅测试编排需注意）。
- 修正了 1 处断言误判（把 Start Poll Counter 丢字段当成 includeOtherFields 应保留）, 属测试预期错误非模板缺陷。

## 下一步

L2-B mock 全链: 保留全节点名, Sisif/Slack/IG 三外部族 mock, 5 场景（全成功/部分失败/全失败熔断/人工 Reject/IG 超时）。等拍板。