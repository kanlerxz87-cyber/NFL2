# Team decision view: one row per club
> All 32 clubs in one table. The injury counts come from the official injury hub read of 16 November 2026 (14:40 UTC). The reserve-list column comes from the official November reserve list read at 14:44 UTC. The starter-change column quotes league articles word for word. Nothing is inferred, and nothing is filled in to make a row look complete.

{{csv data/team_view_3e77121b.csv;;cols=club:Club,club_name:Team,week10_hub_status:Week 10 hub status,hub_rows:Hub rows,out:Out,doubtful:Doubtful,questionable:Questionable,designated_total:Designated (Out + Doubtful + Questionable),did_not_practice:Did not practise,limited:Limited,full:Full,reserve_list_november:Reserve list (November 2026),starter_change_named_by_league_week10:League-named starter change,source:Source:urls;;source_col=source;;show_source=0;;caption=Counts are computed from the hub rows, one row per listed player. "Designated" is the count of players whose game status is Out, Doubtful or Questionable on this read, not a change since an earlier read. A Week 10 bye club has no hub block, so its counts are left blank, not zero. The reserve-list dates are the transaction dates the league prints. Starter rows exist only where a league article names a change.}}

## How to read this table

**Blank does not mean zero.** The four clubs that had a bye in Week 10 (Chicago, Denver, Philadelphia, Tampa Bay) are confirmed on the official schedule page's "Teams on Bye" list. They have no injury block, so their counts are blank.

**Starter rows are what the league says.** Four clubs have a starter change named in an official league article: Seattle (Darnold ruled out, Lock expected to start), Miami (Willis on injured reserve, McCord to start), Cleveland (Watson to start) and Arizona (Beck to start). Each cell quotes the article. We did not derive a depth order, and we did not infer a starter from a chart.

**Reserve-list names are a dated record.** A club shows "none on the November capture" when no November transaction for it appears in the capture read on 16 November. That is a statement about the capture, not a claim that the club has no reserve moves.

## What this view does not do

It does not rank clubs. It does not order depth, and it does not estimate who replaces whom. The depth and replacement registers are separate pages, built from playing-time sources.

Week 11 byes (Atlanta, Cleveland, Green Bay, LA Rams, New England, Seattle) are not verified against an official Week 11 bye list and are not shown on this page.

The reserve list prints the Rams as "LA". This table uses the injury hub's "LAR" code, and the mapping is logged as FL-119.
