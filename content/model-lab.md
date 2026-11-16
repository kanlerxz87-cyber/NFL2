# Fair-Line Origination Lab
> A model that originates our own spread and total, fitted only on data this repository transcribed from nfl.com, evaluated week by week as it would have been evaluated in real time — and then compared against the two things it has to beat.

Everything on this page is **computed in this repository, from the 136 completed 2026 games in [the verified game log](league-data.html)**. It is not a specification: the numbers below came out of a script (`scripts/origination_lab.py`) that anyone can re-run. It is not a claim of edge. **Legacy-diagnostic notice:** the archived-price comparisons below are exploratory and unvalidated because the archive does not document its 2026 quote vintage; under [P-PRICE-01](https://github.com/kanlerxz87-cyber/NFL2/blob/main/docs/PRICE-DATA-POLICY.md) they are excluded from the leaderboard and cannot be used for strategy selection or promotion. Only the outcome-based research is described here as a diagnostic, not a validated strategy.

{{csv data/model_verdict_2026_a392.csv;;cols=metric:Metric,value:Value,method:How it is computed,read:Read;;source_col=source;;caption=The four numbers a decision turns on. "MAE" is mean absolute error in points against the final score, so a smaller number is a better line; a push is impossible because every published line is rounded to a half point.}}

## What was built

Two ridge-regularised regressions over the same game set, fitted on weeks before the week being predicted:

```
margin  (home - away) = net_rating(home) - net_rating(away) + hfa        [hfa unpenalised, zero at neutral sites]
total   (home + away) = league_mean + pace(home) + pace(away)             [pace is a deviation, shrunk to zero]
```

`λ` is chosen from {5, 20, 60} by walk-forward spread error, not by fitting the whole season — the selection table is in the verdict above, and the three settings differ by less than the sampling noise, which is itself the finding. Weeks 1–3 are used only for training, so the first evaluated week is week 4 and the last is week 9; **no game is ever predicted with information from a later game**.

## The three-way comparison, and why the paired row is the one to read

| Predictor | What it is | Spread MAE |
| --- | --- | --- |
| Do-nothing baseline | the league-average home margin; no team information at all | 10.455 |
| **Our model** | ratings above, refitted every week | **9.278** |
| Archived price | the line carried by the community archive this repo vendored | 8.983 |

Reading those three numbers side by side is almost the right test, and it is not quite: the archive row only has a price for 88 of the 136 games, so the model's MAE and the price's MAE are computed on *different slates*. That is why the verdict publishes a **paired** comparison — the same games, both predictors, bootstrap interval on the difference:

- **spreads: +0.295 pts worse than the archived price, 95% CI −0.409 to +1.011.** The interval spans zero. With one season of data we cannot say our line is worse than the market's, and we cannot say it is better. That is the honest headline, and it is the reason gate G-08 (n ≥ 400) exists.
- **totals: +0.847 pts worse, 95% CI +0.153 to +1.580.** The interval excludes zero, in the bad direction — and our totals are also marginally worse than the do-nothing league-mean (11.165 vs 11.078). **The pace half of this model currently earns nothing.** Do not publish our total as a line; publish it as a diagnostic until a measured availability feature is attached to it.

## Week 10 slate, originated from weeks 1–9 only

Our line, the archived line where one exists, and the availability load sitting behind it. The availability columns are **counts of who did not practise, split by side of the ball** — they are deliberately *not* folded into the number, because no coefficient has been measured for them yet ([Q-36](questions.html), [S-35](suggestions.html)).

{{csv data/originated_lines_wk10_a392.csv;;cols=game:Game,away:Away,home:Home,our_spread_home_favoured:Our spread (home favoured),our_total:Our total,archive_spread_home_favoured:Archive spread,archive_total:Archive total,spread_gap_vs_archive:Spread gap,total_gap_vs_archive:Total gap,venue_flag:Venue flag,away_dnp_off:AWAY DNP off,away_dnp_def:AWAY DNP def,home_dnp_off:HOME DNP off,home_dnp_def:HOME DNP def,status:Status;;source_col=source;;caption=Positive spread means the home club is favoured by that many points — the same sign convention as the archive column it is compared with. A gap of zero means we and the archived price agree to the half point; gaps of ±3 mean one of us is wrong. "international" is the Munich fixture, where the model applies a domestic home field and flags it, because this season's log carries no separable coefficient for it.}}

## Where the two sources agree about the games themselves

The game log this model is trained on was transcribed from nfl.com game pages by a parallel session; the archive was pulled independently from a third-party dataset. Joining them by club code without an alias table **drops nine games — every Arizona Cardinals game in weeks 1–9** — because the archive writes `ARI` and `LA` where the league writes `AZ` and `LAR`. With the alias applied, all 136 scores agree cell for cell, and nothing disagrees.

{{csv data/code_collision_a392.csv;;cols=join:Join,games_dropped:Games silently dropped,games_joined:Games joined,detail:What that means,fix:The fix;;source_col=source;;caption=Published so the defect is a page on the site rather than a footnote in a commit. See [FL-28](flagged-for-review.html).}}

## What a reader should conclude

1. **This diagnostic does not establish profitability.** The archived price comparison is exploratory only: the quote vintage is undocumented, the sample is one season, and the result is not admitted evidence under P-PRICE-01.
2. **Archived-line gaps are not actionable residuals.** The archive's 2026 price timing is unknown; only an admitted, timestamped, point-in-time market feed can support a valid market-relative residual ([Q-01](questions.html), [price-data policy](https://github.com/kanlerxz87-cyber/NFL2/blob/main/docs/PRICE-DATA-POLICY.md)).
3. **Totals are the weakest leg and availability is the missing input.** The 2026 log has no injury history in it: the injury register starts at week 10, so *no* availability feature can be backtested today. That single gap blocks more of the brief than any modelling choice ([S-35](suggestions.html)).
