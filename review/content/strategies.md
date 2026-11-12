# Strategy research — originating lines and generating signals (T06)

## What "originate my own NFL lines" means here

NFL.com itself does **not** publish its own betting lines: its widgets display odds, spreads and
over/under supplied by official bookmaker partners ([official NFL Support](https://support.nfl.com/hc/en-us/articles/35869698780564-If-I-place-a-bet-on-NFL-com-or-the-NFL-app-am-I-betting-with-the-NFL)).
The NFL does publish an algorithmic "Predicted Score" from a Genius Sports model over
historical/season data ([official NFL Support](https://support.nfl.com/hc/en-us/articles/35869771634580-What-is-the-Predicted-Score)).
So "originating my own lines" is defined here as: **compute an independent pre-game
probability/line from official league data, then compare it with a licensed market line.**
A difference is a candidate signal, not an edge. No official source provides our own model
coefficients, so every model output cell is blank + `UNVERIFIED`.

## Official data that can legitimately feed a model

| Input | Official source | Model use | Value availability |
| --- | --- | --- | --- |
| Weekly injury report (position, injury, practice, game status) | https://www.nfl.com/injuries/league/2026/REG10 | Availability / replacement features | current week only, verified |
| Game status definitions | https://www.nfl.com/news/competition-committee-approves-revisions-to-injury-report-0ap3000000688693 | Encode categorical statuses | verified, no probabilities |
| Game Day Administration Report / inactive list at the 90-minute meeting | https://operations.nfl.com/game-operations-logistics/preparation-safety/game-and-stadium-prep | Final availability label | mechanism verified; per-game data not archived here |
| Club depth chart, First–Fourth | https://www.chiefs.com/team/depth-chart | Replacement-depth feature | one club snapshot verified, labelled "unofficial" |
| 2026 standings (W/L/T, PF, PA, net points, home/road, streak) | https://www.nfl.com/standings/league/2026/REG | Team-strength features | verified snapshot |
| Player stat categories (passing, rushing, receiving, tackles, …) | https://www.nfl.com/stats/player-stats/ | Player-prop features | verified snapshot |
| Schedule / game context | https://www.nfl.com/schedules | Rest, travel, kickoff windows | verified snapshot |
| Game-center team metrics (PPG, YPG, TOP, sacks, INT, turnover differential) | https://www.nfl.com/games/commanders-at-giants-2026-reg-10?tab=overview | Matchup features | verified for one game |
| Next Gen Stats tracking metrics | https://nextgenstats.nfl.com/ | Advanced signal features (separation, air distance, time to throw) | verified metric catalogue; bulk data licence unresolved |
| 2026 NGS run-scheme / blocking models | https://www.nfl.com/news/next-gen-stats-new-advanced-metrics-you-need-to-know-for-the-2026-nfl-season | Line-play and run-game features | verified description; data access unresolved |
| Official play-by-play stats (via league data partner) | https://www.nfl.com/news/nfl-draftkings-fanduel-fanatics-sports-betting-partners | Drive/play-level modelling | distribution described; access/licence unresolved |

## Signal inventory (candidate, not validated)

| ID | Bet type | Signal hypothesis | Required data | Correlation value | Edge / ROI | Gate status | Official basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ST01 | Single | Model spread vs market spread divergence | licensed opening/closing lines |  |  | NOT RUN | https://support.nfl.com/hc/en-us/articles/35869698780564-If-I-place-a-bet-on-NFL-com-or-the-NFL-app-am-I-betting-with-the-NFL |
| ST02 | Single | Model total vs market total divergence | licensed totals + official team scoring |  |  | NOT RUN | https://www.nfl.com/standings/league/2026/REG |
| ST03 | Single | Moneyline probability vs implied market probability | licensed moneylines |  |  | NOT RUN | https://www.nfl.com/stats/player-stats/ |
| ST04 | Single | Starting-QB replacement depth (QB2/QB3) vs line movement | depth chart + inactives + lines |  |  | NOT RUN | https://www.chiefs.com/team/depth-chart |
| ST05 | Single | Defensive starter Out + backup depth rank | injury report + depth chart + lines |  |  | NOT RUN | https://www.nfl.com/injuries/league/2026/REG10 |
| ST06 | Single | Offensive line backup chain (2nd/3rd/4th string) vs pass-rush matchup | depth chart + NGS |  |  | NOT RUN | https://www.nfl.com/news/next-gen-stats-new-advanced-metrics-you-need-to-know-for-the-2026-nfl-season |
| ST07 | Single | Rest/travel asymmetry from official schedule | schedule archive |  |  | NOT RUN | https://www.nfl.com/schedules |
| ST08 | Parlay | Cross-game independent-leg parlay after correlation screen | multi-game lines + correlation matrix |  |  | NOT RUN | https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf |
| ST09 | Parlay | Same-game parlay where operator explicitly prices correlation | operator SGP rules + prices |  |  | NOT RUN | https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf |
| ST10 | Parlay | Related-outcome detection to reject non-executable combos | operator rule set |  |  | NOT RUN | https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf |
| ST11 | Prop combo | QB passing overs with WR receiving overs (same game) | player props + participation |  |  | NOT RUN | https://www.nfl.com/stats/player-stats/ |
| ST12 | Prop combo | Backup RB volume when starter is Out | injury report + depth chart + props |  |  | NOT RUN | https://www.nfl.com/injuries/league/2026/REG10 |
| ST13 | Prop combo | Defensive backup exposure → opposing WR props | depth chart + props |  |  | NOT RUN | https://www.chiefs.com/team/depth-chart |
| ST14 | Prop combo | Player participation / void risk screen | operator settlement rules |  |  | NOT RUN | https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf |
| ST15 | All | Null / sham strategy control (random picks, same stake) | outcomes only |  |  | NOT RUN | https://www.kaggle.com/docs/competitions |

Blank numeric cells are deliberate and flagged `UNVERIFIED`. No signal has been scored;
there is no official dataset in this repo on which to score one.

## Leaderboard competition design

The design mirrors the NFL's official crowdsourced analytics competition: NFL club analytics
staff judge submissions, a `$100,000` prize pool is documented, and a public/private
leaderboard split prevents leaderboard-chasing
([NFL Football Operations](https://operations.nfl.com/programs-initiatives/innovation/big-data-bowl),
[Kaggle docs](https://www.kaggle.com/docs/competitions)). The 2027 edition publishes explicit
`[PASS/FAIL]` requirements and weighted evaluation components
([official competition](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027)).

| Element | Proposed rule | Verified official analogue | This project's value |
| --- | --- | --- | --- |
| Eligibility | Strategy must be pre-registered before the holdout window | Kaggle submission limits / rules |  |
| Public leaderboard | In-season sample only | Kaggle public leaderboard definition |  |
| Private leaderboard | Final ranking on untouched holdout | Kaggle private leaderboard definition |  |
| Passing standard | Explicit PASS/FAIL per gate | BDB 2027 evaluation table |  |
| Rewards | Recognition-only until jurisdiction (D07) and budget (D08) are answered | BDB prize structure ($100,000; 2027: Open $45,000, University $45,000, Grand Prize $10,000) |  |
| Integrity | No injury/officiating markets prohibited by league policy | NFL integrity policy |  |
| Harm minimisation | No live-money features; link help resources | NCPG / NFL responsible-betting programme | https://www.ncpgambling.org/ |

This project is not affiliated with or endorsed by the NFL or Kaggle; the official pages are
cited as design references only.
