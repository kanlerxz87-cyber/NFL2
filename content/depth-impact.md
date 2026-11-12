# Depth & Deficiencies
> Who is replacing whom because of a confirmed absence — and, as important, what we cannot yet quantify about it.

The brief asked the system to know when second, third and fourth-string backups have to replace starters, on both sides of the ball. Two facts shape this page. First, **the league publishes no depth chart** — the expected official path is an error page, so depth rank cannot be looked up, only reconstructed ([FL-06](flagged-for-review.html)). Second, the hub's injury table is a practice document, so the reliable evidence for "a starter is unavailable" lives in the roster-move and designation stream, which is what this page ingests.

What we can therefore state today, verified: confirmed rule-outs, injured-reserve placements, designated-to-return events, practice participation, and coach-announced starting changes. What we deliberately do **not** state: which depth-chart rung the replacement occupies, and what the replacement costs in points or yards. Those columns are absent from this page rather than guessed — the effect estimate needs playing-time data we are not entitled to store yet ([Q-02](questions.html)).

## Confirmed Week 10 depth and availability events

{{csv data/depth_changes_2026_wk10.csv;;cols=team:Club,player:Player,pos:Pos,change:Event,detail:As published;;source_col=src;;caption=227 rows. "As published" keeps the official wording, including two source typos ("limted") preserved as filed. Event types are a controlled vocabulary: RULED-OUT, IR, IR-ACTIVATED, IR-RETURN-DESIG, DEPTH-CHART, PRACTICE, DNP, SIGNING, ROSTER-CUT, TIMELINE, SEASON-IMPACT, NO-DESIGNATION, IR-DECISION, RULED-OUT-WK9.}}

## What the injury and depth data already establishes for Week 10

| Club | Confirmed absence or change | Evidence type | Why it matters to a line |
| --- | --- | --- | --- |
| SEA | Starting QB out; the backup starts a second straight week and is himself carrying two injuries | official article naming the coach | a two-injury backup under centre moves the team total and every pass prop, and the spread only weakly |
| GB | Lead rusher out for surgery, bye the following week | official roundup plus the hub's DNP row | pass volume up for the replacement; the short week removes a snap-recovery game |
| LAR | Lead receiver out "significant time" but **not** placed on IR, on roster-mechanics grounds | two official pages, in conflict | shows IR status is a poor availability key on its own ([FL-04](flagged-for-review.html)) |
| MIN | Two quarterbacks injured, a third acquired by trade, and the coach refusing to name a starter | official roundup | an unresolved QB chain is a variance event, which is a prop-market problem before it is a spread problem |
| AZ | First career start at quarterback for a third-round rookie | official roundup naming the coach | the least reliable position group in the league, with no starter-quality history to price |
| NE | Three rule-outs including the starting corner and a lead back, in a 09:30 ET kickoff abroad | hub designations plus the roundup | two independent stressors — availability and schedule — in one game |
| NO | Two starting backs absent or limited, with one returning from IR on a designation | official roundup | backfields rebuilt mid-week are where rush props are most mispriced |
| WAS | Starting centre out with a concussion plus a tight end out | hub designations | interior-line absence is the clearest run-game deficiency we can currently evidence |

## Who is actually playing instead: 18 measured cases, one of them a vacancy

This is the direct answer to "tell me when a 2nd, 3rd or 4th string is replacing a starter", and it is
narrower than the requirement asks for. Four clubs — KC, GB, NE and DET — publish a depth chart that has
been transcribed and checked here. For those four clubs the join is exact: a name match inside a club's own
chart, against the same club's rows in the official practice report. Nothing is inferred across sources.

The rule, stated so it can be argued with: a player is **available** if the official report lists him as a
full participant, or does not list him at all (the report covers players with a reportable condition, so
absence from it is not an injury claim). A **limited** or **did not practice** player is treated as not
available to start, which is deliberately conservative — a limited participant often does play.

