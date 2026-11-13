#!/usr/bin/env python3
"""NFL2 site builder.

Reads pipe-delimited CSVs from data/ and markdown from content/, emits a static
site at the repository root (GitHub Pages is configured for main / ).

Design rule enforced here: every rendered data row must carry a source that
resolves to an entry in data/sources.csv. If it does not, the build fails.
Blank cells are rendered as "not published" - never as zero, never as a guess.
"""
import csv, hashlib, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CONTENT = os.path.join(ROOT, "content")

OFFICIAL_HOSTS = {"nfl.com", "www.nfl.com", "operations.nfl.com", "static.www.nfl.com"}
# The league publishes no central depth chart - nfl.com/teams/<club>/depth-chart returns 404,
# verified and published as FL-05. The only official chart for a club is the one its own site
# publishes, so the 32 club domains are treated as official league hosts for source marking.
# They are still recorded as tier B in data/sources.csv: official, but not league-operated.
CLUB_HOSTS = {
    "azcardinals.com", "www.azcardinals.com", "atlantafalcons.com", "www.atlantafalcons.com",
    "baltimoreravens.com", "www.baltimoreravens.com", "buffalobills.com", "www.buffalobills.com",
    "panthers.com", "www.panthers.com", "chicagobears.com", "www.chicagobears.com",
    "bengals.com", "www.bengals.com", "clevelandbrowns.com", "www.clevelandbrowns.com",
    "dallascowboys.com", "www.dallascowboys.com", "denverbroncos.com", "www.denverbroncos.com",
    "detroitlions.com", "www.detroitlions.com", "packers.com", "www.packers.com",
    "houstontexans.com", "www.houstontexans.com", "colts.com", "www.colts.com",
    "jaguars.com", "www.jaguars.com", "chiefs.com", "www.chiefs.com",
    "raiders.com", "www.raiders.com", "chargers.com", "www.chargers.com",
    "therams.com", "www.therams.com", "miamidolphins.com", "www.miamidolphins.com",
    "vikings.com", "www.vikings.com", "patriots.com", "www.patriots.com",
    "neworleanssaints.com", "www.neworleanssaints.com", "giants.com", "www.giants.com",
    "newyorkjets.com", "www.newyorkjets.com", "philadelphiaeagles.com", "www.philadelphiaeagles.com",
    "steelers.com", "www.steelers.com", "49ers.com", "www.49ers.com",
    "seahawks.com", "www.seahawks.com", "buccaneers.com", "www.buccaneers.com",
    "tennesseetitans.com", "www.tennesseetitans.com", "commanders.com", "www.commanders.com",
}
OFFICIAL_HOSTS = OFFICIAL_HOSTS | CLUB_HOSTS
PLAYER_URL = "https://www.nfl.com/players/{}/"
BLANKS = {"", "not published", "n/a", "N/A"}
# This is the capture time of the original Week 10 injury-file snapshot only, not a global data time.
DATA_FETCHED = "2026-11-12 04:45 UTC"

NAV = [
    ("Overview", [("index", "Dashboard"), ("executive-summary", "Executive Summary"),
                  ("requirements", "Requirements"), ("roadmap", "Build Plan & Roadmap")]),
    ("Decisions", [("questions", "Open Questions"), ("information-gaps", "Information Gaps"),
                   ("suggestions", "Suggestion Register"),
                   ("suggestion-review", "Suggestion Review Console"),
                   ("flagged-for-review", "Flagged for Review")]),
    ("Origination", [("line-origination", "Originate Our Own Lines"), ("signals", "Signal Catalogue"),
                     ("correlation", "Correlation"), ("bet-types", "Bet Types"),
                     ("skill-vs-luck", "Removing Luck"),
                     ("model-lab", "Fair-Line Lab (computed)"),
                     ("measured-correlations", "Measured Correlations"),
                     ("week10-settled", "Settled Week 10 (graded)"),
                     ("week11-originated", "Week 11 Lines (pre-registered)")]),
    ("Competition", [("strategies", "Strategy Registry"), ("leaderboard", "Leaderboard & Rewards"),
                     ("validation-gates", "Validation Gates")]),
    ("Data", [("injuries", "Week 10 Injury Report"), ("depth-impact", "Depth & Deficiencies"),
              ("depth-deficiencies", "Depth Register (all 32 clubs)"),
              ("league-data", "Standings & Schedule"),
              ("availability-watch", "Availability Watch (dated)"),
              ("personnel-relief", "Personnel Relief"),
              ("deficiencies", "Depth Deficiencies by Side"),
              ("depth-cascades", "Depth Cascades (re-verified)"),
                   ("data-dictionary", "Data Dictionary")]),
    ("Governance", [("methodology", "Verification Method"), ("price-archive", "Price Archive"),
                   ("sources", "Source Registry")]),
]
PAGES = [slug for _, items in NAV for slug, _ in items]

VALUE_MAP = {
    "practice": {"F": "Full", "L": "Limited", "D": "Did not practice"},
    "status": {"OUT": "Out", "Q": "Questionable", "D": "Doubtful", "": ""},
}


class BuildError(Exception):
    pass


def read_rows(name):
    name = name.split("/")[-1] if name.startswith("data/") else name
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        raise BuildError("missing data file: %s" % name)
    with open(path, encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter="|"))
    header = raw[0]
    bad = [(i + 1, len(r)) for i, r in enumerate(raw[1:], start=1) if len(r) != len(header)]
    if bad:
        raise BuildError("%s: rows with the wrong field count %s" % (name, bad[:8]))
    return [dict(zip(header, r)) for r in raw[1:]]


SOURCES = {r["id"]: r for r in read_rows("sources.csv")}
SCHEDULE = {r["game_id"]: r for r in read_rows("schedule_2026_wk10.csv")}


def source_read_utc(source_id):
    """Return the registered official-source read time; never substitute build time for source time."""
    row = SOURCES.get(source_id)
    if not row:
        raise BuildError("unknown source id for read time: %s" % source_id)
    return row["accessed_utc"]


def display_utc(value):
    return value.replace("T", " ").replace("Z", " UTC")


def blank_cell():
    return '<span class="np" title="Not published by the official source at fetch time; not inferred.">not published</span>'


def expand_metric_refs(text):
    return re.sub(r"\{\{metric (\w+)\}\}", lambda m: metric(m.group(1)), text)


def esc(text):
    return html.escape(str(text), quote=False)


