# Suggestion Register
> The dedicated review page: {{metric suggestions}} ways to improve the site and the system, each with the problem it solves, what it would take, and a recommended path — so a best option can be chosen before anything is implemented.

## How to use this page

Nothing here has been implemented except what your brief itself required (the coordination board, the source-linked tables, the blanks-not-guesses rule, the review page). Everything else is queued for a decision.

- **I / E** are impact and effort, on an H/M/L scale. They are my judgement about this codebase and data state, not measurements — recorded as judgement so they can be argued with.
- **Reversible** is the important column: a reversible change with high impact should be approved on judgement alone; an irreversible one deserves a look first.
- **Decision** is yours. `adopted (v1)` means it is already visible in this build, so the honest record says so rather than claiming a future win. `recommended` means approve-and-build. `blocked` means it cannot proceed until a question on the [question register](questions.html) is answered.

## Tier 1 — approve now (highest impact per unit of risk)

{{csv data/suggestions.csv;;cols=id:ID,title:Suggestion,category:Area,problem_it_solves:Problem it solves,proposal:What we would build,impact:I,effort:E,reversible:Reversible,depends_on:Depends on,recommended_path:Recommended path,decision:Decision;;source=S-DESIGN;;filter=decision=recommended;;caption=Rows containing "recommended" in the recommended-path column, in any state — including those blocked behind a data decision.}}

## Tier 2 — everything else, including what is already live

{{csv data/suggestions.csv;;cols=id:ID,title:Suggestion,category:Area,proposal:What we would build,risk:Risk,depends_on:Depends on,evidence:Evidence behind it,recommended_path:Recommended path,decision:Decision;;source=S-DESIGN;;filter=decision=!recommended}}

## What I would actually do first, in order

| Step | Suggestion | Why this order |
| --- | --- | --- |
| 1 | S-04 pre-registration, no backtests on the leaderboard | Costs nothing and it is the only rule that stops the whole competition becoming self-deception later |
| 2 | S-01 + S-02 + S-13 + S-24 (already adopted) | the honesty layer: timestamps, blanks as first-class, frozen verification vocabulary, no unsourced numerics |
| 3 | S-19 refuse "No Injuries Reported" as zero | protects every downstream feature from the most likely silent error in this dataset |
| 4 | S-15 32-team roster sweep | makes joins trustworthy; without it no team-level number is defensible |
| 5 | S-06 availability graph as a dataset | this, not the model, is the project's differentiator — and it is the only path to the depth requirement |
| 6 | S-09 + S-10 + S-11 pricing, parlay and prop-combo framework | only once Q-01 (prices) and Q-12 (joint data) close |
| 7 | S-18 luck-removal panel on the dashboard | becomes meaningful with the first tracked bets, worthless before |

## The decisions I cannot make for you

| ID | Decision | Why it is not mine |
| --- | --- | --- |
| S-25 / Q-26 | What the leaderboard pays out | it is a budget and incentive question |
| S-05 / Q-11 | Whether v1 covers live, futures and alternate markets | it is a scope and cost trade-off |
| S-27 / Q-27 | Whether losing records are published | transparency preference |
| S-28 / Q-28 | Sign-off on the verification vocabulary | it defines what the project is allowed to claim in public |


## What the second verification pass adds (session `a392a193`, 12 Nov 2026)

Seven new items, all of them born from a check rather than from a wish: each one traces to a measured result or a defect found by comparing two official pages. S-35 and S-36 are the two that change what the project can do next.

{{csv data/suggestions.csv;;cols=id:ID,title:Suggestion,category:Area,problem_it_solves:Problem it solves,proposal:Proposal,impact:Impact,effort:Effort,risk:Risk,reversible:Reversible,depends_on:Depends on,evidence:Evidence behind it,recommended_path:Recommended path,decision:Decision;;filter=id=S-3;;source=S-BRIEF;;caption=Filtered to the seven rows this pass added. The full board is above; nothing here is implemented on your instruction.}}

### Revised order of first moves

The order at the top of this page was written before the lab existed. Two of its steps have now been done or superseded, so the short version is:

| Step | Suggestion | Why it moved |
| --- | --- | --- |
| 1 | S-35 daily stored injury snapshot | the second read of the hub proved the drift is real (25 rows in 18 hours) and that no availability signal can be built without a history — this is now the binding constraint on half the brief |
| 2 | S-36 alias table + join-row-count check | half a day, and it is the difference between a cross-check and a false confirmation |
| 3 | S-37 publish spread as a line, totals as a diagnostic | the measurement is in and it says our totals do not beat a league mean |
| 4 | S-38 paired-error admission gate | the board needs it before any strategy can be promoted on lab numbers |
| 5 | S-39 all-32-club depth-chain transcription | the pattern works on two clubs; the gap is cadence, not method |
| 6 | S-40 correlation-adjusted parlay pricing with a one-ticket cap | measured coupling is large enough to matter (42.4%) and small-sample enough to cap |
| 7 | S-41 repository map on the landing page | implemented in this pass as a build-computed table, so page counts cannot drift from the tree |
