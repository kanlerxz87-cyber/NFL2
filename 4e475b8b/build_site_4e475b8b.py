#!/usr/bin/env python3
"""Session 4e475b8b — build the dated dashboard 4e475b8b/index.html.

Deterministic: re-running regenerates byte-identical HTML from the registers in data/.
Every table row carries an official source link. Blank cells render as 'not published'.
"""
import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "4e475b8b" / "index.html"
HUB = ROOT / "data" / "injuries_wk10_4e475b8b_20261116.csv"
RV = ROOT / "data" / "reverification_4e475b8b_20261116.csv"
TX = ROOT / "data" / "transactions_read_4e475b8b_20261116.csv"
SRC = "https://www.nfl.com/injuries/"
SRC_RES = "https://www.nfl.com/transactions/league/reserve-list/2026/11"
SRC_TRD = "https://www.nfl.com/transactions/league/trades/2026/11"


def cell(v, link=None):
    v = (v or "").strip()
    if not v:
        return '<td class="blank">not published</td>'
    if link:
        return f'<td><a href="{html.escape(link, quote=True)}">{html.escape(v)}</a></td>'
    return f"<td>{html.escape(v)}</td>"


def table(headers, rows_html, title, note=""):
    note_html = f'<p class="note">{note}</p>' if note else ""
    return (f"<h2>{title}</h2>{note_html}"
            f'<table><thead><tr>{"".join(f"<th>{h}</th>" for h in headers)}</tr></thead>'
            f"<tbody>{''.join(rows_html)}</tbody></table>")


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="|"))


