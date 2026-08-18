# 阶段一：初始化与配置（Setup）

本文件细化 SKILL.md「阶段一」的每一步判定逻辑。目标产出：仓库内能跑通 `git` 读写、
`config.json` 写好、知识库与部署目标已登记。

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

| type | 来源 | 适配器 |
|------|------|--------|
| `tencent-docs` | 腾讯文档（本机已连接） | 走 tencent-docs 技能导出 Markdown |
| `feishu` | 飞书文档/知识库（本机已连接） | 走飞书技能导出 |
| `ima` | IMA 知识库 | 走 ima 技能（若已连接） |
| `markdown` | 本地 Markdown 目录 / 已 git 同步的文档 | 直接读取 |

每个 KB 记录：`{id, type, name, inbox: ".geo-cms/inbox/<id>", format: "md"}`。
`inbox` 为该 KB 导出落点，合并时由 `sync_kb.py` 读取。

---

## 4. 收集部署信息

让用户提供部署目标，`config.deployment.type` 取其一：

- `edgeone-pages`：托管平台。本机已连接 EdgeOne Makers 连接器，部署时走其技能。
  记录 `project`（项目名/新建名）、`distDir`（静态产物目录）。
- `custom-server`：自有服务器。记录 `ssh`（user@host）、`remoteDir`（静态根目录）、
  可选 `distDir`。部署用 `rsync -az --delete <distDir>/ <ssh>:<remoteDir>/`。
- `other`：用户自述方案，记录自由字段，部署步骤由用户确认。

> 部署前必须确认产物为纯静态（见 `geo-optimization.md` 的静态校验），
> 非静态一律拒绝上线。

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

满足以下全部条件，阶段一结束，可进入阶段二：
- [ ] `verify_git.py` 输出 `READ_OK` + `WRITE_OK`
- [ ] `config.knowledgeBases` 至少 1 项且 `type` 合法
- [ ] `config.deployment.type` 已填且参数完整
- [ ] `config.json` 已提交并推送
