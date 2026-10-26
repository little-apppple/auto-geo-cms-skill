---
name: geo-cms
slug: geo-cms
agent_created: true
description: |
  GEO 友好的 CMS 管理「桥接」技能 —— 只做内容源与部署之间的编排与搬运，不做内容生成、也不设定 GEO/SEO 规则。
  将「代码仓库（源码）」与「个人知识库（文章）」合并后，委托环境中已安装的外部技能（GEO 优化 / 浏览器验收）
  或在线检索完成优化与验收，再部署上线并把代码提交回库。首次使用会检测环境依赖并与用户沟通补齐（可用 find-skills 查找），
  并提供默认推荐清单（Astro 模板来源、geo-cn 规则技能、内容生成技能、ima/Obsidian 知识库）、模板保护、提示词收集、构建日志与渐进引导，降低使用门槛。
  **硬约束：所有文本必须走知识库落库回环（inbox → sync_kb → content_gate 回读校验）后才能上站，禁止模型直出文本，防止数据游离无法管理。**
  触发词：geo cms、静态官网内容管理、知识库同步官网、官网部署、SSG 内容更新、文章同步到官网、官网上线验收
version: 1.3.0
display_name: "GEO 友好 CMS 桥接"
displayName: "GEO 友好 CMS 桥接"
metadata:
  version: 1.3.0
  author: geo-cms
  description_zh: "内容↔部署桥接：代码仓库 + 知识库合并 → 委托外部 GEO 技能/在线检索优化 → 委托部署与浏览器验收 → 回库；内容生成与 GEO 规则设定均为外部能力；所有文本强制走知识库落库回环（content_gate.py 门禁阻断游离内容）；内置默认推荐清单、模板保护、提示词收集、构建日志与渐进引导降低使用门槛"
  changelog:
    "1.3.0": "新增硬约束「文本落库回环」：任何上站文本必须落库 inbox → sync_kb 归一化 → 回读校验 → 才允许使用，禁止模型直出文本进模板/页面；新增 scripts/content_gate.py（DRIFT/DIVERGED/BAD_SOURCE/PHANTOM/COPY_NO_SRC 五类检查，strict 阻断构建）与 .geo-cms/text-assets.json 文案资产登记；新增 references/content-roundtrip.md；阶段二新增步骤 4「回环门禁」；sync_kb 隐式扫描 `_upload` inbox"
    "1.2.1": "loop review 修复：setup.md 补默认推荐清单(§0.0)/模板选定(§3.5)/提示词收集(§3.6)/构建日志初始化，完成判定扩至 9 项；config-sample 补 site.template；README 新增降门槛章节并补全目录树；构建日志统一为末尾追加(修复读取顺序矛盾)；gitignore 注释更正保留清单"
    "1.2.0": "降低使用门槛：新增 references/defaults.md 默认推荐清单（Astro 模板来源 htmlrev、geo-cn 规则技能、内容生成技能、ima/Obsidian 知识库+目录约束）；模板保护规则（选定后非用户强制不得删改，只按模板丰富内容）；提示词收集（.geo-cms/prompts/ 构建提示词+文章提示词）；构建日志（.geo-cms/build-log.md 每次必记）；渐进引导（每步告知该补什么）"
    "1.1.4": "修复 sync_kb.py 路径根（config 在 .geo-cms 时正确解析 content/inbox）；新增持久 .geo-cms/content-index.json（跨运行增量 diff + prune 作用域）与默认孤儿清理（--no-prune 可关）；步骤 8 验收页清单从 sync-manifest 派生；best-practices 补 G4/G5（Astro Content Collections + llms.txt/sitemap 生成）"
    "1.1.3": "新增 references/best-practices.md：推荐体系（Astro+Obsidian/Markdown+git+EdgeOne）、三条约束映射、图文/富媒体内容适配与 Obsidian 接入要点"
    "1.1.2": "README 新增「为什么小团队更适合 geo-cms（TCO 视角）」定位章节：首配后边际成本趋零、可插拔带来实时性/生成/自动化三翻转"
    "1.1.1": "补充 references/first-run-faq.md：首次运行交互话术（阶段零脚本）+ 常规 FAQ（10 条），对齐桥接定位"
    "1.1.0": "收紧职责边界：本技能仅做桥接与编排，内容生成与 GEO 规则设定委托外部技能/在线检索；新增首次环境依赖检测与搭建（find-skills）"
    "1.0.0": "初始版本 —— 含 git 验证、知识库合并、GEO 优化、部署、浏览器验收、回库"
