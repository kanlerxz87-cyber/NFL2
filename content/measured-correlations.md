# Measured Correlations
> The correlation values the brief asks for, computed on games this repository can actually verify — with intervals wide enough to be true, and an explicit statement of what a number this small cannot support.

The design page ([Correlation](correlation.html)) lists twelve *pair classes* and publishes no rho, because fitting one requires joint-outcome data nobody had assembled here. This page is that assembly, done from the one corpus in the repository that survives a row-by-row source check: the [136 completed 2026 games](league-data.html), each linked to its official nfl.com game page. Nothing here is fitted on a model's own output except where the row says so.

## The measurements

`spans_zero` is the column to read first. Where it says *yes*, the honest answer to "is these two things related?" is **"not measurable on one season."**

{{csv data/measured_correlations_a392.csv;;cols=id:ID,pair:Pair measured,n:N,rho:rho or coefficient,ci_low:CI low,ci_high:CI high,spans_zero:Interval spans zero,method:Method,betting_implication:What it means for a ticket;;source_col=source;;group=;;caption=Intervals are a 4,000-resample percentile bootstrap with a fixed seed, so the build is reproducible. M-06 is not a correlation: it is a measured home-field coefficient with a normal-approximation interval.}}

## What each one does to the decision

**M-01 · the two teams' scores barely move together (rho 0.076, CI −0.088 to 0.244).** A "both teams to score over" style stack therefore behaves close to independently, and the independence assumption in [Bet types](bet-types.html) is not obviously wrong for this pair. Note the interval, not the point estimate: it is compatible with anything from a mild negative to a real positive.

**M-03 · last week's blowout tells you almost nothing about next week (rho 0.088 on 240 consecutive club-game pairs, CI −0.03 to 0.20).** This is the *removal of luck* the brief asks for, stated as a number: at club-game level the week-to-week signal is ~1% of shared variance. A strategy whose whole idea is "team X dominated, back them again" is buying noise at full price, and the leaderboard should not reward it ([S-38](suggestions.html)).

**M-04 · record tracks Pythagorean expectation tightly (rho 0.863, CI 0.741 to 0.938).** The residual is the interesting part: the wins a club took that its point margin did not predict. Ranked by rating rather than by wins, the 2026 table separates the two, and `luck_delta_wins` below is the per-club gap.

{{csv data/ratings_2026_a392.csv;;cols=team:Club,net_rating:Net rating,pace_rating_pts_above_league_mean:Pace (pts over league mean),rank_by_rating:Rank by rating,rank_by_wins:Rank by wins,pyth_expectation_wins:Pyth. expected wins,luck_delta_wins:Luck (wins − expected),games:GP,w:W,l:L,t:T;;source_col=source;;caption=Ratings are the fitted coefficients after week 9, ridge λ=5; pace is a deviation from the league-mean total, so the two halves are added back in the model's prediction. Rank by wins breaks ties alphabetically. Clubs whose rank-by-rating and rank-by-wins disagree by 8 or more places are where the season's luck is concentrated — that is a *feature list*, not a bet.}}

**M-05 · rest-days correlate with the home margin (rho 0.426, CI 0.257 to 0.572) — but read the decomposition before the headline.** In a nine-week sample a rest differential of ±7 days *is* bye-week status, so this row and the bye row are the same fact:

{{csv data/rest_and_hfa_2026_a392.csv;;cols=bucket:Rest situation,games:Games,mean_home_margin:Mean home margin (pts),sd:SD,se:SE,ci_low:CI low,ci_high:CI high,read:Read;;source_col=source;;caption=Two clubs rest, one of them plays, and the margin moves by around 12 points in the rested club's direction on 17 games. That is implausibly large for a fatigue effect and entirely plausible for a selection effect: the bye falls differently for good and bad clubs, and a single season cannot separate the two. Treat as a hypothesis to test on 2013–2025, not a signal to trade.}}

**M-06 · home-field advantage in 2026 is 0.50 points, CI −1.80 to +2.80 (129 non-neutral games).** The most cited number in football betting is not measurable this season, and the conventional 2.5 points sits far outside this interval. Every model in this repository that hard-codes a home field is currently importing a prior, not a measurement — which is why the coefficient here is estimated rather than assumed, and why the Munich fixture is flagged instead of adjusted ([FL-32](flagged-for-review.html)).

## Same-game parlay coupling — the number that changes a ticket

A two-leg same-game parlay is priced by multiplying two marginal probabilities. That is only fair if the legs are independent. Two legs a bettor stacks constantly — home covering the spread and the game going over — are *negatively* coupled, and the measured size of that coupling is the whole story:

| Leg pair | Measured on | Joint observed | Product of marginals | A ticket priced on independence is wrong by |
| --- | --- | --- | --- | --- |
| home covers our spread + game over our total | 88 games, our own lines | 0.1818 | 0.2079 | **14.4%** too generous in hit rate |
| home covers the archived spread + game over the archived total | 82 games, archived prices | 0.1364 | 0.1942 | **42.4%** too generous in hit rate |

Against the market's own lines the true joint hit rate is 0.1364 where the product of the two marginals implies 0.1942. A parlay ticket priced off independence therefore *understates* the true price the book is charging — the correlation is not a free lunch for the parlay bettor, it is a second vig. Row-level values are in the table above (`p_a`, `p_b`, `joint_observed`, `joint_independent`, `price_error_pct`).

**The consequence for the competition:** any parlay strategy must be scored on the **correlation-adjusted** joint, not on the legs individually, and the adjustment has to come from a joint history. Ours is one season long, so the SGP rule for now is [S-40](suggestions.html): price the coupling, cap the exposure at one ticket per game, and do not let a parlay strategy promote a tier on a sample this size.

## Player-prop combos: still not measurable

Prop legs need per-player outcomes and a prop-line history. The league publishes neither, and this repository holds no prop archive — so the QB-completion × rushing-try couplings stay blank on the [Correlation](correlation.html) register, and `not published` here too. That is a data-entitlement decision ([Q-02](questions.html)), not a modelling failure.