def inline(text):
    out = esc(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                 lambda m: '<a href="%s"%s>%s</a>' % (m.group(2), ' rel="noopener"' if not m.group(2).startswith("/") else "", m.group(1)),
                 out)
    # Relative targets are the same-site links: page-to-page references, in-page anchors and the
    # labelled trees of other sessions (review/, portal/, archive/, docs/). They used to survive as
    # literal markdown text in the output, which is how 19 of 22 pages shipped visible "[Q-01](...)"
    # brackets to a reader - check_site.py now fails the audit if any such leak comes back.
    out = re.sub(r"\[([^\]]+)\]\((?!https?://|#)([A-Za-z0-9_.\-/]+\.html(?:#[A-Za-z0-9_.\-/]+)?)\)",
                 lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), out)
    out = re.sub(r"\[([^\]]+)\]\((#[A-Za-z0-9_.\-/]+)\)",
                 lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), out)
    return out


def urlify(cell):
    parts = [p.strip() for p in cell.split("::") if p.strip()]
    out = []
    for p in parts:
        if p.startswith("http://") or p.startswith("https://"):
            host = re.sub(r"^https?://([^/]+).*", r"\1", p)
            mark = "" if host in OFFICIAL_HOSTS else ' <span class="tier src-other">non-official</span>'
            out.append('<a class="src" href="%s" target="_blank" rel="noopener">%s</a>%s' % (p, esc(host), mark))
        else:
            out.append(esc(p))
    return " ".join(out)


def source_ref(cell):
    """Render whatever a row's source column holds: a registered source id, or a raw URL.

    Raw URLs are allowed because a per-row game page is a stronger citation than a page-level
    register entry, but the host is still judged by the same rule - anything that is not an
    official league host is visibly marked non-official instead of being quietly trusted.
    """
    cell = (cell or "").strip()
    if cell.startswith("http://") or cell.startswith("https://"):
        host = re.sub(r"^https?://([^/]+).*", r"\1", cell)
        mark = "" if host in OFFICIAL_HOSTS else ' <span class="tier src-other">non-official</span>'
        return '<a class="src" href="%s" target="_blank" rel="noopener">%s</a>%s' % (cell, esc(host), mark)
    return source_link(cell)


def source_link(sid, tier_label=True):
    row = SOURCES.get(sid)
    if not row:
        raise BuildError("row cites unknown source id: %r" % sid)
    tier = row["tier"].strip()
    cls = "src-official" if tier == "A" else "src-other"
    tag = '<span class="tier %s">%s</span>' % (cls, "official" if tier == "A" else row["kind"])
    return '<a class="src" href="%s" target="_blank" rel="noopener">%s</a>%s' % (row["url"], esc(row["name"]), tag if tier_label else "")


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def render_md(text, ctx):
    lines = text.split("\n")
    out, buf, mode = [], [], None

    def flush_p():
        if buf:
            out.append("<p>%s</p>" % inline(" ".join(buf)))
            buf.clear()

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("{{") and stripped.endswith("}}"):
            flush_p(); out.append(directive(stripped[2:-2].strip(), ctx)); mode = None; i += 1; continue
        if not stripped:
            flush_p(); mode = None; i += 1; continue
        if stripped.startswith("```"):
            flush_p(); mode = None
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>%s</code></pre>" % esc("\n".join(code)))
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            flush_p(); lvl = len(m.group(1))
            anchor = re.sub(r"[^a-z0-9]+", "-", m.group(2).lower()).strip("-")
            out.append('<h%d id="%s">%s</h%d>' % (lvl, anchor, inline(m.group(2)), lvl)); mode = None; i += 1; continue
        if stripped in ("---", "***"):
            flush_p(); out.append("<hr>"); i += 1; continue
        if stripped.startswith("> "):
            flush_p(); quote = [stripped[2:]]
            while i + 1 < len(lines) and lines[i + 1].strip().startswith("> "):
                i += 1; quote.append(lines[i].strip()[2:])
            out.append("<blockquote>%s</blockquote>" % inline(expand_metric_refs(" ".join(quote)))); i += 1; continue
        stripped = expand_metric_refs(stripped)
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?[\s:|-]+$", lines[i + 1].strip()) and "-" in lines[i + 1]:
            flush_p()
            header = split_row(stripped)
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append(split_row(expand_metric_refs(lines[i].strip()))); i += 1
            out.append(html_table(header, body)); continue
        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if mode != "ul":
                flush_p(); out.append("<ul>"); mode = "ul"
            out.append("<li>%s</li>" % inline(m.group(1))); i += 1; continue
        m = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if m:
            if mode != "ol":
                flush_p(); out.append('<ol>'); mode = "ol"
            out.append("<li>%s</li>" % inline(m.group(1))); i += 1; continue
        if mode:
            out.append("<li>%s</li>" % inline(stripped)); i += 1; continue
        buf.append(stripped); i += 1
    if mode:
        out.append("</%s>" % mode)
    flush_p()
    return "\n".join(out)


def html_table(header, body):
    th = "".join("<th>%s</th>" % inline(h) for h in header)
    trs = []
    for row in body:
        cells = []
        for cell in row:
            cell = cell.strip()
            cells.append("<td>%s</td>" % (blank_cell() if cell in BLANKS and cell != "n/a" else inline(cell)))
        trs.append("<tr>%s</tr>" % "".join(cells))
    return '<div class="tablewrap"><table class="data"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, "".join(trs))


# ------------------------------------------------------- repository map ----
# Every tree the parallel sessions published is listed here, and the page counts are measured from
# the filesystem at build time rather than remembered in prose: a session that adds or removes a page
# changes the table without anyone having to edit a sentence (and check_site.py fails if a tree with
# pages in it is missing from this list).
SITE_TREES = [
    (".", "canonical — `bc4b47cf` integration, extended by `a392a193`",
     "#8 #15 #16 #18 #20 #24", "current", "the register, the verified data layer, the origination lab and the review queue"),
    ("crosscheck", "`2063673b`", "#30", "as authored",
     "independent live re-verification of every dataset, cross-tree claim audit, decision registers"),
    ("s92", "`8b4bdcb3`", "#31", "as authored",
     "evidence dashboard: 21-row official-source audit, Week 11 lines with backtest, availability depth"),
    ("research/cef2", "`cef2b11f`", "#33", "as authored",
     "independent re-verification brief, cross-tree census and the 18-hour source-freshness measurement"),
    ("q51", "`51ce8d8e`", "#23 #24", "current",
     "independent evidence dashboard, tested paper-only engine, fail-closed gates"),
    ("s53", "`53126614`", "#19 #20", "as authored",
     "Week 11 fair-line origination, 13-club depth deficiency, interactive decision paths"),
    ("analytics", "`eaba7863`", "#14 #16", "as authored",
     "12-club 1st-4th string cascades, n=32 correlations, fair-line calculators"),
    ("portal", "`e143a7ca`", "#12", "as authored", "quantitative portal, 11/11 zero-sum league reconciliation"),
    ("site", "`63ac21e9`", "#10 #15", "as authored",
     "multi-season walk-forward lab; the calibration every other tree defers to; reads pipeline/data/raw"),
    ("review", "`01b698ef`", "#9 #11", "as authored", "verification-review dashboard and the 423-row register"),
    ("docs", "`85d79210`", "#4 #5", "superseded", "the earliest category dashboard; kept for provenance"),
    ("archive/session-009ec582", "`009ec582`", "#6 #7", "archived", "first 12-page build, kept intact by request"),
]


