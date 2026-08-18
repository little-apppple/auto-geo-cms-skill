# 初始化与配置（Setup）

本文件细化 SKILL.md「阶段零（环境检测）」与「阶段一（初始化）」的判定逻辑。目标产出：
外部依赖映射写入 `config.capabilities`、仓库内能跑通 `git` 读写、`config.json` 写好、
知识库与部署目标已登记。

> **职责边界提醒**：geo-cms 不生成内容、不设定 GEO 规则。下列四类能力（kb-export / geo-optimize /
> deploy / browser-verify）必须来自环境已装的外部技能/连接器或在线检索，本阶段负责把它们**检测并登记**。

---

## 阶段零：环境检测与依赖搭建（首次必做）

geo-cms 本体只做桥接，下列能力全部外部化。首次运行必须逐个检测并登记到 `config.capabilities`。

### 0.1 枚举可用能力
- 用 `Skill` 工具可枚举当前已安装技能（如 `geo-zh`、`agent-browser`、`playwright-cli` 等）。
- 读取连接器连接状态：EdgeOne Makers（`edgeone-pages`）、飞书、腾讯文档、ima 等是否 `connected`。

### 0.2 逐项判定 available / missing
对照 SKILL.md「外部依赖契约」四能力：

| 能力 | 检测方式 |
|------|----------|
| `kb-export` | 腾讯文档/飞书/ima 任一连接器 connected，或用户承诺直接上传 `.md` |
| `geo-optimize` | 已装 GEO 类技能（geo-zh 等），或用户同意走 WebSearch 降级 |
| `deploy` | EdgeOne Makers connected，或用户提供自有服务器 SSH/远程目录 |
| `browser-verify` | 已装 agent-browser / playwright 技能，或同意 verify_deploy.py 降级 |

### 0.3 补齐 missing 项（与用户沟通）
- 调用 `Skill` 工具 `command="find-skills"` 查找可安装技能（如「GEO 优化」「浏览器自动化」）；
- 或请用户连接对应连接器（EdgeOne Makers / 飞书 / 腾讯文档 / ima）；
- `geo-optimize` 实在无法安装时，明确告知用户「将走 WebSearch 降级，规则未由专业 GEO 技能把关」并取得同意；
- `deploy` 无任何来源 → **停止**，缺必要外部能力无法继续。

### 0.4 写入并确认
把映射写进 `config.capabilities`（每项含 `resolved` 与 `mode: skill|connector|fallback`），
向用户展示后确认，再进入阶段一。示例：
```json
"capabilities": {
  "kb-export":     {"resolved": "tencent-docs", "mode": "connector"},
  "geo-optimize":  {"resolved": "geo-zh",       "mode": "skill"},
  "deploy":        {"resolved": "edgeone-pages","mode": "connector"},
  "browser-verify":{"resolved": "agent-browser","mode": "skill"}
}
```

---

## 1. 收集代码 git 库

向用户索取仓库地址，支持两种形式：
- **SSH**：`git@github.com:org/site.git`（需本机有对应私钥且已加入托管平台）
- **HTTPS**：`https://github.com/org/site.git`（可用 token 代替密码）

记录到 `config.git.repo`，并确定 `config.git.localPath`（默认当前仓库根 `.`；
若需另克隆到子目录，写绝对/相对路径）与 `config.git.branch`（默认 `main`，其次 `master`）。

---

## 2. 验证本地访问权限（循环直到连通）

运行：

```bash
python scripts/verify_git.py --repo <url> --path <localPath> --branch <branch>
```

脚本行为：
1. 若 `<localPath>` 不是 git 仓库 → 尝试 `git clone <repo> <localPath>`。
2. 已是仓库 → `git fetch --quiet`（验证**读取**权限）。

> 注意：`--path` 应为「已存在的仓库根目录」（本就是代码仓库）或一个**空目录**。
> 若指向非空且非 git 的目录，`git clone <repo> <path>` 会因目录非空而失败——此时请改用空目录或先 `git init`。
3. **写入**权限探测：`git push --dry-run origin <branch>`；若无 upstream 则先
   `git push -u origin <branch>` 的 dry-run 形式。也可改用探针分支法：
   建 `geo-cms-probe` 分支并真实推送、成功即删，验证写权限且不污染主分支。
