# 默认推荐与渐进引导（降低使用门槛）

本技能保持「桥接」定位不变，但首次使用者往往不知道该装什么、选什么、补什么。
本文件提供**默认推荐清单**与**逐阶段引导规范**：推荐项全部是外部能力，geo-cms 只负责推荐、
编排与记录，不代做内容生成、不代定规则。推荐项用户可全部替换，默认值只是起点。

---

## 一、默认推荐清单（阶段零直接给出）

### 1. 前端模板来源（建新站时）
- 推荐浏览：https://htmlrev.com/free-astro-templates.html （免费 Astro 模板合集）
- 选定后把模板信息写入 `config.site.template`（source/name/url/selectedAt），此后受「四、模板保护规则」约束。
- 已有站点跳过本项。

### 2. 推荐技能（SkillHub 社区，用 find-skills 或 skillhub 安装）

| 用途 | 推荐技能 | 地址 | geo-cms 中的角色 |
|------|---------|------|-----------------|
| 前端设计 / 模板调整 | frontend-design-v2 | https://skillhub.cn/skills/user_e07fe912/frontend-design-v2 | 仅当用户强制要求改模板时，引导用户授权该技能执行 |
| GEO 规则权威 | geo-cn | https://skillhub.cn/skills/user_e059269a/geo-cn | `geo-optimize` 能力首选（步骤 5 委托对象） |
| 内容生成（去 AI 味） | unclecheng-reduce-ai-perception-v2 | https://skillhub.cn/skills/user_ab5ae6ee/unclecheng-reduce-ai-perception-v2 | 生成正文的外部技能，按用户的文章提示词执行；geo-cms 只搬运提示词与产出落库 |

> geo-cms 不内置这些技能：环境里没有就引导安装；用户不装则走各自允许的降级路径
> （geo-optimize 可 WebSearch 降级；内容生成没有就不生成，等用户提供）。

### 3. 知识库推荐（按已连接 MCP 判定）
判定顺序：
1. 已连接 **ima** MCP → 推荐 **ima**（文章沉淀在 ima，`kb-export` 委托 ima 导出）。
2. 本地有 **Obsidian**（或用户偏好本地写作）→ 推荐 **Obsidian vault**（vault 即 `content/` 或作 inbox，详见 best-practices.md）。
3. 都没有 → 退回 `markdown` inbox（用户手动放 `.md`）。

**目录结构约束（无论选哪个都必须遵守，否则 sync_kb.py 无法稳定去重/清理）：**
- 一个知识库一个固定根目录（ima 指定文集、Obsidian 指定 `site/` 子目录），无关笔记不要混入；
- 一篇文章一个 `.md` 文件，文件名即建议 slug（小写中划线）；
- frontmatter 至少含 `title` 与 `date`；
- 图片等资产放文章同级 `assets/` 子目录，用相对路径 `![](assets/xx.png)` 引用；
- 不使用 `[[wikilinks]]` 等非标准语法（Obsidian 需关闭，见 best-practices.md）。

---

## 二、构建日志（每次构建必记）

- 路径：`.geo-cms/build-log.md`（append-only，随仓库提交）。
- 时机：每次「阶段二」结束、步骤 9 回库**之前**必须追加一条；条目模板见 `assets/build-log-template.md`。
- 运行开始时：先读最后一条日志，带上次遗留事项进入本次更新。
- 用途：内容更新同步的依据（下次接着上次进度做）、历史回溯、渐进引导的「下一步建议」来源。
- 最少字段：时间、触发来源、同步范围（added/updated/pruned）、GEO 门禁结果、构建、部署 URL、
  验收结果、模板是否未动、所用外部能力、遗留事项与下一步建议。

---

## 三、提示词收集（引导用户输出，不是 agent 代写）

路径：`.geo-cms/prompts/`（随仓库提交，团队共享口径）。

