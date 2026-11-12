# Validation Gates
> Fourteen gates every strategy must clear before it may be ranked, funded or trusted — with what each one tests, what it blocks, and what is missing that stops any of them from being passed today.

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

## Status, stated plainly

Zero strategies can currently pass any gate, and the matrix on the [leaderboard page](leaderboard.html) shows why: the inputs for the earliest gates — a licensed price feed, a full roster join, a point-in-time store — do not exist in this repository. That is not a criticism of the specifications; it is the reason no number on this site is called an edge.

## The four things that would move the most gates

| Action | Gates it unblocks | Register link |
| --- | --- | --- |
| Approve a price source and ingest three seasons | G-01, G-06, G-07, G-12 (partially G-10) | [Q-01](questions.html), [S-09](suggestions.html) |
| Run the 32-team roster and IR sweep with a daily diff | G-02, part of G-01 | [S-15](suggestions.html), [FL-03](flagged-for-review.html) |
| Store every filing as a dated event, three times a week | G-03, G-04, and the whole availability signal family | [FL-09](flagged-for-review.html) |
| Pre-register the fourteen strategy specs and open the ledger | G-11, then the clock starts on G-08/G-09 | [S-04](suggestions.html) |
