# Official source registry (T02)

**Session:** `session-01b698ef` · **Verified:** 2026-11-12 (UTC)

## Verification rule used

A URL is added to the registry only when it was opened with a page-fetch tool and the
returned title/content matched the recorded excerpt. The machine-readable registry is
[`source-registry.json`](../research/source-registry.json). The site generator and
`tools/verify.py` both read that file; no table row may cite an ID that is not marked
`fetch-verified` (or `local-git-verified` for local repository facts).

"Official" here means the first-party domain of the entity that owns the fact:
`nfl.com`, `operations.nfl.com`, `nextgenstats.nfl.com`, `support.nfl.com`, club sites
such as `chiefs.com`, government/regulator sites such as `massgaming.com`, the official
documentation domains `docs.github.com`, `docs.scipy.org`, `scikit-learn.org`,
`statsmodels.org`, `itl.nist.gov`, and the official competition host `kaggle.com`.
Third-party blogs, aggregators, tip sites and search snippets are never used as sources
for values.

## Registry (fetch-verified)

| ID | Official URL | Fetched title | Status |
| --- | --- | --- | --- |
| S01 | https://www.nfl.com/injuries/league/2026/REG10 | Official NFL Injury Report for Players – Week 10 of the 2026 Season | fetch-verified |
| S02 | https://www.nfl.com/news/competition-committee-approves-revisions-to-injury-report-0ap3000000688693 | Competition Committee approves revisions to injury report | fetch-verified |
| S03 | https://www.nfl.com/standings/league/2026/REG | 2026 NFL League Standings | fetch-verified |
| S04 | https://www.nfl.com/stats/player-stats/ | NFL 2026 Player Stats | fetch-verified |
| S05 | https://www.nfl.com/schedules | NFL Schedules 2026 | fetch-verified |
| S06 | https://www.nfl.com/teams/new-england-patriots/roster | New England Patriots 2026 Player Roster | fetch-verified |
| S07 | https://www.nfl.com/games/commanders-at-giants-2026-reg-10?tab=overview | Commanders at Giants 2026 REG 10 Game Center | fetch-verified |
| S08 | https://nextgenstats.nfl.com/ | NFL Next Gen Stats | fetch-verified |
| S09 | https://www.nfl.com/news/next-gen-stats-new-advanced-metrics-you-need-to-know-for-the-2026-nfl-season | Next Gen Stats: new advanced metrics for 2026 | fetch-verified |
| S10 | https://operations.nfl.com/rules-officiating/2026-nfl-rulebook | 2026 NFL Rulebook | fetch-verified |
| S11 | https://operations.nfl.com/programs-initiatives/innovation/big-data-bowl | Big Data Bowl (NFL Football Operations) | fetch-verified |
| S12 | https://www.kaggle.com/competitions/nfl-big-data-bowl-2027 | NFL Big Data Bowl 2027 | fetch-verified |
| S13 | https://www.kaggle.com/docs/competitions | Kaggle: Competitions (leaderboard / leakage) | fetch-verified |
| S14 | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html | SciPy `pearsonr` | fetch-verified |
| S15 | https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html | scikit-learn `brier_score_loss` | fetch-verified |
| S16 | https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html | statsmodels `multipletests` | fetch-verified |
| S17 | https://www.itl.nist.gov/div898/handbook/ | NIST/SEMATECH e-Handbook of Statistical Methods | fetch-verified |
| S18 | https://www.nfl.com/news/nfl-draftkings-fanduel-fanatics-sports-betting-partners | NFL sports-betting partnerships / integrity | fetch-verified |
| S19 | https://www.nfl.com/news/nfl-increases-gambling-policy-education-integrity-monitoring-efforts-following-successful-offseason | NFL gambling policy education | fetch-verified |
| S20 | https://support.nfl.com/hc/en-us/articles/35869698780564-If-I-place-a-bet-on-NFL-com-or-the-NFL-app-am-I-betting-with-the-NFL | NFL Support: odds widgets are partner odds | fetch-verified |
| S21 | https://support.nfl.com/hc/en-us/articles/35869771634580-What-is-the-Predicted-Score | NFL Support: Predicted Score / Genius Sports | fetch-verified |
| S22 | https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf | BetMGM MA House Rules (Massachusetts Gaming Commission) | fetch-verified |
| S23 | https://www.chiefs.com/team/depth-chart | Kansas City Chiefs Unofficial Depth Chart | fetch-verified |
| S24 | https://operations.nfl.com/game-operations-logistics/preparation-safety/game-and-stadium-prep | NFL Game and Stadium Prep / 90-minute meeting | fetch-verified |
| S25 | https://www.nfl.com/news/nfl-emergency-third-quarterback-rule-questions-and-answers | NFL emergency third-quarterback rule Q&A | fetch-verified |
| S26 | https://operations.nfl.com/game-operations-logistics/preparation-safety/game-ops-manual | NFL Game Ops Manual | fetch-verified |
| S27 | https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages | What is GitHub Pages? | fetch-verified |
| S28 | https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site | Configuring a publishing source | fetch-verified |
| S29 | https://github.com/kanlerxz87-cyber/NFL2 | This repository (local git inspection) | local-git-verified |
| S30 | https://www.ncpgambling.org/ | National Council on Problem Gambling | fetch-verified |
| S32 | https://www.nfl.com/injuries/ | Official Latest NFL Injury Report | fetch-verified |
| S36 | https://www.chiefs.com/team/depth-chart | Chiefs defensive depth (same page, separate excerpt) | fetch-verified |

## Discovered but deliberately NOT used as evidence

| ID | URL | Reason |
| --- | --- | --- |
| S33 | https://www.nfl.com/standings/tiebreakingprocedures | Linked from official standings but content not fetched; link-only. |
| S34 | https://www.nfl.com/news/nfl-announces-agreements-with-four-approved-sportsbook-operators | Appeared in a search snippet only; not fetch-verified. |
| S35 | https://media.nfl.com/LSB | Linked from an official NFL.com article; content not fetched. |

## Third-party material explicitly excluded

Search results contained many betting blogs, injury-probability tables, "play rate
percentages" and parlay guides. None are official sources, so **no numeric value from
any of them was used**. Where a value would have come from such a source, the site shows
a blank cell and an `UNVERIFIED` flag instead.
