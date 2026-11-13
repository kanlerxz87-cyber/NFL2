# Week 11 — originated lines, pre-registered
> The forward sample. These are our lines for the thirteen games of 19–23 November 2026, written and hashed **before** any of them was played, so that the first honest measurement this project can make is a forecast rather than a fitted number.

**Decision timestamp: 2026-11-13T12:39Z.** The games kick off 19–23 November. Nothing on this page is eligible for staking: no strategy on the [leaderboard](leaderboard.html) has cleared a [validation gate](validation-gates.html), and these lines are unvalidated paper output.

## What was published, and what it is measured against

{{csv data/originated_lines_wk11_0a113a24.csv;;cols=game_id:Game,date:Date,kickoff_et:Kickoff (ET),away:Away,home:Home,our_spread_home_favoured:Our spread (home),our_total:Our total,home_net_rating:Home rating,away_net_rating:Away rating,home_field_advantage_applied:HFA applied,archive_spread_home_favoured:Archive spread,archive_total:Archive total,spread_gap_vs_archive:Spread gap vs archive,total_gap_vs_archive:Total gap vs archive,availability_load:Availability,status:Status;;source_col=source;;caption=A spread column holds the predicted HOME margin: positive means the home club is favoured. Ratings are the ridge simultaneous-ratings net values the line is built from; HFA is the measured home-field coefficient, set to zero for the one neutral-site fixture. The archive columns are the community archive in pipeline/data/raw/games.csv, which is NOT official and whose vintage is undocumented (FL-29, FL-30) - they are a comparison anchor, never a source of truth. Availability is blank because the league has not published Week 11 participation (FL-38).}}

Three things in that table are worth the reader's attention before any number in it.

**Our lines are materially less extreme than the community archive's.** The mean signed gap between our spread and the archived spread is **−3.5 points**: in 12 of the 13 games we sit closer to a pick'em than the archive does. The archive's widest lines are Kansas City over Arizona by 14 and Buffalo over Miami by 16.5; we have 8.5 and 10. That is not a claim of superiority in either direction — it is the arithmetic consequence of a model whose fitted home-field coefficient is **0.18 points** and whose team ratings are shrunk hard by the ridge penalty. If these lines were ever taken somewhere, they would be a smaller position than the market's, not a contrarian one.

**The totals are the weak half.** Our totals are above the archive's in 8 of 13 games and below it in 4, with a mean gap of +1.1 points. The [Fair-Line Lab](model-lab.html) has already measured the pace half of this model against a league-mean baseline on 88 out-of-sample games and found it does not beat it. The totals are published as a diagnostic, not as a line.

**The Mexico City game is handled explicitly.** Minnesota at San Francisco is the only fixture the official schedule page marks as an international game, so the home-field term is set to zero for it and the archive's line for it is the only comparison that is not apples to apples.

## The pre-registration record

{{csv data/prereg_week11_0a113a24.csv;;cols=field:Field,value:Value,meaning:What it means;;source=S-PREREG-0A11;;caption=Published before the first kickoff. The hashes are recomputed by tools/grade_forward.py before it grades anything: if a line is edited after this moment, the pre-registration is reported BROKEN, the grade is withheld and the script exits non-zero. That was tested, not asserted - see the note under the grade table below.}}

Two of those hashes matter most. `lines_sha256` is the fingerprint of the thirteen lines above; `backtest_corpus_sha256` is the fingerprint of the 136-game weeks 1–9 corpus, which is the file the whole backtest was built on and which stays byte-identical so that every grade already published against it remains valid.

## The grade, which is empty on purpose

