# GEO/SEO 技术规范本地化管理

本文件落实 SKILL.md「阶段二步骤 0 / 步骤 7」的核心机制——**规范实时搜索 + 本地持久化 +
并行优化 + 增量补充**，保证每次优化口径一致且时效不丢。

---

## 本地规范库结构

规范库默认在 `.geo-cms/specs/`，按主题分文件，便于检索与增量合并：

```
.geo-cms/specs/
├── _inbox.md          ← 实时搜索原始发现（agent 暂存）
├── robots.md          ← robots.txt / AI 爬虫规范
├── llms.md            ← llms.txt 规范
├── schema.md          ← JSON-LD / 结构化数据规范
├── content.md         ← 内容可引用性 / FAQ / 结论前置规范
├── technical.md       ← 性能 / HTTPS / Sitemap / 静态化规范
└── manifest.json      ← 规范条目索引 + 来源 + 更新时间
```

每条规范形如：

```
- [GEO-BOT-01] robots.txt 需 Allow GPTBot/ClaudeBot/PerplexityBot/Baiduspider/Bytespider
  (source: https://...; updated: 2026-08-18)
```

---

## 步骤 0：预检与并行策略

```
specs/ 是否存在且非空？
├─ 是 ──→ 并行：
│   A) 全站优化（geo-optimization.md）直接使用本地 specs/ 作为基线
│   B) 实时规范搜索：见下「实时搜索」→ fetch_geo_specs.py --merge（后台/并行执行）
│   优化结束后执行步骤 7 把 B 的增量并入 specs/
└─ 否 ──→ 先执行 B) 建立基线规范库：
          WebSearch 检索最新规范 → 写入 .geo-cms/specs/_inbox.md
          → 运行 fetch_geo_specs.py --init（空 _inbox 会得到空基线，务必先搜）
          再执行 A) 全站优化
```

> 关键：**已存在本地规范时不要等实时搜索结果再开始优化**，先并行用本地规范开干，
> 实时搜索的结果在收尾时增量补入，既保一致又保时效。

---

## 实时搜索（由 agent 执行 WebSearch）

围绕固定主题发起检索，拾取当下最新规范与反例：

| 主题 | 示例查询 |
|------|----------|
| AI 爬虫 | `GPTBot ClaudeBot PerplexityBot robots.txt allow 2026` |
| llms.txt | `llms.txt format specification best practice` |
| Schema | `FAQPage Article JSON-LD generative engine optimization` |
| 内容 | `AI search answer optimization FAQ conclusion first` |
| 中国区 | `百度 豆包 文心一言 爬虫 robots 收录 优化` |
| 技术 | `static site export SEO Core Web Vitals 2026` |

把检索到的要点写入 `.geo-cms/specs/_inbox.md`（用上面的条目格式，附 `source` URL）。

---

## fetch_geo_specs.py 用法

```bash
# 建立基线（首次，specs/ 为空时）
python scripts/fetch_geo_specs.py --init --specs-dir .geo-cms/specs

# 合并实时搜索结果（并行阶段 / 优化前）
python scripts/fetch_geo_specs.py --merge --specs-dir .geo-cms/specs

# 增量补充（步骤 7，优化完成后只加新规范）
python scripts/fetch_geo_specs.py --append --specs-dir .geo-cms/specs
```

脚本逻辑：
1. 读 `_inbox.md` 的条目（`[TAG] 描述 (source: url; updated: date)`）。
2. 按 TAG 前缀归类到对应主题文件；已存在的相同 TAG 仅在其描述/来源变化时才更新（去重）。
3. `--append` 模式：仅写入「specs/ 中尚不存在 TAG」的条目，避免回写已固化规范。
4. 更新 `manifest.json`（条目数、各文件更新时间），并打印「新增 N / 更新 M」清单。

---

## 步骤 7：增量补充（时效闭环）

优化完成、部署验收通过后，再跑一次实时搜索（补本轮新发现的规范），
执行 `fetch_geo_specs.py --append`，把增量并入 `specs/`，并：

```bash
git add .geo-cms/specs
git commit -m "spec: 补充本轮 GEO/SEO 增量规范"
```

更新 `config.specs.lastUpdated` 为当前日期。这样**下一轮**既有一致基线，又含本轮时效。

---

## 一致性保障要点

- `specs/` 随仓库提交 → 团队/多次运行口径一致。
- 优化步骤（geo-optimization.md）以 `specs/` 为唯一权威清单，不凭记忆。
- 实时搜索只「补充」不「覆盖」既有规范，避免来回摇摆。
- WebSearch 不可用时退回纯本地规范，并在汇报中标注「本轮未做实时增量」。
