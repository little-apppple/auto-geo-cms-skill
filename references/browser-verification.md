# 上线后浏览器自动化验收

本文件细化阶段二步骤 8。部署完成后，用浏览器自动化核对线上内容，确保「优化真的生效、
用户看到的就是优化后的样子」。

---

## 验收前置

- 已取得线上 URL（首页 + 本次新增/更新页面）。
- 加载浏览器自动化能力：优先用 **agent-browser / playwright-cli** 技能做真实页面操作；
  或运行 `scripts/verify_deploy.py`（若环境已装 Playwright 则无头校验）。

---

## 验收清单（逐条核对）

### 1. 可达性与状态码
- [ ] 首页返回 200，无重定向死循环
- [ ] 本次新增/更新页面均返回 200，无 404
- [ ] `https://<domain>/robots.txt` 可访问且含 AI 爬虫 Allow
- [ ] `https://<domain>/llms.txt` 可访问
- [ ] `https://<domain>/sitemap.xml` 可访问

### 2. 内容正确性
- [ ] 正文完整可见（非 JS 渲染空白），AI 爬虫视角可见
- [ ] 本次同步的文章/FAQ 已出现且内容正确
- [ ] FAQ 结论前置（答案首句即结论）

### 3. GEO 元素
- [ ] 页面含 JSON-LD（Organization/Article/FAQPage，按页面类型）
- [ ] NAP（名称/地址/电话）在页脚可见
- [ ] 图片均有 alt
- [ ] Meta description 为答案式

### 4. 体验
- [ ] 关键图片加载正常（无裂图）
- [ ] 移动端视口正文可读（响应式正常）

---

## verify_deploy.py 用法

```bash
python scripts/verify_deploy.py \
  --base-url https://example.com \
  --pages /,/blog/what-is-geo,/faq \
  --report .geo-cms/verify-report.json
```

脚本（Playwright 可用时）无头打开各页面，断言：
- 状态码 200
- `<script type="application/ld+json">` 存在且合法 JSON
- 正文文本长度 > 阈值（非空白）
- `robots.txt`/`llms.txt` 可访问
输出每页通过/失败项，供 agent 汇总。

> 若 Playwright 不可用，脚本降级为提示 agent 改用浏览器技能手动核对上述清单。

---

## 验收不通过的处理

- 内容缺失/错误 → 回到知识库合并（步骤 3）或优化（步骤 5）修复。
- GEO 元素缺失 → 回到优化（步骤 5）补 Schema/NAP/alt。
- 部署异常 → 回到部署（步骤 6）回滚重部。
- 修复后重新部署并复验，直至全部通过才进入步骤 9 提交回库。

---

## 完成判定

满足：全部清单项通过 + `verify_deploy.py` 无 FAIL（或浏览器技能手动核对全绿），
方可视为「上线验收通过」，进入步骤 9。
