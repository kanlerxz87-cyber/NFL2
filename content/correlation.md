# Correlation
> How we determine correlation between bet legs, which signs we are willing to defend without data, and the fact that every numeric ρ on this page is deliberately blank.

Correlation is not a refinement here; it is the difference between a parlay we can price and a parlay we are gambling on. An operator's same-game price is a *joint* probability, and the gap between a joint and the product of two marginals is where the money goes. The brief asked for correlation values to be determined — the honest answer is that the framework and the *signs* are determinable now, and the magnitudes require joint-outcome history we do not yet have. So this page publishes the method and leaves ρ as `not published`, rather than filling the column with plausible-looking constants that would then be quoted back at us as findings.

## The identity we use

To keep the framework concrete, correlation is represented by a single-parameter common-shock model. One game-state shock S is equally likely to be +1 or −1; conditional on S, each leg wins with probability p ± s. Then, in closed form:

```
rho  =  s^2 / ( p (1 - p) )                 same-direction legs
rho  = -s^2 / ( p (1 - p) )                 opposite-direction legs
P(all n legs win)  =  1/2 (p + s)^n + 1/2 (p - s)^n
s = 0  <=>  independence, so the product rule is a special case, not a rival model
```

That gives one knob with an interpretable meaning — how much of each leg's variance is shared — and it degenerates to the naive calculation exactly when it should. It also makes the negative case expressible, which a naive "multiply the legs" habit cannot even represent.

{{csv data/computed_parlays.csv;;cols=case:Case,legs:n,p_each:p per leg,rho_target:rho assumed,shock_s:shock s,joint_independence:product of marginals,joint_model:joint under the model,fair_dec_indep:fair dec (indep),fair_dec_model:fair dec (model),fair_american_model:fair price (model),read:Read;;source=S-CALC;;caption=Assumptions stated, arithmetic exact, no market prices involved. The p and rho values are parameters chosen to demonstrate the method; they are not estimates of any real bet. Note the sign flip: for same-game stacks, the product rule is too pessimistic about the joint; for teammates competing for the same target pool, it is too optimistic — and both errors grow with leg count.}}

## Pair classes, signs we defend, and the numbers we refuse

{{csv data/correlation.csv;;cols=id:ID,pair_class:Pair class,example_legs:Example legs,expected_sign:Sign we assert,sign_basis:Why that sign,magnitude:Magnitude,estimation_method:How it will be estimated,rho:rho,ci_low:CI low,ci_high:CI high,verification:Verification state;;source=S-DESIGN;;caption=Two rows are 1.00 by construction, not by measurement: a main line and its own alternate, and the same position at two books, are one bet. Every other row is a sign argument plus an estimation plan.}}

## Two correlations we have actually measured

Most of this page is method, because most of it cannot be measured without prices. Two pair classes can
be measured from data already in the repository: the 136 settled results of weeks 1–9 carry both teams'
final scores, which *is* the joint outcome those classes need. What is measured below is the correlation
between **real game scores**. It is not ρ, which is the correlation between **bet settlements** and needs
a market archive. Writing the first as the second is the single most common way this analysis becomes
dishonest, so the register keeps `rho` blank and records the measured `r` separately.

{{csv data/computed_correlation.csv;;cols=id:ID,quantity_a:Quantity A,quantity_b:Quantity B,n:n,r:Pearson r,r_squared:r-squared,t:t,ci_low:95% CI low,ci_high:95% CI high,p_value_two_sided:p (two-sided),read:Read;;source=S-CALC;;link_col=source_file;;caption=Recomputed on every build from data/games_2026_wk1_9.csv and re-derived independently by tools/verify.py, which fails if the register disagrees with a fresh calculation. 95 per cent intervals use the Fisher z transform.}}

How to read the two rows:

- **C-07 (both team totals).** r = +0.076, and the interval runs from −0.094 to +0.241. The sign matches the
  argument that scoring is coupled through pace, but at n = 136 the effect is indistinguishable from zero.
  This is a case where the honest answer is "small, and we cannot yet say it is not noise" — which is a
  more useful input to a pricing decision than a number borrowed from a paper.
- **C-08 (spread and total).** r = −0.161, interval −0.321 to +0.008, p = 0.062. The sign is the one the page
  predicted six sections ago: a game that stays close suppresses the total. It is the more interesting
  result precisely because it is not significant — it says the effect, if real, is small enough that
  treating spread and total as independent costs very little, and that claiming otherwise would need more
  than one season of data.

What this does **not** license: multiplying these into a parlay price. A correlation between scores is not a
correlation between *settled bets at a line*, because the line moves, pushes void legs, and each leg's
payoff depends on where the number sits relative to the actual score. That distinction is the whole reason
the `rho` column stays blank.

## What must exist before a ρ can be published

| Requirement | Why it is the bottleneck | Status |
| --- | --- | --- |
| A settled joint-outcome table (leg A, leg B, both, per game) | empirical ρ needs the joint count, and marginals alone cannot produce it | not started — needs outcomes joined to prices |
| Fixed leg definitions per market | a reception prop at 4.5 and one at 6.5 have different couplings; pooling them manufactures a meaningless average | design done, needs the market scope decision (Q-11) |
| Void and push handling | a voided leg silently changes the joint sample and inflates measured ρ | gate G-05 |
| A game-total conditioning variable | most same-game correlation is really "both legs increase in a high-scoring game"; conditioning on the score removes much of what a raw ρ would capture | stage 5 of [origination](line-origination.html) |

## Reading the public research without over-reading it

| Item | What it supports | What it does not support |
| --- | --- | --- |
| A 2026 preprint on cross-game parlay prices in prediction markets | the direction: parlay prices drift above the product of their own legs' prices, and the gap grows with leg count; and the authors explicitly exclude same-game parlays as non-trivially correlated | the magnitude, and its use as an NFL-sportsbook figure — a public review objects that the leg-matching window can manufacture part of the effect |
| The favourite–longshot literature (compound bets mispriced because bettors mishandle compound lotteries) | why a compound product like a parlay is the structural place for mispricing to live | any specific number in any specific market here |

We cite these as motivation for the *framework*, and we do not carry their coefficients into our pricing. An un-fitted borrowed constant is the most common way a small model starts believing its own marketing.
