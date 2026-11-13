# Standings, Schedule & Game Log
> The tables everything else joins to: 32 reconciled standings rows, the 14 Week 10 games, and a {{metric games_log}}-game completed-results log for weeks 1–9 that cross-checks the standings exactly.

Standings rows are not simply copied — they were recomputed. Winning percentage in the NFL counts a tie as half a win, so a 5–3–1 club is listed at 0.611, not 0.556, and that formula reconciles for all 32 clubs. Net points reconciles to points for minus points against everywhere. Two league-wide checks then close the transcription: ΣPF equals ΣPA to the unit ({{metric league_pf}} each) and Σnet points equals 0, which can only hold if every points value was read off the right row.

The official standings page renders multiple value columns without a full column-header row in the fetched table. Eight fields have unambiguous meaning from the NFL legend and arithmetic—W, L, T, PCT, PF, PA, NET PTS and STREAK—and are published; the remaining split-record columns are **omitted rather than guessed** ([FL-07](flagged-for-review.html)). `captured_utc` is our source-read time, not an NFL-published timestamp.

On **13 November 2026 at 12:53 UTC**, all 32 club rows were re-read from the official division standings page and transcribed independently to `data/standings_recheck_20261113.csv`. The machine check compares every club and each of the eight published fields—W/L/T/PCT/PF/PA/NET PTS/STREAK—and reports **32/32 clubs, 256/256 values exact**. No standings value changed; this is a new source-read timestamp, not an NFL publication time. Each displayed row links to the official NFL read in the source registry.

{{csv data/standings_2026.csv;;cols=team:Club,abbr:Abbr,conf:Conf,div:Div,w:W,l:L,t:T,pct:Pct,pf:PF,pa:PA,net:Net,streak:Streak,captured_utc:Read UTC;;source_col=source;;caption=Official division-view standings, captured at 2026-11-13T12:53Z. All 32 clubs and eight published fields matched the saved official re-read; capture time is not the NFL's publication time. Earlier staleness and correction are documented in FL-35.}}

## Completed results, weeks 1–9

This is the only historical corpus in the project, and it came from a **parallel session** (`arena-009ec582`) that transcribed the league's week-by-week schedule pages. It was not taken on trust: it was re-audited here, row by row, and then used as an independent check on the standings table above. Two pages fetched separately, transcribed separately, agreeing on all {{metric games_log_reconciled}} clubs' wins, losses, ties, points for and points against, is the strongest verification available without a second data vendor.

The reconciliation is computed on every build by `tools/verify.py`, including the saved official-read comparison, and published from the measurement, not from a note:

- {{metric games_log}} rows, {{metric games_log_weeks}} weeks, **{{metric games_log_links}} of {{metric games_log}} rows carry an official nfl.com game URL** — the import refused to write a row without one.
- Recounting the log gives {{metric games_log}} games — {{metric games_log_away_wins}} away wins, {{metric games_log_home_wins}} home wins and {{metric games_log_ties}} tie — with ΣPF = ΣPA = {{metric games_log_pf}}. At club level that is {{metric games_log_club_w}} W / {{metric games_log_club_l}} L / {{metric games_log_club_t}} T, which is exactly what the standings table showed for weeks 1–9 (one tie counts for two clubs, which is why the club totals sum to twice the game count).
- Per-club match: **{{metric games_log_reconciled}} of 32 clubs match exactly on W, L, T, PF and PA; {{metric games_log_mismatched}} mismatch** — measured against the standings table, which additionally carries the {{metric games_log_settled_after_corpus}} Week 10 game that has settled since this corpus was cut.
- Bye arithmetic closes: {{metric games_log_byes}} clubs show 8 games and the rest show 9, and the empty game-slots (16 per week × 9 weeks − {{metric games_log}} games = 8) times two clubs equals the {{metric games_log_byes}} byes exactly.
- {{metric games_log_neutral}} games are neutral-site/International Games; any home-field feature must exclude them, which is why the log carries the flag per row.

{{csv data/games_2026_wk1_9.csv;;cols=week:Wk,date:Date,away:Away,away_pts:A,home:Home,home_pts:H,neutral:Ntr;;source_col=source;;group=week;;caption=Final scores as published on each game's official page. Weeks 1–9 only; week 10 is in progress and appears in the schedule table below. Away-at-home order follows the league's own fixture title.}}

## Week 10 slate

{{csv data/schedule_2026_wk10.csv;;cols=game_id:ID,date:Date,kickoff_et:Kickoff ET,away:Away,home:Home,venue:Venue,tv:Broadcast,game_url:Game page:urls;;source=S-WK10REP;;show_source=0;;caption=Game page links are the league's own URLs for each fixture, as published in the official week-10 report.}}

## What the schedule itself contributes as a feature

Two of these games are structural exceptions a model must not treat as ordinary, and both are verifiable from the official schedule alone — no external dataset required:

- **NE at DET, 09:30 ET in Munich.** A non-standard kickoff hour and an intercontinental trip for one club. We publish the fact, not a coefficient: the adjustment stays at zero until measured ([SIG-10](signals.html)).
- **BAL Monday night, following a club that played Thursday the week prior.** Rest asymmetry is computable from kickoff timestamps only, which makes it the cheapest defensible situational feature in the whole catalogue ([SIG-09](signals.html), [S-16](suggestions.html)).

## League-wide reconciliation performed on this page's data

| Check | Result |
| --- | --- |
| Σ wins = Σ losses across 32 clubs | pass — {{metric league_w}} and {{metric league_l}}, with {{metric league_t}} ties counted on both sides |
| Σ points for = Σ points against | pass — {{metric league_pf}} and {{metric league_pf}} |
| Σ net points = 0 | pass |
| [Official standings read (2026-11-13T12:53Z)](https://www.nfl.com/standings/) vs saved 32-club snapshot | pass — 256/256 W/L/T/PCT/PF/PA/NET PTS/STREAK values exact |
| Winning pct = (W + ½T) ÷ (W + L + T) | pass for all 32 rows |
| Net = PF − PA | pass for all 32 rows |
| Games played consistent with week 10 of the schedule | pass — 8 or 9 games per club depending on bye placement, {{metric league_club_games}} club-games in total |
| Game log ({{metric games_log}} games) implies the standings table | pass — {{metric games_log_reconciled}} of 32 clubs identical on W-L-T, PF, PA |
| Every game-log row cites an official game page | pass — {{metric games_log_links}} of {{metric games_log}} |
| Neutral-site count agrees with the international slate | pass — {{metric games_log_neutral}} games |
