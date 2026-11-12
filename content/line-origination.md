# Originate Our Own Lines
> The architecture for setting a price rather than reacting to one — and an explicit list of what must exist before any column in it stops being blank.

To originate means: we produce a distribution over scoring outcomes for each game, convert it into prices for every market we cover, and treat the market as a *check* on us rather than as our answer. A model that consumes the market's line and agrees with it is not originating, and it cannot earn: the whole of its edge would be the vig it pays. So the deliverable of this section is a number, a timestamp, and a residual against the market — published even when the residual is negative.

## The pipeline, and exactly what each stage needs

| # | Stage | Input | Output | State today |
| --- | --- | --- | --- | --- |
| 1 | Team baseline strength | season-to-date scoring, reconciled standings | two efficiency ratings on a points scale | inputs exist ([standings](league-data.html)); estimator unwritten |
| 2 | Rest, travel and venue context | official kickoff times and venue cities | an additive adjustment, prior pinned at zero | buildable now from `data/schedule_2026_wk10.csv` |
| 3 | Availability state | roster status, practice participation, designations, IR and return designations | a probability distribution over lineups, per club per game | half-built: [254 rows](injuries.html) held, one filing not three ([FL-09](flagged-for-review.html)) |
| 4 | Unit-level deficiency | stage 3 plus position groups | separate adjustments for base front, base back, nickel, goal-line, short-yardage | blocked — no official depth chart, no snaps ([FL-06](flagged-for-review.html)) |
| 5 | Game scoring process | stages 1–4 | joint distribution of the two team scores | unwritten by choice: it would be unvalidateable without prices |
| 6 | Player production process | stage 5 conditioned on play counts | distributions for each prop we price | blocked on Q-02 |
| 7 | Market conversion | any distribution | spread, total, ML, team totals, props — each with a no-vig target and a price to quote | needs a vig convention (Q-09) |
| 8 | Residual publication | stage 7 vs the consensus benchmark | our number, the market, the difference, and a verdict | needs prices (Q-01) — the single largest gap in the project |

## Where the injury work actually enters the line

This is the design decision that makes the availability data worth having. Do not subtract a fixed penalty for a missing starter. Instead enumerate the lineup states the club could field, price each state, and mix:

```
P(outcome) = Σ_over lineup states  P(state | roster, practice, designations) × P(outcome | state)
```

The weights come from what we already ingest — a player who did not practise all week and has no designation is a different mixture than one who was limited Wednesday and full Friday. The payoff is that uncertainty itself becomes priced: two clubs can both be "missing a starting left tackle" and generate different lines, because one of them has a replacement with 900 prior snaps and the other has a practice-squad elevation.

**Illustrative shape, not a fitted value.** With two states — starter plays (weight *w*) and replacement plays (weight 1−*w*) — a market price is the weighted average of two conditional prices. Setting *w* to 0.60 or 0.20 moves the total roughly in proportion to the gap between the two conditional prices. Those two numbers are ours to estimate and no one else's; the *formula* is not a claim about any game on this site's schedule page. The reason this is stated so bluntly: a model whose weights are guesses dressed as measurements is the failure mode of exactly this project type.

## Fair value and the vig convention

1. Take the consensus benchmark as a probability pair, remove the overround proportionally, and treat the result as the market's belief — never as truth.
2. Our edge on a side is `p_ours − p_no_vig`, in points, and the vig we must beat is documented on the [bet-types page](bet-types.html) (4.55% on a −110/−110 pair, by arithmetic).
3. We only quote, and only bet, when the residual exceeds the vig **and** k times our own model error. The second condition is what stops a 1% apparent edge on a model with a 4% error bar from being called an edge at all.
4. Every quote is timestamped against a fixed decision clock so the residual can be attributed to a moment rather than to a mood.

## The origination card (what the site will show)

| Column | Currently | Becomes real when |
| --- | --- | --- |
| Our number per market | not published | stage 5 exists |
| Consensus benchmark and its dispersion | not published | a price feed (Q-01) |
| Residual in points, and as a share of vig | not published | both of the above |
| Mixture weights over lineup states | not published | point-in-time availability history |
| Model error bar on our own number | not published | bootstrap over a validation set |
| Gate verdict for the row | computed on [validation gates](validation-gates.html) | now |

## Discipline that keeps this honest

- **We publish our residuals whether or not they flatter us**, including a running count of times the market moved away from us after we quoted.
- **Two control entries stay in the registry forever**: the do-nothing strategy and the follow-the-headline strategy. If a signal cannot beat the second one, it has not demonstrated information — it has demonstrated that we read the news at the same time as everyone else.
- **No stage may borrow from the next.** A scoring process fitted to market prices is a market-echo model wearing a costume, and gate G-11 (pre-registration) exists to stop it happening by accident.
- **Half-point economy caveat**: we treat line movement in quarter-point units internally and never describe a 0.25 shift as if it were 0.25 of *value*; the value of a number depends on the distribution's slope there, which is stage 5's output, not an assumption.
