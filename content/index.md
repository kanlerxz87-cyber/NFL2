# NFL2 — Decision Dashboard
> Collect, organise and analyse NFL data so we can originate our own lines, rank strategies on a leaderboard that must survive validation gates, and publish every number with the official source it came from.

{{kpis}}

> **Independent Q51 audit and tested research engine:** [open the evidence dashboard](q51/index.html). It publishes current-snapshot research lines, descriptive correlations, fail-closed gates and the full Flagged for Review register. Outputs are paper-only and unvalidated; no betting edge is claimed.

## Read this first

This site has two kinds of pages and they never mix on one page without a divider:

- **Measured** (green badge) — tables generated from `data/*.csv`, every row carrying a link to the official league page it was transcribed from.
- **Specified** (blue badge) — the design of the pricing engine, signals, gates and competition rules. These are proposals, not results.
- **Decisions** (amber badge) — the [question register](questions.html), the [suggestion register](suggestions.html) and the [review queue](flagged-for-review.html). Nothing on these pages has been implemented on your instruction.

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
| Injury and availability collection | running — 254 rows snapshotted at 04:45Z, **re-read at 22:35Z: 279 rows across 26 clubs** | `data/injuries_2026_wk10.csv`, `data/injuries_wk10_2026_hubrefresh.csv`, `data/injury_delta_a392.csv` | no stored history, so no availability signal can be backtested (FL-27, Q-36) |
| Depth, IR and roster events | running — 227 rows | `data/depth_changes_2026_wk10.csv` | no official depth chart exists (FL-06) |
| Standings and schedule | running — 32 + 14 rows, reconciled | `data/standings_2026.csv`, `data/schedule_2026_wk10.csv` | seven official columns left out (FL-07) |
| Depth deficiency by side of the ball | 26 clubs with two-sided counts off the official filing; verified 1st-to-4th string chains for the 2 clubs whose charts were transcribed | [Depth Deficiencies](deficiencies.html), `data/deficiency_by_club_a392.csv` | 30 club charts not transcribed (Q-37, S-39) |
| Line origination | **computed** — walk-forward ridge ratings on 136 official games: spread MAE 9.278 vs a 10.455 do-nothing baseline, paired +0.295 pts against the archived price | [Fair-Line Lab](model-lab.html), `data/model_backtest_2026_a392.csv` | totals are worse than a league mean and are published as a diagnostic, not a line (S-37, FL-32) |
| Signal catalogue | specified — 18 families, 5 blocked on data | `data/signals.csv` | entitlement + join keys (G-01, G-02) |
| Strategy registry | 14 entries, none tracked | `data/strategies.csv` | pre-registration + tracking ledger |
| Validation gates | 14 gates defined; 0 strategies can pass any | `data/gates.csv` | see gate matrix |
| Correlation | method defined; 12 pair classes; **no rho asserted**; 2 measured as Pearson *r* on game scores | `data/correlation.csv`, `data/computed_correlation.csv` | joint bet-settlement data (Q-12) for any rho |
| Skill-vs-luck protocol | derived and computed in-repo | `content/skill-vs-luck.md` | sample must still be collected |
| Competition and rewards | tiers and rules written; payout mechanism unfunded | `content/leaderboard.md` | owner decision (Q-26) |

## The blocking chain

Four items sit in front of almost everything else. They are decisions and access, not coding:

1. **Prices.** Without an opening and closing price per market there is no vig to strip, no fair value to deviate from, no CLV to measure skill with, and no way to know whether a line we originate is right. This is [Q-01](questions.html) and it blocks 9 of 14 gates.
2. **Player-level entitlement.** Snaps, routes and targets are what turn "a starter is out" into "the replacement costs 2.1 yards per carry". This is [Q-02](questions.html).
3. **A defensible depth answer.** The league publishes no depth chart, so "2nd/3rd/4th string replacing a starter" must be reconstructed from roster status, participation, designations and actual playing time ([S-06](suggestions.html), [FL-06](flagged-for-review.html)).
4. **Point-in-time storage.** Three filings a week and a dated event log, or the availability signals cannot be built at all ([FL-09](flagged-for-review.html)).

## What changed on 13 November 2026

The league made one Week 10 game official after the last build. Two things follow from it, and both are on the site rather than in a commit message:

