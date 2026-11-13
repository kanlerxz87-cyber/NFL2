# Data Dictionary
> Every file, every column, the transform applied to it, and the source id it inherits — so a reader can re-derive any cell on this site from the official page.

All files are pipe-delimited CSV with a header row. The generator enforces the field count per row: a row that does not match the header width fails the build. That check found six shifted rows in this dataset while the site was being assembled, which is the only reason to trust it.

## Files

| File | Rows | Grain | Source of record |
| --- | --- | --- | --- |
| `data/injuries_2026_wk10.csv` | 254 | one player × game × filing | S-INJ |
| `data/depth_changes_2026_wk10.csv` | 227 | one roster or availability event per club | S-ROUNDUP, S-DARNOLD, S-WILLIS, S-JACKSON, S-NOV5, S-NOV6, S-HUNTLEY |
| `data/standings_2026.csv` | 32 | club × season-to-date, with read timestamp per row | [NFL.com standings](https://www.nfl.com/standings/) (`S-STAND-653B`) |
| `data/standings_recheck_20261113.csv` | 32 | independent transcription of the 2026-11-13T12:53Z official read, used by `tools/verify.py` to compare all eight published standings fields against the current table | [NFL.com standings](https://www.nfl.com/standings/) (`S-STAND-653B`) |
| `data/schedule_2026_wk10.csv` | 14 | game | S-WK10REP |
| `data/sources.csv` | {{metric sources}} | source | — |
| `data/requirements.csv` / `questions.csv` / `suggestions.csv` / `flags.csv` | {{metric requirements}} / {{metric questions}} / {{metric suggestions}} / {{metric flags}} | register rows | S-BRIEF, S-DESIGN, S-REPO |
| `data/games_2026_wk1_9.csv` | {{metric games_log}} | completed results, weeks 1–9, imported from the parallel session and re-audited here | S-GAMES26 |
| `data/gates.csv` / `signals.csv` / `strategies.csv` / `correlation.csv` / `leaderboard.csv` | {{metric gates}} / {{metric signals}} / {{metric strategies}} / {{metric correlation}} / 14 | design rows | S-DESIGN |
| `data/computed_fair_lines.csv` | 14 | one Week 10 fixture; stages 1–2 of the origination pipeline | S-CALC |
| `data/computed_correlation.csv` | 2 | one pair class with a measured Pearson r | S-CALC |
| `data/computed_depth_reach.csv` | 18 | one position group where the 1st string is unavailable, for charted clubs | S-CALC |
| `data/computed_vig.csv` / `computed_parlays.csv` / `computed_sample_sizes.csv` / `computed_luck.csv` | 5 / 10 / 5 / 8 | closed-form exhibits, no market data | S-CALC |
| `data/build_manifest.json` | — | build output, counts, allowlist | generated |
| `data/injuries_wk10_2026_hubrefresh.csv` | 279 | one player × club, re-read from the hub at 22:35Z, side of the ball assigned from the league's own position code | S-INJ-2235 |
| `data/injury_delta_a392.csv` | 40 | one row that appeared, disappeared or changed between the 04:45Z and 22:35Z official reads | S-INJ, S-INJ-2235 |
| `data/reverification_a392.csv` | 9 | one check performed against the live official page, with its outcome | S-STAND-2235, S-INJ-2235 |
| `data/ratings_2026_a392.csv` | 32 | club × season-to-date, fitted coefficients and the Pythagorean luck residual | S-GAMES26 |
| `data/model_backtest_2026_a392.csv` | 6 | evaluation week × market (spread, total), our error against a baseline and the archived price | S-GAMES26, S-NFLDATA-ARCHIVE |
| `data/model_verdict_2026_a392.csv` | 14 | one headline metric, its value, the method that produced it, and the read | S-CALC-A392 |
| `data/measured_correlations_a392.csv` | 8 | one measured pair (rho or phi) with a seeded bootstrap interval and parlay arithmetic | S-GAMES26 |
| `data/rest_and_hfa_2026_a392.csv` | 3 | rest bucket × mean home margin, the decomposition behind M-05 | S-GAMES26 |
| `data/originated_lines_wk10_a392.csv` | 14 | Week 10 fixture × our line, the archived line where one exists, availability load by side | S-GAMES26, S-NFLDATA-ARCHIVE |
| `data/games_2026_wk10_played.csv` | 1 | Week 10 game whose result is official. Append-only: the weeks 1–9 backtest corpus is deliberately left byte-identical so no existing grade is re-baselined (S-26) | S-SCORES-1113, S-GAME-W1001 |
| `data/settled_wk10_5f16dcc6.csv` | 4 | settled game × predictor: the published line, the official result, and the absolute error of each | S-CALC-5F16 |
| `data/computed_settled_5f16dcc6.csv` | 17 | one derived metric, its value, the method that produced it, and the read | S-CALC-5F16 |
| `data/reverification_5f16dcc6.csv` | 13 | one check performed against a live official page on 2026-11-13, with its outcome | S-STAND-1113, S-SCORES-1113, S-WK11-1113, S-INJ-1113 |
| `data/schedule_week11_2026.csv` | 13 | one Week 11 fixture: date, kickoff, broadcaster, neutral-site flag and the official game URL | S-WK11-0A11 |
| `data/originated_lines_wk11_0a113a24.csv` | 13 | one pre-registered Week 11 line: our spread and total, the model inputs beside them, and the non-official archive line it is compared against | S-CALC-0A11 |
| `data/prereg_week11_0a113a24.csv` | 15 | one field of the pre-registration record: the decision timestamp, the SHA-256 of every artefact it covers, and what each one means | S-PREREG-0A11 |
| `data/forward_grade_0a113a24.csv` | 13 | one pre-registered line against the official final score, with the do-nothing baseline error beside it | S-CALC-0A11 |
| `data/forward_grade_summary_0a113a24.csv` | 10 | one derived metric of the forward grade: the hash checks, the settled count and the sample-size arithmetic | S-CALC-0A11 |
| `data/games_week11_played.csv` | 0 | Week 11 game whose result is official. Append-only, like the Week 10 results file; empty until the games are played | S-SCORES-0A11 |
| `data/week11_broadcaster_change_0a113a24.csv` | 2 | one fixture whose broadcaster moved between the league's dated announcement and the live schedule page | S-WK11-0A11 |
| `data/reverification_0a113a24.csv` | 102 | one check performed against a live official page on 2026-11-13, with its outcome | S-STAND-0A11, S-WK11-0A11, S-WK10, S-SCORES-0A11, S-INJ |
| `data/availability_watch_c3ec1487.csv` | 296 | one player × club × game, transcribed from the official injury hub on 2026-11-13T12:45Z | [https://www.nfl.com/injuries/](https://www.nfl.com/injuries/) |
| `data/availability_watch_by_club_c3ec1487.csv` | 28 | one club on the Week 10 slate: practice-code tallies, designations, and the two cells no official source can fill | [https://www.nfl.com/injuries/](https://www.nfl.com/injuries/) |
| `data/availability_watch_movement_c3ec1487.csv` | 5 | what changed between the 2026-11-12 and 2026-11-13 reads of the hub | [https://www.nfl.com/injuries/](https://www.nfl.com/injuries/) |
| `data/availability_watch_practice_deltas_c3ec1487.csv` | 49 | one player whose practice code changed between the two dated reads, and the direction | [https://www.nfl.com/injuries/](https://www.nfl.com/injuries/) |
| `data/availability_watch_gates_c3ec1487.csv` | 4 | one availability readiness gate, its measured value, and why it passes or fails | [https://www.nfl.com/injuries/](https://www.nfl.com/injuries/) |
| `data/computed_availability_watch_c3ec1487.csv` | 12 | one derived availability metric, how it is computed, and what it means | S-CALC |
| `data/reverification_c3ec1487.csv` | 13 | one check performed against a live official page on 2026-11-13, with its outcome | S-STAND-1113, S-SCORES-1113, S-WK11-1113, S-INJ-1113 |

| `data/price_archive_a392.csv` | 5 | one price-bearing asset in the repository, what it proves and what it does not | S-NFLDATA-ARCHIVE, S-NFLDATA-SCHEMA |
| `data/code_collision_a392.csv` | 2 | one cross-source join, how many games it silently dropped with and without the alias table | S-NFLDATA-ARCHIVE |
| `data/deficiency_by_club_a392.csv` | 78 | club × side of the ball, counts off the official filing | S-INJ-2235 |
| `data/deficiency_chains_a392.csv` | 22 | one unavailable player at a club whose depth chart this build transcribes, with the club's own next man up | S-DEPTH-SEA, S-DEPTH-LAR, S-INJ-2235 |
| `data/injuries_wk10_83246f00.csv` | {{metric pr_hub_rows}} | one player-filing on the official Week 10 hub, read 2026-11-13T12:46Z. Its own file, because the 04:45Z and 22:35Z snapshots are the only record of what the hub said then | S-INJ-1246 |
| `data/depth_charts_wk10_83246f00.json` | {{metric pr_charts}} clubs | one club's own published Unofficial Depth Chart, offence and defence, in the club's own left-to-right order, with the chart URL and the date the club prints on it | S-DEPTH-WAS, S-DEPTH-NYG, S-DEPTH-NE, S-DEPTH-DET, S-DEPTH-KC, S-DEPTH-GB, S-DEPTH-MIA, S-DEPTH-SEA, S-DEPTH-BAL, S-DEPTH-LAC |
| `data/personnel_relief_wk10_83246f00.csv` | {{metric pr_rows}} | one listed player × his string on his club's chart × the next man the club names × his unit's published order matched rung by rung against the report | S-INJ-1246, S-DEPTH-* |
| `data/personnel_relief_club_83246f00.csv` | {{metric pr_club_rows}} | club × side of the ball: how many listed players resolved to a string, how many 1st-string players did not practise, and the join state | S-INJ-1246, S-DEPTH-* |
| `data/reverification_83246f00.csv` | 13 | one check performed against a live official page on 2026-11-13 by session 83246f00, with its outcome | S-STAND-1113, S-SCORES-1113, S-INJ-1246, S-DEPTH-* |

| `data/depth_cascades_6539b6a0.csv` | 139 | one named player per depth cascade, placed against his club's own chart and the official Week 10 report | S-DEPTH-BAL, S-DEPTH-MIA, S-DEPTH-ARI, S-DEPTH-NE, S-DEPTH-DET, S-DEPTH-SF, S-DEPTH-DAL, S-DEPTH-SEA, S-DEPTH-LAR, S-DEPTH-GB, S-DEPTH-WAS, S-DEPTH-NYG, S-INJ-REG10 |
| `data/depth_cascade_verdicts_6539b6a0.csv` | 18 | one depth cascade, with a verdict computed from its player rows | as above |
| `data/computed_luck.csv` | 8 | bet count × probability of being ahead at four win rates — arithmetic, not data | S-CALC |
| `data/computed_sample_sizes.csv` | 5 | one win-probability case × the sample size each gate assumes | S-CALC |
| `data/computed_vig.csv` | 5 | one price pair × implied probability, overround and the no-vig line | S-CALC |
| `data/computed_parlays.csv` | 10 | one parlay construction × joint probability under independence and under a modelled coupling | S-CALC |

| `data/club_availability_20261113_66faefac.csv` | 28 | club × the 13 November hub read: rows published, D/L/F split, designations, the load the locked rule consumes, and the same club's counts at the 04:45Z and 22:35Z reads with the delta | S-HUB-1113 |
| `data/hub_flagged_20261113_66faefac.csv` | 17 | one named player: the nine game designations plus the non-participants at the four clubs whose chart this build transcribes, with the hub's practice code | S-HUB-1113 |
| `data/hub_club_counts_20261113_66faefac.csv` | 28 | one club block as the page displayed it, before any derivation - the hand-transcription input the tool re-totals against | S-HUB-1113 |
| `data/availability_deficiency_66faefac.csv` | 18 | one unavailable player × the column he holds in the club's own printed order, the next man up, and how many bodies are left in that group | S-HUB-1113, S-DEPTH-KC, S-DEPTH-GB, S-DEPTH-NE, S-DEPTH-DET |
| `data/prereg_wk10_66faefac.csv` | 14 | one Week 10 fixture × the locked decision: load by side, differential, call or no-call, our line, stake zero, with the decision timestamp | S-HUB-1113, S-CALC |
| `data/prereg_sensitivity_66faefac.csv` | 6 | one threshold × how many fixtures the same rule would call; only the 4 row was registered, the rest are context | S-CALC |
| `data/reverification_66faefac.csv` | 24 | one check performed against a live official page on 13 November, with its outcome, including 4 `NOT CHECKED` and 3 `MISMATCH` rows | S-HUB-1113, S-STAND-1113B, S-SCHED10-1113, S-SCHED11-1113B, S-SCORES-1113B |

### Session 745f788e — all-club depth register and decision console

| File | Rows | Grain | Source of record |
| --- | --- | --- | --- |
| `data/s745_depth_charts.csv` | 1558 | one printed slot on one club's own published depth chart: club × unit × position group × depth (1st–4th string) × player | S-DEPTH-745 |
| `data/s745_depth_deficiencies.csv` | 705 | club × unit × position group: the starter the club prints, his official practice and game status, who is next, and how deep the club has to reach | S-DEPTH-745, S-INJ-1113 |
| `data/s745_depth_summary.csv` | 32 | club × availability roll-up, with the club's own chart page on every row | S-DEPTH-745 |
| `data/s745_injury_refresh.csv` | 298 | one player × club, re-read from the official injury hub at 2026-11-13T12:45Z, plus 2 explicit "No Injuries Reported" markers | S-INJ-1113 |
| `data/s745_suggestion_scores.csv` | 64 | one suggestion from `suggestions.csv`, scored on that register's own impact/effort/risk fields and assigned to a candidate path | S-REGISTER-745 |
| `data/s745_decision_paths.csv` | 4 | one candidate path: the suggestion ids in it, what it unblocks, what it does not fix, and its first milestone | S-REGISTER-745 |
| `data/s745_information_gaps.csv` | 54 | one question from `questions.csv`, restated as have / lack / how-to-close | S-REGISTER-745 |

Rules these seven files obey, all of them re-checked by `scripts/verify_s745.py`:

* **Depth comes from the club, status comes from the league.** No row mixes the two. The chart
  column cites the club's own page; the injury columns cite `nfl.com/injuries`. The league
  publishes no central depth chart — `nfl.com/teams/<club>/depth-chart` returns 404 (FL-05) — so
  a club's own site is the only official chart that exists for it, and it is registered as tier B
  (official club, not league-operated) rather than passed off as tier A.
* **`depth` is 1–4 and is what the club printed.** Where a club prints two names in one column,
  both are recorded at that depth; the join does not pick a winner. Where a club prints nothing,
  there is no row at all, because an absent cell on an official page is not a player.
* **`projected_starter` and `starter_injury_name` are different columns on purpose.** The first
  is what the club's chart prints; the second is what the league's report prints for the same
  man (`Kevin Byard III` against `Kevin Byard`). Keeping both is what lets `verify_s745.py`
  re-check every matched starter instead of trusting a normaliser.
* **`starter_availability_tier`** is one of `not on report`, `full`, `limited`,
  `did not practice`, `out`. `not on report` means the league's page does not list him — a
  different fact from healthy, and never rendered as healthy (FL-01).
* **`depth_reached`** counts from 1. A value of 2 means the club's 1st string is out and the 2nd
  string starts; nothing in this file reaches 3 or 4 this week. It is **blank** where the club
  prints no first string at all — promoting the second line into a "next man up" would be an
  inference about a starter the club never published (2 groups this week).
* **`official_route_exists` = `not established`** is a keyword-match miss over the register's
  own prose, not a claim that no route exists. The word `unknown` is banned in this repository's
  data files, and rightly so — a cell reading `unknown` usually means a value somebody should
  have gone and found.
* **The scoring files add no facts.** They re-arrange fields the registers already publish. The
  `priority_score` column is arithmetic (`impact / (effort + risk)`), and the page that publishes
  it says so in those words.

### Grains introduced by the origination lab

| Column pattern | Meaning | Rule |
| --- | --- | --- |
| `*_mae`, `*_gap_pts` | mean absolute error, in points, against the final score | smaller is better; a line is rounded to a half point so a push cannot occur; computed only on games where the comparison exists, and the paired rows are the ones scored on identical slates |
| `rho`, `ci_low`, `ci_high`, `spans_zero` | measured correlation and its 4,000-resample percentile bootstrap interval, seeded | `spans_zero: yes` means the data cannot distinguish the pair from uncorrelated; nothing downstream may treat such a row as a signal |
| `p_a`, `p_b`, `joint_observed`, `joint_independent`, `price_error_pct` | parlay arithmetic on two binary legs | the percentage is how wrong a ticket priced on the product of the marginals is, against the observed joint |
| `did_not_practise`, `limited`, `designated_out` by `side` | counts off the official filing, offence and defence kept separate | a zero here means the club filed nobody, which the hub also renders as "No Injuries Reported"; it is never read as healthy (FL-01) |
| `string`, `next_man_up` | the club's own column order on its published chart | asserted only where the club's chart and the league's filing both speak; otherwise `not published` |


## Column meanings — standings

| Column | Type | Definition and rule |
| --- | --- | --- |
| `w`, `l`, `t` | count | Wins, losses and ties as published by the NFL; checked against the official [standings page](https://www.nfl.com/standings/). |
| `pct` | decimal | Winning percentage as published; independently recomputed as `(W + 0.5 × T) / (W + L + T)` and checked against the same [NFL standings page](https://www.nfl.com/standings/). |
| `pf`, `pa`, `net` | points | Points for, points against and net points; `net = pf - pa`, checked against the [NFL standings page](https://www.nfl.com/standings/). |
| `streak` | text | Current streak string as published on the [NFL standings page](https://www.nfl.com/standings/). |
| `source` | registry id | Source-register key for the official page read; current rows use `S-STAND-653B`, linked to [NFL.com standings](https://www.nfl.com/standings/). |
| `captured_utc` | ISO-8601 UTC minute | Our read time for that official source, not an NFL publication time. All 32 rows currently record `2026-11-13T12:53Z`; the build checks this against the latest registered source and against all 256 values in the saved official re-read. |

## Column meanings — injury snapshot

| Column | Type | Definition and rule |
| --- | --- | --- |
| `game` | id | fixture key, joins to `schedule_2026_wk10.csv.game_id`; assigned in the order the official page lists games |
| `team` | abbr | league club abbreviation as published (LAR not LA) |
| `player` | text | display name exactly as published, including suffixes ("Gervon Dexter Sr.", "Carlton Davis III", "Deebo Samuel Sr.") |
| `slug` | key | the league's player URL slug, taken from the published href. Not a stable id — collisions carry opaque suffixes ([FL-15](flagged-for-review.html)) |
| `pos` | code | league position string; used only for the offence/defence split below |
| `injury` | text | populated for {{metric injury_detail_cells}} of {{metric injury_rows}} rows because that is what the hub published; never backfilled from prose |
| `practice` | enum | `F` = Full Participation in Practice, `L` = Limited Participation in Practice, `D` = Did Not Participate In Practice |
| `status` | enum | `OUT` = Out, `Q` = Questionable, `D` = Doubtful; empty means no designation had been filed |

### `availability_watch_c3ec1487.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| `game_id` | key | joins to `schedule_2026_wk10.csv.game_id` |
| `club` | abbr | league club abbreviation exactly as the hub prints it |
| `player` | text | display name as published, suffixes included |
| `position` | code | the hub's own position string; not normalised, because normalising is interpretation |
| `injury` | text | the hub's injury cell, verbatim; empty for the majority of rows, and never filled from a news article |
| `practice` | enum | `F` = Full, `L` = Limited, `D` = Did Not Participate In Practice |
| `game_status` | enum | `OUT`, `Q`, `D`, or empty. Empty is the normal state midweek — 287 of {{metric aw_rows}} rows here |
| `captured_utc` | timestamp | the moment the page was read. A row without one is not a dated observation |
| `source` | url | the official page the row was transcribed from |

## Controlled vocabularies

**Position → side of ball** (a project convention used only to split counts; it is our mapping, not the league's):

| Side | Positions |
| --- | --- |
| Offence | QB, RB, FB, WR, TE, T, G, C, OT, OG |
| Defence | DE, DT, LB, OLB, Edge, CB, S, FS, SS, DB, DL |
| Special teams (excluded from both) | K, P, LS |

**Depth-event types** — RULED-OUT, RULED-OUT-WK9, OUT-SEASON, IR, IR-ACTIVATED, IR-RETURN-DESIG, IR-DECISION, DEPTH-CHART, PRACTICE, DNP, NO-DESIGNATION, SIGNING, ROSTER-CUT, TIMELINE, SEASON-IMPACT. A row's `change` value must be one of these; `verify.py` fails on anything else, because an uncategorised event silently disappears from every count.

## Blank policy

An empty field means the official source did not publish it. It renders as `not published`, is excluded from every count and statistic, and never becomes 0, "no" or a plausible default. Cells deliberately filled with the string `not published` (in the correlation and leaderboard tables) mean the same thing, written explicitly because the column is one where a reader would otherwise expect a number.

## Blank census — where the site is honestly empty

{{blank_census}}

<p class="caption">This is not a defect list; it is the shape of what can be claimed. A table with no blanks in a domain like this would be a table someone filled in.</p>
