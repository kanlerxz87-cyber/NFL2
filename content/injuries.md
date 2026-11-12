# Week 10 Injury Report — Official Practice Snapshot
> All 254 rows the league published for Week 10 of the 2026 season, transcribed from nfl.com on 12 November 2026, with the practice-status code and the game status exactly as filed.

This is the **practice** report, not an availability answer. Each club files participation for players with a reportable condition; the game status column (Out / Doubtful / Questionable) is only populated once the club has filed designations. At fetch time six rows in 254 carried one, which is why the column is mostly `not published` below — those are not zeros and they are not omissions by us. The same goes for the injury column: the hub populates it only where a designation has been filed, so 248 of 254 cells are blank in the source and stay blank here.

**How to read the codes.** `Full` / `Limited` / `Did not practice` map to the league's strings "Full Participation in Practice", "Limited Participation in Practice" and "Did Not Participate In Practice". `Out` / `Questionable` are the filed game statuses. Position is the league's abbreviation. Every player name links to that player's official page; every row's Source cell links the official hub page it was transcribed from.

{{csv data/injuries_2026_wk10.csv;;cols=game:Game,team:Club,player:Player,pos:Pos,injury:Injury,practice:Practice:practice,status:Game status:status;;source=S-INJ;;link_player=1;;group=game;;caption=Grouped by game in the order the official page lists them. Club abbreviations are the league's own. Rows are stored verbatim; nothing was corrected, added or removed.}}

## What this snapshot already tells us

| Finding | Number behind it | Consequence for a model |
| --- | --- | --- |
| Designations published at fetch time | 6 of 254 (2 Commanders OUT, 1 Giant QUESTIONABLE, 3 Patriots OUT) | availability features must be built on participation *trend*, not on the status column, until designations land |
| Injury detail published in the hub table | 6 of 254 | body-part features have to come from the prose feed with an explicit join, not from this table |
| Clubs whose hub block is empty | 4 — BAL, CIN, LAC, SEA | must be read as "not published"; Seattle is the worked counter-example ([FL-01](flagged-for-review.html)) |
| Rows marked "did not practice" | {{metric dnp}} | the single strongest pre-designation availability signal we can compute today |
| Rows marked "limited" | {{metric limited}} | the ambiguous middle; the transition matters more than the level ([SIG-02](signals.html)) |
| Rows marked "full" | {{metric full}} | near-noise for availability, but useful as the denominator |
| Quarterback depth items | 5, of which 3 are confirmed starting changes (AZ, CLE, SEA), 1 unresolved (MIN) and 1 backup assignment (SEA) | each confirmed change moves a team total and pass-volume props far more than the spread |

## Availability load by club (arithmetic on the rows above)

{{team_availability}}

## The six designations that were published

{{csv data/injuries_2026_wk10.csv;;cols=game:Game,team:Club,player:Player,pos:Pos,injury:Injury,practice:Practice:practice,status:Game status:status;;source=S-INJ;;link_player=1;;filter=status:!;;caption=Every row the league had designated at fetch time. Three of the five are Patriots rule-outs for the Munich game, which is the whole reason that game's total is fragile.
