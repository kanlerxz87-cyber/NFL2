# Data Dictionary
> Every file, every column, the transform applied to it, and the source id it inherits — so a reader can re-derive any cell on this site from the official page.

All files are pipe-delimited CSV with a header row. The generator enforces the field count per row: a row that does not match the header width fails the build. That check found six shifted rows in this dataset while the site was being assembled, which is the only reason to trust it.

## Files

| File | Rows | Grain | Source of record |
| --- | --- | --- | --- |
| `data/injuries_2026_wk10.csv` | 254 | one player × game × filing | S-INJ |
| `data/depth_changes_2026_wk10.csv` | 227 | one roster or availability event per club | S-ROUNDUP, S-DARNOLD, S-WILLIS, S-JACKSON, S-NOV5, S-NOV6, S-HUNTLEY |
| `data/standings_2026.csv` | 32 | club × season-to-date | S-STAND |
| `data/schedule_2026_wk10.csv` | 14 | game | S-WK10REP |
| `data/sources.csv` | {{metric sources}} | source | — |
| `data/requirements.csv` / `questions.csv` / `suggestions.csv` / `flags.csv` | 40 / {{metric questions}} / {{metric suggestions}} / {{metric flags}} | register rows | S-BRIEF, S-DESIGN, S-REPO |
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
| `data/reverification_c3ec1487.csv` | 12 | one check performed against a live official page on 2026-11-13, with its outcome | S-STAND-1113, S-SCORES-1113, S-WK11-1113, S-INJ-1113 |

| `data/price_archive_a392.csv` | 5 | one price-bearing asset in the repository, what it proves and what it does not | S-NFLDATA-ARCHIVE, S-NFLDATA-SCHEMA |
| `data/code_collision_a392.csv` | 2 | one cross-source join, how many games it silently dropped with and without the alias table | S-NFLDATA-ARCHIVE |
| `data/deficiency_by_club_a392.csv` | 78 | club × side of the ball, counts off the official filing | S-INJ-2235 |
| `data/deficiency_chains_a392.csv` | 22 | one unavailable player at a club whose depth chart this build transcribes, with the club's own next man up | S-DEPTH-SEA, S-DEPTH-LAR, S-INJ-2235 |
| `data/computed_luck.csv` | 8 | bet count × probability of being ahead at four win rates — arithmetic, not data | S-CALC |
| `data/computed_sample_sizes.csv` | 5 | one win-probability case × the sample size each gate assumes | S-CALC |
| `data/computed_vig.csv` | 5 | one price pair × implied probability, overround and the no-vig line | S-CALC |
| `data/computed_parlays.csv` | 10 | one parlay construction × joint probability under independence and under a modelled coupling | S-CALC |

### Grains introduced by the origination lab

| Column pattern | Meaning | Rule |
| --- | --- | --- |
| `*_mae`, `*_gap_pts` | mean absolute error, in points, against the final score | smaller is better; a line is rounded to a half point so a push cannot occur; computed only on games where the comparison exists, and the paired rows are the ones scored on identical slates |
| `rho`, `ci_low`, `ci_high`, `spans_zero` | measured correlation and its 4,000-resample percentile bootstrap interval, seeded | `spans_zero: yes` means the data cannot distinguish the pair from uncorrelated; nothing downstream may treat such a row as a signal |
| `p_a`, `p_b`, `joint_observed`, `joint_independent`, `price_error_pct` | parlay arithmetic on two binary legs | the percentage is how wrong a ticket priced on the product of the marginals is, against the observed joint |
| `did_not_practise`, `limited`, `designated_out` by `side` | counts off the official filing, offence and defence kept separate | a zero here means the club filed nobody, which the hub also renders as "No Injuries Reported"; it is never read as healthy (FL-01) |
| `string`, `next_man_up` | the club's own column order on its published chart | asserted only where the club's chart and the league's filing both speak; otherwise `not published` |


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
