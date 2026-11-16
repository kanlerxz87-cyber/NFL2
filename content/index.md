# NFL2 — Decision Dashboard
> Collect, organise and analyse NFL data so we can originate our own lines, rank strategies on a leaderboard that must survive validation gates, and publish every number with the official source it came from.

{{kpis}}

> **Independent Q51 audit and tested research engine:** [open the evidence dashboard](q51/index.html). It publishes current-snapshot research lines, descriptive correlations, fail-closed gates and the full Flagged for Review register. Outputs are paper-only and unvalidated; no betting edge is claimed.

> **New this session — the competition is finally scored.** [Open the session `2268bfb2` tree](s2268/index.html). It re-reads the official league pages on 13 November 2026 and publishes every row that moved (the injury hub is 41 rows ahead of what this site shows), transcribes the New England and Detroit depth charts into a 1st-to-4th string cascade for the one unplayed game with filed designations, and runs the first pre-registered walk-forward competition: ten candidates scored on 596 decisions across 72 holdout games, with exact tests, a false-discovery correction, a seeded Monte Carlo, a measured same-game correlation matrix, disjoint-parlay arithmetic, ten validation gates and five reward tiers. The headline is uncomfortable and published anyway: **our own originated spread and total both fail to beat knowing nothing on this holdout.** Three Week 10 game ids were also shown to name different fixtures in two published files; that defect was fixed on 15 November 2026 by renumbering the injury register to the schedule convention (S-65), and a fixture-consistency check now fails the build on any recurrence — see [FL-64](flagged-for-review.html).

## Decision readiness — one row per requirement

Every requirement on the register appears once below, with its status, the gate that blocks it, and the clearing condition. It is the same register as the [full requirements page](requirements.html), rendered from `data/requirements.csv`; one source, so the two pages cannot disagree. A `—` means no applicable technical gate or numeric threshold is defined in the project register. The landing-table verifier checks current-row coverage, gate references and source classification.

> **Source class:** Requirement wording, statuses, gate mappings and thresholds are project-design statements taken from the owner brief and in-repository design records. They are **not official NFL facts**, and are not verified by an NFL source. The `Source` column intentionally links to `S-BRIEF` (the owner instruction); official NFL facts are published separately with their own source links. A project gate being documented does not mean it has passed.

