# workflows/ · 四级配演示工作流导览

四个 JSON 四种用法：**一个用来看，两个用来测，一个用来跑**；外加一个 `free-stack.py`（零成本数据层 + STT 服务）。

| 文件 | 级别 | 用法 | 会不会真花钱 |
|------|------|------|--------------|
| `2462-original-template.json` | 原版 | **只读参考**。官方 API 实拉解包 15 节点，4 个坑原样保留——别直接上生产 | 导出不跑=0；真跑=烧 OpenAI/Google 付费 API |
| `L2A-unit-test.json` | A 级 | **单元验证**。复刻白名单/分流/记忆/工具 4 个逻辑点，7 checks 自评分 | 0（工具是假的，模型不外发） |
| `L2B-integration-mock.json` | B 级 | **集成验证**。14 功能节点 1:1 拓扑 mock，**真 DeepSeek** 驱动 5 场景 | 分毛级（DeepSeek 低价额度） |
| `L2C-free-replacement.json` | C 级 | **免费真跑**。edge-tts 真语音 → Vosk 离线识别 → Agent 真调 HTTP 工具 | ≈0（STT/工具全自托管） |

## 导入与触发

### 原版（读）
- 导入后对照 `docs/00-overview.md` 的节点地图读每一处配置。
- ⚠️ 先留意两个地方：`Simple Memory` 的 `sessionKey=angie_session_default`（坑#1）、`AllowList` 把 `<chat id>` 存成 string（坑#2 的引信）。

### L2A（测）
- 触发方式：CLI `n8n execute --id=<导入后的工作流ID>`（含 webhook 节点的工作流 CLI 最稳；注意 2.x CLI 执行需要 Execute Workflow Trigger 类起点）。
- 期望：末节点断言汇总 `7 checks` 全过；双跑应 **14/14**。
- 想体会坑：先读 `docs/05-pitfalls-defense.md`，再看每个断言是"怎么把坑按在地上验证的"。

### L2B（测）
- 前置：**DeepSeek 凭证**——Credentials 新建 **Header Auth**（Name=`Authorization`，Value=`Bearer sk-你的key`），把节点里占位凭证换成你的；假 STT webhook（`L2B` 配套）与假工具在本包内自洽。
- 期望：5 场景全过；S5 邮件摘要若促销被列出 = 你还没用 docs/04 的加固提示词。

### L2C（跑）
- 前置（三件套）：
  1. **起 free-stack.py**：`python free-stack.py` → 监听 `127.0.0.1:8766`，提供 OpenAI 兼容 `/v1/audio/transcriptions`（Vosk）+ `/tasks` `/calendar` 等假数据层。需 Vosk 中文模型 `vosk-model-small-cn-0.22`（42MB，官方站点可下）。
  2. **edge-tts**：`pip install edge-tts`，用 docs/02 的命令造 `test-voice.mp3`。
  3. **DeepSeek 凭证**同 L2B；STT 凭证用 OpenAI 形态、BASE_URL 指 `http://127.0.0.1:8766/v1`。
- 期望：5 场景全过——真 mp3 被离线识别、Agent 真调 HTTP 工具、促销邮件被 STRICTLY EXCLUDE 挡掉。
- ⚠️ 环境坑：URL 一律写 `127.0.0.1` 不要写 `localhost`（IPv6 陷阱）；端口避开 8765/5678/10088（用 8766）。

## 常见排错

| 症状 | 先看哪 |
|------|--------|
| STT 连接 refused | free-stack.py 起没起；URL 是不是写成了 `localhost` |
| Agent 幻觉自答 | toolCode typeVersion 是不是 1（升 1.3） |
| 促销邮件照列 | 系统提示词换 docs/04 的 STRICTLY EXCLUDE 死约束 |
| 白名单放不进/报错 | `looseTypeValidation` 状态 + AllowList 值类型（docs/01 对照实验） |

## 安全红线

- 本包 JSON 里的凭证 id 全是**占位/原作者残留**，不含明文密钥；导入后务必换成你自己的凭证。
- 交付生产前必须修完 docs/00–05 列的 4 个坑（尤其坑#1 记忆共享——那是隐私事故）。