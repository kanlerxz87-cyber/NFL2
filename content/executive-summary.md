# Executive Summary
> What exists, what is verified, what is missing, and the four decisions that unlock the rest — for Week 10 of the 2026 season, fetched 12 November 2026.

## The one-paragraph version

The collection layer now exists and is genuinely verified: 254 rows of the official Week 10 practice report across 28 clubs, 227 official roster and depth events, 32 reconciled standings rows and a 14-game schedule, every row carrying a link to the official page it came from and nothing inferred to fill a gap. The analysis layer is specified in full — line-origination architecture, 18 signal families, 14 validation gates, a correlation framework with twelve pair classes, a sample-size protocol for removing luck, and a 14-entry strategy registry — but it produces no numbers yet, because two inputs do not exist in this project: licensed market prices and player-level participation data. The honest summary is that the pipeline and the rules are real, the data spine is real, and every performance claim you might want from this system is currently un-earnable rather than absent.

## What is verified and how we know

| Dataset | Volume | Official source | Reconciliation performed |
| --- | --- | --- | --- |
| Week 10 practice snapshot | 254 rows / 28 clubs | [nfl.com/injuries](https://www.nfl.com/injuries/) | transcribed row by row from the rendered table; participation strings mapped to three codes; no cell backfilled |
| Game-status designations | {{metric designations}} rows populated | [nfl.com/injuries](https://www.nfl.com/injuries/), [week-10 report](https://www.nfl.com/news/nfl-week-10-injury-report-2026-season) | the two official pages agree on every one; the remaining rows are blank in the source, which is not the same as zero |
| Roster / depth / IR events | 227 rows | [Wed 11-Nov roundup](https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11) | per-team blocks transcribed; typos in the source preserved and annotated |
| Completed results, weeks 1–9 | {{metric games_log}} games | [nfl.com/schedules](https://www.nfl.com/schedules/2026/REG/) plus one [official game page](https://www.nfl.com/games/) per row | imported from a parallel session and re-audited here: every row cites its own game page, and the recount matches the standings row for **{{metric games_log_reconciled}} of 32 clubs** on W, L, T, PF and PA — the strongest independent check available in this repo |
| Standings | 32 rows | [nfl.com/standings](https://www.nfl.com/standings/) | winning pct recomputed with ties counted as half; ΣPF (6246) = ΣPA (6246) and Σnet = 0 across the league, so the transcription is arithmetically closed |
| Week 10 schedule | 14 games | [week-10 report](https://www.nfl.com/news/nfl-week-10-injury-report-2026-season) | venues, kickoff times and network match the injury hub's own headers |
| Quarterback chain changes | 5 quarterback depth items: 3 confirmed starting changes, 1 coach declining to commit, 1 backup assignment | [roundup](https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11), [Darnold article](https://www.nfl.com/news/sam-darnold-ruled-out-for-seahawks-week-10-game-vs-raiders-drew-lock-expected-to-start-again) | each is a direct coach or league statement, not a report about a report |

## Five findings that matter for decisions

1. **The injury hub is a practice document, not an availability answer.** On the day we fetched, only five of 254 rows carried a game status, and the Injury column was populated for six. Anyone modelling availability off this table without the prose feed is modelling an empty column. ([FL-02](flagged-for-review.html), [FL-08](flagged-for-review.html))
2. **"No Injuries Reported" is a data state, not a health statement.** Four clubs show that label; one of them (Seattle) is contradicted on the same site the same week, with twelve players injured and a confirmed quarterback rule-out. Reading the label as zero is the single most likely silent error in this whole system. ([FL-01](flagged-for-review.html))
3. **There is no official depth chart to buy or scrape.** The obvious URL is a 400-style error page, so the requirement about second, third and fourth-stringers has to be met by reconstruction — roster status, participation, designations, then actual playing time. That is a build item, not a lookup. ([FL-06](flagged-for-review.html))
4. **Roster churn in 2026 is large enough to break joins.** Players appear on clubs a naive pipeline would flag as errors; four of the surprising cases are independently confirmed by the same official page. We transcribed everything as published and made the 32-team roster sweep a gate (G-02) rather than quietly "fixing" the league's own data. ([FL-03](flagged-for-review.html))
5. **The parlay and prop-combo problem is a correlation problem before it is a pricing problem.** Same-game legs share a cause; independent-leg multiplication overstates parlay value; and the one piece of public research quantifying a cross-game parlay markup has an openly disputed matching method. We therefore publish the framework and the signs we can defend, and leave every rho value blank. ([correlation](correlation.html))

## What the system can and cannot do today

| Capability | Today | Earliest realistic state |
| --- | --- | --- |
| Answer "who is hurt and who is starting instead" for the current week | yes, from verified rows, with depth rank left blank | improves immediately with the roster sweep |
| Detect availability surprise (trend → designation) | no — needs three dated filings per week | after point-in-time storage lands (G-03) |
| Originate a number and publish the residual | no — no prices | needs a price feed; 1 gate (G-01) and 1 vendor decision (Q-01) |
| Score a strategy on the leaderboard | no — zero tracked bets, by design | first week of forward tracking after pre-registration |
| Quantify replacement cost in points | no — needs snaps | after Q-02 closes |
| Prove an edge is not luck | protocol ready, no sample | 400 bets for the gate, 1,000 for promotion (S-08) |

## The four decisions to make now

1. Choose the price tier we originate against and start ingesting three seasons (unblocks 9 of 14 gates).
2. Approve the pre-registration rule that backtest numbers never appear on the leaderboard (S-04) — this is the decision that keeps the competition honest.
3. Decide whether v1 scope is spreads/totals/ML plus game props only (S-05), or the wider market set with a longer gate build.
4. Decide what the leaderboard actually pays (S-25); until then it is a readiness board, which is what we published.

## Standing risk to name plainly

Everything on the blue pages is a specification written before the data existed. Specifications are cheap in this domain and the record of betting models is poor; the gates and the negative controls (ST-12 do-nothing, ST-13 public-news echo) exist precisely so that a specification has to survive contact with results. Until then the correct posture toward any number on the origination pages is scepticism, and the site is built so that the blanks are visible rather than hidden.
