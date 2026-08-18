#!/usr/bin/env python3
"""sync_kb.py - normalize KB exports in inbox and merge into the repo content dir.

Reads .geo-cms/config.json, for each knowledgeBase reads its inbox/*.md,
normalizes frontmatter (title/date/slug/tags + GEO fields), de-duplicates by slug,
and writes into site.contentDir. Prints a JSON manifest of added/updated/skipped.

Usage:
  python scripts/sync_kb.py --config .geo-cms/config.json
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=".geo-cms/config.json")
    args = ap.parse_args()
    cfg = load_config(args.config)
    root = os.path.dirname(os.path.abspath(args.config))
    content_dir = os.path.join(root, cfg["site"]["contentDir"])
    os.makedirs(content_dir, exist_ok=True)

    manifest = {"added": [], "updated": [], "skipped": [], "conflicts": []}

    for kb in cfg.get("knowledgeBases", []):
        inbox = os.path.join(root, kb.get("inbox", f".geo-cms/inbox/{kb['id']}"))
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
            target = os.path.join(content_dir, slug + ".md")
            content = dump_frontmatter(fm, body)
            if os.path.exists(target):
                old = open(target, encoding="utf-8").read()
                if old == content:
                    manifest["skipped"].append(slug)
                    continue
                manifest["updated"].append(slug)
                manifest["conflicts"].append(slug)
            else:
                manifest["added"].append(slug)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)

    out = os.path.join(root, ".geo-cms", "sync-manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