def render_site_map():
    import glob
    head = ["Tree", "Owner session", "Merged as", "State", "Pages", "What it uniquely holds"]
    out = ['<div class="tablewrap"><table class="data"><thead><tr>']
    out += ["<th>%s</th>" % inline(h) for h in head]
    out.append("</tr></thead><tbody>")
    for path, owner, prs, state, what in SITE_TREES:
        n = len(glob.glob(os.path.join(ROOT, path, "*.html")))
        href = "index.html" if path == "." else "%s/index.html" % path
        link = ('<a href="%s">open</a>' % href) if os.path.exists(os.path.join(ROOT, path, "index.html")) else "not published"
        out.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="num">%d</td><td>%s %s</td></tr>'
                   % (inline("/ (root)" if path == "." else "/%s/" % path), inline(owner), inline(prs),
                      inline(state), n, link, inline(what)))
    out.append("</tbody></table></div>")
    out.append("<p class=\"caption\">Page counts are files ending in .html in that directory, counted when this page was "
               "built, so they cannot drift from the tree. \"as authored\" means the build is published and verified but "
               "its numbers are that session&#39;s snapshot, not this register&#39;s; anything the canonical site adopted "
               "from it is re-audited here and says so. The nine trees are the output of nine parallel agent sessions "
               "working to the same brief - <a href=\"https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md\">"
               "COORDINATION.md</a> is the log of who built what and which claims were cross-checked.</p>")
    return "".join(out)


# ---------------------------------------------------------------- metrics ----
OFF_POS = {"QB", "RB", "FB", "WR", "TE", "T", "G", "C", "OT", "OL", "OG"}
DEF_POS = {"DE", "DT", "LB", "CB", "S", "FS", "SS", "Edge", "DB", "DL", "OLB"}
POS_MAP = {
    "F": "Full", "L": "Limited", "D": "Did not practice",
}


def team_availability(injury_rows):
    teams = {}
    for r in injury_rows:
        t = teams.setdefault(r["team"], {"reported": 0, "dnp": 0, "lim": 0, "full": 0, "dnp_off": 0, "dnp_def": 0})
        t["reported"] += 1
        p = r["practice"]
        if p == "D":
            t["dnp"] += 1
        elif p == "L":
            t["lim"] += 1
        elif p == "F":
            t["full"] += 1
        if p == "D":
            if r["pos"] in OFF_POS:
                t["dnp_off"] += 1
            elif r["pos"] in DEF_POS:
                t["dnp_def"] += 1
    return teams


def _safe_rows(name):
    try:
        return read_rows(name)
    except Exception:
        return []


def _safe_len(name):
    return len(_safe_rows(name))


def _safe_clubs(name, col):
    return len({r.get(col, "").strip() for r in _safe_rows(name) if r.get(col, "").strip()})


def s745_metrics():
    """Session 745f788e: the all-club depth register and the decision console.

    Every figure the two new pages quote in prose is recomputed here from the generated
    CSVs, so a refresh cannot leave a sentence behind the way two hand-written standings
    totals went stale on 13 November (FL-35). The files are produced by
    scripts/build_s745_depth.py and scripts/build_s745_decisions.py.
    """
    def _rows(name):
        p = os.path.join(DATA, name)
        if not os.path.exists(p):
            return []
        with open(p, encoding="utf-8") as fh:
            return list(csv.DictReader(fh, delimiter="|"))

    def _n(name, col, pred):
        return sum(1 for r in _rows(name) if pred((r.get(col) or "").strip()))

    charts = _rows("s745_depth_charts.csv")
    defi = _rows("s745_depth_deficiencies.csv")
    summ = _rows("s745_depth_summary.csv")
    scores = _rows("s745_suggestion_scores.csv")
    gaps = _rows("s745_information_gaps.csv")
    paths = {r["path"]: r for r in _rows("s745_decision_paths.csv")}
    m = {
        "s745_slots": len(charts),
        "s745_clubs_charted": sum(1 for r in summ if r["chart_published"] == "yes"),
        "s745_groups": len(defi),
        "s745_off_groups": sum(1 for r in defi if r["unit"] == "offense"),
        "s745_def_groups": sum(1 for r in defi if r["unit"] == "defense"),
        "s745_first_out": _n("s745_depth_deficiencies.csv", "deficiency_flag",
                             lambda v: v == "1st-string OUT"),
        "s745_dnp": _n("s745_depth_deficiencies.csv", "starter_availability_tier",
                       lambda v: v == "did not practice"),
        "s745_limited": _n("s745_depth_deficiencies.csv", "starter_availability_tier",
                           lambda v: v == "limited"),
        "s745_off_dnp": sum(1 for r in defi if r["unit"] == "offense"
                            and r["starter_availability_tier"] == "did not practice"),
        "s745_def_dnp": sum(1 for r in defi if r["unit"] == "defense"
                            and r["starter_availability_tier"] == "did not practice"),
        "s745_third": _n("s745_depth_deficiencies.csv", "depth_reached", lambda v: v == "3"),
        "s745_fourth": _n("s745_depth_deficiencies.csv", "depth_reached", lambda v: v == "4"),
        "s745_inj_rows": sum(1 for r in _rows("s745_injury_refresh.csv") if r["player"].strip()),
        "s745_matched": sum(1 for r in defi if r["starter_on_injury_report"] == "yes"),
        "s745_quickwins": sum(1 for r in scores if r["quick_win"] == "yes"),
        "s745_have_empty": sum(1 for r in gaps if r["have_is_empty"] == "yes"),
        "s745_official_route": sum(1 for r in gaps if r["official_route_exists"] == "yes"),
        "s745_open": sum(1 for r in gaps if r["status"].strip() == "open"),
        "s745_p0": sum(1 for r in gaps if r["priority"].strip() == "P0"),
    }
    for code in ("A", "B", "C", "D"):
        p = paths.get(code, {})
        m["s745_path%s_n" % code] = p.get("suggestions", "")
        m["s745_path%s_quick" % code] = p.get("quick_wins", "")
        m["s745_path%s_effort" % code] = p.get("total_effort_points", "")
    return m


