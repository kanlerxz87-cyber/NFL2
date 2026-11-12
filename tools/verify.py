#!/usr/bin/env python3
"""Line-by-line verification of the combined NFL2 data and site.

Checks:
  * every table row exists in the generated HTML with exactly the recorded cells;
  * every blank cell is genuinely empty;
  * every UNVERIFIED row has at least one blank cell and a flag;
  * every table row has >= 1 link to a fetch-verified official source;
  * every external link uses an allowlisted official domain over HTTPS;
  * every internal link resolves to an existing file (no broken links);
  * every page has identical navigation, a title, language and local assets;
  * table header/row column counts agree.

Exits non-zero on any failure so CI and the integration session cannot merge a broken site.
"""
from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))
import content  # noqa: E402

REGISTRY_PATH = ROOT / "research" / "source-registry.json"
RECORDS_PATH = ROOT / "data" / "records.json"
REPORT_PATH = ROOT / "data" / "verification-report.json"
PAGE_DIR = ROOT / "review"

REG = json.loads(REGISTRY_PATH.read_text())
ALLOWED_DOMAINS = set(REG["official_domains"]) | {"kanlerxz87-cyber.github.io"}
ALLOWED_STATUSES = {"fetch-verified", "local-git-verified"}
VERIFIED_URLS = {s["url"] for s in REG["sources"] if s["status"] in ALLOWED_STATUSES}
SOURCES = content.SOURCES

ERRORS: list[str] = []
STATS = {"pages": 0, "tables": 0, "rows": 0, "blank_cells": 0,
         "unverified_rows": 0, "source_links": 0, "internal_links": 0,
         "external_links": 0, "broken_links": 0}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[dict] = []
        self.th_counts: list[int] = []
        self.all_hrefs: list[str] = []
        self.all_srcs: list[str] = []
        self.has_lang = False
        self.has_title = False
        self.in_title = False
        self.title_text = ""
        self.in_tbody = False
        self.in_thead = False
        self.in_tr = False
        self.in_cell = False
        self.row: dict | None = None
        self.cell: dict | None = None
        self.th_count = 0
        self.tag_stack: list[str] = []
        self.mismatched: list[str] = []
        self.anchor_href: str | None = None

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in self.VOID:
            self.tag_stack.append(tag)
        if tag == "html" and a.get("lang"):
            self.has_lang = True
        if tag == "title":
            self.has_title = True
            self.in_title = True
        if "href" in a:
            self.all_hrefs.append(a["href"])
        if "src" in a:
            self.all_srcs.append(a["src"])
        if tag == "a" and self.in_cell and self.cell is not None and "href" in a:
            self.cell["links"].append(a["href"])
        if tag == "thead":
            self.in_thead = True
            self.th_count = 0
        if tag == "tbody":
            self.in_tbody = True
        if tag == "tr" and self.in_tbody:
            self.in_tr = True
            self.row = {"id": a.get("data-row-id", ""), "status": a.get("data-status", ""),
                        "flags": a.get("data-flags", ""), "cells": []}
        if tag in ("td", "th"):
            self.in_cell = True
            self.cell = {"text": "", "blank": "blank" in (a.get("class") or "").split(),
                         "links": [], "tag": tag}
            if tag == "th" and self.in_thead:
                self.th_count += 1
        if tag == "table":
            self.cur_table_th = 0

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        elif self.tag_stack and tag in self.tag_stack:
            self.mismatched.append(tag)
            while self.tag_stack and self.tag_stack.pop() != tag:
                pass
        if tag == "title":
            self.in_title = False
        if tag in ("td", "th") and self.in_cell:
            if self.row is not None and self.cell is not None and self.cell["tag"] == "td":
                self.row["cells"].append(self.cell)
            self.in_cell = False
            self.cell = None
        if tag == "tr" and self.in_tr:
            if self.row is not None:
                self.rows.append(self.row)
            self.in_tr = False
            self.row = None
        if tag == "thead":
            self.in_thead = False
            self.th_counts.append(self.th_count)
        if tag == "tbody":
            self.in_tbody = False

    def handle_data(self, data):
        if self.in_title:
            self.title_text += data
        if self.in_cell and self.cell is not None:
            self.cell["text"] += data


