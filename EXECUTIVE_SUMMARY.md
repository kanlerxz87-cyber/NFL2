# Executive summary — NFL 2026 verified analytics

**Built:** 2026-11-12 · **Updated:** 2026-11-13 (session `0a113a24`) · **Data through:** Week 9 results, Week 10 injury reports

> **Current summary:** the site's [executive summary](executive-summary.html) is the maintained version. As of 13 Nov 2026 it adds a pre-registered Week 11 forward sample: 13 lines hashed before kickoff, a grader that refuses edited lines, and a 102-row re-verification register (95 match, 2 explained mismatches under FL-36, 5 not checked). The Week 11 games have not been played; no performance claim is made.
**Live site:** https://kanlerxz87-cyber.github.io/NFL2/
**Code and data:** https://github.com/kanlerxz87-cyber/NFL2

---

## What this is

A working NFL analytics build on a single rule: **every number either traces to an official NFL
source or is explicitly labelled as model output.** Nothing is inferred. Where a value could not be
confirmed it is blank on the site and listed on the Flagged for Review page. Where an official table
could not be decoded, it is named as withheld rather than filled in with a plausible guess.

That rule is what most of the findings below are actually about, because it repeatedly turned out to
matter more than the analysis did.

---

## The five things a decision-maker needs to know

### 1. The data is verified, and the verification is arithmetic rather than editorial

The 136-game log of weeks 1–9 reproduces **all 32 clubs'** W-L-T, win percentage, points for, points
against, net points and current streak. Every club matches on every field. That is 10 of 10 hard
checks.

The team statistics rest on eight exact conservation identities — league-wide offence equals
league-wide defence to the yard: 63,556 passing yards, 30,580 rushing yards, 641 sacks, 411 passing
touchdowns, 257 rushing touchdowns, 197 interceptions, 3,006 passing first downs, 1,757 rushing first
downs. Those identities are not decoration. The league's team-stat pages render with **no header
row**, so conservation is the evidence that the columns were mapped correctly.

### 2. Home-field advantage cannot be detected in 2026 — but the naive number is wrong and would have misled anyone

Pooled over all 136 games, the mean home margin is **+0.00 points** and home clubs are 67-68-1. That
looks like home-field advantage has vanished, and it is the number a careless build would publish.

It is wrong. Seven games were played at neutral sites and have no true home club. Restricted to the
**129 genuine home games**, the mean home margin is **+0.50 points, 95% CI [−1.80, +2.79]**, with a
home win rate of .5155.

The conventional ~+2.5 point prior sits **inside** that interval. So the correct finding is not
"home-field is gone" — it is **"2026 is too small a sample to say anything about home-field at
all."** The model uses +0.50 and states the uncertainty on every page where the number appears.
Closing the question needs multiple seasons (suggestion P-05).

### 3. Zero of six strategies are validated, and that is the honest result

Six strategies were specified, implemented and backtested walk-forward across weeks 5–9, with the
ratings for each week using only games played before it. Seven gates decide whether a strategy has
earned the right to be called an edge.

**Every strategy is UNDERPOWERED.** The largest graded sample is 72 legs against a gate requiring
200. Three strategies pass four of the seven gates, which is encouraging and currently means nothing.
No reward is paid while a strategy is underpowered, and the leaderboard is sorted by gates passed
rather than by hit rate, so the top row cannot be mistaken for a recommendation.

There is also no way to test profitability: **no official NFL source publishes odds.** Every result
on the site is therefore a hit rate and a Brier skill score, never a return. A project showing you an
ROI without an odds source is guessing.

### 4. Starter-versus-backup is answered for 4 clubs, and honestly blank for 28

The official injury report says who is hurt and how much they practised. It does **not** say whether
they start. Joining it to each club's own published depth chart resolves that — for Kansas City,
Green Bay, New England and Detroit, the four charts transcribed and verified here.

The join produces genuinely useful findings: **ten verified first-string absences** across those four
clubs, including five at Green Bay, plus a breakdown of second-, third- and fourth-string absences.
It also surfaces something a naive join would hide: **12 injured players do not appear on their own
club's published chart at all.** They are flagged rather than silently assigned a depth.

For the other 28 clubs, 203 of 254 injury rows carry a blank depth position. Transcribing and
publishing them unverified would have broken the project's central rule, so they are blank (P-02
proposes finishing the job).

### 5. Two leaderboards are withheld because their columns cannot be proven

The rushing and receiving leaderboards render without a header row. No arithmetic identity
identifies their columns: published yards-per-carry disagrees with yards divided by carries for every
sampled row (Bijan Robinson 5.2 versus 5.0, Kenneth Walker 5.5 versus 7.0, Jahmyr Gibbs 4.8 versus
9.0), and yards-per-reception and yards-per-game fail identically.

Both tables are **withheld entirely.** Only 8 passing lines are published, and each is published
because all 15 of its values equal the club's official team passing line exactly — an equality that
can only hold if that player was the club's sole passer, and which simultaneously proves the column
order. Detroit's Jared Goff fails the test (2,134 against a club figure of 2,145) and is excluded
rather than reconciled.