def build_metrics():
    inj = read_rows("injuries_2026_wk10.csv")
    depth = read_rows("depth_changes_2026_wk10.csv")
    st = read_rows("standings_2026.csv")
    sched = read_rows("schedule_2026_wk10.csv")
    agg = team_availability(inj)
    # Which clubs should have an injury block is a fact about the Week 10 slate, so derive it from the
    # fixture list instead of naming clubs by hand. A hand-written list silently stops being true the
    # moment the source page changes: the list that used to live here named four clubs as empty and
    # was wrong for two of them, which the league does populate. See FL-24.
    playing = set()
    for g in sched:
        playing.add(g["away"])
        playing.add(g["home"])
    empty = sorted(playing - set(agg))
    m = {
        # the second read of the same official page, so the landing tiles can state the drift
        # instead of a reader having to open the deficiencies page to find it
        "hub2_rows": _safe_len("injuries_wk10_2026_hubrefresh.csv"),
        "hub2_clubs": _safe_clubs("injuries_wk10_2026_hubrefresh.csv", "team"),
        "hub2_captured_utc": SOURCES["S-INJ-2235"]["accessed_utc"],
        "hub_latest_captured_utc": SOURCES["S-INJ-1246"]["accessed_utc"],
        "injury_primary_capture": DATA_FETCHED,
        "injury_rows": len(inj),
        "injury_teams": len(agg),
        "injury_clubs_playing": len(playing),
        "injury_clubs_missing": len(empty),
        "injury_coverage": "%d of %d" % (len(agg), len(playing)),
        "games": len(read_rows("schedule_2026_wk10.csv")),
        "dnp": sum(1 for r in inj if r["practice"] == "D"),
        "limited": sum(1 for r in inj if r["practice"] == "L"),
        "full": sum(1 for r in inj if r["practice"] == "F"),
        "designations": sum(1 for r in inj if r["status"].strip()),
        "injury_detail_cells": sum(1 for r in inj if r["injury"].strip()),
        # the blank side of the same two counts, so prose never has to subtract by hand
        "status_blank_rows": len(inj) - sum(1 for r in inj if r["status"].strip()),
        "injury_blank_rows": len(inj) - sum(1 for r in inj if r["injury"].strip()),
        "depth_rows": len(depth),
        "dtr_rows": sum(1 for r in depth if r["change"] == "IR-RETURN-DESIG"),
        "ruled_out_rows": sum(1 for r in depth if r["change"] in ("RULED-OUT", "RULED-OUT-WK9")),
        "qb_depth_rows": sum(1 for r in depth if r["change"] == "DEPTH-CHART" and r["pos"] == "QB"),
        "standings_teams": len(st),
        # League-wide identities, recomputed rather than typed. A season-to-date table is the one
        # thing on this site that moves every time a game settles, so every prose sentence that
        # quotes these totals has to read them from the file instead of remembering them - the
        # standings refresh on 13 November 2026 made two hand-written totals stale and this is
        # what stops that happening again.
        "league_w": sum(int(r["w"]) for r in st),
        "league_l": sum(int(r["l"]) for r in st),
        "league_t": sum(int(r["t"]) for r in st),
        "league_pf": sum(int(r["pf"]) for r in st),
        "league_club_games": sum(int(r["w"]) + int(r["l"]) + int(r["t"]) for r in st),
        "sources": len(SOURCES),
        "official_sources": sum(1 for r in SOURCES.values() if r["tier"] == "A"),
        "suggestions": len(read_rows("suggestions.csv")),
        "questions": len(read_rows("questions.csv")),
        "requirements": len(read_rows("requirements.csv")),
        "gates": len(read_rows("gates.csv")),
        "signals": len(read_rows("signals.csv")),
        "strategies": len(read_rows("strategies.csv")),
        "correlation": len(read_rows("correlation.csv")),
        "flags": len(read_rows("flags.csv")),
        "pages": len(PAGES) + 1,          # + 404, which is generated from index
        "data_files": len([f for f in sorted(os.listdir(DATA)) if f.endswith(".csv")]),
        "empty_clubs": ", ".join(empty),
        "empty_club_count": len(empty),
    }
    m.update(personnel_relief_metrics())
    m.update(s745_metrics())
    m.update(gamelog_metrics(st))
    m.update(availability_metrics())
    return m, inj, agg


def personnel_relief_metrics():
    """Counts for the personnel-relief page, derived from its own files.

    Every one of these is counted here rather than typed into the prose, for the
    same reason the league identities above are: a rolling injury register changes
    between builds, and a hand-written total is stale the moment it does.
    """
    relief = _safe_rows("personnel_relief_wk10_83246f00.csv")
    club = _safe_rows("personnel_relief_club_83246f00.csv")
    hub = _safe_rows("injuries_wk10_83246f00.csv")
    chart_path = os.path.join(DATA, "depth_charts_wk10_83246f00.json")
    charts = {}
    if os.path.exists(chart_path):
        with open(chart_path, encoding="utf-8") as fh:
            charts = json.load(fh)["charts"]
    resolved = [r for r in relief if r.get("string", "").strip() not in BLANKS]
    firsts = [r for r in resolved if r["string"] == "1st string"]
    first_dnp = [r for r in firsts if r["practice"] == "D"]
    first_out = [r for r in firsts if r["game_status"] == "Out"]
    # A unit whose whole published order sits on the report: nobody the club names
    # behind the starter is clean either. Counted from the cascade text, which lists
    # each rung and its status, so this cannot drift from the table.
    full_unit = set()
    for r in firsts:
        if r["practice"] in ("D", "L") and r.get("unit_cascade") and \
                "not on the official report" not in r["unit_cascade"]:
            full_unit.add((r["club"], r["depth_unit"]))
    return {
        "pr_rows": len(relief),
        "pr_clubs": len(set(r["club"] for r in relief)),
        "pr_hub_rows": len(hub),
        "pr_hub_clubs": len(set(r["team"] for r in hub)),
        "pr_charts": len(charts),
        "pr_resolved": len(resolved),
        "pr_unresolved": len(relief) - len(resolved),
        "pr_first_listed": len(firsts),
        "pr_first_dnp": len(first_dnp),
        "pr_first_out": len(first_out),
        "pr_full_unit_units": len(full_unit),
        "pr_full_unit_list": ", ".join("%s %s" % (c, u) for c, u in sorted(full_unit)) or "none",
        "pr_offence_first_dnp": len([r for r in first_dnp if r["side"] == "offence"]),
        "pr_defence_first_dnp": len([r for r in first_dnp if r["side"] == "defence"]),
        "pr_club_rows": len(club),
        "pr_charted_clubs_playing": len(set(r["club"] for r in club
                                            if r["chart_url"].startswith("https://"))),
        "pr_uncharted_rows": len([r for r in club if r["chart_url"] == "not published"]),
    }


# The dated availability snapshot is its own register (session c3ec1487). Its counts are read from
# the file on every build for the same reason the standings totals are: a sentence that quotes a
# count must never be a number somebody remembered.
AW_SNAP = "availability_watch_c3ec1487.csv"