def main():
    hub = read_csv(HUB)
    rv = read_csv(RV)
    tx = read_csv(TX)
    flags = [r for r in read_csv(ROOT / "data" / "flags.csv") if r["id"] in
             {f"FL-{n}" for n in range(97, 106)}]

    designations = [r for r in hub if r["status"]]
    c15m = sum(1 for x in rv if x["scope"] == "15 Nov 12:55Z read" and x["result"] == "MATCH")
    c15x = sum(1 for x in rv if x["scope"] == "15 Nov 12:55Z read" and x["result"] == "MISMATCH")
    c13m = sum(1 for x in rv if x["scope"] == "13 Nov 12:46Z read" and x["result"] == "MATCH")
    c13x = sum(1 for x in rv if x["scope"] == "13 Nov 12:46Z read" and x["result"] == "MISMATCH")
    c13o = sum(1 for x in rv if x["scope"] == "13 Nov 12:46Z read" and x["result"] == "ONLY ON THE PAGE TODAY")

    parts = []
    parts.append("""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Session 4e475b8b — fourth dated injury-hub read (2026-11-16) · NFL2</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f7f9;color:#1a1f2b}
header{background:#013369;color:#fff;padding:1.2rem 1.5rem}
header h1{margin:0 0 .3rem;font-size:1.35rem} header p{margin:.15rem 0;color:#cfd8ea;font-size:.92rem}
main{max-width:1200px;margin:0 auto;padding:1rem 1.5rem 3rem}
h2{font-size:1.1rem;margin:2rem 0 .5rem;border-bottom:2px solid #d50a0a;display:inline-block;padding-bottom:.15rem}
table{border-collapse:collapse;width:100%;background:#fff;font-size:.85rem;box-shadow:0 1px 2px rgba(0,0,0,.06)}
th{background:#eef1f5;text-align:left;padding:.45rem .55rem;border:1px solid #d8dde5;font-size:.8rem;text-transform:uppercase;letter-spacing:.02em}
td{padding:.4rem .55rem;border:1px solid #e2e6ec;vertical-align:top}
td.blank{color:#8a93a3;font-style:italic}
a{color:#0b5bd3;text-decoration:none} a:hover{text-decoration:underline}
.note{font-size:.85rem;color:#475062;margin:.3rem 0 .6rem}
.badge{display:inline-block;padding:.1rem .5rem;border-radius:.6rem;font-size:.78rem;font-weight:600}
.b-high{background:#fde8e8;color:#b21c1c}.b-med{background:#fff4dd;color:#8a5b00}.b-match{background:#e3f5e9;color:#136c34}.b-mism{background:#fde8e8;color:#b21c1c}.b-open{background:#e8eefc;color:#1d4fb8}
p.sum{background:#fff;padding:.9rem 1.1rem;border-left:4px solid #013369;font-size:.92rem}
</style></head><body>
<header><h1>Fourth dated read of the official Week 10 injury hub — 2026-11-16</h1>
<p>Session <strong>4e475b8b</strong> · branch <code>arena/4e475b8b-nfl2</code> · series: 12 Nov ×2 → 13 Nov → 15 Nov ×2 → <strong>16 Nov (this page)</strong></p>
<p>All rows transcribed from <a href="https://www.nfl.com/injuries/" style="color:#9fc1ff">nfl.com/injuries/</a> (fetch completed 2026-11-16T14:44Z, 8 content chunks, raw evidence in <code>4e475b8b/raw/</code>) and from the league's November transactions tabs. Nothing corrected; every table row links its official source.</p></header>
<main>""")

    parts.append(f"""<p class="sum"><strong>Headline.</strong> The official Week 10 page is stable: this read reproduces the
2026-11-15 12:55Z read cell for cell on all {len(hub)} rows and {len(designations)} designations ({sum(1 for r in hub if r['status']=='OUT')} Out,
{sum(1 for r in hub if r['status']=='Q')} Questionable, {sum(1 for r in hub if r['status']=='D')} Doubtful). It still differs from the 13 November read on
{c13x} rows (102 identical, {c13o} rows only on the page today) and from the 12 November canonical table rendered on injuries.html on 177 of 254 shared rows
with 93 rows missing entirely (FL-94, FL-97, FL-99). The same-day transactions re-read widens FL-96 from one player to a class of ten (FL-104) and finds the
hub carries traded players inconsistently (FL-105).</p>""")

    # 1. register
    rows = []
    for r in hub:
        rows.append("<tr>"
                    + cell(r["game"]) + cell(r["team"]) + cell(r["player"], SRC) + cell(r["pos"])
                    + cell(r["injury"]) + cell(r["practice"]) + cell(r["status"])
                    + cell(r["fetched_utc"])
                    + f'<td><a href="{SRC}">official hub</a></td>'
                    "</tr>")
    parts.append(table(
        ["Game", "Team", "Player", "Pos", "Injury", "Practice", "Game status", "Read (UTC)", "Source"],
        rows, f"1 · The 2026-11-16 register — {len(hub)} rows across 28 clubs (data/injuries_wk10_4e475b8b_20261116.csv)",
        "Practice codes: F = Full Participation in Practice, L = Limited, D = Did Not Participate. Status codes: OUT, Q (Questionable), D (Doubtful), blank = none published. The page was read on the day of the Monday W10-14 kickoff (8:15 PM EST); the Monday designations had not changed since the 15 November read."))

    # 2. delta summary rows
    drows = [
        ["vs 2026-11-15 12:55Z read (5de1805b)", f"{len(hub)} rows compared", c15m, c15x, 0, 0, SRC],
        ["vs 2026-11-13 12:46Z read (83246f00)", "296 prior rows joined", c13m, c13x, c13o, 0, SRC],
        ["vs canonical 12 Nov table (data/injuries_2026_wk10.csv, rendered on injuries.html)", "254 prior rows joined", 77, 177, 93, 0, SRC],
    ]
    dhtml = "".join(
        "<tr>" + cell(r[0]) + cell(r[1]) + f'<td class="{"blank" if r[2]==0 else ""}">{r[2]}</td>'
        + f'<td class="{"blank" if r[3]==0 else ""}">{r[3]}</td>'
        + f'<td class="{"blank" if r[4]==0 else ""}">{r[4]}</td>'
        + f'<td class="{"blank" if r[5]==0 else ""}">{r[5]}</td>'
        + f'<td><a href="{r[6]}">official hub</a></td></tr>'
        for r in drows)
    parts.append(table(["Compared against", "Basis", "Identical rows", "Differing rows", "Only on page today", "Dropped since", "Source"],
                       dhtml, "2 · Row-level delta summary (data/reverification_4e475b8b_20261116.csv, 694 comparison rows)",
                       "Per-row detail with the exact differing cells is in data/reverification_4e475b8b_20261116.csv. The 51 rows only on the page today are the 15 Nov-era filings the 13 Nov read never saw; 0 rows disappeared after 13 Nov."))

    # 3. reserve list overlap
    reserve = [r for r in tx if r["page"] == "reserve-list"]
    trades = [r for r in tx if r["page"] == "trades"]
    hub_names = {r["player"]: r for r in hub}
    orows = []
    for r in reserve:
        h = hub_names.get(r["player"])
        on_hub = "yes" if h else "no"
        detail = f"{h['practice']} / {h['status'] or '—'} ({h['team']}, {h['game']})" if h else "absent from the report"
        orows.append("<tr>" + cell(r["date"]) + cell(r["player"], SRC_RES) + cell(r["from"]) + cell(r["transaction"])
                     + f'<td>{on_hub}</td>' + cell(detail)
                     + f'<td><a href="{SRC_RES}">reserve list</a> · <a href="{SRC}">hub</a></td></tr>')
    parts.append(table(["IR date", "Player", "Club", "Transaction", "On weekly report?", "Report row (practice / status)", "Source"],
                       orows, "3 · November Reserve List vs the Week 10 report — the FL-96 class is ten players (FL-104)",
                       "The Reserve List names 25 Reserve/Injured placements for November 2026. Ten of those players also appear on the Week 10 injury hub — nine with Did Not Participate and game status Out (all dated 11/14), plus Puka Nacua (11/12, DNP, no designation). The other fifteen do not appear. Data: data/transactions_read_4e475b8b_20261116.csv."))

    # 4. trades join
    trows = []
    for r in trades:
        hits = [h for h in hub if h["player"] == r["player"]]
        if hits:
            detail = "; ".join(f"{h['team']} ({h['game']}): {h['practice']}/{h['status'] or '—'}" for h in hits)
            side = "new club" if hits[0]["team"] == r["to"] else ("old club" if hits[0]["team"] == r["from"] else "neither")
        else:
            detail, side = "absent from the Week 10 report", ""
        trows.append("<tr>" + cell(r["date"]) + cell(r["player"], SRC_TRD) + cell(r["from"] + " → " + r["to"])
                     + f'<td>{side or "not published"}</td>' + cell(detail)
                     + f'<td><a href="{SRC_TRD}">trades</a> · <a href="{SRC}">hub</a></td></tr>')
    parts.append(table(["Trade date", "Player", "Move", "Report lists", "Report placement", "Source"],
                       trows, "4 · November trades vs the Week 10 report — traded players are placed inconsistently (FL-105)",
                       "Bates and Davis (traded 11/10) are listed under their new club Jacksonville; Henley (traded 11/10 LAC→DEN) is listed under his old club, the Chargers, in the W10-14 block. Nine traded players do not appear on the report at all."))

    # 5. FL-95 re-confirmation
    f95 = [
        ["Jacoby Brissett", "Trades 11/06 AZ→BAL", "CONFIRMED 2026-11-16", SRC_TRD],
        ["Keenan Allen", "Trades 11/10 IND→SF", "CONFIRMED 2026-11-16", SRC_TRD],
        ["Josh Downs", "Trades 11/10 IND→KC", "CONFIRMED 2026-11-16", SRC_TRD],
        ["Malik Willis", "Reserve/Injured 11/10 (MIA)", "CONFIRMED 2026-11-16", SRC_RES],
        ["Puka Nacua", "Reserve/Injured 11/12 (LAR)", "CONFIRMED 2026-11-16", SRC_RES],
    ]
    fhtml = "".join("<tr>" + cell(r[0], r[3]) + cell(r[1]) + f'<td class="b-match">{r[2]}</td>'
                    + f'<td><a href="{r[3]}">official page</a></td></tr>' for r in f95)
    parts.append(table(["Player", "FL-95's recorded fact", "Re-read 2026-11-16", "Source"],
                       fhtml, "5 · FL-95 named rows re-confirmed (the transactions hub unblocks the reserve-list and stale-depth brief items)",
                       "FL-95 stays open as a register row until the brief items (VR-25/VQ-06, VR-17/VR-26/VQ-07) are closed by the owner; the underlying facts are now re-confirmed on the day of the W10-14 kickoff."))

    # 6. flags published this session
    frows = []
    for r in flags:
        frows.append("<tr>"
                     + cell(r["id"]) + cell(r["type"]) + f'<td><span class="badge b-{r["severity"]}">{r["severity"]}</span></td>'
                     + cell(r["finding"]) + cell(r["decision_impact"]) + f'<td><span class="badge b-open">{r["status"]}</span></td>'
                     + "".join(f'<td><a href="{html.escape(u, quote=True)}">source {i+1}</a></td>' for i, u in enumerate(r["source"].split(" :: ")))
                     + "</tr>")
    parts.append(table(["Id", "Type", "Severity", "Finding", "Decision impact", "Status", "Source"],
                       frows, "6 · Flags appended to the canonical register by this session (FL-97…FL-105)",
                       "FL-97…FL-103 promote the seven FL-DCF findings (change request CR-D1, logged by session dcf3b0cc on 2026-11-15) into data/flags.csv so they render on the canonical Flagged for Review page; each row names its FL-DCF id in the evidence cell, and dcf3b0cc/flagged.html remains the historical record. FL-104 and FL-105 are new findings of the 2026-11-16 read."))

    # 7. faithful-transcription note
    parts.append(f"""<h2>7 · Faithful-transcription note (cross-club rows)</h2>
<p class="sum">The hub read today lists several players under clubs their players-page or transaction history does not obviously tie them to:
<strong>Myles Garrett</strong> and <strong>David Njoku</strong> in the LAR block, <strong>Quenton Nelson</strong> in the SEA block,
<strong>Mike Evans</strong> in the SF block, <strong>Keaton Mitchell</strong> in the LAC block, and <strong>Kaytron Allen</strong>,
<strong>Will Kacmarek</strong> and <strong>Michael Taaffe</strong> in the MIA block. Following FL-93's convention, these rows are transcribed
exactly as published and <em>no claim is made that they are wrong</em>: no roster or club page was read in this session, so corroboration is
pending (Q-46). The two FL-93 rows sighted on 2026-11-15 (Kenneth Walker III under KC, Dexter Lawrence under CIN) reproduce today unchanged.</p>""")

    parts.append("""<h2>8 · Method and provenance</h2>
<p class="sum">Chunks 0–7 of <a href="https://www.nfl.com/injuries/">nfl.com/injuries/</a> fetched 2026-11-16 (window closing 14:44Z) and stored verbatim in
<code>4e475b8b/raw/chunk-*.md</code>; the two November transactions tabs stored verbatim beside them. <code>4e475b8b/build.py</code> parses the chunks
mechanically (four chunk-boundary row splits spliced positionally and asserted), enforces the practice/status vocabulary, fails loudly on structural drift
(347 rows / 28 clubs expected), and writes the register. <code>4e475b8b/build_transactions.py</code> parses the transactions pages and joins them against
the register. <code>tools/verify_flags_4e475b8b.py</code> re-derives the flag register invariants (unique contiguous ids FL-01…FL-105, next free id,
every row sourced, every FL-reference resolving: 911 references checked). Re-running all three reproduces every byte of this page's inputs.</p>
<p class="note">Change requests logged rather than applied: CR-4E47-01 (add <code>4e475b8b/</code> to scripts/audit_all_pages.py's walk),
CR-4E47-02 (register <code>4e475b8b/</code> in the landing-page tree map, owner tools/build_site.py — PR #71's file),
CR-4E47-03 (tools/s2268_verify.py scope allowlist will report scope-only notices for this session's new files).</p>
</main></body></html>""")

    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(hub)} register rows, {len(flags)} flag rows)")


if __name__ == "__main__":
    main()
