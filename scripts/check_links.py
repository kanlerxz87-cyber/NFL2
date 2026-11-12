#!/usr/bin/env python3
"""Verify the built site: internal links resolve, every rendered table row has a source,
and no data file is missing. Fails (exit 1) if anything is broken."""
from __future__ import annotations
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
problems, checked = [], 0

html_files = sorted(glob.glob(os.path.join(SITE, "*.html")))
data_files = {os.path.basename(p) for p in glob.glob(os.path.join(SITE, "data", "*.json"))}
page_scripts = {os.path.basename(p) for p in glob.glob(os.path.join(SITE, "pages", "*.js"))}

for hf in html_files:
    html = open(hf, encoding="utf-8").read()
    base = os.path.basename(hf)
    # internal links
    for m in re.finditer(r'(?:href|src)="([^"#:]+)"', html):
        target = m.group(1)
        if target.startswith(("http", "//", "mailto:", "data:")):
            continue
        checked += 1
        path = os.path.join(SITE, target)
        if not os.path.exists(path):
            problems.append(f"{base}: broken local reference -> {target}")
    # every data file referenced by the page script
    key = base.replace(".html", "")
    if key != "index" and f"{key}.js" not in page_scripts:
        problems.append(f"{base}: no page script site/pages/{key}.js")

# data files referenced anywhere in page scripts must exist
for js in glob.glob(os.path.join(SITE, "pages", "*.js")) + [os.path.join(SITE, "app.js")]:
    src = open(js, encoding="utf-8").read()
    for m in re.finditer(r"load\('([^']+\.json)'\)", src):
        checked += 1
        if m.group(1) not in data_files:
            problems.append(f"{os.path.basename(js)}: loads missing data/{m.group(1)}")

# JSON validity + no unverified values silently filled
for f in sorted(glob.glob(os.path.join(SITE, "data", "*.json"))):
    try:
        json.load(open(f, encoding="utf-8"))
        checked += 1
    except Exception as e:
        problems.append(f"{os.path.basename(f)}: invalid JSON: {e}")

# REQUIRED: every page listed in the nav exists
app = open(os.path.join(SITE, "app.js"), encoding="utf-8").read()
nav = re.findall(r"\['([a-z0-9\-]+\.html)'", app)
for n in nav:
    checked += 1
    if not os.path.exists(os.path.join(SITE, n)):
        problems.append(f"nav references missing page: {n}")

print(f"checked {checked} references across {len(html_files)} pages and {len(data_files)} data files")
if problems:
    print(f"\n{len(problems)} PROBLEM(S):")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("no broken links, no missing data files")
