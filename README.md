# auto-geo-cms-skill — GEO 友好的 CMS 桥接技能

面向 **SSG 构建、纯静态部署官网** 的内容↔部署桥接技能：把「代码仓库里的官网源码」与
「个人知识库里的文章列表」合并，委托**外部 GEO 能力**优化、委托**部署/浏览器验收能力**上线，
最后把更新代码提交回代码库。

> **职责边界（硬）**：geo-cms 只做桥接与编排——不生成内容正文，也不设定 GEO/SEO 规则。
> 内容生成、GEO 规则权威、浏览器自动化、部署平台 API 全部来自当前环境已装的**外部技能/连接器**
> 或在线检索。首次使用会先检测这些依赖并与用户沟通补齐（可用 `find-skills` 查找）。
>
> **文本落库回环（硬约束，v1.3.0）**：任何要上站的文本不得直接生成写进模板/页面，必须先落库
> 知识库（inbox）→ `sync_kb.py` 归一化 → `content_gate.py` 回读校验，通过后才允许使用。
> 目的是让所有文本可追溯、可修改、可删除，杜绝「数据游离」。

## 能力边界

**做（桥接 + 编排）**
- 编排整条流水线；验证 git 读写与回库（`verify_git.py`）；把多内容源合并进 `content/`（`sync_kb.py`）；
  强制文本落库回环（`content_gate.py`）；检测环境依赖并与用户沟通补齐。

**不做（交给外部）**
- ❌ 不生成内容正文（由用户提供或知识库导出，只搬运合并）
- ❌ 不允许文本游离（页面文案/meta/llms/alt 必须可追溯到知识库文章）
- ❌ 不设定 GEO/SEO 规则（权威在外部 GEO 技能 / WebSearch，本技能仅缓存）
- ❌ 不实现浏览器自动化 / 部署平台 API（由对应技能/连接器提供）
- ❌ 不擅改模板（选定后非用户强制不得删改，只按模板丰富内容）

## 降低使用门槛（v1.2.0 新增）

桥接定位不变，但首次使用不再「从零摸索」，内置四套降门槛机制：

- **默认推荐清单**（`references/defaults.md`）：前端模板来源（htmlrev 免费 Astro 模板）、
  GEO 规则技能（geo-cn）、内容生成技能（unclecheng-reduce-ai-perception-v2）、
  前端设计技能（frontend-design-v2）、知识库选型（ima / Obsidian / markdown，含目录结构约束）。
  全部可替换，推荐不绑定。
- **模板保护**：模板一经选定，非用户强制要求不得删改页面/组件/布局/设计，
  只按模板既有结构丰富内容；每次构建日志标注「模板未动/模板变更」，可审计。
- **提示词收集**：`.geo-cms/prompts/` 两份生产资料——`build-prompt.md`（站点怎么建）+
  `article-prompt.md`（文章怎么写）；用户口述、技能代存，构建时转交外部技能执行。
- **构建日志**：`.geo-cms/build-log.md` append-only，每次构建必记（同步范围/门禁/部署 URL/
  验收/模板状态/遗留事项），下次更新接着上次进度走。
- **渐进引导**：阶段零给推荐清单、阶段一引导选模板+提示词+KB 目录、
  每次结束附 1~3 条下一步建议，让用户始终知道该补什么。

**站点形态**
- ✅ 支持：SSG 纯静态输出（Next.js export / Astro / Hugo / VitePress / Jekyll / 11ty …）
- ❌ 拒绝：SSR 无静态导出、依赖数据库的传统动态 CMS、无预渲染的纯 SPA

## 外部依赖契约（能力清单）

| 能力 | 首选外部来源 | 缺失降级 |
|------|--------------|----------|
| `kb-export`（知识库导出） | tencent-docs / 飞书 / ima 连接器技能 | 用户直接上传 `.md` |
| `geo-optimize`（GEO 优化与规则） | `geo-zh` 等 GEO 技能 | WebSearch 取规范 + 本地缓存（不设定规则） |
| `deploy`（部署上线） | edgeone-pages 连接器 / 自有服务器 | 无（必要外部能力，不可降级） |
| `browser-verify`（浏览器验收） | agent-browser / playwright 技能 | verify_deploy.py 最小本地降级 |

## 整体架构

