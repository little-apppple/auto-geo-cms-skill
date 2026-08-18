---
name: geo-cms
slug: geo-cms
agent_created: true
description: |
  GEO 友好的 CMS 管理「桥接」技能 —— 只做内容源与部署之间的编排与搬运，不做内容生成、也不设定 GEO/SEO 规则。
  将「代码仓库（源码）」与「个人知识库（文章）」合并后，委托环境中已安装的外部技能（GEO 优化 / 浏览器验收）
  或在线检索完成优化与验收，再部署上线并把代码提交回库。首次使用会检测环境依赖并与用户沟通补齐（可用 find-skills 查找）。
  触发词：geo cms、静态官网内容管理、知识库同步官网、官网部署、SSG 内容更新、文章同步到官网、官网上线验收
version: 1.1.2
display_name: "GEO 友好 CMS 桥接"
displayName: "GEO 友好 CMS 桥接"
metadata:
  version: 1.1.2
  author: geo-cms
  description_zh: "内容↔部署桥接：代码仓库 + 知识库合并 → 委托外部 GEO 技能/在线检索优化 → 委托部署与浏览器验收 → 回库；内容生成与 GEO 规则设定均为外部能力"
  changelog:
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

### 本技能「不做」什么（交给外部）
- ❌ **不生成内容**：文章正文由用户提供或来自知识库，本技能只搬运、合并、落库，不创作正文。
- ❌ **不设定 GEO/SEO 规则**：robots/llms/Schema/FAQ 等规范的「权威性」来自外部 GEO 技能或在线检索；
  本技能最多**缓存归档**这些外部产出，绝不自己拍板规则口径。
- ❌ **不实现浏览器自动化 / 部署平台 API**：这些由对应的连接器或技能提供，本技能只负责编排调用。

