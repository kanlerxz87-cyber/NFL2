# NFL2 — verified 2026 NFL analytics

**Live site:** https://kanlerxz87-cyber.github.io/NFL2/
**Executive summary:** [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)
**Coordination board:** [COORDINATION.md](COORDINATION.md)

---

## The rule this project runs on

> Every number on the site either traces to an official NFL source, or is explicitly labelled as
> **model output**. Nothing is inferred. If an official source does not state a value, the cell is
> blank and the item is listed on the **Flagged for Review** page.

That rule is enforced by scripts, not by good intentions.

---

## Pages

| Page | Question it answers |
|---|---|
| [Overview](index.html) | What is here, what is verified, what is missing |
| [Results](results.html) | Every game of weeks 1–9, with a source link per row |
| [Standings](standings.html) | Official standings, with an independent recount beside them |
| [Team Stats](teams.html) | Passing and rushing, offence and defence, with withheld tables named |
| [Injuries & Depth](injuries.html) | Who is hurt, and whether they actually start |
| [Analysis](analysis.html) | Power ratings, correlations, luck, model lines |
| [Strategies](strategies.html) | Six strategies, seven gates, zero validated |
| [Method](method.html) | How every number is produced, and where it is weak |
| [Data Sources](sources.html) | Every official page used — and every one rejected |
| [Questions](questions.html) | 24 questions, with the unanswerable ones left blank |
| [Suggestions](suggestions.html) | 12 proposals, none implemented |
| [Flagged for Review](flagged.html) | Every irregularity and withheld dataset, severity-rated |

---

## Repository layout

```
data/
  games_2026.json          136 game rows, weeks 1-9, each with date and source URL
  standings_raw.json       32 clubs, official standings verbatim
  team_stats.json          32 clubs x 4 stat families + withheld tables recorded
  player_verified.json     8 passing lines proven by exact equality with club team lines
  injuries_week10.json     254 player rows, all 14 Week 10 games
  depth_charts.json        4 club depth charts, normalised
  questions.json           24 questions + answer status + discovery route
  suggestions.json         12 proposals, none implemented
  derived/
    verification_report.json   23 data checks
    personnel.json             injury x depth-chart join + 9 integrity checks
    analysis.json              power ratings, correlations, backtests, model lines
    site_report.json           12 HTML checks

scripts/
  verify_data.py           checks the game log and team stats against official records
  verify_personnel.py      checks the depth-chart join (9 checks)
  analyse.py               deterministic model + walk-forward backtest
  personnel.py             joins the injury report to the depth charts
  build_site.py            generates all 12 HTML pages from the JSON
  verify_site.py           checks the generated HTML before it ships
```

---

## Reproducing everything

```bash
python3 scripts/verify_data.py       # 20/23 — the 3 soft fails are published, not hidden
python3 scripts/personnel.py         # rebuild the injury x depth-chart join
python3 scripts/verify_personnel.py  # 9/9
python3 scripts/analyse.py           # rebuild the model (deterministic, no randomness)
python3 scripts/build_site.py        # regenerate all 12 pages
python3 scripts/verify_site.py       # 12/12
```

No third-party dependencies. Pure Python 3, standard library only — no numpy, no pandas, no network
calls at build time. Every input is a committed JSON file.

---

## What is verified

| Layer | Result |
|---|---|
| Game log vs official standings | **32/32 clubs** match on W, L, T, PCT, PF, PA, net points, streak |
| League-wide conservation | **8/8** identities hold exactly (pass/rush yards, sacks, TD, INT, 1st downs) |
| Data checks | **20/23** — 3 soft source-level failures, all published |
| Personnel checks | **9/9** |
| Site checks | **12/12** |
| Strategies validated | **0 of 6** — all underpowered, stated before any hit rate is shown |

---

## What is deliberately missing

Nothing here is filled in by inference. The site publishes these gaps rather than papering over them:

- **Odds and market prices** — no official NFL source publishes them. No ROI is claimed anywhere.
- **Player-prop correlations** — no per-game box scores, so the dependence is unmeasurable.
- **Depth position for 28 of 32 clubs** — only 4 charts transcribed and verified.
- **Rushing and receiving leaderboards** — column order unprovable, so withheld entirely.
- **Team scoring tables** — column meaning unprovable, so withheld entirely.

See [Flagged for Review](flagged.html) for the full list with severities and fixes.

---

## Corrections found during the build

Two errors were found and fixed by the verification layers rather than shipped:

1. **Home-field advantage** was initially computed over all games, mixing 7 neutral-site games into a
   home-minus-away average. That produced a misleading +0.00. Restricted to true home games it is
   **+0.50 points, 95% CI [−1.80, +2.79]** — and the conventional prior fits inside that interval, so
   2026 cannot reject it.
2. **The parlay prose contradicted the measurement.** The text asserted negative correlation between
   a game's two sides while the measured r was **+0.076**. The generator now derives that sentence
   from the number, and the site check fails the build if a page shows `VALIDATED` while the analysis
   says none is.

A third bug — a duplicate position-group label that scored a third-string player as a starter — is
the reason `verify_personnel.py` exists. A wrong answer that looks right is more dangerous than an
error.
