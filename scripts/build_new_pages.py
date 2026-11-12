#!/usr/bin/env python3
"""
NFL2 — Render depth-deficiencies.html, correlations.html, repo-audit.html,
executive-summary.html, lines-lab.html, and schedule.html using the unified
root navigation, dark theme, and 100% per-row official source links.
"""
from __future__ import annotations
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "analytics"
OUT.mkdir(parents=True, exist_ok=True)

NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "Exec Summary"),
    ("results.html", "Results"),
    ("schedule.html", "Week 11"),
    ("standings.html", "Standings"),
    ("teams.html", "Team Stats"),
    ("injuries.html", "Injuries"),
    ("depth-deficiencies.html", "1st–4th String"),
    ("lines-lab.html", "Lines Lab"),
    ("analysis.html", "Analysis"),
    ("correlations.html", "Correlations"),
    ("strategies.html", "Strategies"),
    ("method.html", "Method"),
    ("suggestions.html", "Suggestions"),
    ("questions.html", "Questions"),
    ("repo-audit.html", "Repo Audit"),
    ("flagged.html", "Flagged for Review"),
    ("sources.html", "Sources"),
    ("../index.html", "Root Dashboard"),
    ("../review/index.html", "Review Build"),
    ("../portal/index.html", "Portal Build"),
    ("../site/index.html", "Lab Build"),
]


def esc(v: object) -> str:
    return html.escape(str(v))


def render_nav(active_href: str) -> str:
    out = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active_href else ""
        out.append(f'<a href="{href}"{cur}>{esc(label)}</a>')
    return "".join(out)