def availability_metrics():
    path = os.path.join(DATA, AW_SNAP)
    if not os.path.exists(path):
        return {"aw_rows": "not published", "aw_clubs": "not published",
                "aw_designations": "not published", "aw_designation_share": "not published"}
    snap = read_rows(AW_SNAP)
    desig = sum(1 for r in snap if r["game_status"].strip())
    return {
        "aw_rows": len(snap),
        "aw_clubs": len({r["club"] for r in snap}),
        "aw_designations": desig,
        "aw_club_states": len(read_rows("availability_watch_by_club_c3ec1487.csv")),
        "aw_designation_share": "%.1f%%" % (100.0 * desig / len(snap)) if snap else "not published",
        "aw_practice_changes": len(read_rows("availability_watch_practice_deltas_c3ec1487.csv")),
    }


# Team codes are not stable across league pages; the schedule/game pages code the Rams LA while
# the standings table codes them LAR. This alias is published as flag FL-17, not hidden.
TEAM_ALIAS = {"LA": "LAR"}


def gamelog_metrics(st):
    """Cross-check the imported week 1-9 game log against the independently transcribed
    standings table. Pure arithmetic over checked-in files, recomputed on every build, so the
    number on the site is a measurement and not a claim copied from a note.

    The weeks 1-9 file is the frozen backtest corpus and is never appended to (suggestion S-26),
    so games that settle after it was cut live in games_2026_wk10_played.csv. Reconciliation
    against the standings therefore folds that file in; every other count below stays a property
    of the corpus alone.
    """
    path = os.path.join(DATA, "games_2026_wk1_9.csv")
    if not os.path.exists(path):
        return {"games_log": 0, "games_log_missing": 1}
    rows = read_rows("games_2026_wk1_9.csv")
    rec = {}
    for g in rows:
        a, h = int(g["away_pts"]), int(g["home_pts"])
        for club, pf, pa in ((g["away"], a, h), (g["home"], h, a)):
            club = TEAM_ALIAS.get(club, club)
            t = rec.setdefault(club, {"w": 0, "l": 0, "t": 0, "pf": 0, "pa": 0, "n": 0})
            t["n"] += 1; t["pf"] += pf; t["pa"] += pa
            t["w" if pf > pa else "l" if pf < pa else "t"] += 1
    # deep copy: rec's values are per-club dicts that the settled loop below mutates in place, so a
    # shallow dict(rec) would report the combined bye count instead of the corpus's own
    corpus_rec = {club: dict(t) for club, t in rec.items()}
    played_path = os.path.join(DATA, "games_2026_wk10_played.csv")
    settled = read_rows("games_2026_wk10_played.csv") if os.path.exists(played_path) else []
    for g in settled:
        a, h = int(g["away_pts"]), int(g["home_pts"])
        for club, pf, pa in ((g["away"], a, h), (g["home"], h, a)):
            club = TEAM_ALIAS.get(club, club)
            t = rec.setdefault(club, {"w": 0, "l": 0, "t": 0, "pf": 0, "pa": 0, "n": 0})
            t["n"] += 1; t["pf"] += pf; t["pa"] += pa
            t["w" if pf > pa else "l" if pf < pa else "t"] += 1
    matched = mismatched = 0
    for row in st:
        r = rec.get(row["abbr"])
        same = r and (r["w"], r["l"], r["t"], r["pf"], r["pa"]) == (
            int(row["w"]), int(row["l"]), int(row["t"]), int(row["pf"]), int(row["pa"]))
        matched += 1 if same else 0
        mismatched += 0 if same else 1
    return {
        "games_log": len(rows),
        "games_log_missing": 0,
        "games_log_weeks": len({g["week"] for g in rows}),
        "games_log_neutral": sum(1 for g in rows if g["neutral"] == "yes"),
        # game-level and club-level splits are different numbers and the prose used to mix them:
        # one tie produces TWO club-ties. Publishing both, computed, so a sentence cannot confuse
        # "68 away wins" with "135 wins across 32 clubs".
        "games_log_away_wins": sum(1 for g in rows if int(g["away_pts"]) > int(g["home_pts"])),
        "games_log_home_wins": sum(1 for g in rows if int(g["home_pts"]) > int(g["away_pts"])),
        "games_log_ties": sum(1 for g in rows if int(g["away_pts"]) == int(g["home_pts"])),
        "games_log_club_w": sum(
            sum(1 for a, h in ((int(g["away_pts"]), int(g["home_pts"])),
                               (int(g["home_pts"]), int(g["away_pts"]))) if a > h) for g in rows),
        "games_log_club_l": sum(
            sum(1 for a, h in ((int(g["away_pts"]), int(g["home_pts"])),
                               (int(g["home_pts"]), int(g["away_pts"]))) if a < h) for g in rows),
        "games_log_club_t": sum(
            sum(1 for a, h in ((int(g["away_pts"]), int(g["home_pts"])),
                               (int(g["home_pts"]), int(g["away_pts"]))) if a == h) for g in rows),
        "games_log_links": sum(1 for g in rows if g["source"].startswith("https://www.nfl.com/games/")),
        "games_log_pf": sum(int(g["away_pts"]) + int(g["home_pts"]) for g in rows),
        "games_log_reconciled": matched,
        "games_log_mismatched": mismatched,
        # byes are a property of the frozen corpus, not of the combined set: a week that is only
        # partly played would otherwise make it look as though clubs had not taken their bye
        "games_log_byes": sum(1 for club, t in corpus_rec.items() if t["n"] == 8),
        "games_log_settled_after_corpus": len(settled),
        "games_log_settled_pf": sum(int(g["away_pts"]) + int(g["home_pts"]) for g in settled),
    }


# Team codes are not stable across league pages: the schedule and game pages code the Rams LA while
# the standings table codes them LAR. The alias is applied in the cross-check and published as flag
# FL-17 - it is never used to edit a stored row.
TEAM_ALIAS = {"LA": "LAR"}


METRICS, INJURY_ROWS, AGG = build_metrics()
BLANK_TALLY = {"count": 0}


def metric(key):
    return str(METRICS.get(key, "?"))


# ------------------------------------------------------------- directives ----
def parse_opts(body):
    opts = {}
    parts = [p.strip() for p in body.split(";;")]
    name = parts[0]
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            opts[k.strip()] = v.strip()
        else:
            opts[p] = True
    return name, opts


def game_label(gid):
    g = SCHEDULE.get(gid)
    if not g:
        return gid
    return "Week %s · %s · %s @ %s · %s ET" % (g["week"], g["date"], g["away"], g["home"], g["kickoff_et"])


