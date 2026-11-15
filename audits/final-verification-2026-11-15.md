# NFL2 final integration verification — 15 November 2026

## Executive result

The repository already contains the requested public dashboard, registers, model/competition design, and several independently built research trees. I ran the available local build and audit suites without changing their source datasets. The primary build is reproducible; the audited pages and data have no broken internal links or row-source failures in the checks that cover them. This is **not** a claim that the model is validated or that every source is current.

**Decision status: research/paper only. No strategy is cleared for real-money use.** In particular, no opening/closing market-price history is sufficient for CLV or ROI validation, no player-prop price archive supports prop correlations, and the current lineup/depth evidence is incomplete. The competition's own Week 5–9 holdout reported both originated spread and total worse than their do-nothing baselines; see the frozen scoring output and [FL-72](../flagged-for-review.html).

- Public dashboard: [NFL2 on GitHub Pages](https://kanlerxz87-cyber.github.io/NFL2/)
- Decision-first summary: [Executive Summary](../executive-summary.html)
- Findings and irregularities: [Flagged for Review](../flagged-for-review.html)
- Full requirement status: [Requirements](../requirements.html)
- Questions and proposed decision paths: [Open Questions](../questions.html) · [Suggestions](../suggestions.html) · [Suggestion Review](../suggestion-review.html)

## Verification run

Commands were run against the active branch at base commit `1eaf7f74c44a94b9113f36fd4dbd0f24a1bdc58f` on 15 November 2026. The generators were allowed to run, and their generated-date-only changes were restored; no dataset values or generated pages were changed for this report.

| Check | Result | Scope / caveat |
|---|---:|---|
| `python tools/build_site.py` | PASS — 36 canonical pages built; 3,693 blank cells rendered as “not published” | Root site generator |
| `python tools/verify.py` | PASS — 174 checks, 0 failures; 1 warning | Warning: duplicate question IDs Q-46/Q-47, already disclosed as FL-54 |
| `python tools/check_site.py` | PASS — 11 checks, 0 failures; 1 warning | Warning: listed research/registry links use non-league hosts; all measured-data rows still pass the official-source check |
| `python scripts/audit_all_pages.py` | PASS — 110 HTML pages, 44 JSON files, 317 tables, 7,839 table rows; 100% row-sourced; 0 broken links / column mismatches | This auditor's stated coverage |
| `python scripts/verify_site.py` | PASS — 13/13 checks | Review-site tree; 58 factual tables source-linked, 11 explanation-only tables explicitly exempt |
| `python scripts/verify_q51.py` | PASS — 155/155 rows have a canonical/official source | Q51 evidence dashboard |
| `python scripts/verify_s53126614.py` | PASS — 9 JSON datasets, 10 pages; 262 table rows; no broken links | S53 tree and repository-link scan |
| `python tools/s2268_verify.py` | PASS — 1,015 checks, 0 errors | Re-ran root, review, data, source, reproducibility, and link checks; includes its own narrower audit counts |
| `python -m unittest discover -s tests/q51 -v` | PASS — 36 tests | Collector, pricing, scoring, leakage, validation and statistical tests |
| `python tools/review_verify.py` | PASS — 423 rows source-linked; 0 broken links | Review tree |
| `python engine/verify_repo_and_site.py` | PASS — 326 portal rows source-linked; 0 broken links | Portal tree; manifest says its source snapshot is as of 12 Nov 2026 |
| `git diff --check` | PASS | No whitespace errors in the resulting change |

These are repository checks, not a fresh independent re-transcription of every historical source row. Each tree keeps its own stated coverage and snapshot date; their page counts differ because their scopes differ.

## Requirements that are present, and blockers that remain

| Area | Current evidence in this repository | Decision gate / missing evidence |
|---|---|---|
| Landing page, category pages, executive summary, open questions, suggestions, and flagged-review section | Root site has 36 generated pages; requirement, question, suggestion, and flag registers are generated from tracked data | Public site deployment is on `main`; this branch's report is not published until its PR merges |
| Fair-line origination | Dated model outputs and walk-forward scoring artifacts exist; output rows include model inputs and fair lines | The scored spread and total did not beat their holdout baselines; do not promote or stake them |
| Competition and proper-score controls | Pre-registration, gates, leaderboard divisions, benchmark and uncertainty methods, and luck analysis are published | No strategy is validated for live betting; the live leaderboard is not evidence of skill absent price and prospective settlement data |
| Market prices and vig-free consensus | A price-archive register and methodology are present | Q-01/Q-02 remain open: a licensed, timestamped opening/closing price feed and prop-price archive are needed for CLV, vig-free market comparisons, ROI, and prop correlations |
| Correlations | Only reproducible correlations from available sourced game results are reported; unsupported prop correlations remain blank | More game-level/player-level samples and rights-cleared official data are needed; blank means unavailable, not zero |
| Injury and availability | Immutable dated files, explicit blank/absent semantics, and deltas exist for selected reads | Coverage is not a complete daily all-32 point-in-time series. Q-51 remains open for full row-level, dated retention and a state for players removed from a report |
| Depth, replacement certainty, actual starters and snaps | Club depth pages and official gamebooks are documented; source limitations are flagged | `R-20`, `R-21`, and `R-44` remain partial; Q-05/Q-49/Q-50/Q-60 block trusted full-coverage depth features. Gamebook reuse rights and verified snap counts are unresolved |
| Safety and provenance | Blank values remain blank; strict source checks pass; known irregularities are published | Design rows cannot literally cite an official NFL fact source; requirement R-33 explicitly records this limitation |

The controlling registers are [data/requirements.csv](../data/requirements.csv), [data/questions.csv](../data/questions.csv), [data/gates.csv](../data/gates.csv), [data/flags.csv](../data/flags.csv), and [data/suggestions.csv](../data/suggestions.csv). They remain the source of truth where this summary and an older page differ.

## Freshness item for human review

On 15 November I opened the [official NFL injury report](https://www.nfl.com/injuries/?week=11). The returned page identifies itself as the 2026 report and shows Sunday, November 15 Week 10 game sections, while its page title/navigation labels the displayed report Week 10 despite the `week=11` query parameter. The repository's latest full Week 10 injury-hub capture is dated 13 November (`data/s745_injury_refresh.csv` and related snapshot files). I did **not** transcribe or hash the full 15 November page in this audit, so I cannot quantify the exact row-level delta or assert that every current designation is represented locally.

**Action:** treat the saved Week 10 availability as stale for decisions; capture the full official page with timestamp and raw hash, compare row-by-row, preserve both versions, and publish conflicts/deltas before any Week 10/11 availability feature is used. The query/page-label mismatch and lack of a retained 15 November capture are not silently resolved here. Do not substitute a web-search excerpt for a source snapshot.

Other open irregularities include the duplicate Q-46/Q-47 IDs (FL-54), the game-id collisions and snapshot inconsistencies (FL-64–66), unofficial club depth-chart status and player/position conflicts (FL-67–68), absent prop prices (FL-69), and failed originated-line holdout (FL-72). See the linked review page for source references and the existing disposition.

## Official sources for manual review

- [NFL injury report](https://www.nfl.com/injuries/) — selected report, designations and practice status; page selection and capture time must be retained with every snapshot.
- [NFL Week 10 schedule](https://www.nfl.com/schedules/2026/by-week/week-10) — official fixture identity and schedule facts.
- [NFL Week 9 scores](https://www.nfl.com/scores/2026/week-9) — official game results referenced by the frozen holdout analysis.
- [NFL Game Books](https://www.nfl.com/games/) — official game-centre entry point; each collected PDF needs its own game-centre source URL and rights review before bulk retention or reuse.
- [Operations: NFL rules and policies](https://operations.nfl.com/) — official rules/policy starting point; not a substitute for the unresolved Game Book rights decision.

The detailed row-level citations are in the published data tables and source register; the links above are review entry points, not a blanket assertion that every displayed row was freshly rechecked on 15 November.
