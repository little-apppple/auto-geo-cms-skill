# 文本落库回环（KB Round-trip，硬约束）

> 一句话：**任何要上站的文本，先在知识库里有据可查，再从知识库读回来用。**
> 不允许「模型脑内生成 → 直接写进模板 / 页面 / content」，那样数据游离在流水线之外，无法管理、无法审计、无法复用。

---

## 1. 为什么加这条约束

| 直接生成（禁止） | 落库回环（唯一合法路径） |
|---|---|
| 文本只存在于这次会话上下文里，结束后蒸发 | 落盘可查，下次还能改、还能删、还能迁移 |
| 改了页面但不知道源头在哪，冲突时无从比对 | 源在 inbox，页面是副本，改源再同步即可 |
| 多页文案互相重复/矛盾，无法统一口径 | 一篇源文章派生多处文案，有唯一真相 |
| 删除靠记忆，容易漏 | `sync_kb.py` 按索引 prune，删源即全网下线 |
| 审计时无法回答「这句话谁写的、从哪来」 | 索引记录 `source / origin / provenance / hash` |

## 2. 强制链路（缺一步即禁止上线）

```
① 起草（可来自 agent / 用户 / 外部生成技能）
        │  禁止直接写进 content/ 或模板文件
        ▼
② 落库 inbox      .geo-cms/inbox/<kbId>/<slug>.md   ← content_gate.py --stage
   必须带 frontmatter：title / date / slug / source / provenance
        │
        ▼
③ 归一化入库      scripts/sync_kb.py  →  content/<slug>.md + content-index.json
        │
        ▼
④ 回读校验        scripts/content_gate.py  （哈希一致、来源可追溯，否则阻断）
        │
        ▼
⑤ 使用（构建 / GEO 优化 / 模板填充 / meta / llms.txt / FAQ）
   文本必须来自第 ③ 步落盘的文件，不得来自对话记忆
```

**判断标准**：这句话如果现在删掉会话上下文，还能从磁盘上找到吗？找不到 = 违规。

## 3. 适用范围与例外

**适用（必须走回环）**
- 文章正文、章节标题、FAQ 问答对、摘要 `summary`
- 首页/落地页文案（hero、卖点、CTA、关于我们、页脚介绍）
- `meta title` / `meta description` / `og:*` 文案
- `llms.txt` / `llms-full.txt` 的说明性内容、FAQ Schema 文本
- 图片 `alt`、结构化数据里的描述字段
- 模板内被替换成业务内容的占位文案

**例外（不需要回环，但仍需可追溯）**
- 纯代码：组件、样式、构建配置、脚本
- 纯配置：`config.json`、部署参数、路由表
- 结构性常量：导航标题若直接取自文章 `title` 字段，视为已回环
- 单字/单位类 UI 标签（「提交」「更多」「¥」）不构成内容资产

> 判断口诀：**能不能被引用、被检索、被翻译成 GEO 答案？能，就必须落库。**

## 4. 文案资产登记（contentDir 之外的文本）

hero copy、meta、llms.txt 等不在 `contentDir` 里的文本，登记到 `.geo-cms/text-assets.json`，
用 `from` 指向源文章 slug。门禁会校验 `from` 是否存在，杜绝「页面上有文案、库里没有出处」。

```json
{
  "assets": [
    {"id": "home-hero",   "kind": "page-copy", "path": "src/pages/index.astro",
     "from": "what-is-geo", "excerpt": "GEO 让 AI 引擎愿意引用你的官网"},
    {"id": "home-meta",   "kind": "meta",      "path": "src/layouts/Base.astro",
     "from": "what-is-geo"},
    {"id": "llms-intro",  "kind": "llms",      "path": "public/llms.txt",
     "from": "geo-checklist"},
    {"id": "faq-pricing", "kind": "faq",       "path": "src/pages/pricing.astro",
     "from": "pricing-explained"}
  ]
}
```

`kind` 取值：`page-copy` / `meta` / `llms` / `faq` / `schema` / `alt`。

## 5. 命令

```bash
# 起草落库（唯一合法的「加文本」入口）
python scripts/content_gate.py --config .geo-cms/config.json \
  --stage drafts/geo-intro.md --kb kb1 --slug what-is-geo

# 归一化入 content/ 并登记索引
python scripts/sync_kb.py --config .geo-cms/config.json

# 回环门禁（strict：有违规即退出码 1，不得继续构建）
python scripts/content_gate.py --config .geo-cms/config.json

# 把已存在的手写/历史文件纳入知识库（消除 DRIFT）
python scripts/content_gate.py --config .geo-cms/config.json \
  --adopt content/legacy-post.md --kb kb1
```

报告落在 `.geo-cms/content-gate.json`。

## 6. 门禁发现的五类问题

| 类型 | 含义 | 处理 |
|---|---|---|
| `DRIFT` | content/ 有文件但索引里没有 → 直接生成/手写未回库 | 用 `--adopt` 纳入 KB，或删除该文件 |
| `DIVERGED` | 文件哈希 ≠ 索引哈希 → 绕过 KB 直接改了 content | 改动搬到 inbox 源文件，重跑 `sync_kb.py` |
| `BAD_SOURCE` | 索引 source 不在 `config.knowledgeBases` | 补声明，或重新从合法 KB 同步 |
| `PHANTOM` | 索引有、文件没了 → 删除绕过同步脚本 | 重跑 `sync_kb.py`（自动 prune 并清索引） |
| `COPY_NO_SRC` | 文案资产 `from` 缺失或指向不存在的文章 | 补 `from`，或先把源文章落库 |

模式由 `config.contentGate.mode` 控制：`strict`（默认，阻断）/ `warn`（仅告警，写日志）。

## 7. 与「不生成内容」边界的关系

本条约束**不改变**职责边界，只是把边界变成可执行的检查：

- 正文创作仍然交给用户或外部生成技能，geo-cms 不写正文；
- 但**任何**正文（哪怕来自外部技能、哪怕只有一句话的 hero 文案）都必须经 inbox 落库，
  由 `sync_kb.py` 归一化后从磁盘读回，才允许进入构建与模板填充；
- 外部生成技能的产出**直接落到 inbox**（或先落临时草稿再 `--stage`），不得直接写进 `content/` 或模板。

## 8. 常见违规写法（会被门禁拦下）

- 在 `.astro` / `.tsx` 里硬编码一段介绍文案，库里没有对应文章。
- 直接 `Write content/new-post.md` 而没经过 inbox。
- 改了 `content/xxx.md` 的正文，却没改 inbox 源文件。
- agent 在对话里想好一段 meta description，直接改 `Base.astro`，没登记 `text-assets.json`。
- 为了让门禁通过，把 `mode` 改成 `warn` 长期使用（等价于废除约束；构建日志必须说明原因与期限）。
