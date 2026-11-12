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


---

## Appendix: third parallel build (preserved, not merged into the pages above)

Three independent sessions produced dashboards in this repository. The root build and the
`docs/` build are preserved exactly as their authors left them. This section documents the
third build (session `01b698ef`), which is published under `review/` so that no existing
page is overwritten.

## Verification Review Dashboard — session 01b698ef

**Live site:** https://kanlerxz87-cyber.github.io/NFL2/review/
**Prepared:** 2026-11-12 (UTC) · **Branch:** `arena/01b698ef-nfl2`

## Executive summary

The repository started with a single 6-byte `README.md` and no data, code, tests or site.
This project turns that empty repo into a live GitHub Pages dashboard containing a full
requirements register, a fetch-verified official-source registry, decision prerequisites,
a dedicated suggestions section with a pre-implementation path chooser, strategy research,
validation gates, correlation structure, a leaderboard design, injury/depth tracking, and a
clearly labelled **Flagged for Review** page.

### Most important findings

1. **The NFL does not publish its own betting lines.** NFL.com widgets show odds, spreads and
   totals supplied by official bookmaker partners
   ([NFL Support](https://support.nfl.com/hc/en-us/articles/35869698780564-If-I-place-a-bet-on-NFL-com-or-the-NFL-app-am-I-betting-with-the-NFL)).
   "Originating my own lines" therefore means an independent model line compared with licensed
   market prices. A league-official algorithmic "Predicted Score" exists
   ([NFL Support](https://support.nfl.com/hc/en-us/articles/35869771634580-What-is-the-Predicted-Score)).
2. **No numeric results can be honestly reported.** There is no licensed historical odds,
   play-by-play or strategy-result dataset here. Correlation coefficients, ROI, Brier scores
   and leaderboard scores are **blank and flagged `UNVERIFIED`**. The official methods for
   computing them are documented and linked.
3. **Injury tracking needs three layers:** the weekly
   [official injury report](https://www.nfl.com/injuries/league/2026/REG10), club depth charts
   labelled [First–Fourth (unofficial)](https://www.chiefs.com/team/depth-chart), and the
   definitive inactive list in the
   [Game Day Administration Report](https://operations.nfl.com/game-operations-logistics/preparation-safety/game-and-stadium-prep)
   exchanged at the 90-minute meeting.
4. **Parlay correlation is a rule as well as a statistic.** Approved operator house rules
   prohibit related-outcome parlays and carve out same-game parlays
   ([Massachusetts Gaming Commission](https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf));
   [NFL integrity policy](https://www.nfl.com/news/nfl-draftkings-fanduel-fanatics-sports-betting-partners)
   restricts injury-linked wagers.
5. **A judged leaderboard template already exists** in the official
   [Big Data Bowl](https://operations.nfl.com/programs-initiatives/innovation/big-data-bowl)
   ($100,000 prize pool, PASS/FAIL standards) and
   [public/private leaderboard docs](https://www.kaggle.com/docs/competitions).

### Decisions that must be made first

Seventeen blocking questions are listed on `decisions.html`. Four gate everything: the
definition of "line" (D02), the source and licence for historical prices (D04), whether injury
signals are executable under league integrity rules (D05), and the legal jurisdiction for
rewards (D07). Suggestions for discovering each missing item are recorded next to the question.

### Recommended path

Path **A** (lock the evidence layer) then **B** (answer the blocking questions). Path **D**
(licensed data) is the only route to real correlation values and is currently blocked. A
reviewer chooses a path on `suggestions.html`; no implementation begins before that choice is
recorded.

## Repository layout

| Path | Purpose |
| --- | --- |
| `review/index.html`, `review/*.html` | This session's landing page and category subpages (namespaced to preserve other sessions) |
| `review/assets/` | Local CSS and JavaScript for this build, no external dependencies |
| `data/content.py` | Single source of truth for every table row |
| `data/records.json` | One record per rendered row, used for line-by-line verification |
| `data/verification-report.json` | Machine-readable result of `tools/verify.py` |
| `tools/build_site.py` | Renders all pages from `content.py` |
| `tools/verify.py` | Checks rows, sources, blank cells, badges, navigation and all links |
| `research/` | Source registry, repo audit, irregularities |
| `content/` | Verbatim brief and the research documents behind each page |
| `COORDINATION.md` | Shared task board, claims, verification log, PR/merge record |
| `.github/workflows/verify.yml` | CI verification on push and pull request |

## Verification rule

Every table row links to an official first-party source that was opened and matched to a
recorded title and excerpt. If a value cannot be confirmed from an official source, the cell is
**blank** and the row carries an `UNVERIFIED` badge and a flag ID. Nothing is inferred,
estimated or filled in. Third-party blogs, aggregators and search snippets are never used as
sources for values. Run locally with:

```sh
python3 tools/build_site.py
python3 tools/verify.py
```

## Coordination, PR and deploy

Task claims, sources, verification performed and irregularities are recorded in
[`COORDINATION.md`](COORDINATION.md). The pull request link and merge/deploy result are
recorded there as well. Flagged irregularities are non-blocking and are published on
`flagged.html`.

## Responsible use

This repository documents research and a validation framework only. It places no wagers,
handles no money, and offers no betting advice. Legal sports betting is age- and
jurisdiction-restricted. Help resources:
[National Council on Problem Gambling](https://www.ncpgambling.org/).
Not affiliated with or endorsed by the NFL or Kaggle; official pages are cited as references.

---

## Cross-Session Integration & Full-Repository Row-Source Verification (Session `eaba7863`)

- **Live Root Dashboard (18 unified pages):** https://kanlerxz87-cyber.github.io/NFL2/
  - Added [`depth-deficiencies.html`](depth-deficiencies.html) (12 official NFL club depth charts joined to Week 10 `REG10` & IR news across **18 verified 1st → 2nd → 3rd → 4th-string offense & defense cascades** + 2026 NFL roster/elevation/ATC spotter rules).
  - Added [`correlations.html`](correlations.html) (**14 reproducible 2026 NFL team correlations** across `n = 32` clubs, Fisher-*z* 95% CIs, Same-Game Parlay / prop copula blank register, and 32-club luck-vs.-skill residuals).
  - Added [`repo-audit.html`](repo-audit.html) (line-by-line commit & upstream official-source audit, including `RA-05` `REG10` IR blindspots and `RA-06` club depth-chart lag).
  - Unified [`executive-summary.html`](executive-summary.html), [`lines-lab.html`](lines-lab.html) (interactive fair-line & correlation calculators + Week 11 MODEL v1 originated lines), and [`schedule.html`](schedule.html) into the root navigation while preserving [`docs/`](docs/index.html) and [`review/`](review/index.html) intact.
- **Full-Repo Verification Suite (51 HTML pages, 137 tables, 1,828 sourced rows, 0 broken links):**
  ```sh
  python3 scripts/verify_data.py
  python3 scripts/verify_personnel.py
  python3 scripts/verify_site.py
  python3 scripts/validate_data.py
  python3 tools/build_site.py && python3 tools/verify.py
  python3 scripts/audit_all_pages.py
  ```

