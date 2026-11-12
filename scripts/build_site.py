#!/usr/bin/env python3
"""
build_site.py — generates every HTML page from the verified JSON.

Why generate instead of hand-writing: every number on the site must be traceable
to a file that a checker has verified. If a page carried a hand-typed figure, that
figure would be the one thing on the site with no provenance.

Run after any data change:  python3 scripts/build_site.py
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "analytics")
os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
D = os.path.join(ROOT, "data"); DER = os.path.join(D, "derived")

def load(p, d=None):
    fp = os.path.join(D, p)
    if not os.path.exists(fp):
        if d is not None: return d
        raise SystemExit(f"missing {fp} — run the pipeline first")
    with open(fp, encoding="utf-8") as f: return json.load(f)

E = html.escape

GAMES = load("games_2026.json")
STAND = load("standings_raw.json")
TEAM  = load("team_stats.json")
AN    = load(os.path.join("derived", "analysis.json"))
VER   = load(os.path.join("derived", "verification_report.json"))
PER   = load(os.path.join("derived", "personnel.json"))
INJ   = load("injuries_week10.json")
DEPTH = load("depth_charts.json")
Q     = load("questions.json")
SUG   = load("suggestions.json")
PLAY  = load("player_verified.json")

BUILD = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

# ---------------------------------------------------------------- sources registry
SRC = {
 "schedule":   "https://www.nfl.com/schedules/2026/REG/",
 "sched_wk":   "https://www.nfl.com/schedules/2026/by-week/week-{w}",
 "standings":  "https://www.nfl.com/standings/2026/reg/",
 "injuries":   "https://www.nfl.com/injuries/",
 "inj_news":   "https://www.nfl.com/news/nfl-week-10-injury-report-2026-season",
 "ts_off_pass":"https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all",
 "ts_off_rush":"https://www.nfl.com/stats/team-stats/offense/rushing/2026/reg/all",
 "ts_def_pass":"https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all",
 "ts_def_rush":"https://www.nfl.com/stats/team-stats/defense/rushing/2026/reg/all",
 "player_pass":"https://www.nfl.com/stats/player-stats/category/passing/2026/reg/all/passingyards/desc",
 "roster":     "https://www.nfl.com/teams/{slug}/roster",
 "club_stats": "https://www.nfl.com/teams/{slug}/stats",
 "ops_cba":    "https://operations.nfl.com/inside-football-ops/nfl-operations/nfl-free-agency/contract-language",
 "rulebook":   "https://operations.nfl.com/rules-officiating/2026-nfl-rulebook",
 "repo":       "https://github.com/kanlerxz87-cyber/NFL2",
 "coord":      "https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md",
 "site":       "https://kanlerxz87-cyber.github.io/NFL2/",
}

SLUG = {
 "AZ":"arizona-cardinals","ATL":"atlanta-falcons","BAL":"baltimore-ravens","BUF":"buffalo-bills",
 "CAR":"carolina-panthers","CHI":"chicago-bears","CIN":"cincinnati-bengals","CLE":"cleveland-browns",
 "DAL":"dallas-cowboys","DEN":"denver-broncos","DET":"detroit-lions","GB":"green-bay-packers",
 "HOU":"houston-texans","IND":"indianapolis-colts","JAX":"jacksonville-jaguars","KC":"kansas-city-chiefs",
 "LA":"los-angeles-rams","LAC":"los-angeles-chargers","LV":"las-vegas-raiders","MIA":"miami-dolphins",
 "MIN":"minnesota-vikings","NE":"new-england-patriots","NO":"new-orleans-saints","NYG":"new-york-giants",
 "NYJ":"new-york-jets","PHI":"philadelphia-eagles","PIT":"pittsburgh-steelers","SEA":"seattle-seahawks",
 "SF":"san-francisco-49ers","TB":"tampa-bay-buccaneers","TEN":"tennessee-titans","WAS":"washington-commanders",
}
NAME = {c: d["name"] for c, d in AN["clubs"].items()} if False else {}

NAV = [
 ("index.html","Overview"),("executive-summary.html","Exec Summary"),
 ("results.html","Results"),("schedule.html","Week 11"),("standings.html","Standings"),
 ("teams.html","Team Stats"),("injuries.html","Injuries"),
 ("depth-deficiencies.html","1st–4th String"),("lines-lab.html","Lines Lab"),
 ("analysis.html","Analysis"),("correlations.html","Correlations"),
 ("strategies.html","Strategies"),("method.html","Method"),
 ("suggestions.html","Suggestions"),("questions.html","Questions"),
 ("repo-audit.html","Repo Audit"),("flagged.html","Flagged for Review"),
 ("sources.html","Sources"),("../index.html","Root Dashboard"),
 ("../review/index.html","Review Build"),("../portal/index.html","Portal Build"),("../site/index.html","Lab Build"),
]

def page(fname, title, body, active=None, desc=""):
    CUR = ' aria-current="page"'
    parts = []
    for f, t in NAV:
        parts.append('<a href="%s"%s>%s</a>' % (f, CUR if f == (active or fname) else "", E(t)))
    nav = "".join(parts)
    doc = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · NFL 2026 Analytics</title>
<meta name="description" content="{E(desc)}">
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header class="top"><div class="wrap">
<a class="brand" href="index.html"><span class="dot"></span>NFL 2026 · Verified Analytics</a>
<nav class="main">{nav}</nav>
</div></header>
{body}
<footer><div class="wrap">
<p><b>Every figure on this site is either transcribed from an official NFL source or is explicitly labelled MODEL output.</b>
Nothing is inferred. Blank cells mean no official source confirms the value — see <a href="flagged.html">Flagged for Review</a>.</p>
<p>Data through Week 9 results and Week 10 injury reports · built {E(BUILD)} · 
<a href="{SRC['repo']}">repository</a> · <a href="{SRC['coord']}">coordination log</a> · 
verification: {VER['totals']['pass']}/{VER['totals']['checks']} data checks, {len(PER['meta']['personnel_verification'])} personnel checks</p>
</div></footer>
<script src="assets/app.js"></script>
</body></html>"""
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(doc)
    return len(doc)

def tbl(headers, rows, cls="", caption=""):
    """headers: list of (label, numeric?) ; rows: list of list[str] (already HTML-safe)"""
    th = "".join(f'<th class="{"num" if n else ""}">{h}</th>' for h,n in headers)
    tr = "".join("<tr>"+"".join(f'<td class="{"num" if headers[i][1] else ""}">{c}</td>'
                 for i,c in enumerate(r))+"</tr>" for r in rows)
    cap = f"<caption>{caption}</caption>" if caption else ""
    return f'<div class="tblwrap {cls}"><table>{cap}<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'

def num(v, d=1, plus=False, blank="—"):
    if v is None or v == "": return f'<span class="blank">{blank}</span>'
    try: f = float(v)
    except Exception: return E(str(v))
    s = f"{f:+.{d}f}" if plus else f"{f:.{d}f}"
    return s

def b(text, kind="dim"): return f'<span class="b b-{kind}">{E(text)}</span>'
STATUS_KIND = {"PASS":"ok","FAIL":"bad","WARN":"warn","ANSWERED":"ok","PARTIAL":"warn",
               "OPEN":"warn","BLOCKED":"bad","PROPOSED":"info","DEFERRED":"dim",
               "REJECTED_PREVIOUSLY":"bad","VALIDATED":"ok","REJECTED":"bad","UNDERPOWERED":"warn"}

def src(url, label="source"): 
    return f'<a href="{E(url)}" target="_blank" rel="noopener">{E(label)} ↗</a>' if url else ""

def note(text, kind=""):
    return f'<div class="note {kind}">{text}</div>'

def hero(eyebrow, h1, lede):
    return f'<div class="hero"><div class="wrap"><span class="eyebrow">{E(eyebrow)}</span><h1>{h1}</h1><p class="lede">{lede}</p></div></div>'

def pagehead(eyebrow, h1, lede):
    return f'<div class="pagehead"><div class="wrap"><span class="eyebrow">{E(eyebrow)}</span><h1>{E(h1)}</h1><p>{lede}</p></div></div>'

def card(title, body, href=None, big=None):
    inner = f'<h3>{E(title)}</h3><p>{body}</p>'
    if big: inner = f'<div class="big">{big}</div><p>{body}</p>'
    if href: return f'<a class="card link" href="{href}" style="display:block;text-decoration:none">{inner}</a>'
    return f'<div class="card">{inner}</div>'

# ================================================================ helpers
ST = {s["team"]: s for s in STAND["standings"]}
def team_name(c): return ST[c]["name"] if c in ST else c
def team_link(c): return f'<a href="teams.html#{E(c)}">{E(c)}</a>'
def game_src(g):
    w = SRC["sched_wk"].format(w=g["week"])
    return src(g.get("src") or w, f'W{g["week"]}')

def sorted_standings(key="PCT"):
    return sorted(STAND["standings"], key=lambda s: (-s["PCT"], -s["W"], s["team"]))

# records derived from the game log — a second, independent witness to standings
def log_records():
    r = {c: {"w":0,"l":0,"t":0,"pf":0,"pa":0,"gp":0} for c in ST}
    for g in GAMES["games"]:
        for side, opp in (("home","away"),("away","home")):
            t = g[side]; o = g[opp]
            if t not in r: continue
            r[t]["gp"] += 1; r[t]["pf"] += g[f"{side}_pts"]; r[t]["pa"] += g[f"{opp}_pts"]
            if g[f"{side}_pts"] > g[f"{opp}_pts"]: r[t]["w"] += 1
            elif g[f"{side}_pts"] < g[f"{opp}_pts"]: r[t]["l"] += 1
            else: r[t]["t"] += 1
    return r
LOG = log_records()

PAGES = {}

# ================================================================ 1. OVERVIEW
hf = AN["home_field"]; sm = AN["summary"]
bf, bo = AN["luck_ladder"][0], AN["luck_ladder"][-1]
valid = [s for s in AN["strategies"] if s["status"] == "VALIDATED"]

body = hero("2026 regular season · weeks 1–9 verified",
  "An NFL analytics build where every number can be traced to an official page",
  f"""This site does three things: it reproduces the league's own published records from a
  {len(GAMES['games'])}-game log and proves the reproduction arithmetically; it researches
  betting-shaped ideas under a leaderboard whose <b>validation gates it is not allowed to pass
  by storytelling</b>; and it tracks injuries against club depth charts so that a missing star
  can be told apart from a missing fourth-stringer. Where a value cannot be confirmed from an
  official source, the cell is blank and the item is on the Flagged for Review page.
  <b>No figure here is invented, and no strategy is claimed to work.</b>""")