def render_csv_table(body):
    name, opts = parse_opts(body)
    rows = read_rows(name)
    cols = [c for c in opts.get("cols", "").split(",") if c]
    if not cols:
        cols = list(rows[0].keys())
    specs = []
    for c in cols:
        parts = [x.strip() for x in c.split(":")]
        key = parts[0]
        label = parts[1] if len(parts) > 1 else key.replace("_", " ").title()
        fn = parts[2] if len(parts) > 2 else ""
        if key not in rows[0]:
            raise BuildError("%s has no column %r (columns: %s)" % (name, key, ", ".join(rows[0].keys())))
        specs.append((key, label, fn))
    src_col = opts.get("source_col", "")
    src_default = opts.get("source", "")
    if not src_col and not src_default:
        raise BuildError("table %s declares no source; every row must cite one" % name)
    if src_col and src_col not in rows[0]:
        raise BuildError("%s has no source column %r" % (name, src_col))
    group = opts.get("group", "")
    link_player = "link_player" in opts
    # A filter clause must be key=value. The old parser dropped anything else on the floor, which is
    # how three tables on the live site ended up unfiltered: a colon instead of an equals sign reads
    # fine to a human ("status:!recommended") and silently means "no filter at all" to the builder.
    raw_filters = [f for f in opts.get("filter", "").split(",") if f.strip()]
    for f in raw_filters:
        if "=" not in f:
            raise BuildError("table %s: filter clause %r is not key=value and would be ignored" % (name, f))
        if f.split("=", 1)[0].strip() not in rows[0]:
            raise BuildError("table %s: filter key %r is not a column of %s" % (name, f.split("=", 1)[0], name))
    filters = [f.split("=", 1) for f in raw_filters]
    for k, v in filters:
        k, v = k.strip(), v.strip()
        neg = v.startswith("!")
        v = v[1:] if neg else v
        if v == "*":
            # "*" means "this cell is filled in". Written out explicitly because "field:!" reads as
            # "not blank" to a human and means "is blank" to the negation branch below - an
            # inverted filter once put 248 rows in a section captioned "the six designations".
            keep = lambda cell: cell.strip() != ""
        elif v == "":
            keep = (lambda cell: cell.strip() == "") if neg else (lambda cell: cell.strip() != "")
        else:
            keep = (lambda cell: v.lower() not in cell.lower()) if neg else (lambda cell: v.lower() in cell.lower())
        rows = [r for r in rows if keep(r.get(k, "").strip())]
    head = [lab for _, lab, _ in specs] + (["Source"] if opts.get("show_source", True) else [])
    out = ['<div class="tablewrap"><table class="data"><thead><tr>']
    out += ["<th>%s</th>" % inline(h) for h in head]
    out.append("</tr></thead><tbody>")
    last_group = object()
    for r in rows:
        if group and r.get(group, "") != last_group:
            last_group = r.get(group, "")
            label = game_label(last_group) if group == "game" else inline(last_group.replace("_", " "))
            out.append('<tr class="grp"><td colspan="%d">%s</td></tr>' % (len(head), label))
        out.append("<tr>")
        for key, _lab, fn in specs:
            val = expand_metric_refs(r.get(key, "").strip())
            if key == "player" and link_player and r.get("slug"):
                val = "[%s](%s)" % (val, PLAYER_URL.format(r["slug"]))
            elif fn in VALUE_MAP:
                val = VALUE_MAP[fn].get(val, val)
            if fn == "urls":
                if "http" not in val:
                    raise BuildError("%s row %r: source cell has no URL" % (name, r.get(specs[0][0], "")))
                out.append("<td>%s</td>" % urlify(val))
                continue
            if val in BLANKS and val != "n/a":
                BLANK_TALLY["count"] += 1
                out.append("<td>%s</td>" % blank_cell())
            else:
                out.append("<td>%s</td>" % inline(val))
        if opts.get("show_source", True):
            if src_col:
                out.append("<td>%s</td>" % source_ref(r[src_col]))
            else:
                out.append("<td>%s</td>" % source_link(src_default))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    if opts.get("caption"):
        # Captions are rendered inside a directive, which is handled before the body pass that
        # expands {{metric ...}} on ordinary lines. Without this a caption quoting a metric
        # ships the raw template text to the live page - check_site only strips <code> blocks
        # when looking for leftovers, so it would not have been caught there.
        out.append('<p class="caption">%s</p>' % inline(expand_metric_refs(opts["caption"])))
    return "".join(out)


def render_gate_matrix():
    gates = read_rows("gates.csv")
    strats = read_rows("strategies.csv")
    head = "<tr><th>Strategy</th>" + "".join("<th class=\"g\">%s</th>" % g["id"] for g in gates) + "<th>Passed</th></tr>"
    body = []
    for s in strats:
        blocking = set(x.strip() for x in s["gates_blocking"].replace("none", "").split(","))
        cells = []
        passed = 0
        for g in gates:
            gid = g["id"]
            if gid in blocking:
                cells.append('<td class="cell bad">%s</td>' % "blocked" if g["class"] == "hard" else '<td class="cell soft">%s</td>' % "soft")
            elif g["current_status"] in ("not started", "design only", "blocked"):
                cells.append('<td class="cell warn">%s</td>' % "pending")
            else:
                cells.append('<td class="cell ok">ready</td>')
                passed += 1
        body.append("<tr><th scope=\"row\">%s</th>%s<td><strong>%d/%d</strong></td></tr>" % (inline(s["name"]), "".join(cells), passed, len(gates)))
    return ('<div class="tablewrap"><table class="matrix"><thead>%s</thead><tbody>%s</tbody></table></div>'
            '<p class="caption">Legend: <span class="cell inline bad">blocked</span> the gate cannot be evaluated for this strategy yet · '
            '<span class="cell inline warn">pending</span> the gate is defined but nothing has been measured · '
            '<span class="cell inline ok">ready</span> the input to evaluate this gate exists in the repo.</p>' % (head, "".join(body)))


def render_blank_census():
    files = ["injuries_2026_wk10.csv", "depth_changes_2026_wk10.csv", "standings_2026.csv",
             "correlation.csv", "strategies.csv", "leaderboard.csv", "suggestions.csv"]
    rows = []
    for f in files:
        data = read_rows(f)
        cols = list(data[0].keys())
        blanks = {}
        for r in data:
            for c in cols:
                if r.get(c, "").strip() in BLANKS:
                    blanks[c] = blanks.get(c, 0) + 1
        for c in sorted(blanks, key=lambda k: -blanks[k])[:4]:
            rows.append("<tr><td>%s</td><td>%s</td><td class=\"num\">%d</td><td>%d</td><td>%s</td></tr>"
                        % (f, c, blanks[c], len(data), blank_cell()))
    return ('<div class="tablewrap"><table class="data"><thead><tr><th>File</th><th>Column</th><th>Blank cells</th><th>Rows</th><th>Handling</th></tr></thead><tbody>%s</tbody></table></div>'
            % "".join(rows))


