# 最佳实践（推荐体系与落地选型）

本文件沉淀 geo-cms 经过验证的「推荐体系」：满足三条硬约束（**代码增量构建 / 知识库层级+时间戳 / 代码托管零额外成本**），
并覆盖**图文（富媒体）内容**的适配方式。阶段零选型、阶段一初始化时优先参考本文件。

> 职责边界不变：geo-cms 仍是「桥」，内容生成与 GEO 规则仍委托外部能力。本文档只解决「用什么搭这套桥最低成本、最顺」。

---

## 1. 推荐体系总览

| 层 | 推荐选型 | 满足的约束 | 成本 |
|----|---------|-----------|------|
| 代码托管 | **GitHub（私有库免费）** | 无额外成本开销 | 0 |
| 静态托管/部署 | **EdgeOne Pages / Makers（已连接）** | 无额外成本开销 + 版本回滚 | 0 |
| SSG 构建 | **Astro 5（Content Layer）** | 增量构建 | 0（开源） |
| 知识库 | **Obsidian vault（本地 Markdown）** 或 **纯 Markdown + git** | 层级结构 + 时间戳 | 0 |

整套只用「已连接/已免费」的能力，无新增付费服务。

---

## 2. 三条硬约束的满足方式

### 2.1 代码支持增量构建 → Astro Content Layer
- Astro 5 的 **Content Layer** 会缓存内容源，仅重新处理发生变化的条目；新增一篇文章不会触发全站重建。
- 轻量备选：**Eleventy（`--incremental`）**，只重建改动模板。
- 不推荐：
  - **Next.js**：ISR 虽增量，但需 Node 运行时，偏重，违背「纯静态」轻量定位。
  - **Hugo**：构建极快但是全量，非真增量。
  - **VitePress**：构建快但每次全量。

### 2.2 知识库支持层级 + 时间戳
- **层级**：目录树（基础）+ 标签/嵌套标签（`#父/子`）+ 双链（Obsidian）。
- **时间戳**来源（任选其一，推荐 git）：
  - **git 提交历史**（`git log`）——最干净，白送 diff / blame；
  - Obsidian 社区插件 **Frontmatter Modified Date** 自动写 `updated` 字段；
  - 文件系统 mtime（最弱，不推荐做权威时间戳）。

### 2.3 代码托管无额外成本
- 代码与内容放 **GitHub 私有库**（免费），部署走已连接的 **EdgeOne Pages**（免费静态托管 + 自带版本回滚）。
- 阶段零的 `deploy` / `kb-export` 两个契约均可用已连接能力满足，无需新接付费服务。

---

## 3. 知识库选型路线

| 路线 | 说明 | 层级 | 时间戳 | 成本 | 编辑体验 | 适合 |
|------|------|------|--------|------|---------|------|
| A 纯 Markdown + git | vault 即仓库目录 | 目录 | git log | 0 | 裸编辑器 | 开发者 solo |
| **A+ Obsidian** | Obsidian 打开 `content/` 为 vault | 目录+标签+双链 | frontmatter / git | 0 | **图形化 KB，非技术也能用** | 个人/小团队（推荐） |
| B 飞书 Wiki | 在线知识库导出 | 节点树 | 版本历史 | 0（已有飞书） | 网页协作 | 多人实时协作 |

> 路线 A+ 是 A 的「带 UI 升级版」：底层仍是 Markdown，geo-cms `markdown` 适配器零改造消费，无需任何导出 API。

---

## 4. Obsidian 接入要点

### 方式 1（推荐）：vault 直接等于 `content/`
把 Obsidian 仓库根指向项目 `content/` 目录，Obsidian 就地编辑。geo-cms 配置：
```json
"knowledgeBases": [{"type": "markdown", "inbox": "content"}]
```
改完 → `git commit`（时间戳）→ `sync_kb.py` 归一化 → Astro 增量构建，一条龙零转换。

### 方式 2：vault 作为 `inbox` 源
Obsidian 在别处，geo-cms 用 `markdown` 适配器把 `.md` 搬进 `content/`。多一层同步但 vault 与站点解耦。

### ⚠ 唯一一个坑（务必处理）
Obsidian 的 **`[[wikilinks]]`、`![[embed]]`、`> [!note]` callouts 不是标准 Markdown**，Astro 渲染会挂。
- **最简**：Obsidian 设置 → Files & Links → 关掉「Use [[Wikilinks]]」，全程用标准 `[文字](文件.md)`。
- 或装 `remark-wikilinks` / `obsidian-export` 类转换插件，让 SSG 自动转。

---