{{csv data/computed_depth_reach.csv;;cols=club:Club,unit:Unit,position_group:Position,depth_reached:String reached,projected_starter:Projected starter,starter_practice:Starter status,next_man_up:Next man up,next_man_practice:His status,chain_length:Chain,players_skipped:Skipped,chart_source:Club chart:url;;source=S-CALC;;caption=Recomputed from data/depth_charts.json and data/injuries_2026_wk10.csv on every build, and re-derived independently by tools/verify.py, which fails if any row stops reproducing. The chart column links each club's own published depth chart.}}

### The three cases that reach a third string

| Club | Position | What happened | What it means |
| --- | --- | --- | --- |
| **NE** | RB | Rhamondre Stevenson did not practise and 2nd-string TreVeyon Henderson did not practise, so the next available back is **3rd-string Corey Kiner** on a four-deep chain | the clearest "down to a third-stringer" case in the dataset, and it is on offence where the requirement specifically asks |
| **GB** | LG | Aaron Banks was limited and 2nd-string Travis Glover was limited, so **3rd-string Donovan Jennings** is the next man up | same shape on the offensive line — the position group where a replacement degrades every other player's numbers |
| **GB** | LB | Zaire Franklin did not practise and 2nd-string Ty'Ron Hopper was limited, so **3rd-string Kristian Welch** is next | the defensive counterpart; this is a second-level defender, which is the R-20 case |

Two more are worth naming because they are one injury away from a cascade: **DET CB_1** and **GB RB** each
have a four-deep chain where only the starter is down, so the backup is a genuine 2nd string and not a
patchwork. A pricing model should treat a four-deep chain with a healthy 2nd string differently from a
two-deep chain with a limited one, and that distinction is now measurable rather than asserted.

### The vacancy, which is worse than a third stringer

One case does not fit the "next man up" shape at all. **New England at left guard**: the starter Ben Brown
did not practise and is listed **Out**, and the 2nd-string Walter Rouse also did not practise. Nobody on the
published two-deep is available. That is a **vacancy**, not a third-string replacement, and the first version
of this table silently dropped it because the loop only recorded cases where *someone* was available.

It is published now, marked `vacant`, with the next-man-up column deliberately empty — filling in a name
there would be inventing a lineup the club has not published. This is the single most decision-relevant row
on the page: a guard vacancy on an offensive line is exactly the situation where a totals model should widen
its distribution rather than shift its mean, and it is the kind of thing a depth chart exists to surface.

### What this table is not

- It is **not 32 clubs.** It covers 4. The other 28 clubs have no verified chart, and the
  site refuses to guess a depth rank for them. That gap is [FL-06](flagged-for-review.html) and the fix is
  a 32-club transcription, which is [S-15](suggestions.html).
- It is **not an availability forecast.** "Next man up" means the next name on the published chart who is
  not on the practice report as limited or out. It does not incorporate inactives, which are published 90
  minutes before kickoff ([Q-07](questions.html)).
- It is **not a points estimate.** How much a 3rd-string guard costs in expected points needs snap-level
  data this project is not entitled to store ([Q-02](questions.html)).

## The framework that replaces the missing depth chart

| Layer | Source | State |
| --- | --- | --- |
| Roster status (active, IR, PUP, NFI, practice squad) | official club roster page | vocabulary confirmed on one club only — [FL-14](flagged-for-review.html) |
| Practice participation, three filings a week | official hub | one filing held; needs the point-in-time store ([FL-09](flagged-for-review.html)) |
| Designation (Out / Doubtful / Questionable) | official hub and the per-game report | 5 rows this week |
| Projected starter | coach statements in official reporting | partial — 3 confirmed QB changes this week (AZ, CLE, SEA), 1 unresolved (MIN), nothing systematic |
| Actual starter and snap share | game data we are not licensed for | not available — [Q-02](questions.html) |
| Replacement effect in points | our own estimate against the two layers above | not published by design |

Until the last two layers exist, the honest output of this section is the **absence inventory**, which is real and useful: it tells a reviewer which clubs are missing a starter without pretending we know how much that costs.