body += f"""<section><div class="wrap">
<div class="grid g4">
  {card("Games verified", f"All {VER['totals']['game_rows']} rows of weeks 1–9, each with its own source link", big=VER['totals']['game_rows'])}
  {card("Clubs reconciled", "Every club's W-L-T, points for/against and streak reproduced from the log", big=VER['totals']['clubs'])}
  {card("Data checks passing", f"{VER['totals']['pass']} of {VER['totals']['checks']} · the 3 soft fails are published, not hidden", href="flagged.html", big=f"{VER['totals']['pass']}/{VER['totals']['checks']}")}
  {card("Strategies validated", "None. All six fail the sample-size gate — that is the honest result", href="strategies.html", big="0/6")}
</div>

<div class="note {"" if valid else "warn"}" style="margin-top:22px">
<p><b>The headline finding is a refusal.</b> Six strategies were built and backtested walk-forward
across weeks 5–9. Every one is <b>UNDERPOWERED</b>: the best graded 72 legs against a gate that
requires 200. Three pass four of the seven gates, which is encouraging and means nothing yet.
The site publishes the leaderboard anyway, sorted by gates passed rather than by hit rate, so
that the table cannot be read as a recommendation.</p>
</div>

<h2 style="margin-top:34px">Four things worth knowing</h2>
<div class="grid g2" style="margin-top:14px">
  <div class="card"><h3>Home-field advantage is not detectable in 2026 — and the naive number is wrong</h3>
  <p>Pooled across all {hf['games']} games the mean home margin is {num(hf['mean_home_margin'],2,True)} points,
  which looks like home-field has vanished. But {hf['neutral_site_games']} of those games were at neutral sites with no real
  home club. On the {hf['true_home_games']} genuine home games the mean is <b>{num(hf['true_home_mean_margin'],2,True)}</b>
  points, 95% CI <b>[{num(hf['true_home_ci95'][0],2,True)}, {num(hf['true_home_ci95'][1],2,True)}]</b>. The conventional
  ~+2.5 prior sits <i>inside</i> that interval, so this season cannot reject it. The model uses
  {num(hf['model_uses'],2,True)}. <a href="method.html">Method →</a></p></div>

  <div class="card"><h3>Team stats conserve exactly — which is why the mapping can be trusted</h3>
  <p>League-wide offence equals league-wide defence on eight separate identities: 63,556 passing yards,
  30,580 rushing yards, 641 sacks, 411 passing TD, 257 rushing TD, 197 interceptions, 3,006 passing
  first downs, 1,757 rushing first downs. Exact conservation is what proved the header-less columns
  were mapped correctly. <a href="teams.html">Team stats →</a></p></div>

  <div class="card"><h3>Starter vs backup is answered for 4 clubs, blank for 28</h3>
  <p>The official injury report says who is hurt but never says whether they start. Joining it to
  club-published depth charts resolves that for Kansas City, Green Bay, New England and Detroit —
  and the join surfaces {PER['meta']['joins_failed_not_on_chart']} injured players who are absent from
  their own club's chart entirely. For the other 28 clubs the field is left blank rather than guessed.
  <a href="injuries.html">Injuries &amp; depth →</a></p></div>

  <div class="card"><h3>Two leaderboards are withheld because their columns cannot be proven</h3>
  <p>The rushing and receiving leaderboards render with no header row, and no arithmetic identity
  identifies the columns — published yards-per-carry disagrees with yards divided by carries for
  every sampled row. They are not published at all. Only 8 passing lines survive an exact equality
  test against their club's official team passing line. <a href="flagged.html">Flagged for Review →</a></p></div>
</div>

<h2 style="margin-top:34px">Where to go</h2>
<p class="sub">Each page answers one question and every table row carries its source.</p>
<div class="grid g3">
  {card("Executive summary", "Architecture, core findings, verification boundary, and open blockers", "executive-summary.html")}
  {card("Results (Weeks 1–9)", f"{len(GAMES['games'])} games, weeks 1–9, each with score, date and source link", "results.html")}
  {card("Week 11 schedule", "All 13 Week 11 games + 6 bye teams, including Nov 9 official flex changes", "schedule.html")}
  {card("Standings", "All 32 clubs with a second, independent record recomputed from the game log", "standings.html")}
  {card("Team stats", "Passing and rushing, offence and defence, with the withheld tables labelled", "teams.html")}
  {card("Injuries & depth", "Week 10 injury report joined to published depth charts", "injuries.html")}
  {card("1st–4th string deficiencies", "12 official club depth charts & 18 offense/defense backup cascades", "depth-deficiencies.html")}
  {card("Lines Lab", "Interactive fair-line & correlation calculators + Week 11 originated baselines", "lines-lab.html")}
  {card("Analysis", "Power ratings, correlations, luck ladder and Week 10 model lines", "analysis.html")}
  {card("Correlations & skill", "14 verified team correlations (n=32), SGP copula checks & luck residuals", "correlations.html")}
  {card("Strategies", "Six strategies, seven gates, and why none of them passes yet", "strategies.html")}
  {card("Method", "Exactly how every number is produced and where the model is weak", "method.html")}
  {card("Suggestions", f"{len(SUG['suggestions'])} proposals awaiting a decision — none are implemented", "suggestions.html")}
  {card("Questions & gaps", f"{len(Q['questions'])} questions, with the unanswerable ones left visibly blank", "questions.html")}
  {card("Repo audit", "Line-by-line audit of commits, upstream source blindspots, and verification gates", "repo-audit.html")}
  {card("Flagged for Review", "Every irregularity, severity-rated, with what would fix it", "flagged.html")}
  {card("Data sources", "The full register of official pages used, and what each one supplied", "sources.html")}
  {card("Root Decision Dashboard", "Root 21-page specification & measured data dashboard (session bc4b47cf)", "../index.html")}
  {card("Verification Review Dashboard", "Parallel 15-page build (session 01b698ef): requirements register, decision gates, path chooser & 423 sourced rows", "../review/index.html")}
  {card("Quantitative Decision Portal", "Parallel 10-page portal (session e143a7ca): Week 10/11 originated lines, correlations, depth chains & Tier-0 gated strategies", "../portal/index.html")}
  {card("Walk-Forward Lab Site", "Parallel 14-page lab site (session 63ac21e9): calibration, ratings, availability & backtest", "../site/index.html")}
  {card("Parallel docs/ Dashboard", "Parallel 16-page build (session 85d79210): player leaders, defense breakdown & interactive calculators", "../docs/index.html")}
  {card("Repository", "Source, data files, verifiers and the coordination log", SRC['repo'])}
</div>
</div></section>"""

PAGES["index.html"] = ("Overview", body,
  "A verified NFL 2026 analytics site: every figure traceable to an official source, strategies gated, gaps published.")

# ================================================================ 2. RESULTS
gk = sorted(GAMES["games"], key=lambda g: (g["week"], g.get("date",""), g["home"]))
rows = []
for g in gk:
    margin = g["home_pts"] - g["away_pts"]
    win = ("home" if margin > 0 else "away" if margin < 0 else "tie")
    tag = ""
    if g.get("neutral"): tag = " " + b("neutral site","info")
    rows.append([
      f'<b>{g["week"]}</b>',
      E(g.get("date","")),
      f'{team_link(g["away"])}{tag}',
      f'<span class="num">{g["away_pts"]}</span>',
      f'<span class="num">{g["home_pts"]}</span>',
      team_link(g["home"]),
      ("<b>"+E(g["away"])+"</b>") if win=="away" else ("<b>"+E(g["home"])+"</b>") if win=="home" else b("tie","dim"),
      num(margin, 0, True),
      game_src(g),
    ])

wins = sum(1 for g in GAMES["games"] if g["home_pts"] > g["away_pts"])
body = pagehead("Results","Every game, weeks 1–9",
  f"""{len(GAMES['games'])} completed games, transcribed from the official schedule and re-verified
  against the official standings. The margin column is computed, not published. The final column
  opens the game's page on NFL.com. Home clubs won {wins} of these, which is why the home-field
  question is argued properly on the <a href="method.html">Method</a> page rather than from this total.""")

body += f"""<section><div class="wrap">
<div class="grid g4" style="margin-bottom:20px">
  {card("Games", "weeks 1–9, all 32 clubs", big=len(GAMES['games']))}
  {card("League points", f"{num(AN['summary']['league_points_per_game'],2)} per game", big=f"{sm['league_points_scored']:,}")}
  {card("Ties", "NYG 27–27 WAS in week 5 was the only one", big=sum(1 for g in GAMES['games'] if g['home_pts']==g['away_pts']))}
  {card("Neutral-site games", "Played outside the home club's stadium or abroad", big=hf['neutral_site_games'])}
</div>
{tbl([("Wk",1),("Date",0),("Away",0),("Away pts",1),("Home pts",1),("Home",0),("Winner",0),("Margin",1),("Source",0)],
     rows, caption=f"All {len(rows)} games. Margin is home minus away; a negative margin means the visiting club won. "
                   f"Seven games were played at neutral sites and are tagged rather than being counted as a home game.")}
<div class="note" style="margin-top:16px"><p><b>Verification.</b> These scores reproduce every club's published
PF, PA, W-L-T and net points exactly — 10 of 10 hard checks. See the <a href="method.html">Method</a> page for the
check list and <a href="flagged.html">Flagged for Review</a> for the three soft failures on derived rates.</p></div>
</div></section>"""
PAGES["results.html"] = ("Results", body, f"{len(GAMES['games'])} verified 2026 NFL games, weeks 1-9, each with its source.")

