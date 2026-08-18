---
name: geo-cms
slug: geo-cms
agent_created: true
description: |
  GEO 友好的 CMS 管理技能 —— 面向 SSG 构建、纯静态部署的官网。
  将「代码仓库（源码）」与「个人知识库（文章列表）」合并，经 GEO/SEO 技术修正后再部署上线，
  并对全站内容做 GEO/SEO 优化与上线后浏览器自动化验收，最后把更新后的代码提交回代码库。
  触发词：geo cms、静态官网内容管理、知识库同步官网、官网 GEO 优化部署、SSG 内容更新、
  文章同步到官网、官网上线验收、GEO 技术规范本地化、内容合并部署
version: 1.0.0
display_name: "GEO 友好 CMS 管理"
displayName: "GEO 友好 CMS 管理"
metadata:
  version: 1.0.0
  author: geo-cms
  description_zh: "面向 SSG 纯静态官网的 CMS 管理：代码仓库 + 个人知识库合并 → GEO 修正 → 部署 → 浏览器验收 → 回库；含 GEO/SEO 技术规范本地化与实时增量补充"
  changelog:
    "1.0.0": "初始版本 — 初始化验证 git、知识库适配器、GEO 规范实时搜索与本地增量、全站优化、部署、浏览器验收、回库提交"
allowed-tools: Read, Grep, Glob, Bash, WebFetch, WebSearch, Write, Edit, Agent
---

# geo-cms — GEO 友好的 CMS 管理技能

把「代码仓库里的官网源码」与「个人知识库里的文章列表」当作两个内容源，合并后经 GEO/SEO
技术修正再部署上线，并对全站做优化与上线后浏览器验收，最后把结果提交回代码库。

---

## 能力边界（必须前置判断）

**仅支持**：SSG（静态站点生成器）构建、产物为**纯静态文件**的官网。
- ✅ Next.js `output: export`、Astro `static`、Hugo、VitePress、Jekyll、11ty 等纯静态输出
- ✅ 产物可被任意静态托管（EdgeOne Pages / Nginx / OSS / GitHub Pages）直接 serve

**明确拒绝**（遇到则停止并说明原因，不要硬做）：
- ❌ 服务端渲染（SSR）且无静态导出能力、需常驻后端才能访问
- ❌ 依赖数据库/接口实时查询才能渲染正文的传统动态 CMS（WordPress/PHP 动态页等）
- ❌ 纯客户端 SPA 且无预渲染（无 SSR/SSG，搜索引擎与 AI 爬虫看不到正文）

> 若用户站点当前不是纯静态，先给出「改造为 SSG 静态导出」的建议，再决定是否继续。

---

## 整体架构

```
┌──────────────┐      ┌────────────────────┐
│ 代码仓库 git  │      │  个人知识库（文章）  │
│ (官网源码/SSG)│      │ tencent-docs/飞书/IMA│
└──────┬───────┘      └──────────┬─────────┘
       │  clone/pull             │ 导出 Markdown
       ▼                         ▼
┌──────────────────────────────────────────┐
│  本地工作区  .geo-cms/inbox/<kb>/  → content/ │
│  合并：KB 文章归一化后写入仓库 content 目录     │
└───────────────────────┬──────────────────────┘
                        │
            ┌───────────▼────────────┐
            │ GEO/SEO 技术修正源码     │  ← 依据本地规范 + 实时规范
            │ (robots/llms/Schema/FAQ)│
            └───────────┬────────────┘
                        │
              ┌─────────▼─────────┐
              │ SSG 构建 → 纯静态   │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │ 部署（平台/自有服务器）│
              └─────────┬─────────┘
                        │
        ┌───────────────▼────────────────┐
        │ 浏览器自动化验收（线上内容核对）  │
        └───────────────┬────────────────┘
                        │
              ┌─────────▼─────────┐
              │ git commit + push  │  ← 更新代码回库
              └───────────────────┘
```

**技术规范一致性机制**（本技能核心）：
- 运行时实时搜索最新 GEO/SEO 技术规范，并**写入本地** `.geo-cms/specs/`。
- 若本地已存在规范文档，则**并行**启动「用本地规范做全站优化」与「实时搜索最新规范」；
  优化完成后，再把本次增量发现的新规范**补充**进本地文档，保证下次一致、且时效不丢。

