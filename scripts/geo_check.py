#!/usr/bin/env python3
"""geo_check.py - generic static GEO/SEO gap SCAN (bridge fallback helper).

ROLE (geo-cms 1.1.0 boundary): GEO rule authority lives in an EXTERNAL geo-optimize
capability (geo-zh skill / WebSearch). This script is a *generic, subordinate* scanner
used only when that capability is unavailable; it flags presence/absence of common
baseline elements but does NOT define what the rules should be.

Scans for baseline GEO elements on the built output (run after build, before deploy):
  - robots.txt with AI crawlers allowed
  - llms.txt present
  - JSON-LD (application/ld+json) in built HTML
  - <img> alt completeness
  - sitemap.xml present

Usage:
  python scripts/geo_check.py --root . --out out --report .geo-cms/geo-report.json

Exit code: 0 if no P0 failures, 1 otherwise.
"""
import argparse
import json
import os
import re
import sys


def chk(name, level, ok, detail):
    return {"check": name, "level": level, "pass": ok, "detail": detail}


def scan(root, out):
    results = []
    bases = [b for b in (out, root) if b]
    robots = None
    for b in bases:
        p = os.path.join(b, "robots.txt")
        if os.path.exists(p):
            robots = open(p, encoding="utf-8", errors="ignore").read()
            break
    if robots is None:
        results.append(chk("robots.txt 存在", "P0", False, "根目录无 robots.txt"))
    else:
        bots = ["GPTBot", "ClaudeBot", "PerplexityBot", "Baiduspider", "Bytespider", "Applebot"]
        missing = [b for b in bots if b not in robots]
        results.append(
            chk(
                "robots 开放 AI 爬虫",
                "P0",
                len(missing) == 0,
                ("缺: " + ",".join(missing)) if missing else "已覆盖主要 AI 爬虫",
            )
        )

    llms = any(os.path.exists(os.path.join(b, "llms.txt")) for b in bases)
    results.append(chk("llms.txt 存在", "P0", llms, "根目录无 llms.txt" if not llms else "ok"))

    has_ld = False
    if out and os.path.isdir(out):
        for dp, _, fs in os.walk(out):
            for f in fs:
                if f.endswith(".html"):
                    t = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
                    if "application/ld+json" in t:
                        has_ld = True
                        break
            if has_ld:
                break
    results.append(
        chk("JSON-LD 注入", "P0", has_ld, "产物 HTML 未发现 ld+json" if not has_ld else "ok")
    )

    missing_alt = 0
    if out and os.path.isdir(out):
        for dp, _, fs in os.walk(out):
            for f in fs:
                if f.endswith(".html"):
                    t = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
                    for m in re.finditer(r"<img\b[^>]*>", t, re.I):
                        if "alt=" not in m.group(0).lower():
                            missing_alt += 1
    results.append(
        chk("图片 alt 完整", "P1", missing_alt == 0,
            f"发现 {missing_alt} 个 <img> 缺 alt" if missing_alt else "ok")
    )

    sm = any(os.path.exists(os.path.join(b, "sitemap.xml")) for b in bases)
    results.append(chk("sitemap.xml", "P1", sm, "无 sitemap.xml" if not sm else "ok"))
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None)
    ap.add_argument("--report", default=".geo-cms/geo-report.json")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    out = os.path.abspath(args.out) if args.out else None
    results = scan(root, out)
    p0 = [r for r in results if r["level"] == "P0" and not r["pass"]]
    summary = {
        "total": len(results),
        "failed": sum(1 for r in results if not r["pass"]),
        "p0_failed": len(p0),
        "results": results,
    }
    report_dir = os.path.dirname(os.path.abspath(args.report))
    os.makedirs(report_dir, exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    for r in results:
        mark = "OK " if r["pass"] else ("ERR" if r["level"] == "P0" else "WARN")
        print(f"[{mark}] [{r['level']}] {r['check']}: {r['detail']}")
    print(f"\nP0 未通过: {len(p0)}  | 总失败: {summary['failed']}")
    sys.exit(1 if p0 else 0)


if __name__ == "__main__":
    main()