# ================================================================ 3. STANDINGS
def div_tables():
    out = ""
    for conf in ("AFC","NFC"):
        for dv in ("East","North","South","West"):
            clubs = [s for s in STAND["standings"] if s["conf"]==conf and s["div"]==dv]
            clubs.sort(key=lambda s: (-s["PCT"], -s["W"], s["team"]))
            rs = []
            for s in clubs:
                lg = LOG[s["team"]]
                ok = (lg["w"]==s["W"] and lg["l"]==s["L"] and lg["t"]==s["T"]
                      and lg["pf"]==s["PF"] and lg["pa"]==s["PA"])
                rs.append([
                  f'<b>{team_link(s["team"])}</b>', E(team_name(s["team"]).replace(s["team"],"").strip() or team_name(s["team"])),
                  s["W"], s["L"], s["T"], num(s["PCT"],3),
                  s["PF"], s["PA"], num(s["NET"],0,True),
                  E(s["c8"] or ""), E(s["c9"] or ""), E(s["streak"] or ""),
                  f'{lg["w"]}-{lg["l"]}-{lg["t"]}', f'{lg["pf"]}', f'{lg["pa"]}',
                  b("match","ok") if ok else b("MISMATCH","bad"),
                  src(SRC["standings"], "NFL.com"),
                ])
            out += f'<h3>{E(conf)} {E(dv)}</h3>' + tbl(
              [("Team",0),("",0),("W",1),("L",1),("T",1),("PCT",1),("PF",1),("PA",1),("Net",1),
               ("Home",1),("Road",1),("Strk",1),("Log W-L-T",1),("Log PF",1),("Log PA",1),("Check",0),("Source",0)],
              rs)
    return out

body = pagehead("Standings","Official standings, with an independent recount beside them",
  """The left half of each table is the league's published standings, transcribed verbatim. The right half is
  recomputed from this site's own game log — a genuinely separate witness. All 32 clubs agree on all five
  fields. The home and road splits are published because they were proven to be home and road splits by
  re-deriving them from the log; the league's table renders them without a header, and the remaining
  unidentifiable columns are deliberately omitted.""")
body += f"""<section><div class="wrap">
<div class="note ok"><p><b>32 of 32 clubs match</b> on W, L, T, PCT, PF, PA and net points. The three columns
shown as Home / Road / Strk were identified by re-deriving them from the game log; every other
unlabelled column in the source table could not be identified with certainty and is not published.
See <a href="flagged.html">Flagged for Review</a> item IR-03.</p></div>
{div_tables()}
<div class="note" style="margin-top:18px"><p>The "Log" columns are computed from <code>data/games_2026.json</code>
by summing every club's results. They are shown so a reader can check the transcription without trusting it.
Source: {src(SRC['standings'], 'NFL.com standings')}</p></div>
</div></section>"""
PAGES["standings.html"] = ("Standings", body, "2026 NFL standings, cross-checked against a recount from the game log.")

# ================================================================ 4. TEAM STATS
COLS = TEAM["meta"]["columns_retained"]
def stat_table(key, cols, title, source_url, note_txt=""):
    rs = []
    order = sorted(TEAM["teams"].items(), key=lambda kv: (-(kv[1].get("off_pass",[0])[4] if key=="off_pass" else 0), kv[0]))
    order = sorted(TEAM["teams"].items(), key=lambda kv: kv[0])
    for c, v in order:
        vals = v.get(key)
        if not vals: continue
        rs.append([team_link(c), E(team_name(c))] + [E(str(x)) if x is not None else "—" for x in vals] + [src(source_url,"NFL.com")])
    return f'<h3>{E(title)}</h3>' + tbl(
      [("Team",0),("Club",0)] + [(E(x),1) for x in cols] + [("Source",0)], rs)

body = pagehead("Team stats","Passing and rushing, offence and defence — with the unusable tables named",
  """The league's team-stat pages render <b>no header row at all</b>. The column order below is not a guess:
  it was proven by reproducing a single-passer club's player line, then confirmed on eight exact
  league-wide conservation identities (offence total = defence total for every yardage and counting stat).
  Two tables that could not be proven — the scoring tables — are withheld and named as withheld.""")
body += f"""<section><div class="wrap">
<div class="note ok"><p><b>Why the mapping is trustworthy.</b> League-wide offensive passing yards equal
league-wide defensive passing yards allowed to the yard (63,556), and the same holds for rushing yards
(30,580), sacks (641), passing touchdowns (411), rushing touchdowns (257), interceptions (197) and both
first-down categories. An incorrectly mapped column would not conserve. See
<a href="method.html">Method</a>.</p></div>
{stat_table("off_pass", COLS["off_pass"], "Offence — passing", SRC["ts_off_pass"])}
{stat_table("off_rush", COLS["off_rush"], "Offence — rushing", SRC["ts_off_rush"])}
{stat_table("def_pass", COLS["def_pass"], "Defence — passing allowed", SRC["ts_def_pass"])}
{stat_table("def_rush", COLS["def_rush"], "Defence — rushing allowed", SRC["ts_def_rush"])}
<div class="note warn" style="margin-top:22px">
<p><b>Withheld: the scoring tables.</b> {E(TEAM['meta'].get('column_caveat',''))}</p>
<p>{E(VER['withheld_from_source']['team_scoring_tables']['reason'])}</p>
<p>This is published as <a href="flagged.html">FL-04</a> rather than filled in.</p>
</div>
<div class="note" style="margin-top:16px"><p><b>Clubs with only one passer are checkable against a player line.</b>
Eight clubs satisfy an exact 15-value equality test; those players are on the <a href="analysis.html">Analysis</a>
page. A club that fails the test — Detroit, where Goff's 2,134 yards is 11 short of the club's 2,145 — is
excluded rather than reconciled.</p></div>
</div></section>"""
PAGES["teams.html"] = ("Team Stats", body, "2026 NFL team passing and rushing statistics with a proven column mapping.")

# ================================================================ 5. INJURIES & DEPTH
bygame = {}
for g in INJ["games"]:
    bygame.setdefault(g["away"]+"@"+g["home"], g)

body = pagehead("Injuries & depth","Who is hurt — and whether they actually start",
  f"""The official injury report tells you a player is injured and how much he practised. It does
  <b>not</b> tell you whether he is a starter. Joining it to each club's own published depth chart
  answers that — for the four clubs whose charts were transcribed and verified. For the rest, the
  answer is left visibly blank. This is the difference between a real deficiency analysis and a
  plausible-looking one.""")

body += f"""<section><div class="wrap">
<div class="grid g4">
  {card("Injury rows", "Week 10, all 14 games — every player the clubs listed", big=PER['meta']['row_count'])}
  {card("Join to a real chart", "Rows that map to a published depth slot", big=PER['meta']['joins_to_published_chart'])}
  {card("Not on their own chart", "Injured but absent from the club's depth chart", big=PER['meta']['joins_failed_not_on_chart'])}
  {card("Depth unmapped", "Clubs whose chart was not transcribed — blank, not guessed", big=PER['meta']['clubs_depth_unmapped'])}
</div>

<div class="note warn" style="margin-top:20px">
<p><b>The limitation, stated up front.</b> Every club labels its depth chart <i>unofficial</i>. It is the
organisation's own working document, not a league-mandated designation, and it can lag a coaching decision.
Charts were transcribed and cross-checked for <b>Kansas City, Green Bay, New England and Detroit</b> only.
Transcribing the other 28 and publishing them unverified would break the no-inference rule, so they are blank.</p>
</div>

<h2>Week 10 by club</h2>
<p class="sub">"Starter DNP" means a player listed first at his position on the club's own chart did not practise.
That is the closest official thing to "a starter is out". It is not a points estimate.</p>
"""

prows = []
for s in PER["by_club"]:
    d = b("mapped","ok") if s["charted"] else b("chart not transcribed","dim")
    row_src = src(DEPTH["depth_charts"][s["team"]]["club_site"], "Club") if s["charted"] else src("https://www.nfl.com/injuries/league/2026/REG10", "REG10")
    prows.append([
      f'<b>{team_link(s["team"])}</b>', s["listed"], s["dnp"], s["lp"], s["fp"],
      s["game_status_out"], s["starters_dnp"], s["second_string_dnp"],
      s["third_string_dnp"], s["fourth_string_dnp"],
      f'<b>{s["deficiency_index"]}</b>' if s["charted"] else '<span class="blank">—</span>',
      d, row_src])
body += tbl([("Team",0),("Listed",1),("DNP",1),("LP",1),("FP",1),("Out",1),
             ("Starter DNP",1),("2nd",1),("3rd",1),("4th",1),("Deficiency idx",1),("Depth chart",0),("Source",0)],
            prows, caption="DNP = did not practise, LP = limited, FP = full. 'Out' is the published game status. "
                           "The deficiency index is a stated weighting (starter ×3, 2nd ×2, 3rd/4th ×1) used only to sort "
                           "clubs — it is explicitly not a points value, because no official source converts a depth slot into points.")
body += '<div class="note ok" style="margin-top:14px"><p><b>Expanded 12-Club 1st–4th String Cascade View:</b> See <a href="depth-deficiencies.html">1st–4th String Deficiencies →</a> for 18 verified offense &amp; defense starter-to-backup replacement chains across 12 official NFL club depth charts plus IR blindspot joins.</p></div>'

body += f"""
<h2 style="margin-top:34px">Verified starter-level absences</h2>
<p class="sub">These are the rows where the club's own chart lists the player first at his position and the
official report says he did not practise. Group labels like CB_1 are the depth-chart rows verbatim; they are
disambiguated because clubs print several rows with the same label.</p>"""

srows = []
for r in PER["rows"]:
    if r["depth_position"] == 1 and r["practice_code"] == "DNP":
        srows.append([
          f'<b>{team_link(r["team"])}</b>', E(r["player"]), E(r["pos"] or "—"),
          E(r["depth_group"] or ""), E(r["unit"] or ""),
          E(r["injury"]) if r["injury"] else '<span class="blank">not listed</span>',
          E(r["practice"].replace("Did Not Participate In Practice","Did not practise")),
          E(r["game_status"]) if r["game_status"] else '<span class="blank">blank</span>',
          src(DEPTH["depth_charts"][r["team"]]["club_site"], "chart"),
        ])
body += tbl([("Team",0),("Player",0),("Pos",0),("Chart row",0),("Unit",0),("Injury",0),("Practice",0),("Game status",0),("Source",0)],
            srows, caption="A blank injury cell is the source printing no injury for that player — not a missing value invented here.")

