# L2-B mock 全链报告 · 模板 21388

> 日期：2026-10-27 | 结果：**25/25 全绿（5/5 场景 ALL_PASS）**

## 场景覆盖

| 场景 | 描述 | 断言 | 结果 |
|------|------|------|------|
| S1 | 全成功：3 变体 READY → 审批 V2 → IG 发布 | 7 | ✅ |
| S2 | 部分失败 2/3：V1 READY / V2 ERROR / V3 重试后 READY → 审批 V1 → IG 发布 | 7 | ✅ |
| S3 | 全失败：3 变体全 ERROR → ready_count=0 → All Variants Failed | 4 | ✅ |
| S4 | 人工拒绝：2 READY → 审批 Reject → 流程终止 | 3 | ✅ |
| S5 | IG 超时：审批通过 → IG 容器 40 次轮询不完成 → 超时报错 | 4 | ✅ |

## 验证要点

### 双轮询循环（Sisif + IG）
- Sisif 轮询：Start Poll Counter(attempt=0) → Wait → Check Status → Track Poll(attempt+1) → Is Ready? → (not ready) → Did Fail? → (not failed) → Under Max? → Wait (loop)
- IG 轮询：同构，Start IG Poll → Wait → Check → Track IG Poll → Is Finished? → Under IG Max? → Wait (loop)
- S2 V3 验证了 PROCESSING×2 后 READY 的重试路径，attempt 正确递增

### 状态映射（Collect Variant）
- READY → video_url 保留
- ERROR → video_url 置空，status=ERROR
- TIMED_OUT → 40 次后兜底，status=TIMED_OUT

### 审批流
- ready_count>0 → Any Variant Ready?=true → Slack 审批
- decision≠Reject → Was Approved?=true → Pick → IG 发布
- decision=Reject → 流程静默终止（模板无显式 reject 处理节点）

### 终止路径
- All Variants Failed：ready_count=0 时触发，错误信息含各变体状态
- IG Processing Timed Out：40 次轮询后触发

## 模板行为确认（B 阶段新发现）

1. **Reject 无显式处理**：模板 Was A Variant Approved? 的 false 分支无连接，Reject 后流程静默结束
2. **Track Poll Attempt 位置**：在 Check Video Status 之后（先查状态再计次数），意味着 attempt=0 时第一次检查
3. **SplitInBatches done 输出**：聚合所有 Collect Variant 输出供 Build Slack Message 使用，连接正确

## 工程参数
- 5 个独立工作流 JSON（31/31/21/23/31 节点）
- Mock 替身：Fetch Page / LLM / Sisif Create+Status / Slack Approval / IG Create+Status+Publish / stopAndError×2
- Wait 节点缩短为 1s（模板 15s/30s）
- 模板核心逻辑（Code/Set/If）全部 verbatim 保留

## 下一步
L2-C 免费真跑：DeepSeek + ffmpeg 替身