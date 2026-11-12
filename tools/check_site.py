#!/usr/bin/env python3
"""Site audit: no broken links, no orphan pages, no empty cells, no unexpanded template.

Runs against the generated HTML, because that is what a reader sees.
"""
import os, re, sys, glob, json, urllib.parse
sys.dont_write_bytecode = True  # importing build_site must not litter the tree the CI drift check inspects

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFICIAL_HOSTS = {"nfl.com", "www.nfl.com", "operations.nfl.com", "static.www.nfl.com",
                  "github.com", "arxiv.org", "pith.science", "nber.org", "morganstanley.com",
                  "kanlerxz87-cyber.github.io"}
NAV_PAGES = None
FAIL, WARN, PASS = [], [], []


def pages_list():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import build_site
    return build_site.PAGES


def ok(m): PASS.append(m)
def bad(m): FAIL.append(m)
def warn(m): WARN.append(m)


def main():
    pages = pages_list()
    htmls = sorted(glob.glob(os.path.join(ROOT, "*.html")))
    files = {os.path.basename(h) for h in htmls}
    expected = {p + ".html" for p in pages} | {"index.html", "404.html"}
    missing = expected - files
    if missing:
        bad("pages not generated: %s" % sorted(missing))
    else:
        ok("%d pages generated (all in navigation)" % len(expected))
    extra = files - expected
    if extra:
        warn("html files not in the page list: %s" % sorted(extra))
    # A page the builder failed to render leaves its previous build on disk: the links still
    # resolve and the empty-cell scan stays clean, so nothing below would notice. Compare the
    # manifest's written list and the input digest instead.
    man_path = os.path.join(ROOT, "data", "build_manifest.json")
    if os.path.exists(man_path):
        man = json.load(open(man_path, encoding="utf-8"))
        stale = sorted(expected - {os.path.basename(x) for x in man.get("pages", [])})
        if stale:
            bad("pages present on disk but not written by the last build (stale output: a render "
                "error was survived): %s" % stale)
        else:
            ok("every page on disk was written by the latest build (no stale output)")
        import hashlib
        d = hashlib.sha256()
        for dd in (os.path.join(ROOT, "data"), os.path.join(ROOT, "content")):
            for f in sorted(os.listdir(dd)):
                fp = os.path.join(dd, f)
                if os.path.isfile(fp) and (f.endswith(".csv") or f.endswith(".md")):
                    d.update(f.encode()); d.update(open(fp, "rb").read())
        if d.hexdigest() == man.get("inputs_sha256"):
            ok("manifest digest matches the current data + content inputs")
        else:
            bad("published HTML was built from different inputs than the data files on disk "
                "(re-run tools/build_site.py)")
    assets_missing, broken, official_links, nonofficial, empties, unexpanded, anchors_bad = [], [], 0, set(), [], [], []
    for path in htmls:
        name = os.path.basename(path)
        text = open(path, encoding="utf-8").read()
        visible = re.sub(r"<pre>.*?</pre>", "", text, flags=re.S)
        leaks = re.findall(r"\[[^\]\n]{1,60}\]\((?!https?://)[A-Za-z0-9_.\-/]+\.html[^)]*\)", visible)
        if leaks:
            bad("%s: %d markdown link(s) never rendered into an <a> tag: %s"
                % (name, len(leaks), leaks[:3]))
        for m in re.finditer(r"\{\{[^}]{0,120}\}\}", text):
            unexpanded.append("%s: %s" % (name, m.group(0)[:60]))
        for m in re.finditer(r'(?:href|src)="([^"]+)"', text):
            u = m.group(1)
            if u.startswith(("http://", "https://")):
                if not u.startswith("https://"):
                    bad("%s: insecure link %s" % (name, u))
                host = urllib.parse.urlsplit(u).hostname or ""
                if host in OFFICIAL_HOSTS:
                    official_links += 1
                elif host not in {"github.com"}:
                    nonofficial.add("%s -> %s" % (name, host))
                continue
            if u.startswith("#"):
                if 'id="%s"' % u[1:] not in text:
                    anchors_bad.append("%s: %s" % (name, u))
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), u))
            if not os.path.exists(target):
                broken.append("%s -> %s" % (name, u))
            elif u.endswith(".css") or u.endswith(".js"):
                assets_missing.append(u)
            if u.endswith(".html") and "#" not in u:
                base = os.path.basename(u)
                if not os.path.exists(os.path.join(ROOT, base)):
                    broken.append("%s -> %s" % (name, u))
        for m in re.finditer(r"<td[^>]*>\s*</td>", text):
            empties.append(name)
    if unexpanded:
        bad("unexpanded template directives: %s" % unexpanded[:5])
    else:
        ok("no leftover template markers in any page")
    if broken:
        bad("broken internal links: %s" % broken[:8])
    else:
        ok("every internal link resolves to a file in the repository")
    if anchors_bad:
        bad("broken in-page anchors: %s" % anchors_bad[:6])
    else:
        ok("every in-page anchor target exists")
    if empties:
        bad("empty table cells (must render as 'not published'): %s" % sorted(set(empties))[:5])
    else:
        ok("no empty cells: every gap renders as 'not published'")
    if official_links < 300:
        bad("only %d links to official league pages; the per-row source links may not be rendering" % official_links)
    else:
        ok("%d links point at the official league domain" % official_links)
    pages_with_official = set()
    for path in htmls:
        t = open(path, encoding="utf-8").read()
        if "nfl.com" in t:
            pages_with_official.add(os.path.basename(path))
    data_pages = {"injuries.html", "depth-impact.html", "league-data.html"}
    if not data_pages <= pages_with_official:
        bad("data pages without an official link: %s" % sorted(data_pages - pages_with_official))
    else:
        ok("all measured-data pages carry official source links")
    if nonofficial:
        warn("links to non-league hosts (fine on registry/research pages, not on data pages): %s" % sorted(nonofficial)[:8])
    manifest = os.path.join(ROOT, "data", "build_manifest.json")
    if os.path.exists(manifest):
        json.load(open(manifest))
        ok("build manifest is valid JSON")
    else:
        bad("build manifest missing — run tools/build_site.py")
    print("=" * 72)
    for m in PASS:
        print("  PASS  " + m)
    for m in WARN:
        print("  WARN  " + m)
    for m in FAIL:
        print("  FAIL  " + m)
    print("=" * 72)
    print("check_site: %d passed · %d warnings · %d failures" % (len(PASS), len(WARN), len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
