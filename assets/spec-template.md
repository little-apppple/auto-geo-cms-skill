# 技术规范文档模板（spec-template.md）

本地规范库 `.geo-cms/specs/` 的两种文件格式。

## 1) 主题文件（robots.md / llms.md / schema.md / content.md / technical.md）

每条规范一行，TAG 为唯一键：

```markdown
- [GEO-BOT-01] robots.txt 需 Allow GPTBot/ClaudeBot/PerplexityBot/Baiduspider/Bytespider/Applebot (source: https://example.com/spec; updated: 2026-08-18)
- [GEO-LLMS-01] 根目录放置 llms.txt，给出站点摘要与关键页面索引 (source: https://llmstxt.example; updated: 2026-08-18)
```

## 2) _inbox.md（agent 实时搜索后的暂存）

agent 执行 WebSearch 后，把发现写入 `_inbox.md`，格式同上；随后
`fetch_geo_specs.py` 解析并按 TAG 前缀归类合并：

```markdown
- [GEO-BOT-02] 新增 AI 爬虫 ExampleBot 需在 robots.txt 显式 Allow (source: https://news.example/2026; updated: 2026-08-18)
- [GEO-TECH-04] 静态产物应保持 no-js 可见，避免内容依赖客户端渲染 (source: https://seo.example; updated: 2026-08-18)
```

## 3) manifest.json（条目索引）

由脚本自动维护，记录每个 TAG 所在文件、来源与更新时间：

```json
{
  "entries": {
    "GEO-BOT-01": {"file": "robots.md", "updated": "2026-08-18", "source": "https://example.com/spec"}
  },
  "lastRun": "2026-08-18"
}
```

TAG 前缀 → 主题文件映射（脚本据此归类）：

| 前缀 | 文件 |
|------|------|
| GEO-BOT / GEO-LLMS | robots.md / llms.md |
| SCHM | schema.md |
| GEO-FAQ / GEO-CITE / GEO-LOCAL / GEO-META / GEO-MULTI | content.md |
| GEO-TECH | technical.md |
