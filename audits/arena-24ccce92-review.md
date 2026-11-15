# Integrated decision-support audit — 2026-11-15

## Scope

Independent reproducibility/build review of the integrated repository at the current branch base. This is a software/data-integrity audit, not a fresh NFL-source transcription. It adds no NFL statistics and does not upgrade any existing value to verified. The source register and per-row citations remain the authority for factual review.

## Reproducible results

| Check | Result |
|---|---|
| `python3 tools/build_site.py` | Pass; 36 canonical pages generated; unavailable values render as “not published”. |
| `python3 tools/verify.py` | 178 passed, 1 warning, 0 failures. |
| `python3 tools/check_site.py` | 11 passed, 1 warning, 0 failures. |
| `python3 scripts/audit_all_pages.py` | 110 HTML pages, 44 JSON files, 319 tables, 7,937 rows; row citations complete; no broken links or column mismatches. |
| `git diff --check` | Pass. |

The warning from `verify.py` is the duplicate question IDs Q-46/Q-47, already published as FL-54. The warning from `check_site.py` identifies non-league links on registry/research pages (including official club pages that label their charts unofficial, and research references); no non-league link was treated as official NFL evidence by this review.

## Decision-relevant blockers confirmed by repository checks

These are existing project state, not newly measured NFL claims:

1. **No market-relative validation for the originated Week 10 lines.** The verifier explicitly reports that no market-relative column exists. The line output therefore cannot establish residual/CLV or demonstrate origination skill.
2. **Leaderboard remains ineligible for ranking.** The verifier confirms no fabricated results: performance cells remain blank or zero-by-definition. The market/settlement and prospective evidence needed for competition rewards are not present.
3. **Measured correlation scope is narrow.** Two by-construction correlations are shown as 1.00; the independently reproducible game-log correlations are C-07 and C-08 with n=136. This is not a player-prop or parlay joint-probability validation set.
4. **Availability and depth are incomplete.** The current fixture-linked injury file covers 24/28 clubs (BAL, CIN, LAC, SEA absent); a separate 2026-11-15 re-read has only 44 rows for four clubs and 13 differences flagged. Existing checks also identify Houston as having no charted depth rows. These are not a complete, immutable 32-club point-in-time availability/depth dataset.
5. **Results corpus is bounded.** The verified corpus contains 136 completed Weeks 1–9 games at the recorded snapshot, with one Week 10 result in a separate file. It is not evidence of multi-season train/validation/holdout performance.
6. **Official game-book sourcing and rights remain gated.** The verifier says the gamebook rights gate remains blocked on Q-50 / FL-55; actual starters, game-day statuses, and snap counts must not be inferred from depth order.
7. **Snapshot history is not equivalent to automated immutable capture.** The validation checks distinguish saved dated reads and their deltas, but this audit found no evidence that scheduled, durable external capture and alerting are running. Do not treat a local snapshot history as an operational capture service.
8. **Questionable reliability is not empirically established.** The existing report vocabulary and small number of designation rows do not validate designation-to-play probabilities. No fixed injury penalty should be used as a substitute.

## Recommended order of work

1. Keep the current site in analysis/shadow mode; do not rank or reward strategies on ROI/win rate.
2. Resolve the price-data policy and acquire a lawful, timestamped opening/closing market feed; preserve raw source hashes, event identifiers, market definitions, and missing/void/push rules. Only then publish fair-line residuals and CLV.
3. Resolve access/rights and source coverage for official Game Books, active/inactive lists, and snap counts. Validate source coverage club- and game-by-game before using replacement depth as a feature.
4. Establish durable point-in-time snapshots for official injury reports, roster/IR transactions, club depth pages, and inactive evidence. Store timestamps, hashes, conflicts, and source URLs; monitor staleness/schema changes.
5. Freeze simple singles-only strategies before evaluation windows; use chronological season splits and prospective grading. Keep controls (random and favorites-only), proper scores, uncertainty, multiplicity correction, and separate staking diagnostics.
6. Gate parlays and player-prop combos until settlement policies and directly validated joint probabilities exist. Marginal multiplication alone is insufficient.
7. Promote injury/personnel features only after paired chronological ablations against the same baseline, with confidence intervals and demonstrated data coverage.

## Official-source links already registered for manual review

- NFL injury hub: https://www.nfl.com/injuries/
- NFL schedules: https://www.nfl.com/schedules/2026/by-week/week-10
- NFL game centre: https://www.nfl.com/games/
- NFL operations / rules: https://operations.nfl.com/

These links are navigation starting points, not proof that every current value was re-read in this audit. Use the dated source rows and flags in `data/sources.csv` and `data/flags.csv` for what the repository actually captured and verified. No missing official value has been filled in by inference.

## Irregularities for review

- Existing duplicate question identifiers Q-46 and Q-47 (FL-54).
- Official-source re-read findings and mismatches are already individually flagged (including FL-73/FL-74); this audit did not re-transcribe those rows.
- Price/prop access, game-book rights, complete immutable snapshots, missing-club coverage, Houston depth, and incomplete forward results remain blockers rather than presumed capabilities.
- Suggestions and readiness gates are project proposals, not official NFL findings. The `suggestions` and `requirements` registers should remain reviewable and should not be presented as verified league facts.
