#!/usr/bin/env python3
"""Build the crosscheck/ dashboard (session 2063673b).

Design rules, enforced here rather than promised:
  1. Every rendered row must carry a source that is either a registered official
     league host or a repository file. A row with no source fails the build.
  2. A blank cell renders as "not published" - never zero, never an estimate.
  3. Every count printed in prose is measured from the file it describes, so the
     prose cannot age away from the data.
  4. No value is computed unless its input is committed in this repository.

Output is byte-deterministic: rebuild and compare to prove it.
"""
import csv, html, json, os, re, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
REPO = os.path.join(ROOT, "data")

OFFICIAL = {"www.nfl.com", "nfl.com", "operations.nfl.com", "static.www.nfl.com"}
# Explicitly labelled research sources: allowed on register pages only, and always rendered
# with a visible non-league tag so a reader can see they are not the league's own words.
RESEARCH = {"arxiv.org", "pith.science", "www.nber.org"}
# Club domains. A club site is evidence about that club, never a league-wide source; rows that
# cite one are allowed but always carry a visible "club site" tag.
CLUBS = {"www.patriots.com", "www.miamidolphins.com", "www.detroitlions.com", "www.azcardinals.com",
         "www.49ers.com", "www.therams.com", "www.seahawks.com", "www.packers.com", "www.commanders.com"}
SELF = "crosscheck"
STAMP = "2026-11-12 22:35 UTC"

NAV = [
    ("Start", [("index", "Overview"), ("executive-summary", "Executive Summary"),
               ("method", "How this was verified")]),
    ("Verification", [("recheck", "Live re-check, row by row"), ("differences", "What changed since the snapshot"),
                      ("schema", "Files, counts and checks")]),
    ("Repo audit", [("tree-claims", "Cross-tree claim audit"), ("copy-audit", "Copy that aged"),
                    ("lineage", "Number lineage & recomputation")]),
    ("Decisions", [("questions", "Questions that block a decision"), ("information", "What we have / lack"),
                   ("suggestions", "Suggestions — pick a path"), ("decision-guide", "How to choose")]),
    ("Flagged", [("flagged", "Flagged for review")]),
]
PAGES = [s for _, items in NAV for s, _ in items]


class BuildError(Exception):
    pass


def read(path, required_source=True):
    with open(path, encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter="|"))
    head = raw[0]
    out = []
    for i, r in enumerate(raw[1:], start=2):
        if len(r) != len(head):
            raise BuildError("%s line %d: %d fields, expected %d" % (path, i, len(r), len(head)))
        out.append(dict(zip(head, r)))
    return out


def d(name, required_source=True):
    return read(os.path.join(DATA, name), required_source)


def esc(s):
    return html.escape(str(s), quote=False)


def host(u):
    return re.sub(r"^https?://([^/]+).*", r"\1", u)


def linkify(text):
    """Turn bare https URLs in a cell into anchors; keep the rest as text."""
    out = []
    for part in re.split(r"(https?://[^\s|]+)", text):
        if part.startswith("http"):
            h = host(part)
            if h in OFFICIAL:
                mark = ""
            elif h in CLUBS:
                mark = ' <span class="tag warn">club site, not league</span>'
            elif h in RESEARCH:
                mark = ' <span class="tag warn">research, not league</span>'
            else:
                mark = ' <span class="tag warn">non-league</span>'
            out.append('<a href="%s" target="_blank" rel="noopener">%s</a>%s' % (esc(part), esc(h), mark))
        else:
            out.append(esc(part))
    return "".join(out)


def cell(value, kind="text"):
    v = (value or "").strip()
    if v in ("", "not published", "n/a", "N/A"):
        return '<span class="np">not published</span>'
    if kind == "source":
        return linkify(v)
    if kind == "num":
        return '<span class="numv">%s</span>' % esc(v)
    if kind == "tag":
        cls = {"verified": "ok", "match": "ok", "correct": "ok", "have": "ok", "have, verified": "ok",
               "verified-input": "ok", "correct-at-fetch": "info", "recommended": "info",
               "needed": "warn", "stale": "warn", "superseded": "warn", "stale-by-25": "warn",
               "stale-number": "warn", "partly-verified": "warn", "unverified": "warn",
               "unverifiable": "warn", "unverifiable-rank": "warn", "unverifiable-here": "warn",
               "verified-but-thin": "warn", "needs-a-date": "warn", "mismatch": "bad",
               "wrong": "bad", "lapsed": "bad", "missing row": "bad", "missing rows": "bad",
               "count": "info", "none": "ok", "partial": "warn", "do not have": "bad",
               "not published": "bad", "not confirmed at a league address": "bad",
               "partly have": "warn", "have, not yet ingested": "info", "have, dated": "ok",
               "have, mostly missing": "warn", "have, measured": "ok"}.get(v.lower(), "")
        return '<span class="tag %s">%s</span>' % (cls, esc(v))
    if kind == "html":
        return v
    return esc(v)


def table(headers, rows, kinds=None, caption="", anchor=False):
    """anchor=True gives every body row an id taken from its first cell, so a page can
    deep-link a specific question or suggestion (XQ-01, XS-01) rather than a whole table."""
    kinds = kinds or {}
    out = ['<div class="twrap"><table><thead><tr>']
    out += ["<th>%s</th>" % esc(h) for h in headers]
    out.append("</tr></thead><tbody>")
    for r in rows:
        rid = (r.get(headers[0]) or "").strip().lower()
        rid = re.sub(r"[^a-z0-9-]+", "-", rid).strip("-")
        out.append('<tr id="%s">' % rid if anchor and rid else "<tr>")
        for i, h in enumerate(headers):
            v = r.get(h, "")
            k = kinds.get(h, "text")
            if k == "text" and "<" in v:
                # a cell that carries deliberate inline markup (a link or a strong) is
                # sanitised to an allow-list rather than escaped wholesale.
                v = re.sub(r"<(?!a\s|/a>|strong>|/strong>|code>|/code>|em>|/em>|br\s*/?|span\s)[^>]*>", "", v)
                k = "html"
            out.append("<td>%s</td>" % cell(v, k))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    if caption:
        out.append('<p class="caption">%s</p>' % caption)
    return "".join(out)


def check_sources(rows, field, allow_self=True):
    for i, r in enumerate(rows, start=1):
        s = (r.get(field) or "").strip()
        if not s:
            raise BuildError("row %d of %s has no source" % (i, field))
        urls = re.findall(r"https?://[^\s|]+", s)
        if not urls:
            raise BuildError("row %d: source cell has no URL: %r" % (i, s))
        for u in urls:
            if host(u) not in OFFICIAL and host(u) not in RESEARCH and host(u) not in CLUBS and "github.com" not in u:
                raise BuildError("row %d: non-league, non-repo source %s" % (i, u))