| 文件 | 内容 | 何时引导填写 |
|------|------|------------|
| `build-prompt.md` | 站点构建偏好：风格关键词、目标受众、页面清单、禁改项 | 阶段一 Setup 时 |
| `article-prompt.md` | 新文章生成提示词：选题方向、结构、口吻、关键词、去 AI 味要求 | 阶段一首次 + 用户想调整时 |

- 这两个文件是**用户的生产资料**：geo-cms 只收集、存储，并在对应环节**转交外部技能**
  （article-prompt 交给内容生成技能；build-prompt 交给前端设计/建站流程），本身不执行生成。
- 引导话术：
  「接下来存两份提示词，以后每次都按它来：① 站点怎么建（风格/受众/页面），
  ② 文章怎么写（结构/口吻/关键词）。你用一段话描述就行，我帮你落成文件；
  之后随时说『改构建提示词』或『改文章提示词』即可更新。」

---

## 四、模板保护规则（硬约束）

> 注意：模板保护管「结构/设计能不能改」，文本落库回环（见「六」）管「文案从哪来」。两者独立，同时生效。

模板一经选定并写入 `config.site.template`：

- ✅ **允许**（内容丰富，不需额外确认）：
  - 按模板既有槽位填充/替换文案、图片；
  - 新增文章页（走 content/ + sync_kb.py）；
  - 调整 SEO meta、正文内容、FAQ 文案。
- ❌ **不允许**（除非用户明确强制要求）：
  - 删除页面、组件、板块；
  - 改布局结构、配色体系、字体体系等设计决策；
  - 重写模板代码。
- 用户强制要改时：引导调用前端设计技能（社区推荐 frontend-design-v2）执行；
  geo-cms 在本次构建日志记录「模板变更：用户要求，改动点…」，并提示可 git revert 回滚。
- 每次构建日志必须标注「模板未动 / 模板变更」，让保护状态可审计。

---

## 五、渐进引导（让用户知道该补什么）

| 时机 | 引导动作 |
|------|---------|
| 阶段零 | 给出「一、默认推荐清单」，逐项确认：模板来源（新站）/ geo-cn / 内容生成技能 / 知识库选型 + 目录约束 |
| 阶段一 | ① 选定模板并写 `config.site.template`；② 引导输出两份提示词（prompts/）；③ 确认知识库目录结构 |
| 阶段二（每次结束） | 汇报后附 **1~3 条下一步建议**，依据：构建日志遗留事项 + geo-report 未清项 + prompts 缺失项。例：「FAQ 页还没有 Schema 标记，建议下次补」「article-prompt 还没填，写文章前我会再问你要」 |
| 用户不知道干嘛 | 按「填提示词 → 补文章 → 跑同步 → 验收上线」提示最短下一步 |

> 原则：**每次只引导 1~3 件事**，不一次倾倒全部要求。

---

## 六、文本落库回环（硬约束，优先级最高）

> 完整规则见 `references/content-roundtrip.md`。

**任何要上站的文本，禁止直接生成写进模板/页面，必须先转存知识库、再读回来使用。**

```bash
# 起草 → 落库（唯一合法入口）
python scripts/content_gate.py --config .geo-cms/config.json --stage <draft> --kb <kbId> --slug <slug>
# 归一化入 content/
python scripts/sync_kb.py --config .geo-cms/config.json
# 回读门禁（strict：不通过即不得构建）
python scripts/content_gate.py --config .geo-cms/config.json
```

- 覆盖：正文、FAQ、summary、hero/CTA/关于文案、meta、og、`llms.txt`、Schema 文本、图片 alt。
- 例外：纯代码/样式/构建配置、`config.json`、路由与部署参数、单字 UI 标签。
- 散落在模板里的文案必须登记 `.geo-cms/text-assets.json`，`from` 指向源文章 slug。
- 用户嫌麻烦时的话术：「落库只多一条命令，换来的是这句话以后能改、能删、能查出处；
  不落库的话，下次想改它，得先猜它当初写在哪。」

引导时机：阶段一 Setup（说明规则 + 建 `text-assets.json` 空文件）、每次用户要求「直接写一段文案上站」时。