---

## 配置约定

所有运行态配置与产物存放在仓库根目录的 `.geo-cms/`（建议加入 `.gitignore` 仅忽略 `inbox/`，
`config.json` 与 `specs/` 应随仓库提交以保证团队一致）。

`config.json` 结构（首次 Setup 时由本技能写入）：

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
  "specs": {"dir": ".geo-cms/specs", "lastUpdated": null}
}
```

---

## 触发场景

- 「把知识库里的文章同步到官网」
- 「更新官网内容（知识库/文档库/直接上传）后部署」
- 「官网做 GEO 优化并上线 + 验收」
- 「每次部署前都做全站 GEO/SEO 优化」

未提供上述输入时，先进入**阶段一（Setup）**；已配置好则直接进入**阶段二（更新循环）**。

---

## 阶段一：初始化与配置（一次性）

> 详细步骤与判定逻辑见 `references/setup.md`。

1. **收集代码 git 库**：请用户提供仓库地址（HTTPS 或 SSH）。
2. **验证本地访问权限**（循环直到连通）：运行 `scripts/verify_git.py --repo <url> --path <local>`
   - 读取权限：能 `clone`/`fetch`。
   - 写入权限：能 `push`（用 `--dry-run` 探测，或推送探针分支后删除）。
   - 任一步失败 → 打印可操作原因（缺 SSH key / 无写权限 / 仓库不存在），**停止并请用户修复后重试**，
     直到 `verify_git.py` 返回 `READ_OK + WRITE_OK` 才继续。
3. **收集知识库指定**：让用户选择**一个或多个**知识库作为内容来源（tencent-docs / 飞书 / IMA /
   本地 Markdown 目录），记录到 `config.knowledgeBases`。详见 `references/knowledge-base.md`。
4. **收集部署信息**：让用户提供部署目标——托管平台（如 EdgeOne Pages，本机已连接）或自有服务器
   （SSH + 远程目录 / rsync）。记录到 `config.deployment`。详见 `references/deployment.md`。
5. **写 `config.json`**：用上列结构落盘，并 `git add .geo-cms/config.json && git commit -m "chore: geo-cms config"`。

---

## 阶段二：内容更新循环（每次更新）

> 完整步骤、脚本参数与验收清单见 `references/geo-spec-management.md`、`geo-optimization.md`、
> `browser-verification.md`、`deployment.md`。

### 0. 技术规范预检（决定并行策略）

```
本地 .geo-cms/specs/ 是否存在？
├─ 存在 ──→ 并行执行：
│            A) 用本地规范对全站做 GEO 优化（步骤 4-5）
│            B) 实时搜索最新规范：WebSearch + scripts/fetch_geo_specs.py --merge
│           （优化完成后，把 B 的增量新规范 append 进 specs/，见步骤 7）
└─ 不存在 ──→ 先执行 B) 建立基线规范库，再执行 A) 优化
```

### 1. 收集更新来源
确认本次更新来自：知识库更新 / 文档库 / 用户直接上传文章（单篇或多篇）。

### 2. 导出知识库内容 → inbox
对每个 `config.knowledgeBases`，用对应适配器把文章导出为 Markdown 到 `.geo-cms/inbox/<kb>/`。
（连接器已连接时优先走 tencent-docs / 飞书技能；详见 `references/knowledge-base.md`。）

### 3. 合并到仓库 content 目录
运行 `scripts/sync_kb.py --config .geo-cms/config.json`
- 归一化 frontmatter（title/date/slug/tags + GEO 字段），按 slug 去重。
- 写入 `site.contentDir`，输出「新增/更新」清单。

### 4. 拉取最新源码
`git pull --rebase`（避免与远程分叉）。

### 5. 全站 GEO/SEO 优化（部署前必做）
按 `references/geo-optimization.md` 清单对合并后的**源码**做修正：
robots.txt 开放 AI 爬虫、llms.txt、JSON-LD（Organization/Article/FAQPage）、FAQ 结论前置、
NAP 全页可见、图片 alt、Meta 可引用等。（源码级预扫描可用 `scripts/geo_check.py --root .`，
但最终门禁在构建后执行，见步骤 6。）

### 6. 构建 + 门禁 + 部署
- 运行 `site.buildCmd` 产出纯静态文件。
- **GEO 门禁（构建后必做）**：运行
  `scripts/geo_check.py --root . --out <outputDir> --report .geo-cms/geo-report.json`
  扫描**构建产物**；P0 未清零 → 回到步骤 5 修复源码后重新构建，不得部署。
- 校验 `outputDir` 确为纯静态（无服务端依赖，见 geo-optimization.md「静态产物校验」）。
- 按 `config.deployment` 部署（EdgeOne Pages 技能 / 自有服务器 rsync）。

### 7. 增量规范补充（关键时效机制）
优化完成后，运行 `scripts/fetch_geo_specs.py --append` 把本次实时搜索发现、但尚未写入本地的
新规范并入 `.geo-cms/specs/`（去重 + 标注来源）。更新 `config.specs.lastUpdated`。

### 8. 浏览器自动化验收（上线后）
按 `references/browser-verification.md` + `scripts/verify_deploy.py`：
- 打开线上首页与本次新增/更新页面。
- 核对：正文可见、FAQ/结论前置、Schema 块存在、robots/llms 可访问、无 404、GEO 元素到位。
- 验收不通过 → 回到步骤 5/6 修复后重新部署验收。

### 9. 提交更新代码回库
`git add -A && git commit -m "content: 同步知识库 + GEO 优化" && git push`
推送成功后向用户汇报：本次更新篇数、优化项、验收结果、上线 URL。

---

## 引用资源

| 类型 | 文件 | 用途 | 加载时机 |
|------|------|------|----------|
| references | `references/setup.md` | 初始化、git 验证、配置写入 | 阶段一 |
| references | `references/knowledge-base.md` | 知识库适配器（导出→inbox） | 步骤 2 |
| references | `references/geo-spec-management.md` | 规范实时搜索 + 本地增量 + 并行策略 | 步骤 0/7 |
| references | `references/geo-optimization.md` | 全站 GEO/SEO 优化清单 | 步骤 5 |
| references | `references/deployment.md` | 部署适配器（EdgeOne/自有服务器） | 步骤 6 |
| references | `references/browser-verification.md` | 上线后浏览器验收流程 | 步骤 8 |
| scripts | `scripts/verify_git.py` | git 读取/写入权限探测循环 | 阶段一 |
| scripts | `scripts/sync_kb.py` | KB 导出归一化合并到 content | 步骤 3 |
| scripts | `scripts/fetch_geo_specs.py` | 实时规范合并/增量补充 | 步骤 0/7 |
| scripts | `scripts/geo_check.py` | 静态 GEO/SEO 缺口扫描 | 步骤 5 |
| scripts | `scripts/verify_deploy.py` | 浏览器验收驱动 | 步骤 8 |
| assets | `assets/content-template.md` | 文章落库模板（含 GEO frontmatter） | 步骤 3 |
| assets | `assets/spec-template.md` | 技术规范文档模板 | 步骤 0/7 |

---

## 错误恢复

| 场景 | 处理 |
|------|------|
| git 读取失败 | 检查 URL/凭据；SSH 提示加 key；HTTPS 提示 token |
| git 写入失败 | `verify_git.py` 探测后提示申请写权限，不擅自强推 `--force` |
| 知识库导出为空 | 提示用户确认 KB 选择/授权；空更新则跳过合并 |
| 构建非纯静态 | 退回步骤 5 修正 SSG 配置；拒绝带服务端依赖的产物上线 |
| 部署失败 | 保留上一版线上（平台回滚 / 不覆盖远程目录），修复后重部署 |
| 浏览器验收不通过 | 回到步骤 5/6 修复，重新部署并复验 |
| WebSearch 不可用 | 退回纯本地规范库继续优化，标注「未做实时增量」 |

## 质量保障

- 每次部署**必须**经过步骤 5 全站优化与步骤 8 浏览器验收，二者缺一无视「完成」。
- 规范库 `specs/` 与 `config.json` 随仓库提交，保证团队优化口径一致。
- 所有 GEO 结论避免绝对承诺（用「提升被引用可能性」而非「保证被引用」）。
- 不虚构 URL/数据；实时搜索所得须标注来源写入 `specs/`。
