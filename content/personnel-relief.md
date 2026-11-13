# Personnel Relief — who replaces which starter, by string
> The brief asked the system to know when a club's 2nd, 3rd or 4th-string player has to replace a starter, on offence and on defence. This page is that join, done for every club whose own depth chart could be read from an official page today — and it states, per row, which string each listed player is on, who the club itself names behind him, and how far down that order you can go before you meet another injured player.

Two registers have been in this repository since the first session: the official injury report
(`nfl.com/injuries`), which says **who is hurt**, and each club's own **Unofficial Depth Chart**, which
says **who is behind whom**. Neither one answers the brief's question on its own. A name on the injury
report with no string is a name; a depth chart with no injury report is a depth chart. This page is the
join, and the whole point of it is the third column: **the named replacement's own status**.

## What this page can and cannot claim

| Claim | Status on this page | Why |
| --- | --- | --- |
| This player is listed on the official injury report, with this practice code | **verified**, per row, against `nfl.com/injuries` read at 2026-11-13T12:46Z | it is the hub's own column, transcribed |
| This player is his club's 1st/2nd/3rd/4th string at this position | **verified as the club's own publication**, per row, against the club's chart URL on the row | the club prints the order; we record its position in that order |
| The club names this player behind the starter | **verified**, taken from the next name in the club's own row | no inference from jersey number, contract or draft slot |
| This player will start on Sunday | **not claimed anywhere** | the depth chart is a publication, not a game-day active list, and the report is practice participation |
| This substitution costs the team *n* points | **not claimed anywhere** | that needs playing-time and EPA data we are not entitled to store yet ([Q-02](questions.html)) |
| "No Injuries Reported" means a club is healthy | **refused** ([S-19](suggestions.html)) | the string is the hub's own sentence, not a zero |

> **Read the practice code before the string.** A Wednesday "Did Not Participate" is a practice
> status, not a Sunday absence. Five of the eighteen 1st-string non-participants below are *not*
> designated Out, and the table says which — a player who does not practise Thursday very often plays
> Sunday. Anything that prices this signal has to clear [G-03](validation-gates.html) (point-in-time
> correctness) first, and nothing here is priced: this is a register, not a line.

## The join, in numbers

| Measure | Value | What it means |
| --- | --- | --- |
| Player-filings on the official hub at this read | {{metric pr_hub_rows}} rows over {{metric pr_hub_clubs}} clubs | the hub grew from 254 rows (12 Nov, morning) to 279 (12 Nov, evening) to this — see [FL-27](flagged-for-review.html) |
| Club depth charts transcribed from the club's own page | {{metric pr_charts}} of 28 clubs playing in Week 10 | S-33 and S-39 named this as the blocking task; it is now {{metric pr_charts}} of 32 clubs, not 32 |
| Listed players that resolve to a string on their own club's chart | {{metric pr_resolved}} of {{metric pr_rows}} | the other {{metric pr_unresolved}} are blank and say so — 18 of 28 clubs have no chart transcribed yet |
| 1st-string players listed on the report | {{metric pr_first_listed}} | a 1st-string listing is not the same as an absence |
| 1st-string players who did **not** practise | {{metric pr_first_dnp}} ({{metric pr_offence_first_dnp}} offence, {{metric pr_defence_first_dnp}} defence) | the brief's exact question, on both sides of the ball |
| 1st-string players actually **designated Out** | {{metric pr_first_out}} | the only ones that are confirmed unavailable, and the column is populated for few of them |
| Position units where **every** player the club names is on the report | {{metric pr_full_unit_units}} | {{metric pr_full_unit_list}} — the deficiency measure, and the reason this page exists |

## The deficiency: units where the replacement is also hurt

This is the finding. For each unit below, the club's published order is listed rung by rung and each
rung is matched against the official report. A unit that runs out of clean players is a genuine depth
problem; a unit whose 1st string is limited but whose 2nd string is clean is a depth problem the club
can absorb, and the table distinguishes them without averaging them together.

**Two units this week have no clean player at any published rung** — {{metric pr_full_unit_list}}:

