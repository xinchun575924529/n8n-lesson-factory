# 飞书 + n8n + Litchi 航线机器人

## 功能
在飞书群里发送 `航线 <纬度> <经度> <高度m> <边长m> [间距m] [速度m/s]`，
机器人自动生成 Litchi 航点 CSV（蛇形航线，逐点拍照），推送审批卡片，
点击"确认执行"后提示到 DJI Fly → 航点飞行中导入执行。

示例：`航线 31.2304 121.4737 80 200 40 5`
（中心 31.2304,121.4737，高度 80m，200m×200m 区域，航带间距 40m，速度 5m/s）

## 一、部署 n8n
```bash
docker run -d --name n8n -p 5678:5678   -v n8n_data:/home/node/.n8n   -v litchi_missions:/data/litchi-missions   docker.n8n.io/n8nio/n8n
```
- n8n 需要有**公网 HTTPS 地址**（云服务器 / frp / cloudflared 均可）。
- 航线文件保存在容器 `/data/litchi-missions/`（已挂载卷）。

## 二、导入工作流
n8n 界面 → Workflows → Import from File → 选择 `feishu_litchi_drone_bot.json`。

## 三、创建飞书应用
1. 打开 https://open.feishu.cn → 创建**企业自建应用** → 启用机器人能力。
2. 权限管理添加：`im:message`、`im:message:send_as_bot`、`im:message.group_msg`（读群消息）、`im:chat:readonly`。
3. 事件订阅：
   - 请求地址填 `https://你的域名/webhook/feishu-drone-bot`
   - 添加事件 `接收消息 im.message.receive_v1`
   - 添加事件 `卡片回传交互 card.action.trigger`（同一个请求地址）
   - **不要开启加密**（工作流未做 AES 解密，开加密会验签失败）
4. 版本管理与发布 → 创建版本并发布。
5. 把机器人拉进目标群，群里 @机器人 发指令（或在应用后台拿到群 chat_id 填入 `notify_chat_id`）。

## 四、配置工作流
打开 **Set Config** 节点，替换三个占位符：
| 字段 | 说明 |
|---|---|
| `__FEISHU_APP_ID__` | 飞书应用 App ID（开发者后台"凭证与基础信息"） |
| `__FEISHU_APP_SECRET__` | 飞书应用 App Secret |
| `__GROUP_CHAT_ID__` | 通知群 chat_id（兜底，指令所在群优先） |

获取 chat_id 最简单的方法：先把应用凭证填好，在群里 @机器人 随便发一句，
到 n8n Executions 里看"解析指令"节点输出的 `chat_id`。

## 五、使用流程
1. 群里发：`航线 31.2304 121.4737 80 200 40 5`
2. 机器人回卡片 → 点"✅ 确认执行"
3. 从 n8n 服务器 `/data/litchi-missions/` 取出 CSV
4. 导入 Litchi Hub（litchi.io 登录 → Missions → Import），同步到 DJI Fly
5. 现场打开 DJI Fly → 航点飞行 → 执行该任务（**起飞仍需人工，合规且安全**）

## 六、可选增强
- **定时任务**：前面加一个 Schedule Trigger，每天定时给某区域生成任务
- **任务台账**：卡片确认后写入飞书多维表格（Bitable 节点），记录时间/区域/状态
- **素材归档**：飞行后手机素材自动上传网盘，n8n 监听并回传飞书群
- **安全加固**：Webhook 加 Header 校验（飞书侧设 Verification Token）

## 已知限制
- Lito X1 无 SDK：本流程自动化到"任务就绪+人工确认"为止，无法回读遥测/自动起飞
- 飞书未开加密时任何人知道 webhook 地址都可触发，生产环境务必加签名校验
- 航线为简化蛇形（等距间距、定高），复杂地形请导入后在 Litchi Hub 中微调