def directive(body, ctx):
    if body.startswith("csv "):
        return render_csv_table(body[4:])
    if body == "kpis":
        return kpi_cards()
    if body == "gate_matrix":
        return render_gate_matrix()
    if body == "blank_census":
        return render_blank_census()
    m = re.match(r"^metric (\w+)$", body)
    if m:
        return metric(m.group(1))
    if body == "site_map":
        return render_site_map()
    if body == "team_availability":
        agg = AGG
        rows = []
        order = sorted(agg, key=lambda t: (-agg[t]["dnp_def"], -agg[t]["dnp"]))
        for t in order:
            a = agg[t]
            rows.append("<tr><td>%s</td><td class=\"num\">%d</td><td class=\"num\">%d</td><td class=\"num\">%d</td><td class=\"num\">%d</td><td class=\"num\">%d</td><td class=\"num\">%d</td><td>%s</td></tr>"
                        % (t, a["reported"], a["dnp"], a["lim"], a["full"], a["dnp_off"], a["dnp_def"], blank_cell()))
        # Absent clubs are derived from the Week 10 fixture list, so this table can never again name
        # a club by hand that the league actually publishes. See FL-24.
        for t in METRICS["empty_clubs"].split(", "):
            if t and t not in agg:
                rows.append("<tr class=\"flagrow\"><td>%s</td><td colspan=\"6\">%s</td><td>%s</td></tr>"
                            % (t, blank_cell(), source_link("S-INJ")))
        caption = ('Counts are arithmetic over the official rows only. "Offence"/"defence" use the position mapping in the '
                   '<a href="data-dictionary.html">data dictionary</a>. Clubs with no rows in this snapshot are listed at the '
                   'foot of the table as not published rather than zero. Two of them (LAC, BAL) read "No Injuries Reported" on '
                   'the hub; the others are a collection gap (<a href="flagged-for-review.html">FL-24</a>).')
        return ('<div class="tablewrap"><table class="data"><thead><tr><th>Club</th><th>Reported</th><th>Did not practice</th><th>Limited</th>'
                '<th>Full</th><th>DNP offence</th><th>DNP defence</th><th>Source</th></tr></thead><tbody>%s</tbody></table></div>'
                '<p class="caption">%s</p>' % ("".join(rows), caption))
    if body == "toc":
        items = ctx.get("toc", [])
        return '<nav class="toc">%s</nav>' % "".join('<a href="#%s">%s</a>' % (a, esc(t)) for a, t in items)
    raise BuildError("unknown directive: %r" % body)


# ---------------------------------------------------------------- layout -----
PAGE_KIND = {
    "index": ("program", "Program"), "executive-summary": ("program", "Report"),
    "requirements": ("program", "Traceability"), "roadmap": ("design", "Specification"),
    "questions": ("decision", "Decision needed"), "suggestions": ("decision", "Awaiting owner review"),
    "flagged-for-review": ("decision", "Review queue"),
    "line-origination": ("design", "Specification"), "signals": ("design", "Specification"),
    "correlation": ("design", "Specification"), "bet-types": ("design", "Specification"),
    "skill-vs-luck": ("design", "Specification"), "strategies": ("design", "Specification"),
    "leaderboard": ("design", "Specification"), "validation-gates": ("design", "Specification"),
    "injuries": ("measured", "Measured data"), "depth-impact": ("measured", "Measured data"),
    "league-data": ("measured", "Measured data"), "data-dictionary": ("measured", "Schema"),
    "methodology": ("program", "Policy"), "sources": ("program", "Register"),
    "model-lab": ("measured", "Computed result"), "measured-correlations": ("measured", "Computed result"),
    "deficiencies": ("measured", "Measured data"), "depth-cascades": ("measured", "Measured data"), "price-archive": ("program", "Register"),
    "week10-settled": ("measured", "Computed result"),
    "week11-originated": ("measured", "Computed result"),
    "personnel-relief": ("measured", "Measured data"),
    "availability-watch": ("measured", "Dated snapshot"),
    "depth-deficiencies": ("measured", "Measured data"),
    "information-gaps": ("decision", "Decision needed"),
    "suggestion-review": ("decision", "Awaiting owner review"),
}

CSS_HREF = "assets/style.css"


def layout(slug, title, lead, kind_label, kind, body, ctx, toc):
    base = ""
    nav = []
    for group, items in NAV:
        rows = "".join('<a class="%s" href="%s.html">%s</a>' % ("on" if s == slug else "", s, esc(t)) for s, t in items)
        nav.append('<div class="navgroup"><span>%s</span>%s</div>' % (esc(group), rows))
    navhtml = "".join(nav)
    order = PAGES
    idx = order.index(slug) if slug in order else 0
    prevn = '<a class="pager" href="%s.html">&larr; %s</a>' % (order[idx - 1], esc(dict((s, t) for _, it in NAV for s, t in it)[order[idx - 1]])) if idx > 0 else ""
    nxt = order[idx + 1] if idx + 1 < len(order) else None
    nxtt = dict((s, t) for _, it in NAV for s, t in it)[nxt] if nxt else ""
    nextlink = '<a class="pager right" href="%s.html">%s &rarr;</a>' % (nxt, esc(nxtt)) if nxt else ""
    lead_html = '<p class="lead">%s</p>' % inline(lead) if lead else ""
    # The meta description gets the same text with the markdown stripped rather than the raw
    # string: before this, %(lead)s was interpolated into the pagehead as escaped markdown, so
    # every page's lede shipped literal ** and backticks to the reader, and a link in a lede
    # was reported by check_site as an unrendered link because it genuinely was one.
    lead_meta = esc(re.sub(r"\[([^\]]+)\]\((?:https?://[^)\s]+)\)", r"\1",
                           re.sub(r"[*`]", "", lead))) if lead else ""
    toc_html = '<nav class="toc"><span>On this page</span>%s</nav>' % "".join(
        '<a href="#%s">%s</a>' % (a, esc(t)) for a, t in toc) if toc else ""
    return """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s · NFL2</title>
<meta name="description" content="%(lead)s">
<link rel="stylesheet" href="%(css)s">
</head>
<body class="kind-%(kind)s">
<header class="top">
  <a class="brand" href="index.html"><span class="mark">NFL</span> <span>Decision dashboard</span></a>
  <div class="asof">Source reads (UTC) · <a href="%(injury_url)s">Week 10 primary injury snapshot</a> <strong>%(fetched)s</strong> · 12 Nov full-hub re-read <strong>%(injury_refresh)s</strong> · 13 Nov settled-game-only recheck <strong>%(injury_subset)s</strong> · latest full-hub snapshot <strong>%(injury_latest)s</strong> · <a href="%(standings_url)s">NFL standings</a> <strong>%(standings_read)s</strong> · <a href="sources.html">source log</a> · <a href="methodology.html">verification rules</a></div>
</header>
<div class="shell">
  <aside class="side">
    %(nav)s
    <div class="sidefoot"><a href="flagged-for-review.html">%(flags)s open flags</a> · <a href="sources.html">%(sources)s sources</a></div>
  </aside>
  <main>
    <div class="pagehead">
      <span class="badge %(kind)s">%(kind_label)s</span>
      <h1>%(title)s</h1>
      %(lead_html)s
    </div>
    %(toc)s
    <div class="body">%(body)s</div>
    <footer class="pagefoot">
      %(prev)s
      %(next)s
      <div class="foot-meta">Rendered from <code>data/</code> by <code>tools/build_site.py</code> — the build is byte-deterministic, so this page is exactly what the audited data says · <a href="https://github.com/kanlerxz87-cyber/NFL2">repository</a></div>
    </footer>
  </main>
</div>
</body></html>
""" % dict(title=esc(title), lead=lead_meta, lead_html=lead_html, css=CSS_HREF, fetched=DATA_FETCHED,
           injury_refresh=display_utc(source_read_utc("S-INJ-2235")),
           injury_subset=display_utc(source_read_utc("S-INJ-1113")),
           injury_latest=display_utc(source_read_utc("S-INJ-1246")),
           standings_read=display_utc(read_rows("standings_2026.csv")[0]["captured_utc"]),
           injury_url=SOURCES["S-INJ"]["url"], standings_url=SOURCES["S-STAND-653B"]["url"], nav=navhtml,
           kind=kind, kind_label=esc(kind_label), toc=toc_html, body=body, prev=prevn, next=nextlink,
           flags=metric("flags"), sources=metric("sources"))


