# Pre-Registration Lock — Week 10
> The first prediction this repository has ever pinned before an outcome existed: one rule, one threshold, fourteen fixtures, a SHA-256, and a grading tool that fails if the file is touched afterwards.

**The rule, in one sentence.** Our published number for a game is built from points scored and allowed through week 9, so it cannot see who is playing this week; when one club's availability load — designated out plus did not practise, counted off the league's own filing — is at least four players heavier than the opponent's, we lean the *healthier* club against our own line, and every other fixture is recorded as a no-call rather than dropped.

That is ST-15 on the [strategy registry](strategies.html). It was written at **12:45 UTC on 13 November 2026**, four hours before the earliest Week 10 kickoff (14:30 UTC, Munich), from a hub read taken in the same hour. The file `data/prereg_wk10_66faefac.csv` is hashed in `data/prereg_wk10_66faefac.sha256`, and `python3 tools/verify_prereg_66faefac.py` recomputes every derived cell from the inputs: an edit to a count, a threshold or a call now changes the hash and the check fails.

## The ledger

{{csv data/prereg_wk10_66faefac.csv;;cols=game_id:Game,date:Date,away:Away,home:Home,away_load:Away load,home_load:Home load,load_delta:Differential,call:Call,side_taken:Side,locked:Locked before kickoff,our_spread_home:Our spread (home),our_total:Our total,fair_spread_home:Points-only spread,stake_units:Stake;;source_col=source;;caption=Load is designated-out plus did-not-practise players on the official hub, one per player. Differential is away minus home, so a positive number means the visitor is the more depleted club. Stake is zero for every row: gates G-01 (entitlement) and G-07 (vig and cost accounting) are not passed, so nothing here is a bet — it is a directional record against our own published number, which is the only number this repository can honestly be measured against without a price feed.}}

Two calls out of thirteen un-played fixtures — a 15% hit rate on the slate, which is what "selective" is supposed to mean, measured rather than asserted:

- **W10-06 Miami at Indianapolis.** The Colts file a load of six — six non-participants and no designations, so nothing in that number is double-counted — against the Dolphins' two, so the lean is Miami. Both clubs are missing a quarterback in the wider sense: the league's own reporting has Miami placing Malik Willis on injured reserve, which removes him from the weekly report altogether — so the count says Indianapolis is the depleted club while the transactions say the opposite. That inversion is the blind spot [Q-42](questions.html) is about.
- **W10-11 Seattle at Las Vegas.** Six Seahawks non-participants against a Raiders block of four rows and a load of zero, so the lean is the home side. Seattle's six non-participants include the quarterback the league's own reporting rules out (Darnold, with Drew Lock again starting), and the Raiders' entire block is four rows.
- **The fixture that got away, and the one that should worry us.** San Francisco at Dallas sits at −3, one player inside the threshold, on a day when Dallas filed nine non-participants. Green Bay against Minnesota is the harder case: four 1st-string columns are empty for Green Bay, Minnesota files six non-participants, and the rule sees a +1 differential and passes. A body count cannot tell a starting running back from a fourth-string long snapper. That is the finding this experiment is designed to produce, and it is why [S-49](suggestions.html) proposes splitting the load by chart column.

## The threshold was chosen once — and here is what choosing it differently would have done

{{csv data/prereg_sensitivity_66faefac.csv;;cols=threshold:Threshold,games_called:Fixtures called,share_of_slate:Share of the un-played slate,note:Status;;source_col=source;;caption=Published so that a reader can see how much of the two-call result is the rule and how much is the number we happened to pick. Only the threshold-4 row was locked; the others are shown for context and were not used to decide anything. If a future session re-tunes the threshold after the results are known, every row in this table is the evidence that it did.}}

## What the one settled game says, and what it does not

Washington at New York finished before this rule existed, so it is **not** part of the locked sample. It is published anyway, because hiding it would be worse than showing it: the rule would have taken the home side (Washington filed five unavailable players, the Giants zero), the Giants lost by 3 against our published 2.5, and the call misses. One row. [The settled page](week10-settled.html) has the full four-way comparison for the same fixture, where our spread lost to a do-nothing season mean by 2.5 points.

The arithmetic on required sample is already on this site and does not move for anyone: detecting a 1.0-point difference in spread error at 80% power and a 5% level needs **1,382 games** off the 136-game verified corpus, and gate G-08 sets n ≥ 400 settled bets before any strategy claim. Thirteen fixtures is 1% of the first figure; the two locked calls are half a percent of the 400 the gate demands. A 2-of-2 start would be luck; a 0-of-2 start would be luck; the number of bets per week this rule allows is the only thing that is real information here.

## How this becomes a leaderboard entry rather than a note

1. The games settle on 15–16 November. Rows are appended to `data/games_2026_wk10_played.csv` — never to the frozen weeks 1–9 corpus, which [S-26](suggestions.html) pins by hash.
2. `python3 tools/compute_settled_wk10.py && python3 tools/compute_availability_66faefac.py && python3 tools/build_site.py` re-scores the settled page and re-emits the pre-registration, which must produce a byte-identical locked file; `tools/verify_prereg_66faefac.py` then prints hits and misses against the official margin.
3. If the file re-hashes differently, the lock is broken and the strategy does not move up a tier — that is gate G-11 doing its job, not a build failure to route around.
4. Rewards stay unallocated through this whole sequence. [The leaderboard rules](leaderboard.html) pay on measured CLV and settled volume, and neither exists while the price feeds in [Q-01](questions.html) are unlicensed. An entry with locked calls and no settled bets sits at T0, which is where the tier table says it belongs.

## What is deliberately missing from this file

- **No point margin is claimed.** The lean is a side, not a number of points. Any conversion from "four unavailable bodies" to "points" would need a positional value that no official source publishes — see [the fair-line lab](model-lab.html), where the same restraint leaves the weighting columns blank.
- **No correlation adjustment.** These are single legs, one per fixture, so the parlay coupling questions on the [correlation page](correlation.html) do not arise; a same-game second leg would have to clear gate G-05 before it could be added to a locked row.
- **No live price.** The comparison beside our number is a column in a vendored community archive whose open-or-close vintage has never been documented ([FL-30](flagged-for-review.html)), not a closing price captured at decision time. The whole story is on the [price archive page](price-archive.html), and it is why the stake column reads zero.
