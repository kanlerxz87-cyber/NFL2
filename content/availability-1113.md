# Week 10 Availability — 13 November Re-read
> Measured on 13 November 2026, 12:45 UTC. What the league's own injury hub says today, what it said at the two earlier reads this repository published, and what that means for a defence or an offence that is down to its second, third or fourth string.

**Why this page exists.** The brief asks for a system that tracks injuries *and* knows which side of the ball is depleted — not a list of names. That needs two documents and the join between them: the league's filing (who did not practise, who is out) and the club's own depth chart (who replaces them). This page is the third read of the first document, taken four hours before the earliest Sunday kickoff, with the join attached where our transcribed charts support it.

| Measure | 12 Nov 04:45Z | 12 Nov 22:35Z | **13 Nov 12:45Z** |
| --- | --- | --- | --- |
| Rows on the hub | 254 | 279 | **296** |
| Clubs with rows | 24 of 28 | 26 of 28 | **26 of 28, plus 2 publishing "No Injuries Reported"** |
| Game designations published | 6 | 6 | **9** |
| Clubs whose chart this build transcribes | 4 | 4 | **4** |

Nothing was withdrawn between reads: ten clubs gained rows, eighteen were unchanged. A second session read the same page one minute later with no coordination and published its own transcription: 296 rows, 26 clubs with names, 9 designations, and **every per-club count identical to ours** — the only difference being that this build also carries the two `No Injuries Reported` clubs as explicit zero rows. That double entry is the strongest availability evidence on the site (RV-24). The growth is the league's filing cadence, not a correction — which is the whole reason a snapshot page like this one has to say when it was taken.

## The designations and non-participants this read publishes

Every row below is a player the official hub lists with a game designation, or with a did-not-practise code at one of the four clubs whose depth chart this build transcribes. Designations at the other clubs are counted in the club table, not listed by name, because listing names for four clubs and counts for twenty-four would imply a coverage this build does not have.

