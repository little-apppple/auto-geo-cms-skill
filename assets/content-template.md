# 文章落库模板（content-template.md）

`sync_kb.py` 会把知识库导出的 Markdown 归一化为下方结构后写入 `content/`。
新增/直接上传文章时，建议直接按此模板撰写，减少合并阶段的补字段工作。

```markdown
---
title: 什么是 GEO（生成式引擎优化）
date: 2026-08-18
slug: what-is-geo
tags: [GEO, SEO, AI搜索]
summary: GEO 是通过结构化内容与可引用表述，提升品牌在 AI 搜索答案中被引用的可能性的优化方法。
source: kb1
geoVerified: false          # 经 geo-optimization 处理后置 true
faq:                        # 可选：结构化问答，用于 FAQPage Schema
  - question: GEO 和 SEO 有什么区别？
    answer: SEO 面向传统搜索引擎排名，GEO 面向 AI 生成式答案的引用，更强调内容可被直接引用。
---

正文首段即给出核心结论（结论前置），让 AI 抓取时直接获得可引用答案。

## 小节标题
展开说明，使用清晰的小标题与列表，便于 AI 提取要点。

> 避免「联系我们了解更多」式死胡同；关键句应自包含、可独立引用。
```

frontmatter 字段说明：

| 字段 | 必填 | 说明 |
|------|------|------|
| title | ✅ | 文章标题 |
| date | ✅ | 发布/导出日期（YYYY-MM-DD） |
| slug | ✅ | 稳定唯一标识，用于去重与 URL |
| tags | ⬜ | 标签数组 |
| summary | ⬜ | 一句话可引用摘要（结论前置） |
| source | ⬜ | 来源 KB id |
| geoVerified | ⬜ | 是否已完成 GEO 优化（默认 false） |
| faq | ⬜ | 结构化问答对，用于 FAQPage Schema |