allowed-tools: Read, Grep, Glob, Bash, WebFetch, WebSearch, Write, Edit, Agent, Skill
---

# geo-cms — GEO 友好的 CMS 桥接技能

把「代码仓库里的官网源码」与「个人知识库里的文章」当作两个内容源，合并后经 **外部 GEO 能力**
优化再部署上线，并对全站做验收，最后把结果提交回代码库。

**本技能是「桥」，不是「生产者」**：它负责把内容从知识库搬到官网、把官网送上部署平台、把结果
回库；而**内容怎么写、GEO 规则怎么定**，一律交给环境里已装的外部技能或在线检索。

---

## 职责边界（硬约束，必须前置判断）

### 本技能「做」什么（桥接 + 编排）
- ✅ 编排整条流水线（收集内容 → 合并 → 委托优化 → 委托部署 → 委托验收 → 回库）。
- ✅ 验证 git **读取/写入权限**并把更新**提交回代码库**（`scripts/verify_git.py`）。
- ✅ 把多个内容源（知识库 / 文档库 / 用户直接上传）**归一化合并**进仓库 `content/` 目录（`scripts/sync_kb.py`）。
- ✅ 检测环境依赖、与用户沟通补齐外部能力（见阶段零）。
- ✅ **强制文本落库回环**：所有上站文本先落库 inbox、经 `sync_kb.py` 归一化、再由 `content_gate.py`
  回读校验通过后才允许使用（详见下方「硬约束一」）。

### 本技能「不做」什么（交给外部）
- ❌ **不生成内容**：文章正文由用户提供或来自知识库，本技能只搬运、合并、落库，不创作正文。
- ❌ **不允许文本游离**：任何上站文本（含页面文案/meta/llms/alt）必须经知识库落库回环
  （inbox → sync_kb → content_gate 回读校验）后才可使用，禁止模型直出写进模板或页面（见「硬约束一」）。
- ❌ **不设定 GEO/SEO 规则**：robots/llms/Schema/FAQ 等规范的「权威性」来自外部 GEO 技能或在线检索；
  本技能最多**缓存归档**这些外部产出，绝不自己拍板规则口径。
- ❌ **不实现浏览器自动化 / 部署平台 API**：这些由对应的连接器或技能提供，本技能只负责编排调用。
- ❌ **不擅改模板**：前端模板一经用户选定（记录在 `config.site.template`），非用户强制要求
  不得删改页面/组件/布局/设计，只允许按模板既有结构填充与丰富内容（详见 `references/defaults.md` 模板保护规则）。

> 一句话：**能力（content / GEO rules / browser / deploy）全在外部；geo-cms 只做连接与编排。**

---

### 硬约束一：文本落库回环（KB Round-trip，最高优先级）

> 详细规则、命令与反例见 `references/content-roundtrip.md`。

**任何要上站的文本，不得直接生成并写入站点，必须先转存进知识库、再从知识库读回来使用。**
目的是杜绝「数据游离」：文本只存在于会话上下文或模板里，导致无法管理、无法审计、无法复用。

强制链路（缺一步即禁止构建/部署）：

```
① 起草（用户 / agent / 外部生成技能均可）
   ✗ 禁止直接写 content/ 或 模板/页面/meta
        ▼
② 落库 inbox   .geo-cms/inbox/<kbId>/<slug>.md
   content_gate.py --stage   带 title/date/slug/source/provenance
        ▼
③ 归一化入库   sync_kb.py  →  content/<slug>.md + content-index.json
        ▼
④ 回读门禁     content_gate.py   哈希一致 + 来源可追溯，否则退出码 1 阻断
        ▼
⑤ 才允许使用（构建 / GEO 优化 / 模板填充 / meta / llms.txt / FAQ / alt）
   文本来源必须是第 ③ 步落盘的文件，不得取自语义记忆
```