{{csv data/forward_grade_0a113a24.csv;;cols=game_id:Game,date:Date,away:Away,home:Home,our_spread_home_favoured:Our spread,our_total:Our total,actual_home_margin:Actual margin,actual_total:Actual total,spread_abs_error:Spread error (pts),total_abs_error:Total error (pts),baseline_spread_abs_error:Do-nothing spread error,baseline_total_abs_error:Do-nothing total error,spread_error_vs_baseline:Spread vs baseline,total_error_vs_baseline:Total vs baseline,status:Status;;source_col=source;;caption=One row per pre-registered line. Nothing is settled yet, so every result cell reads "not published". The two do-nothing columns are the bar: a predictor that writes the weeks 1-9 league average every time. The last two columns are the difference between our error and that bar's, and they are the only columns on this page that can ever show a strategy ahead.}}

{{csv data/forward_grade_summary_0a113a24.csv;;cols=metric:Metric,value:Value,method:How it is computed,read:Read;;source_col=source;;caption=Recomputed on every run by tools/grade_forward.py. The sample-size rows are the reason the performance rows above cannot be read as a ranking: detecting a 1.0-point difference in mean absolute error at 80 per cent power needs about 1,382 games on spreads and about 1,607 on totals, and the whole 2026 regular season is 272 games.}}

## How this was proved to be the same model

The Week 11 lines are produced by `tools/originate_week11.py`, which is a **re-implementation** of the model in `scripts/origination_lab.py` — and a re-implementation is exactly the kind of thing that should not be trusted. So the script proves itself before it writes anything:

> it re-derives all **fourteen published Week 10 lines** from the frozen weeks 1–9 corpus, using the same code path, and compares every spread and every total cell with `data/originated_lines_wk10_a392.csv`. If a single cell differs, it exits non-zero and writes nothing.

The guard passed on every run in this session: 14 of 14 lines re-derived, every spread and every total identical. The two implementations are therefore proved identical on fourteen published games before either is trusted on thirteen new ones.

The tamper guard was tested the same way. Editing one spread in the pre-registered file from 5.5 to 1.5 — one cell, one game — makes `tools/grade_forward.py` report `BROKEN`, withhold the grade and exit 1; restoring the file returns it to `intact`. That is the difference between a pre-registration and a promise.

## The slate these lines are built on

{{csv data/schedule_week11_2026.csv;;cols=game_id:Game,date:Date,kickoff_et:Kickoff (ET),away:Away,home:Home,site:Site,neutral:Neutral,tv:Broadcaster,game_url:Official game page;;source_col=source;;caption=Read from the official Week 11 schedule page on 2026-11-13T12:39Z. The venue column is blank on thirteen of thirteen rows because the official schedule page does not publish venues - only the game centre does, and it was not read for every fixture in this session (S-55). The Mexico City row is the one fixture the official page marks as an international game.}}

## Two broadcasters moved, and the evidence that says so

{{csv data/week11_broadcaster_change_0a113a24.csv;;cols=fixture:Fixture,value_published_2026_11_09:Published 9 Nov (league announcement),value_published_2026_11_13:Published 13 Nov (live page),change_window:Window,conclusion:Conclusion,note:Note;;source_col=source;;caption=FL-36, resolved. The repository's transcription was made from the league's own dated Week 11 Schedule Change article of 9 November 2026, and it matches that article cell for cell. The live schedule page read on 13 November lists the same two fixtures with the broadcasters exchanged. The league moved the two broadcasts; the earlier transcription was not wrong when it was made.}}

This is the kind of episode the project wants on the page rather than in a commit message, because it is the difference between a stale publication and a wrong one — and only a dated second source can tell them apart.

## What was re-verified to build this page

{{csv data/reverification_0a113a24.csv;;cols=check:Check,scope:Scope,official_value:Official value,published_value:What this repo published,result:Result,note:Note;;source_col=source;;caption=Read against the live official pages on 2026-11-13 between 12:30Z and 12:40Z. 102 rows: 95 match, 2 MISMATCH (the two broadcaster cells above) and 5 rows that say NOT CHECKED so the register is never read as a full re-verification. Every row carries the official page it was read from.}}

## What this page does not do

- It does not stake anything, and it does not claim an edge. The model this line comes from has a spread mean absolute error of 9.28 points against 10.46 for a do-nothing baseline on 88 out-of-sample games, and a **paired** gap against the archived price that is *worse* by 0.295 points with a bootstrap interval that excludes zero. It is a better guess than nothing and a worse guess than the market.
- It does not price availability. The league had not published Week 11 participation at the decision timestamp, so the column is blank rather than zero (FL-40, Q-47).
- It does not use a price feed. The league publishes no betting lines; the archive it is compared against is non-official with an undocumented vintage (FL-29, FL-30).
- It does not touch the frozen corpus. Week 11 results go to `data/games_week11_played.csv`, which is append-only and separate, exactly as week 10 results are (Q-41, S-26).
- It does not promote a strategy. The [leaderboard](leaderboard.html) is still unranked, and its ranking column stays hidden until a strategy clears [G-01 to G-11](validation-gates.html) and reaches 400 settled bets.

## What happens next

1. The thirteen games are played on 19–23 November.
2. Their final scores are appended to `data/games_week11_played.csv`, each with its official game URL.
3. `python3 tools/grade_forward.py` re-checks the pre-registration hashes, scores the lines against the official final scores and rewrites the two tables above.
4. The [leaderboard](leaderboard.html) shows thirteen settled forward observations and the sample-size arithmetic beside them — which will still say that thirteen observations cannot decide anything, and that is the correct thing for it to say.
