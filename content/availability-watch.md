# Availability Watch — who is out, who is missing, and what we still cannot say
> A dated read of the official Week 10 injury hub, transcribed player by player on 13 November 2026, plus the movement since the previous read. This is the input the brief asks for: it tracks injuries, it states which clubs are missing from the record, and it says plainly which half of the requirement — "defenders and receivers replaced by 2nd, 3rd or 4th string" — the league's own pages cannot answer.

**Read at 2026-11-13T12:45Z** from [nfl.com/injuries](https://www.nfl.com/injuries/). 28 clubs on the Week 10 slate, **{{metric aw_rows}} player rows**, **{{metric aw_designations}} game-status designations**.

## What this page found that the site did not have yesterday

Three things changed at the source, and all three matter more than any single number on the page:

1. **Every club on the slate now has a stated injury state.** Yesterday the site published `{{metric injury_coverage}}` coverage — SEA and CIN were absent from our file entirely, which [FL-24](flagged-for-review.html) recorded as a collection gap. The official hub now carries full blocks for both. The gap closed at the source, not by us filling it in, and this snapshot transcribes **28 of 28**.
2. **Three more players have an official game status.** There were 6 designation cells in the register; there are now 9. The three new ones are Detroit's — Kerby Joseph, Cade Mays and D.J. Reed, all **OUT**. This is the first week where a full defensive backfield and a starting centre can be priced as unavailable rather than as questionable.
3. **The hub is a series, and it only grew.** 17 players were added across 10 clubs and **none were removed**. Of the 277 players present in both reads, **49 changed practice code — 37 upgraded, 12 downgraded**. A model that read yesterday's file and stopped would have been wrong about 66 of 296 rows without knowing it.

## The snapshot, club by club

{{csv data/availability_watch_by_club_c3ec1487.csv;;cols=club:Club,game_id:Game,rows_published:Rows,did_not_practice:DNP,limited:Ltd,full:Full,designations:Status,out:OUT,questionable:Q,doubtful:D,what_the_hub_publishes:State the hub publishes,string_of_unavailable_player:Depth string of the unavailable player,replacement_effect_pts:Replacement effect (pts);;source_col=source;;caption=One row per club on the Week 10 slate, counted from the 2026-11-13 transcription of the official hub. The last two columns are deliberately blank: no official public depth chart exists (FL-06) and no replacement effect has ever been measured on this site (gate AW-4). LAC and BAL are the two clubs the league answers with "No Injuries Reported" — a stated state, rendered as such, never as zero (S-19).}}

Read the two blank columns as the answer to the hardest part of the brief. The requirement is to know when a 2nd, 3rd or 4th-string backup is replacing a starter, on offence **and** defence. The hub tells us, per player, whether he practised and whether he is out. It does not tell us **where he sits on the depth chart**, and no official public depth chart exists — `nfl.com/teams/<club>/depth-chart/` returns the league's 404 page. Four clubs publish an unofficial chart and those are transcribed on the [Depth & Deficiencies](depth-impact.html) page. For the other 24 clubs, the honest answer is a blank, and filling it from a roster list would be inference, which the brief forbids.

## The arithmetic, so no reader has to redo it

{{csv data/computed_availability_watch_c3ec1487.csv;;cols=metric:Metric,value:Value,how_it_is_computed:How it is computed,what_it_means:What it means;;source_col=source;;caption=Recomputed by tools/build_availability_watch.py on every build from the transcription and the fixture list. Nothing in this table is typed by hand.}}

The number to sit with is **{{metric aw_designation_share}}**. Nine rows out of 296 carry a game status. The rest carry a practice code, which is a statement about Wednesday's or Thursday's workout — not about Sunday. Any availability model built on this file that treats "did not practise" as "will not play" is reading a proxy as a fact.

## What moved between the two dated reads

{{csv data/availability_watch_movement_c3ec1487.csv;;cols=change:Change,count:Count,how_it_is_computed:How it is computed,detail:Detail,what_it_means:What it means;;source_col=source;;caption=The 2026-11-12T22:35Z read (kept in data/injuries_wk10_2026_hubrefresh.csv, another session's file, read-only here) compared with this one, player by player. The comparison is the only part of this page that could not be produced from a single snapshot.}}

Every individual practice-code change is published below, because a signal you cannot audit is not a signal:

{{csv data/availability_watch_practice_deltas_c3ec1487.csv;;cols=club:Club,player:Player,practice_2026_11_12:11 Nov,practice_2026_11_13:13 Nov,direction:Direction;;source_col=source;;caption=D = did not practise, L = limited, F = full. "Upgrade" means a player moved toward full participation; "downgrade" means away from it. This is the raw material for the surprise signal in S-12 — the delta, not the level.}}

Two of these are worth naming because they are the kind of move that decides a Sunday:

- **Tony Pollard (TEN), full to did-not-practise.** The only full-to-DNP move in the interval, and the largest single downgrade in the file.
- **Kerby Joseph (DET), limited to full — and OUT anyway.** It is the clearest demonstration on the page that practice participation does not determine game status. A model that scored his upgrade as "more likely to play" would have been exactly wrong.

## The four readiness gates this snapshot does and does not clear

{{csv data/availability_watch_gates_c3ec1487.csv;;cols=gate:Gate,question:Question,result:Result,measured_value:Measured value,why:Why;;source_col=source;;caption=Each gate is answered with a number, not an opinion. Three fail, and every one of them fails for a stated reason that is a property of the official sources, not of this session's effort.}}

## What was re-verified to build this page

{{csv data/reverification_c3ec1487.csv;;cols=check:Check,scope:Scope,official_value:Official value,published_value:What this repo published,result:Result,note:Note;;source_col=source;;caption=Read against the live official pages on 2026-11-13 between 12:40Z and 12:55Z. MATCH means the repository already agreed; CORRECTED means the source had moved and this session transcribed the current state; SUPERSEDED means both states are true at different times and both are kept; MISMATCH means we publish something the official page does not say, and it is flagged rather than edited.}}

## What this page does not do

- **It does not grade a strategy.** No availability signal here has been tested against a result. The [leaderboard](leaderboard.html) is still empty for exactly that reason ([Q-33](questions.html), [S-44](suggestions.html)).
- **It does not claim the snapshot is live.** It is one read at one moment, with that moment printed at the top. The hub will move again before kickoff — the [sedimentation problem](methodology.html) is the whole point of [S-35](suggestions.html) and [S-43](suggestions.html).
- **It does not name who replaces whom.** That is the blank column above, and it is blocked by [FL-06](flagged-for-review.html), not by a lack of will.
- **It does not use a non-official source.** Every row links `nfl.com/injuries/`. Player-level data from a betting operator or an aggregator does not appear anywhere in this dataset, per [S-14](suggestions.html).
