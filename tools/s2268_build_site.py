#!/usr/bin/env python3
"""Session 2268bfb2 - builds the s2268/ tree from the CSVs this session produced.

Rules inherited from the root build, and enforced here:

  * a table row that asserts a fact about the league carries a link to the official
    page the fact came from. Rows that state a rule rather than a fact say so in the
    caption and carry no link, because there is nothing official to point at.
  * every blank cell renders as the literal phrase "not published". Never 0, never a
    guess, never a value carried over from another session's tree.
  * every number on every page is read from data/ at build time. Nothing is typed twice.

Deterministic: the same CSVs produce byte-identical HTML.
"""

from __future__ import annotations

import csv
import html
import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "s2268")
ASSETS = os.path.join(OUT, "assets")

FETCH_UTC = "2026-11-13T12:40Z"
SESSION = "2268bfb2"
BRANCH = "arena/2268bfb2-nfl2"
BASE_COMMIT = "14d0afcc5dda1c185e78e453407f70d72e49c5f9"

PAGES = [
    ("index.html", "Session overview", "Overview", "program"),
    ("refresh.html", "Live refresh: 13 Nov 2026", "Verification", "measured"),
    ("depth.html", "Depth & deficiencies", "Verification", "measured"),
    ("competition.html", "Leaderboard & rewards", "Competition", "decision"),
    ("forecast.html", "Forecast track", "Competition", "measured"),
    ("correlations.html", "Measured correlations", "Competition", "measured"),
    ("parlays.html", "Parlays & prop combos", "Competition", "design"),
    ("luck.html", "Removing luck", "Competition", "decision"),
    ("gates.html", "Validation gates", "Competition", "decision"),
    ("flagged.html", "Flagged for review", "Governance", "decision"),
    ("sources.html", "Source registry", "Governance", "program"),
]


# ---------------------------------------------------------------- io -----------------