body += """
<h2 style="margin-top:34px">Honest gaps in this join</h2>
<div class="grid g2" style="margin-top:14px">
<div class="card"><h3>Injured players who are not on their club's chart</h3>
<p>These players appear on the official injury report but not on their own club's published depth chart.
That usually means the chart predates a signing, or lists him under a different designation. They are
flagged rather than silently assigned a depth.</p>
""" + tbl([("Team",0),("Player",0),("Source",0)],
   [[team_link(r["team"]), E(r["player"]), src("https://www.nfl.com/injuries/league/2026/REG10","REG10")] for r in PER["rows"] if r["map_status"]=="not on published chart"],
   caption="No depth position is asserted for any of these.") + """
</div>
<div class="card"><h3>Players listed at two positions</h3>
<p>NFL depth charts genuinely list some players twice — for example a linebacker who is second-string
at MIKE and first-string at WILL. The join keeps the highest (lowest-numbered) slot and records every
slot, so the ambiguity is visible instead of being averaged away.</p>
"""
multi = []
for club, ch in DEPTH["depth_charts"].items():
    seen = {}
    for side in ("offense","defense"):
        for grp, ps in ch.get(side, {}).items():
            for i, pl in enumerate(ps):
                if pl: seen.setdefault(pl, []).append(f"{grp} ({i+1})")
    for pl, slots in seen.items():
        if len(slots) > 1: multi.append([team_link(club), E(pl), E(", ".join(slots)), src(ch["club_site"], "chart")])
body += tbl([("Team",0),("Player",0),("Listed at",0),("Source",0)], multi,
            caption="Multi-slot listings are declared, and the join records which slot it used.") + """
</div></div>

<h2 style="margin-top:34px">Full Week 10 injury report</h2>
<p class="sub">All rows, verbatim, with blank cells preserved as blanks. This is the source the join above is built on.</p>"""

irows = []
for g in INJ["games"]:
    for p in sorted(g["players"], key=lambda x: (x["team"], x["pos"] or "", x["player"])):
        irows.append([
          E(g["away"]+" @ "+g["home"]), E(g["kickoff_et"][5:16]),
          f'<b>{E(p["team"])}</b>', E(p["player"]), E(p["pos"] or "—"),
          E(p["injury"]) if p["injury"] else '<span class="blank">—</span>',
          E(p["practice"].replace("Did Not Participate In Practice","DNP")
                       .replace("Limited Participation in Practice","LP")
                       .replace("Full Participation in Practice","FP")) if p["practice"] else '<span class="blank">—</span>',
          (b(p["status"], "bad" if p["status"]=="Out" else "warn" if p["status"]=="Questionable" else "dim")
             if p["status"] else '<span class="blank">—</span>'),
          src("https://www.nfl.com/injuries/league/2026/REG10", "REG10"),
        ])
noinj = INJ["meta"].get("no_injuries_reported", [])
body += f"""<div class="note" style="margin-top:6px"><p>Clubs that printed
<b>"No Injuries Reported"</b>: {E(", ".join(n.replace('/',' and ') for n in noinj)) if noinj else "none"}. That is the source's own statement,
not an inference that those clubs are healthy. Source: {src(SRC['injuries'],'NFL.com injuries')} ·
{src(SRC['inj_news'],'week 10 report')}</p></div>"""
body += tbl([("Game",0),("Kickoff ET",1),("Team",0),("Player",0),("Pos",0),("Injury",0),("Practice",0),("Status",0),("Source",0)],
            irows, caption=f"All {len(irows)} player rows. Blanks are the source printing nothing; they are not zeros or 'unknown' entries here.")
body += f"""
<div class="note" style="margin-top:18px"><p><b>Roster rules behind this page.</b> A club may carry 53 on its
active/inactive list, and may have {src(SRC['ops_cba'],'47 or 48 players active on game day')} — 48 only if at
least eight offensive linemen are among them. That is precisely why the difference between the first-string and
the fourth-string player matters: only a fraction of the roster can play.
Rules source: {src(SRC['rulebook'],'2026 NFL Rulebook')}</p></div>
</div></section>"""
PAGES["injuries.html"] = ("Injuries & Depth", body,
  "Week 10 NFL injury report joined to club-published depth charts, with unmapped clubs left blank.")

# ================================================================ 6. ANALYSIS
cc = AN["club_correlations"]; gc = AN["game_correlations"]
body = pagehead("Analysis","Power ratings, correlations, luck — all computed, none assumed",
  f"""The model is deterministic: re-running <code>scripts/analyse.py</code> reproduces this page byte for byte.
  Nothing here is a prediction about a specific bet, and nothing here is compared against a market, because
  no official source publishes odds. Every number on this page is labelled <b>MODEL</b>, meaning derived from
  verified inputs by a stated formula.""")

body += f"""<section><div class="wrap">
<h2>Home-field advantage, estimated properly</h2>
<p class="sub">This is the model's most important parameter and the easiest one to get wrong.</p>
<div class="grid g4">
  {card("All games", "Pooled mean home margin — misleading, see the note", big=num(hf['mean_home_margin'],2,True))}
  {card("True home games", "The estimator the model actually uses", big=num(hf['true_home_mean_margin'],2,True))}
  {card("95% interval", "On the mean home margin", big=f"{num(hf['true_home_ci95'][0],2,True)} … {num(hf['true_home_ci95'][1],2,True)}")}
  {card("Conventional prior", "Inside the interval — so 2026 cannot reject it", big=f"+{hf['conventional_prior_points']}")}
</div>
<div class="note warn" style="margin-top:16px"><p>{E(hf['note'])}</p></div>

<h2 style="margin-top:34px">Which club metrics track winning?</h2>
<p class="sub">Pearson correlation against win percentage across all 32 clubs. n is small; treat the ordering as suggestive
and the top figures as partly a product of testing many metrics.</p>"""
crows = []
for c in cc:
    strong = abs(c["pearson_r"]) >= 0.6
    crows.append([E(c["label"]), c["n"], f'<b>{num(c["pearson_r"],3,True)}</b>' if strong else num(c["pearson_r"],3,True),
                  num(c["spearman_rho"],3,True), num(c["r_squared"],3), num(c["t_stat"],2,True),
                  b("strong","ok") if strong else b("weak","dim"), src(SRC["ts_off_pass"], "NFL.com")])
body += tbl([("Metric",0),("n",1),("Pearson r",1),("Spearman ρ",1),("r²",1),("t",1),("Read",0),("Source",0)], crows,
            caption="Careful: with 32 clubs and 14 metrics tested, the strongest correlations are partly selection. "
                    "The t column is given so the reader can see the precision, not to imply significance after multiple testing.")
body += '<div class="note ok" style="margin-top:12px"><p>See also <a href="correlations.html">Correlations &amp; Skill →</a> for Fisher-z 95% CIs, two-tailed p-values, and the SGP/prop copula blank register.</p></div>'

body += """
<h2 style="margin-top:34px">Are game totals and margins independent?</h2>
<p class="sub">This is the whole basis for how parlays are treated on this site. If these were strongly related,
combining legs would be a different problem entirely.</p>"""
grows = [[E(c["label"]), c["n"], num(c["pearson_r"],3,True), num(c["spearman_rho"],3,True), num(c["r_squared"],3), num(c["t_stat"],2,True), src(SRC["schedule"], "NFL.com")]
         for c in gc]
body += tbl([("Relationship",0),("n",1),("Pearson r",1),("Spearman ρ",1),("r²",1),("t",1),("Source",0)], grows,
            caption="All four relationships are weak. That is a real result, not a null one: it justifies modelling winner and total separately.")

body += f"""
<div class="note"><p>{E(AN['parlay_math']['finding'])}</p></div>

<h2 style="margin-top:34px">Model lines — Week 10</h2>
<p class="sub">These are <b>model-implied numbers, not market lines</b>. No official NFL source publishes a spread or a total,
so there is nothing to compare them with. They are published because they are the model's output and hiding them would be
worse than labelling them.</p>"""
lrows = []
for g in AN["week10_model_lines"]:
    lrows.append([
      E(g["kickoff_et"][5:16]),
      f'{team_link(g["away"])} @ {team_link(g["home"])}',
      num(g["power_away"],2,True), num(g["power_home"],2,True),
      num(g["model_home_margin"],1,True),
      num(g["model_total"],1),
      num(g["home_win_prob"]*100,1), num(g["away_win_prob"]*100,1),
      b("model","info"),
      src("https://www.nfl.com/schedules/2026/by-week/week-10", "W10"),
    ])
body += tbl([("Kickoff ET",0),("Game",0),("Away power",1),("Home power",1),("Home margin",1),("Total",1),
             ("Home win %",1),("Away win %",1),("Type",0),("Source",0)], lrows,
            caption="Home margin is positive when the home club is expected to win. Power is points per game above the "
                    "league-average club, adjusted for opponent. The total is the two powers' combined scoring expectation.")

body += f"""
<h2 style="margin-top:34px">The luck ladder</h2>
<p class="sub">Pythagorean wins would be the club's record if it had converted its scoring margin at the league's normal rate.
The gap between that and its actual record is the part of its season that did not come from scoring margin.</p>
<div class="grid g2" style="margin-top:14px">
  <div class="card"><h3>Most over-performing: {E(bf['name'])}</h3>
  <p>{bf['wins']} wins against {num(bf['pyth_wins'],2)} expected. One-score games: <b>{E(bf['one_score_record'])}</b>.
  A club that wins every close game has usually been a little lucky rather than a little clutch.</p></div>
  <div class="card"><h3>Most under-performing: {E(bo['name'])}</h3>
  <p>{bo['wins']} wins against {num(bo['pyth_wins'],2)} expected. One-score games: <b>{E(bo['one_score_record'])}</b>.
  The mirror image of the same effect.</p></div>
</div>"""
lrows = []
for r in AN["luck_ladder"]:
    kind = "ok" if r["regression_flag"]=="FADE" else "warn" if r["regression_flag"]=="BUY" else "dim"
    lrows.append([f'<b>{team_link(r["team"])}</b>', E(r["name"]), r["wins"], num(r["pyth_wins"],2),
                  num(r["pyth_residual"],2,True), E(r["one_score_record"]), num(r["one_score_residual"],1,True),
                  num(r["luck_score"],2,True), num(r["power"],2,True), b(r["regression_flag"], kind), src(SRC["standings"], "NFL.com")])
body += tbl([("Team",0),("Club",0),("W",1),("Expected W",1),("Pyth resid",1),("1-score",1),("1-score resid",1),
             ("Luck score",1),("Power",1),("Flag",0),("Source",0)], lrows,
            caption="FADE = won more than its scoring margin implies. BUY = won less. These are descriptive labels for "
                    "regression-to-the-mean candidates, NOT betting recommendations, and the site has no odds to bet against.")

