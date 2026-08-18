# auto-geo-cms-skill — GEO 友好的 CMS 管理技能

面向 **SSG 构建、纯静态部署官网** 的内容管理技能：把「代码仓库里的官网源码」与
「个人知识库里的文章列表」合并，经 GEO/SEO 技术修正后部署上线，并对全站做优化与
上线后浏览器自动化验收，最后把更新代码提交回代码库。

## 能力边界

- ✅ 支持：SSG 纯静态输出（Next.js export / Astro / Hugo / VitePress / Jekyll / 11ty …）
- ❌ 拒绝：SSR 无静态导出、依赖数据库的传统动态 CMS、无预渲染的纯 SPA

## 整体架构

```
代码仓库(git, 源码)  +  个人知识库(文章)
        │  clone/pull         │ 导出 Markdown
        ▼                     ▼
   本地工作区：inbox → content（合并归一化）
        │
        ▼  GEO/SEO 技术修正（依据本地规范 + 实时规范）
   构建 → 纯静态产物
        │
        ▼  部署（EdgeOne Pages / 自有服务器）
   浏览器自动化验收（线上内容核对）
        │
        ▼  git commit + push（更新代码回库）
```

## 核心机制：规范一致性 + 时效

- 运行时实时搜索最新 GEO/SEO 规范，并**写入本地** `.geo-cms/specs/`。
- 若本地已有规范，**并行**启动「用本地规范做全站优化」与「实时搜索最新规范」；
  优化完成后，把本次增量新规范**补充**进本地文档，保证下次一致、且时效不丢。

## 快速开始

### 阶段一：初始化（一次性）

```bash
# 1) 验证 git 读写权限（循环直到 READ_OK + WRITE_OK）
python scripts/verify_git.py --repo <git-url> --path . --branch main

# 2) 配置知识库 / 部署（写入 .geo-cms/config.json，参考 assets/config-sample.json）
# 3) 提交配置
git add .geo-cms/config.json && git commit -m "chore: init geo-cms config" && git push
```

### 阶段二：每次内容更新

```bash
# 0) 规范预检：已存在则并行优化+实时搜索；不存在则先建基线
python scripts/fetch_geo_specs.py --init    # 首次建立基线
python scripts/fetch_geo_specs.py --merge   # 并行阶段合并实时规范

# 2-3) 知识库导出到 inbox 后，归一化合并到 content/
python scripts/sync_kb.py --config .geo-cms/config.json

# 4) 拉取最新源码
git pull --rebase

# 5) 全站 GEO 优化 + 静态扫描（依据 .geo-cms/specs/）
python scripts/geo_check.py --root . --out out --report .geo-cms/geo-report.json

# 6) 构建 + 部署（EdgeOne Pages 技能 / 自有服务器 rsync）

# 7) 增量规范补充
python scripts/fetch_geo_specs.py --append

# 8) 浏览器验收（需 Playwright，否则改用浏览器技能手动核对）
python scripts/verify_deploy.py --base-url https://yoursite.com --pages /,/blog/x --report .geo-cms/verify-report.json

# 9) 提交更新代码回库
git add -A && git commit -m "content: 同步知识库 + GEO 优化" && git push
```

## 目录结构

```
geo-cms/
├── SKILL.md                      # 入口 + 编排工作流
├── references/                   # 详细过程文档（按需加载）
│   ├── setup.md                  # 初始化、git 验证、配置
│   ├── knowledge-base.md         # 知识库适配器（导出→inbox→content）
│   ├── geo-spec-management.md    # 规范实时搜索 + 本地增量 + 并行
│   ├── geo-optimization.md       # 全站 GEO/SEO 优化清单
│   ├── deployment.md             # 部署适配器（EdgeOne/自有服务器）
│   └── browser-verification.md   # 上线后浏览器验收
├── scripts/                      # 可执行脚本
│   ├── verify_git.py             # git 读写权限探测循环
│   ├── sync_kb.py                # KB 导出归一化合并到 content
│   ├── fetch_geo_specs.py        # 实时规范合并/增量补充
│   ├── geo_check.py              # 静态 GEO/SEO 缺口扫描
│   └── verify_deploy.py          # 浏览器验收驱动
└── assets/                       # 模板
    ├── content-template.md       # 文章落库模板（含 GEO frontmatter）
    ├── spec-template.md          # 技术规范文档模板
    ├── config-sample.json        # config.json 样例
    └── geo-cms-gitignore.txt     # 目标仓库 .gitignore 模板
```

## 连接器依赖（本机已连接可直用）

- **EdgeOne Pages**：部署托管平台（`deployment.type=edgeone-pages`）
- **腾讯文档 / 飞书**：知识库导出（走对应连接器技能）
- **浏览器技能（agent-browser / playwright-cli）**：上线后验收

无对应连接器时，改用 `markdown` 类型本地目录作为知识库来源，仍可完整运行。
