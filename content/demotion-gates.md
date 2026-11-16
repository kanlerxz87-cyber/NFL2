# Demotion Gates, Falsifiers & Price Policy
> Design register (blue badge): the missing half of the validation system. Every gate this project registered was one-sided — it said what promotes a strategy and nothing demotes one (FL-86). This page registers the demotion side, the two-sided falsifier field for every strategy (BL-17), and the price-data policy that must stand before any backtest is published (BL-20).

Nothing on this page is a result. It is specification, pre-registered on 2026-11-16 by session `d304c6fe`, and it is enforceable from the moment a strategy goes live.

## Demotion gates (BL-08 — live strategies return to paper)

{{csv data/demotion_gates_d304c6fe.csv;;cols=id:ID,name:Gate,class:Class,direction:Direction,rule:Rule,trigger:Trigger,window:Window,evidence_required:Evidence,status:Status;;source=S-BRIEF;;caption=Each gate names both the number that clears it and the condition that demotes. S-BRIEF is the owner-instruction reference — these are project rules, not NFL facts. DG-03 and DG-04 are enforceable today because the evidence they need (dated source reads, hash-locked registrations) already exists. DG-01 and DG-02 wait on graded decisions and price capture respectively; DG-06 governs any return to live. Together they close FL-86: a promoted strategy can now be demoted on evidence.}}

## What would change our mind — two-sided, per strategy (BL-17)

{{csv data/wwcm_d304c6fe.csv;;cols=strategy_id:ID,strategy:Strategy,would_change_our_mind_for:What would change our mind (for),would_change_our_mind_against:What would change our mind (against),status:Status;;source=S-BRIEF;;caption=One row per registered strategy ([strategy registry](strategies.html)), each with a falsifier in both directions. A strategy without both fields cannot be promoted: the "against" column is the sentence that must be true of the world before we trust the "for" column. These are pre-registered commitments, written before the Week 11 forward sample is graded.}}

## Price-data policy (BL-20 — decided before any backtest is published)

The policy is adopted on 2026-11-16 and recorded in full in the repository at
[docs/PRICE-DATA-POLICY-d304c6fe.md](https://github.com/kanlerxz87-cyber/NFL2/blob/main/docs/PRICE-DATA-POLICY-d304c6fe.md). The binding clauses:

1. **No price without a vintage.** Every price used anywhere must carry a capture timestamp and a source id. A price with no vintage is not evidence (FL-21, FL-29, FL-30).
2. **Community archives are comparison anchors, never truth.** The nfldata archive has no documented vintage; anything computed against it is labelled exploratory and can never be called a published backtest.
3. **The price-snapshot store schema is fixed now** (BL-01): `market id · market type · opening price + timestamp · closing price + timestamp · source id · capture hash`. Opening is the first price observed after market open; closing is the last before kickoff.
4. **No ROI on the leaderboard until the store holds a full week of vintaged rows.** Until then every ROI cell stays blank and flagged — BL-01's gate (G-01, G-07) is unchanged.
5. **Retrospective labeling.** Every backtest already published against unvintaged prices is re-labelled exploratory wherever it appears (this includes the fair-line lab's archive comparisons).

## Where this sits in the gates system

The [validation gates page](validation-gates.html) keeps its fourteen promotion gates; this page supplies their demotion counterparts and the falsifier fields. The demotion gates are also the enforcement arm of the pre-registration rule (BL-70): a frozen rule whose hash fails its integrity check demotes immediately under DG-04, with no discretion.