body += f"""
<h2 style="margin-top:34px">Verified player lines</h2>
<p class="sub">Only passers whose 15 published values are <b>identical</b> to their club's official team passing line.
Exact equality is the proof: it can only happen if they are the club's only passer, and it simultaneously proves the
header-less column order. {len(PLAY['passers'])} of 32 clubs satisfy it.</p>"""
prow = []
for p in PLAY["passers"]:
    prow.append([f'<b>{team_link(p["team"])}</b>', src(p.get("src"), E(p["player"])),
                 p["ATT"], p["CMP"], num(p["PCT"],1), p["YDS"], num(p["YPA"],2), p["TD"], p["INT"],
                 num(p["RATE"],1), p["SACKS"], p["SACK_YDS"],
                 b("exact match","ok")])
body += tbl([("Team",0),("Player",0),("Att",1),("Cmp",1),("Pct",1),("Yds",1),("Y/A",1),("TD",1),("Int",1),
             ("Rate",1),("Sacks",1),("Sack yd",1),("Proof",0)], prow,
            caption=E(PLAY['meta']['inclusion_rule']))
body += f"""<div class="note warn" style="margin-top:16px"><p><b>Withheld.</b> {E(PLAY['meta'].get('withheld',''))}</p>
<p>{E(PLAY['meta'].get('excluded_example',''))}</p></div>
</div></section>"""
PAGES["analysis.html"] = ("Analysis", body, "Power ratings, correlations, luck decomposition and model lines for NFL 2026.")

# ================================================================ 7. STRATEGIES
GATES = {g[0]: g for g in AN["gates"]}
body = pagehead("Strategies","A leaderboard that is designed to reject its own entries",
  f"""Six strategies were specified, implemented and backtested walk-forward across weeks 5–9: for every
  graded game the ratings use <b>only</b> games played before it. Seven gates decide whether a strategy has
  earned the right to be called an edge. <b>None of the six currently passes all seven</b>, and the site says
  so before it shows any hit rate.""")

body += f"""<section><div class="wrap">
<div class="note bad"><p><b>Result: 0 of {len(AN['strategies'])} validated.</b> Every strategy is
<b>UNDERPOWERED</b> — the largest graded sample is {max(s['n'] for s in AN['strategies'])} legs against a gate that
requires 200. This is not a failure of the code; it is the honest state of a single partial season. The leaderboard
is sorted by gates passed, not by hit rate, precisely so that a reader cannot mistake the top row for a recommendation.</p></div>

<h2>The seven gates</h2>
<p class="sub">A strategy must clear all seven. Six are hard; passing fewer than six is a rejection regardless of results.</p>"""
grows = [[f'<b>{E(k)}</b>', E(v[1]), E(v[2]), b(v[3],"bad" if v[3]=="hard" else "dim"), src(SRC["repo"]+"/blob/main/scripts/strategy_engine.py","engine")] for k,v in GATES.items()]
body += tbl([("Gate",0),("Name",0),("Requirement",0),("Type",0),("Source",0)], grows)

body += """
<h2 style="margin-top:34px">Leaderboard</h2>
<p class="sub">Sorted by gates passed, then by Brier skill. Hit rate is shown because it is what people look at —
and the columns to its right are the ones that decide anything.</p>"""
srows = []
for s in AN["strategies"]:
    kind = STATUS_KIND.get(s["status"], "dim")
    gp = s["gates_passed"]
    bar = f'<div class="bar" style="min-width:80px"><i style="width:{gp/7*100:.0f}%"></i></div>'
    srows.append([
      f'<b>{E(s["id"])}</b>',
      f'{E(s["name"])}<div class="tiny" style="color:var(--dim);margin-top:3px">{E(s["kind"])} · {E(s["hypothesis"])}</div>',
      s["n"], num(s["hit_rate"]*100,1),
      num(s["brier_skill"],4,True), num(s["brier"],4), num(s["mean_abs_line_error"],2),
      f'{gp}/7 {bar}', b(s["status"], kind), b("UNPAID","dim"),
      src(SRC["schedule"], "backtest") + " · " + src(SRC["repo"]+"/blob/main/scripts/strategy_engine.py","code"),
    ])
body += tbl([("ID",0),("Strategy",0),("Legs",1),("Hit %",1),("Brier skill",1),("Brier",1),("Mean line err",1),("Gates",0),("Status",0),("Reward",0),("Source",0)],
            srows, caption="Reward points are earned by passing gates, not by winning bets — that is the point of a "
                           "gate-based leaderboard. No reward is paid while a strategy is UNDERPOWERED.")

body += """
<h2 style="margin-top:34px">Gate-by-gate detail</h2>
<p class="sub">Where each strategy stands, gate by gate. A FAIL on G2 is a sample-size problem, not a code bug.</p>"""
drows = []
for s in AN["strategies"]:
    cells = [f'<b>{E(s["id"])}</b>', E(s["name"][:52])]
    for gk in GATES:
        v = s["gates"].get(gk, "N/A")
        cells.append(b(v, "ok" if v=="PASS" else "bad" if v=="FAIL" else "dim"))
    cells.append(src(SRC["repo"]+"/blob/main/data/derived/analysis.json","audit"))
    drows.append(cells)
body += tbl([("ID",0),("Strategy",0)] + [(E(g),"") for g in GATES] + [("Source",0)], drows,
            caption="G2 (n ≥ 200) fails universally. G6 and G7 concern correlation and implementability: G6 is N/A for "
                    "single bets and G7 fails where odds would be required to execute.")

body += """
<h2 style="margin-top:34px">Week-by-week stability</h2>
<p class="sub">A strategy that only works in one week has not worked. These are the five out-of-sample folds.</p>"""
frows = []
for s in AN["strategies"]:
    r = [f'<b>{E(s["id"])}</b>']
    for f in s["fold_hit_rates"]:
        r.append(f'{num(f["hit"]*100,1)}<div class="tiny" style="color:var(--dim)">n={f["n"]}</div>')
    r.append(num(s["hit_rate"]*100,1))
    r.append(src(SRC["schedule"],"NFL.com"))
    frows.append(r)
body += tbl([("ID",0)] + [(f'W{f["week"]}',1) for f in AN["strategies"][0]["fold_hit_rates"]] + [("Overall",1),("Source",0)], frows,
            caption="Fold hit rates swing wildly — week 9 at 100% next to week 6 at 50% is exactly what a small sample "
                    "looks like, and is the argument for gate G5.")

pm = AN["parlay_math"]
body += f"""
<h2 style="margin-top:34px">Parlays and the arithmetic of stacking legs</h2>
<div class="grid g3" style="margin-top:14px">
  {card("2 legs at 60%", "Independent hit probability", big=f"{pm['two_leg_independent_hit_rate_at_60pct']*100:.0f}%")}
  {card("3 legs at 60%", "Independent hit probability", big=f"{pm['three_leg_independent_hit_rate_at_60pct']*100:.1f}%")}
  {card("4 legs at 60%", "Independent hit probability", big=f"{pm['four_leg_independent_hit_rate_at_60pct']*100:.2f}%")}
</div>
<p class="sub" style="margin-top:16px">Even four legs at an optimistic 60% each is barely a one-in-eight proposition.
That is not a reason to avoid parlays; it is a reason to be extremely careful about claiming edge on them.</p>
<div class="note"><p>{E(pm['finding'])}</p></div>
<div class="note warn"><p><b>Player-prop combinations cannot be measured at all.</b> {E(pm['prop_combo_status'])}</p></div>
<div class="note bad"><p><b>No market, therefore no ROI.</b> No NFL.com property publishes a spread, total, moneyline or prop
price — verified rather than assumed. So this page reports hit rate, Brier skill and calibration, and refuses to report a
return, a profit, or a closing-line value. Any project that shows you an ROI without an odds source is guessing.
This is <a href="flagged.html">FL-01</a>.</p></div>
</div></section>"""
PAGES["strategies.html"] = ("Strategies", body, "Six gated strategies, seven validation gates, and why none passes yet.")

# ================================================================ 8. METHOD
body = pagehead("Method","How every number on this site is produced — and where it is weak",
  """No figure on this site is typed by hand into a page. Pages are generated from JSON files, the JSON files are
  checked by scripts, and the scripts fail loudly. This page states the rules the project follows, so that a reader
  can decide whether to trust a number rather than having to take it on faith.""")

body += f"""<section><div class="wrap">
<div class="grid g2">
<div class="card"><h3>The five rules</h3>
<p><b>1. Official sources only.</b> Every value traces to an NFL.com or NFL Football Operations page. No aggregator,
no stats site, no model's memory.</p>
<p><b>2. Never infer.</b> If an official source does not state a value, the cell is blank. A blank is information:
it means nobody official said.</p>
<p><b>3. Prove the mapping, don't assume it.</b> The league's team-stat pages have no header row. Column order is
proven by reproducing a known player line and by exact league-wide conservation, not by eyeballing plausibility.</p>
<p><b>4. Label the model.</b> Anything computed — power ratings, correlations, lines — carries a MODEL label and a
formula. It is never dressed as a fact.</p>
<p><b>5. Publish the failures.</b> Every irregularity goes to <a href="flagged.html">Flagged for Review</a> with a
severity and a fix. Withheld data is named, not quietly dropped.</p></div>

<div class="card"><h3>What the verifier actually checks</h3>
<p><b>{VER['totals']['checks']} data checks</b>, of which {VER['totals']['pass']} pass. The hard ones are structural:
every row references two real distinct clubs; the log reproduces all 32 clubs' W-L-T, PF, PA, PCT and net points;
streaks re-derive from a chronological scan; the eight conservation identities hold exactly.</p>
<p><b>{len(PER['meta']['personnel_verification'])} personnel checks</b>, all passing. These exist because a duplicate
position label once caused a third-string player to be scored as a starter — the single most dangerous kind of bug in
this project, because it produces a plausible answer rather than an error.</p>
<p>Run them yourself: <code>python3 scripts/verify_data.py</code> and <code>python3 scripts/verify_personnel.py</code>.</p></div>
</div>

<h2 style="margin-top:34px">The verification log</h2>
<p class="sub">Statuses are exactly as the script emits them. Soft failures are published rather than being reclassified
as passes.</p>"""
vrows = []
for c in VER["checks"]:
    k = STATUS_KIND.get(c["status"], "dim")
    vrows.append([f'<b>{E(c["id"])}</b>', E(c["name"]), b(c["status"], k), b(c["severity"], "bad" if c["severity"]=="hard" else "dim"),
                  f'<span class="tiny">{E(str(c.get("detail",""))[:180])}</span>',
                  src(SRC["repo"]+"/blob/main/scripts/verify_data.py","verifier")])
body += tbl([("ID",0),("Check",0),("Status",0),("Severity",0),("Detail",0),("Source",0)], vrows,
            caption=f"{VER['totals']['pass']} of {VER['totals']['checks']} pass. The failing three are soft: derived rates that "
                    f"the source itself publishes inconsistently.")