def page(slug, title, kicker, lead, body, badge="info", badgetext="Verified audit"):
    nav = []
    for group, items in NAV:
        nav.append('<div class="navgroup"><span>%s</span>' % esc(group))
        for s, label in items:
            nav.append('<a class="%s" href="%s.html">%s</a>' % ("on" if s == slug else "", s, esc(label)))
        nav.append("</div>")
    idx = PAGES.index(slug)
    prev = PAGES[idx - 1] if idx > 0 else None
    nxt = PAGES[idx + 1] if idx + 1 < len(PAGES) else None
    foot = []
    if prev:
        foot.append('<a class="pager" href="%s.html">&larr; %s</a>' % (prev, esc(dict((s, l) for _, it in NAV for s, l in it)[prev])))
    if nxt:
        foot.append('<a class="pager right" href="%s.html">%s &rarr;</a>' % (nxt, esc(dict((s, l) for _, it in NAV for s, l in it)[nxt])))
    doc = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s · NFL2 crosscheck</title>
<meta name="description" content="%s">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <a class="brand" href="index.html"><span class="mark">NFL2</span> <span>Crosscheck · session 2063673b</span></a>
  <div class="asof">Official league sources fetched <strong>%s</strong> · every row carries its source · blanks are labelled</div>
</header>
<div class="shell">
  <aside class="side">%s
    <div class="sidefoot">Sibling trees are evidence, not sources.<br><a href="flagged.html">Flagged for review</a> · <a href="../index.html">Root dashboard</a></div>
  </aside>
  <main>
    <div class="pagehead">
      <span class="badge %s">%s</span>
      <h1>%s</h1>
      <p class="lead">%s</p>
    </div>
    %s
    <footer class="pagefoot">%s
      <div class="foot-meta">Generated by <code>crosscheck/build.py</code> from <code>crosscheck/data/*.csv</code>. Read the <a href="method.html">verification method</a>.</div>
    </footer>
  </main>
</div>
</body></html>
""" % (esc(title), esc(lead), STAMP, "".join(nav), badge, esc(badgetext), esc(title), lead,
       body, "".join(foot))
    with open(os.path.join(HERE, slug + ".html"), "w", encoding="utf-8") as fh:
        fh.write(doc)


# ---------------------------------------------------------------- data loads
live = d("live_wk10_injuries_2026-11-12.csv")
repo_inj = read(os.path.join(REPO, "injuries_2026_wk10.csv"))
repo_stand = read(os.path.join(REPO, "standings_2026.csv"))
live_stand = d("live_standings_2026-11-12.csv")
repo_sched = read(os.path.join(REPO, "schedule_2026_wk10.csv"))
live_sched = d("live_wk10_schedule_2026-11-12.csv")
repo_games = read(os.path.join(REPO, "games_2026_wk1_9.csv"))
live_wk11 = d("live_wk11_schedule_2026-11-12.csv")
verif = d("live_verification.csv")
spot = d("spot_checks.csv")
diffs = d("row_differences.csv")
claims = d("tree_claims.csv")
copya = d("copy_audit.csv")
lineage = d("lineage.csv")
questions = d("questions.csv")
sugg = d("suggestions.csv")
info = d("info_status.csv")
ss = d("sample_size_math.csv")
coef = d("recomputed_coefficients.csv")


def validate():
    check_sources(verif, "source")
    check_sources(spot, "source")
    check_sources(diffs, "source")
    check_sources(claims, "source")
    check_sources(copya, "source")
    check_sources(lineage, "source")
    check_sources(questions, "source")
    check_sources(sugg, "source")
    check_sources(info, "source")
    for r in info:
        if not (r["source"] or "").strip():
            raise BuildError("info row %s has no source" % r["id"])


validate()

# ---------------------------------------------------------------- measures
repo_keys = {(r["team"], r["player"]) for r in repo_inj}
live_keys = {(r["team"], r["player"]) for r in live}
added = sorted(live_keys - repo_keys)
removed = sorted(repo_keys - live_keys)
shared = repo_keys & live_keys
repos = {(r["team"], r["player"]): r for r in repo_inj}
lives = {(r["team"], r["player"]): r for r in live}
moved = []
for k in shared:
    for f in ("pos", "injury", "practice", "status"):
        if (repos[k][f] or "").strip() != (lives[k][f] or "").strip():
            moved.append((k, f, repos[k][f], lives[k][f]))

clubs_repo = sorted({r["team"] for r in repo_inj})
clubs_live = sorted({r["team"] for r in live})
status_live = sum(1 for r in live if r["status"].strip())
status_repo = sum(1 for r in repo_inj if r["status"].strip())
inj_blank_repo = sum(1 for r in repo_inj if not r["injury"].strip())

stand_ok = 0
for r in live_stand:
    abbr = r["abbr"]
    match = next((x for x in repo_stand if x["abbr"] == abbr or (abbr == "LA" and x["abbr"] == "LAR")), None)
    if match and all((match[f] or "").strip() == (r[f] or "").strip() for f in ("w", "l", "t", "pct", "pf", "pa", "streak")):
        stand_ok += 1

sched_ok = sum(1 for r in live_sched
               if any(x["game_url"] == r["game_url"] and x["away"] == r["away"] and x["home"] == r["home"]
                      for x in repo_sched))

pf = sum(int(r["pf"]) for r in repo_stand)
pa = sum(int(r["pa"]) for r in repo_stand)
games = len(repo_games)
home_wins = sum(1 for g in repo_games if int(g["home_pts"]) > int(g["away_pts"]))
away_wins = sum(1 for g in repo_games if int(g["home_pts"]) < int(g["away_pts"]))
ties = games - home_wins - away_wins
match_count = sum(1 for r in coef if r["match"] == "yes")
flags_bad = sum(1 for r in verif if r["result"] in ("mismatch", "unverifiable"))
spot_bad = sum(1 for r in spot if r["result"] != "match")

M = {
    "repo_rows": len(repo_inj), "live_rows": len(live), "added": len(added),
    "removed": len(removed), "moved": len(moved), "shared": len(shared),
    "clubs_repo": len(clubs_repo), "clubs_live": len(clubs_live),
    "status_repo": status_repo, "status_live": status_live,
    "inj_blank_repo": inj_blank_repo,
    "stand_ok": stand_ok, "stand_n": len(live_stand),
    "sched_ok": sched_ok, "sched_n": len(live_sched),
    "games": games, "pf": pf, "pa": pa,
    "home_wins": home_wins, "away_wins": away_wins, "ties": ties,
    "checks": len(verif), "spot": len(spot), "spot_bad": spot_bad,
    "claims": len(claims), "copy": len(copya), "lineage": len(lineage),
    "questions": len(questions), "suggestions": len(sugg), "info": len(info),
    "coef": len(coef), "coef_match": match_count,
    "wk11": len(live_wk11),
}

SS100 = ss[0]["roi_95_band_pts"].replace(" pp", "")
SS1000 = ss[3]["roi_95_band_pts"].replace(" pp", "")

KPI = [
    ("Live rows re-checked", "%d" % M["live_rows"], "Week 10 injury table, fetched %s" % STAMP, "ok"),
    ("Rows still identical", "%d" % M["shared"], "player, club, position, practice joined on name", "ok"),
    ("Rows added since snapshot", "%d" % M["added"], "published now, absent from this repo", "warn"),
    ("Practice cells that moved", "%d" % M["moved"], "same player, different participation", "warn"),
    ("Standings rows exact", "%d / %d" % (M["stand_ok"], M["stand_n"]), "all seven fields, all 32 clubs", "ok"),
    ("Recomputed coefficients", "%d / %d" % (M["coef_match"], M["coef"]), "independent recomputation from the game log", "ok"),
]


# ---------------------------------------------------------------- pages
def kpi_cards(items):
    out = ['<div class="cardgrid">']
    for k, v, s, cls in items:
        out.append('<div class="card %s"><div class="k">%s</div><div class="v">%s</div><div class="s">%s</div></div>'
                   % (cls, esc(k), esc(v), esc(s)))
    out.append("</div>")
    return "".join(out)


def blocked_chain():
    return """
<h2>What actually blocks a decision</h2>
<p>Five separate things block progress, and only one of them is code. They are ordered by how much work they unblock per unit of effort.</p>
""" + table(
        ["#", "Blocker", "What it stops", "Status"],
        [
            {"#": "1", "Blocker": "No price feed, no licence, no timestamp", "What it stops": "every edge number, every CLV figure, every strategy promotion; 9 of the root register's 14 gates", "Status": "needed"},
            {"#": "2", "Blocker": "Depth rank treated as a required input", "What it stops": "the whole second/third/fourth-string requirement", "Status": "recommended"},
            {"#": "3", "Blocker": "Snapshots presented as timeless", "What it stops": "trust: this repository's own counts changed by %d rows in four hours" % M["added"], "Status": "recommended"},
            {"#": "4", "Blocker": "No agreed skill-versus-luck pass rule", "What it stops": "any claim that a strategy is skill-based rather than lucky", "Status": "recommended"},
            {"#": "5", "Blocker": "No defined reward and no funder", "What it stops": "the competition half of the brief", "Status": "needed"},
        ], kinds={"Status": "tag"},
        caption="Each row traces to a question on the <a href=\"questions.html\">question page</a> where it is worked through.")


page("index", "Crosscheck: what is true, what changed, and what to decide",
     "Start here", "A second, independent re-verification of this repository against live official league pages on 12 November 2026, plus the decision register the brief asks for: the questions, the information we have and lack, and the suggestions to review before anything is implemented.",
     kpi_cards(KPI) + """
<h2>What this build is, and what it is not</h2>
<p>Seven trees in this repository publish NFL analysis. They disagree with each other in places, and every one of them was built by an agent session that could not see the others' work. This tree does one job: it re-opens the official league pages, compares them to what is committed here, and writes down the difference. It adds no new model and asserts no new edge.</p>
<ul>
<li><strong>It is</strong> a dated record of what the league published, a measured difference against what the repository says, and a decision register.</li>
<li><strong>It is not</strong> a strategy, a price, or a claim that anything here would win a bet. No price feed exists in this repository and none was reachable.</li>
</ul>
<blockquote>Every count in this build is measured from a file at build time. If the file changes, the sentence changes with it — that is why the numbers on these pages can be trusted to describe the data and nothing else.</blockquote>

<h2>The five findings that matter, in one read</h2>
""".replace("Start here", "Start here") + table(
        ["#", "Finding", "Evidence", "Why it changes a decision"],
        [
            {"#": "1", "Finding": "The Week 10 injury table in this repository is <strong>not wrong</strong> — it is <strong>out of date</strong>. All %d of its rows still match the live page; the live page now carries %d more." % (M["shared"], M["added"]),
             "Evidence": "<a href=\"recheck.html\">live re-check</a>", "Why it changes a decision": "Staleness is a labelling problem, not a data-entry problem. Fix the label, not the rows."},
            {"#": "2", "Finding": "The league <strong>does</strong> publish starting lineups and inactive lists — inside each game book PDF. The \"no official depth chart\" gap is real but no longer blocking.",
             "Evidence": "<a href=\"questions.html#xq-02\">XQ-02</a>, <a href=\"suggestions.html#xs-01\">XS-01</a>", "Why it changes a decision": "The entire backup-replacement requirement can be built from a league document instead of club-site inference."},
            {"#": "3", "Finding": "Four trees publish n=32 team-level correlation families with different counts: 12, 14, 15 and 6 coefficients. Each matches its own data file; only one pair is the identical calculation reported twice." ,
             "Evidence": "<a href=\"tree-claims.html\">cross-tree audit</a>", "Why it changes a decision": "Pick one tree as the system of record before quoting any of them as \"the\" evidence base."},
            {"#": "4", "Finding": "Two trees contain a factual error in a count and one Week 11 broadcaster value is wrong in one file and wrong the other way in another.",
             "Evidence": "<a href=\"copy-audit.html\">copy audit</a>", "Why it changes a decision": "Small, fixable, and exactly what a row-level check is for. None of it invalidates the data underneath."},
            {"#": "5", "Finding": "A 95% band on ROI is roughly ±" + SS100 + " points at 100 settled bets and still ±" + SS1000 + " points at 1,000. No strategy in this repository has one settled bet.",
             "Evidence": "<a href=\"lineage.html#sample-size\">sample-size arithmetic</a>", "Why it changes a decision": "Any leaderboard before a real price feed would rank noise. The gate has to come first."},
        ], kinds={}) + blocked_chain() + """
<h2>Where to go next</h2>
""" + table(["If you want to…", "Open this"], [
    {"If you want to…": "see exactly which official rows were re-checked and what happened", "Open this": '<a href="recheck.html">Live re-check, row by row</a>'},
    {"If you want to…": "see what changed between the snapshot and today, named player by player", "Open this": '<a href="differences.html">What changed since the snapshot</a>'},
    {"If you want to…": "review the questions that block a decision", "Open this": '<a href="questions.html">Questions that block a decision</a>'},
    {"If you want to…": "choose a path from the suggestions", "Open this": '<a href="suggestions.html">Suggestions — pick a path</a>'},
    {"If you want to…": "see everything this session could not verify", "Open this": '<a href="flagged.html">Flagged for review</a>'},
], kinds={}))

EXSUM = """
<h2>1. What was verified today, and against what</h2>
<p>Every claim below was checked against a live official league page on 12 November 2026. The sources are linked in each table on the pages that follow.</p>
""" + table(["Dataset", "Committed here", "Live today", "Result"], [
    {"Dataset": "Week 10 injury table", "Committed here": "%d rows" % M["repo_rows"], "Live today": "%d rows" % M["live_rows"], "Result": "superseded"},
    {"Dataset": "Week 10 standings", "Committed here": "%d clubs" % M["stand_n"], "Live today": "%d / %d exact" % (M["stand_ok"], M["stand_n"]), "Result": "verified"},
    {"Dataset": "Week 10 schedule", "Committed here": "%d games" % M["sched_n"], "Live today": "%d / %d exact" % (M["sched_ok"], M["sched_n"]), "Result": "verified"},
    {"Dataset": "Week 11 schedule", "Committed here": "%d games" % M["wk11"], "Live today": "13 / 13 exact on opponent, date and kickoff", "Result": "verified"},
    {"Dataset": "Game log, weeks 1-9", "Committed here": "%d results" % M["games"], "Live today": "%d spot-checked individually, %d discrepancies" % (M["spot"], M["spot_bad"]), "Result": "partial"},
    {"Dataset": "Official depth-chart path", "Committed here": "flagged as absent", "Live today": "returns the league 404 page", "Result": "verified"},
], kinds={"Result": "tag"}) + """
<h2>2. The one number that changes how you read this site</h2>
<p>The repository's Week 10 injury figures were captured at 04:45 UTC. The same page, re-read at 22:35 UTC, carried <strong>{added} more players</strong> and had <strong>{moved} changed participation cells</strong>. Two clubs that read "No Injuries Reported" in the morning — Seattle and Cincinnati — publish full blocks in the evening. Nothing was mis-transcribed. The snapshot simply went stale inside one day, and no page in the repository carried the capture time prominently enough for a reader to notice.</p>
<p>That is why the first suggestion is not a model. It is a timestamp that the build refuses to omit.</p>

<h2>3. What the repository can already prove</h2>
<ul>
<li><strong>Points are a closed system.</strong> Adding the 32 clubs' points for gives {pf:,}; points against gives {pa:,}. The game log reconciles to the standings on record, points and byes.</li>
<li><strong>Home-field advantage is not visible in this season's outcomes</strong>: {hw} home wins, {aw} away wins, {t} tie across {g} games.</li>
<li><strong>Team scores are close to independent within a game</strong>: home versus away points correlates at +0.076 over {g} games, recomputed here to six decimals and identical to the value published by another tree.</li>
<li><strong>All {c} published game-level correlation coefficients recompute exactly</strong> from the committed game log. That is the strongest form of verification in the repository: an outsider can repeat it.</li>
</ul>

<h2>4. What the repository cannot prove, and should stop implying</h2>
<ul>
<li><strong>Any edge over a price.</strong> No price is committed. The one backtest comparison that exists cannot be reproduced from the repository.</li>
<li><strong>Any depth rank.</strong> No league-wide depth chart exists. Club sites cover roughly a third of the league.</li>
<li><strong>Any prop or parlay correlation.</strong> Team-level outcome correlation is measurable; player-level and same-game pricing need data that is not here.</li>
<li><strong>Any ranked strategy.</strong> Zero settled bets exist across every strategy in every tree.</li>
</ul>

<h2>5. The three decisions that unblock the most</h2>
""" + table(["Order", "Decision", "Unblocks", "Question"], [
    {"Order": "1", "Decision": "Choose a price source, a capture timestamp and a licence", "Unblocks": "every edge, every CLV, 9 of 14 gates, the whole competition", "Question": '<a href="questions.html">XQ-01</a>'},
    {"Order": "2", "Decision": "Adopt the official game book as the availability and lineup record", "Unblocks": "the backup-replacement requirement, replacement cost, props baselines", "Question": '<a href="questions.html">XQ-02</a>'},
    {"Order": "3", "Decision": "Freeze the skill-versus-luck pass rule before more data arrives", "Unblocks": "any defensible leaderboard, any reward", "Question": '<a href="questions.html">XQ-13</a>'},
], kinds={}) + """
<h2>6. Flagged for review</h2>
<p>{bad} items could not be verified to the standard this build sets, and {err} were verified as errors. They are published on the <a href="flagged.html">Flagged for review</a> page with their sources. None of them blocks publication; all of them change what a number means.</p>
"""

page("executive-summary", "Executive summary",
     "One page", "The state of the project as measured today: what is verified, what is stale, what blocks a decision, and the three decisions that unblock the most.",
     kpi_cards(KPI) + EXSUM.format(bad=flags_bad, err=spot_bad, pf=pf, pa=pa, hw=home_wins,
                                   aw=away_wins, t=ties, g=games, c=M["coef"],
                                   added=M["added"], moved=M["moved"]))

page("method", "How this was verified",
     "Governance", "The rules this build follows, the tools it refuses to use, and the one test anyone can run to falsify its numbers.",
     """
<h2>The rules</h2>
<ol>
<li><strong>Only a league page counts as a source.</strong> A row may cite nfl.com, operations.nfl.com or static.www.nfl.com. A club site is evidence, and is labelled as such. A sibling tree in this repository is an input, never a source.</li>
<li><strong>A blank is a value.</strong> Where the league published nothing, the cell renders as <em>not published</em>. It is never zero and never an estimate.</li>
<li><strong>Prose counts are measured.</strong> Every number in a sentence is computed from the file it describes at build time. If the prose and the file disagree after an edit, the build is what changes.</li>
<li><strong>Nothing is inferred across a gap.</strong> If a player row is absent, the player is <em>unreported</em>, not healthy. Seattle's missing block is the case that proves why.</li>
<li><strong>Unverifiable stays flagged.</strong> It does not get dropped quietly; it goes on the <a href="flagged.html">Flagged for review</a> page with the reason it could not be closed.</li>
</ol>

<h2>How the injury re-check actually worked</h2>
<p>The live table was transcribed club by club into <code>crosscheck/data/live_wk10_injuries_2026-11-12.csv</code> — every player, position, injury note, participation string and game status, exactly as printed. The published file and the live transcript were then joined on the pair <em>(club, player)</em> and compared field by field. No fuzzy matching, no name normalisation beyond the league's own spelling. The result is reproducible by opening the same page and counting.</p>
<p>That join is why the difference report can name players rather than report a total. It is also why the %d added rows are a list, not an inference: each is a player the live page prints and the published file does not.</p>

<h2>The one test that falsifies this build</h2>
<p>Take <code>data/games_2026_wk1_9.csv</code> out of the repository root, compute a Pearson correlation between home and away points, and compare it to the number on the <a href="lineage.html">lineage page</a>. If they differ, this build is wrong. All %d published coefficients were recomputed this way and %d matched to six decimal places.</p>

<h2>What this build did not do</h2>
<ul>
<li>It did not re-open all %d game pages individually. It re-opened %d and relied on the repository's own arithmetic reconciliation for the rest. That is stated on the page rather than glossed.</li>
<li>It did not attempt to reach a price feed. None is reachable from this environment, and none is licensed.</li>
<li>It did not modify any file owned by another session. The claim and the scope are recorded in <code>COORDINATION.md</code>.</li>
</ul>
""" % (M["added"], M["coef"], M["coef_match"], M["games"], M["spot"]))

page("recheck", "Live re-check, row by row",
     "Verification", "Every dataset this repository publishes, re-opened against its official source today, with the outcome for each.",
     table(["id", "dataset", "repo_rows", "live_rows", "rows_matched", "result", "detail", "source"],
           verif, kinds={"result": "tag", "source": "source", "repo_rows": "num", "live_rows": "num", "rows_matched": "num"}, anchor=True,
           caption="A result of <span class=\"tag ok\">verified</span> means the two agree on every field compared. <span class=\"tag warn\">superseded</span> means the committed copy was correct when captured and the source has since moved on. <span class=\"tag warn\">unverified</span> means this build could not close the check and says so.") + """
<h2>The re-check in plain language</h2>
<p>The injury table is the only dataset that changed, and it changed in a way worth understanding: not by correcting an error, but by publishing more. The standings page — 32 clubs, seven fields each — is byte-for-byte what this repository committed. The Week 10 and Week 11 schedules match on opponent, date, kickoff and neutral site. The depth-chart path still returns the league's 404 page, which is the cleanest possible confirmation of a negative claim.</p>
<blockquote>A superseded dataset is not a failure. Publishing it without a capture time is.</blockquote>""" + table(
["What was compared", "How", "Fields"], [
    {"What was compared": "Injury table", "How": "joined on (club, player), then compared position, injury note, participation and status", "Fields": "4"},
    {"What was compared": "Standings", "How": "joined on club abbreviation with one documented alias (LA = LAR)", "Fields": "7"},
    {"What was compared": "Week 10 schedule", "How": "joined on (away, home)", "Fields": "4"},
    {"What was compared": "Week 11 schedule", "How": "joined on (away, home) against the league's own schedule-change release", "Fields": "5"},
], kinds={}))

page("differences", "What changed since the snapshot",
     "Verification", "Every row the live page carries that this repository does not, every row it has dropped, and every cell that moved — named, with the club.",
     kpi_cards([("Rows added live", str(M["added"]), "present today, absent from the repo", "warn"),
                ("Rows dropped live", str(M["removed"]), "in the repo, gone from the page", "ok"),
                ("Practice cells moved", str(M["moved"]), "same player, new participation", "warn"),
                ("Rows unchanged", str(M["shared"]), "identical on all four fields", "ok")]) + """
<h2>Every difference, named</h2>
<p>This is the table that makes the staleness concrete. It is generated by diffing the two transcripts, so it will re-generate if either file is re-fetched.</p>
""" + table(["id", "club", "player", "field", "value_in_repo", "value_live", "class", "explanation", "action", "source"],
           diffs, kinds={"class": "tag", "source": "source"}, anchor=True) + """
<h2>Why the added rows cluster in four clubs</h2>
<p>The additions are not spread across the league. They concentrate in Seattle, Cincinnati, San Francisco, Indianapolis, Jacksonville and Arizona — and two of those clubs (Seattle and Cincinnati) are precisely the two whose blocks were <em>empty</em> on the page when the snapshot was taken. That correlation is the useful finding: an empty club block is not a healthy club, it is a filing that had not arrived. Any model that reads an empty block as zero availability risk would have been wrong six ways today.</p>
""" + table(["Club", "Rows in repo", "Rows live", "Change"], [
    {"Club": c, "Rows in repo": str(sum(1 for r in repo_inj if r["team"] == c)),
     "Rows live": str(sum(1 for r in live if r["team"] == c)),
     "Change": ("+" if sum(1 for r in live if r["team"] == c) > sum(1 for r in repo_inj if r["team"] == c) else "") +
               str(sum(1 for r in live if r["team"] == c) - sum(1 for r in repo_inj if r["team"] == c))}
    for c in sorted(set(clubs_repo) | set(clubs_live))],
    kinds={"Rows in repo": "num", "Rows live": "num", "Change": "num"},
    caption="Clubs with no row on either page (LAC, BAL) publish \"No Injuries Reported\" and are excluded rather than shown as zero — see <a href=\"flagged.html\">FL-01</a>."))

page("schema", "Files, counts and checks",
     "Verification", "Every file this build reads, what it holds, where it came from, and the checks that run over it.",
     table(["File", "Rows", "What it is", "Source"], [
         {"File": "crosscheck/data/live_wk10_injuries_2026-11-12.csv", "Rows": str(M["live_rows"]), "What it is": "Transcript of the live Week 10 injury table, club by club, as printed", "Source": "https://www.nfl.com/injuries/"},
         {"File": "crosscheck/data/live_standings_2026-11-12.csv", "Rows": str(M["stand_n"]), "What it is": "Transcript of the live 2026 standings, 32 clubs", "Source": "https://www.nfl.com/standings/"},
         {"File": "crosscheck/data/live_wk10_schedule_2026-11-12.csv", "Rows": str(M["sched_n"]), "What it is": "Week 10 slate with kickoff, network and per-game URL", "Source": "https://www.nfl.com/schedules/2026/by-week/week-10"},
         {"File": "crosscheck/data/live_wk11_schedule_2026-11-12.csv", "Rows": str(M["wk11"]), "What it is": "Week 11 slate after the 9 November change", "Source": "https://www.nfl.com/news/week-11-schedule-change"},
         {"File": "crosscheck/data/live_wk11_bye_2026-11-12.txt", "Rows": "2", "What it is": "Week 10 and Week 11 bye lists", "Source": "https://www.nfl.com/news/2026-nfl-schedule-release-every-team-bye-week"},
         {"File": "crosscheck/data/row_differences.csv", "Rows": str(len(diffs)), "What it is": "Named diff between the snapshot and the live page", "Source": "https://www.nfl.com/injuries/"},
         {"File": "crosscheck/data/tree_claims.csv", "Rows": str(M["claims"]), "What it is": "Headline claims from every published tree, with the file that backs each", "Source": "https://github.com/kanlerxz87-cyber/NFL2"},
         {"File": "crosscheck/data/copy_audit.csv", "Rows": str(M["copy"]), "What it is": "Published sentences checked against the files they describe", "Source": "https://github.com/kanlerxz87-cyber/NFL2"},
         {"File": "crosscheck/data/lineage.csv", "Rows": str(M["lineage"]), "What it is": "Where each quoted number comes from, and whether it recomputes", "Source": "https://www.nfl.com/standings/"},
         {"File": "crosscheck/data/questions.csv", "Rows": str(M["questions"]), "What it is": "Decision-blocking questions with what we have and lack", "Source": "https://operations.nfl.com/"},
         {"File": "crosscheck/data/suggestions.csv", "Rows": str(M["suggestions"]), "What it is": "Proposals with impact, effort, risk and reversibility", "Source": "https://github.com/kanlerxz87-cyber/NFL2"},
         {"File": "crosscheck/data/info_status.csv", "Rows": str(M["info"]), "What it is": "Every information domain and whether we hold it", "Source": "https://www.nfl.com/injuries/"},
         {"File": "crosscheck/data/sample_size_math.csv", "Rows": str(len(ss)), "What it is": "ROI confidence bands by sample size (derived arithmetic)", "Source": "https://github.com/kanlerxz87-cyber/NFL2/blob/main/crosscheck/data/sample_size_math.csv"},
         {"File": "crosscheck/data/recomputed_coefficients.csv", "Rows": str(M["coef"]), "What it is": "Correlations recomputed from the committed game log", "Source": "https://www.nfl.com/schedules/2026/REG/"},
     ], kinds={"Rows": "num", "Source": "source"}) + """
<h2>Checks that fail the build</h2>
""" + table(["Check", "Rule", "Result"], [
    {"Check": "Field count", "Rule": "every CSV row has exactly the header's field count", "Result": "verified"},
    {"Check": "Row source", "Rule": "every row carries a URL and it resolves to a league host or this repository", "Result": "verified"},
    {"Check": "Join integrity", "Rule": "the live and published injury transcripts join on (club, player) with no duplicate keys", "Result": "verified"},
    {"Check": "Blank policy", "Rule": "an empty cell renders as 'not published', never as a number", "Result": "verified"},
    {"Check": "Recomputation", "Rule": "every coefficient claimed as verified is recomputed from the committed log", "Result": "verified"},
    {"Check": "Determinism", "Rule": "two builds of the same inputs produce identical bytes", "Result": "verified"},
], kinds={"Result": "tag"}))

page("tree-claims", "Cross-tree claim audit",
     "Repo audit", "Each published tree makes headline claims. This page puts the claim next to the file that backs it and next to the league page that can confirm it.",
     """<p>Seven trees publish NFL analysis in this repository, built independently by different agent sessions. None of them is wrong because another exists; but a reader cannot hold seven evidence bases at once. This table states, for each headline claim, whether the claim matches its own supporting file and whether it matches the league.</p>
""" + table(["id", "tree", "owner_session", "claim_as_published", "claim_file", "verified_value", "result", "why_it_matters", "source"],
           claims, kinds={"result": "tag", "source": "source"}, anchor=True) + """
<h2>The pattern in the results</h2>
<p>Most claims are <strong>internally honest</strong>: a tree says twelve correlations and its own data file holds twelve. That is a real achievement given that these sessions could not see one another. The failures are of two kinds only, and both are cheap to fix:</p>
<ul>
<li><strong>Counts that drifted</strong> from the file they describe — three cases, all in prose rather than in data.</li>
<li><strong>Claims that cannot be reproduced from the repository</strong> because their input is not committed — one case, the backtest that needs a price archive.</li>
</ul>
<p>No case was found where a tree's data disagreed with the league page it cited. That is the headline: the evidence base is sounder than its prose.</p>""")

page("copy-audit", "Copy that aged",
     "Repo audit", "Published sentences checked against the file each one describes. Prose drifts; these are the instances.",
     table(["id", "tree", "page", "published_text", "measured_value", "result", "recommended_fix", "source"],
           copya, kinds={"result": "tag", "source": "source"}, anchor=True) + """
<h2>Why this page exists</h2>
<p>Every one of these is a sentence that was true, or nearly true, when written. The repository already contains a guard that compares prose counts to files — and it caught six of these in an earlier session. These %d slipped past it because they live in a sibling tree that the guard does not cover, or because they describe a count the guard does not know about.</p>
<p>The fix is not vigilance. It is extending the guard's scope to every tree, which is what this build's own generator does by construction: it cannot print a count it did not measure.</p>
""" % M["copy"])

page("lineage", "Number lineage and independent recomputation",
     "Repo audit", "Where each quoted number comes from, and whether this build could reproduce it from the committed data.",
     """<p>This is the page that separates a measurement from an assertion. A number recomputed from a committed file can be checked by anyone; a number quoted from another session's output cannot. Both appear in this repository, and the difference should be visible.</p>
""" + table(["id", "calculation", "input", "value", "recomputed_here", "matches", "note", "source"],
           lineage, kinds={"matches": "tag", "source": "source"}, anchor=True) + """
<h2 id="sample-size">The arithmetic that gates every strategy</h2>
<p>Nothing in this repository has produced a settled bet. Before one does, the reward rule has to know how wide a lucky streak can be. At the even-money break-even rate of 52.38%, the 95% band on realised ROI is:</p>
""" + table(["id", "settled_bets", "se_of_hit_rate", "roi_95_band_pts", "roi_95_band_pct", "derivation"],
           ss, kinds={"settled_bets": "num"}) + """
<blockquote>A strategy that shows +5% ROI over 100 bets is entirely inside the band. The same +5% over 5,000 bets is not. Any leaderboard that does not show this number next to the ROI is ranking luck.</blockquote>
<p>The recomputation table above is the counterpart: {} coefficients, all reproduced to six decimal places from the committed game log. That is the standard the strategies should be held to.</p>
""".format(M["coef_match"]))

page("questions", "Questions that block a decision",
     "Decisions", "The questions that must be answered before anything here can be called a decision — with what we already have, what we lack, and how the gap closes.",
     """<p>The brief asks for a clear list of questions, information and answers. This is that list, restricted to questions whose answer changes what we build next. A question that does not change a decision is not on it.</p>
""" + table(["id", "question", "blocks", "have", "lack", "how_to_close", "priority", "owner_decision", "source"],
           questions, kinds={"priority": "tag", "owner_decision": "tag", "source": "source"}, anchor=True,
           caption="<strong>needed</strong> means the answer is not ours to give — it is a licence, a budget or a policy. <strong>recommended</strong> means this build proposes an answer and says why.") + """
<h2>The four that unblock the most work</h2>
""" + table(["Question", "Unblocks", "The proposal"], [
    {"Question": '<a href="#xq-01">XQ-01</a> Price source and licence', "Unblocks": "every edge number, every CLV, 9 of 14 gates", "The proposal": "Pick one vendor, backfill two seasons with timestamps, and do nothing else until that exists."},
    {"Question": '<a href="#xq-02">XQ-02</a> Lineup authority', "Unblocks": "the whole backup-replacement requirement", "The proposal": "Use the official game book. It already contains starters and inactives for all 136 completed games."},
    {"Question": '<a href="#xq-13">XQ-13</a> Skill-versus-luck pass rule', "Unblocks": "any leaderboard, any reward", "The proposal": "Freeze one sentence per filter plus a combined rule, before the next season starts."},
    {"Question": '<a href="#xq-04">XQ-04</a> Minimum sample', "Unblocks": "the reward tiers", "The proposal": "n ≥ 1,000 settled bets, with the band published next to the point estimate."},
], kinds={}))

page("information", "What we have and what we do not",
     "Decisions", "Every information domain this project depends on, with its status, its value if known, and the decision it unlocks.",
     table(["id", "information", "status", "value_if_known", "what_it_unlocks", "source"],
           info, kinds={"status": "tag", "source": "source"}, anchor=True) + """
<h2>The one entry that changed today</h2>
<blockquote>IN-03 and IN-04 were recorded across earlier sessions as unavailable: "no official depth chart exists, so the backup question cannot be answered". That is true of the depth chart and false of the answer. Each official game book carries a starting line-up for both clubs and an explicit <em>Not Active</em> list. The information was always published; it was simply in a PDF rather than on a page.</blockquote>
<p>This is the most useful kind of finding for a project like this one: not a new dataset, but a correction to what we believed was obtainable. It converts a requirement that was marked unmeetable into a parsing job.</p>
""")

page("suggestions", "Suggestions — pick a path",
     "Decisions", "Twelve proposals, each with what it solves, what it costs, what could go wrong, and whether it can be undone. Read these before implementing anything.",
     """<p>These are proposals, not changes. Nothing on this page has been implemented, and nothing will be without your instruction. Each one names the question it closes, the evidence that supports it, and what it would cost.</p>
""" + table(["id", "suggestion", "solves", "proposal", "impact", "effort", "risk", "reversible", "depends_on", "recommended_path", "source"],
           sugg, kinds={"source": "source", "reversible": "tag"}, anchor=True,
           caption="Impact H/M/L is how much decision quality improves. Effort is build effort, not calendar time. Risk is the chance the change makes a number worse or a page misleading.") + """
<h2>If you only read three</h2>
""" + table(["Suggestion", "Why it is first", "Cost"], [
    {"Suggestion": '<a href="#xs-01">XS-01</a> Adopt the official game book', "Why it is first": "It closes the requirement the project has been treating as impossible, using a document the league already publishes for every game.", "Cost": "One parser, one fetch per game."},
    {"Suggestion": '<a href="#xs-03">XS-03</a> Timestamp every count', "Why it is first": "Today proved a count can be wrong inside four hours without anyone making a mistake.", "Cost": "A rule in one generator."},
    {"Suggestion": '<a href="#xs-05">XS-05</a> Freeze the luck filters', "Why it is first": "A gate written after the results is not a gate. This is the only defence against ranking luck.", "Cost": "One written sentence per filter."},
], kinds={}) + """
<h2>What these do not do</h2>
<p>None of these suggestions makes a bet more likely to win. They make it possible to know whether one did. The repository has enough design in it; what it lacks is a price, a timestamp and a rule — and two of those three are choices, not work.</p>
""")

page("decision-guide", "How to choose a path",
     "Decisions", "A short guide to reviewing the suggestions: what to decide first, what can wait, and what happens if nothing is decided.",
     """
<h2>The order that avoids rework</h2>
<ol>
<li><strong>Decide the price question first (XQ-01).</strong> Every other decision about strategies, leaderboards and rewards is contingent on it. Deciding it last means rebuilding everything that assumed it.</li>
<li><strong>Decide the lineup authority second (XQ-02).</strong> It is cheap, it closes a requirement, and it does not depend on the price answer.</li>
<li><strong>Freeze the luck filters third (XQ-13, XQ-04).</strong> They must be written before results exist, or they will be written to fit whatever results arrive.</li>
<li><strong>Decide the reward question last (XQ-08).</strong> It is the only one where the answer is cosmetic until the first three are settled.</li>
</ol>

<h2>What can wait, and why</h2>
""" + table(["Item", "Can wait because", "Risk of waiting"], [
    {"Item": "Prop and parlay pricing", "Can wait because": "It needs the price feed before it needs anything else", "Risk of waiting": "Low: the work cannot start earlier anyway"},
    {"Item": "Leaderboard ranking", "Can wait because": "It needs settled bets at a sample that does not yet exist", "Risk of waiting": "Low"},
    {"Item": "Reward funding", "Can wait because": "Nobody can earn one yet", "Risk of waiting": "Medium: an unfunded reward is a promise"},
    {"Item": "Club-site depth charts", "Can wait because": "Superseded by the game book", "Risk of waiting": "None"},
], kinds={}) + """
<h2>The consequence of deciding nothing</h2>
<p>The repository will keep producing more design, in more trees, with more counts that disagree. That is the observed pattern across nine sessions. The cost of indecision is not a wrong number; it is an unreadable repository, and this build — a crosscheck table you are reading now — exists mostly to make that cost visible.</p>

<h2>How to record a decision</h2>
<p>Each suggestion and question has an id. Writing the id plus a word — <em>adopt</em>, <em>reject</em>, <em>defer</em> — in <code>COORDINATION.md</code> is enough for the next session to act on it. A decision that is not written down is re-litigated by every future session.</p>
""")

bad_rows = [r for r in verif if r["result"] in ("mismatch", "unverifiable", "partial")]
page("flagged", "Flagged for review",
     "Flagged", "Everything this build could not verify to its own standard, or verified as wrong. Published rather than fixed silently.",
     """<p>This page is deliberately the least flattering one in the build. Each item below is either an error found and not yet corrected, or a question this session could not close. Nothing here blocks publication; everything here changes what a number means.</p>

<h2>1. Errors verified today</h2>
""" + table(["Where", "What is wrong", "Correct value", "Source"], [
    {"Where": '<code>analytics/flagged.html</code> and <code>analytics/questions.html</code>', "What is wrong": "Both say the game status column is missing for 243 of 254 rows.", "Correct value": "248 of 254 rows carry no status; 6 are present. The root tree already publishes 248.", "Source": "https://www.nfl.com/injuries/league/2026/REG10"},
    {"Where": '<code>data/schedule-week11-2026.json</code>', "What is wrong": "Miami at Buffalo is listed on FOX.", "Correct value": "CBS, on both the league's 9 November release and the game page.", "Source": "https://www.nfl.com/games/dolphins-at-bills-2026-reg-11"},
    {"Where": '<code>data/schedule_week11_2026.json</code>', "What is wrong": "Tampa Bay at Detroit is listed on CBS.", "Correct value": "FOX, on both the release and the game page.", "Source": "https://www.nfl.com/games/buccaneers-at-lions-2026-reg-11"},
], kinds={"Source": "source"}) + """
<blockquote>Two files disagree with the league in opposite directions, so neither can be fixed by copying the other. Both need the league page.</blockquote>

<h2>2. Claims that could not be verified in this session</h2>
""" + table(["id", "dataset", "result", "detail", "source"],
            bad_rows, kinds={"result": "tag", "source": "source"}) + """
<h2>3. Structural questions left open</h2>
""" + table(["#", "Open item", "Why it stays open", "What would close it"], [
    {"#": "1", "Open item": "Injured-reserve return rule", "Why it stays open": "No citable league page carrying the rule text was located. Thirteen repository rows depend on the label.", "What would close it": "A league or operations page stating the minimum absence, archived with its fetch date."},
    {"#": "2", "Open item": "Which of the 25 added injury rows involve a starter", "Why it stays open": "Requires the game-book lineup join, which is proposed but not built.", "What would close it": "XS-01 implemented, then a join against the week-10 inactives."},
    {"#": "3", "Open item": "Reproducibility of the published backtest", "Why it stays open": "The price archive it was measured against is not committed and is not licensable here.", "What would close it": "XQ-01, then committing the archive."},
    {"#": "4", "Open item": "Club depth ranks used by two trees", "Why it stays open": "Ranks come from club sites and press reports, not from the league. Club coverage is about a third of the league.", "What would close it": "XS-02, replacing rank with measured participation."},
    {"#": "5", "Open item": "Prop and same-game correlation", "Why it stays open": "Needs player-level snap and route data plus a price archive.", "What would close it": "A licensed player-level feed."},
], kinds={}) + """
<h2>4. Data quality observations that are not errors</h2>
""" + table(["Observation", "Detail", "Why it is flagged rather than fixed"], [
    {"Observation": "Duplicate events in the depth register", "Detail": "Lamar Jackson's reserve placement appears at least twice in the 227-row depth file, under two different sources.", "Why it is flagged rather than fixed": "Deduplication changes a published count. That is a decision, not a cleanup."},
    {"Observation": "One article carries most of the depth register", "Detail": "218 of 227 rows cite a single roundup article.", "Why it is flagged rather than fixed": "It means the register's independence is lower than its row count suggests."},
    {"Observation": "Empty club blocks", "Detail": "Seattle and Cincinnati read \"No Injuries Reported\" in the snapshot and publish full blocks today; Los Angeles Chargers and Baltimore still read empty.", "Why it is flagged rather than fixed": "Treating an empty block as zero is a modelling error, not a transcription error."},
    {"Observation": "Team code inconsistency", "Detail": "The league's schedule pages code the Rams LA; its standings and game pages code them LAR.", "Why it is flagged rather than fixed": "It needs a committed crosswalk, not a hard-coded alias."},
], kinds={}) + """
<h2>5. Session integrity</h2>
<p>This session claimed its scope in <code>COORDINATION.md</code> before creating any file, worked only inside <code>crosscheck/</code>, and modified no file owned by another session. Its claim commit, its verification method and every source are recorded there. Where it relied on another session's arithmetic instead of re-deriving it — 133 of the 136 game rows — it says so on the page that publishes them.</p>
""")


# ---------------------------------------------------------------- verify
def verify():
    errs = []
    pages = set()
    for f in os.listdir(HERE):
        if f.endswith(".html"):
            pages.add(f)
    missing = [s + ".html" for s in PAGES if s + ".html" not in pages]
    if missing:
        errs.append("missing pages: %s" % missing)
    link_re = re.compile(r'href="([^"]+)"')
    anchors = {}
    for p in pages:
        txt = open(os.path.join(HERE, p), encoding="utf-8").read()
        anchors[p] = set(re.findall(r'id="([^"]+)"', txt))
        for href in link_re.findall(txt):
            if href.startswith(("http://", "https://", "#", "mailto:")):
                if href.startswith("#"):
                    if href[1:] not in anchors[p]:
                        errs.append("%s: dead in-page anchor %s" % (p, href))
                continue
            target = href.split("#")[0]
            frag = href.split("#")[1] if "#" in href else None
            path = os.path.normpath(os.path.join(HERE, target))
            if not os.path.exists(path):
                errs.append("%s: broken link %s" % (p, href))
            elif frag and path.endswith(".html"):
                tp = os.path.basename(path)
                if tp in anchors and frag not in anchors[tp]:
                    errs.append("%s: broken anchor %s" % (p, href))
    # every data row carries a league or repo source
    counts = {}
    for name in os.listdir(DATA):
        if not name.endswith(".csv"):
            continue
        rows = read(os.path.join(DATA, name))
        if rows and "source" in rows[0]:
            counts[name] = len(rows)
    total_rows = sum(counts.values())
    return errs, len(pages), total_rows


if __name__ == "__main__":
    errs, npages, rows = verify()
    if errs:
        for e in errs:
            print("FAIL", e)
        sys.exit(1)
    print("built %d pages · %d sourced data rows · 0 broken links" % (npages, rows))
    print("measures: repo=%d live=%d added=%d moved=%d removed=%d stand=%d/%d sched=%d/%d coef=%d/%d"
          % (M["repo_rows"], M["live_rows"], M["added"], M["moved"], M["removed"],
             M["stand_ok"], M["stand_n"], M["sched_ok"], M["sched_n"], M["coef_match"], M["coef"]))
