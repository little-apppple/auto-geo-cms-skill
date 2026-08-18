# auto-geo-cms-skill — GEO 友好的 CMS 桥接技能

面向 **SSG 构建、纯静态部署官网** 的内容↔部署桥接技能：把「代码仓库里的官网源码」与
「个人知识库里的文章列表」合并，委托**外部 GEO 能力**优化、委托**部署/浏览器验收能力**上线，
最后把更新代码提交回代码库。

> **职责边界（硬）**：geo-cms 只做桥接与编排——不生成内容正文，也不设定 GEO/SEO 规则。
> 内容生成、GEO 规则权威、浏览器自动化、部署平台 API 全部来自当前环境已装的**外部技能/连接器**
> 或在线检索。首次使用会先检测这些依赖并与用户沟通补齐（可用 `find-skills` 查找）。

## 能力边界

**做（桥接 + 编排）**
- 编排整条流水线；验证 git 读写与回库（`verify_git.py`）；把多内容源合并进 `content/`（`sync_kb.py`）；
  检测环境依赖并与用户沟通补齐。

**不做（交给外部）**
- ❌ 不生成内容正文（由用户提供或知识库导出，只搬运合并）
- ❌ 不设定 GEO/SEO 规则（权威在外部 GEO 技能 / WebSearch，本技能仅缓存）
- ❌ 不实现浏览器自动化 / 部署平台 API（由对应技能/连接器提供）

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

## 核心机制：规范缓存一致性 + 时效（规则仍在外部）

- 把外部 GEO 能力 / 在线检索得到的规范**缓存**到本地 `.geo-cms/specs/`，下次复用保一致。
- 若本地已有缓存，**并行**启动「用缓存委托优化」与「实时检索刷新规范」；
  优化完成后，把增量新规范**补充**进本地缓存（bridge 不设定规则口径）。

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
# 2-3) 知识库导出到 inbox（kb-export 外部能力）后，归一化合并到 content/
python scripts/sync_kb.py --config .geo-cms/config.json

# 4) 拉取最新源码
git pull --rebase

# 5) 委托 geo-optimize 外部能力做全站 GEO 优化；可辅以 geo_check 通用扫描
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
│   ├── knowledge-base.md         # 知识库导出（委托 kb-export 能力）
│   ├── geo-spec-management.md    # 规范缓存（外部产出）+ 并行策略
│   ├── geo-optimization.md       # 委托 geo-optimize 能力 / 降级参考
│   ├── deployment.md             # 委托 deploy 能力
│   └── browser-verification.md   # 委托 browser-verify 能力 / 降级
├── scripts/                      # 可执行脚本（bridge 自身仅 verify_git/sync_kb）
│   ├── verify_git.py             # [bridge] git 读写权限探测循环
│   ├── sync_kb.py                # [bridge] KB 导出归一化合并到 content
│   ├── fetch_geo_specs.py        # [降级] 缓存外部 GEO 规范（不设定规则）
│   ├── geo_check.py              # [降级] 通用静态 GEO 缺口扫描
│   └── verify_deploy.py          # [降级] 最小本地浏览器核对
└── assets/                       # 模板
    ├── content-template.md       # 文章落库模板（含 frontmatter）
    ├── spec-template.md          # 技术规范缓存文档模板
    ├── config-sample.json        # config.json 样例（含 capabilities）
    └── geo-cms-gitignore.txt     # 目标仓库 .gitignore 模板
```

## 连接器依赖（本机已连接可直用）

- **EdgeOne Pages**：部署托管平台（`deployment.type=edgeone-pages`）
- **腾讯文档 / 飞书 / ima**：知识库导出（走对应连接器技能）
- **浏览器技能（agent-browser / playwright-cli）**：上线后验收

无对应连接器时，改用 `markdown` 类型本地目录作为知识库来源，仍可完整运行。
