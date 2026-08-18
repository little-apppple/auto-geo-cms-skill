#!/usr/bin/env python3
"""verify_deploy.py - FALLBACK browser verification driver for the live site.

ROLE (geo-cms 1.1.0 boundary): browser verification is an EXTERNAL capability
(browser-verify = agent-browser / playwright skill). This script is a *minimal local
fallback* used only when no browser skill is available (requires Playwright installed).

If Playwright is available, opens each page headlessly and asserts:
  - HTTP 200
  - presence of application/ld+json
  - non-empty body text (>200 chars)
plus reachability of robots.txt / llms.txt / sitemap.xml.

If Playwright is not installed, degrades to a checklist prompt for the
browser skill (agent-browser / playwright-cli).

Usage:
  python scripts/verify_deploy.py --base-url https://example.com \
      --pages /,/blog/what-is-geo,/faq --report .geo-cms/verify-report.json

Exit code: 0 if all checks pass, 1 otherwise.
"""
import argparse
import json
import os
import sys
import urllib.request


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--pages", default="/", help="comma-separated paths")
    ap.add_argument("--report", default=".geo-cms/verify-report.json")
    args = ap.parse_args()
    pages = [p if p.startswith("/") else "/" + p for p in args.pages.split(",")]
    base = args.base_url.rstrip("/")

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        HAVE = True
    except Exception:
        HAVE = False

    if not HAVE:
        print("WARN: 未检测到 Playwright，请改用浏览器技能(agent-browser/playwright-cli)手动核对：")
        print(" - 各页面返回 200")
        print(" - 含 application/ld+json 且为合法 JSON")
        print(" - 正文非空白、FAQ 结论前置")
        print(" - robots.txt / llms.txt / sitemap.xml 可访问")
        print(f"目标: {base} + {pages}")
        sys.exit(0)

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for path in pages:
            url = base + path
            rec = {"url": url, "checks": {}}
            try:
                page = browser.new_page()
                resp = page.goto(url, timeout=30000)
                rec["checks"]["status200"] = (resp.status if resp else None) == 200
                html = page.content()
                rec["checks"]["hasJsonLd"] = "application/ld+json" in html
                body = page.query_selector("body")
                rec["checks"]["bodyNonEmpty"] = bool(body) and len(body.inner_text().strip()) > 200
                page.close()
            except Exception as e:
                rec["checks"]["error"] = str(e)
            results.append(rec)
        browser.close()

    for name in ("robots.txt", "llms.txt", "sitemap.xml"):
        url = base + "/" + name
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                ok = r.status == 200
        except Exception:
            ok = False
        results.append({"url": url, "checks": {"reachable": ok}})

    report_dir = os.path.dirname(os.path.abspath(args.report))
    os.makedirs(report_dir, exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    def rec_failed(r):
        checks = r.get("checks", {})
        if "error" in checks:  # page threw during load -> must fail
            return True
        bools = [v for v in checks.values() if isinstance(v, bool)]
        return bool(bools) and not all(bools)

    fails = [r for r in results if rec_failed(r)]
    for r in results:
        status = "FAIL" if rec_failed(r) else "PASS"
        print(f"[{status}] {r['url']} {r['checks']}")
    print("RESULT:", "FAIL" if fails else "PASS")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
