#!/usr/bin/env python3
"""Regression test for the pagination chain in tools/roster_capture_6eeab460.py (FL-120).

Runs the real run() against a mocked fetch() in a temporary directory. The template is a real stored
official page (25 rows, Next link present). Nothing outside the temp directory is written.

Cases (FL-120: the Aug/Sep cursor interleaves repeated bytes with pages that add rows):
  1. A repeated page with different bytes does NOT stop the chain. The chain reaches a later page that adds
     a row, stores it, and ends at the page with no Next link.
  2. A stuck cursor (same bytes, same Next link) runs to MAX_PAGES, is recorded as INCOMPLETE, is not a run
     failure, and stores only the one distinct page.
  3. Re-running case 2 against its own manifest stores nothing new.
  4. A short page (fewer than 25 rows) ends the chain even when a Next link is present.
"""
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import roster_capture_6eeab460 as rc  # noqa: E402

BASE = "https://www.nfl.com/transactions/league/reserve-list/2026/11"
TEMPLATE = sorted((ROOT / "data" / "captures" / "reserve_list" / "2026-11").glob("*.bin"))[0].read_bytes().decode("utf-8", "replace")
HREF = rc.NEXT_RE.search(TEMPLATE)
NEXT_TEXT = HREF.group(0)
ANCHOR_HREF = HREF.group(1) or HREF.group(2)


def page(next_url, extra=b"", rename=None):
    text = TEMPLATE
    if rename:
        old, new = rename
        assert text.count(old) >= 1
        text = text.replace(old, new, 1)
    if next_url:
        text = text.replace(ANCHOR_HREF, next_url.replace("&", "&amp;"), 1)
    else:
        text = re.sub(rc.NEXT_RE, "", text)
    return text.encode("utf-8") + extra


def setup(tmp, pages, months=(11,)):
    rc.ROOT = Path(tmp)
    rc.CAPTURE_DIR = Path(tmp) / "captures"
    rc.MANIFEST = Path(tmp) / "manifest.csv"
    rc.page_urls = lambda ms: [("reserve_list", 11, BASE)]
    calls = []

    def fake_fetch(url):
        calls.append(url)
        body = pages[url]
        return 200, body, ""
    rc.fetch = fake_fetch
    return calls


def manifest_rows():
    return rc.read_manifest() if rc.MANIFEST.exists() else []


def stored_files():
    return sorted(p.name for p in rc.CAPTURE_DIR.rglob("*.bin")) if rc.CAPTURE_DIR.exists() else []


def main():
    fails = []
    # Pick a player name that appears once in the template, to make page 3 add one row.
    names = re.findall(r'href="/players/[^"]+"[^>]*>([^<]+)<', TEMPLATE)
    target = next(">%s</a>" % n for n in names if TEMPLATE.count(">%s</a>" % n) == 1)
    replacement = ">Zed Testcase</a>"

    n1 = "https://www.nfl.com/transactions/league/reserve-list/2026/11?after=PAGE2"
    n2 = "https://www.nfl.com/transactions/league/reserve-list/2026/11?after=PAGE3"

    # Case 1: page 2 repeats rows with different bytes; page 3 adds a row and has no Next link.
    with tempfile.TemporaryDirectory() as tmp:
        pages = {
            BASE: page(n1),
            n1: page(n2, extra=b"<!-- cursor echo -->"),
            n2: page(None, rename=(target, replacement)),
        }
        calls = setup(tmp, pages)
        rc_code = rc.run([11], dry_run=False)
        rows = manifest_rows()
        if calls != [BASE, n1, n2]:
            fails.append("case 1: chain visited %r, expected all three pages" % calls)
        if rc_code != 0:
            fails.append("case 1: exit code %s, expected 0" % rc_code)
        if [r["page_seq"] for r in rows] != ["1", "2", "3"]:
            fails.append("case 1: manifest page_seq %r" % [r["page_seq"] for r in rows])
        if rows and rows[-1]["stored_path"] == "":
            fails.append("case 1: page 3 added a row but was not stored")
        if len(stored_files()) != 2:
            fails.append("case 1: stored %d files, expected 2 (page 1 and page 3; page 2 adds nothing)" % len(stored_files()))

    # Case 2: stuck cursor. Every page returns page 1's bytes with the same Next link.
    with tempfile.TemporaryDirectory() as tmp:
        pages = {BASE: page(n1), n1: page(n1)}
        calls = setup(tmp, pages)
        rc_code = rc.run([11], dry_run=False)
        rows = manifest_rows()
        if len(calls) != rc.MAX_PAGES:
            fails.append("case 2: chain made %d fetches, expected MAX_PAGES=%d" % (len(calls), rc.MAX_PAGES))
        if rc_code != 0:
            fails.append("case 2: an open chain must not fail the run (exit %s)" % rc_code)
        if len(stored_files()) != 1:
            fails.append("case 2: stored %d files, expected 1" % len(stored_files()))
        if rows and "INCOMPLETE" not in rows[-1]["note"]:
            fails.append("case 2: open-chain note does not say INCOMPLETE: %r" % rows[-1]["note"])

        # Case 3: a second run over the same cursor must store nothing new.
        before = stored_files()
        calls = setup(tmp, pages)
        rc.run([11], dry_run=False)
        if stored_files() != before:
            fails.append("case 3: a rerun stored new bytes for an unchanged cursor")

    # Case 4: a 24-row page with a Next link is the last page of the table.
    short_text = TEMPLATE
    trs = list(rc.ROW_RE.finditer(short_text))
    last = trs[-1]
    short_text = short_text[:last.start()] + short_text[last.end():]
    assert rc.inspect(short_text)["tbody_rows"] == 24, rc.inspect(short_text)["tbody_rows"]
    short_body = short_text.replace(ANCHOR_HREF, n1.replace("&", "&amp;"), 1).encode("utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        calls = setup(tmp, {BASE: short_body, n1: page(None)})
        rc.run([11], dry_run=False)
        if calls != [BASE]:
            fails.append("case 4: short page did not end the chain (visited %r)" % calls)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 4 chain cases (repeat continues; open chain is INCOMPLETE not failed; rerun stores nothing; short page ends)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
