# Week 10 Injury Report — Official Practice Snapshot
> This page leads with the **newest verified read** of the official hub — the full-page transcription of 15 November 2026, 12:51 UTC (347 rows, every club on the Week 10 slate), re-confirmed by the game-day read of 16 November 2026, 15:07 UTC. The first ingest (12 November, 254 rows) is kept below as history, clearly labelled. Read the Injury Read Lineage page (injury-lineage.html) before using any count from this page.

**Dated note, 16 November 2026 (session `f3ec0ff8`):** the game-day read is **value-identical** to the 15 November read on every shared player — zero field changes across the 344 shared rows, the same designation total (70 Out, 90 Questionable, 11 Doubtful), and only three name spellings differ (Chig/Chigoziem Okonkwo, Jacob/Jake Hummel, Kam/Kamren Curl). Two independently transcribed reads of the same official page now agree cell for cell, which is the strongest corroboration this repository has that its newest read is faithful. The three Lions designations that FL-94 publishes as stale in the old table below (Kerby Joseph, Cade Mays, D.J. Reed) carry **Out** in the newest read and in the game-day read. The Week 10 capture series now holds five dated reads (12 Nov ×2, 13 Nov, 15 Nov, 16 Nov game-day); the full ledger is on the [league data page](league-data.html).

## Newest full-hub read — 15 November 2026, 12:51 UTC (347 rows)

{{csv data/hub_read_8dee7df7.csv;;cols=club:Club,player:Player,pos:Pos,injury:Injury,practice:Practice:practice,game_status:Game status:status;;source_col=source_url;;group=club;;caption=The full official Week 10 hub, read 2026-11-15T12:51Z and transcribed row by row by session 8dee7df7 (S-INJ-8DEE). This is the table a reader should use; the 12 November table below is history. Practice codes: F = Full Participation in Practice, L = Limited Participation in Practice, D = Did Not Participate In Practice. Blank cells are blank on the official page — never zero, never an omission by us. The club column stores the club block the official page printed the player under; the page itself places some players under blocks other than their own club (FL-93, FL-99).}}

**Re-verified 16 November 2026, 15:07 UTC:** the game-day read of the same official page repeats these values exactly. The 16 November transcription is stored in `data/hub_read_f3ec0ff8_20261116.csv`; rendering it as a second 347-row table would double the page without adding information, so the ledger entry and the file stand in for it.

## Who is not on the report at all — the official Reserve List (captured 16 November 2026)

{{csv data/reserve_list_capture_f3ec0ff8.csv;;cols=date:Date,club:Club,player:Player,transaction:Transaction;;source_col=source;;caption=The official November 2026 Reserve List, read in full on 2026-11-16T14:44Z (S-RES-F3EC): 25 dated Reserve/Injured rows, the complete capture that FL-95 records as previously partial. The club abbreviations are the league's own; the Position cell is blank on the official page and stays blank here.}}

A player on this register **cannot play**, yet nine of the eleven placements dated 14 November still appear on the Week 10 report with a game status of Out, and Puka Nacua (Reserve/Injured 12 November) appears without a game status. That systematic disagreement is published as [FL-107](flagged-for-review.html), which extends [FL-96](flagged-for-review.html) to the whole class. It is why "not listed on the injury report" has never meant "available" on this site, and why every availability feature must join the transactions register before it reads any designation as a playing probability.

## First ingest — 12 November 2026, 04:40 UTC (254 rows)

> The 254 rows below are the first Week 10 ingest (12 November 2026, 04:40 UTC), transcribed from nfl.com with the practice-status code and the game status exactly as filed. They are not the full hub: the 22:35 UTC read the same day holds 279 rows, including every Cincinnati and Seattle row this table lacks, and the 15 November full read above supersedes this table entirely. Read the Injury Read Lineage page before using any count from this page.

**Dated note, 15 November 2026:** this section is the 12 November read. On 15 November the official page listed rows for the Chargers and the Ravens, which this table shows as having none. See the [Injury Hub delta](hub-delta.html) and [FL-81](flagged-for-review.html).

This is the **practice** report, not an availability answer. The headline count was wrong: see [the injury read lineage](injury-lineage.html) and [FL-87](flagged-for-review.html). Each club files participation for players with a reportable condition; the game status column (Out / Doubtful / Questionable) is only populated once the club has filed designations. At fetch time six rows in 254 carried one, which is why the column is mostly `not published` below — those are not zeros and they are not omissions by us. The same goes for the injury column: the hub populates it only where a designation has been filed, so 248 of 254 cells are blank in the source and stay blank here.

**How to read the codes.** `Full` / `Limited` / `Did not practice` map to the league's strings "Full Participation in Practice", "Limited Participation in Practice" and "Did Not Participate In Practice". `Out` / `Questionable` are the filed game statuses. Position is the league's abbreviation. Every player name links to that player's official page; every row's Source cell links the official hub page it was transcribed from.

{{csv data/injuries_2026_wk10.csv;;cols=game:Game,team:Club,player:Player,pos:Pos,injury:Injury,practice:Practice:practice,status:Game status:status;;source=S-INJ;;link_player=1;;group=game;;caption=Grouped by game in the schedule's fixture order (data/schedule_2026_wk10.csv). The game key was renumbered to that convention on 15 November 2026 (S-65; FL-61 and FL-64 resolved): every club under every id now names the fixture it actually plays, checked against the official game-centre pages, and tools/verify.py fails the build on any recurrence. Club abbreviations are the league's own. Player rows are stored verbatim; nothing was added or removed and no player value changed - only the game key and the row order. Club coverage is stated in the table above the find-out list; SEA, CIN and IND are partial or absent, a collection gap published as FL-24 rather than a claim that those clubs are healthy.}}

## What this snapshot already tells us

| Finding | Number behind it | Consequence for a model |
| --- | --- | --- |
| Designations published at fetch time | 6 of 254 (2 Commanders OUT, 1 Giant QUESTIONABLE, 3 Patriots OUT) | availability features must be built on participation *trend*, not on the status column, until designations land |
| Injury detail published in the hub table | 6 of 254 | body-part features have to come from the prose feed with an explicit join, not from this table |
| Clubs with no row in this snapshot | {{metric injury_clubs_missing}} of the {{metric injury_clubs_playing}} playing Week 10 — {{metric empty_clubs}} | must be read as "not published", never as "healthy". LAC and BAL show "No Injuries Reported" on the hub; SEA and CIN publish full blocks and their rows are a known gap here ([FL-24](flagged-for-review.html)) |
| Rows marked "did not practice" | {{metric dnp}} | the single strongest pre-designation availability signal we can compute today |
| Rows marked "limited" | {{metric limited}} | the ambiguous middle; the transition matters more than the level ([SIG-02](signals.html)) |
| Rows marked "full" | {{metric full}} | near-noise for availability, but useful as the denominator |
| Quarterback depth items | 5, of which 3 are confirmed starting changes (AZ, CLE, SEA), 1 unresolved (MIN) and 1 backup assignment (SEA) | each confirmed change moves a team total and pass-volume props far more than the spread |

## Availability load by club (arithmetic on the rows above)

{{team_availability}}

## The six designations that were published

{{csv data/injuries_2026_wk10.csv;;cols=game:Game,team:Club,player:Player,pos:Pos,injury:Injury,practice:Practice:practice,status:Game status:status;;source=S-INJ;;link_player=1;;filter=status=*;;caption=Every row the league had designated at fetch time. Three of the five are Patriots rule-outs for the Munich game, which is the whole reason that game's total is fragile.}}
