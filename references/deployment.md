# 部署（委托 deploy 外部能力）

> **职责边界**：geo-cms 不实现部署平台 API。本文件指导如何**委托** `config.capabilities.deploy`
> 选定的来源把静态产物上线；部署是必要外部能力，阶段零必须确认有真实来源，不可降级。

统一要求：**产物必须是纯静态**，否则拒绝上线（此门禁由 bridge 把关）。

---

## 通用前置（bridge 自身）

1. 运行 `config.site.buildCmd` 构建。
2. 校验 `config.site.outputDir` 为纯静态（见 geo-optimization.md「静态产物校验」）。
3. 确认线上回滚能力（平台版本 / 远程目录备份），部署失败可恢复。

---

## 适配器 A：EdgeOne Pages（连接器，mode=connector）

本机已连接 **EdgeOne Makers** 连接器，优先**委托**其技能部署：

- `config.deployment.type = "edgeone-pages"`，`capabilities.deploy.resolved = "edgeone-pages"`
- 字段：`project`（项目名，可新建）、`distDir`（静态产物目录，默认 `out`）
- 流程：调用 EdgeOne Pages 技能将 `distDir` 部署/更新到指定项目，取回线上 URL 供步骤 8 验收。
- 平台自带版本与回滚，部署异常直接在平台回退上一版。

---

## 适配器 B：自有服务器（custom-server，bridge 执行 rsync 编排）

- `config.deployment.type = "custom-server"`
- 字段：`ssh`（user@host）、`remoteDir`（静态根目录）、`distDir`
- 流程（先备份再同步，避免误删）：

```bash
# 备份远程当前版本
ssh <ssh> "cp -r <remoteDir> <remoteDir>.bak-$(date +%Y%m%d%H%M)"
# 同步静态产物（删除式，但已备份）
rsync -az --delete <distDir>/ <ssh>:<remoteDir>/
```

- 失败处理：保留 `.bak-*` 不删；修复后重跑 rsync，必要时 `cp -r` 回滚。
- 注：此处 rsync 属「部署编排」，非 geo-cms 自研部署能力；若用户希望改用其他同步工具，按需调整。

---

## 适配器 C：其他（other）

用户自述方案（如对象存储 + CDN、GitHub Pages 等）。按用户确认的步骤执行，
但**仍须满足纯静态门禁**与「可回滚」两条硬约束。

---

## 部署后动作

- 记录线上 URL（首页 + 本次更新页面路径）供验收。
- 更新 `config` 中本次部署时间（可选）。
- 进入阶段二步骤 8 浏览器验收。

---

## 失败与回滚

| 场景 | 处理 |
|------|------|
| 构建非静态 | 退回 geo-optimization.md 修正 SSG，禁止上线 |
| 部署中断 | EdgeOne 平台回滚 / 自有服务器用 `.bak-*` 回退 |
| 线上 404/异常 | 不覆盖结论，先回滚再排查，复验通过再切流 |
