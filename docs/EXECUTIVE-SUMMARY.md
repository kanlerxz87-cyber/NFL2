# Executive Summary — NFL2 Research & Line-Origination Project

**Generated:** 2026-11-12 · **Data as of:** games through 2026-11-09 (Week 9 complete, Week 10 in progress)
**Upstream commit:** `leesharpe/nfldata@692e5f9` (2026-11-12T03:45Z)

---

## 1. What this project is

A reproducible pipeline that (a) audits a verified NFL dataset, (b) **originates its own
spread, total and moneyline** for every scheduled game, (c) tests 22 candidate betting
strategies through seven hard validation gates on a locked holdout, (d) measures the
correlations needed to price parlays, and (e) tracks injuries and depth-chart
vacancies. Every number on the site is produced by code in this repository from a
hashed source file. Nothing is typed by hand.

## 2. The headline result — stated plainly

**Zero of 22 strategies passed the gates.** This is the correct outcome, not a failure.

| Metric | Our model | Market close | Gap |
|---|---|---|---|
| Spread MAE (3,404 games, 2013-2025) | **10.25 pts** | **9.94 pts** | +0.31 worse |
| Total MAE | **10.87 pts** | **10.50 pts** | +0.37 worse |
| Spread-to-result correlation | 0.379 | 0.439 | −0.060 |

The closing line is a better forecast than this model. Any site claiming otherwise
with these inputs would be selling a story. What the model *is* good for:

* it is **unbiased** (spread bias −0.19 pts, total bias −0.02 pts) where naive models
  drift, and
* it produces a defensible **probability**, so it can tell you when a *price* is wrong
  even when its *line* is not the sharpest.

## 3. What did survive scrutiny

| Finding | Evidence | Status |
|---|---|---|
| **Wind suppresses scoring more than the market prices** | Wind 10-15 mph: under went 194/326 (59.5%, +13.6% ROI) in development and 103/178 (57.2%, +10.4% ROI) in holdout. Market's line sits **1.6 pts high** in that band in development and **0.9 pts high** in holdout. | **Real signal, unproven edge.** Fails G2 (Wilson lower 0.4992 vs break-even 0.5238), G5 (p=0.110 vs 0.00083 required) and G6 (z=1.94 vs 2.0). The band was chosen after looking at results, so selection bias is a live risk. |
| **Indoor games score more than the market prices** | Indoor actual total 47.76 vs market line 46.47 (n=952). | Direction confirmed, but betting the over lost money in both windows (ROI −2.0% dev, −3.2% holdout). Do not bet it. |
| **Spread and total legs are genuinely independent** | φ = +0.019 (n=3,289). | Verified. Combining them in a parlay is real diversification. |
| **Spread and home moneyline are NOT independent** | φ = +0.669 (n=3,320). | Verified. A "spread + ML" same-game parlay is largely one bet, and the book prices the legs independently — a 10.4% overstatement of the fair price. |
| **Injury reports are concentrated in the back seven, but "Out" rates are not** | Linebackers (14.3% of all entries), receivers (13.9%) and cornerbacks (13.9%) dominate the report. However only **tight end** has an "Out" rate distinguishably above the pooled 45.3% (52.8%, 95% CI 47.6-57.9%), and TE is a thin position with only 362 entries. | The volume story is verified; the "some positions get hurt worse" story is **not** supported at this sample size. |

## 4. The single most important number

**ΔMAE = +0.31 points.** Until the model's spread error beats the market's, no
strategy built on it can be certified, because the market is the opponent. The gates
exist so that nobody has to take that on faith.

## 5. Data reality check — what we have and what we do not

| Have (verified) | Do not have (and why it matters) |
|---|---|
| 7,548 games, 6,967 completed regular-season games 1999-2025, with closing spread, total, moneyline, weather, rest, QB identity | **Player-prop line history** — so prop-to-prop correlation is published as UNVERIFIED, never estimated |
| 28,617 player-seasons with games/starts/experience 2006-2018 | **Starts after 2018** — the upstream field is empty, so the backup-deficiency index stops at 2018 |
| Weekly NFL injury reports 2024-2026 (15,008 rows) | **Depth charts for any season except 2024** |
| Full 2024 depth charts (37,312 rows, depth 1/2/3, all 32 clubs) | **Snap counts** — published only as release assets above this environment's size limit |
| Official-note cross-check of the current injury report from nfl.com | **An auditable projection feed for props** |

Every one of those gaps is visible on the Flagged for Review page with the reason
attached. Nothing is filled in, estimated, or inferred.

## 6. Two irregularities found in the source data (both explained, neither hidden)

1. **2022 has 271 regular-season games, not 272.** The Week 17 Bills-Bengals game was
   suspended after Damar Hamlin's cardiac arrest and the NFL announced it would not be
   resumed. Confirmed against ESPN and NFL reporting; the season is complete at 271.
2. **`rosters.csv` reports zero starts for every player from 2019 onward.** The field
   is simply not populated upstream. Seven rows also carry negative experience values
   for two players. Both are logged in the audit and the affected metrics are withheld.

## 7. What to decide, and what is missing before deciding it

The full question register is on the **Open Questions** page. The four that actually
gate a decision:

1. **Do we fund anything now?** No. Zero strategies are certified. The correct action
   is to keep the pipeline running and revisit at 100+ holdout legs per candidate.
2. **Do we buy prop-line history?** It is the only way to move prop combinations from
   UNVERIFIED to measured. Everything else on the prop page is arithmetic.
3. **Do we accept a 0.31-point model gap as a research baseline?** If yes, the value
   is in the *probability* output (finding mispriced prices), not the *line* output.
4. **What is the reward currency?** Points are defined; cash payouts, if any, are a
   compliance question first and a modelling question second — see the legality note.

## 8. Compliance note that constrains the leaderboard design

The NFL's Gambling Policy for Players prohibits betting on NFL games, and the league
has told personnel that **prediction-market sports contracts count as betting**. Any
leaderboard that pays for picks must be a research-and-education artefact for people
**outside** the league, or run on paper only. This is why the reward structure below
is denominated in points and paper allocation rather than money.

## 9. Deliverables

| Artefact | Where |
|---|---|
| Live dashboard, 12 category pages + Flagged for Review | `site/index.html` (GitHub Pages) |
| Reproducible pipeline (`python3 -m pipeline.build`) | `pipeline/` |
| This summary | `docs/EXECUTIVE-SUMMARY.md` |
| Requirements register | `docs/REQUIREMENTS.md` |
| Question/information register | `docs/OPEN-QUESTIONS.md` |
| Verification log with official links | `docs/VERIFICATION.md` |
| Suggestions & decision paths | `docs/SUGGESTIONS.md` |
