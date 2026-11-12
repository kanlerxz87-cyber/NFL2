# Decision prerequisites — questions, information, answers (T04)

**Rule:** a decision is permitted only when every blocking question in its row has an answer
that comes from a fetch-verified official source. Where no official answer exists, the
"Answer" and "Missing" cells are **blank** and the row is flagged `UNVERIFIED / BLOCKING`.
Suggestions for discovering the missing information are in the last column. The full,
filterable version is `decisions.html`.

## What we already have (verified)

| ID | Information we HAVE | Official source |
| --- | --- | --- |
| H01 | Official Week 10 2026 injury report with per-player position, injury, practice status and game status | https://www.nfl.com/injuries/league/2026/REG10 |
| H02 | Official definitions: Questionable = uncertain; Doubtful = unlikely; Out = will not play; practice report = DNP / Limited / Full | https://www.nfl.com/news/competition-committee-approves-revisions-to-injury-report-0ap3000000688693 |
| H03 | Official 2026 standings, player stats categories, 2026 schedule and game-center team metrics | https://www.nfl.com/standings/league/2026/REG |
| H04 | Official 2026 club roster and a club-published depth chart with First / Second / Third / Fourth columns | https://www.chiefs.com/team/depth-chart |
| H05 | Official 90-minute Game Day Administration Report containing the inactive list | https://operations.nfl.com/game-operations-logistics/preparation-safety/game-and-stadium-prep |
| H06 | NFL.com odds widgets are partner-supplied, not NFL-originated lines | https://support.nfl.com/hc/en-us/articles/35869698780564-If-I-place-a-bet-on-NFL-com-or-the-NFL-app-am-I-betting-with-the-NFL |
| H07 | A "Predicted Score" exists as a Genius Sports algorithm over historical/season data | https://support.nfl.com/hc/en-us/articles/35869771634580-What-is-the-Predicted-Score |
| H08 | Official NFL tracking data / Next Gen Stats and 2026 metric families | https://nextgenstats.nfl.com/ |
| H09 | Official Big Data Bowl judged competition with a $100,000 prize pool and a public/private leaderboard model | https://operations.nfl.com/programs-initiatives/innovation/big-data-bowl |
| H10 | Approved operator house rules prohibit related-outcome parlays and define same-game-parlay settlement | https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf |
| H11 | NFL integrity policy prohibits wagers tied to injuries/officiating and bets knowable in advance | https://www.nfl.com/news/nfl-draftkings-fanduel-fanatics-sports-betting-partners |
| H12 | Official statistics methods for correlation, proper scoring and multiple-test correction | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html |

## What we do NOT have (blank + UNVERIFIED)

Historical odds (open/close), historical player-prop prices, a licensed play-by-play archive,
per-snap participation counts, archived weekly injury reports, archived inactive lists,
official depth-chart history, market hold/vig per book, correlation coefficients, out-of-sample
strategy results, reward budget, and the project owner's legal jurisdiction. No official
source for any of these was fetch-verified, so no value is recorded.

## Blocking questions

| ID | Question | Answer (official only) | Missing information | Decision blocked | Suggestion to discover missing information |
| --- | --- | --- | --- | --- | --- |
| D01 | Does the NFL publish its own betting lines? | No — NFL widgets show partner odds, spreads and totals | — | Whether "own lines" means a self-computed model | Compare model lines with partner lines documented at the source; record the definition in a decision record |
| D02 | What exactly is a "line" for this project (spread, total, moneyline, prop)? |  |  | Model target definition | Enumerate target markets from an official licensed operator's market list before writing code |
| D03 | Which seasons/weeks form the training and holdout sets? |  |  | Any backtest | Use official schedule archives to fix seasons, then pre-register cut-offs before seeing outcomes |
| D04 | Where will time-stamped opening and closing market prices come from, with what licence? |  |  | Closing-line value, ROI, all strategy scores | Request an official data-licence route via the league's official data distributor; record licence terms |
| D05 | Are injury/lineup signals executable given NFL integrity restrictions? |  |  | Injury-based strategy deployment | Confirm permitted markets with a licensed operator; exclude prohibited markets from the leaderboard |
| D06 | Are club depth charts authoritative enough to define "2nd/3rd/4th string"? | No — the club labels its chart "Unofficial Depth Chart" | — | Whether to treat depth rank as a verified fact | Combine club chart with the official game-day inactive list and snap counts; keep both with timestamps |
| D07 | Which jurisdiction and legal structure govern the reward competition? |  |  | Rewards, live-money features | Obtain a written compliance determination from the relevant regulator before enabling rewards |
| D08 | What is the reward budget and who funds it? |  |  | Reward tiers | Adopt a non-cash recognition-only leaderboard until a budget is approved; mirror the official BDB structure |
| D09 | What is the minimum sample size and significance threshold for a "skill" claim? |  |  | Passing any validation gate | Pre-register alpha, power and minimum N; use multiple-testing correction from the official statsmodels method |
| D10 | What correlation values exist between signals? |  |  | Parlay / prop-combo pricing | Compute Pearson/Spearman on the licensed dataset with bootstrap confidence intervals; publish blank until then |
| D11 | Are same-game prop combos actually offered at the target operator? |  |  | Prop-combo strategies | Read the operator's approved house rules for the exact jurisdiction; record permitted leg combinations |
| D12 | How will injuries, inactives and depth changes be ingested automatically? |  |  | Injury tracker build | Define a polling schedule against the official injury report, club charts and 90-minute inactive list |
| D13 | Which official source is the settlement authority for each market? |  |  | Grading results | Use official league results and the operator's approved house rules; store the URL per graded event |
| D14 | What does "remove luck" mean operationally? |  |  | Leaderboard ranking | Define skill as out-of-sample, calibration-positive, multiple-test-corrected edge over a null strategy |
| D15 | Is a public leaderboard alone sufficient? | No — public leaderboard scores can overfit; a private holdout is required | — | Competition design | Use public/private leaderboard split as documented by the official competition host |
| D16 | Does the repo contain any prior data or code to preserve? | No — base commit contained only a 6-byte README | — | Migration planning | None needed; the audit is complete |
| D17 | Will GitHub Pages build from `main:/` after merge? |  |  | Publishing | Confirm build via the official Pages API and fetch the live URL after merge; retry on failure |

## Answer policy

Answers above are copied only from fetch-verified official pages. Blank answer cells are
intentional: **no inference, no estimate, no "typical" value**. A decision whose row has a
blank answer is `BLOCKING` and must not be implemented until the discovery suggestion is
completed and an official source is recorded in `research/source-registry.json`.
