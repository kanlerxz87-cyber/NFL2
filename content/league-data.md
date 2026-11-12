# Standings & Schedule
> The two tables everything else joins to: 32 reconciled standings rows and the 14 Week 10 games, with the venue, kickoff and broadcast as the league published them.

Standings rows are not simply copied — they were recomputed. Winning percentage in the NFL counts a tie as half a win, so a 5–2–1 club is listed at 0.688, not 0.625, and that formula reconciles for all 32 clubs. Net points reconciles to points for minus points against everywhere. Two league-wide checks then close the transcription: ΣPF equals ΣPA to the unit (6246 each) and Σnet points equals 0, which can only hold if every points value was read off the right row.

The official standings page renders sixteen value columns and the fetched markup carries no header row. Seven columns have unambiguous meaning from their format and arithmetic and are published; the remaining split-record columns are **omitted rather than guessed** ([FL-07](flagged-for-review.html)).

{{csv data/standings_2026.csv;;cols=team:Club,abbr:Abbr,conf:Conf,div:Div,w:W,l:L,t:T,pct:Pct,pf:PF,pa:PA,net:Net,streak:Streak;;source=S-STAND;;caption=Division-view standings as published on 12 November 2026 (week 10 of the 2026 regular season, in progress).}}

## Week 10 slate

{{csv data/schedule_2026_wk10.csv;;cols=game_id:ID,date:Date,kickoff_et:Kickoff ET,away:Away,home:Home,venue:Venue,tv:Broadcast,game_url:Game page:urls;;source=S-WK10REP;;show_source=0;;caption=Game page links are the league's own URLs for each fixture, as published in the official week-10 report.}}

## What the schedule itself contributes as a feature

Two of these games are structural exceptions a model must not treat as ordinary, and both are verifiable from the official schedule alone — no external dataset required:

- **NE at DET, 09:30 ET in Munich.** A non-standard kickoff hour and an intercontinental trip for one club. We publish the fact, not a coefficient: the adjustment stays at zero until measured ([SIG-10](signals.html)).
- **BAL Monday night, following a club that played Thursday the week prior.** Rest asymmetry is computable from kickoff timestamps only, which makes it the cheapest defensible situational feature in the whole catalogue ([SIG-09](signals.html), [S-16](suggestions.html)).

## League-wide reconciliation performed on this page's data

| Check | Result |
| --- | --- |
| Σ wins = Σ losses across 32 clubs | pass — 135 and 135, with 2 ties counted on both sides |
| Σ points for = Σ points against | pass — 6246 and 6246 |
| Σ net points = 0 | pass |
| Winning pct = (W + ½T) ÷ (W + L + T) | pass for all 32 rows |
| Net = PF − PA | pass for all 32 rows |
| Games played consistent with week 10 of the schedule | pass — 8 or 9 games per club depending on bye placement |
