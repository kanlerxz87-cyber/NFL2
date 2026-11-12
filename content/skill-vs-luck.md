# Removing Luck
> The protocol for separating skill from variance — with the sample sizes computed rather than asserted, and an explicit statement of what cannot be concluded from any small sample, including ours.

The brief asks to remove luck and to build strategies that are *selectively* skill-based. Two things follow mechanically. First, profit is not evidence: at a genuine 55% win rate on −110 bets, the probability of being ahead after 100 bets is only about 63%. Second, accuracy is not evidence either — a strategy that bets every game at 53% is just a slightly expensive habit. So the protocol measures *price quality* and *restraint*, not P&L.

{{csv data/computed_luck.csv;;cols=bets:Bets placed,prob_ahead_53:p(ahead) at 53%,prob_ahead_55:p(ahead) at 55%,prob_ahead_57:p(ahead) at 57%,prob_ahead_60:p(ahead) at 60%,read:Read;;source=S-CALC;;caption=Normal approximation, one unit to win 0.909 per bet, i.i.d. legs — the independence assumption is generous to the small-sample end and is why parlay tickets are counted as one bet, not as n.}}

## The sample-size arithmetic behind the gates

{{csv data/computed_sample_sizes.csv;;cols=case:Case,p_true:Win prob,ev_per_bet_units:EV per bet (u),sd_units:SD (u),n_95pct_confidence:n for 95% one-sided,n_95pct_80pct_power:n for 95% with 80% power,bets_to_75pct_surely_ahead:n to be 75% likely up,weeks_to_power_target_15_per_week:weeks at 15 bets/week,read:Read;;source=S-CALC;;caption=n = (z·SD / EV)² with the numbers above; 15 bets per week is a deliberately optimistic throughput assumption. The row that matters is 53%: a thin edge is not merely unproven at n = 200, it is unprovable inside a season.}}

Gate G-08 (n ≥ 400) and G-09 (n ≥ 1,000) sit on this table on purpose: at a 57% true win rate 400 bets is comfortably conclusive, and at 55% a thousand bets is where an edge stops looking like luck. Neither is a large sample by the standards of the 53% row — which is the argument for the *other* metric below, not an argument to relax the gate.

## The four instruments

| Instrument | What it measures | Why it survives luck |
| --- | --- | --- |
| **Closing line value (CLV)** | the difference between our price and the settled consensus close, in points or in implied probability | it is independent of the game's result; a lucky week cannot manufacture it and an unlucky one cannot erase it |
| **Bootstrap on realised ROI** | the resampled distribution of mean units per 100, tickets resampled whole (a parlay is one draw) | makes no normality assumption and exposes fat tails that a t-statistic hides |
| **Split-half stability** | re-fit on odd weeks, evaluate on even, and swap | a strategy whose sign flips between halves has been fitted to noise, and this is the cheapest way to catch it |
| **Luck-adjusted P&L** | results re-priced at our own fair value instead of at the outcome | shows what the process earned with the variance removed, and how much of the reported P&L was coin-flip |

## Selectivity, because "right often" is not the goal

```
precision = fraction of bets taken that win, measured against the no-vig benchmark
coverage  = fraction of available bets the strategy chose to take
value per bet taken = mean CLV, in points per side
```

A strategy with high precision and 100% coverage is a market-echo model; one with 5% coverage and strong CLV is a real filter. Coverage is therefore reported *next to* precision on every entry, and a rising coverage with a flat CLV is treated as evidence of decay, not of growth. The rejection log is a first-class artefact: every game the model declined is stored with the residual it declined on, so the counterfactual can be audited after the fact.

## What falsifies us

| Test | Kill condition |
| --- | --- |
| Do-nothing control (ST-12) | a strategy whose after-vig result is indistinguishable from never betting is not promoted, however good its hit rate |
| Public-news echo control (ST-13) | a strategy that cannot beat betting the headline direction is not information, it is latency |
| CLV sign test (G-12) | if the 95% interval on mean CLV includes zero at n ≥ 1,000, the entry is retired, not re-tuned |
| Split-half (G-10) | opposite signs in the two halves ⇒ the fit is noise |
| Post-promotion decay | CLV that is positive in-sample and flat or negative over the following 500 bets ⇒ demotion and clawback of staking |

## The discipline this page exists to enforce

- Pre-register the spec and the planned n before the first tracked bet; no rule edits inside a measurement window (G-11).
- Backtests never appear on the leaderboard. They live on a research page, labelled as research, and they may inform a decision but not a ranking.
- One bet is one ticket. Correlated tickets are netted to an exposure before any count is used in a significance calculation, or the sample size becomes a fiction.
- No number on this site will be described as an edge until the interval excludes zero. Until then the correct description is "under observation", which is what every strategy row on the [leaderboard](leaderboard.html) currently says.