**适用范围**：文章正文、标题、FAQ、summary、页面文案（hero/卖点/CTA/关于）、meta title/description、
og 文案、`llms.txt` 说明、Schema 文本、图片 alt、模板占位替换内容。

**例外**（不需要回环，但仍需可追溯）：纯代码/样式/构建配置、`config.json`、路由与部署参数、
结构性常量（导航标题直接取自文章 `title` 字段视为已回环）、单字 UI 标签。

**内容源与文案资产的区分**：
- 落在 `site.contentDir` 里的文章 → 必须由 `sync_kb.py` 生成，且登记在 `content-index.json`。
- 散落在模板/页面里的文案 → 登记到 `.geo-cms/text-assets.json`，`from` 指向源文章 slug，
  否则门禁报 `COPY_NO_SRC`。

**判定口诀**：删掉当前会话上下文，这段文本还能从磁盘上找到出处吗？找不到即违规。

**禁止的规避手段**：把 `config.contentGate.mode` 长期改为 `warn` 以绕过门禁；直接把生成结果
`Write` 进 `content/`；改完 `content/` 却不回改 inbox 源文件。三者均视为违反本约束。

### 站点形态边界（不变）
仅支持 SSG（静态站点生成器）构建、产物为**纯静态文件**的官网：
- ✅ Next.js `output: export`、Astro `static`、Hugo、VitePress、Jekyll、11ty 等纯静态输出
- ✅ 产物可被任意静态托管（EdgeOne Pages / Nginx / OSS / GitHub Pages）直接 serve
- ❌ SSR 无静态导出、依赖数据库/接口实时渲染的动态 CMS、纯客户端 SPA 无预渲染 —— 遇到则停止并说明。

---

## 外部依赖契约（能力清单）

本技能运行需要以下 4 类**外部能力**。首次使用（阶段零）会逐项检测是否就绪：

| 能力 ID | 用途 | 首选外部来源（技能/连接器） | 缺失时的降级 |
|---------|------|----------------------------|--------------|
| `kb-export` | 把知识库/文档库导出为 Markdown | tencent-docs / feishu / ima 连接器技能 | 用户直接把 `.md` 放到 `.geo-cms/inbox/` |
| `geo-optimize` | 全站 GEO/SEO 优化与规则权威 | `geo-zh`（或同类 GEO 技能） | WebSearch 取规范 + `scripts/fetch_geo_specs.py` 缓存（bridge 不设定规则） |
| `deploy` | 把构建产物上线 | edgeone-pages 连接器 / 自有服务器 rsync | 无 —— 必须由用户提供部署目标 |
| `browser-verify` | 上线后浏览器自动化验收 | `agent-browser` / `playwright` 技能 | `scripts/verify_deploy.py` 最小本地降级 |

> bridge 自身**只保有两个工具脚本**：`verify_git.py`（git 权限/回库）与 `sync_kb.py`（内容合并落库）。
> 其余三类能力一律**优先委托外部**，仅在外部缺失且无法安装时，才用附带的最小脚本降级（降级不等于规则权威）。

---

## 整体架构

```
┌──────────────┐      ┌────────────────────┐
│ 代码仓库 git  │      │  个人知识库（文章）  │
│ (官网源码/SSG)│      │ tencent-docs/飞书/IMA│
└──────┬───────┘      └──────────┬─────────┘
       │  clone/pull             │ 导出(kb-export 外部能力)
       ▼                         ▼
┌──────────────────────────────────────────┐
│  本地工作区  .geo-cms/inbox/<kb>/  → content/ │  ← sync_kb.py（bridge 自身）
│  合并：KB 文章归一化后写入仓库 content 目录     │
└───────────────────────┬──────────────────────┘
                        │
            ┌───────────▼────────────┐
            │ 回环门禁 content_gate.py │  ← 游离内容即阻断（bridge 自身）
            │ 来源可追溯 + 哈希一致     │
            └───────────┬────────────┘
            ┌───────────▼────────────┐
            │ 委托 geo-optimize 外部能力│  ← 规则权威在外部 GEO 技能/在线检索
            │ 做全站 GEO/SEO 优化       │     bridge 仅缓存其产出到 specs/
            └───────────┬────────────┘
                        │
              ┌─────────▼─────────┐
              │ SSG 构建 → 纯静态   │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │ 委托 deploy 外部能力 │  ← edgeone-pages / 自有服务器
              └─────────┬─────────┘
                        │
        ┌───────────────▼────────────────┐
        │ 委托 browser-verify 外部能力验收 │  ← agent-browser / playwright
        └───────────────┬────────────────┘
                        │
              ┌─────────▼─────────┐
              │ git commit + push  │  ← verify_git.py（bridge 自身）
              └───────────────────┘
```

