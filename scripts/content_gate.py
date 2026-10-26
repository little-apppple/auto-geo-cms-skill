#!/usr/bin/env python3
"""content_gate.py - enforce the "KB round-trip" rule for ALL text content.

Rule (hard constraint): no text may be injected straight from the model into the
site or template. Every piece of text must first be persisted into a managed
store (KB inbox), then normalized into site.contentDir by sync_kb.py, then read
back from disk before it is used for building or filling templates.

This gate refuses to pass when text has no managed origin ("游离内容"):
  1. DRIFT       content/ file exists but is not registered in content-index.json
  2. DIVERGED    content/ file hash != indexed hash (edited in place, not via KB)
  3. BAD_SOURCE  index entry points to a KB that is neither declared nor _upload
  4. PHANTOM     index entry has no corresponding file on disk
  5. COPY_NO_SRC text asset (hero copy / meta / llms / faq) has no source slug

Usage:
  # gate (default): blocks on any violation when mode=strict
  python scripts/content_gate.py --config .geo-cms/config.json

  # stage a draft into the KB inbox (the ONLY sanctioned way to add text)
  python scripts/content_gate.py --config .geo-cms/config.json \
      --stage drafts/geo-intro.md --kb kb1 --slug what-is-geo

  # adopt an existing content file into the KB so it stops being drift
  python scripts/content_gate.py --config .geo-cms/config.json \
      --adopt content/what-is-geo.md --kb kb1

Exit codes: 0 = pass (or warn mode with findings), 1 = blocked, 2 = usage error.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date

SKIP_PREFIXES = ("_", ".")


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_frontmatter(text):
    if text.startswith("---"):
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
        if m:
            fm = {}
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"').strip("'")
            return fm, m.group(2)
    return {}, text


def dump_frontmatter(fm, body):
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f'{k}: [{", ".join(str(x) for x in v)}]')
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body


def resolve_paths(config_path):
    cfg = load_json(config_path, {})
    if not cfg:
        sys.exit(f"[gate] config not found or invalid: {config_path}")
    cfg_dir = os.path.dirname(os.path.abspath(config_path))
    repo_root = os.path.dirname(cfg_dir) if os.path.basename(cfg_dir) == ".geo-cms" else cfg_dir
    state_dir = os.path.join(repo_root, ".geo-cms")
    content_dir = os.path.join(repo_root, cfg.get("site", {}).get("contentDir", "content"))
    return cfg, repo_root, state_dir, content_dir


def iter_content(content_dir):
    for root, dirs, files in os.walk(content_dir):
        dirs[:] = [d for d in dirs if not d.startswith(SKIP_PREFIXES)]
        for fn in sorted(files):
            if not fn.endswith(".md") or fn.startswith(SKIP_PREFIXES):
                continue
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, content_dir).replace(os.sep, "/")
            yield rel[:-3], fp


# ---------------------------------------------------------------- stage / adopt
def stage(args, cfg, repo_root):
    kbs = {kb["id"]: kb for kb in cfg.get("knowledgeBases", [])}
    if args.kb not in kbs:
        sys.exit(f"[gate] unknown KB id '{args.kb}'. declared: {list(kbs) or 'none'}")
    inbox = os.path.join(repo_root, kbs[args.kb].get("inbox", f".geo-cms/inbox/{args.kb}"))
    if not os.path.isfile(args.stage):
        sys.exit(f"[gate] draft not found: {args.stage}")

    text = open(args.stage, encoding="utf-8").read()
    fm, body = parse_frontmatter(text)
    slug = args.slug or re.sub(r"\.md$", "", os.path.basename(args.stage))
    if "title" not in fm:
        m = re.search(r"^#\s+(.+)$", body, re.M)
        fm["title"] = m.group(1).strip() if m else slug
    fm.setdefault("date", str(date.today()))
    fm["slug"] = slug
    fm["source"] = args.kb
    fm["provenance"] = "kb-roundtrip"
    fm["stagedAt"] = str(date.today())

    os.makedirs(inbox, exist_ok=True)
    target = os.path.join(inbox, slug + ".md")
    if os.path.exists(target) and not args.force:
        sys.exit(f"[gate] already staged: {target} (use --force to overwrite)")
    with open(target, "w", encoding="utf-8") as f:
        f.write(dump_frontmatter(fm, body))
    print(json.dumps({
        "staged": os.path.relpath(target, repo_root).replace(os.sep, "/"),
        "next": "python scripts/sync_kb.py --config .geo-cms/config.json "
                "&& python scripts/content_gate.py --config .geo-cms/config.json",
    }, ensure_ascii=False, indent=2))
    return 0


def adopt(args, cfg, repo_root):
    kbs = {kb["id"]: kb for kb in cfg.get("knowledgeBases", [])}
    if args.kb not in kbs:
        sys.exit(f"[gate] unknown KB id '{args.kb}'. declared: {list(kbs) or 'none'}")
    src = args.adopt
    if not os.path.isfile(src):
        sys.exit(f"[gate] file not found: {src}")
    inbox = os.path.join(repo_root, kbs[args.kb].get("inbox", f".geo-cms/inbox/{args.kb}"))
    os.makedirs(inbox, exist_ok=True)
    slug = re.sub(r"\.md$", "", os.path.basename(src))
    target = os.path.join(inbox, slug + ".md")
    text = open(src, encoding="utf-8").read()
    fm, body = parse_frontmatter(text)
    fm.setdefault("date", str(date.today()))
    fm["slug"] = slug
    fm["source"] = args.kb
    fm["provenance"] = "adopted"
    with open(target, "w", encoding="utf-8") as f:
        f.write(dump_frontmatter(fm, body))
    print(json.dumps({
        "adopted": os.path.relpath(target, repo_root).replace(os.sep, "/"),
        "next": "python scripts/sync_kb.py --config .geo-cms/config.json",
    }, ensure_ascii=False, indent=2))
    return 0


# ----------------------------------------------------------------------- gate
def gate(args, cfg, repo_root, state_dir, content_dir):
    index_path = os.path.join(state_dir, "content-index.json")
    index = load_json(index_path, {"entries": {}}).get("entries", {})
    declared = {kb["id"] for kb in cfg.get("knowledgeBases", [])} | {"_upload"}

    gate_cfg = cfg.get("contentGate", {}) or {}
    mode = gate_cfg.get("mode", "strict")
    assets_path = os.path.join(
        repo_root, gate_cfg.get("textAssets", ".geo-cms/text-assets.json"))

    violations = []
    on_disk = set()

    for slug, fp in iter_content(content_dir):
        on_disk.add(slug)
        rel = os.path.relpath(fp, repo_root).replace(os.sep, "/")
        text = open(fp, encoding="utf-8").read()
        meta = index.get(slug)
        if not meta:
            violations.append({
                "type": "DRIFT", "target": rel,
                "hint": "未登记内容（直接生成或手写后未回库）。"
                        "先落库 inbox（--stage / --adopt）再跑 sync_kb.py",
            })
            continue
        if meta.get("hash") != sha256(text):
            violations.append({
                "type": "DIVERGED", "target": rel,
                "hint": f"哈希与索引不一致（索引 hash={str(meta.get('hash'))[:12]}）。"
                        "改动应发生在 inbox 源文件，然后重跑 sync_kb.py",
            })
        src = meta.get("source")
        if src and src not in declared:
            violations.append({
                "type": "BAD_SOURCE", "target": rel,
                "hint": f"source='{src}' 未在 config.knowledgeBases 中声明，也无法追溯来源",
            })

    for slug, meta in index.items():
        if slug not in on_disk:
            violations.append({
                "type": "PHANTOM", "target": slug + ".md",
                "hint": "索引存在但文件不存在；可能是归档操作绕过了 sync_kb.py",
            })

    # Text assets outside contentDir (hero copy / meta description / llms.txt / FAQ)
    if os.path.exists(assets_path):
        assets = load_json(assets_path, {}).get("assets", [])
        for a in assets:
            aid = a.get("id") or "(no-id)"
            src = a.get("from")
            if not src:
                violations.append({
                    "type": "COPY_NO_SRC", "target": aid,
                    "hint": "文案资产缺少 from（来源文章 slug），无法追溯",
                })
            elif src not in index:
                violations.append({
                    "type": "COPY_NO_SRC", "target": aid,
                    "hint": f"from='{src}' 不在内容索引中，文案属游离数据",
                })
        checked_assets = len(assets)
    else:
        checked_assets = 0

    report = {
        "checkedAt": str(date.today()),
        "mode": mode,
        "contentDir": os.path.relpath(content_dir, repo_root),
        "contentFiles": len(on_disk),
        "indexEntries": len(index),
        "textAssets": checked_assets,
        "violations": violations,
        "passed": not violations,
    }
    write_json(os.path.join(state_dir, "content-gate.json"), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if violations and mode == "strict":
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=".geo-cms/config.json")
    ap.add_argument("--stage", help="draft file to persist into the KB inbox")
    ap.add_argument("--adopt", help="existing content file to pull back into the KB")
    ap.add_argument("--kb", help="KB id for --stage / --adopt")
    ap.add_argument("--slug")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    cfg, repo_root, state_dir, content_dir = resolve_paths(args.config)
    if args.stage or args.adopt:
        if not args.kb:
            sys.exit("[gate] --kb is required with --stage / --adopt")
        return stage(args, cfg, repo_root) if args.stage else adopt(args, cfg, repo_root)
    return gate(args, cfg, repo_root, state_dir, content_dir)


if __name__ == "__main__":
    sys.exit(main())
