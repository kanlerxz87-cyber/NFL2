# Suggestions for Improving Decision Making

Each suggestion is scored on **impact** (how much it changes a decision), **cost**
(what it takes), and **evidence** (what we already know that supports it). Nothing
here is a preference — every row cites the measurement that motivates it.

Status: **ready** (can start now), **blocked** (needs data or a decision), **done**.

---

## Tier 1 — highest impact per unit of effort

### S1. Buy opening-line history before buying anything else — *ready*

*Evidence:* every injury question we cannot answer (A5, A6, B6) fails for the same
reason: we only have closing prices for most seasons. Our QB-change fade loses 8.2%
because we cannot tell whether the market already moved.
*Action:* acquire any archive of pre-week prices, 2015-2026, one book is enough.
*Impact:* unlocks four open questions and turns the availability index from descriptive
into measurable.
*Cost:* low — one licence, one join on `game_id`.

### S2. Stop looking at the 2021-2025 holdout — *ready*

*Evidence:* 22 strategies have now been evaluated on it. Each additional look inflates
the chance of a false positive; the Bonferroni threshold already assumes 60 tests.
*Action:* declare 2026 weeks 10-18 plus 2027 the new holdout, sealed until a strategy
is frozen in writing.
*Impact:* protects the only clean evidence we have. Free.

### S3. Adopt the two-number reporting rule — *done*

*Evidence:* the model is unbiased (−0.19 pts) but 0.31 pts worse than the market. A
site that reported only "ROI +2.4%" would be concealing that.
*Action:* every strategy shows ROI **and** its market-relative MAE. Implemented on the
Leaderboard and Calibration pages.
*Impact:* makes it impossible to mistake luck for skill in the UI itself.

### S4. Publish the "1600 legs" budget — *done*

*Evidence:* at 1,200 legs a genuine 55% edge still has a Wilson lower bound below
break-even; at 1,600 it clears. That is the honest sample requirement.
*Action:* stated on the Open Questions page and in the leaderboard rules.
*Impact:* stops anyone funding a 40-leg "system".

## Tier 2 — improves the product

### S5. Add EPA/play-by-play as a second model family — *blocked*

*Evidence:* our two independent model families correlate **0.976**. Blending them buys
0.01 pts of MAE. Diversification needs a different *input*, not a different formula.
*Action:* ingest nflfastR play-by-play, build EPA/play ratings, re-run the blend test.
*Impact:* the only realistic route to closing the 0.31-pt gap.

### S6. Turn the vacancy index into a live availability score — *blocked*

*Evidence:* 45 "thin" position-weeks in 2024 where a starter was Out with no depth-2
body available. That is a concrete, checkable signal — but it stops at 2024.
*Action:* extend depth-chart coverage to 2025-2026, then score each team's *current*
week before kickoff.
*Impact:* makes the injury page decision-relevant instead of archival.

### S7. Price parlays from measured correlation, not from the legs — *done*

*Evidence:* spread+total φ=+0.019 (independent, good parlay) vs spread+ML φ=+0.669 (one
bet twice). The book prices both at −110/−110.
*Action:* the Parlays page computes the fair price from the measured joint probability
and shows the 10.4% error on the correlated pair.
*Impact:* the single most exploitable structural fact in the data.

### S8. Separate "public research" from "funded strategies" in the UI — *done*

*Evidence:* zero of 22 passed. A single leaderboard with no separation invites readers
to assume the top ROI is fundable.
*Action:* three tiers (funded / paper / rejected), with the tier rule stated on the page.
*Impact:* prevents the most likely misreading of the site.

## Tier 3 — worth doing when the above are in place

### S9. Add a "what changed this week" diff — *ready*

Compare this build with the previous one and show only the deltas: new injuries, line
moves, rating shifts. Decision-making degrades when 3,000 rows change at once.
*Cost:* low — the pipeline already stamps every artefact.

### S10. Backtest against the price actually available, not just the close — *blocked*

Closing lines are the fairest benchmark but nobody bets the close. Adding best-price
(or even a fixed 30-minutes-before number) would give a realistic ROI.
*Blocked on:* the same data as S1.

### S11. Model the totals market separately — *ready*

*Evidence:* total correlation with the result is only 0.19 for the model and 0.30 for
the market, both far below the spread's 0.38-0.44. Totals are the weaker half and
deserve their own feature set (pace, weather, red-zone efficiency), not the
points-for/points-against residual.
*Impact:* plausible 0.3-0.5 pt of total MAE, which is the whole gap.

### S12. Add a licence review before any commercial use — *ready*

*Evidence:* `leesharpe/nfldata` ships no LICENSE file; data originates with Pro Football
Reference and nflverse.
*Action:* written position on redistribution before the site is used commercially.

---

## Anti-suggestions — things deliberately NOT done

| Tempting idea | Why it was rejected |
|---|---|
| Publish prop-correlation numbers by estimating them from intuition | Would be fabrication. Published as UNVERIFIED instead, with the data that would fix it. |
| Tune thresholds until something passes | That is how a lucky streak becomes a "system". Dev/holdout split plus Bonferroni exists to prevent exactly this. |
| Report the best backtest ROI on the landing page | Cherry-picking. The landing page reports the *market gap* and the certification count. |
| Fill the post-2018 backup-deficiency cells with an estimate | The brief says never infer. Those cells are blank and the reason is on the page. |
| Add a "confidence score" that is not calibrated | Every published probability is checked against its observed frequency on the Calibration page. |

---

## Suggested decision path

The site's *Suggestions* page renders this as a reviewable list, so a decision can be
made before implementation rather than after.

1. **Read** Executive Summary §2 (the market gap). Decide whether a 0.31-pt model is
   acceptable as a research baseline.
2. **Review** Flagged for Review. Nothing there blocks anything, but S1 depends on the
   data gaps listed.
3. **Decide** on S2 (reserve a new holdout) — the only irreversible item, and it costs
   nothing today.
4. **Decide** on S1 (opening lines) — the highest-leverage purchase.
5. **Defer** S5, S6, S10 until S1 lands, because they all need the same data.
6. **Never** fund a strategy that has not cleared all seven gates, regardless of ROI.