**规范一致性机制**（沿用，但权威在外部）：运行时把外部 GEO 能力或在线检索得到的规范**缓存**到
本地 `.geo-cms/specs/`，下次复用以保证口径一致；若本地已有缓存，则**并行**启动「用缓存委托优化」
与「实时检索刷新规范」，优化完成后再把增量新规范**补充**进本地缓存。

---

## 配置约定

运行态配置与产物放在仓库根 `.geo-cms/`（`inbox/` 建议忽略，`config.json` 与 `specs/` 应随仓库提交）。

`config.json`（`capabilities` 字段为 1.1.0 新增，记录阶段零检测到的外部依赖映射）：

```json
{
  "site": {
    "name": "示例官网",
    "ssg": "next-static | hugo | vitepress | astro | jekyll | other",
    "contentDir": "content",
    "buildCmd": "npm run build",
    "outputDir": "out",
    "staticExport": true,
    "template": {
      "source": "htmlrev",
      "name": "所选模板名",
      "url": "https://模板地址",
      "selectedAt": "2026-10-21"
    }
  },
  "git": {
    "repo": "git@github.com:org/site.git",
    "localPath": ".",
    "branch": "main"
  },
  "knowledgeBases": [
    {"id": "kb1", "type": "tencent-docs | feishu | ima | markdown",
     "name": "产品知识库", "inbox": ".geo-cms/inbox/kb1", "format": "md"}
  ],
  "deployment": {
    "type": "edgeone-pages | custom-server | other",
    "project": "", "distDir": "out", "ssh": "", "remoteDir": ""
  },
  "capabilities": {
    "kb-export":     {"resolved": "tencent-docs", "mode": "skill"},
    "geo-optimize":  {"resolved": "geo-zh",       "mode": "skill"},
    "deploy":        {"resolved": "edgeone-pages","mode": "connector"},
    "browser-verify":{"resolved": "agent-browser","mode": "skill"}
  },
  "specs": {"dir": ".geo-cms/specs", "lastUpdated": null},
  "contentGate": {
    "mode": "strict",
    "textAssets": ".geo-cms/text-assets.json"
  }
}
```

`contentGate.mode`：`strict`（默认，门禁不通过即阻断构建/部署）/ `warn`（仅告警，需在构建日志说明原因）。

---

## 触发场景

- 「把知识库里的文章同步到官网」
- 「更新官网内容（知识库/文档库/直接上传）后部署」
- 「官网做 GEO 优化并上线 + 验收」
- 「每次部署前都做全站 GEO/SEO 优化」

未配置 → 先进入**阶段零（环境检测）**，再**阶段一（Setup）**；已配置好则直接进入**阶段二（更新循环）**。

---

## 阶段零：环境检测与依赖搭建（首次必做）

> 详细步骤见 `references/setup.md` §环境检测。

0. **给出默认推荐清单（降门槛）**：对照 `references/defaults.md` 向用户展示推荐组合 ——
   前端模板来源（htmlrev 免费 Astro 模板）、GEO 规则技能（geo-cn）、内容生成技能
   （unclecheng-reduce-ai-perception-v2 等）、知识库选型（已连 ima MCP → 推荐 ima；
   本地 Obsidian → 推荐 vault；否则 markdown inbox）及其**目录结构约束**。
   用户可全部采纳或替换，确认结果进入第 1 步能力检测。
