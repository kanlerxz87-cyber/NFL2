# Validation Gates
> Fifteen gates every strategy must clear before it may be ranked, funded or trusted — with what each one tests, what it blocks, and what is missing that stops any of them from being passed today. Fourteen are promotion-side gates; G-15 is the demotion gate that sends a promoted strategy back to paper (the two-sided rule the brief demands; added 2026-11-16 as C-14 in the brief traceability register).

A gate is not a formality. In this domain almost every failure looks like success at some point in the middle, so the gates exist to make "it looked good" insufficient. Each row states a *pass criterion* that can be checked by someone else, because a gate nobody can audit is a mood.

{{csv data/gates.csv;;cols=id:ID,gate:Gate,class:Class,applies_to:Applies to,test:What the test does,pass_criterion:Pass criterion,blocks:What it blocks,current_status:State today,missing_input:What is missing;;source=S-DESIGN;;caption=Hard gates cannot be waived, traded off, or overridden by a good run. Soft gates may be waived by an explicit owner decision, which is then recorded on the review page.}}

## Gate clusters, and the order they clear in

| Cluster | Gates | Clears when | Note |
| --- | --- | --- | --- |
| Data trust | G-01, G-02 | a source list is approved and every id resolves | the roster sweep alone takes G-02 most of the way |
| Time honesty | G-03, G-04 | the store is event-sourced with timestamps and outputs are reproducible | this is the cluster that kills most backtests on contact, which is its purpose |
| Ticket correctness | G-05, G-07 | settlement rules and executed prices exist | parlays and prop combos are unusable without G-05; a void leg silently changes a joint estimate |
| Model quality | G-06 | a validation set of settled outcomes joined to our own predictions | calibration, not accuracy — a model right 55% of the time with 60% stated confidence is broken |
| Evidence | G-08, G-09, G-10, G-12 | forward tracking, and only forward | the sample-size arithmetic is on the [removing-luck page](skill-vs-luck.html) |
| Governance | G-11, G-13, G-14 | registration discipline and a bankroll policy | the cheapest cluster to satisfy and the one most often skipped |
| Demotion | G-15 | the way back down | fires only after promotion, which is why it has never run yet |

## The demotion gate (G-15) — what sends a live strategy back to paper

Every gate above is one-sided by construction: it states what earns promotion and says nothing about what revokes it. G-15 (added 2026-11-16, the register row behind brief item C-14) is the other side:

- **Skill collapse.** Benchmark-relative Brier skill below 0 over the trailing window, with a one-sided 95% interval.
- **Price decay.** Rolling 20-ticket mean closing line value below −0.5, with a 95% interval excluding 0.
- **Repeated drawdown breach.** The G-14 drawdown limit breached twice inside a rolling 30-day window.

Any one trigger with interval support demotes the strategy to paper until it re-qualifies through the promotion gates from G-08 onward, and the trigger, its interval and the demoted entry are published as register rows before any re-promotion. The gate is defined but untestable until something is promoted — and nothing is promoted, because the leaderboard is empty by design.

## Status, stated plainly

Zero strategies can currently pass any gate, and the matrix on the [leaderboard page](leaderboard.html) shows why: the inputs for the earliest gates — a licensed price feed, a full roster join, a point-in-time store — do not exist in this repository. That is not a criticism of the specifications; it is the reason no number on this site is called an edge.

## The four things that would move the most gates

| Action | Gates it unblocks | Register link |
| --- | --- | --- |
| Approve a price source and ingest three seasons | G-01, G-06, G-07, G-12 (partially G-10) | [Q-01](questions.html), [S-09](suggestions.html) |
| Run the 32-team roster and IR sweep with a daily diff | G-02, part of G-01 | [S-15](suggestions.html), [FL-03](flagged-for-review.html) |
| Store every filing as a dated event, three times a week | G-03, G-04, and the whole availability signal family | [FL-09](flagged-for-review.html) |
| Pre-register the fourteen strategy specs and open the ledger | G-11, then the clock starts on G-08/G-09 | [S-04](suggestions.html) |