{{csv data/hub_flagged_20261113_66faefac.csv;;cols=game:Game,club:Club,player:Player,pos:Pos,side:Side,injury:Injury,practice:Practice,kind:What the hub shows;;source_col=source;;group=club;;caption=Practice codes are the league's: F practised fully, L limited, D did not practise. A designation of OUT with an F practice code is not a transcription error - see the flag underneath this table (FL-58). The game column is the Week 10 fixture id in the [schedule table](league-data.html).}}

Three of the nine designations are new since last night and all three are Detroit: safety Kerby Joseph, centre Cade Mays and cornerback D.J. Reed. Both clubs in Sunday's Munich fixture carry a gap in a printed first-string column: Detroit a starting centre and a starting corner, New England a starting left guard whose absence is what empties the chart's centre column.

## Availability by club, in three states

The three states matter. A club can file fifteen players (New England), file nobody because the block reads "No Injuries Reported" (Los Angeles and Baltimore), or be absent from the file because the read did not reach it — and only the first of those is a fact about football. Treating the second as healthy is how an availability model ends up pricing a team that is without both its quarterbacks.

{{csv data/club_availability_20261113_66faefac.csv;;cols=game:Game,club:Club,state:Block on the hub,rows_today:Rows,load_out_plus_dnp:Load (out + DNP),dnp:Did not practise,limited:Limited,full:Full,out:Designated out,questionable:Questionable,rows_at_2235:Rows at 2235Z,change_since_2235:Change,chart_in_build:Chart in this build;;source_col=source;;group=game;;caption="Load" is what the pre-registration rule consumes: the club's designated-out count plus its did-not-practise count, limited reports excluded by design. It is a sum of two published counts, so a player who is both designated out and listed as a non-participant is counted twice. Today only Washington, New England and Detroit carry both columns, and where the hub names the players the overlap is knowable: de-duplicating moves Washington 5 to 3, New England 6 to 3 and Detroit 6 to 4, and changes none of the locked calls. [S-64](suggestions.html) is the proposal to rebuild it as a name-level union across the whole slate. Rows are one per player at every read — the 254/279/296 comparison is like for like, which is why it is checked in [tools/verify.py](https://github.com/kanlerxz87-cyber/NFL2/blob/main/tools/verify.py) rather than asserted here.}}

The league-wide load is 98 against 296 rows, and its distribution is the useful part: thirteen clubs sit at four or more, twelve file nothing that reaches the threshold, and Baltimore and Los Angeles (Chargers) file nothing at all. Dallas is the extreme case on both axes — eighteen rows, nine non-participants — and it is the club our own number has San Francisco laying 5.5 on, which is the fixture [S-62](suggestions.html) exists for.

This page is the 13 November read and its join; the standing dated snapshot maintained separately lives on [Availability Watch](availability-watch.html), and [Personnel Relief](personnel-relief.html) covers IR moves, returns and signings that the weekly filing does not show. Between them the three pages are one measurement, one rolling register and one transaction feed — read together they agree, which is the point of publishing them apart.

## Which starter slots are actually empty

This is the join the brief asks for: an unavailable name is only a deficiency if the club's own chart says the next man up is a lower string. Depth position here is the column the club prints, 1-based, exactly as [the hierarchy rule in the source file](https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/depth_charts.json) states it. Every club labels its chart *unofficial*; that label travels with each row.

{{csv data/availability_deficiency_66faefac.csv;;cols=club:Club,game:Game,side:Side,position_group:Group,player:Unavailable player,availability_state:State,string_depth:Chart column,next_man_up:Next man up,others_in_group:Others behind,practice_and_designation:Practice vs designation,prior_read_2235:At 2235Z,chart_note:Join note,depth_url:Chart source;;source_col=injury_url;;group=club;;caption=Two official documents, one row: the league's filing gives the state and the URL in the last column pair, the club's chart gives the column and the replacement. "not listed on the club's chart in this build" in the Group column means the chart is not transcribed here; "the transcribed chart carries no row naming this player" means it is, and the name is absent - those two states are different facts and the join never collapses them. Nothing is inferred: no salary, draft round, jersey number or prior-season start is used to guess a depth slot, and where the hub's practice code and its designation disagree the row says so instead of picking one.}}

Eight of the eighteen rows sit in a 1st-string column, which is the population that changes what we expect a team to score:

- **Green Bay** — four 1st-string columns are empty on the day: Josh Jacobs (RB), Sean Rhyan (C), Zaire Franklin (LB_1) and Javon Bullard (NB), on both sides of the ball. Their opponents Minnesota file a load of six too — six non-participants, two limited, one full — which is why a counter reads this fixture a coin flip and a chart reads it Green Bay's problem.
- **Detroit** — Cade Mays at 1st-string centre and D.J. Reed at 1st-string CB_1 are designated out; Juice Scruggs and Rock Ya-Sin are the club's printed replacements, with three bodies behind Reed and one behind Mays. Kerby Joseph appears on no row of the safety chart, so no string is asserted for him, and Sione Vaki's 2nd-string backfield slot rolls one deep to Jacob Saylors.
- **New England** — Ben Brown holds two columns (1st-string left guard, 2nd-string centre), so one absence appears twice with two different answers: the guard slot rolls to Walter Rouse, and the centre group is left with a single charted body and no printed alternative.
- **Kansas City** — Jaylon Moore is the printed 1st-string right tackle and did not practise. Peter Woods is 2nd-string defensive tackle with no name behind him on that row, which is an exhausted chain rather than a shallow one, and Green Bay's 4th-string tight end Josh Whyle is the same shape at the other end of a depth chart.
- **Detroit's contradiction** — Kerby Joseph is designated out with a full-practice code on the same row. The join refuses to guess a string for him: the transcribed Lions chart carries S_1 and S_2 rows and neither names him, so his string is left blank and the disagreement is published as [FL-58](flagged-for-review.html).

## What this read does not establish

- It does not price an absence. No official source publishes a positional point value, so the deficiency table counts columns instead of converting them into points — the same rule the [depth-impact page](depth-impact.html) applies, and the reason [Q-36](questions.html) stays open.
- It does not carry a Week 11 filing. The hub's Week 11 view was not open at read time; practice reporting starts 18 November. Anything written into that slot today would be invented.
- It does not resolve which column wins when practice and designation disagree. [FL-58](flagged-for-review.html) publishes the contradiction and [Q-52](questions.html) asks for the precedence rule; the register keeps both columns until an owner decides.
- It does not know why a player left a report. A withdrawal can mean cleared or it can mean injured reserve, and the league's own pages use both. [Q-51](questions.html) and [S-59](suggestions.html) are the fix.

## Line-by-line re-verification for this page

{{csv data/reverification_66faefac.csv;;cols=id:ID,check:Check,scope:Scope,published_value:Published here,official_value:Official page today,result:Result,note:Note;;source_col=source;;caption=Every value on this page and the pre-registration page beside it, compared against the live official page it came from, with the outcome recorded. NOT CHECKED rows are counted as a result, not skipped, so the register cannot be read as a clean sweep it did not perform. MISMATCH rows are published rather than edited: FL-36 and FL-56.}}