1. **枚举可用能力**：列出当前环境的技能与连接器（用 `Skill` 工具可枚举；或读取连接器连接状态）。
2. **逐项判定**：对照「外部依赖契约」四能力，标记为 `available` / `missing`。
3. **补齐 `missing` 项**：
   - 调用 `Skill` 工具 `command="find-skills"` 查找可安装的技能（如 GEO 优化、浏览器自动化）；
   - 或与用户确认是否连接对应连接器（edgeone-pages / 飞书 / 腾讯文档 / ima）；
   - 或明确告知用户「该项将走在线检索降级」并取得同意（仅 `geo-optimize` 允许此降级）。
4. **写入并确认**：把依赖映射写进 `config.capabilities`，向用户**展示映射并确认**后，才进入阶段一。

> 若用户拒绝补齐关键能力（如 `deploy` 无任何来源），则**停止**并告知无法继续。

---

## 阶段一：初始化与配置（一次性）

> 详细步骤与判定逻辑见 `references/setup.md`；默认推荐与引导话术见 `references/defaults.md`。

1. **收集代码 git 库**：请用户提供仓库地址（HTTPS 或 SSH）。
2. **验证本地访问权限**（循环直到连通）：运行 `scripts/verify_git.py --repo <url> --path <local>`
   - 读取权限：能 `clone`/`fetch`；写入权限：能 `push`（`--dry-run` 探测）。
   - 失败 → 打印可操作原因（缺 SSH key / 无写权限 / 仓库不存在），**停止并请用户修复后重试**，
     直到返回 `READ_OK + WRITE_OK` 才继续。
3. **选定前端模板（新站必做）**：引导用户从推荐来源（htmlrev 免费 Astro 模板等）选定模板，
   写入 `config.site.template`（source/name/url/selectedAt）。**此后受模板保护规则约束**：
   非用户强制要求不得删改，只能按模板规范丰富内容。
4. **收集知识库指定**：让用户选择**一个或多个**知识库（按 defaults.md 推荐顺序：ima / Obsidian /
   tencent-docs / 飞书 / 本地 Markdown），**确认目录结构约束**（一库一根目录、一文一文件、
   frontmatter 必含 title/date、图片同级 assets/、禁 wikilinks），记录到 `config.knowledgeBases`，
   并通过 `capabilities.kb-export` 选定的来源导出。
5. **收集提示词（引导用户输出，agent 不代写）**：按 `references/defaults.md` §三话术，
   引导用户提供并落盘 `.geo-cms/prompts/build-prompt.md`（站点怎么建：风格/受众/页面清单/禁改项）
   与 `.geo-cms/prompts/article-prompt.md`（文章怎么写：选题/结构/口吻/关键词/去 AI 味要求）。
   用户暂不提供可跳过，后续构建前再次引导。
6. **收集部署信息**：让用户提供部署目标 —— 托管平台（如 EdgeOne Pages）或自有服务器（SSH + 远程目录 / rsync），
   记录到 `config.deployment`，并通过 `capabilities.deploy` 选定的来源上线。
7. **初始化构建日志**：创建 `.geo-cms/build-log.md`（模板见 `assets/build-log-template.md`）。
8. **写 `config.json`**：落盘含 `capabilities`、`site.template` 的完整结构，
   并 `git add .geo-cms/config.json && git commit -m "chore: geo-cms config"`。

---

## 阶段二：内容更新循环（每次更新）

> 完整步骤、脚本参数与验收清单见 `references/geo-spec-management.md`、`geo-optimization.md`、
> `browser-verification.md`、`deployment.md`。

### 0. 读取上次构建日志 + 规范预检（决定并行策略）
- 读 `.geo-cms/build-log.md` 最后一条：带上次遗留事项与下一步建议进入本次更新。
- 规范预检（依赖 geo-optimize 能力）：
```
本地 .geo-cms/specs/ 是否已有「外部 GEO 能力/检索」产出的规范缓存？
├─ 存在 ──→ 并行执行：
│            A) 用缓存委托 geo-optimize 能力优化（步骤 4-5）
│            B) 实时检索刷新规范（WebSearch）+ scripts/fetch_geo_specs.py --merge 缓存增量
└─ 不存在 ──→ 先通过 geo-optimize 能力（或 WebSearch）建立基线并缓存，再执行 A)
```

### 1. 收集更新来源
确认本次更新来自：知识库更新 / 文档库 / 用户直接上传文章（单篇或多篇）。