> 一句话：**能力（content / GEO rules / browser / deploy）全在外部；geo-cms 只做连接与编排。**

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
    "staticExport": true
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
  "specs": {"dir": ".geo-cms/specs", "lastUpdated": null}
}
```

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

> 详细步骤与判定逻辑见 `references/setup.md`。

1. **收集代码 git 库**：请用户提供仓库地址（HTTPS 或 SSH）。
2. **验证本地访问权限**（循环直到连通）：运行 `scripts/verify_git.py --repo <url> --path <local>`
   - 读取权限：能 `clone`/`fetch`；写入权限：能 `push`（`--dry-run` 探测）。
   - 失败 → 打印可操作原因（缺 SSH key / 无写权限 / 仓库不存在），**停止并请用户修复后重试**，
     直到返回 `READ_OK + WRITE_OK` 才继续。
3. **收集知识库指定**：让用户选择**一个或多个**知识库（tencent-docs / 飞书 / IMA / 本地 Markdown），
   记录到 `config.knowledgeBases`，并通过 `capabilities.kb-export` 选定的来源导出。
4. **收集部署信息**：让用户提供部署目标 —— 托管平台（如 EdgeOne Pages）或自有服务器（SSH + 远程目录 / rsync），
   记录到 `config.deployment`，并通过 `capabilities.deploy` 选定的来源上线。
5. **写 `config.json`**：落盘含 `capabilities` 的完整结构，并 `git add .geo-cms/config.json && git commit -m "chore: geo-cms config"`。

---

## 阶段二：内容更新循环（每次更新）

> 完整步骤、脚本参数与验收清单见 `references/geo-spec-management.md`、`geo-optimization.md`、
> `browser-verification.md`、`deployment.md`。

### 0. 规范预检（决定并行策略，依赖 geo-optimize 能力）
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

### 3. 合并到仓库 content 目录（bridge 自身）
运行 `scripts/sync_kb.py --config .geo-cms/config.json`
- 归一化 frontmatter（title/date/slug/tags），按 slug 去重；写入 `site.contentDir`，输出「新增/更新」清单。

### 4. 拉取最新源码
`git pull --rebase`（避免与远程分叉）。

### 5. 全站 GEO/SEO 优化（委托 geo-optimize 外部能力）
- **首选**：调用环境中已安装的 GEO 技能（如 `geo-zh`）对合并后**源码**做优化（robots.txt 开放 AI 爬虫、
  llms.txt、JSON-LD、FAQ 结论前置、NAP 可见、图片 alt、Meta 可引用等）。**规则口径由该技能/在线检索决定。**
- **降级**：若未安装 GEO 技能，用 `WebSearch` 获取最新规范、由本技能按规范缓存应用（bridge 仅搬运，不创作规则）；
  可用 `scripts/geo_check.py` 做**通用**静态缺口扫描作为辅助（规则仍以外部 GEO 能力为准）。

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
- **首选**：用 `agent-browser` / `playwright` 技能打开线上首页与本次新增/更新页面，核对正文可见、
  FAQ/结论前置、Schema 块存在、robots/llms 可访问、无 404、GEO 元素到位。
- **降级**：若未安装浏览器技能，用 `scripts/verify_deploy.py` 做最小本地核对。
- 验收不通过 → 回到步骤 5/6 修复后重新部署验收。

### 9. 提交更新代码回库（bridge 自身）
`git add -A && git commit -m "content: 同步知识库 + GEO 优化" && git push`
推送成功后向用户汇报：本次更新篇数、优化项、验收结果、上线 URL、所用外部能力清单。

---

## 引用资源

| 类型 | 文件 | 用途 | 加载时机 |
|------|------|------|----------|
| references | `references/setup.md` | 环境检测 + 初始化、git 验证、配置写入 | 阶段零/一 |
| references | `references/first-run-faq.md` | 首次运行交互话术 + 常规 FAQ | 阶段零 |
| references | `references/knowledge-base.md` | 知识库导出（委托 kb-export 能力） | 步骤 2 |
| references | `references/geo-spec-management.md` | 规范缓存（外部产出）+ 并行策略 | 步骤 0/7 |
| references | `references/geo-optimization.md` | 如何委托 geo-optimize 能力 / 降级 | 步骤 5 |
| references | `references/deployment.md` | 如何委托 deploy 能力 | 步骤 6 |
| references | `references/browser-verification.md` | 如何委托 browser-verify 能力 / 降级 | 步骤 8 |
| scripts | `scripts/verify_git.py` | **bridge 自身**：git 读取/写入权限探测 | 阶段一/九 |
| scripts | `scripts/sync_kb.py` | **bridge 自身**：KB 导出归一化合并到 content | 步骤 3 |
| scripts | `scripts/fetch_geo_specs.py` | 降级辅助：缓存外部 GEO 规范（不设定规则） | 步骤 0/7 |
| scripts | `scripts/geo_check.py` | 降级辅助：通用静态 GEO 缺口扫描 | 步骤 5/6 |
| scripts | `scripts/verify_deploy.py` | 降级辅助：最小本地浏览器核对 | 步骤 8 |
| assets | `assets/content-template.md` | 文章落库模板（含 frontmatter） | 步骤 3 |
| assets | `assets/spec-template.md` | 技术规范缓存文档模板 | 步骤 0/7 |

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
| WebSearch 不可用 | 退回纯本地规范缓存继续，标注「未做实时增量」 |

## 质量保障

- 每次部署**必须**经过步骤 5（委托优化）与步骤 8（委托验收），二者缺一无视「完成」。
- 规范缓存 `specs/` 与 `config.json` 随仓库提交，保证团队优化口径一致（口径来自外部 GEO 能力）。
- 所有 GEO 结论避免绝对承诺；**规则权威永远在外部 GEO 技能/在线检索，不在本技能**。
- 不虚构 URL/数据；外部检索所得须标注来源写入 `specs/`。
- 本技能不生成正文内容，仅搬运/合并用户提供或知识库导出的内容。
