# Fixture context — features built only from published schedule facts

> BL-14 asked for a fixture-context feature set built **only** from published schedule facts. This is it:
> twenty-six rows, one per club-fixture side of the Week 11 slate, every feature derived from a date, a
> kickoff time, a venue and a result that an official page publishes. Nothing here comes from a model, a
> third party, or an assumption about how tired a team "should" be.

The point of the set is that these are the features you can have for **every** fixture, forever, without
waiting for an injury report, a depth chart or a price feed. They are also the features most likely to be
silently double-counted: rest and bye are the same information at two resolutions, and a divisional flag
is already partly inside any rating that was fitted on divisional games.

## The set

{{csv data/fixture_context_0a28b225.csv;;cols=side_id:Side,date:Date,kickoff_et:Kickoff (ET),team:Team,opponent:Opponent,home_away:Home/away,venue_city:Venue city,et_offset_hours:ET offset,local_kickoff:Local kickoff,prev_game_date:Last game,prev_game_status:Last game status,rest_days:Rest (days),off_bye:Off bye,short_week:Short week,opp_rest_days:Opp rest,rest_edge_days:Rest edge,divisional_game:Divisional,conference_game:Conference,kickoff_window:Window,neutral_site:Neutral;;source_col=source;;caption=One row per club-fixture side; 26 rows for 13 fixtures. Rest is the difference in days between this fixture's date and the club's most recent earlier game in the official results files. Blank cells are blank on the official page.}}

## What the Week 11 slate actually says

Read off the register above, these are the facts that would move a number:

- **Four clubs come off a bye**: Chicago, Denver, Philadelphia and Tampa Bay. Each carries a
  **+7 day rest edge** into its fixture — the largest structural edge on the slate, and it appears in
  W11-04 (NO at CHI), W11-06 (TB at DET), W11-08 (PIT at PHI) and W11-10 (LV at DEN).
- **Two clubs are on a short week because of the Monday night game**: Baltimore and the LA Chargers both
  played on 16 November and both play again on 22 November — six days. Baltimore carries a **−1 day**
  edge at Carolina (W11-03); the Chargers carry **−1** at home to the Jets (W11-09).
- **The Thursday game is short for both sides.** Indianapolis and Houston both last played on 15
  November, so W11-01 is four days' rest each and the rest edge is exactly zero. Anyone pricing that game
  off a rest differential is pricing noise.
- **The two largest edges are not byes.** The Giants (W11-11) last played on 12 November and get ten days
  before Jacksonville's seven — a **+3** edge. Washington (W11-13) gets eleven days against Cincinnati's
  eight — also **+3**. Both come from a Thursday appearance in Week 10, not from a bye.
- **Body clock is the one feature the schedule hides in plain sight.** The Jets at Chargers (W11-09)
  kicks at 16:05 ET, which is **13:05 local** in Inglewood. Raiders at Broncos (W11-10) is 16:25 ET and
  **14:25 local** in Denver. Saints at Bears is 13:00 ET and **12:00 local** — an early-body-clock road
  game. The offset is a static geographic constant from the venue's state, listed in the builder and
  audited by the verifier; it is not an NFL-published fact and is not published as one.

## How each column is derived

| Column | Derivation | Input it comes from |
| --- | --- | --- |
| `rest_days` | fixture date minus the club's most recent earlier game date | `data/games_2026_wk1_9.csv`, `data/games_2026_wk10_played.csv` |
| `prev_game_status` | `Final` when a result is on file; otherwise the scheduled date is used for rest and the row says so | Week 10 schedule file |
| `off_bye` | the club has no Week 10 fixture at all | `data/schedule_2026_wk10.csv` |
| `short_week` | rest of six days or fewer | derived |
| `opp_rest_days`, `rest_edge_days` | the other side's rest, and this side's minus that | derived; the two sides' edges are exact negatives |
| `divisional_game`, `conference_game` | same conference and division, from the published standings table | `data/standings_2026.csv` |
| `et_offset_hours`, `local_kickoff` | static offset for the venue's state, applied to the published ET kickoff | venue register |
| `kickoff_window` | weekday and hour of the published kickoff | Week 11 schedule file |

The one judgement call is W10-14. The Chargers at Ravens game is scheduled for 16 November and was not
final at read time, so both clubs' rest is counted from that date and the row prints
`scheduled, not final at read time` in `prev_game_status` rather than implying a result exists.

## What this set is not

- **It is not a rating.** No points, no yards, no injuries, no prices. Every column is a property of the
  calendar.
- **It is not independent across rows.** The two sides of a fixture share a venue, a kickoff and a window,
  and their rest edges are exact negatives. Treating 26 rows as 26 observations in a regression would
  roughly halve the effective sample; the fixture is the unit.
- **It is not yet a fitted model.** These are candidate features. Before any of them enters an originated
  line it has to clear the same gates every other signal clears, and the honest answer on this project so
  far is that none has: see the [validation gates](validation-gates.html) and the
  [measured correlations](measured-correlations.html), which still report no fitted market benchmark.
- **`venue_state` is blank for Mexico City**, because Mexico has no state. The offset for that row is
  Mexico City's own, and the verifier checks it.

## Method

1. `tools/build_0a28b225.py` reads the Week 11 schedule, the 136 completed results of weeks 1–9, the
   thirteen settled Week 10 results, the full Week 10 slate and the published standings table, then writes
   `data/fixture_context_0a28b225.csv`.
2. `tools/verify_0a28b225.py` recomputes every cell from those inputs — previous game, rest, bye, short
   week, mirrored opponent rest, the antisymmetry of the rest edges, divisional and conference flags, the
   timezone offset, the local kickoff and the kickoff window — and fails on any mismatch. 30 checks pass.
3. Reproduce with `python3 tools/build_0a28b225.py && python3 tools/verify_0a28b225.py`.

Sources: each row cites the official
[game-centre page](https://www.nfl.com/schedules/2026/by-week/week-11) for its own fixture
(`S-WK11-GC-0A28`); divisions come from the [official standings](https://www.nfl.com/standings/).