### 2. 导出知识库内容 → inbox
对每个 `config.knowledgeBases`，用 `capabilities.kb-export` 选定的来源（连接器技能 / 用户上传）
把文章导出为 Markdown 到 `.geo-cms/inbox/<kb>/`。详见 `references/knowledge-base.md`。

**若本次有 agent 起草的文本**（外部技能产出的文章、页面文案、FAQ、meta 等）：**禁止直接写进 `content/`
或模板**，一律先落库 ——
`python scripts/content_gate.py --config .geo-cms/config.json --stage <草稿> --kb <kbId> --slug <slug>`。

### 3. 合并到仓库 content 目录（bridge 自身）
运行 `scripts/sync_kb.py --config .geo-cms/config.json`
- 归一化 frontmatter（title/date/slug/tags），按 slug 去重；写入 `site.contentDir`，输出「新增/更新/跳过/清理」清单到 `.geo-cms/sync-manifest.json`。
- **持久内容索引**：同步写 `.geo-cms/content-index.json`（slug → {title, source, hash, lastSync, origin}），跨运行保留，支撑桥接层真增量 diff 与删除作用域。
- **孤儿清理（prune，默认开启）**：知识库中已删除/移除的文章，其 `content/<slug>.md` 会被自动删除；仅作用于 `origin=kb` 的索引项，手写 `origin=manual` 文件永不被误删。需保留可用 `--no-prune` 关闭。
- 步骤 8 验收页面清单直接取本步 `sync-manifest.json` 的 added/updated（首页必含）。
- `inbox/_upload/`（用户直传 / 一次性草稿）在存在时被隐式纳入扫描，无需登记进 `knowledgeBases`。

### 3.5 文本回环门禁（同步后，硬约束一）
运行 `scripts/content_gate.py --config .geo-cms/config.json`
- `DRIFT`（content 有文件但未登记）/ `DIVERGED`（哈希不一致，绕过 KB 改了正文）/
  `BAD_SOURCE`（来源 KB 未声明）/ `PHANTOM`（索引有、文件无）/ `COPY_NO_SRC`（文案无源文章）任一命中 → **退出码 1，停止**。
- 修正方式：改动搬到 inbox 源文件后重跑步骤 3；历史文件用 `--adopt` 纳入 KB；文案补齐 `from`。
- 允许 `warn` 的唯一情形：用户明确知情并同意，且本次构建日志记录原因与期限。


### 4. 拉取最新源码
`git pull --rebase`（避免与远程分叉）。

### 5. 全站 GEO/SEO 优化（委托 geo-optimize 外部能力）
- **首选**：调用环境中已安装的 GEO 技能（如 `geo-zh`）对合并后**源码**做优化（robots.txt 开放 AI 爬虫、
  llms.txt、JSON-LD、FAQ 结论前置、NAP 可见、图片 alt、Meta 可引用等）。**规则口径由该技能/在线检索决定。**
- **降级**：若未安装 GEO 技能，用 `WebSearch` 获取最新规范、由本技能按规范缓存应用（bridge 仅搬运，不创作规则）；
  可用 `scripts/geo_check.py` 做**通用**静态缺口扫描作为辅助（规则仍以外部 GEO 能力为准）。
- **优化产出的文本同样受硬约束一管辖**：llms.txt 说明、meta description、FAQ、hero 文案、图片 alt
  若要新增或改写，必须先落库（`--stage` 到 inbox 或登记 `text-assets.json` 的 `from`），不得由模型直出写进文件。

### 5.5 文本回环门禁（构建前，二次校验）
再跑一次 `scripts/content_gate.py --config .geo-cms/config.json`
- 覆盖步骤 5 期间新增的文案与文件改动（模板填充、llms.txt、meta、alt）。
- 未通过 → 回到步骤 5 补齐落库/登记，禁止进入构建。

### 6. 构建 + 门禁 + 部署（委托 deploy 外部能力）
- 运行 `site.buildCmd` 产出纯静态文件。
- **GEO 门禁（构建后必做）**：`scripts/geo_check.py --root . --out <outputDir> --report .geo-cms/geo-report.json`
  扫描**构建产物**；P0 未清零 → 回到步骤 5 修复源码后重新构建，不得部署。