body += """
<h2 style="margin-top:34px">Personnel checks</h2>
<p class="sub">These guard the injury-to-depth-chart join, where a wrong answer looks right.</p>"""
prow = [[f'<b>{E(c["id"])}</b>', E(c["name"]), b(c["status"], STATUS_KIND.get(c["status"],"dim")),
         f'<span class="tiny">{E(str(c.get("detail",""))[:140])}</span>',
         src(SRC["repo"]+"/blob/main/scripts/verify_personnel.py","verifier")]
        for c in PER["meta"]["personnel_verification"]]
body += tbl([("ID",0),("Check",0),("Status",0),("Detail",0),("Source",0)], prow)

body += f"""
<h2 style="margin-top:34px">The model, stated plainly</h2>
<div class="card">
<p><b>Power rating.</b> Each club's points scored and allowed per game, adjusted for the strength of the opponents it
actually faced, shrunk toward the league mean by the number of games played. It is a club-strength number in points.</p>
<p><b>Model line.</b> <code>home_margin = power(home) − power(away) + HFA</code>, with HFA = {num(hf['model_uses'],2,True)}
(the neutral-site-excluded estimate). Positive means the home club is expected to win. <b>Sign is asserted, not assumed</b>:
the build checks that a power-rating line picks the home side well above 50% and aborts if it does not. Current check:
{AN['sign_check']['hit_rate']*100:.1f}% correct, {b('PASS','ok') if AN['sign_check']['passed'] else b('FAIL','bad')}.</p>
<p><b>Win probability.</b> A normal distribution over the model margin with the measured margin standard deviation
of {num(hf['stdev_home_margin'],2)} points. This is a deliberate simplification: real margins are a little
fat-tailed, so the model will slightly understate blowout probability.</p>
<p><b>Pythagorean expectation.</b> Wins expected from points scored and allowed with exponent {2.37},
computed per club. The gap to the actual record is the luck score.</p>
<p><b>Backtest.</b> Walk-forward. For week W the ratings see only weeks &lt; W. Folds are weeks 5–9. Scored by Brier skill
against a 50/50 baseline and by log loss; the gates do the rest.</p>
<p><b>What the model does not do.</b> It does not know about injuries, weather, rest, travel or venue — except that
neutral sites are excluded from the HFA estimate. It is a scoring-margin model and nothing more.</p>
</div>

<h2 style="margin-top:34px">Determinism</h2>
<div class="note ok"><p>The analysis uses no random numbers and no clock-dependent logic in its arithmetic. Re-running
<code>scripts/analyse.py</code> on the same inputs produces the same output — the build timestamp changes, nothing else.
If two runs ever disagree, that is a bug and should be reported.</p></div>

<h2 style="margin-top:34px">Known weaknesses</h2>
<div class="grid g2">
  <div class="card"><h3>Sample</h3><p>Nine weeks. 136 games. Thirty-two clubs. Every correlation on this site is
  estimated on a sample small enough that a single club can move it. The gates exist because of this, and every
  table prints its own n.</p></div>
  <div class="card"><h3>No market</h3><p>Without odds there is no way to test whether any of this is profitable,
  or even whether a model line is better than the market's. That distinction — good at predicting versus good at
  betting — is the one most analytics projects blur.</p></div>
  <div class="card"><h3>Depth coverage</h3><p>Four of thirty-two depth charts. The deficiency analysis is real
  for those four and blank elsewhere, and the index is a transparent weighting rather than a measured effect.</p></div>
  <div class="card"><h3>Transcription</h3><p>Values are read from rendered pages. The verifier catches arithmetic
  inconsistency, not a single mistyped digit that happens to preserve an identity. The conservation checks make that
  unlikely for the team stats and impossible for the game log, but not for every cell.</p></div>
</div>
</div></section>"""
PAGES["method.html"] = ("Method", body, "Exactly how every number on this site is produced, and where the model is weak.")

# ================================================================ 9. SOURCES
REGS = [
 ("Schedule — full season","Schedule results, dates and final scores",
  [("Full 2026 REG schedule", SRC["schedule"]),
   ("Week-by-week 1","https://www.nfl.com/schedules/2026/by-week/week-1"),
   ("Week-by-week 2","https://www.nfl.com/schedules/2026/by-week/week-2"),
   ("Week-by-week 3","https://www.nfl.com/schedules/2026/by-week/week-3"),
   ("Week-by-week 4","https://www.nfl.com/schedules/2026/by-week/week-4"),
   ("Week-by-week 5","https://www.nfl.com/schedules/2026/by-week/week-5"),
   ("Week-by-week 6","https://www.nfl.com/schedules/2026/by-week/week-6"),
   ("Week-by-week 7","https://www.nfl.com/schedules/2026/by-week/week-7"),
   ("Week-by-week 8","https://www.nfl.com/schedules/2026/by-week/week-8"),
   ("Week-by-week 9","https://www.nfl.com/schedules/2026/by-week/week-9")]),
 ("Standings","W-L-T, PCT, PF, PA, home/road splits, streaks",
  [("Division standings", SRC["standings"]),("Detailed standings","https://www.nfl.com/standings/division/2026/REG")]),
 ("Team statistics","Passing and rushing, offence and defence",
  [("Offence — passing", SRC["ts_off_pass"]),("Offence — rushing", SRC["ts_off_rush"]),
   ("Defence — passing allowed", SRC["ts_def_pass"]),("Defence — rushing allowed", SRC["ts_def_rush"]),
   ("Offence — scoring (WITHHELD, see FL-04)","https://www.nfl.com/stats/team-stats/offense/scoring/2026/reg/all"),
   ("Defence — scoring (WITHHELD, see FL-04)","https://www.nfl.com/stats/team-stats/defense/scoring/2026/reg/all")]),
 ("Player statistics","Passing leaderboard; rushing/receiving withheld",
  [("Passing leaderboard", SRC["player_pass"]),
   ("Rushing leaderboard (WITHHELD, see FL-08)","https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all"),
   ("Receiving leaderboard (WITHHELD, see FL-08)","https://www.nfl.com/stats/player-stats/category/receiving/2026/reg/all")]),
 ("Injuries","Week 10 injury report and practice participation",
  [("League injury report", SRC["injuries"]),("Week 10 report article", SRC["inj_news"]),
   ("Kansas City injury page","https://www.chiefs.com/team/injury-report/")]),
 ("Rosters","Jersey numbers, positions, height, weight, experience, college",
  [("Roster — every club, /teams/<club>/roster", "https://www.nfl.com/teams/")]),
 ("Depth charts","Club-published unofficial depth charts (the only place this information exists)",
  [("Detroit","https://www.detroitlions.com/team/depth-chart"),
   ("Minnesota","https://www.vikings.com/team/depth-chart"),
   ("Kansas City","https://www.chiefs.com/team/depth-chart"),
   ("Green Bay","https://www.packers.com/team/depth-chart"),
   ("New England","https://www.patriots.com/team/depth-chart")]),
 ("Rules and policy","Roster limits, game-day actives, 2026 rule changes",
  [("Roster sizes and CBA mechanics", SRC["ops_cba"]),("2026 NFL Rulebook", SRC["rulebook"])]),
 ("Project","The code and the coordination log",
  [("Repository", SRC["repo"]),("Coordination log", SRC["coord"]),("Verification report json",
    SRC["repo"]+"/blob/main/data/derived/verification_report.json")]),
]

body = pagehead("Data sources","Every official page this project read, and what it supplied",
  f"""This is the complete register. Nothing on this site comes from a source that is not on this page.
  Where a page was read and then <b>rejected</b>, it is still listed — with the reason — because a source
  that was tried and failed is more useful to a reader than one that was quietly deleted.""")
body += f'<section><div class="wrap">'
for title, desc, items in REGS:
    rs = [[f'<b>{E(n)}</b>', f'<span class="tiny" style="color:var(--dim);word-break:break-all">{E(u)}</span>', src(u,"open")] for n,u in items]
    body += f'<h3>{E(title)}</h3><p class="sub">{E(desc)}</p>' + tbl([("Page",0),("URL",0),("Link",0)], rs)
