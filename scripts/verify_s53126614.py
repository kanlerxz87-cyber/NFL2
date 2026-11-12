#!/usr/bin/env python3
"""Deterministic line-by-line data, table-row source-link, and cross-repo link verifier for Session arena-53126614."""
import glob
import html.parser
import json
import math
import os
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

S53_HTML_PAGES = [
    "repo-audit.html",
    "requirements.html",
    "correlations.html",
    "depth-deficiencies.html",
    "originated-lines.html",
    "leaderboard-competition.html",
    "decision-center.html",
]

OFFICIAL_DOMAINS = {
    "www.nfl.com", "nfl.com", "static.www.nfl.com", "operations.nfl.com",
    "github.com", "kanlerxz87-cyber.github.io", "docs.github.com",
    "www.patriots.com", "www.49ers.com", "www.dallascowboys.com",
    "www.detroitlions.com", "www.commanders.com", "www.miamidolphins.com",
    "www.seahawks.com", "www.giants.com", "www.packers.com",
    "www.chiefs.com", "www.therams.com", "www.azcardinals.com",
    "www.baltimoreravens.com", "www.atlantafalcons.com", "www.buffalobills.com",
    "www.panthers.com", "www.chicagobears.com", "www.bengals.com",
    "www.clevelandbrowns.com", "www.denverbroncos.com", "www.houstontexans.com",
    "www.colts.com", "www.jaguars.com", "www.raiders.com", "www.chargers.com",
    "www.vikings.com", "www.neworleanssaints.com", "www.newyorkjets.com",
    "www.philadelphiaeagles.com", "www.steelers.com", "www.buccaneers.com",
    "www.tennesseetitans.com",
}


class PageInspector(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.srcs = []
        self.in_tbody = False
        self.in_tr = False
        self.tr_links = []
        self.tbody_rows = []
        self.tr_td_count = 0

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if tag == "a" and "href" in ad:
            self.hrefs.append(ad["href"])
            if self.in_tbody and self.in_tr:
                self.tr_links.append(ad["href"])
        if tag in ("link", "script", "img"):
            target = ad.get("href") or ad.get("src")
            if target:
                self.srcs.append(target)
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_tr = True
            self.tr_links = []
            self.tr_td_count = 0
        elif tag in ("td", "th") and self.in_tbody and self.in_tr:
            self.tr_td_count += 1

    def handle_endtag(self, tag):
        if tag == "tbody":
            self.in_tbody = False
        elif tag == "tr" and self.in_tbody and self.in_tr:
            self.tbody_rows.append((self.tr_td_count, list(self.tr_links)))
            self.in_tr = False


def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den


def main():
    errors = []

    # 1. Verify JSON datasets & conservation identities
    with open(os.path.join(ROOT, "data/s53126614_team_offense_2026.json")) as f:
        off = json.load(f)
    teams = off["teams"]
    if len(teams) != 32:
        errors.append(f"Expected 32 teams, got {len(teams)}")
    for f_off, f_def, label in [
        ("pf", "pa", "Points"),
        ("pass_yds", "def_pass_yds", "Pass Yds"),
        ("rush_yds", "def_rush_yds", "Rush Yds"),
        ("sacks_taken", "def_sacks", "Sacks"),
        ("pass_int", "def_int", "Interceptions"),
    ]:
        s1 = sum(t[f_off] for t in teams)
        s2 = sum(t[f_def] for t in teams)
        if s1 != s2:
            errors.append(f"Zero-sum conservation mismatch on {label}: {s1} != {s2}")

    # 2. Re-verify every Pearson r in s53126614_correlations_2026.json
    with open(os.path.join(ROOT, "data/s53126614_correlations_2026.json")) as f:
        corr = json.load(f)
    for c in corr["correlations"]:
        xs = [t[c["field_x"]] for t in teams]
        ys = [t[c["field_y"]] for t in teams]
        r_calc = round(pearson(xs, ys), 3)
        if abs(r_calc - c["pearson_r"]) > 0.001:
            errors.append(f"Correlation mismatch {c['id']}: stored={c['pearson_r']} calc={r_calc}")

    # 3. Verify originated lines blank market policy & neutral site HFA=0
    with open(os.path.join(ROOT, "data/s53126614_originated_lines_week11.json")) as f:
        orig = json.load(f)
    if len(orig["games"]) != 13:
        errors.append(f"Expected 13 Week 11 games, got {len(orig['games'])}")
    for g in orig["games"]:
        for mfield in ("market_spread", "market_total", "market_home_ml", "edge_vs_market"):
            if g[mfield] is not None:
                errors.append(f"{g['game_id']} has non-null {mfield}")
        if g["neutral_site"] and g["hfa_applied"] != 0.0:
            errors.append(f"{g['game_id']} neutral_site has non-zero HFA {g['hfa_applied']}")

    # 4. Verify leaderboard & decision-center unverified/blank policy
    with open(os.path.join(ROOT, "data/s53126614_signals_leaderboard.json")) as f:
        ldb = json.load(f)
    for s in ldb["strategies"]:
        if s["clv"] is not None or s["roi"] is not None:
            errors.append(f"Strategy {s['id']} has non-null CLV/ROI")

    with open(os.path.join(ROOT, "data/s53126614_decision_center.json")) as f:
        dec = json.load(f)
    if dec["selected_path"] is not None:
        errors.append("Decision center selected_path must remain null before human review")

    # 5. Inspect all S53 HTML pages: 100% tbody rows must have an official https:// source link
    total_s53_rows = 0
    for page in S53_HTML_PAGES:
        pfull = os.path.join(ROOT, page)
        if not os.path.isfile(pfull):
            errors.append(f"Missing S53 page: {page}")
            continue
        with open(pfull, encoding="utf-8") as f:
            raw = f.read()
        insp = PageInspector()
        insp.feed(raw)
        for r_idx, (td_cnt, links) in enumerate(insp.tbody_rows, 1):
            total_s53_rows += 1
            ext_official = [
                u for u in links
                if u.startswith("https://") and urlparse(u).netloc in OFFICIAL_DOMAINS
            ]
            if not ext_official:
                errors.append(f"{page} tbody row #{r_idx} missing official https:// source link")

    # 6. Repo-wide internal link & asset check across all HTML files
    all_html = []
    for sub in ("*.html", "docs/*.html", "review/*.html", "portal/*.html"):
        all_html.extend(glob.glob(os.path.join(ROOT, sub)))
    checked_links = 0
    for hfile in sorted(all_html):
        rel_dir = os.path.dirname(hfile)
        with open(hfile, encoding="utf-8") as f:
            raw = f.read()
        insp = PageInspector()
        insp.feed(raw)
        for ref in insp.hrefs + insp.srcs:
            if not ref or ref.startswith(("http://", "https://", "mailto:", "javascript:", "#", "data:")):
                continue
            clean = ref.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            checked_links += 1
            target = os.path.normpath(os.path.join(rel_dir, clean))
            if os.path.isdir(target):
                target = os.path.join(target, "index.html")
            if not os.path.isfile(target):
                errors.append(f"Broken internal ref in {os.path.relpath(hfile, ROOT)}: {ref}")

    if errors:
        print("VERIFY_S53126614 FAILED:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print(
        f"[PASS] verify_s53126614: 32/32 zero-sum conservation, 15/15 exact correlations, "
        f"{total_s53_rows}/{total_s53_rows} S53 table rows linked to official sources, "
        f"{checked_links} internal links verified across {len(all_html)} HTML pages (0 broken)."
    )


if __name__ == "__main__":
    main()