1. **The standings were one game stale.** `NYG` and `WAS` each moved by exactly the settled 24–21 game. Both rows are refreshed, the league identities still close (136–136, 6291 points for and against), and the episode is recorded as [FL-35](flagged-for-review.html) because the real defect is that no cumulative table on this site states when it was read.
2. **The site has a settled result for the first time.** Every line this repository originated for that game is now scored against the official final score on the [Settled Week 10](week10-settled.html) page. Our spread lost to a predictor that knows nothing about either team by 2.5 points; our total beat the archived price by 4.0 points, on a game whose total landed 0.93 points from the league mean — only 8 of the 136 verified games are that average. The page publishes the arithmetic rather than the flattering reading: detecting a 1.0-point difference at 80% power needs about 1,400 games, so one settled game is 0.07% of the evidence required.

Nothing was appended to the weeks 1–9 backtest corpus. Suggestion [S-26](suggestions.html) asks for that file to be the pre-registered corpus with its hash published, so week 10 results go into a separate append-only file and the corpus stays byte-identical at `sha256 f0dffce0…6f33`.

Two items in the register came out of the re-read and are waiting on you rather than on code: the refresh cadence for cumulative tables ([Q-40](questions.html), [S-43](suggestions.html)) and a broadcaster disagreement on two Week 11 games ([FL-36](flagged-for-review.html)).

## Repository map

{{site_map}}

## Page map

| Category | Page | What you get |
| --- | --- | --- |
| Overview | [Executive summary](executive-summary.html) | the whole project in one read |
| Overview | [Requirements](requirements.html) | {{metric requirements}} requirements, each traced to a page and a status |
| Overview | [Build plan](roadmap.html) | ordered work after your decisions |
| Decisions | [Open questions](questions.html) | {{metric questions}} questions with what we have / what we lack / how to close |
| Decisions | [Suggestion register](suggestions.html) | {{metric suggestions}} suggestions with impact, effort, risk, reversibility — pick a path |
| Decisions | [Flagged for review](flagged-for-review.html) | {{metric flags}} irregularities and unverifiable items, with source links |
| Origination | [Originate our own lines](line-origination.html) | model architecture, inputs, no-vig math, publication of residuals |
| Origination | [Signals](signals.html) | 18 signal families with decay, capacity and blocking gate |
| Origination | [Correlation](correlation.html) | 12 pair classes, sign arguments, estimation method, blank rhos, and 2 measured from the game log |
| Origination | [Bet types](bet-types.html) | singles, parlays and prop combos priced consistently |
| Origination | [Removing luck](skill-vs-luck.html) | sample sizes, CLV, bootstrap, split-half, luck-adjusted P&L |
| Origination | [Settled Week 10 (graded)](week10-settled.html) | the first result any line here has been scored against: our spread, our total, the archived price and a do-nothing baseline, measured against WAS 24 – NYG 21 |
| Competition | [Strategy registry](strategies.html) | 14 entries including two negative controls |
| Competition | [Leaderboard & rewards](leaderboard.html) | ranking rules, tiers, reward mechanics, gate-readiness matrix |
| Competition | [Validation gates](validation-gates.html) | 14 gates, pass criteria, what each one blocks |
| Data | [Week 10 injury report](injuries.html) | all 254 official rows, per-row source links |
| Data | [Depth & deficiencies](depth-impact.html) | who is replacing whom, and what we cannot yet quantify |
| Data | [Standings, schedule & game log](league-data.html) | 32 reconciled rows, the Week 10 slate, and a {{metric games_log}}-game verified results log for weeks 1–9 |
| Data | [Data dictionary](data-dictionary.html) | every column, its meaning, its source, its transform |
| Governance | [Verification method](methodology.html) | the rules this project will not bend |
| Governance | *Repository map* (below) | ten published trees, their owner sessions, their page counts and what each uniquely holds, generated at build time; only the game log was adopted into this register, after re-audit |
| Governance | [Crosscheck: live re-verification](crosscheck/index.html) | A second, independent re-check against the official league pages on 12 November 2026: what still matches, what moved since the snapshot, a claim-by-claim audit of every tree in this repository, and the questions / information / suggestions register to review before anything is implemented. Every row carries its official source; anything unverifiable is published as flagged |
| Governance | [Price archive](price-archive.html) | what market data the repository actually holds, what each column proves, and what it cannot be used for (FL-29, FL-30) |
| Governance | [Source registry](sources.html) | {{metric sources}} sources with tier, access time and what each was used for |