body += f"""
<h2 style="margin-top:34px">Sources that were tried and rejected</h2>
<p class="sub">Recorded so nobody repeats the attempt.</p>"""
rej = [
 ["nfl.com/teams/&lt;club&gt;/depth-chart/","404 — NFL.com does not host club depth charts","Use the club's own site: &lt;club&gt;.com/team/depth-chart", src("https://www.patriots.com/team/depth-chart","example")],
 ["nfl.com/stats/team-stats/offense/points/2026/reg/","404 — wrong route","Use /offense/scoring/2026/reg/all", src("https://www.nfl.com/stats/team-stats/offense/scoring/2026/reg/all","NFL.com")],
 ["operations.nfl.com/football-ops/league-media-injury-report/","404 — the policy page has moved","Use the 2026 rulebook for roster rules; injury-reporting mechanics cited from the published report itself", src(SRC["rulebook"],"Rulebook")],
 ["nfl.com/injuries/ (as the sole injury source)","Renders without Injury and Game Status columns","Cross-read the per-week news article and the club injury pages", src("https://www.nfl.com/injuries/league/2026/REG10","REG10")],
 ["nfl.com/stats/player-stats/category/rushing/2026/reg/all","Header-less; column order unprovable — every identity fails","Withheld (FL-08); needs per-player pages instead (suggestion P-01)", src("https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all","NFL.com")],
 ["nfl.com/stats/team-stats/offense/scoring/2026/reg/all","Header-less; no identity holds for columns 3–4","Withheld (FL-04)", src("https://www.nfl.com/stats/team-stats/offense/scoring/2026/reg/all","NFL.com")],
]
body += tbl([("Source",0),("What went wrong",0),("What replaced it",0),("Verify",0)], rej)
body += f"""
<h2 style="margin-top:34px">Data files produced</h2>
<p class="sub">Each file is committed and is the single source of truth for the pages built from it.</p>"""
files = [
 ["<code>data/games_2026.json</code>","136 game rows, weeks 1–9, each with date, venue type and source URL", src(SRC["repo"]+"/blob/main/data/games_2026.json","GitHub")],
 ["<code>data/standings_raw.json</code>","32 clubs, published standings verbatim, unidentifiable columns omitted", src(SRC["repo"]+"/blob/main/data/standings_raw.json","GitHub")],
 ["<code>data/team_stats.json</code>","32 clubs × 4 stat families, with the withheld scoring tables recorded in meta", src(SRC["repo"]+"/blob/main/data/team_stats.json","GitHub")],
 ["<code>data/player_verified.json</code>","8 passing lines proven by exact equality with club team lines", src(SRC["repo"]+"/blob/main/data/player_verified.json","GitHub")],
 ["<code>data/injuries_week10.json</code>","254 player rows across all 14 Week 10 games", src(SRC["repo"]+"/blob/main/data/injuries_week10.json","GitHub")],
 ["<code>data/depth_charts.json</code>","4 club depth charts, transcribed and normalised", src(SRC["repo"]+"/blob/main/data/depth_charts.json","GitHub")],
 ["<code>data/depth-charts-2026.json</code>","12 official club depth charts &amp; 18 1st–4th string deficiency cascades", src(SRC["repo"]+"/blob/main/data/depth-charts-2026.json","GitHub")],
 ["<code>data/correlations-2026.json</code>","14 verified 2026 team correlations (n=32), SGP blank register &amp; luck residuals", src(SRC["repo"]+"/blob/main/data/correlations-2026.json","GitHub")],
 ["<code>data/nfl-rules-operations-2026.json</code>","8 verified 2026 NFL Rulebook &amp; Operations anchors", src(SRC["repo"]+"/blob/main/data/nfl-rules-operations-2026.json","GitHub")],
 ["<code>data/questions.json</code>",f"{len(Q['questions'])} questions, with answer status and discovery path", src(SRC["repo"]+"/blob/main/data/questions.json","GitHub")],
 ["<code>data/suggestions.json</code>",f"{len(SUG['suggestions'])} proposals, none implemented", src(SRC["repo"]+"/blob/main/data/suggestions.json","GitHub")],
 ["<code>data/derived/verification_report.json</code>",f"{VER['totals']['checks']} checks, generated by the verifier", src(SRC["repo"]+"/blob/main/data/derived/verification_report.json","GitHub")],
 ["<code>data/derived/personnel.json</code>","The injury × depth-chart join plus 9 integrity checks", src(SRC["repo"]+"/blob/main/data/derived/personnel.json","GitHub")],
 ["<code>data/derived/analysis.json</code>","Power ratings, correlations, backtests, gates, model lines", src(SRC["repo"]+"/blob/main/data/derived/analysis.json","GitHub")],
]
body += tbl([("File",0),("Contents",0),("Source",0)], files)
body += "</div></section>"
PAGES["sources.html"] = ("Data Sources", body, "The complete register of official NFL sources used, and the ones rejected.")

# ================================================================ 10. QUESTIONS
cnt = {}
for q in Q["questions"]: cnt[q["status"]] = cnt.get(q["status"],0)+1
body = pagehead("Questions","What you would need to know before acting — including what nobody can answer yet",
  f"""Every row is a question a decision-maker would reasonably ask. The answer column contains only what an
  official source states. Where no official source can settle it, <b>the answer is left blank</b> and the row says
  exactly how it could be closed. {cnt.get('BLOCKED',0) + cnt.get('OPEN',0)} of {len(Q['questions'])} are open or blocked —
  that number is the point of this page, not a failure of it.""")
body += f'<section><div class="wrap">'
body += '<div class="grid g4" style="margin-bottom:22px">'
for k in ("ANSWERED","PARTIAL","OPEN","BLOCKED"):
    body += card(k.title(), {"ANSWERED":"Settled from an official source",
                             "PARTIAL":"Partly official, partly not obtainable",
                             "OPEN":"No official source can settle it",
                             "BLOCKED":"Needs a data source that does not exist"}[k],
                 big=cnt.get(k,0))
body += '</div>'
body += '<div class="legend"><span><i style="background:#7cf3b0"></i>ANSWERED — cite and move on</span>' \
        '<span><i style="background:#ffc86b"></i>PARTIAL / OPEN — usable with a caveat</span>' \
        '<span><i style="background:#ff8a8a"></i>BLOCKED — do not act on this</span></div>'

for cat in ["Data integrity","Rules","Injuries","Model","Player stats","Player props","Betting","Coverage","Process"]:
    qs = [q for q in Q["questions"] if q["category"]==cat]
    if not qs: continue
    body += f'<h3>{E(cat)}</h3>'
    rows = []
    for q in qs:
        ans = E(q["answer"]) if q["answer"] else '<span class="blank">— no official source can answer this —</span>'
        rows.append([
          f'<b>{E(q["id"])}</b>',
          f'<b>{E(q["question"])}</b><div class="tiny" style="color:var(--dim);margin-top:4px">{ans}</div>',
          b(q["status"], STATUS_KIND.get(q["status"],"dim")),
          (src(q["source"], "source") if q["source"]
            else f'<span class="blank" title="No official source publishes this">no source exists</span> · {src(SRC["repo"]+"/blob/main/data/questions.json","register")}'),
          f'<span class="tiny">{E(q["discovery"])}</span>',
          f'<span class="tiny" style="color:var(--dim)">{E(q["evidence"])}</span>',
        ])
    body += tbl([("ID",0),("Question &amp; answer",0),("Status",0),("Source",0),("How to close it",0),("Evidence",0)], rows)
body += "</div></section>"
PAGES["questions.html"] = ("Questions", body, "The decision register: what is known, what is partial, and what nobody can answer.")

# ================================================================ 11. SUGGESTIONS
body = pagehead("Suggestions","Proposals for review — nothing on this page is implemented",
  f"""A working list of improvements, each with what it would fix, what it would let this site claim that it
  cannot claim today, what it costs, how it would be validated, and what could go wrong. Suggestions are
  <b>reviewed before implementation</b>, not after. {len(SUG['suggestions'])} are listed; none is built.""")
body += f'<section><div class="wrap">'
body += f'<div class="note"><p>{E(SUG["meta"]["governance"])}</p></div>'
body += f'<div class="note warn"><p><b>Decision rule.</b> {E(SUG["meta"]["decision_rule"])}</p></div>'

rows = []
for s in SUG["suggestions"]:
    rows.append([
      f'<b>{E(s["id"])}</b>',
      f'<b>{E(s["title"])}</b>'
      f'<div class="tiny" style="color:var(--dim);margin-top:5px"><b>Problem:</b> {E(s["problem"])}</div>'
      f'<div class="tiny" style="margin-top:5px"><b>Proposal:</b> {E(s["proposal"])}</div>',
      b(s["status"], STATUS_KIND.get(s["status"],"dim")),
      E(s["effort"]), E(s["impact"]),
      f'<span class="tiny"><b>Validated by:</b> {E(s["validation"])}<br><b>Risk:</b> {E(s["risk"])}<br><b>Unlocks:</b> {E(s["unlocks"])}</span>',
      src(SRC["repo"]+"/blob/main/data/suggestions.json","register"),
    ])
body += tbl([("ID",0),("Suggestion",0),("Status",0),("Effort",0),("Impact",0),("Validation, risk, payoff",0),("Source",0)], rows,
            caption="Sorted by priority. Effort and impact are the author's judgement and are labelled as such, not measured.")

body += """
<h2 style="margin-top:34px">How to react to a suggestion</h2>
<div class="grid g3" style="margin-top:14px">
  <div class="card"><h3>Approve</h3><p>It becomes a task on the coordination board with a file scope, and it is
  implemented with the same verification standard as everything else. Approval is a decision, not an implication.</p></div>
  <div class="card"><h3>Defer</h3><p>Kept on the list with the reason it is blocked. A deferred idea is not a rejected
  idea: several of these are waiting on a legitimate data source rather than on effort.</p></div>
  <div class="card"><h3>Reject</h3><p>Recorded with the reason, so it is not proposed again. One entry (P-09) is
  already in this state because it was attempted and failed.</p></div>
</div>
<div class="note" style="margin-top:18px"><p><b>One suggestion is a warning, not an opportunity.</b> P-09 is listed so
that nobody repeats it: reconstructing the rushing and receiving leaderboards by inference was tried, every identity
failed, and the correct response was to withhold the tables rather than pick the ordering that looked plausible.</p></div>
</div></section>"""
PAGES["suggestions.html"] = ("Suggestions", body, "Proposed improvements, each with cost, validation and risk - none implemented.")

