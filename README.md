# NFL2 — verified NFL research & decision dashboard

**Live site:** https://kanlerxz87-cyber.github.io/NFL2/
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
| `index.html`, root `*.html` | Landing page and category subpages (GitHub Pages publishes `main:/`) |
| `assets/` | Local CSS and JavaScript, no external dependencies |
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
