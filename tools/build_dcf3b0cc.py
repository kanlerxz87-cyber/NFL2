#!/usr/bin/env python3
"""Session dcf3b0cc — build the dated re-verification dashboard at dcf3b0cc/.

Reads only data/*_dcf3b0cc.{csv,json} and writes only files under dcf3b0cc/.
Every table row carries at least one official https:// source link; cells whose
value is the literal `not published` are rendered muted so a blank can never be
mistaken for a measured zero.
"""
import csv
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "dcf3b0cc", "data")
OUT = os.path.join(ROOT, "dcf3b0cc")
BLANK = "not published"

CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#14161a;--muted:#5b6472;--line:#e3e6ea;
--accent:#0b5fff;--warn:#b8860b;--bad:#b4232a;--good:#0f7b41;--chip:#eef2f7}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header{background:#101418;color:#fff;padding:14px 20px}
header .t{font-size:17px;font-weight:600}
header .s{font-size:13px;color:#9aa4b1;margin-top:2px}
header a{color:#8fb6ff}
nav{background:var(--card);border-bottom:1px solid var(--line);padding:0 20px;overflow-x:auto;white-space:nowrap}
nav a{display:inline-block;padding:12px 14px;color:var(--muted);font-size:14px;
border-bottom:2px solid transparent}
nav a.on{color:var(--ink);border-bottom-color:var(--accent);font-weight:600}
nav a:hover{color:var(--ink);text-decoration:none}
main{max-width:1280px;margin:0 auto;padding:22px 20px 70px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:12px;margin:0 0 22px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:13px 15px}
.kpi .n{font-size:25px;font-weight:650;letter-spacing:-.02em}
.kpi .l{font-size:12px;color:var(--muted);margin-top:3px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin-bottom:20px}
.card h2{margin:0 0 4px;font-size:17px}
.card h3{margin:20px 0 6px;font-size:14px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.card p{margin:6px 0;color:#2b313b}
.note{background:var(--chip);border-left:3px solid var(--accent);padding:10px 13px;
border-radius:0 6px 6px 0;color:#2b313b;font-size:14px;margin:10px 0}
.warn{border-left-color:var(--warn)}
.muted{color:var(--muted)}
.tools{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:12px 0}
input[type=search],select{padding:7px 10px;border:1px solid var(--line);border-radius:7px;
font-size:14px;background:#fff;color:var(--ink)}
.tw{overflow:auto;border:1px solid var(--line);border-radius:9px;background:#fff;max-height:78vh}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
thead th{position:sticky;top:0;background:#eef1f5;font-size:12px;text-transform:uppercase;
letter-spacing:.04em;color:#39414e;z-index:1;white-space:nowrap}
tbody tr:hover{background:#f9fbfd}
td.np{color:#8a93a0;font-style:italic}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.pill{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11.5px;font-weight:600}
.p-out{background:#fdecec;color:var(--bad)}
.p-q{background:#fff5e0;color:var(--warn)}
.p-d{background:#fdecec;color:var(--bad)}
.p-m{background:#e7f6ee;color:var(--good)}
.p-mm{background:#fdecec;color:var(--bad)}
.p-x{background:#eef2f7;color:#39414e}
footer{color:var(--muted);font-size:13px;padding:0 20px 40px;max-width:1280px;margin:0 auto}
code{background:var(--chip);padding:1px 5px;border-radius:4px;font-size:12.5px}
"""

JS = """
document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('[data-filter]').forEach(function(inp){
    var tid=inp.getAttribute('data-filter');
    var tbl=document.getElementById(tid); if(!tbl) return;
    var rows=Array.prototype.slice.call(tbl.tBodies[0].rows);
    function apply(){
      var q=inp.value.toLowerCase().trim();
      var sel=inp.getAttribute('data-col');
      rows.forEach(function(r){
        var hay = sel ? (r.cells[parseInt(sel,10)]||r).innerText : r.innerText;
        r.style.display = hay.toLowerCase().indexOf(q)=== -1 ? 'none' : '';
      });
      var n=rows.filter(function(r){return r.style.display!=='none';}).length;
      var c=document.getElementById(tid+'-count'); if(c) c.textContent=n;
    }
    inp.addEventListener('input',apply); apply();
  });
  document.querySelectorAll('th[data-sort]').forEach(function(th){
    th.style.cursor='pointer';
    th.addEventListener('click',function(){
      var tbl=th.closest('table'), i=parseInt(th.getAttribute('data-sort'),10), dir=th.dataset.dir==='asc'?1:-1;
      th.dataset.dir=dir===1?'desc':'asc';
      var tb=tbl.tBodies[0], rows=Array.prototype.slice.call(tb.rows);
      rows.sort(function(a,b){
        var x=(a.cells[i]||{}).innerText||'', y=(b.cells[i]||{}).innerText||'';
        var nx=parseFloat(x.replace(/[^0-9.\\-]/g,'')), ny=parseFloat(y.replace(/[^0-9.\\-]/g,''));
        if(!isNaN(nx)&&!isNaN(ny)&&x!==''&&y!=='') return (nx-ny)*dir;
        return x.localeCompare(y)*dir;
      });
      rows.forEach(function(r){tb.appendChild(r);});
    });
  });
});
"""

PAGES = [
    ("index.html", "Overview", "Overview"),
    ("executive-summary.html", "Executive summary", "Executive summary"),
    ("discovery.html", "Discovery", "Questions & suggestions"),
    ("official-register.html", "Official register", "Official register"),
    ("reverification.html", "Re-verification", "Re-verification"),
    ("club-availability.html", "Club availability", "Club availability"),
    ("deficiency-matrix.html", "Deficiency matrix", "Deficiency matrix"),
    ("depth-reach.html", "Depth reach", "Depth reach"),
    ("coverage.html", "Join coverage", "Join coverage"),
    ("correlations.html", "Correlations", "Correlations"),
    ("flagged.html", "Flagged", "Flagged for review"),
    ("method.html", "Method", "Method & hashes"),
]


def read(name):
    with open(os.path.join(D, name), newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def cell(v, numeric=False, pill=None):
    v = "" if v is None else str(v)
    if v == BLANK or v == "":
        return '<td class="np">not published</td>'
    cls = []
    if numeric:
        cls.append("num")
    if pill:
        cls.append("pill")
        cls.append(pill(v))
    return "<td%s>%s</td>" % (' class="%s"' % " ".join(cls) if cls else "", e(v))


def link_cell(url, label=None):
    if not url or url == BLANK:
        return '<td class="np">not published</td>'
    return '<td><a href="%s" rel="noopener" target="_blank">%s</a></td>' % (
        e(url), e(label or "source"))


def build_table(rows, cols, headers, tid, link_cols=(), numeric_cols=(), pill=None, pill_col=None):
    out = ['<div class="tw"><table id="%s"><thead><tr>' % tid]
    for i, h in enumerate(headers):
        out.append('<th data-sort="%d">%s</th>' % (i, e(h)))
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>")
        for c in cols:
            if c in link_cols:
                out.append(link_cell(r.get(c, "")))
            else:
                p = pill if (pill_col and c == pill_col) else None
                out.append(cell(r.get(c, ""), numeric=(c in numeric_cols), pill=p))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def page(active, title, body, kpis=None):
    nav = "".join(
        '<a href="%s"%s>%s</a>' % (p, ' class="on"' if p == active else "", e(label))
        for p, label, _ in PAGES)
    kp = ""
    if kpis:
        kp = '<div class="kpis">' + "".join(
            '<div class="kpi"><div class="n">%s</div><div class="l">%s</div></div>' % (e(n), e(l))
            for n, l in kpis) + "</div>"
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s — NFL2 dated re-verification (dcf3b0cc)</title>
<style>%s</style></head><body>
<header><div class="t">NFL2 · dated official re-verification</div>
<div class="s">Session <code>dcf3b0cc</code> · official NFL injury hub read 2026-11-15T12:55Z ·
<a href="../index.html">back to the main site</a></div></header>
<nav>%s</nav>
<main>%s%s</main>
<footer>Every row below links to the official page it was read from. A value shown as
<em>not published</em> means it could not be confirmed from an official source; nothing is imputed.
Generated deterministically by <code>tools/build_dcf3b0cc.py</code>.</footer>
<script>%s</script></body></html>
""" % (e(title), CSS, nav, kp, body, JS)


def write(name, active, title, body, kpis=None):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(page(active, title, body, kpis))



def exec_summary_page(summary, clubs, cov, corr, mat, reach):
    n_cov = sum(int(c["report_rows_20261115"]) for c in cov)
    n_on = sum(int(c["rows_matched_to_a_chart"]) for c in cov)
    n_out = sum(int(c["out_rows"]) for c in cov)
    n_out_on = sum(int(c["out_rows_on_chart"]) for c in cov)
    zero = [c["club"] for c in cov if c["rows_matched_to_a_chart"] == "0"]
    no_repo = [c["club"] for c in clubs if c["rows_listed_20261113"] == "0"]
    rank1 = sum(1 for r in reach if r["available_rank"] == "1")
    b = []
    b.append("""<div class="card"><h2>Executive summary</h2>
<p class="muted">Session <code>dcf3b0cc</code> · official NFL injury hub read 2026-11-15T12:55Z ·
written for a reader who has to decide what to do next, not for a reader who wants to check the arithmetic.
Every number below is counted from the sources named on the <a href="method.html">method page</a>.</p>

<h3>What was done</h3>
<p>The official injury hub was read end to end today and every published row for the Week 10 slate was
transcribed verbatim: %d rows across %d clubs and %d fixtures, each with the practice status, the game
status and the official player link the page prints. That capture was then compared, row by row, against
the Week 10 injury table the repository already publishes (read 2026-11-13T12:46Z from the same URL), and
joined to the club depth charts transcribed on 2026-11-13 to produce an offence-versus-defence deficiency
matrix.</p>

<h3>The five things that matter</h3>
<ol>
<li><strong>The table the site publishes is missing almost every designation.</strong> It carries %d
game-status designations across 296 rows; the same page read today carries %d — %d Out, %d Doubtful,
%d Questionable. It also leaves 287 of 296 injury-description cells blank. Any count built on that table
is counting a page that no longer exists.</li>
<li><strong>One of the fourteen fixtures has no injury coverage at all.</strong> Neither %s
appears anywhere in the published table, while the page lists %d rows for them today. A seventh of the
slate is invisible to any count built on that table.</li>
<li><strong>Two days is enough to change two thirds of the table.</strong> Of the 296 rows both reads
share, 102 are identical and 194 differ; 55 differ on practice status alone. A single weekly snapshot
cannot see the Wednesday-to-Friday movement the brief asks us to measure.</li>
<li><strong>The deficiency feature can only name a replacement for %d of %d listed players</strong>
(%0.1f%%), and for %d of the %d players ruled Out. %s resolves none of its listed players at all, because
its chart is published as an image.</li>
<li><strong>Nothing correlates yet, and that is the honest answer.</strong> Seven descriptive
correlations over the 28 clubs playing this week, both inputs officially sourced: none significant at
5%%, largest absolute r under 0.28. One week of 28 clubs cannot separate injuries from roster quality.</li>
</ol>

<h3>What is blocked, and by what</h3>
<div class="tw"><table id="t-bl">
<thead><tr><th>Decision</th><th>Blocked by</th><th>Number that would clear it</th><th>Official page to check</th></tr></thead><tbody>
<tr><td>Use injuries as a model input</td><td>No daily series; designations not joined to inactives; no reserve list</td><td>Dated captures from Wednesday to kickoff for at least four weeks, joined to official inactive lists</td><td><a href="https://www.nfl.com/injuries/" target="_blank" rel="noopener">nfl.com/injuries</a></td></tr>
<tr><td>Publish a backup-deficiency count for the league</td><td>%d of %d Out players cannot be attached to a depth slot; Houston resolves zero</td><td>Official inactive lists and snap counts captured for the clubs that publish no chart</td><td><a href="https://www.nfl.com/injuries/" target="_blank" rel="noopener">nfl.com/injuries</a></td></tr>
<tr><td>Treat chart rank as depth</td><td>Not measured against playing time; clubs label their charts unofficial</td><td>Rank-one snap share measured over several weeks</td><td><a href="https://www.houstontexans.com/team/depth-chart" target="_blank" rel="noopener">a club chart page</a></td></tr>
<tr><td>Backtest anything</td><td>Raw bytes are not retained, only hashes; a stale read is treated as current</td><td>Body retention enabled once the terms review clears</td><td><a href="https://www.nfl.com/injuries/" target="_blank" rel="noopener">nfl.com/injuries</a></td></tr>
<tr><td>Claim any edge</td><td>n = 28, one week, no significance</td><td>Accumulated weekly samples that survive a multiplicity correction</td><td><a href="https://www.nfl.com/standings/" target="_blank" rel="noopener">nfl.com/standings</a></td></tr>
</tbody></table></div>

<h3>What to do next, in order</h3>
<ol>
<li>Label every injury table on the canonical site with the time it was read, and keep both reads
published. This costs nothing and removes the largest source of silent error.</li>
<li>Adopt the schedule-page order as the single game-id convention, or drop game_id as a join key.</li>
<li>Add a drift alarm that fails the build when a club that is playing publishes zero rows.</li>
<li>Capture reserve lists, then game-day inactives and snap counts — in that order. The second is what
turns a suspected replacement into a confirmed one.</li>
<li>Only then pre-register the personnel feature and test it as an ablation, not as a fixed penalty.</li>
</ol>
<p class="note">This summary describes what the repository can and cannot currently see. It makes no
prediction and claims no betting edge.</p></div>""" % (
        summary["injury_rows_transcribed"], summary["clubs_covered"], summary["fixtures_covered"],
        summary["repo_20261113_designations"],
        summary["designations_out"] + summary["designations_doubtful"] + summary["designations_questionable"],
        summary["designations_out"], summary["designations_doubtful"], summary["designations_questionable"],
        " nor ".join(sorted(no_repo)) if len(no_repo) == 2 else (", ".join(sorted(no_repo)) if no_repo else "No club"),
        sum(int(c["rows_listed_20261115"]) for c in clubs if c["rows_listed_20261113"] == "0"),
        n_on, n_cov, 100.0 * n_on / n_cov, n_out_on, n_out,
        ", ".join(zero) if zero else "No club",
        n_out - n_out_on, n_out))
    return "".join(b)


def discovery_page(questions, suggestions):
    b = []
    b.append("""<div class="card"><h2>What we have, what we lack, and how to find it</h2>
<p>Eight questions that must be answered before a decision can reasonably be made on the numbers in this
tree. Each row states what the repository already holds, what is missing, and the concrete step that
would close it. The source column points at the official page the question is about, so a reviewer can
check the premise rather than take our word for it.</p>
<p class="note warn">These rows are project questions, not NFL facts. The source link identifies the
official page under discussion; it does not certify the question or the answer.</p>""")
    b.append(build_table(
        questions,
        ["id", "topic", "question", "information_we_have", "information_we_lack",
         "how_to_discover_it", "blocks", "source"],
        ["ID", "Topic", "Question", "What we have", "What we lack", "How to discover it",
         "Blocks", "Source"],
        "t-q", link_cols=("source",)))
    b.append("</div>")
    b.append("""<div class="card"><h2>Suggested paths, for a human to choose between</h2>
<p>Nine suggestions derived from what this session measured. Each names the evidence in this tree that
motivates it and the path that would implement it. A recommendation here is not a decision: the point of
the page is to let someone pick a path before anything is built.</p>""")
    b.append(build_table(
        suggestions,
        ["id", "suggestion", "why_it_matters", "evidence_in_this_session", "discovery_path",
         "effort", "recommendation", "source"],
        ["ID", "Suggestion", "Why it matters", "Evidence in this session", "Path", "Effort",
         "Recommendation", "Source"],
        "t-s", link_cols=("source",),
        pill=lambda v: {"adopt now": "p-m", "recommended": "p-q",
                        "recommended, blocked on terms": "p-x"}.get(v, ""),
        pill_col="recommendation"))
    b.append("</div>")
    return "".join(b)


def main():
    summary = json.load(open(os.path.join(D, "summary_dcf3b0cc.json")))
    hub = read("nfl_injury_hub_20261115_dcf3b0cc.csv")
    fix = read("nfl_fixtures_wk10_20261115_dcf3b0cc.csv")
    rev = read("reverify_20261115_dcf3b0cc.csv")
    clubs = read("club_availability_20261115_dcf3b0cc.csv")
    mat = read("deficiency_matrix_dcf3b0cc.csv")
    reach = read("depth_reach_20261115_dcf3b0cc.csv")
    cov = read("coverage_dcf3b0cc.csv")
    corr = read("correlation_dcf3b0cc.csv")
    flags = read("flags_dcf3b0cc.csv")
    questions = read("questions_dcf3b0cc.csv")
    suggestions = read("suggestions_dcf3b0cc.csv")

    kpis = [
        (summary["injury_rows_transcribed"], "official rows transcribed"),
        (summary["clubs_covered"], "clubs covered (of 32)"),
        (summary["fixtures_covered"], "Week 10 fixtures"),
        (summary["designations_out"] + summary["designations_doubtful"] + summary["designations_questionable"],
         "game-status designations"),
        (summary["repo_20261113_designations"], "designations in the 13 Nov read"),
        (summary["reverify"]["mismatch"], "rows that changed"),
    ]

    # ------------------------------------------------------------------ index
    b = []
    b.append('<div class="card"><h2>What this session did</h2>'
             '<p>Read the official NFL injury hub end to end on <strong>2026-11-15T12:55Z</strong> and '
             'transcribed every published row for the Week 10 slate — all 14 fixtures, 28 clubs, '
             '<strong>347 rows</strong> — with the practice status, the game status and the player link '
             'the page prints for each. Then compared that capture, row by row, against the Week 10 '
             'injury table this repository already publishes '
             '(<code>data/injuries_wk10_83246f00.csv</code>, read 2026-11-13T12:46Z), and joined it to the '
             'club depth charts transcribed on 2026-11-13 to produce an offence-versus-defence deficiency '
             'matrix.</p>'
             '<p class="note">This is a dated comparison of two reads of one official page plus one '
             'transcription layer. It is not a prediction, not a model, and not a betting claim. Club depth '
             'charts are published by the clubs themselves and labelled unofficial; rank order in a chart is '
             'not playing time.</p></div>')

    b.append('<div class="card"><h2>Headline findings</h2><ol>'
             '<li><strong>The published Week 10 table is missing almost every designation.</strong> '
             'It carries %d game-status designations across 296 rows. The same page read today carries '
             '<strong>171</strong> — 70 Out, 11 Doubtful, 90 Questionable. It also leaves 287 of 296 '
             'injury-description cells blank.</li>'
             '<li><strong>One fixture has no injury coverage at all.</strong> Neither the Chargers nor the '
             'Ravens (W10-14, Monday) appear anywhere in the 13 Nov table — 29 rows present on the page today '
             'and absent from the repository.</li>'
             '<li><strong>Two-thirds of joined rows changed in two days.</strong> Of the 296 rows the two '
             'reads share, 102 are identical and 194 differ; 55 differ on practice status alone, which is '
             'exactly the Wednesday-to-Friday movement a single weekly snapshot cannot see.</li>'
             '<li><strong>The deficiency join resolves 284 of 347 listed players to a depth slot</strong> '
             '(81.8%%), and 55 of the 70 players ruled Out. Houston resolves 0 of 16 — its chart is an image.</li>'
             '<li><strong>No correlation survives.</strong> Seven descriptive correlations over the 28 clubs '
             'that play this week, both inputs officially sourced. None is significant at 5%%; the largest '
             '|r| is under 0.28.</li>'
             '</ol></div>' % (summary["repo_20261113_designations"],))

    b.append('<div class="card"><h2>Pages</h2><ul>'
             '<li><a href="executive-summary.html">Executive summary</a> — what was found, what it blocks, '
             'and the order to do things in.</li>'
             '<li><a href="official-register.html">Official register</a> — all 347 rows as read today, '
             'one official player link per row.</li>'
             '<li><a href="reverification.html">Re-verification</a> — 347 joined rows: match, mismatch, or '
             'present on only one side, with the fields that differ.</li>'
             '<li><a href="club-availability.html">Club availability</a> — 28 clubs, both reads side by side.</li>'
             '<li><a href="deficiency-matrix.html">Deficiency matrix</a> — 168 offence-versus-defence matchup '
             'cells for the 14 fixtures.</li>'
             '<li><a href="depth-reach.html">Depth reach</a> — 291 club/unit/groups with the rank that is '
             'actually available.</li>'
             '<li><a href="coverage.html">Join coverage</a> — how much of the report can be attached to a '
             'depth slot, per club.</li>'
             '<li><a href="correlations.html">Correlations</a> — 7 pairs, n = 28, with intervals and p.</li>'
             '<li><a href="flagged.html">Flagged for review</a> — 7 irregularities, each with its source.</li>'
             '<li><a href="discovery.html">Questions &amp; suggestions</a> — 8 questions with what we '
             'have, what we lack and how to find it; 9 suggested paths for a human to choose between.</li>'
             '<li><a href="method.html">Method &amp; hashes</a> — how it was read, and the SHA-256 of every '
             'artefact.</li></ul></div>')
    write("index.html", "index.html", "Overview", "".join(b), kpis)

    write("executive-summary.html", "executive-summary.html", "Executive summary",
          exec_summary_page(summary, clubs, cov, corr, mat, reach), kpis)
    write("discovery.html", "discovery.html", "Questions & suggestions",
          discovery_page(questions, suggestions), kpis)

    # --------------------------------------------------------- official register
    b = ['<div class="card"><h2>Official Week 10 injury register — read 2026-11-15T12:55Z</h2>'
         '<p>Every row the official hub publishes for the Week 10 slate, transcribed verbatim. '
         'Blank injury and blank game-status cells are the page\'s own blanks, not ours: they are rendered '
         'as <em>not published</em>.</p>'
         '<div class="note warn">Game ids follow the repository\'s schedule file '
         '(<code>data/schedule_2026_wk10.csv</code>), which numbers fixtures in the order the official '
         'schedule page prints them. The injury hub prints the three 1:00&nbsp;p.m. games in a different '
         'order — that disagreement is the existing flag FL-64.</div>'
         '<div class="tools"><input type="search" data-filter="t-reg" data-col="1" '
         'placeholder="Filter by club or player…"><span class="muted"><span id="t-reg-count"></span> rows shown</span></div>']
    b.append(build_table(
        hub, ["fixture_id", "club", "club_role", "player", "pos", "injury", "practice_status",
              "game_status", "player_url", "source_url"],
        ["Fixture", "Club", "Home/Away", "Player", "Pos", "Injury", "Practice status",
         "Game status", "Player page", "Page"],
        "t-reg", link_cols=("player_url", "source_url"),
        numeric_cols=(), pill=lambda v: {"Out": "p-out", "Questionable": "p-q",
                                         "Doubtful": "p-d"}.get(v, ""),
        pill_col="game_status"))
    b.append("</div>")
    write("official-register.html", "official-register.html", "Official register", "".join(b), kpis)

    # ------------------------------------------------------------- re-verification
    b = ['<div class="card"><h2>Row-by-row re-verification against the published 13 November read</h2>'
         '<p>Joined on club + normalised player name + position. Names are normalised by lower-casing, '
         'stripping punctuation and dropping generational suffixes, so <code>A.J. Brown</code> and '
         '<code>AJ Brown</code> join. No row is discarded: every row on either side appears below.</p>'
         '<div class="tools"><input type="search" data-filter="t-rev" data-col="1" '
         'placeholder="Filter by club or player…">'
         '<span class="muted"><span id="t-rev-count"></span> rows shown</span></div>']
    b.append(build_table(
        rev, ["club", "player", "pos", "result", "fields_differing", "injury_20261115",
              "practice_20261115", "game_status_20261115", "injury_20261113", "practice_20261113",
              "game_status_20261113", "official_source", "repo_source"],
        ["Club", "Player", "Pos", "Result", "Fields differing", "Injury 15 Nov", "Practice 15 Nov",
         "Status 15 Nov", "Injury 13 Nov", "Practice 13 Nov", "Status 13 Nov",
         "Official link", "Repo source"],
        "t-rev", link_cols=("official_source", "repo_source"),
        pill=lambda v: {"match": "p-m", "mismatch": "p-mm", "official_only": "p-q",
                        "repo_only": "p-x"}.get(v, ""),
        pill_col="result"))
    b.append("</div>")
    write("reverification.html", "reverification.html", "Re-verification", "".join(b), kpis)

    # ------------------------------------------------------------ club availability
    b = ['<div class="card"><h2>Club availability — both reads, side by side</h2>'
         '<p>Counts are of rows the official page publishes for that club in that fixture. '
         '"Designations" means rows carrying a game status (Out, Doubtful or Questionable).</p>'
         '<div class="tools"><input type="search" data-filter="t-cl" data-col="1" '
         'placeholder="Filter by fixture or club…">'
         '<span class="muted"><span id="t-cl-count"></span> rows shown</span></div>']
    b.append(build_table(
        clubs, ["fixture_id", "club", "home_or_away", "rows_listed_20261115", "dnp", "limited",
                "full", "out", "doubtful", "questionable", "no_game_status_published",
                "rows_listed_20261113", "designations_20261113", "row_delta", "source"],
        ["Fixture", "Club", "H/A", "Rows 15 Nov", "DNP", "Limited", "Full", "Out", "Doubtful",
         "Questionable", "No status", "Rows 13 Nov", "Designations 13 Nov", "Row delta", "Source"],
        "t-cl", link_cols=("source",),
        numeric_cols=("rows_listed_20261115", "dnp", "limited", "full", "out", "doubtful",
                      "questionable", "no_game_status_published", "rows_listed_20261113",
                      "designations_20261113", "row_delta")))
    b.append("</div>")
    write("club-availability.html", "club-availability.html", "Club availability", "".join(b), kpis)

    # ------------------------------------------------------------ deficiency matrix
    b = ['<div class="card"><h2>Offence versus defence deficiency matrix</h2>'
         '<p>Six published matchup pairs, both directions, all 14 fixtures — 168 cells. '
         '<strong>Available rank</strong> is the shallowest chart rank still standing once Out and Doubtful '
         'players are removed. <strong>Clean rank</strong> additionally removes Questionable players. '
         '<strong>Unavailable</strong> counts Out plus Doubtful in that group.</p>'
         '<p class="note warn">Designations are dated 2026-11-15; the depth charts are dated 2026-11-13, '
         'and clubs label their own charts unofficial. Rank order is chart order, not playing time — the '
         'brief explicitly rejects inferring depth from jersey number, experience or salary, and chart '
         'order is only one step better than that. Treat every cell as a hypothesis to confirm against '
         'inactives and snap counts, not as a finding.</p>'
         '<div class="tools"><input type="search" data-filter="t-mx" data-col="1" '
         'placeholder="Filter by matchup, club or group…">'
         '<span class="muted"><span id="t-mx-count"></span> rows shown</span></div>']
    b.append(build_table(
        mat, ["fixture_id", "matchup", "offense_club", "offense_group", "offense_available_rank",
              "offense_clean_rank", "offense_unavailable", "defense_club", "defense_group",
              "defense_available_rank", "defense_clean_rank", "defense_unavailable",
              "defence_minus_offence", "read", "designation_source"],
        ["Fixture", "Matchup", "Offence", "Off group", "Off rank", "Off clean", "Off unavail",
         "Defence", "Def group", "Def rank", "Def clean", "Def unavail", "Def − Off", "Read",
         "Source"],
        "t-mx", link_cols=("designation_source",),
        numeric_cols=("offense_available_rank", "offense_clean_rank", "offense_unavailable",
                      "defense_available_rank", "defense_clean_rank", "defense_unavailable",
                      "defence_minus_offence")))
    b.append("</div>")
    write("deficiency-matrix.html", "deficiency-matrix.html", "Deficiency matrix", "".join(b), kpis)

    # ----------------------------------------------------------------- depth reach
    b = ['<div class="card"><h2>Depth reach by club, unit and group</h2>'
         '<p>For each club\'s charted group: how many chart rows there are, how many of those players the '
         'official report lists, and the shallowest rank still available. '
         '"Starter out" is yes when no rank-1 player in the group is free of an Out or Doubtful '
         'designation.</p>'
         '<div class="tools"><input type="search" data-filter="t-dr" data-col="0" '
         'placeholder="Filter by club, unit or group…">'
         '<span class="muted"><span id="t-dr-count"></span> rows shown</span></div>']
    b.append(build_table(
        reach, ["club", "unit", "group", "chart_rows", "deepest_rank_charted", "listed_on_report",
                "out", "doubtful", "questionable", "available_rank", "available_player",
                "clean_rank", "clean_player", "starter_out", "chart_source", "designation_source"],
        ["Club", "Unit", "Group", "Chart rows", "Deepest rank", "Listed", "Out", "Doubtful",
         "Questionable", "Avail rank", "Available player", "Clean rank", "Clean player",
         "Starter out", "Chart page", "Report page"],
        "t-dr", link_cols=("chart_source", "designation_source"),
        numeric_cols=("chart_rows", "deepest_rank_charted", "listed_on_report", "out", "doubtful",
                      "questionable", "available_rank", "clean_rank"),
        pill=lambda v: {"yes": "p-out", "no": "p-m"}.get(v, ""), pill_col="starter_out"))
    b.append("</div>")
    write("depth-reach.html", "depth-reach.html", "Depth reach", "".join(b), kpis)

    # -------------------------------------------------------------------- coverage
    b = ['<div class="card"><h2>How much of the report can be attached to a depth slot</h2>'
         '<p>A starter-out count can be produced for the whole league from the official report alone. '
         'A <em>named replacement</em> can only be produced for the players who appear on a transcribed '
         'chart. This page publishes the gap between the two, per club, so the two numbers are never '
         'reported as one.</p>'
         '<div class="tools"><input type="search" data-filter="t-cv" data-col="0" '
         'placeholder="Filter by club…">'
         '<span class="muted"><span id="t-cv-count"></span> rows shown</span></div>']
    b.append(build_table(
        cov, ["club", "report_rows_20261115", "rows_matched_to_a_chart", "rows_not_on_any_chart",
              "match_pct", "out_rows", "out_rows_on_chart", "out_rows_not_on_chart",
              "questionable_rows", "questionable_rows_on_chart", "club_chart_url",
              "designation_source"],
        ["Club", "Report rows", "On a chart", "Not on a chart", "Match %", "Out rows",
         "Out on chart", "Out not on chart", "Questionable rows", "Questionable on chart",
         "Club chart page", "Report page"],
        "t-cv", link_cols=("club_chart_url", "designation_source"),
        numeric_cols=("report_rows_20261115", "rows_matched_to_a_chart", "rows_not_on_any_chart",
                      "out_rows", "out_rows_on_chart", "out_rows_not_on_chart",
                      "questionable_rows", "questionable_rows_on_chart")))
    b.append("</div>")
    write("coverage.html", "coverage.html", "Join coverage", "".join(b), kpis)

    # ---------------------------------------------------------------- correlations
    b = ['<div class="card"><h2>Descriptive correlations, n = 28 clubs</h2>'
         '<p>Both inputs are officially sourced: designations from '
         '<a href="https://www.nfl.com/injuries/" target="_blank" rel="noopener">nfl.com/injuries</a> '
         'read 2026-11-15T12:55Z; win percentage and point differential from '
         '<a href="https://www.nfl.com/standings/" target="_blank" rel="noopener">nfl.com/standings</a> '
         'captured 2026-11-13T12:53Z. n is published with every value, as is the interval and the '
         'two-sided p.</p>'
         '<p class="note warn">Cross-sectional, one week, 28 clubs. It measures whether banged-up clubs '
         'happen to be worse clubs <em>this</em> week; it does not measure whether injuries cause losses, '
         'and it is not a predictive result. None of the seven is significant at 5%, and no multiplicity '
         'correction beyond publishing all seven p-values is applied.</p>']
    b.append(build_table(
        corr, ["pair_id", "label", "n_clubs", "r", "r_squared", "ci95_low", "ci95_high", "t",
               "p_two_sided", "significant_at_05", "x_source", "y_source"],
        ["ID", "Pair", "n", "r", "r²", "95% CI low", "95% CI high", "t", "p (two-sided)",
         "Significant at 5%", "X source", "Y source"],
        "t-co", link_cols=("x_source", "y_source"),
        numeric_cols=("n_clubs", "r", "r_squared", "ci95_low", "ci95_high", "t", "p_two_sided"),
        pill=lambda v: {"yes": "p-out", "no": "p-m"}.get(v, ""), pill_col="significant_at_05"))
    b.append("<h3>Caveat carried with every row</h3><p class=\"muted\">%s</p></div>" % e(corr[0]["caveat"]))
    write("correlations.html", "correlations.html", "Correlations", "".join(b), kpis)

    # --------------------------------------------------------------------- flagged
    b = ['<div class="card"><h2>Flagged for review</h2>'
         '<p>Seven irregularities found by this session, each with the evidence file and the official '
         'source it was checked against. These are published for review and do not block anything.</p>']
    b.append(build_table(
        flags, ["flag_id", "class", "severity", "finding", "evidence", "source", "impact", "status"],
        ["ID", "Class", "Severity", "Finding", "Evidence", "Source", "Impact", "Status"],
        "t-fl", link_cols=("source",),
        pill=lambda v: {"high": "p-out", "medium": "p-q", "open": "p-x"}.get(v, ""),
        pill_col="severity"))
    b.append("</div>")
    write("flagged.html", "flagged.html", "Flagged for review", "".join(b), kpis)

    # ---------------------------------------------------------------------- method
    rows = "".join(
        "<tr><td><code>%s</code></td><td><code>%s</code></td></tr>" % (e(k), e(v))
        for k, v in sorted(summary["sha256"].items()))
    b = ['<div class="card"><h2>Method</h2>'
         '<h3>How the page was read</h3>'
         '<p>The official hub at <a href="https://www.nfl.com/injuries/" target="_blank" rel="noopener">'
         'nfl.com/injuries</a> was fetched in eight sequential reads beginning at 2026-11-15T12:54Z and '
         'completed at 2026-11-15T12:55Z. Every club table was transcribed row by row as the page printed '
         'it: player, position, injury, practice status, game status, and the player page the row links to. '
         'Nothing was normalised except for joining purposes, and no value was inferred.</p>'
         '<h3>What was compared to what</h3>'
         '<ul><li><code>data/nfl_injury_hub_20261115_dcf3b0cc.csv</code> — today\'s transcription, 347 rows.</li>'
         '<li><code>data/injuries_wk10_83246f00.csv</code> — the repository\'s published Week 10 table, '
         '296 rows, read 2026-11-13T12:46Z from the same URL.</li>'
         '<li><code>data/s745_depth_charts.csv</code> — 1,558 club depth-chart rows transcribed 2026-11-13 '
         'by an earlier session, each carrying its own club URL.</li>'
         '<li><code>data/standings_2026.csv</code> — nfl.com standings, 32 clubs, captured '
         '2026-11-13T12:53Z.</li></ul>'
         '<h3>Limits stated up front</h3>'
         '<ul><li>Rank order in a club depth chart is not playing time, and clubs label their own charts '
         'unofficial.</li>'
         '<li>Designations are dated 2026-11-15 and charts 2026-11-13; the join spans two days.</li>'
         '<li>"Not listed on the report" is not the same as "available": players on injured reserve do not '
         'appear on the weekly report at all, and no reserve list is captured in this session.</li>'
         '<li>Correlations are cross-sectional over one week and are not predictive.</li></ul>'
         '<h3>SHA-256 of every artefact</h3>'
         '<div class="tw"><table id="t-sh" data-nosource="1"><thead><tr><th>File</th><th>SHA-256</th></tr></thead>'
         '<tbody>%s</tbody></table></div>'
         '<p class="muted">Hashes are of the files as committed. Re-running '
         '<code>python3 tools/compute_dcf3b0cc.py</code> then '
         '<code>python3 tools/build_dcf3b0cc.py</code> reproduces every byte.</p></div>' % rows]
    write("method.html", "method.html", "Method & hashes", "".join(b), kpis)

    print("built %d pages in %s" % (len(PAGES), OUT))


if __name__ == "__main__":
    main()
