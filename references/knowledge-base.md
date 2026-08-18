# 知识库适配器（KB → inbox → content，导出委托 kb-export 外部能力）

本文件定义「个人知识库」如何成为官网内容来源。核心链路：
**知识库导出 Markdown（由 kb-export 能力完成）→ `.geo-cms/inbox/<kbId>/` → `sync_kb.py` 归一化合并 → `content/`**。

> **职责边界**：geo-cms 不生成内容。「导出」动作由 `config.capabilities.kb-export` 选定的来源完成
> （连接器技能或用户直接上传），geo-cms 只负责把导出物归一化合并进 `content/`。

---

## 适配器总览（导出执行方 = kb-export 能力）

| type | 导出执行方 | 说明 |
|------|------------|------|
| `tencent-docs` | 调 tencent-docs 连接器技能导出 `.md` | 本机已连接，优先走连接器 |
| `feishu` | 调飞书技能导出知识库节点/多维表格为 Markdown | 本机已连接 |
| `ima` | 调 IMA 技能导出知识库 | 需已连接 |
| `markdown` | 直接读取本地目录（或已 git 同步的文档库） | 无凭据依赖，最稳 |

**通用原则**：本技能不直接调用各 KB 的私有 API，而是复用 `kb-export` 选定的连接器技能完成「导出」，
保证鉴权由连接器托管。导出产物统一为 Markdown 落到 `inbox`。

---

## 导出约定（inbox 结构）

每个 KB 导出到独立子目录，文件用稳定 slug 命名，便于去重与增量：

```
.geo-cms/inbox/
├── kb1/                      ← tencent-docs 来源
│   ├── what-is-geo.md
│   └── geo-checklist.md
└── kb2/                      ← 飞书来源
    └── product-faq.md
```

导出时尽量保留原文标题、正文与原有层级；图片以相对路径引用或留占位（验收阶段补 alt）。

---

## 归一化（由 sync_kb.py 执行）

`sync_kb.py` 读取 `config.knowledgeBases` 列出的所有 `inbox`，对每个 `.md`：

1. **解析/补 frontmatter**：至少包含
   `title`、`date`（导出日或原文日期）、`slug`（文件 basename）、`source`（KB id）、`tags`。
2. **GEO 字段注入**（见 `assets/content-template.md`）：
   - `summary`：一句话可引用摘要（结论前置）
   - `faq`：可选，结构化问答对（用于 FAQPage Schema）
   - `geoVerified`: false（合并后由优化步骤置 true）
3. **去重**：按 `slug` 跨 KB 去重，后到的 KB 版本覆盖先到的（可在日志提示冲突）。
4. **写入 `content/`**：保持原相对路径或按 `slug` 平铺；输出「新增/更新」清单与冲突告警。

---

## 直接上传文章

用户「直接上传文章」等价于：把文章作为 `markdown` 类型的一次性 KB 放入
`.geo-cms/inbox/_upload/`，再跑 `sync_kb.py`。无需登记进 `config.knowledgeBases`。

---

## 增量更新识别

`sync_kb.py` 对比 `content/` 已有文件与 inbox 新文件的 `slug` + mtime/内容哈希：
- 内容无变化 → 跳过（不重复写入）
- 内容变化 → 标记 `updated`
- 新 slug → 标记 `added`

输出 JSON 清单供阶段二步骤 3 汇报与后续优化针对性处理。

---

## 常见失败与处理

| 现象 | 处理 |
|------|------|
| 连接器未连接 | 提示用户先连接对应连接器；或改用 `markdown` 本地目录 |
| 导出为空 | 确认 KB 选择/授权范围；空更新则跳过合并 |
| frontmatter 缺失 | `sync_kb.py` 用文件名/首行 H1 兜底生成 |
| 图片引用断裂 | 记录到验收清单，部署阶段补 alt/转存 |
