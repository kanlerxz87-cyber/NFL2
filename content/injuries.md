# Week 10 Injury Report — Official Practice Snapshot
> The 254 rows below are the first Week 10 ingest (12 November 2026, 04:40 UTC), transcribed from nfl.com with the practice-status code and the game status exactly as filed. They are not the full hub: the 22:35 UTC read the same day holds 279 rows, including every Cincinnati and Seattle row this table lacks. Read the Injury Read Lineage page before using any count from this page.

**Dated note, 15 November 2026:** this page is the 12 November read. On 15 November the official page lists rows for the Chargers and the Ravens, which this page shows as having none. See the [Injury Hub delta](hub-delta.html) and [FL-81](flagged-for-review.html).

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
