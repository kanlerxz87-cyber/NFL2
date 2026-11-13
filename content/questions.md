# Open Questions
> The questions that must be answered before a decision here can be called reasonable — with what we already have, what is missing, and how the gap closes.

{{csv data/questions.csv;;cols=id:ID,question:Question,blocks:What it blocks,what_we_have:What we already have,what_we_lack:What we do not have,how_to_close:How to close it,priority:P,status:State;;source=S-DESIGN;;caption=P0 means a decision or a dataset that blocks other work. "blocked-on-owner" means the analysis cannot proceed without a choice that is not ours to make.}}

## How to read the two middle columns

The brief asked for a clear separation between information we already have and information we do not. Those are the two central columns, and they are the reason several rows look blunt: on most modelling questions we have *nothing* — no prices, no snaps, no licensed history. Saying so is the deliverable. Where the "what we have" column names a dataset, that dataset is on this site with per-row sources, so the answer to "do we really have this" is checkable rather than asserted.

## Questions that gate the next decisions

| # | Question | Unblocks |
| --- | --- | --- |
| Q-01 | Which price feed, at what latency and what licence cost? | 9 of 14 gates, every CLV and edge number, the whole origination objective |
| Q-02 | Which player-level data are we entitled to store and re-price? | replacement cost in points, unit-level deficiency, prop modelling |
| Q-05 | What is authoritative for depth rank, given that no official depth chart exists? | the entire "backups replacing starters" requirement |
| Q-07 | How do we reconstruct the game-time active/inactive list? | who actually played, which is the ground truth for every availability model |
| Q-23 | Is the 2026 roster churn real, or does our join silently mis-assign players to clubs? | trust in every team-level number produced from these rows |
| Q-33 | Should the two measured correlations be used in parlay pricing, given both intervals include zero? | the parlay and prop-combo side of the objective, and two validation gates — this is the newest P0 and it appeared only once the correlations could actually be measured |
| Q-50 | May NFL Game Books be fetched, retained, parsed, and used for this project? | bulk lineup/inactive collection and any reuse of gamebook-derived player data; written permission or applicable terms are missing |
