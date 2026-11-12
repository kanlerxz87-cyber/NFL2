# Depth Deficiencies by Side of the Ball
> The requirement in the brief is specific: know when a defence is down to its second, third or fourth string, and know the same about an offence. This page is the join that answers it — the league's own availability filing crossed with the club's own published depth chart, for the Week 10 slate.

Two official documents, and only these two:

1. **nfl.com/injuries/** — the practice and game-status filing, transcribed row by row at **22:35Z on 12 Nov 2026** (279 rows, 26 clubs with entries).
2. **the club's own depth chart** — seahawks.com and therams.com in this build. Every club publishes one and every club labels it *unofficial*; it is a working document, not a league designation. That label is part of the data, and it is why no string claim on this site is stronger than "the club printed it in column 2".

Nothing else is used. No depth is inferred from salary, draft round, jersey number or last season's starts. Where a club's chart has not been transcribed into this build, the replacement column says `not published` — that is the honest state of 26 of 28 clubs, and it is the single biggest gap in the injury workstream ([S-39](suggestions.html)).

## refreshed: what the hub actually says today

The hub is a rolling document. Our published snapshot was taken at 04:45Z; a second read at 22:35Z has **25 more rows and 15 re-filed practice codes**, and **no row withdrawn**. So the earlier table is not wrong, it is a timestamp — and the delta is the part a model needs.

{{csv data/reverification_a392.csv;;cols=check:Check,scope:Scope,official_value:Official (22:35Z),published_value:Published in this build,result:Result,note:Note,source:Source;;source_col=source;;caption=Every re-verification run against the live official page, with its outcome. Two rows read "superseded": the hub moved, the transcription did not. See [Flagged for review](flagged-for-review.html) FL-27.}}

{{csv data/injury_delta_a392.csv;;cols=kind:Change,team:Club,player:Player,pos:Pos,side:Side,practice_at_2235:Practice 22:35,status_at_2235:Game status,note:What changed,game:Game;;source_col=source;;group=kind;;caption=The row-level diff between the two official reads. Rows the clubs added late are mostly defensive — which is exactly the population a spread model misses if it only reads the Wednesday filing.}}

## Availability load by club and side of the ball

`did_not_practise` split by offence and defence is the closest thing to a deficiency count the league's own filing supports. A club can file eleven men and still be at full strength on one side; the split is what tells you which side broke.

{{csv data/deficiency_by_club_a392.csv;;cols=club:Club,game:Game,side:Side,reported:Reported,did_not_practise:Did not practise,limited:Limited,designated_out:Designated out,positions_affected:Position groups touched,first_string_unavailable:First-string names unavailable,depth_chart_in_this_build:Chart transcribed;;source_col=source;;group=club;;caption=One row per club per side of the ball, including rows where the club filed nobody — "reported 0" here means the hub block was empty, which the league also renders as "No Injuries Reported" and which must be read as missing, not healthy ([FL-01](flagged-for-review.html)).}}

## The two clubs where the chain is verified end to end

For Seattle and Los Angeles the join produces the thing the brief actually asks for: which string is out, and who has to do the job instead. Read `next_man_up` as "the club's own column 2 (then 3, then 4)".

{{csv data/deficiency_chains_a392.csv;;cols=club:Club,side:Side,position_group:Club's group,player:Player unavailable,position:Hub position,string:String on the club chart,practice:Practice,status:Game status,next_man_up:Next man up,why:Why this row is assertable,depth_url:Club chart:urls,injury_url:League hub:urls;;source_col=injury_url;;show_source=0;;group=club;;caption=Rows are limited to players a club filed as limited or non-participant. "no backup listed on the club chart" is a published fact about the document, not an absence of one in real life — several clubs list a single name for a role. Where the hub's position code and the club's group label disagree (the hub files Jarran Reed as DT, the chart lists him on the end line), the club's own row is used and the mapping is documented in the script.}}

## What this changes about a line, and what it does not

- **A first-string quarterback is a different animal from four defensive linemen.** Seattle's filing has Sam Darnold (chart column 1 at QB) not practising with Drew Lock limited and Jalen Milroe — a third-stringer — as the next unreserved name. The league's own news page confirms the starter change. That moves a team total and the pass-volume props far more than it moves the spread; the register's job is to make sure the model is told which.
- **Second- and third-string defenders unavailable is the invisible deficiency.** Brandon Pili is Seattle's *second-string nose tackle*; his unavailability puts Deven Eastern in the rotation, and nothing in a box score or a standings table reveals that. Four of the twenty-five rows added to the hub after our snapshot were defensive.
- **None of it is priced yet.** There is no coefficient in this repository that converts "1st-string LT out, 2nd string in" into points, and inventing one from a 136-game log with no matching injury history would be the exact failure mode this project exists to avoid. The deficiency register is an *input* to gate G-02 and to [Q-02](questions.html), and it is published as a tracked dataset from today.
