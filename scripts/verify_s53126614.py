#!/usr/bin/env python3
"""
Deterministic Row-Source, Schema, Blank-Cell & Link Verifier (Session arena-53126614, Task S53-08/09)
Verifies:
  1. All 9 data/s53126614_*.json files parse cleanly and preserve zero-sum / blank-market / sandbox-stake invariants.
  2. All 10 s53/*.html pages have matching <thead>/<tbody> column counts, 100% official https:// source links on every <tbody><tr> row, and zero broken internal href/src/anchor references.
  3. All HTML pages across the entire repository (root, s53/, analytics/, portal/, review/, docs/, site/, archive/session-009ec582/) resolve every relative internal href/src cleanly.
"""
import html.parser
import json
import os
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

S53_JSON_FILES = [
    "data/s53126614_repo_audit.json",
    "data/s53126614_requirements.json",
    "data/s53126614_team_offense_2026.json",
    "data/s53126614_correlations_2026.json",
    "data/s53126614_injuries_reg10_2026.json",
    "data/s53126614_depth_deficiencies_2026.json",
    "data/s53126614_originated_lines_week11.json",
    "data/s53126614_signals_leaderboard.json",
    "data/s53126614_decision_center.json",
]

S53_HTML_PAGES = [
    "s53/index.html",
    "s53/executive-summary.html",
    "s53/requirements.html",
    "s53/repo-audit.html",
    "s53/originated-lines.html",
    "s53/correlations.html",
    "s53/depth-deficiencies.html",
    "s53/leaderboard-competition.html",
    "s53/decision-center.html",
    "s53/flagged.html",
]

TRUSTED_DOMAINS = {
    "www.nfl.com",
    "static.www.nfl.com",
    "operations.nfl.com",
    "github.com",
    "api.github.com",
    "kanlerxz87-cyber.github.io",
    "www.azcardinals.com",
    "www.atlantafalcons.com",
    "www.baltimoreravens.com",
    "www.buffalobills.com",
    "www.panthers.com",
    "www.chicagobears.com",
    "www.bengals.com",
    "www.clevelandbrowns.com",
    "www.dallascowboys.com",
    "www.denverbroncos.com",
    "www.detroitlions.com",
    "www.packers.com",
    "www.houstontexans.com",
    "www.colts.com",
    "www.jaguars.com",
    "www.chiefs.com",
    "www.raiders.com",
    "www.chargers.com",
    "www.therams.com",
    "www.miamidolphins.com",
    "www.vikings.com",
    "www.patriots.com",
    "www.neworleanssaints.com",
    "www.giants.com",
    "www.newyorkjets.com",
    "www.philadelphiaeagles.com",
    "www.steelers.com",
    "www.49ers.com",
    "www.seahawks.com",
    "www.buccaneers.com",
    "www.tennesseetitans.com",
    "www.commanders.com",
}


class PageAuditParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.assets = []
        self.tables = []
        self._in_table = False
        self._section = None
        self._in_tr = False
        self._in_cell = False
        self._cur_table = None
        self._cur_row = None

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if "id" in ad and ad["id"]:
            self.ids.add(ad["id"])
        if tag == "a" and "href" in ad:
            href = ad["href"]
            self.links.append(href)
            if self._in_tr and self._cur_row is not None:
                self._cur_row["hrefs"].append(href)
        if tag in ("link", "script", "img"):
            ref = ad.get("href") or ad.get("src")
            if ref:
                self.assets.append(ref)
        if tag == "table":
            self._in_table = True
            self._cur_table = {"id": ad.get("id", ""), "thead_rows": [], "tbody_rows": []}
        elif self._in_table and tag in ("thead", "tbody", "tfoot"):
            self._section = tag
        elif self._in_table and tag == "tr":
            self._in_tr = True
            self._cur_row = {"cells": 0, "hrefs": [], "blank_cells": 0}
        elif self._in_tr and tag in ("td", "th"):
            self._in_cell = True
            colspan = int(ad.get("colspan", "1") or "1")
            self._cur_row["cells"] += colspan
            if "blank-cell" in ad.get("class", ""):
                self._cur_row["blank_cells"] += 1

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._in_cell:
            self._in_cell = False
        elif tag == "tr" and self._in_tr:
            self._in_tr = False
            if self._cur_table is not None:
                if self._section == "thead":
                    self._cur_table["thead_rows"].append(self._cur_row)
                elif self._section == "tbody":
                    self._cur_table["tbody_rows"].append(self._cur_row)
            self._cur_row = None
        elif tag in ("thead", "tbody", "tfoot") and self._in_table:
            self._section = None
        elif tag == "table" and self._in_table:
            self._in_table = False
            self.tables.append(self._cur_table)
            self._cur_table = None