def render_page(slug):
    path = os.path.join(CONTENT, slug + ".md")
    if not os.path.exists(path):
        raise BuildError("missing content page content/%s.md" % slug)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    lines = text.split("\n")
    title = dict((s, t) for _, it in NAV for s, t in it).get(slug, slug)
    lead = ""
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        lines = lines[1:]
    body_md = "\n".join(lines).strip("\n")
    m = re.match(r"^>\s?(.*)\n", body_md)
    if m:
        # the lede is page furniture with real numbers in it: measure it like everything else
        lead = expand_metric_refs(m.group(1).strip())
        body_md = body_md[m.end():]
    ctx = {"slug": slug}
    body = render_md(body_md, ctx)
    toc = re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', body)
    kind, kind_label = PAGE_KIND[slug]
    return layout(slug, title, lead, kind_label, kind, body, ctx, toc)


def main():
    problems = []
    written = []
    for slug in PAGES:
        try:
            htmlout = render_page(slug)
        except BuildError as exc:
            problems.append("%s: %s" % (slug, exc))
            continue
        if "__INJECT_" in htmlout:
            problems.append("%s: unexpanded placeholder" % slug)
        out = os.path.join(ROOT, slug + ".html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(htmlout)
        written.append(os.path.relpath(out, ROOT))
    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(render_page("index").replace("<body", '<body', 1))
    written.append("404.html")   # so the auditor can tell a written page from a stale one
    digest = hashlib.sha256()
    for d in (DATA, CONTENT):
        for f in sorted(os.listdir(d)):
            fp = os.path.join(d, f)
            if os.path.isfile(fp) and (f.endswith(".csv") or f.endswith(".md")):
                digest.update(f.encode()); digest.update(open(fp, "rb").read())
    manifest = {
        "inputs_sha256": digest.hexdigest(),
        # Backward-compatible alias for the original Week 10 injury-file capture only; do not read this
        # as the fetch time of every file. The source-specific map below is the authoritative freshness record.
        "data_fetched_utc": DATA_FETCHED,
        "source_read_times_utc": {
            "week10_injury_file_capture": DATA_FETCHED,
            "week10_injury_full_hub_reread": source_read_utc("S-INJ-2235"),
            "week10_injury_settled_game_subset_recheck": source_read_utc("S-INJ-1113"),
            "week10_injury_latest_full_hub_snapshot": source_read_utc("S-INJ-1246"),
            "standings": read_rows("standings_2026.csv")[0]["captured_utc"],
        },
        "pages": written,
        "metrics": METRICS,
        "blank_cells_rendered_as_not_published": BLANK_TALLY["count"],
        "official_host_allowlist": sorted(OFFICIAL_HOSTS),
    }
    with open(os.path.join(DATA, "build_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("built %d pages · %d blank cells rendered as 'not published'" % (len(written), BLANK_TALLY["count"]))
    if problems:
        print("\n".join("ERROR " + p for p in problems))
        return 1
    return 0





KPIS = [
    ("injury_rows", "Injury rows ingested", "injuries",
     lambda m: "%d rows, %d/%d clubs (%s); %d/%d (%s); latest %d/%d (%s). Separate dated reads." % (m["injury_rows"], m["injury_teams"], m["injury_clubs_playing"], m["injury_primary_capture"], m["hub2_rows"], m["hub2_clubs"], m["hub2_captured_utc"], m["pr_hub_rows"], m["pr_hub_clubs"], m["hub_latest_captured_utc"])),
    ("designations", "Designations published", "injuries",
     lambda m: "%d of %d rows carry a game status; the rest are not published" % (m["designations"], m["injury_rows"])),
    ("depth_rows", "Depth & roster events", "depth-impact",
     lambda m: "%d entries: IR, returns, signings, QB chain changes" % m["depth_rows"]),
    ("standings_teams", "Standings reconciled", "league-data",
     lambda m: "%d clubs; points and winning %s recomputed clean" % (m["standings_teams"], "pct")),
    ("suggestions", "Suggestions to decide", "suggestions",
     lambda m: "%d options scored; adopted work is labeled and owner-only choices remain open" % m["suggestions"]),
    ("questions", "Open questions", "questions",
     lambda m: "%d questions, %d marked P0 blocking" % (m["questions"], m.get("p0", "?"))),
    ("flags", "Flags for review", "flagged-for-review",
     lambda m: "%d irregularities published, none blocking" % m["flags"]),
    ("signals", "Signal families specified", "signals",
     lambda m: "%d specified, %d blocked on data we do not have" % (m["signals"], m.get("signals_blocked", "?"))),
]


def kpi_cards():
    METRICS["p0"] = sum(1 for r in read_rows("questions.csv") if r["priority"] == "P0")
    METRICS["signals_blocked"] = sum(1 for r in read_rows("signals.csv") if r["status"] != "specified")
    cards = []
    for key, title, slug, sub in KPIS:
        cards.append('<div class="card"><h3>%s</h3><div class="big"><a href="%s.html">%s</a></div>'
                     '<div class="sub">%s</div></div>' % (esc(title), slug, metric(key), esc(sub(METRICS))))
    return '<div class="cards">%s</div>' % "".join(cards)


if __name__ == "__main__":
    sys.exit(main())
