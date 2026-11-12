#!/usr/bin/env python3
"""
NFL2 — Strict Line-by-Line Site & Table-Row Verification Gate.

Asserts across ALL HTML files (root *.html and docs/*.html) and ALL data/*.json files:
  1. Every JSON file parses cleanly.
  2. Every local href / src link resolves to a real file in the repository (zero broken links).
  3. Every <table> has matching header vs body cell counts (accounting for colspan).
  4. Every <tbody><tr> row contains at least one <a href="https://..."> link to an approved
     official / authoritative domain (NFL.com, operations.nfl.com, official NFL club sites,
     NIST statistical handbook, NWS weather.gov, or canonical repo/Pages URLs).
  5. No page mislinks Week 10 injuries to REG9.
"""
from __future__ import annotations
import json
import pathlib
import sys
import urllib.parse
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent

OFFICIAL_DOMAINS = {
    "nfl.com",
    "www.nfl.com",
    "operations.nfl.com",
    "static.www.nfl.com",
    "nextgenstats.nfl.com",
    "github.com",
    "kanlerxz87-cyber.github.io",
    "www.itl.nist.gov",
    "www.weather.gov",
    "api.weather.gov",
    # Verified official NFL club domains fetched with HTTP 200:
    "www.azcardinals.com",
    "www.baltimoreravens.com",
    "www.commanders.com",
    "www.dallascowboys.com",
    "www.detroitlions.com",
    "www.49ers.com",
    "www.giants.com",
    "www.miamidolphins.com",
    "www.packers.com",
    "www.patriots.com",
    "www.seahawks.com",
    "www.therams.com",
    "www.clevelandbrowns.com",
}


class PageAuditor(HTMLParser):
    def __init__(self, html_path: pathlib.Path) -> None:
        super().__init__()
        self.path = html_path
        self.local_refs: list[tuple[int, str]] = []
        self.ext_urls: list[tuple[int, str]] = []
        self.tables: list[dict] = []
        self._cur_table: dict | None = None
        self._in_thead = False
        self._in_tbody = False
        self._cur_row: dict | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = dict(attrs)
        line = self.getpos()[0]

        for attr in ("href", "src"):
            val = ad.get(attr)
            if not val:
                continue
            val = val.strip()
            if val.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
                continue
            if val.startswith(("http://", "https://")):
                self.ext_urls.append((line, val))
                if self._cur_row is not None:
                    self._cur_row["links"].append(val)
            else:
                self.local_refs.append((line, val))

        if tag == "table":
            self._cur_table = {"line": line, "head_cols": 0, "body_rows": []}
            self.tables.append(self._cur_table)
        elif tag == "thead":
            self._in_thead = True
        elif tag == "tbody":
            self._in_tbody = True
        elif tag == "tr" and self._cur_table is not None:
            self._cur_row = {"line": line, "cols": 0, "links": [], "in_tbody": self._in_tbody, "in_thead": self._in_thead}
        elif tag in ("th", "td") and self._cur_row is not None:
            try:
                span = int(ad.get("colspan") or "1")
            except ValueError:
                span = 1
            self._cur_row["cols"] += span

    def handle_endtag(self, tag: str) -> None:
        if tag == "thead":
            self._in_thead = False
        elif tag == "tbody":
            self._in_tbody = False
        elif tag == "tr" and self._cur_table is not None and self._cur_row is not None:
            if self._cur_row["in_thead"] and self._cur_table["head_cols"] == 0:
                self._cur_table["head_cols"] = self._cur_row["cols"]
            elif self._cur_row["in_tbody"]:
                self._cur_table["body_rows"].append(self._cur_row)
            self._cur_row = None
        elif tag == "table":
            self._cur_table = None


def has_official_link(urls: list[str]) -> bool:
    for u in urls:
        parsed = urllib.parse.urlparse(u)
        host = parsed.netloc.lower()
        if host in OFFICIAL_DOMAINS:
            return True
    return False


def main() -> None:
    errors: list[str] = []
    total_json = 0
    for jf in sorted((ROOT / "data").glob("*.json")):
        total_json += 1
        try:
            data = json.loads(jf.read_text())
        except Exception as exc:
            errors.append(f"JSON parse error in {jf.relative_to(ROOT)}: {exc}")
            continue
        raw = jf.read_text()
        if "injuries/league/2026/REG9" in raw:
            errors.append(f"{jf.relative_to(ROOT)}: contains wrong Week 10 URL REG9 (should be REG10)")

    html_files = sorted(list(ROOT.glob("*.html")) + list((ROOT / "docs").glob("*.html")))
    total_tables = 0
    total_rows = 0

    for hf in html_files:
        rel = hf.relative_to(ROOT)
        text = hf.read_text()
        if "injuries/league/2026/REG9" in text:
            errors.append(f"{rel}: contains wrong Week 10 URL REG9 (should be REG10)")

        aud = PageAuditor(hf)
        aud.feed(text)

        for line, ref in aud.local_refs:
            clean_ref = ref.split("#", 1)[0].split("?", 1)[0]
            if not clean_ref:
                continue
            target = (hf.parent / clean_ref).resolve()
            if not target.exists():
                errors.append(f"{rel}:{line}: broken local link -> {ref}")

        for tbl in aud.tables:
            total_tables += 1
            hcols = tbl["head_cols"]
            for row in tbl["body_rows"]:
                total_rows += 1
                if hcols > 0 and row["cols"] != hcols:
                    errors.append(
                        f"{rel}:{row['line']}: column count mismatch (row has {row['cols']} cols, thead has {hcols})"
                    )
                if not has_official_link(row["links"]):
                    errors.append(
                        f"{rel}:{row['line']}: table row missing official external source link (found: {row['links']})"
                    )

    if errors:
        print(f"VERIFY FAILED ({len(errors)} issues across {len(html_files)} HTML pages / {total_json} JSON files):")
        for e in errors[:80]:
            print("  -", e)
        if len(errors) > 80:
            print(f"  ... and {len(errors) - 80} more")
        sys.exit(1)

    print(
        f"VERIFY PASSED: {len(html_files)} HTML pages, {total_json} JSON files, "
        f"{total_tables} tables, {total_rows} table rows — 100% row-sourced, 0 broken links, 0 column mismatches."
    )


if __name__ == "__main__":
    main()