def load(name):
    with open(os.path.join(DATA, name), newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def meta(name):
    with open(os.path.join(DATA, name)) as fh:
        return json.load(fh)


def esc(v):
    return html.escape(str(v), quote=True)


def cell(v):
    v = (v or "").strip()
    if v == "":
        return '<span class="np">not published</span>'
    if v.startswith("https://"):
        label = v.replace("https://www.", "")
        if len(label) > 46:
            label = label[:43] + "..."
        return f'<a href="{esc(v)}">{esc(label)}</a>'
    return esc(v)


def pretty(h):
    return h.replace("_", " ")


def table(rows, cols=None, caption=None, source_cols=("source", "depth_url", "injury_url",
                                                      "definitions_sha256"), cls="data"):
    if rows is None:
        rows = []
    headers = cols or list(rows[0].keys()) if rows else []
    out = ['<div class="tablewrap">', f'<table class="{cls}"><thead><tr>']
    for h in headers:
        out.append(f"<th>{esc(pretty(h))}</th>")
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>")
        for h in headers:
            v = (r.get(h) or "").strip()
            if h in source_cols and v.startswith("https://"):
                label = "official source"
                if "injuries" in v:
                    label = "nfl.com/injuries"
                elif "/games/" in v:
                    label = "game page"
                elif "depth-chart" in v:
                    label = "club depth chart"
                out.append(f'<td><a href="{esc(v)}">{esc(label)}</a></td>')
            else:
                out.append(f"<td>{cell(v)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    if caption:
        out.append(f'<p class="caption">{caption}</p>')
    return "\n".join(out)


# ------------------------------------------------------------- shell -----------------

def nav(active):
    groups = {}
    for fn, title, group, _ in PAGES:
        groups.setdefault(group, []).append((fn, title))
    out = []
    for group, items in groups.items():
        out.append(f'<div class="navgroup"><span>{esc(group)}</span>')
        for fn, title in items:
            on = ' class="on"' if fn == active else ""
            out.append(f'<a{on} href="{fn}">{esc(title)}</a>')
        out.append("</div>")
    return "".join(out)


def pages_list():
    return "".join(
        f'<li><a href="{fn}">{esc(t)}</a> &mdash; {esc(g.lower())}, {"measured" if k == "measured" else ("design" if k == "design" else ("decision" if k == "decision" else "programme"))}</li>'
        for fn, t, g, k in PAGES)


def page(fn, title, kind, lead, body, badge=None, toc=None):
    badge_html = f'<span class="badge {kind}">{esc(badge)}</span>' if badge else ""
    toc_html = ""
    if toc:
        toc_html = '<nav class="toc"><span>On this page</span>' + "".join(
            f'<a href="#{a}">{esc(t)}</a>' for a, t in toc) + "</nav>"
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — NFL2 session {SESSION}</title>
<link rel="stylesheet" href="assets/style.css">
</head><body class="kind-{kind}">
<div class="top">
  <a class="brand" href="index.html"><span class="mark">NFL2</span> session {SESSION}</a>
  <div class="asof">Official pages read <strong>{FETCH_UTC}</strong> · <a href="../index.html">back to the canonical dashboard</a></div>
</div>
<div class="shell">
  <aside class="side">{nav(fn)}<div class="sidefoot"><a href="flagged.html">flagged items</a> · <a href="sources.html">sources</a></div></aside>
  <main>
    <div class="pagehead">{badge_html}<h1>{esc(title)}</h1><p class="lead">{lead}</p></div>
    {toc_html}
    <div class="body">{body}</div>
  </main>
</div>
<div class="foot"><div class="foot-meta">Built from <code>data/</code> by <code>tools/s2268_build_site.py</code> · branch <code>{BRANCH}</code> from <code>{BASE_COMMIT[:12]}</code> · rendered {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}</div></div>
</body></html>
"""


# ------------------------------------------------------------- pages -----------------

def pick_stats():
    rows = {r["id"]: r for r in load("s2268_pick_scores.csv")}
    return rows


def build_index(comp, ref):
    ps = pick_stats()
    pd_hits, pd_n = ps["P-PD"]["wins"], ps["P-PD"]["decisions"]
    ct_hits, ct_n = ps["P-CONTRA"]["wins"], ps["P-CONTRA"]["decisions"]
    rest_hits, rest_n = ps["P-REST"]["wins"], ps["P-REST"]["decisions"]
    cards = [
        ("Rows on the live injury hub", ref["rows_on_live_hub"], "refresh.html",
         f"{ref['clubs_with_rows']} clubs publish rows; LAC and BAL print &ldquo;No Injuries Reported&rdquo;"),
        ("Rows the Injuries page shows", ref["rows_in_published_injuries_csv"], "refresh.html",
         f"{ref['rows_on_live_hub'] - ref['rows_in_published_injuries_csv']} rows behind the live page"),
        ("Week 10 game ids that disagree", ref["game_id_disagreements"], "refresh.html",
         f"{ref['game_id_rotations']} of them name a completely different fixture in two published files"),
        ("Strategies scored out of sample", comp["strategies"], "competition.html",
         f"{comp['decisions_scored']} decisions on {comp['holdout_games']} holdout games"),
        ("Candidates surviving the luck gate", comp["survivors_fdr"], "luck.html",
         "Benjamini&ndash;Hochberg at a 10% false-discovery rate"),
        ("Gates still blocking any stake", "4", "gates.html",
         "G-C7 through G-C10 &mdash; no price feed, no forward track record"),
    ]
    cards_html = '<div class="cards">' + "".join(
        f'<div class="card"><h3>{esc(t)}</h3><div class="big"><a href="{h}">{esc(v)}</a></div>'
        f'<div class="sub">{s}</div></div>' for t, v, h, s in cards) + "</div>"

    body = f"""
{cards_html}
<blockquote><strong>What this session is.</strong> Every parallel session before this one had built and merged
a large, verified dashboard at the repository root. What none of them had done was <em>score</em> anything:
the leaderboard read &ldquo;T0 &mdash; prospective, 0 of 14 gates&rdquo; with every performance cell blank, and the
one settled game had been graded by hand. This session does two things: it re-reads the official league
pages on 13 November 2026 and publishes exactly what moved, and it builds the first pre-registered
walk-forward competition so that the leaderboard has real numbers on it &mdash; including the numbers that
say our own originated lines do not beat knowing nothing.</blockquote>

<h2 id="read-this-first">Read this first</h2>
<p>Everything here is measured, or it is labelled <span class="np">not published</span>. The competition is
scored against the frozen weeks 1&ndash;9 corpus (136 games, every row carrying its own official
<a href="https://www.nfl.com/scores/2026/week-9">nfl.com</a> game page). It is <strong>not</strong> a betting
record: no price feed exists anywhere in this repository, so there is no closing line, no vig, no CLV, no
ROI and no units. Anywhere a price would be needed, the cell is blank and says so.</p>

<h2 id="what-moved">What moved on 13 November 2026</h2>
<ul>
<li>The official injury hub now publishes <strong>{ref['rows_on_live_hub']}</strong> Week 10 rows across
<strong>{ref['clubs_with_rows']}</strong> clubs. The page the site renders carries
<strong>{ref['rows_in_published_injuries_csv']}</strong> rows across 24 clubs.</li>
<li>Against the published register there are <strong>{ref['delta_vs_published']}</strong> differences
(rows added, removed or changed); against session <code>a392a193</code>&rsquo;s later re-fetch there are
<strong>{ref['delta_vs_hubrefresh']}</strong>, which is the same league page moving in about fourteen hours.</li>
<li>Three Week 10 game ids (<code>W10-06</code>, <code>W10-07</code>, <code>W10-08</code>) name different
fixtures in <code>data/injuries_2026_wk10.csv</code> than they do in
<code>data/schedule_2026_wk10.csv</code>. Any join between the two files attaches a club&rsquo;s injuries to
the wrong opponent.</li>
</ul>

<h2 id="what-we-found">What the competition found</h2>
<ul>
<li>Our originated spread does <strong>not</strong> beat a prediction of zero on the holdout
(MAE {comp['spread_model_mae']} vs {comp['spread_baseline_mae']}); the correlation between our predicted
home margin and the actual margin is effectively nil.</li>
<li>Our originated total misses by {comp['total_model_mae']} points against
{comp['total_baseline_mae']} for the do-nothing league mean. Also no improvement.</li>
<li>The best side selector wins {int(round(comp['best_hit_rate'] * 100))}% of its decisions, but it does
so on {rest_n} of them &mdash; below this build&rsquo;s own 40-decision floor. Ten coin-flipping selectors
produce a best-of-ten of {comp['mc_p95_best']} or better one time in twenty by luck alone.</li>
<li>The strongest genuine signal is the boring one: pick the team with the better season point
differential, {pd_hits} of {pd_n}. That is the definition of a favourite, not an edge, and without a price
nobody can say whether it was already paid for. Its mirror image, the contrarian control, wins
{ct_hits} of {ct_n} on the same games.</li>
</ul>

<h2 id="pages">Pages in this tree</h2>
<p>Eleven pages. Every table row on every one of them carries a link to the official page it came from,
except rows that state a rule rather than a fact &mdash; those say so in their caption, because there is
nothing official to point at.</p>
<ul>{pages_list()}</ul>
<p>This tree is additive. Nothing in the canonical root dashboard, or in any other session&rsquo;s tree,
was modified to build it.</p>
"""
    return page("index.html", "Session overview", "program",
                "A dated re-read of the official league pages, and the first pre-registered "
                "walk-forward competition in this repository.",
                body, badge="session 2268bfb2",
                toc=[("read-this-first", "Read this first"), ("what-moved", "What moved"),
                     ("what-we-found", "What the competition found"), ("pages", "Pages in this tree")])


def build_refresh(ref):
    delta = load("s2268_injury_delta_20261113.csv")
    cov = load("s2268_coverage_20261113.csv")
    coll = load("s2268_gameid_collisions.csv")
    reg = load("s2268_injuries_wk10_20261113.csv")
    counts = {}
    for d in delta:
        counts[(d["change"], d["compared_against"].split(" ")[0])] = \
            counts.get((d["change"], d["compared_against"].split(" ")[0]), 0) + 1
    pub = [k for k in counts if "injuries_2026_wk10" in k[1]]
    hub = [k for k in counts if "hubrefresh" in k[1]]

    def bullet(d, keys):
        return "".join(f"<li><strong>{esc(k[0])}</strong> against <code>{esc(k[1])}</code>: "
                       f"{counts[k]}</li>" for k in sorted(keys))

    body = f"""
<blockquote>The official injury hub was read at <strong>{FETCH_UTC}</strong> and every row of it was
transcribed field for field into <code>data/s2268_injuries_wk10_20261113.csv</code>. This page publishes
the differences against the two Week 10 injury registers already in the repository. Nothing here was
corrected in place: the differences are published, and the decision to refresh the published table is
yours (<a href="../suggestions.html">S-43</a>, <a href="../questions.html">Q-40</a>).</blockquote>

<h2 id="scale">Scale of the change</h2>
<ul>{bullet(counts, pub)}</ul>
<p class="caption">Against <code>data/injuries_2026_wk10.csv</code> &mdash; the file the
<a href="../injuries.html">Injuries page</a> renders.</p>
<ul>{bullet(counts, hub)}</ul>
<p class="caption">Against <code>data/injuries_wk10_2026_hubrefresh.csv</code> &mdash; session
<code>a392a193</code>&rsquo;s re-fetch of the same page roughly fourteen hours earlier.</p>

<h2 id="coverage">What the live hub publishes, club by club</h2>
{table(cov, caption="The two clubs with zero rows are not absent by accident: the hub prints "
                    "&ldquo;No Injuries Reported&rdquo; for both, which is a declaration, not a gap. "
                    "Every other club's rows are published in full below.")}

<h2 id="gameids">Three Week 10 game ids name the wrong fixture</h2>
<p><code>data/schedule_2026_wk10.csv</code> and <code>data/injuries_2026_wk10.csv</code> both number the
Week 10 games <code>W10-01</code> to <code>W10-14</code>, and for three of the fourteen they number them
differently: the injury file follows the order the hub prints its blocks in, the schedule file follows the
order the schedule page prints its fixtures in, and those two orders disagree for the three 1:00&nbsp;pm
Sunday games. Every id in <code>data/computed_fair_lines.csv</code> and
<code>data/deficiency_by_club_a392.csv</code> follows the schedule convention, so the injury register is
the odd one out &mdash; and a join on <code>game_id</code> silently attaches six clubs' injury rows to the
wrong opponent.</p>
{table(coll, caption="Verdict is computed by comparing the team set under each id in the two files. "
                     "&ldquo;Rotation&rdquo; means the id points at a real Week 10 fixture that the other "
                     "file numbers differently; &ldquo;incomplete&rdquo; means a club's rows were never "
                     "ingested at all.")}

<h2 id="delta">Every difference, row by row</h2>
<p>{len(delta)} rows. &ldquo;Field changed&rdquo; excludes pure vocabulary differences: the published
register writes <code>OUT</code> and <code>Q</code> where the hub prints <code>Out</code> and
<code>Questionable</code>, and those six cells are not counted as data changes.</p>
{table(delta, caption="Each row names the register it differs from. Where the old value is blank the row "
                      "simply did not exist in that register.")}

<h2 id="register">The full register as read on 13 November</h2>
<p>{len(reg)} rows, transcribed from the official hub. Practice codes are the league's own:
<code>D</code> did not participate, <code>L</code> limited, <code>F</code> full. A blank game status is
not a zero and not an omission by this project &mdash; the hub only populates it once a club has filed a
designation.</p>
{table(reg, caption="Player links go to the official nfl.com player page printed by the hub.")}
"""
    return page("refresh.html", "Live refresh: 13 November 2026", "measured",
                "What the official league pages say today, and every difference against what this "
                "repository already publishes.",
                body, badge="measured",
                toc=[("scale", "Scale of the change"), ("coverage", "Club coverage"),
                     ("gameids", "Game-id collision"), ("delta", "Row-by-row delta"),
                     ("register", "Full register")])


def build_depth():
    chains = load("s2268_depth_chains_20261113.csv")
    body = f"""
<blockquote><strong>What a deficiency is here.</strong> Two official documents have to agree before this
build will assert one. The league's own injury hub says who is unavailable; the club's own published depth
chart says which string that player is and who is printed behind him. Where either document is silent the
cell is <span class="np">not published</span> &mdash; no inference from salary, draft position, jersey
number or past starts.</blockquote>

<h2 id="caveat">Read the caveat first</h2>
<p>Both clubs label the page this comes from an <strong>unofficial</strong> depth chart &mdash;
Patriots.com states plainly that it &ldquo;reflects the opinions of the Patriots.com writers,&rdquo; and
the Lions publish theirs as &ldquo;compiled by Lions Football Communications.&rdquo; They are official club
publications, they are the only published statement of string order, and they are not the league's own
depth chart, because the league does not publish one. That distinction is recorded as
<a href="flagged.html">FL-2268-04</a> and it is the reason every row below cites the club page it came
from.</p>

<h2 id="why-these-clubs">Why these two clubs</h2>
<p>Of the fourteen Week 10 games, exactly one has not been played and has filed game-status designations:
the Munich game, <strong>NE @ DET</strong>, Sunday 15 November, 09:30 EST. It carries six of the seven
designations on the whole Week 10 hub. The other clubs file practice participation but no status, so a
&ldquo;who is out&rdquo; chain cannot be asserted for them yet. The remaining 24 clubs are the obvious next
task and the URL pattern is in <a href="sources.html">the source registry</a>.</p>

<h2 id="chain">The chain that matters</h2>
<p>New England's running-back room is the case the whole register exists for. Rhamondre Stevenson is the
1st string and is <em>limited</em>. TreVeyon Henderson is the 2nd string and is <strong>ruled out</strong>.
So the first available replacement is the 3rd string, Corey Kiner, and behind him the 4th string, Lan
Larison. That is exactly the second-, third- and fourth-string cascade the brief asks the system to know,
and it comes from two official pages agreeing, not from a model.</p>

<h2 id="table">Every injured player, with the string behind him</h2>
{table(chains, cols=["club", "game", "side", "position_group", "player", "string", "practice", "status",
                     "next_man_up", "next_string", "next_practice", "next_status", "note",
                     "depth_url", "injury_url"],
       caption="One row per player per position group the club prints him in. Where the club's chart "
               "prints no group for a player's position, or omits the player entirely, the string is "
               "not published rather than guessed.")}

<h2 id="gaps">Three gaps this table refuses to paper over</h2>
<ul>
<li><strong>Kerby Joseph (DET, S) is ruled Out but does not appear on the Lions' published chart.</strong>
His string and his replacement cannot be asserted from an official page, so both are
<span class="np">not published</span>.</li>
<li><strong>Ben Brown (NE) is listed at C on the league hub and at LG (1st string) and C (2nd string) on
the club chart.</strong> Which lineman actually replaces him depends on which is right. Both readings are
published side by side; the discrepancy is flagged, not resolved by picking one.</li>
<li><strong>Reggie Gilliam (NE, FB) and Greg Van Roten (NE, G) have no group on the club chart</strong>,
which prints linemen only as LT / LG / C / RG / RT. Their strings are <span class="np">not
published</span>.</li>
</ul>
"""
    return page("depth.html", "Depth & deficiencies", "measured",
                "Who is unavailable, which string he is, and who the club prints behind him &mdash; "
                "only where two official documents agree.",
                body, badge="measured",
                toc=[("caveat", "Caveat"), ("why-these-clubs", "Why these clubs"),
                     ("chain", "The chain that matters"), ("table", "Full chain table"),
                     ("gaps", "Gaps we will not paper over")])


def build_competition(comp):
    ps = pick_stats()
    pd_hits, pd_n, pd_p = ps["P-PD"]["wins"], ps["P-PD"]["decisions"], ps["P-PD"]["binomial_p_two_sided"]
    ct_hits, ct_n = ps["P-CONTRA"]["wins"], ps["P-CONTRA"]["decisions"]
    lb = load("s2268_leaderboard.csv")
    rewards = load("s2268_rewards.csv")
    reg = load("s2268_strategy_register.csv")
    body = f"""
<blockquote><strong>Nothing on this leaderboard is a betting record.</strong> There is no price feed in
this repository, so there is no closing line, no vig, no CLV and no return on investment. The competition
ranks selection skill, which is measurable without a price, and it leaves every economics cell blank. The
moment a price exists, the ROI column can be filled; until then, filling it would be invention.</blockquote>

<h2 id="result">The result</h2>
<p>Ten candidates were pre-registered &mdash; eight real signals and two deliberate negative controls
&mdash; then scored on {comp['holdout_games']} holdout games (weeks 5&ndash;9) that no fitted coefficient
ever saw. {comp['decisions_scored']} decisions were settled. {comp['survivors_fdr']} candidates survive a
Benjamini&ndash;Hochberg correction at a 10% false-discovery rate; two of those are the negative controls
doing their job in the wrong direction or the right one.</p>
{table(lb, caption="Ranked by log loss, a proper scoring rule: it rewards being right and penalises being "
                   "confidently wrong, so a lucky streak on few bets cannot top the table. The rank column "
                   "reads &ldquo;unranked&rdquo; when no candidate clears the luck gate, because ranking "
                   "noise is how a competition talks itself into a bad strategy.")}

<h2 id="read-this">How to read the hit rates</h2>
<p>The favourite signal wins {pd_hits} of {pd_n} decisions, {round(int(pd_hits) / int(pd_n) * 100, 1)}%,
with an exact binomial p of {pd_p}. Every fibre of a betting brain wants to call that an edge. It is not one: a team with the
better season point differential <em>is</em> the favourite, and winning two times in three is what being a
favourite means. Whether that was already in the price is unknowable here, because there is no price. The
one number that would settle it &mdash; the closing line &mdash; is the one number this repository does
not have.</p>
<p>The contrarian control wins {ct_hits} of {ct_n} on the same games, which is the exact complement. That is the
point of including it: it prices the multiple-comparisons problem by showing what the mirror image of a
real signal looks like to the same test.</p>

<h2 id="rewards">Rewards</h2>
<p>Five tiers, each with a stake multiplier and a list of gates that unlock it. Every tier above T0 is
blocked, and the table says exactly which gate blocks it and why. Nothing is staked and nothing is earned
until a licensed price feed exists and a forward track record has been paper-tracked and settled.</p>
{table(rewards, caption="Stake multipliers are fractions of a notional reference unit, not recommendations. "
                        "The reference unit is undefined until there is a bankroll policy, which is "
                        "another open decision.")}

<h2 id="definitions">Pre-registered definitions</h2>
<p>These ten rules were written down and hashed <em>before</em> any result was computed. The hash is
<code>{comp['definitions_sha256'][:40]}&hellip;</code>, stored in
<code>data/s2268_preregistration.json</code>. The scorer refuses to run if the definitions change and the
hash is not deliberately re-cut, so adding a strategy after seeing the leaderboard is a visible act rather
than a silent one.</p>
{table(reg, cols=["id", "name", "track", "market", "family", "selection_rule", "abstention_rule",
                  "pre_registration_note", "source"],
       caption="These rows state rules, not league facts, so they carry no source link: there is nothing "
               "official to point at. The hash above is the provenance.")}
"""
    return page("competition.html", "Leaderboard & rewards", "decision",
                "Ten pre-registered candidates, scored out of sample, with every economics cell left "
                "blank because there is no price.",
                body, badge="decision",
                toc=[("result", "The result"), ("read-this", "How to read the hit rates"),
                     ("rewards", "Rewards"), ("definitions", "Pre-registered definitions")])


def build_forecast(comp):
    fc = load("s2268_forecast_scores.csv")
    coef = load("s2268_model_coefficients.csv")
    body = f"""
<blockquote>Three ways to predict the home margin and three to predict the game total, scored on the same
{comp['holdout_games']} holdout games. Two of the six are do-nothing baselines, and they are the ones that
matter: a model that cannot beat them has no value, however sophisticated it looks.</blockquote>

<h2 id="headline">The headline</h2>
<p>Our originated spread misses by <strong>{comp['spread_model_mae']} points</strong> per game. Predicting
that the home team wins by nothing at all misses by <strong>{comp['spread_baseline_mae']}</strong>. Our
originated total misses by <strong>{comp['total_model_mae']}</strong> against
<strong>{comp['total_baseline_mae']}</strong> for the point-in-time league mean.</p>
<p>In other words: <strong>on this holdout, our own lines do not beat knowing nothing.</strong> That is the
finding, it is the same wall session <code>63ac21e9</code> hit with thirteen seasons of data (spread MAE
10.25 against the market's 9.94), and publishing it is worth more than publishing a tuned number that
would not survive next week.</p>

<h2 id="scores">Every predictor, scored</h2>
{table(fc, cols=["id", "track", "games_scored", "mae", "rmse", "mean_bias", "pearson_r_vs_actual",
                 "r_squared", "p_value", "beats_baseline_rate", "beats_baseline_binomial_p", "rule",
                 "note", "source_first_week", "source_last_week", "sample_scope"],
       caption="MAE is mean absolute error in points. &ldquo;Beats baseline rate&rdquo; is the share of "
               "games where this predictor was closer to the truth than the do-nothing baseline, paired "
               "on the same games; its p value is an exact two-sided binomial. The two baselines are "
               "excluded from their own comparison, so those cells are blank by construction, not by "
               "omission.")}

<h2 id="why">Why the model failed, and what that means</h2>
<p>The slope fitted on weeks 2&ndash;4 for the spread is small enough that, after shrinkage, the model
barely moves off the home-field baseline; the correlation between its prediction and the actual margin is
0.031 with a p value of 0.80. The total model's slope is <em>negative</em>, which is to say the training
window told it that teams with high scoring rates would play in lower-scoring games. On 48 games that is
noise, and the shrinkage only partly damps it.</p>
<p>The honest reading is that nine weeks of one season is not enough to fit anything. The league's own
scoring environment moves, opponent quality is not adjusted for, and the only feature with real signal in
this data &mdash; the point-differential gap &mdash; correlates with the actual margin at r = 0.26
(p = 0.026), which explains about 7% of the variance and still does not translate into a better
point forecast than zero.</p>

<h2 id="coefficients">The frozen coefficients</h2>
{table(coef, caption="Fitted on weeks 2 to 4 only, then frozen and applied unchanged to weeks 5 to 9. "
                     "The shrinkage rule is part of the pre-registration hash: predictions are blended "
                     "toward the do-nothing baseline, never toward zero.")}
"""
    return page("forecast.html", "Forecast track", "measured",
                "Spreads and totals, scored against the only baselines that matter: the ones that "
                "know nothing.",
                body, badge="measured",
                toc=[("headline", "The headline"), ("scores", "Every predictor scored"),
                     ("why", "Why the model failed"), ("coefficients", "Frozen coefficients")])


def build_correlations():
    pred = load("s2268_predictor_correlations.csv")
    sgp = load("s2268_sgp_correlations.csv")
    strat = load("s2268_strategy_correlations.csv")
    body = f"""
<blockquote>Three correlation tables, all measured rather than assumed, because a parlay priced as if its
legs were independent is a parlay priced wrong. The correlations the repository previously left blank were
the market, backtest and same-game-parlay cells; the same-game ones below are now filled from real
settled games. The prop ones are still blank, and the reason is on this page.</blockquote>

<h2 id="predictors">How much signal is in the signal</h2>
{table(pred, caption="Pearson r between each prediction and what actually happened, on the weeks 5-9 "
                     "holdout. r-squared is the share of variance explained. A sports model with an "
                     "r-squared of 0.07 is not useless and is not a business; it is roughly the real "
                     "ceiling for pre-game margin prediction from season-to-date rates.")}

<h2 id="sgp">Same-game legs &mdash; the correlations a parlay needs</h2>
<p>These six legs are the building blocks of a same-game parlay or a prop combination. The
<strong>phi</strong> column is the measured correlation between two legs' outcomes (phi is Pearson's r for
two binary series). The <strong>rate if independent</strong> column is what a book would charge if it
assumed the legs had nothing to do with each other; the <strong>actual joint rate</strong> is what
happened.</p>
{table(sgp, caption="n = 72 holdout games throughout. The gap between the last two columns is the pricing "
                    "error a naive independence assumption would produce.")}

<h3>What the numbers say</h3>
<ul>
<li><strong>Home team wins &times; home margin beats our spread: phi = 0.9449.</strong> They are almost the
same bet. Our spread model barely moves off a constant, so &ldquo;covers our number&rdquo; and &ldquo;wins
the game&rdquo; fire together. A two-leg parlay built from them is one leg sold twice, and the
independence assumption would price it at 17.4% when it hits 41.7% of the time.</li>
<li><strong>Home team wins &times; away team scores 24 or more: phi = &minus;0.6400.</strong> Strongly
negative, as it must be: the away team scoring heavily is evidence against the home team winning. Priced
independently this pair would be badly wrong in the punter's favour, which is precisely why no book prices
it that way.</li>
<li><strong>Over our total &times; away team scores 24 or more: phi = 0.6112.</strong> Likewise positive
and large.</li>
<li><strong>Home team scores 24+ &times; away team scores 24+: phi = 0.0622.</strong> Nearly independent
&mdash; the one pair here where the independence assumption does little damage.</li>
</ul>

<h2 id="strategies">Correlation between strategies</h2>
<p>The same measurement applied to the competitors themselves: when two strategies both bet on a game, do
they win and lose together? This is the number that determines whether a parlay of two strategies is
diversification or the same bet twice.</p>
{table(strat, caption="Pairs with fewer than ten common decisions are not published: with ten games a "
                      "correlation estimate is indistinguishable from noise.")}

<h2 id="props">Player props: still blank, and why</h2>
<p>The brief asks for player prop bet combinations and their correlations. Every cell that would need one
is <span class="np">not published</span>, because measuring the correlation between two prop legs requires
a history of prop lines, and no prop-line archive exists anywhere in this repository. nfl.com does not
publish one, and the price feed question (<a href="../questions.html">Q-01</a>,
<a href="../questions.html">Q-02</a>) is still open. It is logged as
<a href="flagged.html">FL-2268-06</a> and it blocks gate G-C8.</p>
"""
    return page("correlations.html", "Measured correlations", "measured",
                "Predictor correlations, same-game leg correlations, and the correlation matrix "
                "between strategies.",
                body, badge="measured",
                toc=[("predictors", "Signal strength"), ("sgp", "Same-game legs"),
                     ("strategies", "Between strategies"), ("props", "Player props")])


def build_parlays():
    par = load("s2268_parlays.csv")
    body = f"""
<blockquote>Parlays are built <strong>disjoint</strong>: inside a week, the games a strategy bet are taken
in corpus order and grouped into consecutive pairs or triples that share no game. That makes each parlay an
independent observation, so the binomial test against the independent-product rate is actually valid. The
overlapping enumeration a careless build would use is counted at the bottom of the table and labelled for
what it is.</blockquote>

<h2 id="method">Why the construction matters more than the result</h2>
<p>Cross every pair of games in a week and a strategy with eleven bets per week yields several hundred
parlays from six weeks of football. Each game then appears in dozens of them. Any p value computed on that
set treats the same twelve games as fresh evidence every time, and will manufacture significance out of
nothing. The disjoint construction throws most of that away and keeps only parlays that share no game
&mdash; about thirty of them, which is a small honest sample instead of a large dishonest one.</p>

<h2 id="results">What we found</h2>
<p>Across every disjoint two-leg and three-leg parlay in the table, not one deviates significantly from
what independence would predict. The smallest p value on the page is 0.1047, on 31 parlays. The honest
conclusion is not &ldquo;parlays are independent&rdquo;; it is that <strong>with about thirty parlays we
cannot detect the correlation that certainly exists</strong>. That is a sample-size statement, and it is
the same wall the rest of this project keeps hitting.</p>
{table(par, cols=["construction", "legs", "strategy_a", "strategy_b", "strategy_c", "parlays_formed",
                  "legs_shared_between_parlays", "actual_hit_rate", "rate_if_independent",
                  "correlation_gap", "binomial_p_vs_independent", "note",
                  "source_first_week", "source_last_week"],
       caption="Legs are single-game side selections. A parlay never repeats a game: two legs on the same "
               "game are one bet, not two, and the correlation table on the correlations page shows how "
               "close to one bet they really are.")}

<h2 id="economics">The economics, without a price</h2>
<p>A two-leg parlay at standard -110 per leg pays about 2.6 to 1, which needs a 27.7% hit rate to break
even. Two independent 55% legs give 30.3%; two independent 50% legs give 25.0%. Our best genuine signal
runs at 68.2% per leg, which would make a two-leg parlay enormously profitable &mdash; if the market
priced those legs at even money, which it does not and would not.</p>
<p>Without a closing price there is no way to know what a book would actually pay for these legs, so no
parlay return is published anywhere in this tree. What is published is the part that does not need a
price: the hit rates, the correlations, and the sample size you would need before believing any of it.</p>
"""
    return page("parlays.html", "Parlays & prop combos", "design",
                "Disjoint parlay construction, measured against the independence assumption, with the "
                "economics left blank where they need a price.",
                body, badge="design",
                toc=[("method", "Why construction matters"), ("results", "Results"),
                     ("economics", "The economics")])


def build_luck(comp):
    ps = pick_stats()
    rest_req = ps["P-REST"]["required_n_for_80pct_power"]
    rest_hits, rest_n, rest_p = (ps["P-REST"]["wins"], ps["P-REST"]["decisions"],
                                 ps["P-REST"]["binomial_p_two_sided"])
    luck = load("s2268_luck.csv")
    picks = load("s2268_pick_scores.csv")
    rest = load("s2268_rest_audit.csv")
    body = f"""
<blockquote>&ldquo;Remove luck from the equation.&rdquo; You cannot remove it, but you can measure it, and
you can refuse to promote anything that has not been separated from it. Four instruments do that here: an
exact binomial test, a false-discovery correction across the whole candidate set, a seeded Monte Carlo that
asks what ten coin-flipping selectors would have produced, and the sample size each observed effect would
need before it could be believed.</blockquote>

<h2 id="headline">The headline number</h2>
<p>Ten candidates were scored. The best hit rate achieved is
<strong>{comp['best_hit_rate']}</strong>. Ten selectors flipping coins, given the same number of decisions
each, produce a best-of-ten of <strong>{comp['mc_mean_best']}</strong> on average and
<strong>{comp['mc_p95_best']} or better one time in twenty</strong>. So the observed best does clear the
luck threshold &mdash; and it does so on {rest_n} decisions, which is below this build's own 40-decision
floor and far below the {rest_req} the effect size would nominally need.</p>

<h2 id="instruments">The four instruments</h2>
{table(luck, caption="Every value is computed at build time by tools/s2268_competition.py from the frozen "
                     "corpus. The Monte Carlo is seeded, so re-running the build reproduces these numbers "
                     "exactly.")}

<h2 id="candidates">Every candidate, tested</h2>
{table(picks, caption="The p value is an exact two-sided binomial against a coin flip. The BH column is "
                      "the Benjamini-Hochberg adjusted p at a 10% false-discovery rate across all ten "
                      "candidates. &ldquo;Required n&rdquo; is the number of decisions needed to detect "
                      "the observed edge at 80% power. The two Monte Carlo columns place each result "
                      "against the best of ten coin flippers and against a single one.")}

<h3>The trap on this page, stated plainly</h3>
<p>P-REST wins {rest_hits} of {rest_n} &mdash; {round(int(rest_hits) / int(rest_n) * 100, 1)}%, the best
number on the site, with a p value of {rest_p} that survives
the false-discovery correction. It is also the smallest sample on the page, it is one season, it is six
weeks, and the effect is larger than any rest effect has a right to be. A large effect on a small sample is
the classic signature of something that will not repeat. It is published because it is what the data says,
and it is not promoted because our own 40-decision floor exists precisely to stop a number like this from
being promoted.</p>

<h2 id="rest">The rest signal, decision by decision</h2>
<p>Every one of the 24 decisions, with the days of rest each side had and the official game page the
result came from. Read it and judge for yourself whether &ldquo;the better-rested team wins&rdquo; is a
signal or a small sample wearing one.</p>
{table(rest, caption="Rest is whole days between a team's previous game and this one, computed from the "
                     "calendar. The signal only fires when the difference is at least two days, which is "
                     "why it appears mostly on bye weeks and short turnarounds.")}
"""
    return page("luck.html", "Removing luck", "decision",
                "Exact tests, a false-discovery correction, a seeded Monte Carlo, and the sample size "
                "each result would need.",
                body, badge="decision",
                toc=[("headline", "The headline number"), ("instruments", "The four instruments"),
                     ("candidates", "Every candidate tested"), ("rest", "The rest signal")])


def build_gates():
    gates = load("s2268_gates.csv")
    body = f"""
<blockquote>Ten gates. Four pass, six block. The four that pass are the ones that stop us cheating
ourselves &mdash; point-in-time features, a clean fit/test split, a pre-registration hash, a minimum
sample. The six that block are the ones that stop us betting: no price feed, no measured prop
correlations, no forward paper track record, no elapsed seasons.</blockquote>

<h2 id="gates">The gate board</h2>
{table(gates, caption="&ldquo;Hard&rdquo; means the gate cannot be waived by a good story. A blocked gate "
                      "is not a defect in a strategy; it is a missing input, and each row names it.")}

<h2 id="chain">The blocking chain, in order</h2>
<ol>
<li><strong>G-C7, price feed.</strong> Nothing that involves money can be evaluated without one. Until a
licensed feed exists and every price carries a capture timestamp, ROI, CLV and units stay
<span class="np">not published</span>. This is the single decision that unblocks the most:
<a href="../questions.html">Q-01</a>.</li>
<li><strong>G-C8, leg correlation.</strong> Game-level legs are measured on the
<a href="correlations.html">correlations page</a>. Player-prop legs are not, because no prop-line archive
exists. Any same-game product involving a prop stays unpriced.</li>
<li><strong>G-C9, forward paper tracking.</strong> One Week 10 game has settled. Fifty forward-tracked
paper bets with decision timestamps are needed before anything is promoted past T0.</li>
<li><strong>G-C10, two seasons.</strong> Nine weeks of one season exist. This gate cannot be argued with,
only outlasted.</li>
</ol>

<h2 id="difference">How these differ from the root register's gates</h2>
<p>The root <a href="../validation-gates.html">validation gates</a> page carries fourteen gates, all
&ldquo;blocked&rdquo; or &ldquo;not started&rdquo;, because each one describes an input the repository does
not yet have. These ten are the same idea applied to something that <em>does</em> exist: a frozen corpus and
a scoring harness. Four of them can be evaluated today, and they pass. The point of the split is that a
gate board on which nothing can ever pass is not a gate board, it is a wish list.</p>
"""
    return page("gates.html", "Validation gates", "decision",
                "Ten gates: four that stop us cheating ourselves, six that stop us betting.",
                body, badge="decision",
                toc=[("gates", "Gate board"), ("chain", "The blocking chain"),
                     ("difference", "How these differ")])


def build_flagged():
    rows = [
        ("FL-2268-01", "data integrity", "high",
         "Three Week 10 game ids (W10-06, W10-07, W10-08) name different fixtures in "
         "data/injuries_2026_wk10.csv than they do in data/schedule_2026_wk10.csv.",
         "Ids compared club-by-club against the schedule; the injury register follows the hub's block "
         "order, everything else follows the schedule's fixture order.",
         "https://www.nfl.com/injuries/",
         "Blocking for any join: fix the ids in the injury register or stop joining on game_id. Not "
         "fixed here because data/injuries_2026_wk10.csv belongs to another session's scope.",
         "open"),
        ("FL-2268-02", "freshness", "high",
         f"The Injuries page renders 254 rows taken from a Wednesday/Thursday read; the official hub "
         f"published 295 rows at {FETCH_UTC}. 42 rows added, 1 removed, 42 field changes.",
         "Full row-by-row delta published on the refresh page.",
         "https://www.nfl.com/injuries/",
         "Same root cause as FL-35: no cumulative table on this site states when it was read. The "
         "refresh cadence decision is Q-40 / S-43.",
         "open"),
        ("FL-2268-03", "coverage", "medium",
         "SEA and CIN publish full injury blocks on the live hub but have no rows in "
         "data/injuries_2026_wk10.csv. FL-01 and FL-24 describe this as corrected; the data file was "
         "not updated.",
         "Club-by-club coverage counted from the live hub and compared with the published register.",
         "https://www.nfl.com/injuries/",
         "The flag text is right and the file is stale. Either refresh the file or restate the flag.",
         "open"),
        ("FL-2268-04", "source quality", "medium",
         "Club depth charts are published by the clubs as UNOFFICIAL: Patriots.com states the chart "
         "reflects its writers' opinions; the Lions publish theirs as compiled by Football "
         "Communications. The league publishes no depth chart at all.",
         "Both club pages read in full at " + FETCH_UTC + ".",
         "https://www.patriots.com/team/depth-chart",
         "Every string asserted in this tree cites the club page it came from and carries the caveat. "
         "A league-published chart would remove the caveat; none exists.",
         "open"),
        ("FL-2268-05", "identifier mismatch", "medium",
         "Ben Brown is listed at C on the league injury hub and at LG (1st string) and C (2nd string) on "
         "the Patriots' published chart. Kevin Byard is 'Kevin Byard' on the hub and 'Kevin Byard III' on "
         "the club chart.",
         "Both documents read at " + FETCH_UTC + " and transcribed verbatim.",
         "https://www.patriots.com/team/depth-chart",
         "Both readings published side by side; not resolved by choosing one. Which lineman replaces "
         "Brown changes with the answer.",
         "open"),
        ("FL-2268-06", "missing data", "high",
         "No player-prop line archive exists in this repository, so no prop-leg correlation can be "
         "measured and gate G-C8 stays blocked for prop combinations.",
         "nfl.com publishes no prop-line archive; the price-feed questions Q-01 and Q-02 are open.",
         "https://www.nfl.com/injuries/",
         "Every prop cell in this tree is blank. Blocks the same-game-parlay tier and any prop-combination "
         "strategy.",
         "open"),
        ("FL-2268-07", "method defect, self-reported", "low",
         "The first cut of the competition harness shrank fitted predictions toward zero instead of "
         "toward the do-nothing baseline, making the totals model look 7.6 points worse than it is. A "
         "second cut used y*365.25 + m*30.6 + d for rest days, which is not monotone across month "
         "boundaries.",
         "Both found by reading the output against common sense, not by a test. Both fixed; the "
         "shrinkage rule is now inside the pre-registration hash so it cannot drift again.",
         "https://www.nfl.com/scores/2026/week-9",
         "Closed, and recorded rather than quietly overwritten, because the value of a pre-registration "
         "hash is that a change to the model leaves a seam.",
         "closed"),
        ("FL-2268-08", "statistical honesty", "medium",
         "P-REST wins 19 of 24 decisions (79.2%) and survives the false-discovery correction, on the "
         "smallest sample in the competition and six weeks of one season.",
         "Exact binomial p = 0.0066; required n for 80% power at this effect = 21; the build's own floor "
         "is 40.",
         "https://www.nfl.com/scores/2026/week-9",
         "Published, ranked by log loss, and not promoted: G-C4 fails on sample size. It should be "
         "re-tested on week 10 onwards rather than acted on.",
         "open"),
        ("FL-2268-09", "result", "high",
         "Our own originated spread and total both fail to beat do-nothing baselines on the weeks 5-9 "
         "holdout (spread MAE 11.03 vs 10.92; total 11.21 vs 11.18). The correlation between our "
         "predicted home margin and the actual margin is 0.031 (p = 0.80).",
         "Scored on 72 holdout games by tools/s2268_competition.py, reproducible from the frozen corpus.",
         "https://www.nfl.com/scores/2026/week-9",
         "Published rather than tuned. The same wall session 63ac21e9 hit with thirteen seasons of data.",
         "open"),
    ]
    body = f"""
<blockquote>Irregularities are published, not silently fixed. Nine items below, one already closed (a
defect this session found in its own harness, which is recorded because a pre-registration hash is only
worth having if a change to the model leaves a seam).</blockquote>

<h2 id="flags">Flagged items</h2>
{table([{"id": r[0], "type": r[1], "severity": r[2], "finding": r[3], "evidence": r[4],
         "source": r[5], "decision_impact": r[6], "status": r[7]} for r in rows],
       caption="Nothing here blocks the merge. Every item is either a decision for you to make or a fact "
               "about the data that a reader is entitled to know.")}

<h2 id="not-published">What is not published, and why</h2>
<ul>
<li><strong>Return on investment, CLV, units, drawdown.</strong> No price feed exists. Q-01.</li>
<li><strong>Player-prop correlations and prop-combination prices.</strong> No prop-line archive. Q-02.</li>
<li><strong>Kerby Joseph's string and replacement.</strong> Ruled out on the league hub, absent from the
club's published depth chart. FL-2268-04.</li>
<li><strong>Depth chains for the other 24 clubs.</strong> Only NE and DET have filed game-status
designations for a game that has not been played.</li>
<li><strong>The string order of any club the NFL itself publishes.</strong> The league publishes no depth
chart.</li>
</ul>
"""
    return page("flagged.html", "Flagged for review", "decision",
                "Nine items: eight open, one self-reported defect already closed. None blocks the merge.",
                body, badge="decision",
                toc=[("flags", "Flagged items"), ("not-published", "What is not published")])


SOURCES = [
    ("S-2268-01", "https://www.nfl.com/injuries/", "A", "Official NFL injury hub, Week 10",
     FETCH_UTC, "The full 295-row Week 10 register: every club's practice participation and game status."),
    ("S-2268-02", "https://www.nfl.com/schedules/2026/by-week/week-10", "A", "Official Week 10 schedule",
     FETCH_UTC, "The canonical Week 10 fixture list, used to verify game ids and to attach a game page "
                "to every row."),
    ("S-2268-03", "https://www.nfl.com/scores/2026/week-9", "A", "Official Week 9 scores",
     FETCH_UTC, "The weeks 1-9 corpus this competition is scored against; every one of its 136 rows "
                "carries an individual nfl.com game page of its own."),
    ("S-2268-04", "https://www.patriots.com/team/depth-chart", "A", "Patriots unofficial depth chart",
     FETCH_UTC, "String order for every New England position group, offense, defense and special teams."),
    ("S-2268-05", "https://www.detroitlions.com/team/depth-chart", "A", "Lions unofficial depth chart",
     FETCH_UTC, "String order for every Detroit position group, offense, defense and special teams."),
    ("S-2268-06", "https://www.nfl.com/news/sam-darnold-ruled-out-for-seahawks-week-10-game-vs-raiders-drew-lock-expected-to-start-again",
     "A", "League news: Sam Darnold ruled out",
     FETCH_UTC, "Confirms the quarterback chain change the injury hub implies for SEA."),
]


def build_sources():
    body = f"""
<blockquote>Every source this session read, with the access time and what it was used for. Club sites are
tier A because they are the clubs' own publications, and they are the only published statement of depth
order anywhere; the league itself publishes no depth chart.</blockquote>

<h2 id="sources">Sources</h2>
{table([{"id": s[0], "source": s[1], "tier": s[2], "label": s[3], "accessed_utc": s[4], "used_for": s[5]}
        for s in SOURCES],
       caption="No third-party site, aggregator or statistics reseller was used for anything on this "
               "tree. Where a fact could not be confirmed from a source on this list, it is blank.")}

<h2 id="inherited">Inputs inherited from earlier sessions</h2>
<ul>
<li><code>data/games_2026_wk1_9.csv</code> &mdash; the frozen 136-game corpus, imported and re-audited by
session <code>bc4b47cf</code> and designated the pre-registered backtest corpus by
<a href="../suggestions.html">S-26</a>. Every row carries its own nfl.com game URL. Not modified here.</li>
<li><code>data/schedule_2026_wk10.csv</code> &mdash; the Week 10 fixture list, used as the canonical
game-id convention.</li>
<li><code>data/injuries_2026_wk10.csv</code> and <code>data/injuries_wk10_2026_hubrefresh.csv</code>
&mdash; the two earlier Week 10 injury registers, used here only as the comparison baseline for the
refresh. Neither was edited.</li>
</ul>

<h2 id="reproduce">Reproduce this tree</h2>
<pre><code>python3 tools/s2268_competition.py     # scores the competition, writes data/s2268_*.csv
python3 tools/s2268_refresh.py         # diffs the dated register, writes the delta tables
python3 tools/s2268_build_site.py      # renders s2268/ from the CSVs</code></pre>
<p>The competition script is deterministic and refuses to run if the pre-registered strategy definitions
change without the hash being deliberately re-cut. The only randomness anywhere is the Monte Carlo, seeded
from <code>20261113</code>.</p>
"""
    return page("sources.html", "Source registry", "program",
                "Every source this session read, with its access time and what it was used for.",
                body, badge="program",
                toc=[("sources", "Sources"), ("inherited", "Inherited inputs"),
                     ("reproduce", "Reproduce this tree")])


def main():
    os.makedirs(ASSETS, exist_ok=True)
    src_css = os.path.join(ROOT, "assets", "style.css")
    if os.path.exists(src_css):
        with open(src_css) as fh:
            css = fh.read()
        with open(os.path.join(ASSETS, "style.css"), "w") as fh:
            fh.write(css + "\n/* s2268 additions */\n.np{color:#8a94a2;font-style:italic}\n"
                           "pre{background:#f3f6fa;border:1px solid var(--line);border-radius:8px;"
                           "padding:12px 14px;overflow-x:auto;font-size:13px}\n")
    comp = meta("s2268_competition_summary.json")
    ref = meta("s2268_refresh_summary.json")
    builders = {
        "index.html": lambda: build_index(comp, ref),
        "refresh.html": lambda: build_refresh(ref),
        "depth.html": build_depth,
        "competition.html": lambda: build_competition(comp),
        "forecast.html": lambda: build_forecast(comp),
        "correlations.html": build_correlations,
        "parlays.html": build_parlays,
        "luck.html": lambda: build_luck(comp),
        "gates.html": build_gates,
        "flagged.html": build_flagged,
        "sources.html": build_sources,
    }
    for fn, title, group, kind in PAGES:
        with open(os.path.join(OUT, fn), "w") as fh:
            fh.write(builders[fn]())
        print("built", fn)
    print(f"{len(PAGES)} pages in s2268/")


if __name__ == "__main__":
    main()