{{csv data/requirements.csv;;cols=id:ID,requirement:Requirement,raised_in:Origin,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it;;source=S-BRIEF;;caption=The Source link leads to the durable register; Origin records each row's stated project brief, session or audit provenance. S-BRIEF is an owner-instruction reference, not an NFL source. Requirement text, gate rules and statuses are project design, not official NFL facts or source verification.}}

### Depth coverage counts are different measures

The **10-chart personnel-relief join** uses the dated 2026-11-13 Week 10 injury snapshot: 85 of its 296 filed rows resolve to one of the 10 club chart pages in that join ([Personnel Relief](personnel-relief.html), [dated injury table](availability-1113.html), [official NFL injury hub](https://www.nfl.com/injuries/)). This 85/296 figure is a repository join result, not an NFL-published statistic. Separately, the S745 register transcribes **31 of 32 club-published, explicitly unofficial depth charts** as read on 2026-11-13 ([Depth Register with row-level chart links](depth-deficiencies.html)); Houston's [official club page](https://www.houstontexans.com/team/depth-chart) presents its chart as an image, which remains untranscribed ([FL-60](flagged-for-review.html)). The 31/32 figure counts chart pages transcribed; it does **not** establish 31/32 point-in-time starter-replacement joins. The 10-club and 31/32-club counts describe different files, dates and operations; see also [FL-44](flagged-for-review.html).

## What changed this session: a full official re-read, and what is still uncovered

Two things are new this session and both are on one page: [Brief Coverage & Freshness](brief-coverage.html).

The **injury hub was read in full in this session**, and the Week 10 table this site renders rests on a read from 12 November. It shows {{metric d_pub_rows}} rows over {{metric d_pub_clubs}} clubs with {{metric d_pub_desig}} game-status designations; the league published {{metric d_rows_15}} rows over {{metric d_clubs_15}} clubs with {{metric d_desig_15}} designations at the 2026-11-15T12:56Z read. The read was reconciled club by club against this repository's own 13 November capture before a single row was stored: **{{metric d_unchanged}} clubs match exactly, {{metric d_gained}} gain rows, and not one club loses a row or a player.** That reconciliation is the proof the transcription is complete rather than partial, and it is published row by row ([FL-84](flagged-for-review.html)).

The **brief itself is now traced clause by clause**: {{metric cov_rows}} clauses across {{metric cov_categories}} categories, of which {{metric cov_covered}} are covered, {{metric cov_partial}} partial, {{metric cov_blocked}} blocked and **{{metric cov_uncovered}} are owned by nothing at all** ([FL-85](flagged-for-review.html)). The uncovered set is the part worth reading, because it is the only part that work already in flight cannot close: no ablation framework exists to test the injury and personnel features the way the brief asks, and all fourteen validation gates are one-sided, so a strategy that is promoted can never be demoted on evidence ([FL-86](flagged-for-review.html)).

A third panel answers a question a static site normally cannot: **how old is the evidence behind each published table.** {{metric fresh_behind}} of {{metric fresh_pages}} pages rest on an official read older than the newest read of that same page held in the repository.

## Read this first

This site has two kinds of pages and they never mix on one page without a divider:

- **Measured** (green badge) — tables generated from `data/*.csv`, every row carrying a link to the official league page it was transcribed from.
- **Specified** (blue badge) — the design of the pricing engine, signals, gates and competition rules. These are proposals, not results.
- **Decisions** (amber badge) — the [question register](questions.html), the [suggestion register](suggestions.html) and the [review queue](flagged-for-review.html). Each suggestion is labeled as adopted, recommended, owner-only, or blocked; a recommendation is not an owner decision.

The root register remains design-only. Independent Q51 research outputs are labelled unvalidated and paper-only; no betting edge is claimed. Blank cells are rendered as `not published` rather than filled with an estimate — see [verification method](methodology.html).

## What this session found when it re-opened the repository

This dashboard is the product of several concurrent workstreams that have each been merged to `main`.
The table below is the state of the repository as this session received it on **12 November 2026**, so a
reader can tell what was inherited from what was added.

| Item | State received | Where checked |
| --- | --- | --- |
| Tracked files | 384, across seven merged session trees | `git ls-files`, counted |
| Commits | `25d88a9`, the merge of pull request #24 | `git log --oneline` |
| Published trees | `/` (canonical, audited), plus `q51/`, `portal/`, `analytics/`, `s53/`, `review/`, `site/`, `docs/`, `archive/session-009ec582/` | [source registry](sources.html) |
| Requirements document | present — {{metric requirements}} traced requirements | [requirements](requirements.html) |
| Verifiers | eight suites on disk, all green before this session changed anything | `tools/verify.py`, `tools/check_site.py`, `tools/review_verify.py`, `tests/q51`, `scripts/audit_all_pages.py`, `scripts/verify_s53126614.py`, `engine/verify_repo_and_site.py`, `scripts/verify_q51.py` |
| GitHub Pages | configured: legacy build, branch `main`, path `/` | GitHub Pages API |

The original repository held only a README; the current site was built across multiple documented sessions. Their scoped work, sources, verification and integration history are recorded in the [coordination log](https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md). The requirement list reconstructed from the brief is now [a tracked file](requirements.html) so it stops living only in chat. The table above describes the repository as the *first* session found it; the map below says which of the ten published trees holds what, and it is generated from the filesystem so it cannot drift.

The eight verifiers all pass, but they are **self-referential**: they prove the published HTML matches
`data/*.csv`. They do not prove `data/*.csv` still matches the league. This session therefore re-fetched
`nfl.com` and compared row by row. That found published prose which contradicted the repository's own
data — the counts, the club coverage and one flag — and those are corrected here and listed on the
[Flagged for Review](flagged-for-review.html) page rather than quietly edited.

## State of the workstreams

| Workstream | State | Evidence in repo | Blocking |
| --- | --- | --- | --- |
| Injury and availability collection | separate reads: 254-row primary file (12 Nov 04:45Z), 279-row full re-read (12 Nov 22:35Z), 296-row full-hub file (13 Nov 12:46Z, session `83246f00`) and **this branch's 12:45Z read with all 28 blocks and the depth join** | `data/injuries_2026_wk10.csv`, `data/injuries_wk10_2026_hubrefresh.csv`, `data/injuries_wk10_83246f00.csv`, `data/injury_delta_a392.csv` | canonical display remains owner-only (Q-42); repeated-read cadence and history remain open (Q-43, S-35) |
| Depth, IR and roster events | running — 227 rows | `data/depth_changes_2026_wk10.csv` | no official depth chart exists (FL-06) |
| Standings and schedule | 32 club rows × 8 published fields; official re-read captured at `2026-11-13T12:53Z`, exact match | `data/standings_2026.csv`, `data/standings_recheck_20261113.csv`, `data/schedule_2026_wk10.csv` | remaining split-record columns are omitted rather than inferred (FL-07) |
| Depth deficiency by side of the ball | 26 clubs with two-sided counts off the official filing; the 13 November read joins an unavailable name to the column it holds on the club's own chart — **18 joined rows on the 13 November read, 8 of them 1st string** — for the 4 clubs this build transcribes | [Depth Deficiencies](deficiencies.html), [Week 10 availability](availability-1113.html), `data/availability_deficiency_66faefac.csv` | 28 club charts not transcribed (Q-37, S-39, S-61) |
| Line origination | **computed** — walk-forward ridge ratings on 136 official games: spread MAE 9.278 vs a 10.455 do-nothing baseline, paired +0.295 pts against the archived price | [Fair-Line Lab](model-lab.html), `data/model_backtest_2026_a392.csv` | totals are worse than a league mean and are published as a diagnostic, not a line (S-37, FL-32) |
| Signal catalogue | specified — 18 families, 5 blocked on data | `data/signals.csv` | entitlement + join keys (G-01, G-02) |
| Strategy registry | {{metric strategies}} entries; **1 locked before its slate (ST-15)**, none ranked | `data/strategies.csv`, `data/prereg_wk10_66faefac.csv` | tracking ledger + settled volume (G-08) |
| Validation gates | 15 gates defined; 0 strategies can pass any | `data/gates.csv` | see gate matrix |
| Correlation | method defined; 12 pair classes; **no rho asserted**; 2 measured as Pearson *r* on game scores | `data/correlation.csv`, `data/computed_correlation.csv` | joint bet-settlement data (Q-12) for any rho |
| Skill-vs-luck protocol | derived and computed in-repo | `content/skill-vs-luck.md` | sample must still be collected |
| Competition and rewards | tiers and rules written; payout mechanism unfunded | `content/leaderboard.md` | owner decision (Q-26) |

## The blocking chain

Four items sit in front of almost everything else. They are decisions and access, not coding:

1. **Prices.** Without an opening and closing price per market there is no vig to strip, no fair value to deviate from, no CLV to measure skill with, and no way to know whether a line we originate is right. This is [Q-01](questions.html) and it blocks 9 of 15 gates.
2. **Player-level entitlement.** Snaps, routes and targets are what turn "a starter is out" into "the replacement costs 2.1 yards per carry". This is [Q-02](questions.html).
3. **A defensible depth answer.** The league publishes no depth chart, so "2nd/3rd/4th string replacing a starter" must be reconstructed from roster status, participation, designations and actual playing time ([S-06](suggestions.html), [FL-06](flagged-for-review.html)).
4. **Point-in-time storage.** Three filings a week and a dated event log, or the availability signals cannot be built at all ([FL-09](flagged-for-review.html)).

## What changed on 13 November 2026

The league made one Week 10 game official after the last build. Two things follow from it, and both are on the site rather than in a commit message:

1. **The standings were one game stale.** `NYG` and `WAS` each moved by exactly the settled 24–21 game. Both rows are refreshed, the league identities still close (136–136, 6291 points for and against), and the episode is recorded as [FL-35](flagged-for-review.html) because the real defect is that no cumulative table on this site states when it was read.
2. **The site has a settled result for the first time.** Every line this repository originated for that game is now scored against the official final score on the [Settled Week 10](week10-settled.html) page. Our spread lost to a predictor that knows nothing about either team by 2.5 points; our total beat the archived price by 4.0 points, on a game whose total landed 0.93 points from the league mean — only 8 of the 136 verified games are that average. The page publishes the arithmetic rather than the flattering reading: detecting a 1.0-point difference at 80% power needs about 1,400 games, so one settled game is 0.07% of the evidence required.

Nothing was appended to the weeks 1–9 backtest corpus. Suggestion [S-26](suggestions.html) asks for that file to be the pre-registered corpus with its hash published, so week 10 results go into a separate append-only file and the corpus stays byte-identical at `sha256 f0dffce0…6f33`.

Two items in the register came out of the re-read and are waiting on you rather than on code: the refresh cadence for cumulative tables ([Q-40](questions.html), [S-43](suggestions.html)) and a broadcaster disagreement on two Week 11 games ([FL-36](flagged-for-review.html)).

## What changed on 13 November 2026, later

A settlement is not a forecast. The one graded Week 10 game was published after the fact, so it proves the arithmetic runs and nothing else. The thing a competition needs is a line published **before** the games it describes, and there was none — so this session built one.

1. **Thirteen Week 11 lines, pre-registered.** For the games of 19–23 November: our spread and our total for each fixture, with the model inputs beside them, published with a decision timestamp of `2026-11-13T12:39Z` and a SHA-256 over four artefacts — the lines file, the frozen weeks 1–9 corpus, the append-only settled-games file and the generator script. The full record is on the [Week 11 lines](week11-originated.html) page, and `tools/grade_forward.py` recomputes those hashes before it grades anything.
2. **The model was proved to be the same model, not a look-alike.** The Week 11 generator re-implements the published ratings model, so before it writes anything it re-derives all fourteen already-published Week 10 lines from the frozen corpus and compares every cell. It matched 14 of 14, and `tools/verify.py` now re-runs that guard on every verification.
3. **The pre-registration was tested, not asserted.** Editing one spread from 5.5 to 1.5 makes the grader report `BROKEN`, withhold the grade and exit non-zero. Restoring it returns `intact`.
4. **Two flags and two questions came out of a 102-row re-verification.** All 32 standings rows, all 14 Week 10 fixtures and all 13 Week 11 fixtures were re-read against the live official pages on 13 November: 95 matches, 2 mismatches, 5 rows that say NOT CHECKED. The two mismatches are the Week 11 broadcasters — and they are now **explained**, not just flagged: the league's own announcement of 9 November matches this repository's transcription cell for cell, so the league moved the two broadcasts between 9 and 13 November ([FL-36](flagged-for-review.html)). Two new questions ask which official page is the record when the league changes a schedule after announcing it ([Q-64](questions.html)) and when participation for the next week will exist ([Q-65](questions.html)).
5. **Two suggestions were implemented.** S-44 (auto-grade every originated line against the settled result) and S-45 (publish the required-sample number beside every performance figure) are now code, and the standings table carries the capture timestamp S-43 asked for.

The honest finding on the lines themselves: **our spreads sit about 3.5 points closer to a pick'em than the community archive's** — the model's fitted home-field coefficient is 0.18 points, where the archive's widest lines are 14 and 16.5. The totals remain the weak half. And the sample-size arithmetic is unchanged and unforgiving: thirteen observations against a required ~1,400.

### Later the same day — the injury hub moved, so the site now dates it

A second read of the official injury hub at **2026-11-13T12:45Z** found the source had changed materially
in 14 hours, and the new [Availability Watch](availability-watch.html) page publishes all of it:

- **Coverage is now 28 of 28 clubs on the Week 10 slate.** The league published full SEA and CIN blocks, which closes the
  collection gap [FL-24](flagged-for-review.html) recorded. This Dashboard tile still reads
  `{{metric injury_coverage}}` from the 12 November capture, and that disagreement is [FL-37](flagged-for-review.html) —
  published, not silently reconciled.
- **Player rows went 254 → 279 → {{metric aw_rows}}, and the hub has only ever added.** 17 players were
  added and none removed; **{{metric aw_practice_changes}} of 277 shared players changed practice code**
  (37 toward full participation, 12 away from it). The availability signal is that delta, not the level
  ([S-47](suggestions.html), [FL-38](flagged-for-review.html)).
- **Game-status designations went 6 → {{metric aw_designations}}.** The three new ones are all Detroit,
  all OUT: Kerby Joseph, Cade Mays, D.J. Reed.
- **No second Week 10 game has settled**, so the [settled page](week10-settled.html) cannot gain a row
  until 15–16 November. That is a property of the calendar, not a gap in the pipeline.

Four new decisions came out of it — which register is canonical ([Q-42](questions.html)), how often the
hub must be read ([Q-43](questions.html)), what replaces depth rank ([Q-44](questions.html)), and whether
to buy snap counts ([Q-45](questions.html)).

## What changed on 16 November 2026

### What changed on 16 November 2026, later — fixture context, the kickoff regime, and a weekly diff

1. **Fixture context is now a first-class dataset** ([fixture context](fixture-context.html)): 26 rows,
   BL-14 closed. Four clubs are off a bye with a +7 day rest edge; two clubs are on a six-day week because
   of the Monday night game; and the largest edges on the slate (+3) are not byes but the two clubs whose
   Week 10 game fell on a Thursday.
2. **The 2026 kickoff and onside-kick regime is published as a prior** ([kickoff regime](kickoff-regime.html)),
   BL-69 closed. Rule 6-1-6 lets any club declare an onside kick at any time, regardless of score — the
   official rulebook and NFL.com agree, and several third-party summaries say otherwise. No success-rate
   prior is published, because the widely quoted recovery percentages are not on any official page.
   One new source conflict ([FL-121](flagged-for-review.html)): the official rulebook's own 2026 Rule
   Changes table lists four rules and omits the fifth rule the league's approved summary passed.
3. **A weekly diff is published instead of only snapshots** ([weekly diff](weekly-diff.html)): the change
   between the 13 and 16 November standings reads for all 32 clubs. Eight clubs changed division rank, and
   two of the four that moved down — Chicago and Denver — did not play in the window.
4. **Two lapsed pull requests from 15 November, #71 and #84**, are recorded on the coordination board;
   their head branches no longer exist on the remote and neither has been merged or closed by this session.

### What changed on 16 November 2026, later — fixture context, the kickoff regime, and a weekly diff

1. **Fixture context is now a first-class dataset** ([fixture context](fixture-context.html)): 26 rows,
   BL-14 closed. Four clubs are off a bye with a +7 day rest edge; two clubs are on a six-day week because
   of the Monday night game; and the largest edges on the slate (+3) are not byes but the two clubs whose
   Week 10 game fell on a Thursday.
2. **The 2026 kickoff and onside-kick regime is published as a prior** ([kickoff regime](kickoff-regime.html)),
   BL-69 closed. Rule 6-1-6 lets any club declare an onside kick at any time, regardless of score — the
   official rulebook and NFL.com agree, and several third-party summaries say otherwise. No success-rate
   prior is published, because the widely quoted recovery percentages are not on any official page.
   One new source conflict ([FL-121](flagged-for-review.html)): the official rulebook's own 2026 Rule
   Changes table lists four rules and omits the fifth rule the league's approved summary passed.
3. **A weekly diff is published instead of only snapshots** ([weekly diff](weekly-diff.html)): the change
   between the 13 and 16 November standings reads for all 32 clubs. Eight clubs changed division rank, and
   two of the four that moved down — Chicago and Denver — did not play in the window.
4. **Two lapsed pull requests from 15 November, #71 and #84**, are recorded on the coordination board;
   their head branches no longer exist on the remote and neither has been merged or closed by this session.

## Latest official reads (retained captures)

The time labels identify different source snapshots rather than one global “last updated” date; each read is kept under its own capture date and none is overwritten.

| Read | Capture time (UTC) | What it represents |
| --- | --- | --- |
| Primary Week 10 injury file | 2026-11-12 04:45 | Original player-filing snapshot; not the later hub states |
| Full injury-hub re-read | 2026-11-12 22:35 | 279 rows across 26 clubs with filed rows |
| Settled-game injury recheck | 2026-11-13 06:52 | Only the 20 WAS–NYG rows; **not** a full hub re-read |
| Latest full injury-hub snapshot | 2026-11-13 12:46 | 296 filings across 26 clubs with rows; the two explicit “No Injuries Reported” blocks remain distinct |
| Latest injury-hub read (15 Nov, row-level, hand-transcribed, FL-82) | 2026-11-15 12:51 | 347 filings covering all of the 28 clubs on the slate; Chargers and Ravens now have rows (FL-81); 51 new players and no removals against the 13 Nov file. See [Injury Hub delta](hub-delta.html) |
| Full hub re-read (retained machine capture) | 2026-11-16 14:39 / 14:44 | 347 filings across every club on the 28-club slate; cell-for-cell identical to the 15 Nov read; raw bytes retained under `data/captures/injuries_hub/` with per-response SHA-256 (FL-90 partly resolved; FL-97 — one capture is not a series) |
| Independent standings re-read | 2026-11-16 14:50 | 32 clubs × 8 fields; identical cell-for-cell to the 14:57Z snapshot published the same day (cross-validated on [Re-Verification](reverification.html)) |
| NFL division standings | **2026-11-13 12:53** | 32 clubs × W/L/T/PCT/PF/PA/NET PTS/STREAK: **256/256 values matched** the independent saved re-read; no standings value changed |

The standings timestamp appears in the site-wide source-read banner and on each standings row. `tools/verify.py` checks it against the latest registered NFL standings source and compares every value against [`data/standings_recheck_20261113.csv`](data/standings_recheck_20261113.csv) on each run. The injury times above are intentionally separate; they describe different data snapshots and coverage, not a shared live refresh.

A second discovery is useful for availability research but does **not** close the ordinal-depth or snap-count gap: official gamebooks for [NE at SEA, Week 1](https://www.nfl.com/games/patriots-at-seahawks-2026-reg-1) and [NYG at WAS, Week 5](https://www.nfl.com/games/giants-at-commanders-2026-reg-5) contain starting lineups, substitutions, Did Not Play, Not Active, and player-stat sections. They record game-day evidence, not second/third/fourth-string rank or snap counts. Each PDF carries an NFL notice requiring written permission for other use. No gamebook data has been copied into the repository; the rights question is [Q-50](questions.html), with the source-backed but blocked proposal [S-58](suggestions.html).

**Current review order:** S-43 is partly adopted (visible, machine-checked timestamps); the refresh cadence remains the owner’s open choice in Q-40. S-44 and S-45 are already adopted upstream (auto-grading and sample-size context). The dated injury-register choice remains owner-only ([Q-42](questions.html), [S-46](suggestions.html)); gamebook collection remains blocked on written-use rights ([Q-50](questions.html)). Existing blanks and flags remain in place.

## Depth cascades re-verified on 13 November 2026

The eighteen depth cascades on this site were checked player by player against the twelve clubs' own depth charts and the league's Week 10 injury report. Five are verified, nine are only partly confirmed and four are contradicted by the official pages. Nine statuses on the earlier labels are wrong, and two more are understated. The full line-by-line table, with each club chart and report link, is on [Depth Cascades (re-verified)](depth-cascades.html). Every irregularity is on [Flagged for Review](flagged-for-review.html) as FL-46 to FL-54.

## Repository map

{{site_map}}

## Page map

| Category | Page | What you get |
| --- | --- | --- |
| Overview | [Executive summary](executive-summary.html) | the whole project in one read |
| Overview | [Requirements · decision readiness](requirements.html) | {{metric requirements}} requirements, each with the gate that blocks it and the number that clears it |
| Overview | [Build plan](roadmap.html) | ordered work after your decisions |
| Decisions | [Open questions](questions.html) | {{metric questions}} questions with what we have / what we lack / how to close |
| Decisions | [Suggestion register](suggestions.html) | {{metric suggestions}} suggestions with impact, effort, risk, reversibility — pick a path |
| Decisions | [Flagged for review](flagged-for-review.html) | {{metric flags}} irregularities and unverifiable items, with source links |
| Decisions | [Brief backlog](backlog.html) | the brief's line-item directives the requirement register never tracked, each with the gate that blocks it, the number that clears it and the official page it needs |
| Origination | [Originate our own lines](line-origination.html) | model architecture, inputs, no-vig math, publication of residuals |
| Origination | [Signals](signals.html) | 18 signal families with decay, capacity and blocking gate |
| Origination | [Correlation](correlation.html) | 12 pair classes, sign arguments, estimation method, blank rhos, and 2 measured from the game log |
| Origination | [Bet types](bet-types.html) | singles, parlays and prop combos priced consistently |
| Origination | [Removing luck](skill-vs-luck.html) | sample sizes, CLV, bootstrap, split-half, luck-adjusted P&L |
| Origination | [Settled Week 10 (graded)](week10-settled.html) | the first result any line here has been scored against: our spread, our total, the archived price and a do-nothing baseline, measured against WAS 24 – NYG 21 |
| Availability | [Week 10 availability](availability-1113.html) | the 13 November hub read: 296 rows over the whole Week 10 slate, and every unavailable name from a transcribed chart joined to the column it leaves empty |
| Availability | [Pre-registration lock](preregistration.html) | the first prediction pinned before kickoff: one rule, one threshold, fourteen fixtures, a hash, and the grading tool that fails if the file is touched |
| Competition | [Strategy registry](strategies.html) | {{metric strategies}} entries including two negative controls, one of them the locked rule above |
| Competition | [Leaderboard & rewards](leaderboard.html) | ranking rules, tiers, reward mechanics, gate-readiness matrix |
| Competition | [Validation gates](validation-gates.html) | 15 gates, pass criteria, what each one blocks |
| Data | [Week 10 injury report](injuries.html) | all 347 official rows of the pinned 16 Nov capture (the canonical table), per-row source links; the 12 Nov 254-row read is kept as an archived file; the hub has since grown to {{metric pr_hub_rows}} rows and the later reads are kept in their own dated files |
| Data | [Availability Watch (dated)](availability-watch.html) | {{metric aw_rows}} player rows across 28 of 28 clubs, read at 12:45Z on 13 November, the movement since the previous read, and the 4 readiness gates — 1 pass, 3 fails, each with the number that decides it |
| Data | [Depth & deficiencies](depth-impact.html) | who is replacing whom, and what we cannot yet quantify |
| Data | [Week 11 venues (game centre)](fixture-venues.html) | the stadium printed on each of the 13 Week 11 game centres, read 16 Nov, with the 3 disagreements with the schedule parameter flagged ([FL-118](flagged-for-review.html)) |
| Data | [Team decision view (32 clubs)](teams.html) | one row per club: injury-hub counts from the 16 Nov read, the November reserve list, league-named starter changes, and the Week 10 byes left blank |
| Data | [Personnel Relief](personnel-relief.html) | **new 13 Nov** — the verified join: {{metric pr_resolved}} of {{metric pr_rows}} listed players resolved to a 1st/2nd/3rd/4th string on their own club's published chart, with the next man the club names, and {{metric pr_first_dnp}} 1st-string non-participants across {{metric pr_charts}} clubs |
| Data | [Standings, schedule & game log](league-data.html) | 32 reconciled rows, the Week 10 slate, and a {{metric games_log}}-game verified results log for weeks 1–9 |
| Origination | [Fixture context (computed)](fixture-context.html) | **new 16 Nov** — 26 club-fixture sides of the Week 11 slate: rest, bye, short week, mirrored rest edge, divisional flag, the venue's body-clock kickoff and the kickoff window, every column derived from a published schedule fact and re-derived on every build |
| Origination | [Kickoff regime 2026](kickoff-regime.html) | **new 16 Nov** — the five 2026 rule changes that move a game total, including 6-1-6: any club may now declare an onside kick at any time, regardless of score. Sourced to the official rulebook and NFL.com because third-party summaries contradict each other |
| Data | [Weekly what-changed diff](weekly-diff.html) | **new 16 Nov** — the change between two dated official standings reads rather than a snapshot: W/L/T, points, net and within-division rank movement for all 32 clubs, with the two Week 10 games that fall outside the window named rather than folded in |
| Origination | [Fixture context (computed)](fixture-context.html) | **new 16 Nov** — 26 club-fixture sides of the Week 11 slate: rest, bye, short week, mirrored rest edge, divisional flag, the venue's body-clock kickoff and the kickoff window, every column derived from a published schedule fact and re-derived on every build |
| Origination | [Kickoff regime 2026](kickoff-regime.html) | **new 16 Nov** — the five 2026 rule changes that move a game total, including 6-1-6: any club may now declare an onside kick at any time, regardless of score. Sourced to the official rulebook and NFL.com because third-party summaries contradict each other |
| Data | [Weekly what-changed diff](weekly-diff.html) | **new 16 Nov** — the change between two dated official standings reads rather than a snapshot: W/L/T, points, net and within-division rank movement for all 32 clubs, with the two Week 10 games that fall outside the window named rather than folded in |
| Data | [Data dictionary](data-dictionary.html) | every column, its meaning, its source, its transform |
| Governance | [Verification method](methodology.html) | the rules this project will not bend |
| Governance | [Re-Verification (16 Nov)](reverification.html) | the dated line-by-line re-read of the official pages behind every Week 10 number: the frozen hub delta, the thirteen final results with their game pages, the standings delta club by club, and the Week 11 slate |
| Governance | *Repository map* (below) | ten published trees, their owner sessions, their page counts and what each uniquely holds, generated at build time; only the game log was adopted into this register, after re-audit |
| Governance | [Crosscheck: live re-verification](crosscheck/index.html) | A second, independent re-check against the official league pages on 12 November 2026: what still matches, what moved since the snapshot, a claim-by-claim audit of every tree in this repository, and the questions / information / suggestions register to review before anything is implemented. Every row carries its official source; anything unverifiable is published as flagged |
| Governance | [Price archive](price-archive.html) | what market data the repository actually holds, what each column proves, and what it cannot be used for (FL-29, FL-30) |
| Governance | [Source registry](sources.html) | {{metric sources}} sources with tier, access time and what each was used for |