- 校验 `outputDir` 确为纯静态（无服务端依赖）。
- 按 `config.deployment` 委托 `capabilities.deploy` 选定的来源上线（EdgeOne Pages 技能 / 自有服务器 rsync）。

### 7. 增量规范补充（缓存外部产出，bridge 不设定规则）
优化完成后，运行 `scripts/fetch_geo_specs.py --append` 把本次实时检索/外部 GEO 能力发现、尚未写入本地的
新规范并入 `.geo-cms/specs/`（去重 + 标注来源）。更新 `config.specs.lastUpdated`。

### 8. 浏览器自动化验收（委托 browser-verify 外部能力）
- **验收范围**：从 `.geo-cms/sync-manifest.json` 取本次 `added`+`updated` 页面路径（首页 `/` 必含）；避免手填遗漏。
- **首选**：用 `agent-browser` / `playwright` 技能打开线上首页与本次新增/更新页面，核对正文可见、
  FAQ/结论前置、Schema 块存在、robots/llms 可访问、无 404、GEO 元素到位。
- **降级**：若未安装浏览器技能，用 `scripts/verify_deploy.py --pages <added,updated,/>` 做最小本地核对。
- 验收不通过 → 回到步骤 5/6 修复后重新部署验收。

### 9. 提交更新代码回库（bridge 自身）
- **追加构建日志（必做）**：按 `assets/build-log-template.md` 向 `.geo-cms/build-log.md` 写入本次条目
  （触发来源、同步 added/updated/pruned、**回环门禁结果**、GEO 门禁结果、构建、部署 URL、验收结果、
  **模板未动/模板变更**、所用外部能力、遗留事项与下一步建议）。
- **渐进引导（每次结束附 1~3 条下一步建议）**：依据构建日志遗留事项 + geo-report 未清项 +
  prompts 缺失项（如 article-prompt 未填则提醒）。让用户始终知道该补什么、该添加什么。
- `git add -A && git commit -m "content: 同步知识库 + GEO 优化" && git push`
- 推送成功后向用户汇报：本次更新篇数、优化项、验收结果、上线 URL、所用外部能力清单、下一步建议。

---

## 引用资源

| 类型 | 文件 | 用途 | 加载时机 |
|------|------|------|----------|
| references | `references/setup.md` | 环境检测 + 初始化、git 验证、配置写入 | 阶段零/一 |
| references | `references/first-run-faq.md` | 首次运行交互话术 + 常规 FAQ | 阶段零 |
| references | `references/defaults.md` | **默认推荐清单**（模板/技能/知识库+目录约束）、模板保护规则、提示词收集、渐进引导 | 阶段零/一、步骤 9 |
| references | `references/best-practices.md` | 推荐体系（SSG/KB/托管选型）、图文内容适配、Obsidian 接入要点 | 选型/阶段零 |
| references | `references/knowledge-base.md` | 知识库导出（委托 kb-export 能力） | 步骤 2 |
| references | `references/content-roundtrip.md` | **文本落库回环**硬约束：链路、适用范围、五类违规、命令与反例 | 步骤 2/3.5/5.5 |
| references | `references/geo-spec-management.md` | 规范缓存（外部产出）+ 并行策略 | 步骤 0/7 |
| references | `references/geo-optimization.md` | 如何委托 geo-optimize 能力 / 降级 | 步骤 5 |
| references | `references/deployment.md` | 如何委托 deploy 能力 | 步骤 6 |
| references | `references/browser-verification.md` | 如何委托 browser-verify 能力 / 降级 | 步骤 8 |
| scripts | `scripts/verify_git.py` | **bridge 自身**：git 读取/写入权限探测 | 阶段一/九 |
| scripts | `scripts/sync_kb.py` | **bridge 自身**：KB 导出归一化合并到 content；写 `.geo-cms/content-index.json` 持久索引 + 默认 prune 孤儿；隐式扫描 `_upload` | 步骤 3 |
| scripts | `scripts/content_gate.py` | **bridge 自身**：文本回环门禁（DRIFT/DIVERGED/BAD_SOURCE/PHANTOM/COPY_NO_SRC）+ `--stage` 落库 + `--adopt` 纳管 | 步骤 2/3.5/5.5 |
| scripts | `scripts/fetch_geo_specs.py` | 降级辅助：缓存外部 GEO 规范（不设定规则） | 步骤 0/7 |
| scripts | `scripts/geo_check.py` | 降级辅助：通用静态 GEO 缺口扫描 | 步骤 5/6 |
| scripts | `scripts/verify_deploy.py` | 降级辅助：最小本地浏览器核对 | 步骤 8 |
| assets | `assets/content-template.md` | 文章落库模板（含 frontmatter） | 步骤 3 |
| assets | `assets/spec-template.md` | 技术规范缓存文档模板 | 步骤 0/7 |
| assets | `assets/build-log-template.md` | 构建日志条目模板（每次构建必记） | 阶段一/步骤 9 |

