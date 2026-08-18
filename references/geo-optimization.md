# 全站 GEO/SEO 优化清单（部署前必做）

本清单在阶段二步骤 5 执行，依据本地 `.geo-cms/specs/` 规范对合并后的源码做修正。
可用 `scripts/geo_check.py` 做静态缺口扫描，按报告从 P0 到 P2 逐项修复。

---

## 优化总原则

- **可引用性优先**：AI 搜索引擎抓取的是「能直接引用的清晰文本」，结论前置、无死胡同。
- **结构化数据**：让 AI 明确「这是谁、这是什么文章、有哪些问答」。
- **静态可达**：纯静态产物，AI 爬虫与搜索引擎无需执行 JS 即可见正文。
- **避免绝对承诺**：用「提升被引用可能性」，不写「保证被 ChatGPT 引用」。

---

## P0（部署前必须完成）

| 优化项 | 规范 ID | 做法 |
|--------|---------|------|
| robots.txt 开放 AI 爬虫 | GEO-BOT-01 | `Allow` GPTBot、ClaudeBot、PerplexityBot、Baiduspider、Bytespider、Applebot 等 |
| llms.txt 站点摘要 | GEO-LLMS-01 | 根目录放 `llms.txt`，给出站点摘要 + 关键页面索引 |
| 纯静态输出 | GEO-BOT-02 | SSG `output: export` / `static` 模式，确认产物无服务端依赖 |
| Organization Schema | SCHM-ORG-01 | 全局注入 JSON-LD（名称/Logo/URL/sameAs） |
| 文章 Article Schema | SCHM-ART-01 | 每篇内容页注入 Article/ BlogPosting JSON-LD |
| FAQPage Schema | GEO-FAQ-03 | 含 FAQ 的页面注入 FAQPage JSON-LD，且 Question 数 = 正文 FAQ 数 |

---

## P1（强烈建议）

| 优化项 | 规范 ID | 做法 |
|--------|---------|------|
| FAQ 结论前置 | GEO-FAQ-02 | 答案首句即核心结论，用 `<strong>`/加粗标记 |
| 内容可独立引用 | GEO-CITE-01 | 无「联系我们获取详情」式死胡同，关键句自包含 |
| NAP 全页可见 | GEO-LOCAL-01 | Footer 全局渲染名称/地址/电话（本地商家尤其重要） |
| 图片 alt 完整 | GEO-MULTI-01 | 所有 `<img>` 有描述性 alt；装饰图 `alt=""` |
| Meta description 可引用 | GEO-META-01 | 答案式描述，首句给出核心信息 |
| Sitemap | GEO-TECH-01 | 生成 `sitemap.xml` 并在 robots.txt 引用 |
| HTTPS | GEO-TECH-02 | 全站 https 链接，无混合内容 |

---

## P2（锦上添花）

| 优化项 | 规范 ID | 做法 |
|--------|---------|------|
| 结构化 FAQ 区块 | GEO-FAQ-01 | FAQ 首屏展示，不折叠 |
| Open Graph / Twitter Card | GEO-META-02 | 社交与 AI 摘要卡片完整 |
| 面包屑 Schema | SCHM-BR-01 | 内容层级清晰 |
| 多语言 hreflang | GEO-MULTI-02 | 多语言站点加 hreflang |
| 核心 Web Vitals | GEO-TECH-03 | LCP/CLS/INP 达标，利于收录与体验 |

---

## 源码修正方式（按技术栈）

| 技术栈 | 注入位置 |
|--------|----------|
| Next.js (App Router) | `app/layout.tsx` 全局 Schema；`app/(content)/[slug]/page.tsx` 注入 Article |
| Astro / Hugo / VitePress | 公共布局/模板注入 JSON-LD；内容 frontmatter → Schema |
| 纯 HTML | 直接改 `<head>` 与页脚；`robots.txt`/`llms.txt` 放根 |
| 其他 SSG | 改公共模板/布局，遵循其静态输出约定 |

> 注入时**遵循原站样式与结构**，不重写项目；只做增量 GEO 修正。

---

## 静态产物校验（部署前门禁）

部署前必须确认 `outputDir` 为纯静态：
- 无 `server.js`/`api/` 运行时依赖、无必须后端才能渲染的正文。
- `robots.txt`、`llms.txt`、`sitemap.xml` 均在产物根目录可访问。
- 不满足 → 退回修正 SSG 配置，**拒绝带服务端依赖的产物上线**。

---

## geo_check.py 用法

```bash
python scripts/geo_check.py --root <repoRoot> --out <outputDir> --report .geo-cms/geo-report.json
```

> `geo_check.py` 扫描的是**构建产物**（`--out`），因此必须在步骤 6 构建之后、部署之前运行；
> 源码级预扫描可加 `--root .` 不加 `--out`，但 P0 门禁以构建后扫描为准。

输出 P0/P1/P2 缺口清单（含文件路径与建议），据此逐项修复后复跑直至无 P0 残留。
