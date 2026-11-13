# Flagged for Review
> Every irregularity, conflict and unverifiable item found while working line by line — published with its source links, not blocking the merge, and awaiting your call.

These items are the reason the rest of the site has blanks in it. Each row was found by comparing official pages against each other, or by trying to fetch something that does not exist. Nothing below was "fixed" silently: where two official sources disagree, both links are here and the site uses the one that is defensible rather than the one that is convenient.

Severity means what happens to a decision if the item is ignored: **high** = a number or a model built on top of this would be wrong in a way you could not see; **medium** = it degrades a feature; **low** = housekeeping.

## Game Book use restriction — FL-55

Two official books are verified: [NE at SEA, Week 1](https://static.www.nfl.com/image/upload/v1789038923/gamecenter/a8fb0d78-4feb-11f1-abca-2c54536568a9.pdf) and [NYG at WAS, Week 5](https://static.www.nfl.com/image/upload/v1791805921/gamecenter/aa94b906-4feb-11f1-abca-2c54536568a9.pdf). Both include actual lineups and game-day status sections, but carry a notice that other use requires written NFL permission. No PDF or extracted Game Book data has been stored here. Bulk capture and reuse stay blocked pending a rights/terms review ([Q-50](questions.html), [S-58](suggestions.html)); the flag is review-only and does not block publication.

{{csv data/flags.csv;;cols=id:ID,type:Type,severity:Severity,finding:What we found,evidence:Evidence,source:Sources:urls,decision_impact:Effect on decisions,status:State;;source=S-REPO;;caption=Source column links the official pages involved. Rows with "arithmetic" or "design" findings link the repository instead, because the claim is about our build, not about the league.}}

## Items that are blank on purpose

The brief said: if a value cannot be confirmed from an official source, leave it blank and flag it as unverified. These are the blanks a reader will notice first, and what each one is waiting on.

| Blank | Where it appears | What would fill it |
| --- | --- | --- |
| Game status for {{metric status_blank_rows}} of {{metric injury_rows}} Week 10 players | [injury report](injuries.html) | Sunday and Monday designations, published later in the week than our fetch (FL-02) |
| Injury body part for {{metric injury_blank_rows}} of {{metric injury_rows}} rows | [injury report](injuries.html) | the hub table does not populate it; the prose feed does, with an explicit join (FL-08) |
| Depth rank (1st / 2nd / 3rd / 4th string) | [depth & deficiencies](depth-impact.html) | no official depth chart exists; reconstruct from roster status, participation and playing time (FL-06) |
| Replacement effect in points or yards | [depth & deficiencies](depth-impact.html) | licensed player-level data (Q-02) |
| Every correlation value ρ | [correlation](correlation.html) | joint-outcome history we have not fitted; only two arithmetic cases are 1.00 by construction |
| Our number, the consensus close, the residual | [line origination](line-origination.html) | a price feed (Q-01) — this is the whole objective, currently un-earnable |
| Tracked bets, CLV, ROI, drawdown on the leaderboard | [leaderboard](leaderboard.html) | forward tracking after pre-registration; nothing is back-filled from a backtest by rule (S-04) |
| Seven official standings columns | [standings](league-data.html) | field names from the underlying data source; guessing column order was refused (FL-07) |