4. 读取与写入均通过 → 打印 `READ_OK` 与 `WRITE_OK` 并以退出码 0 结束。
5. 任一步失败 → 打印可操作原因并以非 0 退出：

| 失败现象 | 原因提示 |
|----------|----------|
| `Permission denied (publickey)` | 本机缺 SSH key 或未加入托管平台 |
| `remote: Repository not found` | 仓库地址错误或无访问权限 |
| `fatal: could not read Username` | HTTPS 缺少凭据/token |
| `! [remote rejected] (permission denied)` | 账号无写权限，需申请 |
| `failed to push` 但 fetch 正常 | 仅缺写权限，区分读/写分别提示 |

**循环约束**：本技能在 `verify_git.py` 返回成功前**不得**进入内容合并/部署。
每失败一次，把原因转述给用户并请其修复（加 key / 换地址 / 申请权限），用户确认后重试。

---

## 3. 收集知识库指定

让用户明确**选择哪些知识库**作为内容来源（可多选）。支持的 `type`：

| type | 来源 | 导出方式（依赖 `capabilities.kb-export`） |
|------|------|--------|
| `tencent-docs` | 腾讯文档（本机已连接） | 走 tencent-docs 连接器技能导出 Markdown |
| `feishu` | 飞书文档/知识库（本机已连接） | 走飞书技能导出 |
| `ima` | IMA 知识库 | 走 ima 技能（若已连接） |
| `markdown` | 本地 Markdown 目录 / 已 git 同步的文档 | 直接读取 |

> 导出的**执行**由 `kb-export` 能力选定的来源完成（连接器技能或用户上传），geo-cms 只负责把导出物
> 归一化合并进 `content/`，不创作正文。

每个 KB 记录：`{id, type, name, inbox: ".geo-cms/inbox/<id>", format: "md"}`。
`inbox` 为该 KB 导出落点，合并时由 `sync_kb.py` 读取。

---

## 4. 收集部署信息

让用户提供部署目标，`config.deployment.type` 取其一：

- `edgeone-pages`：托管平台。本机已连接 EdgeOne Makers 连接器，部署时**委托**其技能上线
  （对应 `capabilities.deploy.mode=connector`）。记录 `project`（项目名/新建名）、`distDir`。
- `custom-server`：自有服务器。记录 `ssh`（user@host）、`remoteDir`（静态根目录）、可选 `distDir`。
  部署用 `rsync -az --delete <distDir>/ <ssh>:<remoteDir>/`（bridge 执行该命令，属部署编排）。
- `other`：用户自述方案，记录自由字段，部署步骤由用户确认。

> **部署是必要外部能力，不可降级**：若 `capabilities.deploy` 无任何来源，阶段零即应停止。
> 部署前必须确认产物为纯静态（见 `geo-optimization.md` 的静态校验），非静态一律拒绝上线。

---

## 5. 写 config.json 并首次提交

按 SKILL.md 的 `config.json` 结构落盘到仓库根 `.geo-cms/config.json`，然后：

```bash
git add .geo-cms/config.json
git commit -m "chore: init geo-cms config"
git push
```

`config.specs.lastUpdated` 首次置 `null`（表示规范库尚未建立，阶段二首次运行会先建基线）。

> 将 `assets/geo-cms-gitignore.txt` 的内容合并进仓库根 `.gitignore`（忽略 `inbox/` 与报告文件，
> 保留 `config.json` 与 `specs/`），避免把待合并原始导出提交进库。

---

## 完成判定

满足以下全部条件，阶段零 + 阶段一结束，可进入阶段二：
- [ ] `config.capabilities` 四能力均已 `resolved` 且经用户确认（`deploy` 必须有真实来源）
- [ ] `verify_git.py` 输出 `READ_OK` + `WRITE_OK`
- [ ] `config.knowledgeBases` 至少 1 项且 `type` 合法
- [ ] `config.deployment.type` 已填且参数完整
- [ ] `config.json` 已提交并推送
