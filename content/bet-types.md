# Bet Types — Singles, Parlays, Prop Combos
> The same fair-value machinery applied to the three products the brief names, with what each one costs, where each one leaks, and the rules we will follow when betting each.

Every number below is arithmetic on stated assumptions. There are no offered prices in this repository — no spread, no total, no prop line — so nothing here says "the market is offering X". Where a price would sit, the cell says `not published` ([FL-10](flagged-for-review.html)).

## Shared machinery

```
implied probability from an American price
    negative price:  p = -price / (100 - price)
    positive price:  p =  100 / (price + 100)

no-vig probability   = p_side / (p_side + p_other)          [two-way market]
edge (per unit)      = p_ours * (1 + dec - 1) - (1 - p_ours) * 1  =  p_ours * dec - 1
expectancy in units  = p_ours * payout_win - (1 - p_ours) * stake
stake                = f_Kelly * lambda ,  f_Kelly = (p_ours*(b+1) - 1) / b
```

`b` is the decimal payout minus one, `lambda` is the fraction of full Kelly we are willing to risk, and full Kelly is *not* a recommendation — it is the growth-optimal stake for a *known* probability, and our probability is estimated. The model-error term from [skill-vs-luck](skill-vs-luck.html) is what shrinks `lambda`.

{{csv data/computed_vig.csv;;cols=market:Two-way pair,price:Prices,implied_prob:Implied prob each side,two_sides_sum:Sum of both sides,overround_pct:Overround pct,no_vig_prob:No-vig prob,read:Cost of playing both sides;;source=S-CALC;;caption=Exactly how much a two-way market charges to be in it. Any claimed edge smaller than the overround figure is not an edge, whatever the model says.}}

## Single bets (spread, total, moneyline)

| Aspect | Position |
| --- | --- |
| Why this is the base product | the least-priced, most liquid, and the only type where our residual against the market is directly interpretable as model quality |
| Cost | the overround above; on a −110/−110 pair the vig is 4.55% of a two-sided cycle |
| Main failure mode | betting the *level* of a public fact instead of the *surprise*, which converts a news feed into a fee generator |
| Entry rule | residual > vig **and** residual > k × model error; otherwise no bet, and "no bet" is logged as a decision with a reason |
| Stake rule | fractional Kelly on our own interval, capped per game, positions netted across books before staking (C-12) |
| Evaluation | CLV per ticket, plus calibration of our probability against settled results |

## Parlays

Parlays are where an operator's margin compounds, because the vig on each leg is multiplied rather than added — and where a bettor's *apparent* price looks most generous, because the payout grows geometrically while the true joint probability often does not.

1. **Price the joint, never the product.** The product of marginals is only correct when legs are independent, which is precisely the assumption same-game legs violate. Use the joint from the common-shock model or, better, from the conditioned scoring process.
2. **The two errors go in opposite directions.** For same-direction stacks the product rule *understates* the true joint; for teammates competing for one target pool it *overstates* it. Both errors grow with leg count. A book that prices a stack short is not making an error; it is pricing a covariance we have not fitted.
3. **Derivative legs are the same bet.** A main line and its alternate, or one position held at two books, have ρ = 1.00 by construction. Net them before staking or you will double a risk you already counted once.
4. **Void handling is a leg-level problem.** A pushed leg must be removed from the parlay by rule, consistently in the backtest and the forward ledger, or the correlation estimate is contaminated by tickets that never existed (gate G-05).

| Rule | Threshold |
| --- | --- |
| Maximum legs in a ticket we will price | 3 — beyond that the joint estimate's error dominates the offered payout |
| Accept a parlay only if | offered price beats our joint estimate by more than the sum of the individual leg edges |
| Default action on cross-game multis | decline; the product is engineered for the house and the correlation adjustment buys nothing |

## Player-prop combos

| Source of coupling | Direction | How we represent it |
| --- | --- | --- |
| Shared game script and pace | positive | condition every leg on the same scoring process (SIG-13) |
| One quarterback's attempts | positive across his receivers, jointly bounded | a per-play allocation over receivers |
| A team's target budget | negative between teammates (SIG-12) | an explicit sum constraint, so two teammate overs cannot both be priced as if the volume doubled |
| Snap count and involvement | positive between a back's rush yards and receptions | a single involvement factor, then fit the residual sign rather than assume it (ST-10) |
| Touchdown dependency | positive, mechanical | a count-based identity, since a rushing score is a rush-yards event |
| Lineup uncertainty | positive in the tails | the availability mixture from [origination](line-origination.html): an un-declared starter fattens the tail, which matters more for a prop line than for a spread |

**Why props are the honest place to start, and the dangerous one.** Props are slower to reprice than a game spread and thinner, so information survives longer — that is the argument for them. The counter-argument is that prop *combos* are the least efficiently priced product in the sport precisely because the covariance is hard, and a model that is confidently wrong about a covariance is worse than a model that never looked. So: single props first, combos only after our fitted joint exists, and one-number-per-player limits until then.