def parse(path: Path) -> PageParser:
    p = PageParser()
    p.feed(path.read_text(encoding="utf-8"))
    p.close()
    return p


def is_external(href: str) -> bool:
    return href.startswith(("http://", "https://", "//"))


def norm_text(s: str) -> str:
    return " ".join(s.split()).strip()


def main() -> int:
    if not RECORDS_PATH.exists():
        print("FAIL: data/records.json missing — run tools/build_site.py first", file=sys.stderr)
        return 1
    records = json.loads(RECORDS_PATH.read_text())["records"]

    # ---- registry integrity ------------------------------------------------
    for s in REG["sources"]:
        if s["status"] in ALLOWED_STATUSES:
            host = urlparse(s["url"]).hostname or ""
            if host not in ALLOWED_DOMAINS:
                ERRORS.append(f"registry {s['id']}: host not allowlisted: {host}")
            if not s["url"].startswith("https://"):
                ERRORS.append(f"registry {s['id']}: not https")
            if not s.get("excerpt"):
                ERRORS.append(f"registry {s['id']}: no verbatim excerpt recorded")

    used_src = set()
    for r in records:
        for sid in r["src"]:
            used_src.add(sid)
            if sid not in SOURCES:
                ERRORS.append(f"row {r['row_id']}: unknown source id {sid}")
            elif SOURCES[sid]["status"] not in ALLOWED_STATUSES:
                ERRORS.append(f"row {r['row_id']}: source {sid} is not fetch-verified")
        if not r["src"]:
            ERRORS.append(f"row {r['row_id']}: no source id")
        if r["status"] == "unverified":
            STATS["unverified_rows"] += 1
            if not r["blank_indices"]:
                ERRORS.append(f"row {r['row_id']}: UNVERIFIED but has no blank cell")
            if not r["flags"]:
                ERRORS.append(f"row {r['row_id']}: UNVERIFIED but has no flag")

    # ---- required files ----------------------------------------------------
    for f in (".nojekyll", "review/404.html", "review/assets/style.css",
              "review/assets/site.js", ".github/workflows/verify.yml",
              "README.md", "COORDINATION.md", "research/source-registry.json"):
        if not (ROOT / f).exists():
            ERRORS.append(f"required file missing: {f}")

    nav_files = [f for _, items in content.NAV for f, _ in items]
    page_files = [p["file"] for p in content.PAGES]
    for f in nav_files:
        if f not in page_files:
            ERRORS.append(f"navigation points at a missing page: {f}")

    parsed: dict[str, PageParser] = {}

    # ---- per-page checks ---------------------------------------------------
    for page in content.PAGES:
        f = page["file"]
        path = PAGE_DIR / f
        if not path.exists():
            ERRORS.append(f"page missing: {f}")
            continue
        STATS["pages"] += 1
        p = parse(path)
        parsed[f] = p
        if not p.has_lang:
            ERRORS.append(f"{f}: missing <html lang>")
        if not p.has_title or not p.title_text.strip():
            ERRORS.append(f"{f}: missing <title>")
        if p.mismatched:
            ERRORS.append(f"{f}: mismatched HTML tags: {p.mismatched[:5]}")
        if p.tag_stack:
            ERRORS.append(f"{f}: unclosed HTML tags: {p.tag_stack[:5]}")
        if "assets/style.css" not in p.all_hrefs:
            ERRORS.append(f"{f}: missing local stylesheet link")
        if not p.rows:
            ERRORS.append(f"{f}: no table rows")
        STATS["tables"] += len(p.th_counts)
        STATS["rows"] += len(p.rows)

        # column consistency
        for i, n in enumerate(p.th_counts):
            if n == 0:
                ERRORS.append(f"{f}: table {i} has no header cells")
        for row in p.rows:
            if len(row["cells"]) not in p.th_counts:
                ERRORS.append(f"{f}: row {row['id']} has {len(row['cells'])} cells, headers are {p.th_counts}")

        # links
        for href in p.all_hrefs:
            if href in ("", "#") or href.startswith("#"):
                if href in ("", "#"):
                    ERRORS.append(f"{f}: placeholder link {href!r}")
                continue
            if is_external(href):
                STATS["external_links"] += 1
                u = urlparse(href)
                if u.scheme != "https":
                    ERRORS.append(f"{f}: non-https external link {href}")
                if u.hostname not in ALLOWED_DOMAINS:
                    ERRORS.append(f"{f}: non-official external link {href}")
            else:
                STATS["internal_links"] += 1
                target = href.split("#", 1)[0].split("?", 1)[0]
                if target and not (PAGE_DIR / target).exists():
                    STATS["broken_links"] += 1
                    ERRORS.append(f"{f}: broken internal link {href}")
        for src in p.all_srcs:
            if is_external(src):
                ERRORS.append(f"{f}: external script/image {src}")
            elif src.split("#", 1)[0] and not (PAGE_DIR / src).exists():
                ERRORS.append(f"{f}: broken local asset {src}")

        # navigation consistency
        for navf in nav_files:
            if navf not in p.all_hrefs:
                ERRORS.append(f"{f}: navigation missing link to {navf}")

        # every row: official source link
        for row in p.rows:
            all_cell_links = [h for c in row["cells"] for h in c["links"]]
            official = [h for h in all_cell_links if h in VERIFIED_URLS]
            if not official:
                ERRORS.append(f"{f}: row {row['id']} has no official source link")
            else:
                STATS["source_links"] += 1
            for c in row["cells"]:
                if c["blank"]:
                    STATS["blank_cells"] += 1
                    if norm_text(c["text"]) != "":
                        ERRORS.append(f"{f}: row {row['id']} blank cell contains text: {c['text']!r}")

    # ---- line-by-line record vs HTML --------------------------------------
    by_id: dict[str, dict] = {}
    for f, p in parsed.items():
        for row in p.rows:
            if row["id"] in by_id:
                ERRORS.append(f"duplicate row id: {row['id']}")
            by_id[row["id"]] = row

    for rec in records:
        rid = rec["row_id"]
        row = by_id.get(rid)
        if row is None:
            ERRORS.append(f"record {rid} not found in generated HTML")
            continue
        cells = row["cells"][:-1]  # last cell is the appended official-link cell
        if len(cells) != len(rec["cells"]):
            ERRORS.append(f"{rid}: cell count {len(cells)} != record {len(rec['cells'])}")
            continue
        for i, (want, got) in enumerate(zip(rec["cells"], cells)):
            if norm_text(want) != norm_text(got["text"]):
                ERRORS.append(f"{rid}: cell {i} mismatch: {want!r} != {got['text']!r}")
            if i in rec["blank_indices"] and not got["blank"]:
                ERRORS.append(f"{rid}: cell {i} should be blank but is not")
        if row["status"] != rec["status"]:
            ERRORS.append(f"{rid}: status {row['status']} != {rec['status']}")

    if len(by_id) != len(records):
        ERRORS.append(f"rendered row count {len(by_id)} != record count {len(records)}")

    # ---- report ------------------------------------------------------------
    report = {"ok": not ERRORS, "stats": STATS, "errors": ERRORS,
              "sources_used": sorted(used_src), "registry_version": REG["registry_version"]}
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("NFL2 verification report")
    for k, v in STATS.items():
        print(f"  {k:18s}: {v}")
    if ERRORS:
        print(f"\nFAIL: {len(ERRORS)} problem(s):")
        for e in ERRORS[:60]:
            print("  - " + e)
        if len(ERRORS) > 60:
            print(f"  ... and {len(ERRORS) - 60} more (see {REPORT_PATH})")
        return 1
    print("\nOK: all rows, sources, blank cells and links verified. No broken links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
