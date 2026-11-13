# Executive Summary
> What exists, what is verified, what is missing, and the four decisions that unlock the rest — for Week 10 of the 2026 season, fetched 12 November 2026.

## The one-paragraph version

The collection layer now exists and is genuinely verified: 254 rows of the official Week 10 practice report across 24 of the 28 clubs playing that week, 227 official roster and depth events, 32 reconciled standings rows and a 14-game schedule, every row carrying a link to the official page it came from and nothing inferred to fill a gap. The analysis layer is specified in full — line-origination architecture, 18 signal families, 14 validation gates, a correlation framework with twelve pair classes, a sample-size protocol for removing luck, and a 14-entry strategy registry — but it produces no numbers yet, because two inputs do not exist in this project: licensed market prices and player-level participation data. The honest summary is that the pipeline and the rules are real, the data spine is real, and every performance claim you might want from this system is currently un-earnable rather than absent.

## What is verified and how we know

| Dataset | Volume | Official source | Reconciliation performed |
| --- | --- | --- | --- |
| Week 10 practice snapshot | 254 rows / 24 clubs | [nfl.com/injuries](https://www.nfl.com/injuries/) | transcribed row by row from the rendered table; participation strings mapped to three codes; no cell backfilled |
| Game-status designations | {{metric designations}} rows populated | [nfl.com/injuries](https://www.nfl.com/injuries/), [week-10 report](https://www.nfl.com/news/nfl-week-10-injury-report-2026-season) | the two official pages agree on every one; the remaining rows are blank in the source, which is not the same as zero |
| Roster / depth / IR events | 227 rows | [Wed 11-Nov roundup](https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11) | per-team blocks transcribed; typos in the source preserved and annotated |
| Completed results, weeks 1–9 | {{metric games_log}} games | [nfl.com/schedules](https://www.nfl.com/schedules/2026/REG/) plus one [official game page](https://www.nfl.com/games/) per row | imported from a parallel session and re-audited here: every row cites its own game page, and the recount matches the standings row for **{{metric games_log_reconciled}} of 32 clubs** on W, L, T, PF and PA — the strongest independent check available in this repo |
| Standings | 32 rows | [nfl.com/standings](https://www.nfl.com/standings/) | winning pct recomputed with ties counted as half; ΣPF ({{metric league_pf}}) = ΣPA ({{metric league_pf}}) and Σnet = 0 across the league, so the transcription is arithmetically closed |
| Week 10 schedule | 14 games | [week-10 report](https://www.nfl.com/news/nfl-week-10-injury-report-2026-season) | venues, kickoff times and network match the injury hub's own headers |
| Quarterback chain changes | 5 quarterback depth items: 3 confirmed starting changes, 1 coach declining to commit, 1 backup assignment | [roundup](https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11), [Darnold article](https://www.nfl.com/news/sam-darnold-ruled-out-for-seahawks-week-10-game-vs-raiders-drew-lock-expected-to-start-again) | each is a direct coach or league statement, not a report about a report |

## Five findings that matter for decisions

1. **The injury hub is a practice document, not an availability answer.** On the day we fetched, only {{metric designations}} of {{metric injury_rows}} rows carried a game status, and the Injury column was populated for {{metric injury_detail_cells}} — the same six filings. Anyone modelling availability off this table without the prose feed is modelling an empty column. ([FL-02](flagged-for-review.html), [FL-08](flagged-for-review.html))
2. **"No Injuries Reported" is a data state, not a health statement — and so is a missing club.** The live Week 10 hub labels only two clubs that way (LAC, BAL). Two more of the 28 playing clubs are simply absent from our file (SEA, CIN), which is a collection gap and not a claim those clubs are healthy. A third (IND) is partial. Reading any of the three states as zero is the most likely silent error in this system, so the snapshot now reports coverage as `{{metric injury_coverage}}` and refuses to phrase it as a sentence. ([FL-01](flagged-for-review.html), [FL-24](flagged-for-review.html))
3. **There is no official depth chart to buy or scrape.** The obvious URL is a 400-style error page, so the requirement about second, third and fourth-stringers has to be met by reconstruction — roster status, participation, designations, then actual playing time. That is a build item, not a lookup. ([FL-06](flagged-for-review.html))
4. **Roster churn in 2026 is large enough to break joins.** Players appear on clubs a naive pipeline would flag as errors; four of the surprising cases are independently confirmed by the same official page. We transcribed everything as published and made the 32-team roster sweep a gate (G-02) rather than quietly "fixing" the league's own data. ([FL-03](flagged-for-review.html))
5. **The parlay and prop-combo problem is a correlation problem before it is a pricing problem.** Same-game legs share a cause; independent-leg multiplication overstates parlay value; and the one piece of public research quantifying a cross-game parlay markup has an openly disputed matching method. We therefore publish the framework and the signs we can defend, leave every rho value blank, and publish the two correlations that *can* be measured from real game scores — C-07 at r = +0.076 and C-08 at r = −0.161 — both with intervals that include zero. ([correlation](correlation.html))

## What the system can and cannot do today

| Capability | Today | Earliest realistic state |
| --- | --- | --- |
| Answer "who is hurt and who is starting instead" for the current week | **yes for 4 charted clubs** — 17 measured cascades, 3 reaching a third string; depth rank blank for the other 28 | improves immediately with the 32-club roster sweep |
| Detect availability surprise (trend → designation) | no — needs three dated filings per week | after point-in-time storage lands (G-03) |
| Originate a number | **yes, stages 1–2** — 14 Week 10 fair totals and spreads, fully reproducible | stage 3 onward needs player data (Q-02) |
| Publish the residual against the market | no — no prices, so a residual would be invented | needs a price feed; 1 gate (G-01) and 1 vendor decision (Q-01) |
| Score a strategy on the leaderboard | no — zero tracked bets, by design | first week of forward tracking after pre-registration |
| Quantify replacement cost in points | no — needs snaps | after Q-02 closes |
| Prove an edge is not luck | protocol ready, no sample | 400 bets for the gate, 1,000 for promotion (S-08) |

## The four decisions to make now

1. Choose the price tier we originate against and start ingesting three seasons (unblocks 9 of 14 gates).
2. Approve the pre-registration rule that backtest numbers never appear on the leaderboard (S-04) — this is the decision that keeps the competition honest.
3. Decide whether v1 scope is spreads/totals/ML plus game props only (S-05), or the wider market set with a longer gate build.
4. Decide what the leaderboard actually pays (S-25); until then it is a readiness board, which is what we published.

## What the 12 November re-verification changed

This session did not take the previous build's word for anything. It re-fetched the official standings,
the Week 10 fixture list and all seven rendered chunks of the injury hub, and compared them row by row
against `data/`. The result is worth stating plainly because it cuts both ways.

**What held up exactly.** All **32 of 32** standings rows matched the live NFL page on wins, losses, ties,
winning percentage, points for, points against, net points and streak. All **14 of 14** Week 10 fixtures
matched on date, kickoff time, broadcaster and venue. Every one of the 254 injury rows that *is* in the file
matched the league's own table on name, position and practice status — there is no fabricated row anywhere.

**What did not hold up.** The published prose claimed more than the data supported, in four places:

| Claim | Reality | Now |
| --- | --- | --- |
| The snapshot covers `28 clubs` | it holds **24** of the 28 playing | reported as `{{metric injury_coverage}}`, derived from the fixture list |
| Empty blocks are **SEA, CIN, LAC, BAL** | only **LAC and BAL** say "No Injuries Reported"; SEA and CIN publish full blocks we never ingested | [FL-24](flagged-for-review.html) published, the stale assertion in [FL-01](flagged-for-review.html) corrected |
| **25** suggestions / **28** questions / **15** flags | 29 / 29 / 22 registers actually hold | all corrected, and now guarded by an audit |
| the repository holds **1 tracked file** | it holds **384** across seven merged sessions | the landing page states the real inventory |

The mechanism matters more than the errors. `tools/build_site.py` had **hard-coded** the empty-club list and
the `28 clubs` subtitle, so both were immune to the truth of the file next to them. Eight passing audit
suites never caught it, because every one of them compares the *site* to `data/` and none compares `data/`
to the *league*. That gap is now closed for these cases: the club set is derived from the fixture list, and
two new checks fail the build rather than warn. Both were tested with negative controls, which is recorded
on the [verification method](methodology.html) page.

**The lesson, for whoever runs next.** A number a file can be asked about must either be measured from that
file on every build or be absent. Prose counts rot silently, and a green audit suite is not evidence that
the data is still true — only that the site still agrees with it.

## What the 13 November settlement changed

One Week 10 game became official after the previous build — **Washington 24, NY Giants 21** on Thursday 12 November — and it is the first result any line on this site has been measured against. It is worth reading carefully, because it is a small sample that produces one flattering number and one unflattering one.

| What we published | What happened | Read |
| --- | --- | --- |
| Our spread, NYG −2.5 | Giants lost by 3 | **5.50 pts of error.** A predictor that wrote the league average of 0.00 every week was off by 3.00. Our lean cost 2.5 points against knowing nothing. |
| Our total, 45.5 | Actual total 45 | **0.50 pts of error** — the best number on the site, and the least meaningful. |
| Archived community price, 40.5 | Actual total 45 | 4.50 pts of error. We beat it by 4.0, but the league mean is 45.93, so the archive was the outlier. |
| Points-only fair line, NYG −5.0 / 48.0 | — | 8.00 and 3.00 pts of error. The simplest model here is also the worst on this game. |

The reason the 0.5 does not mean what it looks like is on the [Settled Week 10](week10-settled.html) page: this game's total landed 0.93 points from the league mean, and only **8 of the 136** verified games are that average or closer. A near-average game hands every predictor a cheap win. Detecting a 1.0-point difference in mean absolute error at 80% power needs roughly **1,400–1,600 games**; one settled game is 0.07% of that.

Two consequences for the programme:

1. **The standings refresh exposed a process gap, not a data one.** NYG and WAS were each one game stale. The two rows are corrected, but no cumulative table on this site states when it was read, so the next staleness will be just as invisible. That is [FL-35](flagged-for-review.html), [Q-40](questions.html) and [S-43](suggestions.html).
2. **The backtest corpus is now explicitly frozen.** The weeks 1–9 file keeps its published SHA-256 (`f0dffce0…6f33`) and week 10 results go into a separate append-only file, so no grade already published is silently re-baselined by a refresh.

The settlement pipeline works end to end. That is genuinely new and genuinely useful — it is the mechanism the leaderboard needs. It is not evidence that the model works, and nothing yet published could be.

## Standing risk to name plainly

Everything on the blue pages is a specification written before the data existed. Specifications are cheap in this domain and the record of betting models is poor; the gates and the negative controls (ST-12 do-nothing, ST-13 public-news echo) exist precisely so that a specification has to survive contact with results. Until then the correct posture toward any number on the origination pages is scepticism, and the site is built so that the blanks are visible rather than hidden.


---

## Added in the second verification pass, 12 Nov 2026 22:35–23:30Z (session `a392a193`)

The site you are reading was re-checked against the live official pages rather than against its own notes. Four things changed as a result, and all four are decision-relevant.

| What changed | The measured result | Where |
| --- | --- | --- |
| **The injury register is a timestamp, and it had moved.** A second read of the same official hub 18 hours later held 279 rows instead of 254, 26 clubs with entries instead of 24, and 15 re-filed practice codes. No row was withdrawn, no player URL key changed, and the six game-status designations were identical. | 0 retracted rows · 25 added · 15 re-coded | [Depth deficiencies](deficiencies.html), [FL-27](flagged-for-review.html) |
| **Standings and the Week 10 slate re-verified clean.** 32 clubs × 8 published columns matched the live page exactly, including streaks; all 14 fixtures, dates and kickoff times matched the hub's own slate headers. | 9 re-verification checks, 0 mismatches | [data/reverification_a392.csv](https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/reverification_a392.csv) |
| **Origination stopped being a specification.** A ridge ratings model fitted only on the officially sourced 136-game log, walked forward week by week, beats every no-information baseline on spreads and does not beat the archived price by enough to call either way: paired error +0.295 pts (CI −0.409 to +1.011) on spreads, +0.847 (CI +0.153 to +1.580) on totals. Totals are therefore published as a diagnostic, not a line. | spread MAE 9.278 vs 10.455 baseline vs 8.983 archived price | [Fair-Line Lab](model-lab.html) |
| **Correlations became numbers.** Eight measurements with seeded bootstrap intervals, including the same-game coupling a parlay is priced on: against the archived lines, home-spread-cover and game-over have a phi of −0.241, and a ticket priced by multiplying the marginals overstates the joint hit rate by 42.4%. Home-field advantage this season is 0.50 pts with an interval spanning zero, so the conventional 2.5 is now visibly a prior rather than a measurement. | [Measured correlations](measured-correlations.html) | |

Two defects found while doing it are worth reading before any next step, because both are the kind that survive a passing test:

- **A cross-source join silently dropped a whole club.** The community archive writes `ARI` and `LA` where the league writes `AZ` and `LAR`; without an alias table the join loses all nine Arizona games and the model still reports an error rate ([FL-28](flagged-for-review.html), [S-36](suggestions.html)).
- **The register asserted something the repository contradicted.** "No price data of any kind" sat next to 20,490 rows of vendored prices, and the file named `closing_lines.csv` stops in 2018 while the only 2026 prices live in `games.csv`. The upstream schema that is supposed to define those columns was last edited 13 May 2020 and never says whether the price is an open or a close ([FL-29](flagged-for-review.html), [FL-30](flagged-for-review.html), [Price archive](price-archive.html)).

**The requirement that is still not met, stated plainly:** 2nd/3rd/4th-string deficiency tracking works — for two clubs. The join pattern is proven end to end on Seattle and Los Angeles (a first-string quarterback out with a limited second-stringer and an unreserved third-stringer behind him; a second-string nose tackle out and a third in; a long snapper with no backup listed on the club's own chart), and it produces the deficiency signal the standings cannot see. Scaling it is a transcription cadence decision ([Q-37](questions.html), [S-39](suggestions.html)), not a research problem.

**What to decide now, in order:** (1) start the daily stored injury snapshot so availability signals have a history — it is worth more every day it runs and it unblocks the largest part of the brief ([S-35](suggestions.html), [Q-36](questions.html)); (2) adopt the alias table plus a join-row-count check ([S-36](suggestions.html)); (3) admit the paired-error rule to the gates so a strategy cannot promote itself on an easy slate ([S-38](suggestions.html)); (4) decide the price-vintage question, because it changes the wording of every CLV claim in the project ([Q-35](questions.html)).