---

## 错误恢复

| 场景 | 处理 |
|------|------|
| git 读取失败 | 检查 URL/凭据；SSH 提示加 key；HTTPS 提示 token |
| git 写入失败 | `verify_git.py` 探测后提示申请写权限，不擅自强推 `--force` |
| 知识库导出为空 | 提示用户确认 KB 选择/授权；空更新则跳过合并 |
| 缺少 geo-optimize 能力 | 阶段零应已处理；若运行时缺失，走 WebSearch 降级并明确告知用户「规则未由专业 GEO 技能把关」 |
| 缺少 deploy 能力 | **停止**——部署是必要外部能力，无法降级 |
| 构建非纯静态 | 退回步骤 5 修正 SSG 配置；拒绝带服务端依赖的产物上线 |
| 部署失败 | 保留上一版线上（平台回滚 / 不覆盖远程目录），修复后重部署 |
| 浏览器验收不通过 | 回到步骤 5/6 修复，重新部署并复验 |
| 用户要求删改模板但非强制场景 | 按模板保护规则拒绝并解释；用户坚持 → 引导前端设计技能执行，日志记录变更点 |
| 回环门禁 `DRIFT` | 文本未落库。`--adopt` 纳入 KB 或删除该文件，再跑 `sync_kb.py` |
| 回环门禁 `DIVERGED` | 绕过 KB 改了正文。把改动搬回 inbox 源文件，重跑 `sync_kb.py` |
| 回环门禁 `COPY_NO_SRC` | 页面/meta 文案无来源。补 `text-assets.json` 的 `from`，或先把源文章落库 |
| 回环门禁 `PHANTOM` | 删除绕过同步脚本。重跑 `sync_kb.py` 让其 prune 并清理索引 |
| 用户要求跳过回环直接生成 | 拒绝，说明会形成无法管理的游离数据；如需快速产出，可落库到 `inbox/_upload/` 再同步（同样一句话的代价） |
| WebSearch 不可用 | 退回纯本地规范缓存继续，标注「未做实时增量」 |

## 质量保障

- 每次部署**必须**经过步骤 5（委托优化）与步骤 8（委托验收），二者缺一无视「完成」。
- **文本回环门禁（步骤 3.5 + 5.5）不通过不得构建、不得部署**；`mode=warn` 属例外，须记入构建日志。
- 所有上游文本的可追溯性以 `.geo-cms/content-index.json` 与 `content-gate.json` 为唯一凭据，不以会话记忆为准。
- 规范缓存 `specs/` 与 `config.json` 随仓库提交，保证团队优化口径一致（口径来自外部 GEO 能力）。
- 所有 GEO 结论避免绝对承诺；**规则权威永远在外部 GEO 技能/在线检索，不在本技能**。
- 不虚构 URL/数据；外部检索所得须标注来源写入 `specs/`。
- 本技能不生成正文内容，仅搬运/合并用户提供或知识库导出的内容；上游即便由外部能力生成，也必须落库后再用。
- 文本落库回环：所有上站文本可追溯到 `content-index.json`（文章）或 `text-assets.json` 的 `from`（文案），
  无源头即视为数据游离，门禁阻断。
- 模板保护：选定模板后非用户强制不得删改，每次构建日志必须标注「模板未动/模板变更」，可审计。
- 构建日志 append-only：`.geo-cms/build-log.md` 每次构建必追加，不修改历史记录；`prompts/` 是用户生产资料，只收集转交不代写。
