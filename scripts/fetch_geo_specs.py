#!/usr/bin/env python3
"""fetch_geo_specs.py - merge real-time GEO/SEO norm findings into the local spec library.

Flow:
  1. agent runs WebSearch and writes findings into .geo-cms/specs/_inbox.md
     using the entry format:  - [GEO-BOT-01] description (source: url; updated: 2026-08-18)
  2. this script parses _inbox.md and merges into topic files (robots/llms/schema/content/technical)
     + manifest.json, de-duplicating by TAG.

Modes:
  --init    first-time baseline (specs/ empty)
  --merge   parallel-phase merge (used during optimization)
  --append  post-optimization increment (only add TAGs not already present)

Usage:
  python scripts/fetch_geo_specs.py --init   --specs-dir .geo-cms/specs
  python scripts/fetch_geo_specs.py --merge  --specs-dir .geo-cms/specs
  python scripts/fetch_geo_specs.py --append --specs-dir .geo-cms/specs
"""
import argparse
import json
import os
import re
from datetime import date

TOPIC_MAP = {
    "GEO-BOT": "robots.md",
    "GEO-LLMS": "llms.md",
    "SCHM": "schema.md",
    "GEO-FAQ": "content.md",
    "GEO-CITE": "content.md",
    "GEO-LOCAL": "content.md",
    "GEO-META": "content.md",
    "GEO-MULTI": "content.md",
    "GEO-TECH": "technical.md",
}

ENTRY_RE = re.compile(
    r"^\s*-\s*\[([A-Z0-9-]+)\]\s*(.+?)\s*"
    r"(?:\(source:\s*(\S+?)\s*;?\s*updated:\s*(\S+?)\))?\s*$",
    re.S,
)


def parse_inbox(path):
    entries = []
    if not os.path.exists(path):
        return entries
    for line in open(path, encoding="utf-8"):
        m = ENTRY_RE.match(line)
        if m:
            tag, desc, src, upd = m.groups()
            entries.append(
                {
                    "tag": tag,
                    "desc": desc.strip(),
                    "source": (src or "").strip(")"),
                    "updated": (upd or str(date.today())).strip(")"),
                }
            )
    return entries


def topic_file(tag):
    for prefix, fn in TOPIC_MAP.items():
        if tag.startswith(prefix):
            return fn
    return "technical.md"


def write_entry(specs, tf, tag, line):
    tpath = os.path.join(specs, tf)
    kept = []
    if os.path.exists(tpath):
        kept = [l for l in open(tpath, encoding="utf-8") if f"[{tag}]" not in l]
    with open(tpath, "w", encoding="utf-8") as f:
        f.writelines(kept)
        f.write(line)


def load_manifest(specs):
    mp = os.path.join(specs, "manifest.json")
    if os.path.exists(mp):
        return json.load(open(mp, encoding="utf-8"))
    return {"entries": {}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs-dir", default=".geo-cms/specs")
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--append", action="store_true")
    args = ap.parse_args()

    specs = os.path.abspath(args.specs_dir)
    os.makedirs(specs, exist_ok=True)
    inbox = os.path.join(specs, "_inbox.md")
    manifest = load_manifest(specs)
    manifest.setdefault("entries", {})
    existing = set(manifest["entries"].keys())

    mode = "append" if args.append else ("init" if args.init else "merge")
    entries = parse_inbox(inbox)
    added, updated, skipped = [], [], []

    for e in entries:
        tf = topic_file(e["tag"])
        line = (
            f'- [{e["tag"]}] {e["desc"]} '
            f'(source: {e["source"] or "n/a"}; updated: {e["updated"]})\n'
        )
        if e["tag"] in existing:
            if mode == "append":
                skipped.append(e["tag"])
                continue
            updated.append(e["tag"])
        else:
            added.append(e["tag"])
        write_entry(specs, tf, e["tag"], line)
        existing.add(e["tag"])
        manifest["entries"][e["tag"]] = {
            "file": tf,
            "updated": e["updated"],
            "source": e["source"],
        }

    manifest["lastRun"] = str(date.today())
    with open(os.path.join(specs, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    if os.path.exists(inbox):
        os.remove(inbox)

    print(
        json.dumps(
            {"mode": mode, "added": added, "updated": updated, "skipped": skipped},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
