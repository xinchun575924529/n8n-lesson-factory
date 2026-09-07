# n8n-lesson-factory

n8n视频教案制作组 · **项目工厂**。

飞书群 D1 每日 08:10 推送候选模板，群友定选后项目入本库：

- **A 入库等待** → projects/<id>-<slug>/ 状态 backlog，待提取
- **B 立即研发** → 状态 research，自动触发研发立项（L2 验证 → L3 教案 → L4 视频）

## 目录
- projects/index.json — 全部项目索引
- projects/<id>-<slug>/project.json — 项目档案（状态/模式/历史）
- projects/<id>-<slug>/research-brief.md — 研发立项报告（B模式生成）

状态机：backlog → research → lesson → video → published