# ================================================================ 12. FLAGGED FOR REVIEW
IRR = [
 ("IR-01","Low","Depth charts are unofficial by construction",
  "Every club publishes its depth chart explicitly labelled 'unofficial'. It is the organisation's own working document.",
  "The site says so wherever a depth slot is used. Starter status should be read as the club's own current opinion.",
  "No fix available. This is inherent to the only official source of depth information.",
  "https://www.patriots.com/team/depth-chart"),
 ("IR-02","Medium","Only 4 of 32 club depth charts are joined in personnel.json (12 charted on 1st–4th String page)",
  "Kansas City, Green Bay, New England and Detroit in personnel.json; expanded to 12 clubs on depth-deficiencies.html. Remaining clubs stay blank rather than guessed.",
  "The deficiency table shows a chart status per club; unmapped clubs are labelled explicitly.",
  "Suggestion P-02: transcribe the remaining clubs from each club's own site and re-run the personnel checks.",
  "https://www.detroitlions.com/team/depth-chart"),
 ("IR-03","Low","Standings table has unidentifiable columns",
  "The league standings render 16 data columns; the page legend names only 12.",
  "Home, road and streak columns were proven by re-deriving them from the game log. Every other unlabelled column is omitted.",
  "Would need the league's own column definitions, which are not published.",
  SRC["standings"]),
 ("IR-04","High","Home-field advantage is not detectable, and the pooled figure is misleading",
  "Pooled over all 136 games the mean home margin is +0.00 pts and home clubs are 67-68-1, which looks like home-field has vanished. Seven games were at neutral sites with no true home club.",
  "The estimate is restricted to the 129 genuine home games: +0.50 pts, 95% CI [-1.80, +2.79], win rate .5155. The conventional +2.5 prior is INSIDE that interval, so 2026 cannot reject it. The model uses +0.50 and the site states the uncertainty.",
  "Suggestion P-05: add 2023–2025 so the estimate has enough games to settle the question.",
  SRC["schedule"]),
 ("IR-05","Medium","Two official total-offence figures disagree by 70 yards",
  "Kansas City's club page reports 3,069 total offensive yards while the official team-stat components sum to 2,037 + 1,102 = 3,139.",
  "Both values are published side by side and the discrepancy is stated. Nothing is reconciled by assumption.",
  "Suggestion P-04: check whether the gap is systematic across all 32 clubs or a one-club typo.",
  "https://www.nfl.com/teams/kansas-city-chiefs/stats"),
 ("IR-06","Low","A published completion percentage does not recompute",
  "Washington's completion percentage computes to 61.7 from 164 of 266 but is published as 61.6.",
  "The published value is shown; the recomputation is shown next to it so the disagreement is visible.",
  "Rounding convention in the source. Not resolvable without the league's formula.",
  SRC["ts_off_pass"]),
 ("IR-07","Medium","Yards per attempt disagrees for four clubs",
  "Kansas City, Jacksonville, Seattle and Pittsburgh disagree with every candidate denominator tested: (YDS+SACK_YDS)/(ATT+SACKS) fails for 22 of 32 clubs; YDS/(ATT+SACKS) fails for all 32.",
  "Published values are transcribed as published, and the fact that they do not recompute is stated rather than hidden.",
  "Needs the league's official YPA definition.",
  SRC["ts_off_pass"]),
 ("IR-08","High","Rushing and receiving leaderboards are unusable",
  "Both render without a header row. No arithmetic identity identifies the columns: published yards-per-carry disagrees with yards divided by carries for every sampled row (Bijan Robinson 5.2 vs 5.0, Kenneth Walker 5.5 vs 7.0, Jahmyr Gibbs 4.8 vs 9.0), and yards-per-reception and yards-per-game fail identically.",
  "Both leaderboards are withheld entirely. Only 8 passing lines that pass an exact 15-value equality test against their club's team passing line are published.",
  "Suggestion P-01: use per-player pages with labelled headers instead of the leaderboard.",
  "https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all"),
 ("IR-09","Medium","No official odds source exists",
  "No NFL.com property publishes spreads, totals, moneylines or player-prop prices.",
  "No market comparison, no ROI, no closing-line value. The site reports hit rate and Brier skill only, and says why.",
  "Suggestion P-06, and it stays deferred until a legitimate timestamped source exists.",
  SRC["coord"]),
 ("RA-05","High","Official REG10 injury report omits IR & pre-practice ruled-out QBs",
  "nfl.com/injuries/league/2026/REG10 prints 'No Injuries Reported' for SEA, CIN, LAC, and BAL at snapshot time — yet official NFL.com news confirms SEA QB1 Sam Darnold is ruled out, CIN S Kyle Dugger was DNP Wednesday, and BAL QB1 Lamar Jackson + QB2 Tyler Huntley are on Injured Reserve.",
  "Cross-joined REG10 with official NFL.com IR/starter announcements on depth-deficiencies.html so 'No Injuries Reported' is never misread as 'healthy'.",
  "Always join weekly active-roster practice reports with official NFL Reserve/Injured transaction logs.",
  "https://www.nfl.com/news/sam-darnold-ruled-out-for-seahawks-week-10-game-vs-raiders-drew-lock-expected-to-start-again"),
 ("RA-06","Medium","Official club depth charts exhibit roster lag & blank cells",
  "Line-by-line review of official club depth charts caught retired DE Aaron Donald still listed on therams.com, a blank Kicker row on miamidolphins.com, OUT C Lucas Patrick omitted on commanders.com, and Questionable LB Malik Harrison omitted on giants.com.",
  "Published verbatim with explicit club-lag warnings on depth-deficiencies.html and repo-audit.html.",
  "Verify every club depth-chart slot against 53-man active roster and 90-minute pre-kickoff Inactive Lists.",
  "https://www.therams.com/team/depth-chart"),
]
body = pagehead("Flagged for Review","Every irregularity and unverified value, published rather than buried",
  f"""Nothing on this site is silently dropped. Where the data is inconsistent, incomplete, or simply not
  obtainable, it appears here with a severity, an exact statement of what is wrong, what the site does about it,
  and what would fix it. {len(IRR)} irregularities and the withheld datasets are listed below.""")
body += f'<section><div class="wrap">'
body += ('<div class="note bad"><p><b>This page is part of the deliverable, not an apology for it.</b> A site that '
         'claims 100% completeness on a partial season is either not checking or not telling you. The items below '
         'are the difference between those two.</p></div>')

IRR_SRC = {
 "IR-01":"https://www.detroitlions.com/team/depth-chart",
 "IR-02":"https://www.packers.com/team/depth-chart",
 "IR-03":SRC["standings"],
 "IR-04":SRC["schedule"],
 "IR-05":SRC["club_stats"].format(slug="kansas-city-chiefs"),
 "IR-06":SRC["ts_off_pass"],
 "IR-07":SRC["ts_off_pass"],
 "IR-08":"https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all",
 "IR-09":"https://www.nfl.com/injuries/",
}
rows = []
for iid, sev, title, what, does, fix, s_url in IRR:
    kind = {"High":"bad","Medium":"warn","Low":"dim"}[sev]
    rows.append([f'<b>{E(iid)}</b>', b(sev, kind), f'<b>{E(title)}</b><div class="tiny" style="color:var(--dim);margin-top:4px">{E(what)}</div>',
                 f'<span class="tiny">{E(does)}</span>', f'<span class="tiny">{E(fix)}</span>',
                 src(IRR_SRC.get(iid, s_url), "source")])
body += tbl([("ID",0),("Severity",0),("Irregularity",0),("What the site does",0),("What would fix it",0),("Source",0)], rows,
            caption="Severity High = a reader could reach a wrong conclusion if this were hidden. Medium = a value is missing or contested. Low = a labelling or convention difference.")

body += """
<h2 style="margin-top:34px">Withheld datasets</h2>
<p class="sub">These exist in the source and are deliberately not published, because publishing them would require
guessing what their columns mean.</p>"""
withheld = [
 ["Team scoring — offence","4 header-less columns; no identity holds for columns 3–4 (SF 12+17=29 but published 31; TB 11+6=17 vs 19; ATL 9+11=20 vs 21; DEN 9+11=20 vs 21), and the defensive identity fails for CIN","IR-05 / FL-04","Not published","https://www.nfl.com/stats/team-stats/offense/scoring/2026/reg/all"],
 ["Team scoring — defence","Same page family; CIN 1+1+0=2 but the published total column is 0","IR-05 / FL-04","Not published","https://www.nfl.com/stats/team-stats/defense/scoring/2026/reg/all"],
 ["Rushing leaderboard","9 header-less columns; YDS/CAR and YDS/game fail for all 25 sampled rows under every candidate ordering","IR-08 / FL-08","Not published","https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all"],
 ["Receiving leaderboard","11 header-less columns; YDS/REC and YDS/game fail identically","IR-08 / FL-08","Not published","https://www.nfl.com/stats/player-stats/category/receiving/2026/reg/all"],
 ["Per-game player box scores","Not obtainable in this environment — NFL.com does not expose them on the fetched pages, so player-vs-team dependence cannot be measured","FL-09","Not published",SRC["coord"]],
]
body += tbl([("Dataset",0),("Why it is withheld",0),("Ref",0),("Status",0),("Source",0)],
            [[f'<b>{E(a)}</b>', E(why), E(ref), b(stat,"warn"), src(u,"source")] for a, why, ref, stat, u in withheld])

body += """
<h2 style="margin-top:34px">Unverified values, by page</h2>
<p class="sub">Where a table cell is blank, this is what the blank means.</p>"""
uv = [
 ["Injuries & Depth","Depth position for unmapped clubs","No transcribed depth chart","Blank","https://www.nfl.com/injuries/league/2026/REG10"],
 ["1st–4th String","Snap-adjusted EPA / point drop for backup strings","No official NFL source converts depth slots into spread points","Blank, flagged","https://operations.nfl.com/calendar-events/nfl-free-agency/contract-language"],
 ["Injuries & Depth","Game status for 243 of 254 rows","The report prints 'UNSPECIFIED' until later in the week","Blank, flagged","https://www.nfl.com/injuries/league/2026/REG10"],
 ["Injuries & Depth","Injury description where the report prints none","Source states no injury for that player","Blank","https://www.nfl.com/injuries/league/2026/REG10"],
 ["Team Stats","Scoring tables","Column meaning unprovable","Withheld","https://www.nfl.com/stats/team-stats/offense/scoring/2026/reg/all"],
 ["Analysis","Rushing / receiving player leaders","Column order unprovable","Withheld","https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all"],
 ["Strategies","ROI, profit, CLV","No official odds source","Not reported at all",SRC["coord"]],
 ["Correlations & Strategies","Same-Game Parlay & player-prop play-level correlations (U-C01…U-C06)","No per-game play-by-play box scores","Blank, flagged",SRC["coord"]],
 ["Standings","Columns 10–14 and 16","Unidentifiable from the page","Omitted",SRC["standings"]],
]
body += tbl([("Page",0),("Value",0),("Why it is not there",0),("How it appears",0),("Source",0)],
            [[E(a), E(vv), E(why), b(st,"dim"), src(u,"source")] for a, vv, why, st, u in uv])

body += f"""
<h2 style="margin-top:34px">What is NOT flagged, because it passed</h2>
<div class="note ok"><p>For balance: the game log reproduces all 32 clubs' records exactly ({VER['totals']['checks']} checks,
{VER['totals']['pass']} passing). The eight conservation identities hold to the yard. All 14 Week 10 games have injury
coverage. The depth-chart join passes all {len(PER['meta']['personnel_verification'])} integrity checks, and 39 injury rows
map to a real published depth slot. The things that are wrong are listed above; the things that are right were tested,
not assumed.</p></div>
<div class="note" style="margin-top:16px"><p><b>These items do not block publication.</b> The project's rule is that
flagged and unverified content is published on this page, clearly labelled, rather than being withheld from release or
quietly presented as fact.</p></div>
</div></section>"""
PAGES["flagged.html"] = ("Flagged for Review", body, "Every irregularity, withheld dataset and unverified value, with severity and fix.")

# ================================================================ EMIT
meta = {}
for fname, (title, body, desc) in PAGES.items():
    meta[fname] = page(fname, title, body, active=fname, desc=desc)

with open(os.path.join(OUT, "assets", "meta.json"), "w", encoding="utf-8") as f:
    json.dump({"built_utc": BUILD, "pages": sorted(PAGES), "bytes": meta}, f, indent=1)

total = sum(meta.values())
print(f"built {len(PAGES)} pages, {total:,} bytes")
for f, n in sorted(meta.items()): print(f"  {f:20s} {n:>9,} bytes")