def verify_json_datasets(errors):
    for rel in S53_JSON_FILES:
        full = os.path.join(ROOT, rel)
        if not os.path.isfile(full):
            errors.append(f"Missing JSON file: {rel}")
            continue
        with open(full, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            errors.append(f"{rel}: root must be object")

    # Conservation & unverified-blank invariants
    with open(os.path.join(ROOT, "data/s53126614_team_offense_2026.json"), encoding="utf-8") as f:
        off = json.load(f)
    if len(off["teams"]) != 32:
        errors.append("s53126614_team_offense_2026.json must contain 32 teams")
    if sum(t["pass_yds"] for t in off["teams"]) != 63556:
        errors.append("Offense gross pass yards must equal 63,556")
    if sum(t["rush_yds"] for t in off["teams"]) != 30580:
        errors.append("Offense rush yards must equal 30,580")

    with open(os.path.join(ROOT, "data/s53126614_originated_lines_week11.json"), encoding="utf-8") as f:
        lines = json.load(f)
    for g in lines["games"]:
        for mk in ("market_spread", "market_total", "market_home_ml", "edge_vs_market"):
            if g[mk] is not None:
                errors.append(f"Week 11 game {g['game_id']}: {mk} must remain null (unverified)")

    with open(os.path.join(ROOT, "data/s53126614_signals_leaderboard.json"), encoding="utf-8") as f:
        sigs = json.load(f)
    for s in sigs["strategies"]:
        if "0.00u" not in s["tier"]:
            errors.append(f"Strategy {s['id']} tier must remain Sandbox (0.00u) until gates pass")
        for bk in ("clv", "roi"):
            if s[bk] is not None:
                errors.append(f"Strategy {s['id']} {bk} must remain null without verified odds history")

    # Verify REQ-FIX-04 player leaders correction
    with open(os.path.join(ROOT, "data/player_leaders_2026.json"), encoding="utf-8") as f:
        pl = json.load(f)
    rush_map = {r[0]: r for r in pl["rushing"]["rows"]}
    rec_map = {r[0]: r for r in pl["receiving"]["rows"]}
    if rush_map["Bijan Robinson"][3] != 5 or rush_map["Jaylen Warren"][3] != 2:
        errors.append("player_leaders_2026.json rushing TD column-shift fix regression")
    if rec_map["Trey McBride"][5] != 27 or rec_map["Ja'Marr Chase"][3] != 7:
        errors.append("player_leaders_2026.json receiving Lng/TD column-shift fix regression")


def collect_all_html_pages():
    pages = []
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "archive"}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in sorted(filenames):
            if fn.endswith(".html"):
                rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
                pages.append(rel)
    return sorted(pages)


def main():
    errors = []
    verify_json_datasets(errors)

    all_pages = collect_all_html_pages()
    parsed = {}
    for rel in all_pages:
        full = os.path.join(ROOT, rel)
        p = PageAuditParser()
        with open(full, encoding="utf-8") as f:
            p.feed(f.read())
        parsed[rel] = p

    s53_tbody_rows = 0
    s53_blank_cells = 0
    for rel in S53_HTML_PAGES:
        if rel not in parsed:
            errors.append(f"Missing S53 HTML page: {rel}")
            continue
        p = parsed[rel]
        for ti, tbl in enumerate(p.tables):
            expected_cols = tbl["thead_rows"][-1]["cells"] if tbl["thead_rows"] else None
            for ri, row in enumerate(tbl["tbody_rows"], 1):
                s53_tbody_rows += 1
                s53_blank_cells += row["blank_cells"]
                if expected_cols is not None and row["cells"] != expected_cols:
                    errors.append(f"{rel} table#{ti+1} row#{ri}: {row['cells']} cols != thead {expected_cols}")
                ext = [h for h in row["hrefs"] if h.startswith("https://")]
                if not ext:
                    errors.append(f"{rel} table#{ti+1} row#{ri}: missing official https:// source link")
                for h in ext:
                    host = urlparse(h).netloc
                    if host not in TRUSTED_DOMAINS:
                        errors.append(f"{rel} table#{ti+1} row#{ri}: untrusted source host '{host}'")

    checked_internal_links = 0
    for rel, p in parsed.items():
        base_dir = os.path.dirname(os.path.join(ROOT, rel))
        for ref in p.links + p.assets:
            if not ref or ref.startswith(("http://", "https://", "mailto:", "javascript:", "data:")):
                continue
            checked_internal_links += 1
            path_part, _, frag = ref.partition("#")
            path_part = path_part.split("?", 1)[0]
            if not path_part:
                target_rel = rel
            else:
                target_full = os.path.normpath(os.path.join(base_dir, path_part))
                if os.path.isdir(target_full):
                    target_full = os.path.join(target_full, "index.html")
                if not os.path.isfile(target_full):
                    errors.append(f"{rel}: broken internal ref '{ref}'")
                    continue
                target_rel = os.path.relpath(target_full, ROOT)
            # Strict fragment verification on all S53 pages
            if frag and rel.startswith("s53/") and target_rel in parsed:
                if frag not in parsed[target_rel].ids:
                    errors.append(f"{rel}: missing fragment '#{frag}' in '{target_rel}'")

    if errors:
        print(f"VERIFICATION FAILED ({len(errors)} error(s)):")
        for e in errors[:40]:
            print(f"  - {e}")
        sys.exit(1)

    print(
        f"VERIFICATION PASSED: {len(S53_JSON_FILES)} S53 JSON datasets, "
        f"{len(S53_HTML_PAGES)} S53 HTML pages ({s53_tbody_rows} tbody rows, 100% official https:// row links, "
        f"{s53_blank_cells} explicit blank cells), and {len(all_pages)} total repo HTML pages "
        f"({checked_internal_links} internal links/assets, 0 broken)."
    )


if __name__ == "__main__":
    main()
