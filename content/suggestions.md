# Suggestion Register
> The dedicated review page: {{metric suggestions}} ways to improve the site and the system, each with the problem it solves, what it would take, and a recommended path — so a best option can be chosen before anything is implemented.

## How to use this page

Some suggestions have since been adopted by this or earlier sessions; their decision field says so. This register does not treat an owner-only question as approved. S-43 is partly implemented here (read-time display and an exact-field verifier), while its refresh cadence remains open as Q-40; S-44 and S-45 are already adopted upstream. The current order below separates completed work from owner decisions and rights-blocked work.

- **I / E** are impact and effort, on an H/M/L scale. They are my judgement about this codebase and data state, not measurements — recorded as judgement so they can be argued with.
- **Reversible** is the important column: a reversible change with high impact should be approved on judgement alone; an irreversible one deserves a look first.
- **Decision** is yours. `adopted (v1)` means it is already visible in this build, so the honest record says so rather than claiming a future win. `recommended` means approve-and-build. `blocked` means it cannot proceed until a question on the [question register](questions.html) is answered.

## Tier 1 — approve now (highest impact per unit of risk)

{{csv data/suggestions.csv;;cols=id:ID,title:Suggestion,category:Area,problem_it_solves:Problem it solves,proposal:What we would build,impact:I,effort:E,reversible:Reversible,depends_on:Depends on,recommended_path:Recommended path,decision:Decision;;source=S-DESIGN;;filter=decision=recommended;;caption=Rows whose decision is exactly "recommended"; blocked, partly adopted and owner-only items remain visible in Tier 2.}}

## Tier 2 — everything else, including what is already live

{{csv data/suggestions.csv;;cols=id:ID,title:Suggestion,category:Area,proposal:What we would build,risk:Risk,depends_on:Depends on,evidence:Evidence behind it,recommended_path:Recommended path,decision:Decision;;source=S-DESIGN;;filter=decision=!recommended}}

## Current order — 13 November 2026, 12:53Z

This is a review order, not approval to make owner-only decisions. “Adopted” means the work is already present; it is not a new task. No gamebook data collection is authorized by this recommendation.

| Step | Suggestion / question | State and next action |
| --- | --- | --- |
| 1 | Q-42 / S-46 — choose the canonical injury register | Owner decision. Preserve the 04:45Z and 22:35Z historical files; choose how the dated series and current coverage metric are presented before changing the dashboard's lead number. |
| 2 | Q-50 / S-58 — gamebook use rights | Rights review is a blocker. The two verified PDFs establish lineups and explicit game-day status, not ordinal depth or snaps; do not bulk-fetch, retain, parse, or republish gamebook-derived data until written permission or applicable terms are confirmed. |
| 3 | Q-40 / S-43 — cumulative-table refresh cadence | Partly adopted: standings show `2026-11-13T12:53Z` and the verifier checks source, timestamp, and all 256 values. The owner still chooses per-settlement, weekly, or per-build refresh and how that affects prior grades. |
| 4 | S-44 + S-45 — auto-grade and disclose the required sample | Adopted upstream and verified: hashes are checked before grading, and every performance figure carries its observed count and sample requirement. No duplicate implementation is needed. |
| 5 | S-47 / S-35 — retain dated injury reads and measure deltas | Continue only under an agreed cadence; the 04:45Z, 22:35Z, 06:52Z subset, and 12:46Z full-hub reads are separate records, not a single continuous series. |
| 6 | S-39 / S-53 — expand club-chart depth coverage | Keep the club's UNOFFICIAL label and source URL attached; do not claim league-wide 2nd/3rd/4th-string coverage from the two gamebooks. |

The earlier generic priority list is superseded by this dated order. Existing owner-only decisions listed below remain open.

## The decisions I cannot make for you

| ID | Decision | Why it is not mine |
| --- | --- | --- |
| S-25 / Q-26 | What the leaderboard pays out | it is a budget and incentive question |
| S-05 / Q-11 | Whether v1 covers live, futures and alternate markets | it is a scope and cost trade-off |
| S-27 / Q-27 | Whether losing records are published | transparency preference |
| S-28 / Q-28 | Sign-off on the verification vocabulary | it defines what the project is allowed to claim in public |
| S-43 / Q-40 | Refresh cadence for standings and other cumulative tables | it determines when each rolling source is re-read and whether earlier grades are superseded |
| S-46 / Q-42 | Which dated injury register is canonical | it changes the coverage number the dashboard leads with; older snapshots must remain preserved |
| S-58 / Q-50 | Permission to retain, parse, and reuse NFL Game Books | the PDFs require written permission for other use; no permission is presumed or obtained here |


## What the second verification pass adds (session `a392a193`, 12 Nov 2026)

Seven new items, all of them born from a check rather than from a wish: each one traces to a measured result or a defect found by comparing two official pages. S-35 and S-36 are the two that change what the project can do next.

{{csv data/suggestions.csv;;cols=id:ID,title:Suggestion,category:Area,problem_it_solves:Problem it solves,proposal:Proposal,impact:Impact,effort:Effort,risk:Risk,reversible:Reversible,depends_on:Depends on,evidence:Evidence behind it,recommended_path:Recommended path,decision:Decision;;filter=id=S-3;;source=S-BRIEF;;caption=Filtered to the seven rows this pass added. The full board is above; nothing here is implemented on your instruction.}}

### Historical order of first moves (12 Nov; superseded by the current order above)

The order at the top of this historical verification-pass section predates the later injury and forward-sample work. It is retained as a dated record; use the current 13 Nov order above for present decisions:

| Step | Suggestion | Why it moved |
| --- | --- | --- |
| 1 | S-35 daily stored injury snapshot | the second read of the hub proved the drift is real (25 rows in 18 hours) and that no availability signal can be built without a history — this is now the binding constraint on half the brief |
| 2 | S-36 alias table + join-row-count check | half a day, and it is the difference between a cross-check and a false confirmation |
| 3 | S-37 publish spread as a line, totals as a diagnostic | the measurement is in and it says our totals do not beat a league mean |
| 4 | S-38 paired-error admission gate | the board needs it before any strategy can be promoted on lab numbers |
| 5 | S-39 all-32-club depth-chain transcription | the pattern works on two clubs; the gap is cadence, not method |
| 6 | S-40 correlation-adjusted parlay pricing with a one-ticket cap | measured coupling is large enough to matter (42.4%) and small-sample enough to cap |
| 7 | S-41 repository map on the landing page | implemented in this pass as a build-computed table, so page counts cannot drift from the tree |
