# Independent final audit — NFL2 decision site

**Audit session:** `fd94fccd` on `arena/fd94fccd-nfl2`  
**Audit date:** 2026-11-12 (UTC)  
**Purpose:** Independent re-run of the existing repository checks and review of the live site/configuration. This is an audit report, not a new model-performance claim.

## Result

The existing implementation covers the requested decision workflow: a landing dashboard and category pages; requirements; open questions; a separately reviewable suggestion register; line-originating methods and signals; singles/parlays/prop-combo design; correlation methodology; skill-vs-luck gates; injury and depth/availability records; strategy leaderboard/rewards; an executive summary; and a Flagged for Review page. These are already present on the live root site. The separate Q51 pages describe their outputs as **paper-only and unvalidated**.

The independent build and local verification commands all exited successfully. The canonical Flagged for Review register now has 23 entries, including FL-22 (corrected provenance statement) and FL-23 (open Pages deployment-mode review). This does **not** mean the proposed strategies have demonstrated skill or that all NFL availability inputs are complete. The project itself correctly leaves those conclusions blocked or unverified.

## Verification performed

| Check | Observed result |
|---|---|
| `python3 tools/build_site.py` | Built 22 root pages; 588 missing cells displayed as “not published”. |
| `python3 tools/verify.py` | 39 checks passed, 0 warnings, 0 failures. Checks include register schemas, standings arithmetic, 254 injury rows, 227 depth events, 136 game rows with per-row NFL game links, and game-log/standings reconciliation. |
| `python3 tools/check_site.py` | 10 checks passed, 0 failures. All 22 pages are generated and navigable; 1,302 links point to NFL.com; internal links/anchors resolve; no blank cells or unresolved template markers. One disclosed warning covers four non-league research/corroboration hosts on `sources.html` plus the GitHub API reference on the review flag page (see findings). |
| `python3 scripts/audit_all_pages.py` | 96 HTML pages, 36 JSON files, 222 tables, 3,425 rows; 0 broken links and 0 column mismatches. The repository auditor reports all table rows sourced under its official/canonical-source rules. |
| `python3 -m unittest discover -s tests/q51 -v` | 36 tests passed. |
| `python3 scripts/verify_q51.py` | 10 Q51 pages; 155/155 rows have an official or canonical source; 130 explicit blanks; 0 errors. |
| `python3 engine/verify_repo_and_site.py` | 326 portal rows have official HTTPS source links; 1,619 repository internal links checked; 0 broken. |
| `python3 scripts/verify_s53126614.py` | 9 JSON datasets, 10 pages, 262 rows, 100% official HTTPS row links; 3,287 internal links/assets checked, 0 broken. |
| GitHub CI on this audit branch | `build-and-audit`, `Verify site data and links`, and `Q51 evidence and engine verification` completed successfully. |
| GitHub Pages API and live page | API reports `built`, legacy source `main` `/`; live root page fetched successfully at https://kanlerxz87-cyber.github.io/NFL2/ . |

The machine-readable source register and row-level audits are in `data/sources.csv`, `data/verification-report.json`, `q51/`, and the scripts listed above. Official manual-review starting points include the [NFL injury hub](https://www.nfl.com/injuries/), [NFL standings](https://www.nfl.com/standings/), [NFL regular-season schedules](https://www.nfl.com/schedules/2026/REG/), and [NFL Football Operations](https://operations.nfl.com/). Where the official source does not expose a needed value, the site flags the gap and leaves the value blank.

## Findings published for review

1. **Landing-page historical attribution was inaccurate.** The old `content/index.md` sentence said, “Everything on this site was therefore created in this session, in one branch.” It has been corrected to say the current site was built across multiple documented sessions and link to `COORDINATION.md`. Flag FL-22 preserves the issue and its provenance for reader review.
2. **Pages publishing configuration merits a deployment-owner check.** The GitHub Pages API reports legacy publication from `main` `/`, while `.github/workflows/pages.yml` uploads the `docs/` tree as an Actions Pages artifact. Both the root and `/docs/` pages currently serve and post-merge deployment checks succeeded, but those descriptions should be reconciled/documented to avoid ambiguity about the canonical tree. Flag FL-23 is published with the GitHub Pages API and workflow source links. No workflow/config file was changed.
3. **Non-league source-registry links are intentionally not primary NFL evidence.** `tools/check_site.py` warns about non-league hosts on `sources.html` (DraftKings Network, Patriots Wire/USA Today, Morgan Stanley, NBER) and now the GitHub Pages API link on `flagged-for-review.html`. The registry classifies the former links as third-party/research/corroboration; the GitHub API is official evidence for GitHub Pages configuration, not NFL facts. None substitutes for official injury, standings, schedule, or game evidence. This warning is non-failing; the page labels them as review/source references.
4. **The original T18 board row was stale.** The >60-minute stale claim was documented and taken over under the board's own rule. T18 has now been completed for this audit's final-site follow-up; it does not alter the already-completed main integration.

## Decision/product limits that remain explicit

- No trustworthy, timestamped, book-identified 2026 archive of spreads, totals, moneylines, and prop prices was found in the audited evidence; without that, no current-season closing-line value or validated betting edge is established.
- The Q51 independent engine's README reports its spread and total forecast errors worse than the closing-line benchmark and **zero strategies certified**. Treat all current lines and correlations as exploratory/paper-only, not as proof of skill.
- The root correlation register does not assert fitted rho values; the Q51 measured descriptive correlations are tied to their stated sample and are not automatically a causal or predictive estimate.
- Injury/practice data are point-in-time snapshots with incomplete published designations. The root flags report that only 6 of 254 rows had game-status values in the captured Week 10 snapshot. The official NFL hub is the source of record: https://www.nfl.com/injuries/ . Do not treat missing rows/fields as “healthy.”
- The official depth-chart evidence needed to label second-/third-/fourth-string replacements is incomplete; the project flags the gap rather than infer ranks. NFL news and injury evidence cited in the register include https://www.nfl.com/news/nfl-week-10-injury-report-2026-season and https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11 .

## Publication record

- Audit PR: [#25](https://github.com/kanlerxz87-cyber/NFL2/pull/25), merged 2026-11-12T22:25:38Z as `d2c0af0e7c2008ba4b64a7c1dcd03c44a6b4293e`.
- Post-merge CI: `build-and-audit`, `Verify site data and links`, `Q51 evidence and engine verification`, `GitHub Pages`, and `pages-build-deployment` all succeeded on the merge commit.
- GitHub Pages API after deployment: `status=built`, `build_type=legacy`, `source=main /`.
- Both the canonical root dashboard (https://kanlerxz87-cyber.github.io/NFL2/) and the separate `/docs/` site were fetched successfully after deployment. The API/workflow destination mismatch remains reported above rather than silently treated as resolved.

## Scope boundary

This follow-up corrected one inaccurate provenance sentence and added two sourced review rows to the canonical `data/flags.csv`; the root site pages were rebuilt from those sources. No NFL facts, league data, models, or other sessions' tools were altered. The Pages workflow/configuration itself remains unchanged; its ambiguous deployment mode is published as FL-23 for owner review.