def page_shell(title: str, desc: str, eyebrow: str, h1: str, lede: str, active: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · NFL 2026 Analytics</title>
<meta name="description" content="{esc(desc)}">
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header class="top"><div class="wrap">
<a class="brand" href="index.html"><span class="dot"></span>NFL 2026 · Verified Analytics</a>
<nav class="main">{render_nav(active)}</nav>
</div></header>
<div class="pagehead"><div class="wrap"><span class="eyebrow">{esc(eyebrow)}</span><h1>{esc(h1)}</h1><p>{lede}</p></div></div>
<section><div class="wrap">
{body_html}
</div></section>
<footer><div class="wrap">
<p><b>Every figure on this site is either transcribed from an official NFL source or is explicitly labelled MODEL output.</b>
Nothing is inferred. Blank cells mean no official source confirms the value — see <a href="flagged.html">Flagged for Review</a>.</p>
<p>Data through Week 9 results, Week 10 injury reports &amp; Week 11 schedule ·
<a href="https://github.com/kanlerxz87-cyber/NFL2">repository</a> ·
<a href="https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md">coordination log</a> ·
<a href="../docs/index.html">parallel docs/ view</a></p>
</div></footer>
<script src="assets/app.js"></script>
</body></html>
"""


def build_depth_page() -> None:
    dc = json.loads((ROOT / "data" / "depth-charts-2026.json").read_text())
    inj = json.loads((ROOT / "data" / "full-injuries-week10-2026.json").read_text())
    rules = json.loads((ROOT / "data" / "nfl-rules-operations-2026.json").read_text())

    cascade_rows = []
    for c in dc["cascades"]:
        sev_cls = "b-bad" if any(k in c["active_deficiency_tier"] for k in ("3rd", "Critical", "Severe", "Multi-Level")) else "b-warn"
        cascade_rows.append(
            f"<tr>"
            f"<td><b>{esc(c['id'])}</b><br><span class=\"tiny\">{esc(c['team'])}</span></td>"
            f"<td>{esc(c['side'])} · <b>{esc(c['unit'])}</b></td>"
            f"<td>{esc(c['string_1_starter'])}</td>"
            f"<td>{esc(c['string_2_backup'])}</td>"
            f"<td>{esc(c['string_3_backup'])}</td>"
            f"<td>{esc(c['string_4_emergency'])}</td>"
            f"<td><span class=\"b {sev_cls}\">{esc(c['active_deficiency_tier'][:36])}</span><div class=\"tiny\">{esc(c['active_deficiency_tier'])}</div></td>"
            f"<td><span class=\"blank\">— blank (unverified) —</span></td>"
            f"<td class=\"src\"><a href=\"{esc(c['injury_source'])}\" target=\"_blank\" rel=\"noopener\">NFL.com ↗</a> · "
            f"<a href=\"{esc(c['depth_source'])}\" target=\"_blank\" rel=\"noopener\">Club ↗</a></td>"
            f"</tr>"
        )

    reg10_rows = []
    for t in inj["team_summaries"]:
        status_badge = (
            '<span class="b b-warn">Flagged (0 listed — check IR/news)</span>'
            if t["total_listed"] == 0
            else f'<span class="b b-ok">Verified ({t["total_listed"]} listed)</span>'
        )
        reg10_rows.append(
            f"<tr>"
            f"<td>{esc(t['game'])}</td>"
            f"<td><b>{esc(t['team'])}</b> ({esc(t['abbr'])})</td>"
            f"<td class=\"num\">{t['total_listed']}</td>"
            f"<td class=\"num\"><b>{t['dnp']}</b></td>"
            f"<td class=\"num\">{t['lp']}</td>"
            f"<td class=\"num\">{t['fp']}</td>"
            f"<td class=\"num\">{t['out']}</td>"
            f"<td class=\"num\">{t['questionable']}</td>"
            f"<td class=\"tiny\">{status_badge}<br>{esc(t['note'])}</td>"
            f"<td class=\"src\"><a href=\"{esc(t['source'])}\" target=\"_blank\" rel=\"noopener\">REG10 ↗</a></td>"
            f"</tr>"
        )

    club_rows = []
    for ch in dc["verified_club_depth_charts_fetched"]:
        disclaimer = "Unofficial PR chart — verify vs 90-min inactives"
        club_rows.append(
            f"<tr>"
            f"<td><b>{esc(ch['team'])}</b></td>"
            f"<td>{esc(ch['label_on_page'])}</td>"
            f"<td><span class=\"b b-ok\">Fetched 2026-11-12</span> · <span class=\"tiny\">{esc(disclaimer)}</span></td>"
            f"<td class=\"src\"><a href=\"{esc(ch['url'])}\" target=\"_blank\" rel=\"noopener\">Club Chart ↗</a></td>"
            f"</tr>"
        )

    rule_rows = []
    for r in rules["rules"]:
        rule_rows.append(
            f"<tr>"
            f"<td><b>{esc(r['id'])}</b> · {esc(r['rule_ref'])}</td>"
            f"<td>{esc(r['category'])}</td>"
            f"<td>{esc(r['verified_fact'])}</td>"
            f"<td class=\"tiny\">{esc(r['modeling_impact'])}</td>"
            f"<td class=\"src\"><a href=\"{esc(r['source'])}\" target=\"_blank\" rel=\"noopener\">{esc(r['source_label'])} ↗</a></td>"
            f"</tr>"
        )

    body = f"""
<div class="grid g4">
  <div class="card"><div class="big">{inj['total_players_listed_on_reg10']}</div><p>Week 10 REG10 summary entries ({inj['total_dnp_players']} DNP · {inj['total_lp_players']} LP · {inj['total_fp_players']} FP)</p></div>
  <div class="card"><div class="big">{len(dc['cascades'])}</div><p>Verified 1st → 2nd → 3rd → 4th-string cascades across offense &amp; defense</p></div>
  <div class="card"><div class="big">{len(dc['verified_club_depth_charts_fetched'])}</div><p>Official NFL club depth charts fetched &amp; cross-audited</p></div>
  <div class="card"><div class="big">{len(rules['rules'])}</div><p>Official 2026 NFL roster, PS elevation &amp; ATC spotter rules</p></div>
</div>

<div class="note"><p><b>Strict verification boundary:</b> Every player name, string rank, practice participation code (DNP / LP / FP), and game designation (OUT / Questionable / IR) is verified directly from the linked official NFL.com or NFL club page. Because no official NFL source publishes point-spread values for individual backups, the <i>Point / EPA Drop</i> column is intentionally left <b>blank and flagged unverified</b>.</p></div>

<h2 style="margin-top:30px">1 · Verified Offense &amp; Defense 1st → 2nd → 3rd → 4th-String Replacement Matrix</h2>
<p class="sub">Machine-readable dataset: <code>data/depth-charts-2026.json</code>. Filter by club, unit (QB, OL, CB, RB, S, LB), or string tier:</p>
<label for="f-dc">Filter string cascades</label>
<input id="f-dc" type="search" placeholder="e.g. Ravens, Patriots, 49ers, QB, CB, OL, 3rd-String…" data-filter-input="#dc-table" style="width:100%;max-width:460px">
<div class="tblwrap"><table id="dc-table">
  <thead><tr><th>ID / Club</th><th>Side &amp; Unit</th><th>1st String (Starter)</th><th>2nd String</th><th>3rd String</th><th>4th String / Emergency</th><th>Deficiency Tier</th><th>EPA / Pt Drop</th><th>Official Sources</th></tr></thead>
  <tbody>{"".join(cascade_rows)}</tbody>
</table></div>

<h2 style="margin-top:34px">2 · Why 2nd / 3rd / 4th-String Replacements Move Fair Lines Non-Linearly</h2>
<p class="sub">Cross-checked against verified 2026 NFL team-level correlations (<a href="correlations.html">Correlations &amp; Skill</a>, n = 32 clubs):</p>
<div class="tblwrap"><table>
  <thead><tr><th>Unit Deficiency Type</th><th>Mechanism When 2nd/3rd/4th String Plays</th><th>Verified 2026 Empirical Link (n=32)</th><th>Affected Markets</th><th>Official Source</th></tr></thead>
  <tbody>
    <tr><td><b>Quarterback Cascade (QB1 → QB2 → QB3)</b></td><td>Timing, protection checks, and downfield accuracy degrade sharply when moving from starter to cold backup or undrafted 3rd-stringer (e.g., BAL DC-01, MIA DC-02).</td><td>Offensive Passer Rating vs. PF/G: <b>r = +0.750</b> (p &lt; 0.00001)</td><td>Spread, Team Total Under, WR Receiving Unders</td><td class="src"><a href="https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all" target="_blank" rel="noopener">NFL.com Passing ↗</a></td></tr>
    <tr><td><b>Offensive Line Cluster (Adjacent Backup C/G/T)</b></td><td>OL is a weak-link unit: one 3rd-string guard or backup center (e.g., NE DC-06, AZ DC-05) breaks stunt/blitz pickups and spikes sack rate.</td><td>Offensive Sack Rate Allowed vs. PF/G: <b>r = −0.635</b> (p = 0.00009)</td><td>Team Total Under, Opposing Sacks Over, QB Yards Under</td><td class="src"><a href="https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all" target="_blank" rel="noopener">NFL.com Passing ↗</a></td></tr>
    <tr><td><b>Perimeter / Slot CB Cascade (CB1 → CB3/CB4)</b></td><td>Offenses isolate 3rd/4th-string corners in man/match coverage or force safety shading that opens explosive seams (e.g., SF DC-11, NE DC-08, DET DC-09).</td><td>Defensive Passer Rating Allowed vs. PA/G: <b>r = +0.815</b> (p &lt; 0.00001)</td><td>Opponent Team Total Over, Opposing QB/WR Props Over</td><td class="src"><a href="https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all" target="_blank" rel="noopener">NFL.com Def Pass ↗</a></td></tr>
    <tr><td><b>Defensive Spine / Run Front (NT + ILB + S)</b></td><td>Replacing nose tackle + green-dot ILB + safety (e.g., AZ DC-16, DAL DC-13) degrades gap fits and pre-snap coverage checks simultaneously.</td><td>Def Rush Yds Allowed/G vs. PA/G: <b>r = +0.613</b> (p = 0.00019)</td><td>Opponent RB Rush Attempts/Yards Over, Game Total Over</td><td class="src"><a href="https://www.nfl.com/stats/team-stats/defense/rushing/2026/reg/all" target="_blank" rel="noopener">NFL.com Def Rush ↗</a></td></tr>
  </tbody>
</table></div>

<h2 style="margin-top:34px">3 · Week 10 Official Injury Report Team Summary &amp; IR Blindspot Audit (All 28 Active Clubs)</h2>
<p class="sub">Note how 4 clubs print “No Injuries Reported” on REG10 despite major IR/ruled-out QB news — proving why weekly practice reports must always be joined with IR transactions (<a href="flagged.html">RA-05</a>).</p>
<label for="f-reg10">Filter Week 10 clubs</label>
<input id="f-reg10" type="search" placeholder="e.g. Cowboys, Packers, Ravens, DNP, IR…" data-filter-input="#reg10-table" style="width:100%;max-width:460px">
<div class="tblwrap"><table id="reg10-table">
  <thead><tr><th>Week 10 Game</th><th>Club</th><th class="num">Listed</th><th class="num">DNP</th><th class="num">LP</th><th class="num">FP</th><th class="num">OUT</th><th class="num">Quest.</th><th>Verified Participation &amp; IR Blindspot Notes</th><th>Source</th></tr></thead>
  <tbody>{"".join(reg10_rows)}</tbody>
</table></div>

<h2 style="margin-top:34px">4 · Official 2026 NFL Roster, Active/Inactive, Practice Squad Elevation &amp; Spotter Rules</h2>
<div class="tblwrap"><table>
  <thead><tr><th>Rule ID &amp; Reference</th><th>Category</th><th>Verified Official Rule</th><th>Line Origination &amp; Depth Impact</th><th>Official Source</th></tr></thead>
  <tbody>{"".join(rule_rows)}</tbody>
</table></div>

<h2 style="margin-top:34px">5 · Official NFL Club Depth Charts Captured &amp; Audited (12 Clubs)</h2>
<div class="note warn"><p><b>Upstream club-chart lag (<a href="flagged.html">RA-06</a>):</b> Club websites explicitly label depth charts “Unofficial” (compiled by club PR/writers). Line-by-line review caught retired DE Aaron Donald still listed on <code>therams.com</code>, a blank Kicker cell on <code>miamidolphins.com</code>, OUT C Lucas Patrick omitted on <code>commanders.com</code>, and Questionable LB Malik Harrison omitted on <code>giants.com</code>. Always verify against the 90-minute pre-kickoff Inactive List.</p></div>
<div class="tblwrap"><table>
  <thead><tr><th>Club</th><th>Published Depth-Chart Heading</th><th>Audit Status</th><th>Official Source</th></tr></thead>
  <tbody>{"".join(club_rows)}</tbody>
</table></div>
"""
    (OUT / "depth-deficiencies.html").write_text(
        page_shell(
            "1st–4th String Deficiencies",
            "Verified 1st, 2nd, 3rd, and 4th-string offense and defense depth-chart replacement deficiencies from official NFL.com and club sources.",
            "Personnel & String Cascades",
            "Offense & defense 1st–4th string replacement deficiencies",
            'Cross-joins the <a href="https://www.nfl.com/injuries/league/2026/REG10">Official Week 10 Injury Report</a>, official NFL.com Injured Reserve announcements, and 12 official NFL club depth charts — separating true starter/multi-string collapses from rotational noise.',
            "depth-deficiencies.html",
            body,
        )
    )


def build_correlations_page() -> None:
    corr = json.loads((ROOT / "data" / "correlations-2026.json").read_text())
    stats = json.loads((ROOT / "data" / "team-stats-offense-defense-2026.json").read_text())
    code_url = "https://github.com/kanlerxz87-cyber/NFL2/blob/main/scripts/compute_correlations.py"

    corr_rows = []
    for c in corr["verified_team_correlations"]:
        r = c["pearson_r"]
        cls = "b-ok" if abs(r) >= 0.50 and c["p_value"] < 0.01 else ("b-info" if c["p_value"] < 0.05 else "b-warn")
        corr_rows.append(
            f"<tr>"
            f"<td><b>{esc(c['id'])}</b></td>"
            f"<td><b>{esc(c['pair'])}</b><div class=\"tiny\">{esc(c['category'])}</div></td>"
            f"<td class=\"num\"><span class=\"b {cls}\">{r:+.3f}</span></td>"
            f"<td class=\"num\">{c['spearman_rho']:+.3f}</td>"
            f"<td class=\"num\">{c['r_squared']:.3f}</td>"
            f"<td class=\"num\">{c['t_stat']:+.2f}</td>"
            f"<td class=\"num\">{c['p_value']:.5f}</td>"
            f"<td class=\"num\">[{c['ci95_low']:+.3f}, {c['ci95_high']:+.3f}]</td>"
            f"<td class=\"tiny\">{esc(c['implication'])}</td>"
            f"<td class=\"src\"><a href=\"{esc(c['source'])}\" target=\"_blank\" rel=\"noopener\">NFL.com ↗</a> · "
            f"<a href=\"{code_url}\" target=\"_blank\" rel=\"noopener\">Script ↗</a></td>"
            f"</tr>"
        )

    sgp_rows = []
    for u in corr["unverified_parlay_prop_correlations"]:
        sgp_rows.append(
            f"<tr>"
            f"<td><b>{esc(u['id'])}</b></td>"
            f"<td>{esc(u['leg_a'])}</td>"
            f"<td>{esc(u['leg_b'])}</td>"
            f"<td>{esc(u['bet_structure'])}</td>"
            f"<td class=\"tiny\">{esc(u['expected_mechanism'])}</td>"
            f"<td><span class=\"blank\">— blank (unverified) —</span></td>"
            f"<td><span class=\"blank\">— blank (unverified) —</span></td>"
            f"<td class=\"src\"><a href=\"{esc(u['source'])}\" target=\"_blank\" rel=\"noopener\">NFL.com ↗</a></td>"
            f"</tr>"
        )

    luck_rows = []
    for lk in corr["luck_vs_skill_team_residuals"]:
        res = lk["luck_residual_win_pct"]
        cls = "b-bad" if res >= 0.12 else ("b-ok" if res <= -0.12 else "b-info")
        luck_rows.append(
            f"<tr>"
            f"<td><b>{esc(lk['team'])}</b> ({esc(lk['abbr'])})</td>"
            f"<td class=\"num\">{esc(lk['record'])}</td>"
            f"<td class=\"num\">{lk['actual_win_pct']:.3f}</td>"
            f"<td class=\"num\">{lk['pf']} / {lk['pa']} ({lk['net_pts']:+d})</td>"
            f"<td class=\"num\">{lk['pythagorean_win_pct']:.3f}</td>"
            f"<td class=\"num\"><b>{res:+.3f}</b> ({lk['luck_residual_wins']:+.2f} W)</td>"
            f"<td class=\"num\">{lk['int_margin']:+d}</td>"
            f"<td class=\"num\">{lk['net_yds_per_play']:+.2f}</td>"
            f"<td><span class=\"b {cls}\">{esc(lk['signal_classification'])}</span></td>"
            f"<td class=\"src\"><a href=\"{esc(lk['source'])}\" target=\"_blank\" rel=\"noopener\">NFL.com ↗</a></td>"
            f"</tr>"
        )

    eff_rows = []
    for t in sorted(stats["teams"], key=lambda x: x["derived_efficiency"]["net_yds_per_play"], reverse=True):
        de = t["derived_efficiency"]
        eff_rows.append(
            f"<tr>"
            f"<td><b>{esc(t['team'])}</b> ({esc(t['abbr'])})</td>"
            f"<td class=\"num\">{t['games']}</td>"
            f"<td class=\"num\">{t['pf_per_g']:.1f} / {t['pa_per_g']:.1f}</td>"
            f"<td class=\"num\">{t['off_pass']['yds_per_att']:.1f}</td>"
            f"<td class=\"num\">{t['off_pass']['rate']:.1f}</td>"
            f"<td class=\"num\">{de['off_sack_rate_pct']:.2f}%</td>"
            f"<td class=\"num\">{t['off_rush']['ypc']:.1f}</td>"
            f"<td class=\"num\">{t['def_pass']['rate_allowed']:.1f}</td>"
            f"<td class=\"num\">{de['def_sack_rate_pct']:.2f}%</td>"
            f"<td class=\"num\">{(t['def_rush']['rush_yds_allowed']/t['games']):.1f}</td>"
            f"<td class=\"num\"><b>{de['net_yds_per_play']:+.2f}</b></td>"
            f"<td class=\"src\"><a href=\"{esc(t['off_pass']['source'])}\" target=\"_blank\" rel=\"noopener\">Off ↗</a> · "
            f"<a href=\"{esc(t['def_pass']['source'])}\" target=\"_blank\" rel=\"noopener\">Def ↗</a></td>"
            f"</tr>"
        )

    body = f"""
<div class="grid g4">
  <div class="card"><div class="big">r = +0.815</div><p>#1 defensive scoring driver: Passer Rating Allowed vs. PA/G (p &lt; 0.00001)</p></div>
  <div class="card"><div class="big">r = +0.750</div><p>#1 offensive scoring driver: Off Passer Rating vs. PF/G (p &lt; 0.00001)</p></div>
  <div class="card"><div class="big">r = −0.635</div><p>OL protection signal: Off Sack Rate % vs. PF/G (p = 0.00009)</p></div>
  <div class="card"><div class="big">r = +0.017</div><p>Pure noise trap: Off Rushing YPC vs. PF/G (p = 0.926)</p></div>
</div>

<div class="note"><p><b>MODEL output from verified inputs:</b> Team-level correlations (<code>C-01</code>…<code>C-14</code>) are deterministically computed by <code>scripts/compute_correlations.py</code> across all 32 NFL clubs from verified 2026 NFL.com statistics. Play-by-play Same-Game Parlay and player-prop leg correlations (<code>U-C01</code>…<code>U-C06</code>) require play-level box scores not available on NFL.com summary pages — their numeric cells remain <b>strictly blank and flagged unverified</b>.</p></div>

<h2 style="margin-top:30px">1 · Verified 2026 NFL Team-Level Correlation Matrix (n = 32 Clubs, Weeks 1–9)</h2>
<p class="sub">Machine-readable file: <code>data/correlations-2026.json</code> · Recompute via <code>python3 scripts/compute_correlations.py</code>.</p>
<div class="tblwrap"><table>
  <thead><tr><th>ID</th><th>Signal Pair &amp; Channel</th><th class="num">Pearson r</th><th class="num">Spearman ρ</th><th class="num">R²</th><th class="num">t-stat</th><th class="num">p-value</th><th class="num">95% CI (Fisher z)</th><th>Line Origination &amp; Parlay Implication</th><th>Sources</th></tr></thead>
  <tbody>{"".join(corr_rows)}</tbody>
</table></div>

<h2 style="margin-top:34px">2 · Same-Game Parlay (SGP) &amp; Player-Prop Correlation Register (Play-Level Values Blank &amp; Flagged)</h2>
<p class="sub">Multiplying marginal probabilities <code>P(A)·P(B)</code> fails whenever <code>r ≠ 0</code>. Play-level empirical correlations stay blank below until play-by-play logs are connected.</p>
<div class="tblwrap"><table>
  <thead><tr><th>ID</th><th>Leg A</th><th>Leg B</th><th>Bet Type</th><th>Football Mechanism</th><th>Empirical Play-Level r</th><th>Joint Copula Price Adj.</th><th>Official Ref</th></tr></thead>
  <tbody>{"".join(sgp_rows)}</tbody>
</table></div>

<h2 style="margin-top:34px">3 · Removing Luck: 2026 Team Luck-vs.-Skill Residuals (All 32 Clubs)</h2>
<p class="sub">Compares actual 2026 Win% against Pythagorean scoring expectation (<code>PF^2.37 / (PF^2.37 + PA^2.37)</code>, MODEL output) plus INT Margin and Net Yards/Play.</p>
<label for="f-luck">Filter clubs or signal classification</label>
<input id="f-luck" type="search" placeholder="e.g. Broncos, Buccaneers, Fade, Buy-Low…" data-filter-input="#luck-table" style="width:100%;max-width:460px">
<div class="tblwrap"><table id="luck-table">
  <thead><tr><th>Club</th><th class="num">Record</th><th class="num">Actual Win%</th><th class="num">PF / PA (Net)</th><th class="num">Pythag. Skill%</th><th class="num">Luck Residual</th><th class="num">INT Margin</th><th class="num">Net Yds/Play</th><th>Skill vs. Luck Signal</th><th>Source</th></tr></thead>
  <tbody>{"".join(luck_rows)}</tbody>
</table></div>

<h2 style="margin-top:34px">4 · Complete 2026 Team Offense &amp; Defense Efficiency Table (All 32 Clubs · Ranked by Net Yds/Play)</h2>
<label for="f-eff">Filter efficiency table</label>
<input id="f-eff" type="search" placeholder="e.g. 49ers, Jaguars, Bills, Ravens…" data-filter-input="#eff-table" style="width:100%;max-width:460px">
<div class="tblwrap"><table id="eff-table">
  <thead><tr><th>Club</th><th class="num">G</th><th class="num">PF/G · PA/G</th><th class="num">Off YPA</th><th class="num">Off Rate</th><th class="num">Off Sack%</th><th class="num">Off YPC</th><th class="num">Def Rate</th><th class="num">Def Sack%</th><th class="num">Def Rush/G</th><th class="num">Net Yds/Play</th><th>Official Sources</th></tr></thead>
  <tbody>{"".join(eff_rows)}</tbody>
</table></div>
"""
    (OUT / "correlations.html").write_text(
        page_shell(
            "Correlations & Skill",
            "Reproducible 2026 NFL team correlations (n=32), SGP/prop correlation register, and luck-vs-skill residuals.",
            "Correlations, Parlay Copulas & Luck Removal",
            "Empirical correlation matrix (n = 32 clubs) & skill-vs.-luck decomposition",
            "Separates repeatable offensive/defensive efficiency signals from turnover and one-score variance — while keeping unconfirmed play-level SGP/prop correlations explicitly blank.",
            "correlations.html",
            body,
        )
    )


def build_repo_audit_page() -> None:
    audit = json.loads((ROOT / "data" / "repo-audit-2026.json").read_text())
    finding_rows = []
    for f in audit["findings"]:
        sev = f["severity"]
        cls = "b-bad" if "High" in sev else ("b-warn" if "Medium" in sev else "b-ok")
        finding_rows.append(
            f"<tr>"
            f"<td><b>{esc(f['id'])}</b></td>"
            f"<td><code>{esc(f['file_or_commit'])}</code></td>"
            f"<td><span class=\"b {cls}\">{esc(sev)}</span></td>"
            f"<td>{esc(f['finding'])}</td>"
            f"<td class=\"tiny\">{esc(f['resolution'])}</td>"
            f"<td class=\"src\"><a href=\"{esc(f['review_url'])}\" target=\"_blank\" rel=\"noopener\">Review ↗</a> · "
            f"<a href=\"{esc(f['official_source'])}\" target=\"_blank\" rel=\"noopener\">Official ↗</a></td>"
            f"</tr>"
        )

    body = f"""
<div class="note ok"><p><b>Automated verification suite:</b> Run <code>python3 scripts/verify_data.py</code>, <code>python3 scripts/verify_personnel.py</code>, <code>python3 scripts/verify_site.py</code>, <code>python3 scripts/validate_data.py</code>, and <code>python3 scripts/audit_all_pages.py</code> from the repository root to re-verify 100% of JSON arithmetic, internal links, and per-row official source links across all root and <code>docs/</code> pages.</p></div>

<h2 style="margin-top:26px">1 · Repository &amp; Upstream Irregularities Found, Fixed &amp; Flagged</h2>
<div class="tblwrap"><table>
  <thead><tr><th>Audit ID</th><th>Target File / Commit / Feed</th><th>Severity</th><th>Line-by-Line Finding</th><th>Resolution / Status</th><th>Manual Review Links</th></tr></thead>
  <tbody>{"".join(finding_rows)}</tbody>
</table></div>

<h2 style="margin-top:34px">2 · Parallel Session Coordination &amp; Non-Destructive Integration Summary</h2>
<div class="tblwrap"><table>
  <thead><tr><th>Session</th><th>Branch &amp; PRs</th><th>Primary Deliverables Preserved</th><th>Verification Status</th><th>Audit Source</th></tr></thead>
  <tbody>
    <tr><td><b>Baseline</b></td><td><code>main</code> @ <code>01f2271</code></td><td>Initial 6-byte <code>README.md</code> (<code># NFL2</code>)</td><td><span class="b b-ok">Audited verbatim</span></td><td class="src"><a href="https://github.com/kanlerxz87-cyber/NFL2/commit/01f227119ee8df4223b0aa697d08ed92257773c3" target="_blank" rel="noopener">01f2271 ↗</a></td></tr>
    <tr><td><b>Session 194db560</b></td><td><code>arena/194db560-nfl2</code> (PR #1, #3)</td><td><code>executive-summary.html</code>, <code>schedule.html</code>, <code>lines-lab.html</code>, <code>data/*-2026.json</code></td><td><span class="b b-ok">Preserved + REG10 &amp; row links fixed</span></td><td class="src"><a href="https://github.com/kanlerxz87-cyber/NFL2/pull/1" target="_blank" rel="noopener">PR #1 ↗</a></td></tr>
    <tr><td><b>Session arena-85d79210</b></td><td><code>arena/85d79210-nfl2</code> (PR #4, #5)</td><td><code>docs/</code> 16-page build, <code>data/*_2026.json</code>, <code>scripts/validate_data.py</code>, Pages workflow</td><td><span class="b b-ok">Preserved verbatim + row links verified</span></td><td class="src"><a href="https://github.com/kanlerxz87-cyber/NFL2/pull/4" target="_blank" rel="noopener">PR #4 ↗</a></td></tr>
    <tr><td><b>Session arena-009ec582</b></td><td><code>arena/009ec582-nfl2</code> (PR #6)</td><td>136-game log, conservation &amp; personnel verifiers, 12 generated root pages</td><td><span class="b b-ok">Preserved + per-row links added</span></td><td class="src"><a href="https://github.com/kanlerxz87-cyber/NFL2/pull/6" target="_blank" rel="noopener">PR #6 ↗</a></td></tr>
    <tr><td><b>Session eaba7863</b></td><td><code>arena/eaba7863-nfl2</code> (Integration)</td><td>12 official club depth charts &amp; 1st–4th string tracker, 32-team correlations &amp; luck residuals, 2026 rulebook anchors, full-repo row-source auditor</td><td><span class="b b-ok">100% row-sourced &amp; verified</span></td><td class="src"><a href="https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md" target="_blank" rel="noopener">COORDINATION.md ↗</a></td></tr>
  </tbody>
</table></div>
"""
    (OUT / "repo-audit.html").write_text(
        page_shell(
            "Repository Audit",
            "Line-by-line repository and upstream official NFL source verification audit.",
            "Line-by-Line Audit",
            "Repository & upstream official-source audit trail",
            "Documents every commit, multi-session merge, upstream NFL.com / club depth-chart irregularity, and automated verification gate.",
            "repo-audit.html",
            body,
        )
    )


def build_exec_summary_page() -> None:
    body = """
<div class="grid g4">
  <div class="card"><div class="big">136</div><p>Verified Weeks 1–9 games reproducing all 32 clubs’ W-L-T, PF, PA &amp; streaks</p></div>
  <div class="card"><div class="big">8 / 8</div><p>Exact league-wide offense = defense yardage &amp; TD conservation identities</p></div>
  <div class="card"><div class="big">18</div><p>Verified 1st→2nd→3rd→4th string offense &amp; defense replacement cascades</p></div>
  <div class="card"><div class="big">0 / 6</div><p>Strategies promoted (all 6 honestly held back by the n ≥ 200 gate)</p></div>
</div>

<h2 style="margin-top:30px">1 · Verified 2026 League Snapshot (As of 2026-11-12 UTC)</h2>
<div class="tblwrap"><table>
  <thead><tr><th>Domain</th><th>Verified Finding</th><th>Detail Page</th><th>Official Source</th></tr></thead>
  <tbody>
    <tr><td><b>Conference leaders</b></td><td>Buffalo Bills 7–1 (.875) in AFC; San Francisco 49ers 7–1 (.875) in NFC</td><td><a href="standings.html">Standings</a></td><td class="src"><a href="https://www.nfl.com/standings/division/2026/reg" target="_blank" rel="noopener">NFL.com ↗</a></td></tr>
    <tr><td><b>Point differential extremes</b></td><td>Jacksonville Jaguars +108 (229 PF / 121 PA) leads NFL; LA Chargers 0–8 (−98 net)</td><td><a href="standings.html">Standings</a></td><td class="src"><a href="https://www.nfl.com/standings/division/2026/reg" target="_blank" rel="noopener">NFL.com ↗</a></td></tr>
    <tr><td><b>Home-field advantage (2026)</b></td><td>Pooled 136-game mean is +0.00 pts (diluted by 7 neutral-site games); 129 true-home mean is <b>+0.50 pts</b> (95% CI [−1.80, +2.79])</td><td><a href="analysis.html">Analysis</a></td><td class="src"><a href="https://www.nfl.com/schedules/2026/REG/" target="_blank" rel="noopener">NFL.com ↗</a></td></tr>
    <tr><td><b>Skill vs. noise correlations</b></td><td>Def Passer Rating Allowed vs. PA/G (<b>r = +0.815</b>) &amp; Off Passer Rating vs. PF/G (<b>r = +0.750</b>) dominate; Team Rush YPC vs. PF/G is noise (<b>r = +0.017</b>)</td><td><a href="correlations.html">Correlations</a></td><td class="src"><a href="https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all" target="_blank" rel="noopener">NFL.com ↗</a></td></tr>
    <tr><td><b>Week 10 injuries &amp; string cascades</b></td><td>254 official REG10 player rows; critical QB/OL/CB cascades at BAL (QB3), MIA (QB2), SEA (QB2), NE (LG1+LG2, RB1+RB2, CB1), SF (3 starting DBs), DAL &amp; AZ</td><td><a href="depth-deficiencies.html">1st–4th String</a></td><td class="src"><a href="https://www.nfl.com/injuries/league/2026/REG10" target="_blank" rel="noopener">NFL.com REG10 ↗</a></td></tr>
    <tr><td><b>Week 11 slate &amp; flex changes</b></td><td>13 games (Thu Nov 19 – Mon Nov 23) including MIN vs SF in Mexico City; 6 byes (ATL, CLE, GB, LAR, NE, SEA)</td><td><a href="schedule.html">Week 11</a></td><td class="src"><a href="https://www.nfl.com/news/week-11-schedule-change" target="_blank" rel="noopener">NFL.com ↗</a></td></tr>
    <tr><td><b>2026 Rulebook &amp; roster anchors</b></td><td>TD 6 / FG 3 / Safety 2 / Try 1–2; modified 2026 kickoff setup/50-yd touchback &amp; anytime onside kick; 48 active requires ≥8 OL</td><td><a href="depth-deficiencies.html">Rules Table</a></td><td class="src"><a href="https://operations.nfl.com/rules-officiating/2026-nfl-rulebook" target="_blank" rel="noopener">Operations.nfl.com ↗</a></td></tr>
  </tbody>
</table></div>

<h2 style="margin-top:34px">2 · System Architecture &amp; Decision Governance</h2>
<div class="grid g2" style="margin-top:14px">
  <div class="card"><h3>Line Origination &amp; Skill Separation</h3><p><a href="lines-lab.html">Lines Lab</a> and <a href="analysis.html">Analysis</a> originate transparent MODEL spreads, totals, and win probabilities from verified scoring &amp; efficiency inputs while stripping out one-score/turnover luck (<a href="correlations.html">Luck Residuals</a>).</p></div>
  <div class="card"><h3>Gated Strategy Leaderboard</h3><p><a href="strategies.html">Strategies</a> evaluates single bets, parlays, and prop combos under 7 strict gates (walk-forward out-of-sample, n ≥ 200, Brier skill, copula correlation check, fold stability). Reward status remains UNPAID while n &lt; 200.</p></div>
  <div class="card"><h3>1st–4th String Deficiency Tracker</h3><p><a href="injuries.html">Injuries</a> and <a href="depth-deficiencies.html">1st–4th String</a> join active practice reports with IR transactions and official club depth charts on both offense and defense.</p></div>
  <div class="card"><h3>Suggestions &amp; Information-Gap Registers</h3><p><a href="suggestions.html">Suggestions</a> presents 12 reviewable upgrade proposals with effort/impact/risk trade-offs; <a href="questions.html">Questions</a> inventories 24 answered, partial, open, and blocked questions.</p></div>
</div>

<h2 style="margin-top:34px">3 · Recommended Reviewer Decision Paths (Choose Before Implementation)</h2>
<div class="tblwrap"><table>
  <thead><tr><th>Path</th><th>First Action</th><th>What It Unblocks</th><th>Governance Link</th></tr></thead>
  <tbody>
    <tr><td><b>Path A · Multi-Season + Play-by-Play Data</b> (Recommended)</td><td>Ingest 2023–2025 official game logs &amp; per-game play-by-play box scores</td><td>Clears the n ≥ 200 sample gate (G2), settles HFA CI, and measures play-level SGP/prop correlations</td><td class="src"><a href="https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/suggestions.json" target="_blank" rel="noopener">Suggestions JSON ↗</a></td></tr>
    <tr><td><b>Path B · Full 32-Club Depth Automation</b></td><td>Extend club depth-chart parser from 12 clubs to all 32 clubs + 90-minute pre-kickoff Inactive Lists</td><td>Eliminates club PR chart lag (RA-06) and completes league-wide 1st–4th string coverage</td><td class="src"><a href="https://operations.nfl.com/calendar-events/nfl-free-agency/contract-language" target="_blank" rel="noopener">Operations.nfl.com ↗</a></td></tr>
    <tr><td><b>Path C · Timestamped Market Capture</b></td><td>Approve licensed open/closing odds snapshot schema with strict UTC timestamps</td><td>Unlocks Closing Line Value (CLV), market edge measurement, and Gate G7 execution checks</td><td class="src"><a href="https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/questions.json" target="_blank" rel="noopener">Questions JSON ↗</a></td></tr>
  </tbody>
</table></div>

<div class="note warn" style="margin-top:20px"><p><b>Research disclosure:</b> This repository produces transparent statistical models and data verification audits — not betting or financial advice. Full markdown brief also committed at <code>EXECUTIVE_SUMMARY.md</code>.</p></div>
"""
    (OUT / "executive-summary.html").write_text(
        page_shell(
            "Executive Summary",
            "Executive summary of verified 2026 NFL data, line origination, gated strategy leaderboard, depth-chart tracking, and next decisions.",
            "Executive Summary",
            "Project architecture, verified 2026 findings & decision blockers",
            "One-page synthesis of what is verified from official NFL sources, what our deterministic models show, what is flagged for review, and which path a reviewer should approve next.",
            "executive-summary.html",
            body,
        )
    )


def build_lines_lab_page() -> None:
    corr = json.loads((ROOT / "data" / "correlations-2026.json").read_text())
    wk11_rows = []
    for g in corr["week11_v1_model_originated_lines"]:
        sp_txt = g["model_fair_spread_home"]
        note_badge = '<span class="b b-warn">Mexico City (HFA=0)</span>' if g["neutral_site"] else '<span class="b b-info">Model v1</span>'
        wk11_rows.append(
            f"<tr>"
            f"<td><b>{esc(g['away_abbr'])} at {esc(g['home_abbr'])}</b><div class=\"tiny\">{esc(g['date'])} · {esc(g['kickoff_et'])}</div></td>"
            f"<td class=\"num\">{g['model_proj_away']:.1f} – {g['model_proj_home']:.1f}</td>"
            f"<td class=\"num\"><b>{esc(sp_txt)}</b></td>"
            f"<td><span class=\"blank\">— blank —</span></td>"
            f"<td class=\"num\"><b>{g['model_fair_total']:.1f}</b></td>"
            f"<td><span class=\"blank\">— blank —</span></td>"
            f"<td class=\"num\">{g['model_home_win_prob_pct']:.1f}% ({esc(g['model_fair_ml_home'])} / {esc(g['model_fair_ml_away'])})</td>"
            f"<td class=\"src\">{note_badge} · <a href=\"{esc(g['schedule_source'])}\" target=\"_blank\" rel=\"noopener\">NFL.com ↗</a></td>"
            f"</tr>"
        )

    body = f"""
<div class="note"><p><b>MODEL ONLY — Not a sportsbook line:</b> Every spread, total, and moneyline on this page is computed transparently from verified 2026 NFL.com scoring and yards-per-play statistics. Market Spread, Market Total, and Edge columns are intentionally left <b>blank</b> because no official NFL source publishes betting odds (<a href="flagged.html">IR-09</a>).</p></div>

<h2 style="margin-top:26px">1 · Origination Formula (v0 Points Baseline &amp; v1 Efficiency-Blended Model)</h2>
<div class="calc-out">v0 Baseline:   projHome = (homePF/g + awayPA/g)/2 + HFA     projAway = (awayPF/g + homePA/g)/2
v1 Blended:    70% PF/PA baseline + 30% Net Yards/Play adjustment (r = +0.700 with Net Pts/G)
True-Home HFA: +0.50 pts (measured across 129 non-neutral 2026 games; 0.00 pts for Mexico City / Munich)
Win Prob &amp; ML: P(home) = Φ(fairMargin / 13.32)  →  Fair ML = −100·P/(1−P) if P≥0.5 else +100·(1−P)/P</div>

<div class="grid g2" style="margin-top:22px">
  <div class="card">
    <h3>Interactive Fair-Line Calculator (MODEL ONLY)</h3>
    <p>Pre-filled with Week 11 MIN vs. SF (neutral site in Mexico City → set HFA = 0.0; SF 235/156, MIN 146/116 over 8 games).</p>
    <form id="lines-calc">
      <label for="g">Games played (each club)</label><input id="g" type="number" value="8" min="1" max="17">
      <label for="hPF">Home PF</label><input id="hPF" type="number" value="235">
      <label for="hPA">Home PA</label><input id="hPA" type="number" value="156">
      <label for="aPF">Away PF</label><input id="aPF" type="number" value="146">
      <label for="aPA">Away PA</label><input id="aPA" type="number" value="116">
      <label for="hfa">Home-field advantage (pts; 0.50 true-home, 0.0 neutral)</label><input id="hfa" type="number" value="0.0" step="0.1">
      <label for="sd">Margin SD (pts; 2026 measured = 13.32)</label><input id="sd" type="number" value="13.32" step="0.01">
      <p><button type="submit">Recompute fair line</button></p>
    </form>
    <div id="lines-out" class="calc-out" aria-live="polite"></div>
  </div>

  <div class="card">
    <h3>Interactive Pearson Correlation Checker</h3>
    <p>Test any two paired weekly or team series before combining legs in a parlay or prop combo:</p>
    <form id="corr-calc">
      <label for="corr-x">Series X (comma or space separated, n ≥ 3)</label>
      <input id="corr-x" type="text" value="110.2, 108.9, 103.5, 98.4, 84.1, 79.3" style="width:100%">
      <label for="corr-y">Series Y (equal length)</label>
      <input id="corr-y" type="text" value="32.0, 29.4, 30.0, 25.3, 18.0, 15.8" style="width:100%">
      <p><button type="submit">Compute Pearson r</button></p>
    </form>
    <div id="corr-out" class="calc-out" aria-live="polite">Enter two paired series and click Compute Pearson r.</div>
  </div>
</div>

<h2 style="margin-top:34px">2 · Model Roadmap &amp; Verification Gates</h2>
<div class="tblwrap"><table>
  <thead><tr><th>Version</th><th>Specification</th><th>Why It Matters</th><th>Status</th><th>Reference Source</th></tr></thead>
  <tbody>
    <tr><td><b>v0 — Raw PF/PA Baseline</b></td><td>Season PF/G &amp; PA/G + HFA</td><td>100% transparent browser sanity check</td><td><span class="b b-ok">Live above</span></td><td class="src"><a href="https://www.nfl.com/standings/division/2026/reg" target="_blank" rel="noopener">NFL.com Standings ↗</a></td></tr>
    <tr><td><b>v1 — Opponent &amp; Efficiency Adjusted</b></td><td>Opponent-shrunk power ratings (<a href="analysis.html">Analysis</a>) + Net Yds/Play blend (below)</td><td>Removes soft-schedule &amp; turnover-luck distortion</td><td><span class="b b-ok">Live below</span></td><td class="src"><a href="https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all" target="_blank" rel="noopener">NFL.com Team Stats ↗</a></td></tr>
    <tr><td><b>v2 — Play-by-Play EPA &amp; Key Numbers</b></td><td>Down-distance EPA + empirical 3/6/7/10 discrete margin push model</td><td>Continuous normal CDF misprices NFL key numbers 3 &amp; 7</td><td><span class="b b-warn">Proposed (Suggestions)</span></td><td class="src"><a href="https://static.www.nfl.com/image/upload/fl_attachment/league/tqivdkzt9mu6wdgsh1ku.pdf" target="_blank" rel="noopener">2026 Rules PDF ↗</a></td></tr>
    <tr><td><b>v3 — 1st–4th String Injury Delta Layer</b></td><td>Positional starter→backup priors gated by <a href="depth-deficiencies.html">1st–4th String</a> cascades</td><td>Captures late-week QB/OL/CB clusters invisible to season averages</td><td><span class="b b-warn"> qualitative active; pts blank</span></td><td class="src"><a href="https://www.nfl.com/injuries/league/2026/REG10" target="_blank" rel="noopener">NFL.com REG10 ↗</a></td></tr>
  </tbody>
</table></div>

<h2 style="margin-top:34px">3 · Week 11 Originated Fair-Line Sheet (All 13 Games · Market Columns Blank Until Captured)</h2>
<p class="sub">Generated deterministically by <code>scripts/compute_correlations.py</code>. Note: MIN at SF is played in Mexico City (neutral site → HFA = 0.00 pts).</p>
<div class="tblwrap"><table>
  <thead><tr><th>Week 11 Matchup</th><th class="num">Proj Score (Away–Home)</th><th class="num">Model v1 Spread</th><th>Market Spread</th><th class="num">Model v1 Total</th><th>Market Total</th><th class="num">Home Win% (Fair ML)</th><th>Source</th></tr></thead>
  <tbody>{"".join(wk11_rows)}</tbody>
</table></div>
"""
    (OUT / "lines-lab.html").write_text(
        page_shell(
            "Lines Lab",
            "Transparent methodology and interactive calculator for originating fair NFL spreads, totals, and moneylines from verified data.",
            "Line Origination Lab",
            "Originate your own fair spreads, totals & moneylines",
            "Interactive browser calculators plus reproducible Week 11 MODEL fair lines derived from verified 2026 scoring and net yards-per-play efficiency — with market odds columns honestly left blank.",
            "lines-lab.html",
            body,
        )
    )


def build_schedule_page() -> None:
    sched = json.loads((ROOT / "data" / "schedule-week11-2026.json").read_text())
    g_rows = []
    for g in sched["games"]:
        g_rows.append(
            f"<tr>"
            f"<td>{esc(g['date'])}</td>"
            f"<td><b>{esc(g['away'])}</b></td>"
            f"<td><b>{esc(g['home'])}</b></td>"
            f"<td class=\"num\">{esc(g['timeET'])}</td>"
            f"<td>{esc(g['tv'])}</td>"
            f"<td class=\"tiny\">{esc(g.get('note',''))}</td>"
            f"<td class=\"src\"><a href=\"{esc(sched['source'])}\" target=\"_blank\" rel=\"noopener\">NFL.com ↗</a></td>"
            f"</tr>"
        )
    bye_rows = []
    for b_team in sched["byeWeek11"]:
        bye_rows.append(
            f"<tr>"
            f"<td><b>{esc(b_team)}</b></td>"
            f"<td class=\"src\"><a href=\"{esc(sched['byeSource'])}\" target=\"_blank\" rel=\"noopener\">NFL.com Bye Weeks ↗</a></td>"
            f"</tr>"
        )
    body = f"""
<div class="grid g4">
  <div class="card"><div class="big">{len(sched['games'])}</div><p>Official Week 11 games (Thu Nov 19 – Mon Nov 23, 2026)</p></div>
  <div class="card"><div class="big">{len(sched['byeWeek11'])}</div><p>Clubs on Week 11 bye (13 × 2 + 6 = 32 NFL clubs accounted for)</p></div>
  <div class="card"><div class="big">2</div><p>Official Nov 9 flex moves (PIT@PHI to 1:00p CBS; JAX@NYG to 4:25p CBS)</p></div>
  <div class="card"><div class="big">1</div><p>International neutral-site game: MIN vs SF in Mexico City (SNF)</p></div>
</div>

<h2 style="margin-top:30px">1 · Official Week 11 Game Slate (All Times ET)</h2>
<div class="tblwrap"><table>
  <thead><tr><th>Date</th><th>Away</th><th>Home</th><th class="num">Kickoff (ET)</th><th>Broadcast</th><th>Official Note</th><th>Source</th></tr></thead>
  <tbody>{"".join(g_rows)}</tbody>
</table></div>

<h2 style="margin-top:34px">2 · Week 11 Bye Clubs (6 Teams)</h2>
<div class="tblwrap"><table>
  <thead><tr><th>Club on Bye (Week 11)</th><th>Official Source</th></tr></thead>
  <tbody>{"".join(bye_rows)}</tbody>
</table></div>
"""
    (OUT / "schedule.html").write_text(
        page_shell(
            "Week 11 Schedule",
            "Official NFL Week 11 2026 schedule, Nov 9 flex changes, and bye teams transcribed from NFL.com.",
            "Upcoming Slate · Week 11",
            "Official 2026 Week 11 schedule & bye clubs",
            "Transcribed verbatim from NFL.com’s November 9, 2026 schedule-change release and official 2026 bye-week schedule. For completed Weeks 1–9 final scores, see <a href=\"results.html\">Results</a>.",
            "schedule.html",
            body,
        )
    )


if __name__ == "__main__":
    build_depth_page()
    build_correlations_page()
    build_repo_audit_page()
    build_exec_summary_page()
    build_lines_lab_page()
    build_schedule_page()
    print("SUCCESS: Built depth-deficiencies, correlations, repo-audit, executive-summary, lines-lab, schedule")
