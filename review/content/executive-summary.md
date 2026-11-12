# Executive summary

**Project:** NFL2 — requirements, verified research, decision gates, strategy framework,
injury tracking and a live GitHub Pages dashboard.
**Prepared:** 2026-11-12 (UTC) · **Session:** `session-01b698ef`
**Site:** https://kanlerxz87-cyber.github.io/NFL2/

## What was found

The repository was effectively empty: one commit (`01f2271`), one tracked file
(`README.md`, 6 bytes, `# NFL2`), no data, no code, no CI, no site. GitHub Pages was already
configured as a legacy build from `main:/` at `https://kanlerxz87-cyber.github.io/NFL2/`.
There was therefore nothing to inherit, no prior values to preserve, and no existing dataset
to analyse. The complete line-by-line audit is on `repo-review.html`.

## What was delivered

| Deliverable | Contents | Verification |
| --- | --- | --- |
| Live dashboard | Landing page plus subpages grouped into Overview, Decisions, Research, Data, Validation and Governance | Static HTML/CSS/JS, no external dependencies; row-level verifier in CI |
| Requirements register | 52 atomic requirements traced to the verbatim brief | Each requirement row links to the official project repository |
| Decision gates | 17 blocking questions with "have / missing / answer / how to discover" | Official links for every answer; blank + UNVERIFIED where unknown |
| Suggestions | 5 improvement paths + 10 usability suggestions + a path chooser and decision record | No path implemented; selection is deliberately blank |
| Strategy research | 15 candidate signals across singles, parlays and player-prop combos; leaderboard design | All performance cells blank + UNVERIFIED |
| Validation | 12 gates, 10 correlation pairs, 9-step skill-vs-luck protocol | Official method docs (SciPy, scikit-learn, statsmodels, NIST, Kaggle) |
| Injury tracking | Verified Week 10 injury snapshot (20 rows) and Chiefs First–Fourth depth snapshot (10 rows); tracker schema | Every row links to the official NFL/club page |
| Governance | COORDINATION.md board, source registry, 14 flagged irregularities | Flagged for Review page |

## Most important findings

1. **The NFL does not publish its own betting lines.** NFL.com widgets show odds, spreads and
   totals supplied by official bookmaker partners
   ([NFL Support](https://support.nfl.com/hc/en-us/articles/35869698780564-If-I-place-a-bet-on-NFL-com-or-the-NFL-app-am-I-betting-with-the-NFL)).
   "Originating my own lines" therefore means an independent model line compared with
   licensed market prices. A league-official algorithmic "Predicted Score" exists as a
   Genius Sports product
   ([NFL Support](https://support.nfl.com/hc/en-us/articles/35869771634580-What-is-the-Predicted-Score)).
2. **No numeric results can be honestly reported.** There is no licensed historical odds
   archive, play-by-play archive, or strategy result in this repository. Correlation values,
   ROI, Brier scores and leaderboard scores are **blank and flagged UNVERIFIED**. The methods
   for computing them are fully specified, with official documentation links.
3. **Injury tracking has three distinct layers, not one.** The weekly injury report
   ([NFL](https://www.nfl.com/injuries/league/2026/REG10)), club depth charts labelled
   "Unofficial Depth Chart" ([Chiefs](https://www.chiefs.com/team/depth-chart)), and the
   definitive Game Day Administration Report / inactive list at the 90-minute officiating
   meeting ([NFL Football Operations](https://operations.nfl.com/game-operations-logistics/preparation-safety/game-and-stadium-prep)).
4. **Parlay correlation is a rule, not just a statistic.** Approved operator house rules
   prohibit related-outcome parlays and treat same-game parlays as a separately priced
   product ([Massachusetts Gaming Commission](https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf)).
   NFL integrity policy additionally prohibits wagers tied to injuries/officiating
   ([NFL.com](https://www.nfl.com/news/nfl-draftkings-fanduel-fanatics-sports-betting-partners)).
5. **A credible competition already exists as a template.** The NFL Big Data Bowl uses club
   analysts as judges, a $100,000 prize pool, explicit `[PASS/FAIL]` standards and a
   public/private leaderboard split
   ([NFL Football Operations](https://operations.nfl.com/programs-initiatives/innovation/big-data-bowl),
   [Kaggle](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027),
   [Kaggle docs](https://www.kaggle.com/docs/competitions)).

## Decisions that must be made before implementation

The 17 blocking questions on `decisions.html` are unresolved where no official answer
exists. The four that gate everything else are: the definition of "line" (D02), the source and
licence for historical prices (D04), whether injury signals are executable under league
integrity rules (D05), and the legal jurisdiction for rewards (D07). Suggestions for
discovering each missing item are recorded next to the question.

## Recommended path

Path **A** (lock the evidence layer) then **B** (answer the blocking questions) are the
lowest-effort, highest-impact steps. Path **D** (licensed data) is the only route to real
correlation values and leaderboard scores, and it is currently blocked. The reviewer chooses
a path on `suggestions.html`; no implementation begins before that choice is recorded.

## Irregularities

Fourteen items are published on **Flagged for Review** with official source links. They do
not block the build or the merge. The most material are F01 (no official NFL lines), F02
(no licensed dataset), F03 (unofficial depth charts) and F13 (unresolved jurisdiction).

## Responsible-use note

This site documents research and a validation framework only. It places no wagers, handles
no money, and offers no betting advice. Legal sports betting is age- and
jurisdiction-restricted; help resources are at the
[National Council on Problem Gambling](https://www.ncpgambling.org/).