```
代码仓库(git, 源码)  +  个人知识库(文章)
        │  clone/pull         │ 导出(kb-export 外部能力)
        ▼                     ▼
   本地工作区：inbox → content（sync_kb.py 合并归一化，bridge 自身）
        │
        ▼  委托 geo-optimize 外部能力做 GEO/SEO 优化（规则权威在外部）
   构建 → 纯静态产物
        │
        ▼  委托 deploy 外部能力部署（EdgeOne Pages / 自有服务器）
   委托 browser-verify 外部能力验收（线上内容核对）
        │
        ▼  git commit + push（verify_git.py，bridge 自身回库）
```

## 核心机制一：文本落库回环（v1.3.0 硬约束）

```
起草（用户 / agent / 外部生成技能）
   │  ✗ 禁止直接写 content/ 或模板
   ▼
inbox（.geo-cms/inbox/<kb>/<slug>.md）   ← content_gate.py --stage
   ▼
content/（sync_kb.py 归一化 + content-index.json 登记）
   ▼
content_gate.py 回读校验（哈希一致 + 来源可追溯）→ 不通过则阻断构建
   ▼
才允许使用：构建 / 模板填充 / meta / llms.txt / FAQ / alt
```

- **为什么**：直出文本只活在会话里，改不动、删不掉、查不到出处；落库后一切都是文件 + 索引，可 diff、可回滚、可审计。
- **覆盖范围**：正文、标题、FAQ、summary、hero/CTA/关于文案、meta、og、`llms.txt`、Schema 文本、图片 alt。
- **例外**：纯代码/样式/构建配置、`config.json`、路由与部署参数、单字 UI 标签。
- **五类拦截**：`DRIFT`（未登记）/ `DIVERGED`（绕过 KB 改正文）/ `BAD_SOURCE`（来源未声明）/
  `PHANTOM`（索引有文件无）/ `COPY_NO_SRC`（文案无源文章）。
- **文案资产**：模板里的文案登记 `.geo-cms/text-assets.json`，`from` 指向源文章 slug。
- 详见 `references/content-roundtrip.md`。

## 核心机制二：规范缓存一致性 + 时效（规则仍在外部）

- 把外部 GEO 能力 / 在线检索得到的规范**缓存**到本地 `.geo-cms/specs/`，下次复用保一致。
- 若本地已有缓存，**并行**启动「用缓存委托优化」与「实时检索刷新规范」；
  优化完成后，把增量新规范**补充**进本地缓存（bridge 不设定规则口径）。

## 为什么小团队更适合 geo-cms（TCO 视角）

geo-cms 的甜区不在「开箱即用」，而在**首配跑通之后边际成本趋零**。要区分两种成本：

| | 一次性配置成本 | 配置后每次使用（边际成本） |
|---|---|---|
| 传统 CMS | 低（装好即用） | **持续高**：服务器运维、插件更新/冲突、人工 SEO、后台发稿点击、备份管理 |
| geo-cms | 高（git / SSG / agent 环境 / 首配） | **极低**：一句话触发「导出→合并→构建→部署→验收→回库」全链路 |

可插拔 + 高度可扩展带来三个翻转：

- **实时性（操作时延趋零）**：不是发布时延变零（静态构建物理时间仍在），而是人不用点后台、不用等插件、不用排期——
  agent 一句话即时编排全链路。对「想到就发」的小团队，体感就是实时。
- **内容生成可插拔**：本技能不写正文，反而成了优势——生成能力随时换最好的 agent，不被 CMS 编辑器锁定；
  桥只管搬，生成交给专精 agent，组合自由。
- **自动化原生**：agent 原生调度（定时、事件触发、多步）天然强于 CMS 的 cron/插件，且免维护。

**本质**：一个 agent 会话 = 编辑 + SEO 专员 + DevOps + QA 四角合一，且无服务器、无插件膨胀、无后台培训。
传统 CMS 省下的是前期的「开箱」，geo-cms 省下的是**长期的人力和运维**——这正是小团队最扛不住的部分。

> 诚实边界：① 整套低成本的前提是 WorkBuddy + 已装 skill/连接器都在，环境塌了就瘫（传统 CMS 是独立服务）；
> ② 首配 + 排错仍有门槛，对完全非技术的个体户，「第一次配置」本身可能比学 WordPress 还难。
> geo-cms 的低成本，是**给能过首配门槛的人**的。

## 快速开始

### 阶段零：环境检测（首次必做）

枚举已装技能/连接器，对照「外部依赖契约」逐项判定 `available`/`missing`；
缺失项用 `Skill` 工具 `command="find-skills"` 查找安装，或连接对应连接器，或与用户沟通补齐，
把映射写入 `config.capabilities` 并确认。

### 阶段一：初始化（一次性）

