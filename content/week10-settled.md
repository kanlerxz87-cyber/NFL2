# Settled Week 10 — the first out-of-sample grade
> One game has finished. Every line this site originated for it can now be scored against the official result. This page is where we find out whether the pipeline produces a number — and, more importantly, whether that number means anything yet.

**Status at 2026-11-13T06:55Z:** 1 of 14 Week 10 games is Final. The Thursday-night fixture, **Washington 24 – NY Giants 21**, is the first result any line on this site has been measured against. The other 13 kick off 15–16 November.

## The result, and the four predictions it settles

{{csv data/settled_wk10_5f16dcc6.csv;;cols=predictor:Predictor,predicted_spread_home:Predicted spread (home),spread_abs_error:Spread error (pts),predicted_total:Predicted total,total_abs_error:Total error (pts),prediction_origin:Where the prediction came from;;source_col=source;;caption=Actual result: WAS 24 at NYG 21, so the home margin was −3 and the total was 45. A spread column holds the predicted HOME margin, so +2.5 means the Giants were favoured by 2.5 at home. Error is absolute, in points, against the official final score. The last row is a predictor that knows nothing about either team — it writes the weeks 1-9 league average every time, and it is the bar the other three have to clear.}}

Read the table in this order:

1. **Our spread lost to knowing nothing.** We published NYG −2.5. The Giants lost by 3. A predictor that wrote `0` every week was off by 3.0; we were off by 5.5. **The model's lean cost 2.5 points** against a baseline with no team information in it.
2. **Our total beat the archive by 4.0 points, and that is not the win it looks like.** We published 45.5 against an actual 45. The archived community price published 40.5. But the league mean total is 45.93 — so the archive was the outlier, not us, and our 45.5 was within half a point of the number anyone could have written down from the standings page.
3. **The simplest model on the site was also the worst on this game.** The points-only fair line (8.0 spread error, 3.0 total error) is dominated by a season average.
4. **Nobody covered the spread.** Every one of the four predictors had the Giants winning; the Giants lost by 3.

## What the arithmetic says

{{csv data/computed_settled_5f16dcc6.csv;;cols=metric:Metric,value:Value,method:How it is computed,read:Read;;source_col=source;;caption=Recomputed on every build by tools/compute_settled_wk10.py from data/games_2026_wk10_played.csv, data/originated_lines_wk10_a392.csv, data/computed_fair_lines.csv and the frozen weeks 1-9 corpus. The null distribution is the 136 verified games; no game outside that corpus is used.}}

## The one finding worth acting on

Our 0.5-point total error looks like the best number on the site. It is the number most likely to be luck, and the register above says why in two lines:

- **This game was unusually average.** Its total landed 0.93 points from the weeks 1-9 league mean. Only **8 of the 136 verified games (5.9%)** are that close to the mean or closer.
- **A naive total predictor lands within 0.5 points of the actual total in 3.7% of games** (5 of 136).

So the game handed every total predictor a near-free shot, and we took it. The right conclusion is not "our total model works" — it is that **a single game carries no information about whether it works**, because the error we are measuring is dominated by how average the game turned out to be, not by what the model knew.

## How much evidence it would actually take

The 136-game log gives a standard deviation of 14.31 points on game totals and 13.27 on home margin. Detecting a **1.0-point** difference in mean absolute error at 80% power and a two-sided 5% level needs:

| Quantity | Games required | What that is |
| --- | --- | --- |
| Totals | **1,607** | about ten NFL seasons |
| Spreads | **1,382** | about nine NFL seasons |

One settled game is **0.07%** of that. Gate G-08 on this site sets n ≥ 400 for any strategy claim; this page is the arithmetic underneath it, measured rather than asserted.

## What this page does not do

- It does not add WAS–NYG to the backtest corpus. That corpus is deliberately frozen — see the note below.
- It does not grade a strategy. No strategy on the [leaderboard](leaderboard.html) has a settled leg, because none was registered before a corpus existed ([S-26](suggestions.html)).
- It does not use the injury or depth data as a feature. The availability columns on the [Week 10 origination table](model-lab.html) are counts, not coefficients, because no availability effect has been measured yet ([Q-36](questions.html)).

## Why the result lives in its own file

`data/games_2026_wk10_played.csv` is append-only and separate from `data/games_2026_wk1_9.csv`.

Suggestion [S-26](suggestions.html) asks for the weeks 1–9 file to be registered as the pre-registered backtest corpus, with its SHA-256 published so that **a later edit invalidates every grade built on it**. Appending week 10 to that file would silently re-baseline in-sample work that was already published against it. So the corpus is left byte-identical and its hash is recorded in the re-verification register at the bottom of this page instead:

```
data/games_2026_wk1_9.csv  sha256  f0dffce05e79b5267318c444eb50ca151390480fbd6c10965290228995fb6f33
```

As the rest of Week 10 settles, rows are appended to the played file only, and this page re-scores itself on the next build.

## What was re-verified to build this page

{{csv data/reverification_5f16dcc6.csv;;cols=check:Check,scope:Scope,official_value:Official value,published_value:What this repo published,result:Result,note:Note;;source_col=source;;caption=Read against the live official pages on 2026-11-13. CORRECTED means the repository held a stale value and this session refreshed it; MISMATCH means a value on the site disagrees with the official page and has been flagged instead of edited (FL-36); NOT CHECKED is stated so the register is never read as a full re-verification.}}
