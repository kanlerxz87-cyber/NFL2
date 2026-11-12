# Build Plan & Roadmap
> The order of work after the decisions are made — written so that no step depends on a number the previous step cannot produce.

Every stage below is a specification with acceptance criteria. Nothing is scheduled here that assumes market data we do not yet have, and no stage is allowed to publish a performance number before stage 5.

## Stage 0 — already in this build

| Artefact | State | Acceptance evidence |
| --- | --- | --- |
| Verified Week 10 dataset (254 + 227 + 32 + 14 rows) | done | per-row sources; standings reconciled to the unit |
| Requirement, question, suggestion, flag registers | done | 40 / {{metric questions}} / {{metric suggestions}} / {{metric flags}} rows |
| Parallel-session integration (game log imported, standings cross-checked, their build archived) | done | 136 rows re-audited; {{metric games_log_reconciled}} of 32 clubs reconcile; two new flags published |
| Site generator with source enforcement and field-count strictness | done | build fails on an unsourced row — demonstrated during this session |
| GitHub Pages deployment from `main` | done | site reachable at the published URL |

## Stage 1 — trust the join (no new data needed)

1. **32-team roster sweep**, one page per club, status vocabulary enumerated from the data rather than assumed (closes FL-14, feeds S-15). Acceptance: 32 × 1 roster files, each with fetch time and source id; the set of status codes observed is written into the data dictionary.
2. **Stable athlete keys.** Adopt the numeric id, keep the URL slug for display only, and assert one-row-per-player-per-game across every table (closes Q-22, FL-15). Acceptance: zero unresolved ids in `verify.py` (gate G-02).
3. **Event store.** Every fact carries `observed_at` and `published_at`; a snapshot rebuild must reproduce exactly (gate G-03). Acceptance: replay of Week 10 from stored events produces byte-identical inputs.

## Stage 2 — the availability graph (the differentiator)

4. Model each club-week as *roster status → practice participation → designation → projected available → actual active → snaps*. Acceptance: for Week 10, all 14 games reconstruct to a stated projected starter and actual starter for QB, with the "who is missing and what replaced them" answer derived rather than hand-written.
5. **Deficiency index by unit** — base front, base back, nickel, goal-line, short-yardage — computed from the participation and designation facts, with the *effect* columns left blank until playing-time data exists (S-07). Acceptance: index published for all 32 clubs; effect columns visibly not published, and the reason is a flag link.
6. **Late-designation capture.** Store all three filings per week; publish the delta per player (unblocks SIG-01, SIG-02).

## Stage 3 — prices and the fair-value spine

7. Ingest opening and closing prices for spread, total, ML plus game props, with quote timestamps and the venue of the quote; build the consensus close as the median of at least three quotes with dispersion stored (S-09, closes the input side of Q-01).
8. Strip vig into no-vig probabilities, publish the vig distribution per market (Q-09). Acceptance: for every market, the sum of the two sides' implied probabilities and the median overround are reported.
9. **Origination card** published weekly (S-22): our number, the consensus, the residual — with any column that cannot yet be computed printed as not published and the blocking gate named.

## Stage 4 — correlation, parlays and prop combos

10. Joint-outcome table from settled legs; publish fitted ρ with intervals per pair class in `data/correlation.csv`, replacing "not published" only where the fit exists (Q-12).
11. Structural priors for volume-conservation pairs (S-11), validated against the operator's own same-game pricing gap versus the independence baseline (C-03, C-04).
12. Parlay pricing through our own joint distribution, never by multiplying leg prices; a parlay is only bettable when its price beats the joint estimate (SIG-14, gate G-05).

## Stage 5 — competition, gates, rewards

13. Register every strategy with a spec hash before its first tracked bet (S-04, gate G-11); open the forward ledger (gate G-08 at 400 bets, G-09 at 1,000).
14. Publish the luck-removal panel weekly (S-18): mean CLV with interval, bootstrap p-value, split-half agreement, luck-adjusted P&L.
15. Award tiers by the rules on the [leaderboard page](leaderboard.html), with the do-nothing and public-news-echo controls reported next to every entry — a strategy that cannot beat ST-13 has not demonstrated information, only enthusiasm.

## Explicitly out of scope until the data exists

Live and in-play pricing; futures; team-total alternates beyond the ST-11 experiment; anything requiring a bettor-behaviour assumption; any auto-betting execution; and any public claim of an edge. Each of these is gated behind stage 3 or 4, and staging them earlier is the fastest known way to produce a confident, wrong number.