| Club | Unit | Rung 1 | Rung 2 | What the club itself published | Sources |
| --- | --- | --- | --- | --- | --- |
| NE | LG | Ben Brown — *Did Not Participate* | Walter Rouse — *Limited* | the Patriots list Ben Brown 1st at LG **and** 2nd at C; both of his rungs' occupants are on the report | [patriots.com chart](https://www.patriots.com/team/depth-chart) · [nfl.com/injuries](https://www.nfl.com/injuries/) |
| SEA | LG | Quenton Nelson — *Did Not Participate* | Anthony Bradford — *Limited* | the Seahawks also list Bradford 2nd at RG, so his backup duty is double | [seahawks.com chart](https://www.seahawks.com/team/depth-chart/) · [nfl.com/injuries](https://www.nfl.com/injuries/) |

That is a two-rung deficiency at one guard spot on two clubs in the same week, read off the clubs' own
documents rather than inferred. It is the clearest thing this page produces, and the honest reading of it
is narrow: **both clubs' published interior-line depth is on the report at that spot.** It is not a claim
that either club will lose yards, and no line on this site has been moved for it.

{{csv data/personnel_relief_club_83246f00.csv;;cols=club:Club,side:Side,listed:Listed on report,resolved_to_chart:Resolved to chart,first_string_listed:1st string listed,first_string_dnp:1st string DNP,first_string_designated_out:1st string Out,relief_named:Relief the club names,chart_state:Chart join state;;source_col=chart_url;;filter=first_string_dnp=!0;;caption=One row per club and side of the ball where at least one 1st-string player did not practise on the date read. "Relief the club names" is the club's own next name down, with the string it occupies; where the club lists only one player in the unit the cell is blank rather than filled with a guess. The join-state column is the honesty check: it says how many listed players the club's chart could not resolve, so a row can never look complete when it is not.}}

## Every listed player, with his string

Two clubs in full, chosen because they are the two shapes of the problem: one where a starter is out and
the man behind him is clean, and one where the club's own order runs out. The `Unit cascade` column is the
whole published order for that player's unit in one cell, rung by rung, so a reader sees the club's own
sequence rather than a single row's opinion of it. The complete {{metric pr_rows}}-row table is published
below in the coverage table's place — filtering the whole file is done in the content file, and the
remaining clubs are added as their charts are transcribed.

{{csv data/personnel_relief_wk10_83246f00.csv;;cols=player:Player,pos:Pos,side:Side,practice_word:Practice as filed,game_status:Game status,depth_unit:Unit,string:String,next_man_up:Next man up,unit_cascade:Unit cascade;;source_col=injury_url;;filter=club=SEA;;caption=Seattle first, because it is the sharpest case in the league this week: four 1st-string players did not practise, including the quarterback, and the club's own backup is carrying two injuries of his own. Change the filter in the content file to read any other club.}}

{{csv data/personnel_relief_wk10_83246f00.csv;;cols=player:Player,pos:Pos,side:Side,practice_word:Practice as filed,game_status:Game status,depth_unit:Unit,string:String,next_man_up:Next man up,unit_cascade:Unit cascade;;source_col=injury_url;;filter=club=NE;;caption=New England, because it is the case that puts two rungs on the report at once: the 1st and 2nd-string centres both appear, so the club's own order runs out before it reaches a player the league has not listed. The Patriots also state on the page that their chart is written by team reporters and not by the organisation — recorded on every NE row, because it makes the string a weaker claim than the same slot elsewhere.}}

## The clubs that are not covered, and why that is stated rather than hidden

18 of the 28 clubs playing in Week 10 have no depth chart transcribed here. Every one of their rows
carries `not published` in the string columns and names the club chart it lacks, rather than borrowing a
chart from another club, inferring a string from a roster's line order, or using a third-party depth
chart. The reason is the rule this repository does not bend: a value that cannot be confirmed from an
official page stays blank and is flagged.

{{csv data/personnel_relief_club_83246f00.csv;;cols=club:Club,side:Side,listed:Listed on report,chart_state:Chart join state;;source_col=injury_url;;filter=chart_state=not transcribed;;caption=The uncovered clubs, one row per club and side of the ball. The count is recomputed from the file on every build, so this table cannot go stale the way a hand-written "we cover ten clubs" sentence would.}}

Extending this to the remaining 18 clubs is the single highest-value data task left in the project, and
it is what [S-39](suggestions.html) already asks for. It was not done in this session because each chart
has to be read from the club's own page, the clubs print their positions under different labels (WAS
prints `DL` where SEA prints `DT` and `NT`), and a transcription done at speed is exactly the kind of
work that produces a confident wrong string. Ten clubs, checked rung by rung, is worth more than 28
clubs transcribed in one pass.

## What this changes about the rest of the site

- **[Depth & Deficiencies](depth-impact.html)** previously said the depth rung of a replacement could
  not be stated. That is now true for 18 clubs instead of 28, and this page is where the 10 whose rung
  *can* be stated live. The older page is not rewritten, because its rows are still correct for the
  clubs it covers.
- **[Flagged for Review](flagged-for-review.html)** carries three new flags: the hub's growth since the
  morning read (FL-27 is now a series, not an incident), the club-domain sources being tier B rather
  than tier A (FL-38), and the egress finding that changes the premise of [Q-24](questions.html) (FL-37).
- **The leaderboard does not move.** [SIG-01 and SIG-02](signals.html) are the availability signals this
  join would feed, and every strategy that would use them is still behind
  [G-03](validation-gates.html), because a register of who is hurt is not a point-in-time backtest and
  cannot be one until the hub is stored as a daily series ([S-35](suggestions.html)).

## Method and reproduction

```
python3 tools/compute_personnel_relief_83246f00.py     # rebuilds both tables from the two inputs
python3 tools/build_site.py                            # rebuilds this page
python3 tools/verify.py                                # 13 new checks, including the join's own arithmetic
```

Inputs: `data/injuries_wk10_83246f00.csv` (the hub read, 296 rows, its own file so the two earlier
snapshots survive) and `data/depth_charts_wk10_83246f00.json` (ten club charts, one `https://` URL and
one printed-date label each). The string rule, the best-slot rule and the treatment of a hole in a club's
row are written out in that file's `meta` block, so the transform can be audited without reading the
script.