## 5. 图文 / 富媒体内容适配

**结论：适配 ✅，且 Astro 让图文比纯 Markdown 更利好 GEO。**

- **用标准图片语法**：`![alt](./assets/fig.png)`，避免 Obsidian `![[embed]]`（非标准，需转换）。
- **Astro 原生优化**：`astro:assets` 在构建期自动做响应式图、懒加载、格式转换；**并要求 `alt`**——这恰好是 GEO 的关键因子。
- **geo-cms 门禁兜底**：`scripts/geo_check.py` 扫描构建产物的 `<img>` 缺 `alt`，P0 未清零卡构建不上线。
- **资源随仓库走**：图片放 `content/assets/`（或 Obsidian attachments 目录）一并 `git` 提交，构建后由 EdgeOne CDN 分发。
- **增量构建不受影响**：Content Layer 仅重处理变化的 MD；新增图片在构建期被优化，无全量重算。
- **层级/时间戳不受影响**：图文笔记同样是带 frontmatter 的 `.md`，slug 去重、时间戳逻辑照常工作。

> 注意：图片体积过大时，建议本地预压缩或依赖 `astro:assets` 自动优化，避免单一大图拖慢首屏（影响 GEO 的可读性与停留）。

---

## 6. 推荐 config.json 样板（Obsidian + Astro + EdgeOne）

```json
{
  "site": {
    "name": "示例官网",
    "ssg": "astro",
    "contentDir": "content",
    "buildCmd": "npm run build",
    "outputDir": "dist",
    "staticExport": true
  },
  "git": {
    "repo": "git@github.com:org/site.git",
    "localPath": ".",
    "branch": "main"
  },
  "knowledgeBases": [
    {"id": "kb1", "type": "markdown", "name": "Obsidian 内容库",
     "inbox": "content", "format": "md"}
  ],
  "deployment": {
    "type": "edgeone-pages", "project": "my-site", "distDir": "dist"
  },
  "capabilities": {
    "kb-export":     {"resolved": "markdown", "mode": "local"},
    "geo-optimize":  {"resolved": "geo-zh",   "mode": "skill"},
    "deploy":        {"resolved": "edgeone-pages", "mode": "connector"},
    "browser-verify":{"resolved": "agent-browser", "mode": "skill"}
  },
  "specs": {"dir": ".geo-cms/specs", "lastUpdated": null}
}
```

> Astro 默认产物目录是 `dist`（非 Next.js 的 `out`），`outputDir` / `distDir` 需对应。

---

## 7. 落地检查清单

- [ ] SSG 选 **Astro**（增量构建）
- [ ] 知识库选 **Obsidian / 纯 Markdown**（层级 + 时间戳）
- [ ] 关闭 Obsidian **wikilinks**（或加转换插件）
- [ ] 仓库托管 **GitHub 私有库**（免费）
- [ ] 部署走 **EdgeOne Pages**（已连接，免费 + 回滚）
- [ ] 图文用标准 `![](path)` 语法 + **必填 alt**
- [ ] `config.json` 按第 6 节样板填好并 `git commit`
- [ ] Astro 启用 **Content Collections**（增量构建前提）
- [ ] 加 `src/pages/llms.txt.ts` 路由从 collection 生成 llms.txt（GEO 索引，P0）
- [ ] 装 **@astrojs/sitemap**（自动 sitemap.xml）
- [ ] `sync_kb.py` 默认开启 **prune**（孤儿清理；`--no-prune` 可关）

---

## 8. SSG 增量与 GEO 索引生成（补齐 G4/G5）

- **增量构建由 SSG 提供**：Astro 必须启用 Content Collections（`src/content/config.ts` 定义 schema），Content Layer 才会缓存并仅重处理变化条目。geo-cms 只负责把 `content/` 保持同步，不配置/校验 SSG 增量模式。
- **llms.txt（GEO 机器可读目录）**：Astro 不自带，需加动态路由 `src/pages/llms.txt.ts`，遍历 content collection 输出「站点摘要 + 各页面标题/路径」纯文本——这正是给 AI 爬虫的索引，也满足 `geo_check.py` 的 P0 要求。
- **sitemap.xml**：装 `@astrojs/sitemap` 集成，构建自动生成并在 `robots.txt` 引用（GEO-TECH-01）。
- 二者均从同一 content collection 派生，**不要手写页面索引**；手写会与源脱节。注意区分：`.geo-cms/content-index.json` 是**桥接层控制索引**（slug→来源/哈希/同步时间，用于增量 diff 与 prune 作用域），不是站点导航索引，二者职责不同。
