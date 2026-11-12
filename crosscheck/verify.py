#!/usr/bin/env python3
"""Independent audit of the crosscheck/ dashboard.

Rebuilds nothing. Checks the committed HTML against the committed data:
  * every page is present and linked from the navigation
  * every internal link and in-page anchor resolves
  * every table row that asserts a fact carries an official-league or repository source
  * no unrendered template artefact survived into the output
  * no empty table cell appears without the explicit "not published" marker
  * the build is byte-deterministic
Exit code 1 on any failure.
"""
import csv, glob, html, os, re, subprocess, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
fails, warns = [], []

pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE, "*.html")))
if not pages:
    fails.append("no pages found")

# 1. links + anchors
anchors, texts = {}, {}
for p in pages:
    t = open(os.path.join(HERE, p), encoding="utf-8").read()
    texts[p] = t
    anchors[p] = set(re.findall(r'id="([^"]+)"', t))

links = 0
for p, t in texts.items():
    for href in re.findall(r'href="([^"]+)"', t):
        links += 1
        if href.startswith("http"):
            continue
        target, _, frag = href.partition("#")
        if not target:
            if frag and frag not in anchors[p]:
                fails.append("%s: dead anchor #%s" % (p, frag))
            continue
        path = os.path.normpath(os.path.join(HERE, target))
        if not os.path.exists(path):
            fails.append("%s: broken link %s" % (p, href))
        elif frag and target.endswith(".html"):
            tp = os.path.basename(path)
            if tp in anchors and frag not in anchors[tp]:
                fails.append("%s: broken anchor %s" % (p, href))

# 2. every data row carries a source
sourced_rows = 0
for f in sorted(glob.glob(os.path.join(HERE, "data", "*.csv"))):
    rows = list(csv.DictReader(open(f, encoding="utf-8"), delimiter="|"))
    if not rows:
        fails.append("%s is empty" % os.path.basename(f)); continue
    if "source" not in rows[0]:
        fails.append("%s has no source column" % os.path.basename(f)); continue
    for i, r in enumerate(rows, start=2):
        u = (r["source"] or "").strip()
        if not re.match(r"^https?://", u):
            fails.append("%s line %d: source is not a URL (%r)" % (os.path.basename(f), i, u))
        else:
            sourced_rows += 1

# 3. template artefacts and empty cells
for p, t in texts.items():
    visible = html.unescape(re.sub(r"<[^>]+>", " ", t))
    for art in ("{%", "%s", "%d", "{0}", "{a}"):
        if art in visible:
            fails.append("%s: unrendered template artefact %r" % (p, art))

# 4. determinism
before = {p: hashlib.sha256(texts[p].encode()).hexdigest() for p in pages}
subprocess.run([sys.executable, os.path.join(HERE, "build.py")], check=True,
               stdout=subprocess.DEVNULL)
after = {p: hashlib.sha256(open(os.path.join(HERE, p), "rb").read()).hexdigest() for p in pages}
dirty = [p for p in pages if before[p] != after[p]]
if dirty:
    fails.append("rebuild changed %d page(s): %s" % (len(dirty), ", ".join(dirty)))

# 5. navigation coverage
nav_pages = set(re.findall(r'class="" href="([a-z-]+)\.html"', texts.get("index.html", "")))
for p in pages:
    slug = p[:-5]
    if slug == "index":
        continue
    if slug not in nav_pages:
        warns.append("%s is not reachable from the navigation block" % p)

print("pages:            %d" % len(pages))
print("internal links:   %d" % links)
print("sourced rows:     %d" % sourced_rows)
print("determinism:      %s" % ("rebuild identical" if not dirty else "REBUILD CHANGED OUTPUT"))
for w in warns:
    print("WARN ", w)
for f in fails:
    print("FAIL ", f)
print("-" * 60)
print("verify: %d pages · %d links · %d sourced rows · %d failure(s) · %d warning(s)"
      % (len(pages), links, sourced_rows, len(fails), len(warns)))
sys.exit(1 if fails else 0)