---

## What is on the site

| Page | What it answers |
|---|---|
| **Overview** (`index.html`) | The dashboard: coverage, verification state, the five findings |
| **Results** (`results.html`) | 136 games, each with score, date, margin and its own source link |
| **Standings** (`standings.html`) | Official standings with an independent recount beside each club |
| **Team stats** (`teams.html`) | Passing and rushing, offence and defence, with withheld tables named |
| **Injuries & Depth** (`injuries.html`) | Week 10 injury report joined to published depth charts |
| **Analysis** (`analysis.html`) | Power ratings, correlations, luck ladder, model lines |
| **Strategies** (`strategies.html`) | Six strategies, seven gates, per-fold stability, parlay arithmetic |
| **Method** (`method.html`) | The five rules, the verifier, the model, and where it is weak |
| **Data Sources** (`sources.html`) | Every official page used — and every one tried and rejected |
| **Questions** (`questions.html`) | 24 questions with answer status and a route to closing each one |
| **Suggestions** (`suggestions.html`) | 12 proposals with cost, validation and risk — none implemented |
| **Flagged for Review** (`flagged.html`) | Nine irregularities, five withheld datasets, severity-rated |

All 12 pages are generated from JSON by `scripts/build_site.py`. No figure is typed by hand into a
page, so no figure on the site lacks a provenance chain.

---

## Verification state

| Layer | Result |
|---|---|
| Data checks (`scripts/verify_data.py`) | **20 / 23** pass — the 3 failures are soft and published |
| Personnel checks (`scripts/verify_personnel.py`) | **9 / 9** pass |
| Site checks (`scripts/verify_site.py`) | **12 / 12** pass |
| Game log → official standings | **32 / 32 clubs** match on every field |
| League-wide conservation identities | **8 / 8** hold exactly |

The three soft failures are real source-level inconsistencies, not build errors: Kansas City's club
page total-offence figure is 70 yards short of its own team-stat components; Washington's published
completion percentage does not recompute from its own completions and attempts; and yards per attempt
disagrees for four clubs under every candidate denominator tested. All three are published with the
recomputation shown beside the published value.

---

## What is missing, and how to get it

| Gap | Why it is missing | How to close it | Ref |
|---|---|---|---|
| Odds, spreads, totals, prop prices | No official NFL source publishes them | Licensed, timestamped odds feed | P-06 |
| Player-prop correlations | No per-game player box scores in this dataset | Fetch gamebook pages (≈122 reads for the season) | P-01 |
| Depth position for 28 clubs | Only 4 charts transcribed and verified; the 13 Nov read joins them to 18 unavailable names | Transcribe 28 club charts (S-48 costs the 4 first) | P-02 |
| Rush/receive leaderboards | Column order unprovable | Per-player pages with labelled headers | P-01 |
| Multi-season baseline | Single season only | Add 2023–2025 game logs | P-05 |
| Snap counts | No official NFL.com snap table found | Licensed feed | P-12 |

Twelve proposals are set out on the Suggestions page with effort, impact, validation method and the
risk of each. None is implemented. The governance rule is that a proposal is a decision for review,
never a finding to be shipped.

---

## Added 2026-11-13 12:45Z — availability, and the first locked call (session `66faefac`)

Two things the project did not have before today.

