# GEO/SEO 技术规范缓存管理（bridge 仅归档，不设定规则）

本文件落实 SKILL.md「阶段二步骤 0 / 步骤 7」的**规范缓存**机制——把来自**外部 GEO 能力**
（已装的 GEO 技能如 `geo-zh`，或在线检索 WebSearch）的规范**本地持久化**，以支持并行优化与
增量补充，保证每次优化口径一致且时效不丢。

> **边界**：geo-cms **不创作、不设定** GEO 规则。规范条目的「权威性」属于外部 GEO 能力/检索结果；
> 本文件与 `fetch_geo_specs.py` 只负责**缓存、归类、去重、增量补充**这些外部产出，绝不自行拍板口径。

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
specs/ 是否已缓存「外部 GEO 能力/检索」产出的规范且非空？
├─ 是 ──→ 并行：
│   A) 全站优化（geo-optimization.md）直接使用本地 specs/ 作为基线（规则权威在外部）
│   B) 实时规范检索（见下）→ fetch_geo_specs.py --merge（后台/并行执行）
│   优化结束后执行步骤 7 把 B 的增量并入 specs/
└─ 否 ──→ 先执行 B) 建立基线规范缓存：
          geo-optimize 能力（如 geo-zh）导出规范，或 WebSearch 检索最新规范
          → 写入 .geo-cms/specs/_inbox.md
          → 运行 fetch_geo_specs.py --init（空 _inbox 会得到空基线，务必先取规范）
          再执行 A) 全站优化
```

> 关键：**已存在本地规范时不要等实时检索结果再开始优化**，先并行用本地规范开干，
> 实时检索的结果在收尾时增量补入，既保一致又保时效。

---

## 规范获取（依赖 geo-optimize 外部能力）

规范条目的来源**必须是外部 GEO 能力**，优先级如下：

1. **首选：已装 GEO 技能**（如 `geo-zh`）——直接请该技能产出当前规范清单，作为最权威来源。
2. **降级：WebSearch 在线检索**——当环境未装 GEO 技能、且用户在阶段零已同意降级时，由 agent 检索：

| 主题 | 示例查询 |
|------|----------|
| AI 爬虫 | `GPTBot ClaudeBot PerplexityBot robots.txt allow 2026` |
| llms.txt | `llms.txt format specification best practice` |
| Schema | `FAQPage Article JSON-LD generative engine optimization` |
| 内容 | `AI search answer optimization FAQ conclusion first` |
| 中国区 | `百度 豆包 文心一言 爬虫 robots 收录 优化` |
| 技术 | `static site export SEO Core Web Vitals 2026` |

把检索到的要点（或 GEO 技能导出的清单）写入 `.geo-cms/specs/_inbox.md`
（条目格式 `[TAG] 描述 (source: url; updated: date)`，附 `source` URL）。

> geo-cms 此时只是「搬运工」：把外部权威规范落到本地缓存，绝不自行增减或改写规则口径。

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

- `specs/` 随仓库提交 → 团队/多次运行口径一致（口径本质来自外部 GEO 能力，缓存只是镜像）。
- 优化步骤（geo-optimization.md）以 `specs/` 为**本地缓存基线**，规则权威始终在外部 GEO 能力/检索，不凭记忆。
- 实时检索只「补充」不「覆盖」既有规范，避免来回摇摆。
- WebSearch 不可用时退回纯本地规范缓存，并在汇报中标注「本轮未做实时增量」。
- 若阶段零选定的 `geo-optimize` 是 WebSearch 降级，**必须在汇报中明示「规则未由专业 GEO 技能把关」**。
