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

## What the repository held at the start of this session

| Item | State found | Where checked |
| --- | --- | --- |
| Tracked files | 1 (`README.md`, 6 bytes, contents `# NFL2`) | [repository root](https://github.com/kanlerxz87-cyber/NFL2) |
| Commits | 1 — `01f2271 Initial commit` | `git log` |
| Requirements document | none | repository root |
| Code, data, tests, CI | none | repository root |
| GitHub Pages | already configured: legacy build, branch `main`, path `/` | GitHub Pages API |

The table above describes the repository when the *first* session on this project opened it. Everything since — the register, the site, the pipelines, the audits and this dashboard — was written by eleven parallel agent sessions on eleven branches, each merged through its own pull request and recorded in [COORDINATION.md](https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md). The requirement list in the brief is now [a tracked file](requirements.html) so it stops living only in chat, and the map below says which tree holds what.

## State of the workstreams

| Workstream | State | Evidence in repo | Blocking |
| --- | --- | --- | --- |
| Injury and availability collection | running — 254 rows snapshotted at 04:45Z, **re-read at 22:35Z: 279 rows, 26 clubs** | `data/injuries_2026_wk10.csv`, `data/injuries_wk10_2026_hubrefresh.csv` | no stored history, so no availability signal can be backtested (FL-22, Q-31) |
| Depth, IR and roster events | running — 227 rows | `data/depth_changes_2026_wk10.csv` | no official depth chart exists (FL-06) |
| Standings and schedule | running — 32 + 14 rows, reconciled | `data/standings_2026.csv`, `data/schedule_2026_wk10.csv` | seven official columns left out (FL-07) |
| Line origination | **computed** — walk-forward ridge ratings on 136 official games, spread MAE 9.278 vs 10.455 baseline, paired +0.295 pts vs the archived price | [Fair-Line Lab](model-lab.html) | totals are worse than a league mean and are labelled diagnostic (S-32, FL-27) |
| Depth deficiency by side of the ball | 28-club two-sided counts; verified 1st→4th string chains for 2 clubs | [Depth Deficiencies](deficiencies.html) | 26 club charts not transcribed (Q-32, S-34) |
| Signal catalogue | specified — 18 families, 6 blocked on data | `data/signals.csv` | entitlement + join keys (G-01, G-02) |
| Strategy registry | 14 entries, none tracked | `data/strategies.csv` | pre-registration + tracking ledger |
| Validation gates | 14 gates defined; 0 strategies can pass any | `data/gates.csv` | see gate matrix |
| Correlation | method defined; 12 pair classes; **no rho asserted** | `data/correlation.csv` | joint-outcome data (Q-12) |
| Skill-vs-luck protocol | derived and computed in-repo | `content/skill-vs-luck.md` | sample must still be collected |
| Competition and rewards | tiers and rules written; payout mechanism unfunded | `content/leaderboard.md` | owner decision (Q-26) |

## The blocking chain

Four items sit in front of almost everything else. They are decisions and access, not coding:

1. **Prices.** Without an opening and closing price per market there is no vig to strip, no fair value to deviate from, no CLV to measure skill with, and no way to know whether a line we originate is right. This is [Q-01](questions.html) and it blocks 9 of 14 gates.
2. **Player-level entitlement.** Snaps, routes and targets are what turn "a starter is out" into "the replacement costs 2.1 yards per carry". This is [Q-02](questions.html).
3. **A defensible depth answer.** The league publishes no depth chart, so "2nd/3rd/4th string replacing a starter" must be reconstructed from roster status, participation, designations and actual playing time ([S-06](suggestions.html), [FL-06](flagged-for-review.html)).
4. **Point-in-time storage.** Three filings a week and a dated event log, or the availability signals cannot be built at all ([FL-09](flagged-for-review.html)).

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
| Origination | [Correlation](correlation.html) | 12 pair classes, sign arguments, estimation method, blank rhos |
| Origination | [Bet types](bet-types.html) | singles, parlays and prop combos priced consistently |
| Origination | [Removing luck](skill-vs-luck.html) | sample sizes, CLV, bootstrap, split-half, luck-adjusted P&L |
| Competition | [Strategy registry](strategies.html) | 14 entries including two negative controls |
| Competition | [Leaderboard & rewards](leaderboard.html) | ranking rules, tiers, reward mechanics, gate-readiness matrix |
| Competition | [Validation gates](validation-gates.html) | 14 gates, pass criteria, what each one blocks |
| Data | [Week 10 injury report](injuries.html) | all 254 official rows, per-row source links |
| Data | [Depth & deficiencies](depth-impact.html) | who is replacing whom, and what we cannot yet quantify |
| Data | [Standings, schedule & game log](league-data.html) | 32 reconciled rows, the Week 10 slate, and a {{metric games_log}}-game verified results log for weeks 1–9 |
| Data | [Data dictionary](data-dictionary.html) | every column, its meaning, its source, its transform |
| Governance | [Verification method](methodology.html) | the rules this project will not bend |
| Governance | [Price archive](price-archive.html) | what market data the repository actually holds, what each column proves and what it cannot be used for |
| Governance | [Source registry](sources.html) → see *Repository map* above | parallel session trees are preserved intact and cross-linked: this session's audited dashboard is the root; Nine sibling trees, their owners and their page counts are in the Repository map above; only the game log was adopted into this register, after re-audit |
| Governance | [Source registry](sources.html) | {{metric sources}} sources with tier, access time and what each was used for |
