# Fresh Official Verification — 16 November 2026

> A same-day, line-by-line re-read of the official league pages this repository's published tables rest on, taken in the **14:55–15:10Z window on 16 November 2026**. Every row below was checked against the live official page and carries the page it was checked against. Nothing is inferred: where the league publishes nothing, the cell says so.

Same-day source reads registered this session: [S-INJ-4540f880](https://www.nfl.com/injuries/), [S-STAND-4540f880](https://www.nfl.com/standings/), [S-WK11-4540f880](https://www.nfl.com/schedules/2026/by-week/week-11).

## Result at a glance

| Read | What was checked | Result |
|---|---|---|
| Standings — `S-STAND-4540f880` | 32 clubs × 8 published fields (W/L/T/PCT/PF/PA/net/streak) | 32/32 MATCH |
| Week 11 schedule — `S-WK11-4540f880` | 13 fixtures: date, kickoff, away, home, TV network | 13/13 MATCH |
| Injury hub — `S-INJ-4540f880` | 28 club blocks present on the current Week 10 slate | 28/28 present |

## Standings — club by club

One row per club, checked cell by cell against the official division standings page read **2026-11-16T15:00Z**. All 32 clubs × 8 fields = **256 values match**. The repository table carries the same capture-time column (`captured_utc`) and the same values; no cell changed between the published table and this fresh read.

{{csv data/reverification_4540f880.csv;;cols=id:Club,scope:Check,published_value:Repository publishes,official_value:Official page showed,result:Result,note:Note;;filter=check=Standings W/L/T/PCT/PF/PA/net/streak;;source_col=source;;caption=Standings comparison, one row per club, against https://www.nfl.com/standings/ read 2026-11-16T15:00Z. Published value and official value are identical in every row, so every result is MATCH.}}

## Week 11 schedule — fixture by fixture

One row per fixture, checked against the official Week 11 schedule page read **2026-11-16T15:00Z**. All 13 fixtures match on date, kickoff, clubs and network. Six clubs are on bye this week (ATL, CLE, GB, LAR, NE, SEA); the schedule page lists them under "Teams on Bye" and they are not fixtures.

{{csv data/reverification_4540f880.csv;;cols=id:Fixture,scope:Check,published_value:Repository publishes,official_value:Official page showed,result:Result,note:Note;;filter=check=Week 11 fixture date/kickoff/away/home/TV;;source_col=source;;caption=Week 11 fixture comparison, one row per fixture, against https://www.nfl.com/schedules/2026/by-week/week-11 read 2026-11-16T15:00Z. Published value and official value are identical in every row, so every result is MATCH.}}

## What this page does not establish

- **It does not grade any line or strategy.** Verification is the record that the inputs are what they claim to be; grading lives on the [Settled Week 10](week10-settled.html) and [Week 11 Lines (pre-registered)](week11-originated.html) pages.
- **It does not set a refresh cadence.** The standings and schedule are dated snapshots; how often cumulative tables move is [Q-40](questions.html), an open owner decision.
- **It does not make the injury hub a live feed.** The hub shows the current incomplete Week 10 slate (MNF LAC@BAL not final at read time); a single snapshot cannot support backtesting, which is why the dated-snapshot series remains open ([Q-36](questions.html), [S-35](suggestions.html)).

The raw reads are kept at [data/verify_reads_20261116_4540f880.csv](data/verify_reads_20261116_4540f880.csv) and the full row-by-row comparison at [data/reverification_4540f880.csv](data/reverification_4540f880.csv).
