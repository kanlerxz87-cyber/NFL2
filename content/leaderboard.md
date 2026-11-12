# Leaderboard & Rewards
> A competition that ranks strategies on price quality and gate compliance rather than on recent profit — published empty, on purpose, because an empty board is the truthful state today.

Ranking by profit would rank by luck at small samples; the removing-luck page shows that a genuine 55% bettor is ahead only about 63% of the time after 100 bets. So the standing is built from the instruments that do not depend on the bounce, and the board below shows *readiness* until a forward sample exists.

## Score, and why it is defined this way

```
score = 1000 * mean_CLV_points                      (primary; result-independent)
      + 250  * bootstrap_lower_bound(ROI, 95%)      (rewards an edge that survives resampling)
      + 100  * gates_passed / gates_total           (compliance, not performance)
      - 150  * max_drawdown_units                   (risk)
eligibility: gates G-01, G-02, G-03, G-07, G-11 all hard-pass AND settled bets >= 400
tie-break, in order: larger n, then higher value per bet, then lower coverage, then higher capacity
```

Mean CLV leads because it is measurable the day the first bet settles and cannot be faked by a hot month. The drawdown penalty exists so that an entry cannot win by sizing up. Coverage enters the *tie-break* rather than the score: restraint is desirable but it must not become the objective, or the optimal strategy degenerates into betting once a year.

## Tiers and rewards

| Tier | Requirement | Reward | Why this reward |
| --- | --- | --- | --- |
| T0 prospective | registered, pre-hashed, no tracking | nothing — a claim on compute to build its pipeline | an entry earns resources by being testable, not by being described |
| T1 validated | ≥ 400 settled bets, G-12 interval excluding zero, no gate failures | staking allocation at 1u per bet plus a shared read on the price feed | the reward is capital and data access, which is what actually scales a strategy |
| T2 funded | ≥ 1,000 settled, split-half same sign, G-14 drawdown within limit | staking allocation at up to 3u, priority on capacity, first claim on new datasets | sized by demonstrated, variance-resistant edge |
| T3 lead | two consecutive promotion windows in T2 with no decay | the allocation ceiling and the right to veto a rule change that would dilute its own market | a lead strategy should be allowed to protect the edge it found |
| Clawback | any tier | drop one tier and freeze allocation | CLV negative over the 500 bets following promotion, or any gate retro-found to have failed |

Two further rules keep the competition from being gamed: **a strategy may not be re-registered under an edited spec to reset a bad window** (the hash is permanent), and **entries in the same family share one allocation**, so splitting one idea into four rows buys four stakes — it buys one stake, reported four times.

## Current standing

{{csv data/leaderboard.csv;;cols=rank:Rank,strategy:Entry,bet_type:Type,tier:Tier,gates_passed:Gates passed,gates_blocking:Blocking gates,tracked_bets:Tracked,settled:Settled,mean_clv:Mean CLV,roi_units_per_100:ROI u/100,max_drawdown:Max DD,selectivity:Coverage,reward:Reward;;source=S-DESIGN;;caption=The only populated row in the competition is ST-12, and it is populated with zeros because never betting is arithmetically exactly zero. Every other performance cell is not published because no bet has been placed. This is the correct state of a project one day old, and it is published that way rather than seeded with a backtest.}}

## Gate readiness, which is what can honestly be ranked today

{{gate_matrix}}

## Reward mechanics that are deliberately not decided

The reward *structure* is above; the reward *funding* is not, because a payout pool is a budget decision. Until that decision exists the board pays in staking allocation and data access only — see [S-25](suggestions.html) and [Q-26](questions.html). A competition with a leader board and no cost to winning produces entries, not effort, and that is the failure mode this section is written to avoid.


## The lab ledger is not this board

A separate, historical measurement now exists — [the Fair-Line Lab](model-lab.html) scores a model's *lines* against results and against an archived price on 136 completed 2026 games. It is kept off this board deliberately, for two reasons.

- Those games are **in-sample history**, not forward-tracked bets. The whole point of the zero in every performance cell above is that nobody can promote a strategy on a backtest; that rule stays.
- What the lab measures is **line quality**, not bet outcomes. It is the right instrument for deciding whether origination deserves funding, and the wrong one for allocating stakes.

The rule the lab suggests adding is [S-33](suggestions.html): before a strategy enters a ranked tier, its mean absolute error must beat the benchmark **on the identical set of games where the benchmark exists**, with a bootstrap interval that excludes zero. Unpaired means are how a weak model gets promoted by an easy week, and the lab's own numbers show why: our spread error looks 0.28 points worse unpaired and +0.295 points worse paired, on 88 of 136 games.
