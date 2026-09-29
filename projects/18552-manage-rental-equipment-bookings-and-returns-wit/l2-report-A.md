# L2-A 单元级验证报告 · 项目 18552（租赁设备预订/归还管家）

- 时间：2026-09-29（Asia/Shanghai）
- 方法：7 个 Code 节点 jsCode 原样抽出 node 真跑 + Set/If 参数级断言 + 模板坑静态留证
- 模板节点总数：58（含 5 stickyNote）

## 结果：72/72 通过


### U1
- [x] Set 含 10 个赋值字段 — booking_id,renter_name,renter_email,items,start_date,end_date,notes,total_qty,created_at,status
- [x] booking_id 表达式=RB-前缀+base36
- [x] status 硬编码 pending
- [x] email 规整=trim+toLowerCase
- [x] total_qty=逗号分割计数
- [x] includeOtherFields=true（webhook body 透传）
- [x] items 规整去空段
- [x] total_qty 复算=3
- [x] email 规整复算
- [x] created_at=$now.toISO()

### U2
- [x] 五字段非空校验
- [x] combinator=and
- [x] 全部为 notEmpty 且 loose 校验

### U3
- [x] 【坑】模板模型名=deepseek-v4-flash（非官方模型名，必换 deepseek-chat）
- [x] LLM 凭证类型=openAiApi（自定义 baseURL 中转）
- [x] temperature=0.2
- [x] Agent prompt 要求只回 JSON(availability/message/summary)
- [x] Agent 绑库存工具 Rental Inventory Tool(googleSheetsTool)
- [x] 库存计算口径 available_qty = total_qty - booked_qty

### U4
- [x] available→status=confirmed
- [x] availability 字段透传
- [x] 带 code fence 的 JSON 可解析
- [x] 【坑】partial→status=conflict（部分有货被误杀）
- [x] 【坑】非法 JSON 静默 fallback=conflict（租客被无端拒单）
- [x] fallback message 兜底文案存在

### U5
- [x] 仅 availability==available 进确认链
- [x] 【坑佐证】partial 落 false 分支（与 conflict 同路）

### U6
- [x] 输出结构 {due, due_count} — [{'due': [{'booking_id': 'B1', 'renter_name': 'A', 'renter_email': 'a@x', 'items': 'Cam', 'start_date': '2026-09-30', 'end_date': '2026-10-02', 'action': 'pickup'}, {'booking_id': 'B2', 'renter_name':
- [x] 明天起租→pickup
- [x] 今天到期→return
- [x] 昨天到期→late
- [x] 非 confirmed 行被跳过
- [x] 【坑】start=明天且end=今天(同日单) pickup 优先于 return
- [x] 空日期行被跳过
- [x] due_count=4 — 4

### U7
- [x] due_count>0 数值比较

### U8
- [x] 四条输入全产出（含未知 action）
- [x] pickup 主题含 tomorrow
- [x] pickup 正文含起租日+带ID
- [x] return 主题=return your rental today
- [x] late 主题=overdue 且正文提 late fees
- [x] 【坑】未知 action 落默认主题 Your rental confirmation（body 为空串）
- [x] to=renter_email 透传

### U9
- [x] 统计 pickup2/return1/late1 — [{'reminder_count': 4, 'pickups': 2, 'returns': 1, 'late': 1, 'summary': '2 pickup reminders, 1 return reminders, 1 late notices'}]
- [x] summary 文案格式
- [x] reminder_count=4

### U10
- [x] 8 个赋值字段
- [x] return_id=RT-前缀
- [x] condition 默认 good
- [x] returned_date=今天ISO日期
- [x] status 硬编码 logged

### U11
- [x] 三字段非空(booking_id/item_name/renter_email)

### U12
- [x] 找到库存行 found=true — [{'return_id': 'RT-1', 'booking_id': 'B1', 'renter_email': 'a@x', 'item_name': 'DSLR Camera', 'returned_date': '2026-09-29', 'notes': '', 'condition':
- [x] booked 2→new_booked_qty=1
- [x] good→damage_alert=false 且 deposit_note 空
- [x] damaged→damage_alert=true + 押金复核文案
- [x] 【防负】booked=0 归还→new_booked_qty=max(0,-1)=0
- [x] 未知物品 found=false
- [x] 物品名匹配大小写不敏感(trim+lower)

### U13
- [x] Update Booked Quantity 仅来自 Prepare Inventory Update(归还链) — ['Prepare Inventory Update']
- [x] 【坑】确认预订后只发通知，无任何库存+1动作（超卖风险实锤） — ['Alert New Rental on Discord']

### U14
- [x] total_bookings=5/returned=3 — [{'total_bookings': 5, 'active_count': 3, 'conflict_count': 1, 'returned_count': 3, 'late_count': 1, 'upcoming_count': 1, 'top_items': 'Cam x3, Tripod x1, Mic x1', 'digest_date': '2026-09-29'}]
- [x] active=3(confirmed)/conflict=1
- [x] late=1(逾期confirmed)
- [x] upcoming=1(7天内起租: __iso(2); __iso(20)不算)
- [x] top_items=Cam x3 居首 — Cam x3, Tripod x1, Mic x1
- [x] digest_date=今天

### U15
- [x] fence 被剥掉且统计字段并入

### U16
- [x] 【坑】两处无效通知收件人硬编码 user@example.com — count=5
- [x] 每日清扫 cron=0 7 * * *（跟随实例时区，国内需改）
- [x] 周报触发器存在(weekly digest 支线)
- [x] 外部节点盘点: gmail x9 / discord x10 / sheets 系 x9(含tool与update) — g=9 d=10 s=9