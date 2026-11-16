# Weekly "what changed" — the Week 10 window, measured

> BL-62 asks for a weekly diff instead of a static snapshot: store the snapshots and publish the change,
> not the level. Two **dated, independent transcriptions** of the same official standings page already
> exist in this repository — 13 November 2026 (`S-STAND-653B`) and 16 November 2026 (`S-STAND-F3EC`) — so
> the change across the Week 10 window can be measured rather than asserted. Thirty-two rows below, one
> per club.

## Read the window before you read the numbers

The two reads are dated, so the window between them is a **date window, not a week number**. That matters,
and it is the one thing on this page worth understanding:

- **The Thursday game is outside it.** Commanders at Giants was played on 12 November, before the first
  read. Washington and the Giants therefore show **zero games played in the window** even though both
  played in Week 10.
- **The Monday game is outside it.** Chargers at Ravens kicks at 20:15 ET on 16 November, after the
  second read. Both clubs also show zero, and the [fixture-context](fixture-context.html) register marks
  that game `scheduled, not final at read time`.
- **So the window holds 12 games, not 13.** The verifier proves it: total games played across the 32 rows
  is **24 team-games**, which is exactly twice the twelve Week 10 results dated between the two reads.

Eight clubs show zero games: the four on a bye (Chicago, Denver, Philadelphia, Tampa Bay) plus the four
above whose Week 10 game fell outside the window. A diff that cannot say which zero is which is a diff
that will mislead someone, so the page says it.

## The diff

{{csv data/weekly_diff_0a28b225.csv;;cols=abbr:Club,team:Team,conf:Conf,div:Division,games_played:Games in window,w_delta:W,l_delta:L,t_delta:T,pf_delta:PF,pa_delta:PA,net_delta:Net,div_rank_before:Div rank 13 Nov,div_rank_after:Div rank 16 Nov,div_rank_change:Rank change,streak_before:Streak 13 Nov,streak_after:Streak 16 Nov;;source_col=source;;caption=One row per club. W/L/T, points for, points against and net are the difference between the 16 November read and the 13 November read. Division rank is computed within each club's own division from that read's published win percentage, with net points as the tiebreak; a positive rank change means the club moved up. Blank cells are blank on the official page.}}

## What moved

Eight clubs changed position inside their own division over the window:

| Club | Division | 13 Nov | 16 Nov | Moved |
| --- | --- | --- | --- | --- |
| Detroit | NFC North | 2 | 1 | up 1 |
| Kansas City | AFC West | 2 | 1 | up 1 |
| Tampa Bay | NFC South | 3 | 2 | up 1 |
| LA Rams | NFC West | 3 | 2 | up 1 |
| Chicago | NFC North | 1 | 2 | down 1 |
| Denver | AFC West | 1 | 2 | down 1 |
| New Orleans | NFC South | 2 | 3 | down 1 |
| Seattle | NFC West | 2 | 3 | down 1 |

Two of the four clubs that moved **down** — Chicago and Denver — did not play in the window. Losing a
division lead without playing is the cleanest illustration of why a diff beats a snapshot: the level looked
stable, the rank did not.

## What this page is not

- **It is not a full Week 10 diff.** It is the change between two dated reads. The two games outside the
  window are named above rather than folded in, because folding them in would mean inventing a read that
  does not exist.
- **It is not a rating change.** The brief's diff column asks for rank, rating and availability change.
  Rank is here. Rating change is not: no dated rating snapshot pair exists, so it stays blank. Availability
  change is not here either — that lives on the [injury lineage](injury-lineage.html) and
  [hub delta](hub-delta.html) pages, which diff dated reads of a different page.
- **It is not a stored series yet.** These are two reads that happened to be taken. A weekly snapshot
  store with retained hashes is BL-29/BL-30/BL-48 and remains not started; until it exists, a "weekly" diff
  can only be produced when two reads happen to be on file.

## Method

1. `tools/build_0a28b225.py` reads `data/standings_recheck_20261113.csv` and `data/standings_2026.csv`,
   computes each club's win/loss/tie, points, net and within-division rank on each read, differences them,
   and writes `data/weekly_diff_0a28b225.csv`.
2. `tools/verify_0a28b225.py` re-derives all 32 rows from the two reads — every level, every delta, both
   ranks and the rank change — then proves the window: total games played must equal twice the number of
   Week 10 results whose date falls strictly between the two read dates, and the zero-game clubs must be
   exactly the clubs absent from those results. 38 checks pass.
3. Reproduce with `python3 tools/build_0a28b225.py && python3 tools/verify_0a28b225.py`.

Sources: both dated reads of the [official standings page](https://www.nfl.com/standings/) —
`S-STAND-653B` (2026-11-13T12:53Z) and `S-STAND-F3EC` (2026-11-16T14:57Z) — cited on every row.
