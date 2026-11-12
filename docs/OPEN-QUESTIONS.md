# Open Questions — what must be answered before a decision

This is the "questions, information and answers" register. Every row is either
**ANSWERED** (with the evidence and where it came from) or **OPEN** (with the specific
information that would close it, and why it matters). No row is guessed.

Legend: `A` = answered here · `O` = open, needs information we do not have.

---

## A. Model and market

| # | Question | Status | Answer / what is missing |
|---|----------|--------|--------------------------|
| A1 | Is our line better than the closing line? | **A** | No. Spread MAE 10.25 vs 9.94; total 10.87 vs 10.50 over 3,404 games. Source: `site/data/calibration.json`. |
| A2 | Is our line at least unbiased? | **A** | Yes. Spread bias −0.19 pts, total bias −0.02 pts. A silent bias of 1 pt would wipe out every edge we are looking for, so this check is a permanent gate. |
| A3 | Are our probabilities calibrated? | **A** | Mostly. Six probability buckets; the largest error is +8.3 pts in the 0.80-1.00 bucket (n=136), and −4.5 pts in 0.35-0.50 (n=894). See the *Calibration* page. |
| A4 | Could a second model family help? | **A** | Not this one. A net-points-differential model correlates 0.976 with the ridge ratings and improves MAE by only 0.01 at a 3:1 blend. Diversification needs a genuinely different input (e.g. play-by-play EPA), which we do not have here. |
| A5 | Does the market already price injuries? | **O** | We can measure *that* an injury happened and *whether the number moved*, but `games.csv` carries only closing lines for most seasons, not opening lines. Closing the question needs **opening lines at scale** (only 2021 is present, one book, 1,088 rows). |
| A6 | Do backup quarterbacks move the line by a measurable amount? | **O** | We can detect the QB change (12.5% of games) but our favourite is *worse* than the market when we fade it (−8.2% holdout ROI). Distinguishing "market already priced it" from "no effect" needs opening lines (A5). |

## B. Injuries and depth

| # | Question | Status | Answer / what is missing |
|---|----------|--------|--------------------------|
| B1 | Which positions are hurt most? | **A** | By volume: LB 14.3%, WR 13.9%, CB 13.9% of all report entries. By "Out" rate: only TE is distinguishably above the 45.3% pooled rate (52.8%, CI 47.6-57.9%). |
| B2 | How often does a depth-1 starter get ruled out? | **A (2024 only)** | 954 team-position-weeks had at least one starter out; league-wide vacancy rate by team ranges 1.9%-10.9% of starter slots. SF highest (10.85%), CLE second (10.46%). |
| B3 | How often is a team down to a 3rd-string player? | **A (2024 only)** | 45 "thin" position-weeks where a starter was Out **and** no depth-2 body was available. That is the operational definition; it is a floor, not a ceiling, because a player can be active but limited. |
| B4 | Can we get snap counts to confirm who actually played? | **O** | Not from this environment. Snap counts are published only as release assets above the API size limit. Needs either a mirror under 1 MB or direct release-asset access. |
| B5 | Can we extend depth-chart coverage past 2024? | **O** | Needs the nflverse `depth_charts` release for 2025-2026, currently unreachable. |
| B6 | Does a starter being out actually move the line or the total? | **O** | Gated on A5 (opening lines). Without a pre/post price, any claim would be a story. |

## C. Strategies and validation

| # | Question | Status | Answer / what is missing |
|---|----------|--------|--------------------------|
| C1 | Did any strategy pass? | **A** | No. 0 of 22. Closest: S22 moderate-wind under (holdout +10.4% ROI, 180 legs) fails on sample, multiplicity and skill. See *Leaderboard*. |
| C2 | Is the gate set too strict? | **A** | Not for real money. Bonferroni at 60 tests requires p<0.00083; with 180 legs no realistic edge can clear that. The gates are calibrated for *capital allocation*, and the site says so explicitly. |
| C3 | How many legs are needed to certify a 55% hit rate? | **A** | Using the Wilson bound: **between 1,200 and 1,600 legs** — at 1,200 the lower bound is 0.5217 (still below the 0.5238 break-even), at 1,600 it is 0.5255 (clears it). Verified by direct computation, so budget ~1,600 legs per candidate. This is the number that should drive the research plan. |
| C4 | Are we over-fitting the holdout by looking at it? | **O — actively dangerous** | Every additional look at 2021-2025 burns a little of its value. Mitigation: a *new* holdout (2026 weeks 10-18 plus 2027) should be reserved from now on, and this one re-labelled "development". Logged as an open decision. |
| C5 | What is the correct reward currency? | **O** | Points are defined. Cash raises compliance questions (see compliance note). Decision required before any payout design. |

## D. Parlays and props

| # | Question | Status | Answer / what is missing |
|---|----------|--------|--------------------------|
| D1 | Are spread and total legs independent? | **A** | Yes, φ=+0.019 (n=3,289). Combining them is real diversification. |
| D2 | What is the cost of a same-game parlay? | **A** | At −110/leg the book keeps 8.9% on 2 legs, 13.0% on 3, 17.0% on 4, and it compounds. Exact table on the *Parlays* page. |
| D3 | Which prop pairs are correlated? | **O** | Structural signs are known (QB yards ↔ WR yards, +) but magnitudes need prop-line history. Published as UNVERIFIED, never estimated. |
| D4 | Do team scores correlate within a game? | **A** | Essentially not: r = −0.030 across 3,404 games. The "shared pace" story is weaker than commonly assumed, so opposing team-total overs are closer to independent than expected. |
| D5 | Is there a legal/ToS constraint on automated betting? | **O** | Most books prohibit bot-placed wagers; the NFL prohibits its personnel from betting on NFL games and treats prediction-market sports contracts as betting. Needs a written position before any automation. |

## E. Operations

| # | Question | Status | Answer / what is missing |
|---|----------|--------|--------------------------|
| E1 | Is the pipeline reproducible? | **A** | Yes — `python3 -m pipeline.build`, pinned upstream commit, SHA-256 per file in `provenance.json`. |
| E2 | How stale can the site be before it misleads? | **A** | Lines and injuries are the volatile parts. The site stamps `generated_utc` on every page; anything older than one week should be treated as historical. |
| E3 | What breaks if the upstream mirror moves? | **A** | The build fails loudly on hash mismatch (see `pipeline/common.py` UPSTREAM pin). It does not silently produce numbers from a different dataset. |
| E4 | Is a licence in place for redistribution? | **O** | `leesharpe/nfldata` publishes no LICENSE file. Data is aggregated from Pro Football Reference and nflverse. Attribution is given; a formal licence review is required before any commercial use. |

---

## Discovery backlog — the cheapest ways to close the open items

Ordered by how much each one unlocks.

1. **Opening lines at scale** (closes A5, A6, B6, and makes the injury research real).
   Any archive with pre-week prices for 2015-2026, even a single book, unlocks four
   open questions at once.
2. **Prop-line history** (closes D3, C1 for prop strategies). Three seasons with closing
   prices is enough to estimate pair-level φ.
3. **Snap counts** (closes B4). Turns "listed Out" into "actually did not play".
4. **Depth charts 2025-2026** (closes B5, and lets the vacancy index extend to today).
5. **Play-by-play or EPA data** (closes A4 and gives a genuinely independent second
   model family, which is the only realistic route to beating the market MAE).
6. **A reserved new holdout** (closes C4). Free, but has to be decided before the next
   research cycle, not after.