**A third read of the same official page, published beside the first two instead of over them.** The
Week 10 injury hub now stands at 296 rows across the whole 28-club slate — 26 clubs filing names, two
publishing `No Injuries Reported` — against 279 at 22:35Z and 254 at 04:45Z, with 90 non-participants,
115 limited reports, 91 full reports and 9 game designations. No club's list shrank in either interval.
Availability is then joined to the club's own depth chart: 18 unavailable names, 8 of them sitting in a
printed 1st-string column, 3 groups left with no charted body behind the absent player, and one row
that contradicts itself (Detroit's Kerby Joseph: full practice, `OUT` designation) published as a
conflict rather than resolved. Twenty-four line-by-line checks against live official pages are in
`data/reverification_66faefac.csv` (12 confirmed, 5 newly published, 3 still standing as mismatches, 4 explicitly not
re-checkable today) — and they include a correction against us: the previous session's
"Minnesota DNP 6→3" claim does not reproduce (MIN holds 9 rows, unchanged), so it is withdrawn here.

**A prediction pinned before the games it predicts.** Rule ST-15 — take the healthier club when the
availability load differs by four or more — was written at 12:45Z, four hours before the earliest
kickoff, and hashed: `sha256 1186474bab75dd41…`, 14 fixtures, 2 locked calls, 12 recorded no-calls,
every stake zero because gate G-07 is not passed and no licensed price exists. The threshold's whole
sensitivity curve (thresholds 1–6) is published with it, and so is the arithmetic that bounds what the
result can ever mean: 1,382 games to detect a 1.0-point error difference, 400 settled bets before any
leaderboard claim. Two calls is a mechanism working, not evidence.

Pages: [Week 10 availability](https://kanlerxz87-cyber.github.io/NFL2/availability-1113.html) ·
[Pre-registration lock](https://kanlerxz87-cyber.github.io/NFL2/preregistration.html) ·
[Flagged for review](https://kanlerxz87-cyber.github.io/NFL2/flagged-for-review.html) (FL-36 to FL-59).

---


## Addendum — session `2268bfb2`, 13 November 2026: the competition is finally scored

Everything above was written before any strategy in this repository had been scored against a settled
game. This session changed that, and the result is uncomfortable enough to lead with.

**1. Our own lines do not beat knowing nothing.** Ten pre-registered candidates were scored on 596
decisions across 72 holdout games (weeks 5–9), with coefficients fitted only on weeks 2–4 and every
team feature computed from games strictly earlier than the one being predicted. Our originated spread
misses by 11.03 points per game; predicting that the home team wins by nothing misses by 10.92. Our
originated total misses by 11.21 against 11.18 for the point-in-time league mean. The correlation
between our predicted home margin and the actual margin is r = 0.031 (p = 0.80) — indistinguishable
from no relationship. This is the same wall session `63ac21e9` hit with thirteen seasons of data, and
it is published rather than tuned away. ([FL-72](flagged-for-review.html))

**2. The best number on the site is the least trustworthy.** The highest hit rate is 79.2%, from a
rest-advantage signal, and it survives a Benjamini–Hochberg correction at a 10% false-discovery rate
(exact binomial p = 0.0066). It is also 24 decisions, six weeks, one season, and an effect larger than
any rest effect has a right to be. Ten coin-flipping selectors produce a best-of-ten of 70.8% or better
one time in twenty by luck alone. It is ranked by log loss, shown in full, and deliberately **not
promoted**, because the build's own 40-decision floor exists to stop exactly this number.
([FL-71](flagged-for-review.html))

**3. A 68% hit rate is not an edge.** The strongest genuine signal — pick the team with the better
season point differential — wins 45 of 66. That is what being the favourite means, not evidence of
skill, and without a price nobody can say whether the market already charged for it. The one number
that would settle it, the closing line, is the one number this repository does not have.

**4. The same-game correlations the brief asked for are now measured, not modelled.** Fifteen pairs
over six legs, n = 72. The extremes are the point: home-team-wins × home-beats-our-spread sits at
φ = 0.945, meaning a two-leg ticket on them is one bet sold twice (the independence assumption would
price it at 17.4% when it hits 41.7% of the time); home-wins × away-scores-24+ sits at φ = −0.64.
Prop-leg correlations remain blank, because no prop-line archive exists. ([FL-69](flagged-for-review.html))

**5. Six Week 10 game ids disagree between two published files.** Three of them, `W10-06`, `W10-07`
and `W10-08`, name a completely different fixture in `data/injuries_2026_wk10.csv` than they do in
`data/schedule_2026_wk10.csv`. A join on `game_id` silently attaches six clubs' injury rows to the
wrong opponent. Nothing in this repository joins them today; the defect is published rather than
patched, because the file belongs to another session's scope. ([FL-64](flagged-for-review.html))

**6. The live hub has moved 41 rows past what the site shows.** Re-read at 2026-11-13T12:40Z it
publishes 295 rows across 26 clubs; the Injuries page renders 254 across 24. Against session
`a392a193`'s re-fetch fourteen hours earlier it shows 17 additions, 1 removal and 51 changes. That is
not an error, it is what a daily report does — but no cumulative table on this site states when it was
read, so a reader cannot tell a snapshot from a stale one. ([FL-65](flagged-for-review.html))

**7. Depth is now answered with strings attached.** New England and Detroit's own published charts were
joined to the league's filing, producing the cascade the brief describes: with Rhamondre Stevenson
limited and TreVeyon Henderson ruled out, the next available back is the 3rd string and then the 4th.
Two caveats travel with it — the clubs label their charts *unofficial*, and the league publishes no
depth chart at all. Where a club's chart omits a player (Kerby Joseph) the cell stays blank.
([FL-67](flagged-for-review.html), [FL-68](flagged-for-review.html))

### What this addendum changes about the bottom line

Nothing above is retracted, and one thing is now stronger: the claim that this project publishes its
own failures now covers its model's performance, not just its data gaps. Five reward tiers exist, ten
validation gates are defined, four pass and six block. Every tier that would carry a stake is blocked
by the same missing input — a licensed, timestamped price feed. Until that decision is made
([Q-01](questions.html)), this site can tell you how accurate a line is and never whether it was worth
betting.

---


---

## Bottom line

The dataset is verified to a standard that lets you check it yourself. The modelling is deterministic
and reproduces byte for byte. The strategies are gated and **none of them has passed**, which is
stated before any hit rate is shown. The injury-depth join is real for four clubs and visibly blank
for twenty-eight rather than quietly fabricated. Two official tables are withheld because nobody can
prove what their columns mean.

The most useful thing this build demonstrates is not a prediction. It is that a project can publish
its own failures — nine irregularities, five withheld datasets, three soft verification failures,
zero validated strategies — and still be worth reading, because everything it does claim is
checkable.
