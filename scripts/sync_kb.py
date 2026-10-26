#!/usr/bin/env python3
"""sync_kb.py - normalize KB exports in inbox and merge into the repo content dir.

Reads .geo-cms/config.json, for each knowledgeBase reads its inbox/*.md,
normalizes frontmatter (title/date/slug/tags + GEO fields), de-duplicates by slug,
and writes into site.contentDir. Maintains a persistent content index
(.geo-cms/content-index.json) and prunes orphans (articles removed from the KB).

Outputs .geo-cms/sync-manifest.json with added/updated/skipped/pruned/conflicts.

Usage:
  python scripts/sync_kb.py --config .geo-cms/config.json [--no-prune]
"""
import argparse
import hashlib
import json
import os
import re
from datetime import date


def load_config(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def parse_frontmatter(text):
    if text.startswith("---"):
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
        if m:
            fm_raw, body = m.group(1), m.group(2)
            fm = {}
            for line in fm_raw.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"').strip("'")
            return fm, body
    return {}, text


def ensure_frontmatter(fm, body, filename):
    if "title" not in fm:
        m = re.search(r"^#\s+(.+)$", body, re.M)
        fm["title"] = (m.group(1).strip() if m else filename)
    if "slug" not in fm:
        fm["slug"] = re.sub(r"\.md$", "", filename)
    if "date" not in fm:
        fm["date"] = str(date.today())
    if "tags" not in fm:
        fm["tags"] = []
    fm.setdefault("summary", "")
    fm.setdefault("faq", [])
    fm.setdefault("geoVerified", False)
    fm.setdefault("source", "kb")
    return fm


def dump_frontmatter(fm, body):
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f'{k}: [{", ".join(v)}]')
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=".geo-cms/config.json")
    ap.add_argument("--no-prune", action="store_true",
                    help="disable orphan pruning (keep stale content/ files)")
    args = ap.parse_args()
    cfg = load_config(args.config)
    cfg_dir = os.path.dirname(os.path.abspath(args.config))
    # repo root = parent of .geo-cms (config lives at <repo>/.geo-cms/config.json);
    # if config is passed at repo root instead, repo_root is its own directory.
    repo_root = os.path.dirname(cfg_dir) if os.path.basename(cfg_dir) == ".geo-cms" else cfg_dir
    content_dir = os.path.join(repo_root, cfg["site"]["contentDir"])
    os.makedirs(content_dir, exist_ok=True)

    # Persistent content index (cross-run registry for incremental diff + prune scope)
    index_path = os.path.join(repo_root, ".geo-cms", "content-index.json")
    index = {"entries": {}}
    if os.path.exists(index_path):
        try:
            index = json.load(open(index_path, encoding="utf-8"))
            index.setdefault("entries", {})
        except Exception:
            index = {"entries": {}}

    manifest = {"added": [], "updated": [], "skipped": [], "pruned": [], "conflicts": []}
    seen = set()
    today = str(date.today())

    # KB round-trip rule: ad-hoc uploads and agent drafts must also live in a
    # managed inbox, so `_upload` is scanned implicitly when present.
    kbs = list(cfg.get("knowledgeBases", []))
    upload_inbox = os.path.join(repo_root, ".geo-cms", "inbox", "_upload")
    if os.path.isdir(upload_inbox) and not any(
            os.path.basename(str(kb.get("inbox", "")).rstrip("/")) == "_upload" for kb in kbs):
        kbs.append({"id": "_upload", "type": "markdown",
                    "inbox": ".geo-cms/inbox/_upload"})

    for kb in kbs:
        inbox = os.path.join(repo_root, kb.get("inbox", f".geo-cms/inbox/{kb['id']}"))
        if not os.path.isdir(inbox):
            continue
        for fn in sorted(os.listdir(inbox)):
            if not fn.endswith(".md"):
                continue
            fp = os.path.join(inbox, fn)
            text = open(fp, encoding="utf-8").read()
            fm, body = parse_frontmatter(text)
            fm = ensure_frontmatter(fm, body, fn)
            fm["source"] = kb["id"]
            slug = fm["slug"]
            seen.add(slug)
            content = dump_frontmatter(fm, body)
            digest = sha256(content)
            target = os.path.join(content_dir, slug + ".md")

            prev = index["entries"].get(slug)
            if os.path.exists(target):
                old = open(target, encoding="utf-8").read()
                if old == content:
                    manifest["skipped"].append(slug)
                else:
                    manifest["updated"].append(slug)
                    # conflict = same slug now sourced from a different KB than before
                    if prev and prev.get("source") != kb["id"]:
                        manifest["conflicts"].append(slug)
            else:
                manifest["added"].append(slug)

            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            index["entries"][slug] = {
                "title": fm.get("title", slug),
                "source": kb["id"],
                "hash": digest,
                "lastSync": today,
                "origin": "kb",
            }

    # Prune orphans: indexed as kb-origin but no longer present in any inbox.
    # Hand-authored (origin != "kb") files are never touched.
    if not args.no_prune:
        for slug in list(index["entries"].keys()):
            meta = index["entries"][slug]
            if meta.get("origin") == "kb" and slug not in seen:
                target = os.path.join(content_dir, slug + ".md")
                if os.path.exists(target):
                    os.remove(target)
                    manifest["pruned"].append(slug)
                del index["entries"][slug]

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    out = os.path.join(repo_root, ".geo-cms", "sync-manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
