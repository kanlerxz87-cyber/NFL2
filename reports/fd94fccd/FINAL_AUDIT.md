# Independent final audit — NFL2 decision site

**Audit session:** `fd94fccd` on `arena/fd94fccd-nfl2`  
**Audit date:** 2026-11-12 (UTC)  
**Purpose:** Independent re-run of the existing repository checks and review of the live site/configuration. This is an audit report, not a new model-performance claim.

## Result

The existing implementation covers the requested decision workflow: a landing dashboard and category pages; requirements; open questions; a separately reviewable suggestion register; line-originating methods and signals; singles/parlays/prop-combo design; correlation methodology; skill-vs-luck gates; injury and depth/availability records; strategy leaderboard/rewards; an executive summary; and a Flagged for Review page. These are already present on the live root site. The separate Q51 pages describe their outputs as **paper-only and unvalidated**.

The independent build and local verification commands all exited successfully. This does **not** mean the proposed strategies have demonstrated skill or that all NFL availability inputs are complete. The project itself correctly leaves those conclusions blocked or unverified.

## Verification performed

| Check | Observed result |
|---|---|
| `python3 tools/build_site.py` | Built 22 root pages; 588 missing cells displayed as “not published”. |
| `python3 tools/verify.py` | 39 checks passed, 0 warnings, 0 failures. Checks include register schemas, standings arithmetic, 254 injury rows, 227 depth events, 136 game rows with per-row NFL game links, and game-log/standings reconciliation. |
| `python3 tools/check_site.py` | 10 checks passed, 0 failures. All 22 pages are generated and navigable; 1,295 links point to NFL.com; internal links/anchors resolve; no blank cells or unresolved template markers. It emits one disclosed warning for four non-league hosts on the source-registry page (see findings). |
| `python3 scripts/audit_all_pages.py` | 96 HTML pages, 36 JSON files, 222 tables, 3,423 rows; 0 broken links and 0 column mismatches. The repository auditor reports all table rows sourced under its official/canonical-source rules. |
| `python3 -m unittest discover -s tests/q51 -v` | 36 tests passed. |
| `python3 scripts/verify_q51.py` | 10 Q51 pages; 155/155 rows have an official or canonical source; 130 explicit blanks; 0 errors. |
| `python3 engine/verify_repo_and_site.py` | 326 portal rows have official HTTPS source links; 1,619 repository internal links checked; 0 broken. |
| `python3 scripts/verify_s53126614.py` | 9 JSON datasets, 10 pages, 262 rows, 100% official HTTPS row links; 3,287 internal links/assets checked, 0 broken. |
| GitHub CI on this audit branch | `build-and-audit`, `Verify site data and links`, and `Q51 evidence and engine verification` completed successfully. |
| GitHub Pages API and live page | API reports `built`, legacy source `main` `/`; live root page fetched successfully at https://kanlerxz87-cyber.github.io/NFL2/ . |

The machine-readable source register and row-level audits are in `data/sources.csv`, `data/verification-report.json`, `q51/`, and the scripts listed above. Official manual-review starting points include the [NFL injury hub](https://www.nfl.com/injuries/), [NFL standings](https://www.nfl.com/standings/), [NFL regular-season schedules](https://www.nfl.com/schedules/2026/REG/), and [NFL Football Operations](https://operations.nfl.com/). Where the official source does not expose a needed value, the site flags the gap and leaves the value blank.

## Findings requiring review

1. **Landing-page historical attribution is inaccurate as currently worded.** `content/index.md` says, “Everything on this site was therefore created in this session, in one branch,” immediately after describing the original one-file repository state. The current repository and site were assembled by multiple parallel sessions and merged PRs. The initial-state description is historical context, but that sentence over-attributes the final site to one session. Suggested correction: say the project was built across multiple documented sessions and link to the coordination/integration log. This audit did not edit the canonical page because it is generated shared output outside this task's scope.
2. **Pages publishing configuration merits a deployment-owner check.** The GitHub Pages API currently reports legacy publication from `main` `/`, while `.github/workflows/pages.yml` uploads the `docs/` tree as an Actions Pages artifact. The live root currently serves the root dashboard and the latest recorded deployment checks succeeded, but those two configuration descriptions should be reconciled/documented to avoid a future deployment publishing the wrong tree. No workflow/config file was changed in this audit.
3. **Non-league source-registry links are intentionally not primary NFL evidence.** `tools/check_site.py` warns about four non-league hosts on `sources.html` (DraftKings Network, Patriots Wire/USA Today, Morgan Stanley, NBER). The registry classifies them as third-party/research/corroboration and states their restricted use; they are not substitutes for official injury, standings, schedule, or game evidence. The warning is non-failing, but those entries should remain visibly distinguished from official-league sources.
4. **The coordination board's original T18 row remains marked `in progress` despite the later PR #24 integration and successful main-branch Pages/CI records.** This is a stale board-state inconsistency; this audit did not rewrite another integration session's row.

## Decision/product limits that remain explicit

- No trustworthy, timestamped, book-identified 2026 archive of spreads, totals, moneylines, and prop prices was found in the audited evidence; without that, no current-season closing-line value or validated betting edge is established.
- The Q51 independent engine's README reports its spread and total forecast errors worse than the closing-line benchmark and **zero strategies certified**. Treat all current lines and correlations as exploratory/paper-only, not as proof of skill.
- The root correlation register does not assert fitted rho values; the Q51 measured descriptive correlations are tied to their stated sample and are not automatically a causal or predictive estimate.
- Injury/practice data are point-in-time snapshots with incomplete published designations. The root flags report that only 6 of 254 rows had game-status values in the captured Week 10 snapshot. The official NFL hub is the source of record: https://www.nfl.com/injuries/ . Do not treat missing rows/fields as “healthy.”
- The official depth-chart evidence needed to label second-/third-/fourth-string replacements is incomplete; the project flags the gap rather than infer ranks. NFL news and injury evidence cited in the register include https://www.nfl.com/news/nfl-week-10-injury-report-2026-season and https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11 .

## Scope boundary

No facts, source values, generated pages, datasets, models, or other sessions' tools were altered. The only code-repository additions for this task are this report and the appended coordination log/change requests. The canonical-site wording and Pages configuration findings are requests for the shared site/deployment owner, not unreviewed changes.