```bash
# 1) 验证 git 读写权限（循环直到 READ_OK + WRITE_OK）
python scripts/verify_git.py --repo <git-url> --path . --branch main

# 2) 配置知识库 / 部署 + capabilities（写入 .geo-cms/config.json，参考 assets/config-sample.json）
# 3) 提交配置
git add .geo-cms/config.json && git commit -m "chore: init geo-cms config" && git push
```

### 阶段二：每次内容更新

```bash
# 2) 知识库导出到 inbox（kb-export 外部能力）；agent 起草的文本同样先落库
python scripts/content_gate.py --config .geo-cms/config.json --stage drafts/x.md --kb kb1 --slug x

# 3) 归一化合并到 content/ 并登记索引
python scripts/sync_kb.py --config .geo-cms/config.json

# 3.5) 文本回环门禁（strict：有游离内容即阻断）
python scripts/content_gate.py --config .geo-cms/config.json

# 4) 拉取最新源码
git pull --rebase

# 5) 委托 geo-optimize 外部能力做全站 GEO 优化；可辅以 geo_check 通用扫描

# 5.5) 构建前再跑一次回环门禁（覆盖优化阶段新增的文案）
python scripts/content_gate.py --config .geo-cms/config.json

python scripts/geo_check.py --root . --out out --report .geo-cms/geo-report.json

# 6) 构建 + 委托 deploy 外部能力部署（EdgeOne Pages 技能 / 自有服务器 rsync）

# 7) 增量规范补充（缓存外部产出，bridge 不设定规则）
python scripts/fetch_geo_specs.py --append

# 8) 委托 browser-verify 外部能力验收（或用 verify_deploy.py 降级）
python scripts/verify_deploy.py --base-url https://yoursite.com --pages /,/blog/x --report .geo-cms/verify-report.json

# 9) 提交更新代码回库
git add -A && git commit -m "content: 同步知识库 + GEO 优化" && git push
```

## 目录结构

```
geo-cms/
├── SKILL.md                      # 入口 + 编排工作流 + 职责边界
├── references/                   # 详细过程文档（按需加载）
│   ├── setup.md                  # 环境检测 + 初始化、git 验证、配置
│   ├── first-run-faq.md          # 首次运行话术 + FAQ
│   ├── defaults.md               # 默认推荐清单、模板保护、提示词收集、渐进引导
│   ├── best-practices.md         # 推荐体系（Astro/Obsidian/EdgeOne）、图文适配
│   ├── knowledge-base.md         # 知识库导出（委托 kb-export 能力）
│   ├── content-roundtrip.md      # 文本落库回环硬约束（链路/范围/五类违规/命令）
│   ├── geo-spec-management.md    # 规范缓存（外部产出）+ 并行策略
│   ├── geo-optimization.md       # 委托 geo-optimize 能力 / 降级参考
│   ├── deployment.md             # 委托 deploy 能力
│   └── browser-verification.md   # 委托 browser-verify 能力 / 降级
├── scripts/                      # 可执行脚本（bridge 自身：verify_git/sync_kb/content_gate）
│   ├── verify_git.py             # [bridge] git 读写权限探测循环
│   ├── sync_kb.py                # [bridge] KB 导出归一化合并到 content
│   ├── content_gate.py           # [bridge] 文本回环门禁 + --stage/--adopt
│   ├── fetch_geo_specs.py        # [降级] 缓存外部 GEO 规范（不设定规则）
│   ├── geo_check.py              # [降级] 通用静态 GEO 缺口扫描
│   └── verify_deploy.py          # [降级] 最小本地浏览器核对
└── assets/                       # 模板
    ├── content-template.md       # 文章落库模板（含 frontmatter）
    ├── spec-template.md          # 技术规范缓存文档模板
    ├── build-log-template.md     # 构建日志条目模板（每次构建必记）
    ├── config-sample.json        # config.json 样例（含 capabilities、site.template、contentGate）
    ├── text-assets-sample.json   # 文案资产登记表样例（from → 源文章 slug）
    └── geo-cms-gitignore.txt     # 目标仓库 .gitignore 模板
```

## 连接器依赖（本机已连接可直用）

- **EdgeOne Pages**：部署托管平台（`deployment.type=edgeone-pages`）
- **腾讯文档 / 飞书 / ima**：知识库导出（走对应连接器技能）
- **浏览器技能（agent-browser / playwright-cli）**：上线后验收

无对应连接器时，改用 `markdown` 类型本地目录作为知识库来源，仍可完整运行。
