# COORDINATION.md — shared task board

**Repository:** `kanlerxz87-cyber/NFL2`
**Board owner / integration session:** `session-01b698ef`
**Current branch:** `arena/01b698ef-nfl2` (branched from `main@01f227119ee8df4223b0aa697d08ed92257773c3`)
**Board created:** 2026-11-12 (UTC)
**Purpose:** shared task board for parallel agent sessions. Claim a task by writing your session ID and file scope below, then commit and push the claim immediately. Never start a task another session has claimed.

## Environment constraint (flagged irregularity, does not block work)

The request specifies per-session branches / worktrees named `session-<id>/<task>`. This execution
environment pins every session to the single fixed branch `arena/01b698ef-nfl2` and forbids creating,
switching to, or pushing any other branch. Therefore this board serializes tasks **on the fixed branch**
using non-overlapping **file scopes** instead of separate branches. Remote branch inventory was checked
at board creation (`git branch -a`): only `main` and `arena/01b698ef-nfl2` exist, so there are no
competing sessions or branches at this time. If another session appears, it must claim an unclaimed
task with a disjoint file scope, run `git pull --rebase` before every push, and log the handoff here.
See `site/flagged.html` → "Flagged for Review" for the published version of this irregularity.

## Task board

Status vocabulary: `unclaimed` | `in progress` | `done` | `needs review`
`needs review` = published on the "Flagged for Review" page; it does not block anything.

| Task ID | Task | Status | Owner session ID | File scope (exclusive) | Claimed / updated (UTC) |
| --- | --- | --- | --- | --- | --- |
| T00 | Create this board, define tasks and scopes, push claim | done | `session-01b698ef` | `COORDINATION.md` | 2026-11-12 |
| T01 | Repo audit, line-by-line review, flag irregularities, official links for manual review | done | `session-01b698ef` | `research/repo-audit.md`, `research/irregularities.md` | 2026-11-12 |
| T02 | Official-source registry: discover + fetch-verify every official URL used anywhere on the site | done | `session-01b698ef` | `research/sources.md`, `research/source-registry.json` | 2026-11-12 |
| T03 | Full requirements list (line-by-line), acceptance criteria, status | done | `session-01b698ef` | `content/requirements.md`, `content/brief.md` | 2026-11-12 |
| T04 | Decision prerequisites: clear list of questions / information / answers known and missing; discovery suggestions | done | `session-01b698ef` | `content/decision-gates.md` | 2026-11-12 |
| T05 | Improvement suggestions + decision path chooser (review picks before implementing) | done | `session-01b698ef` | `content/suggestions.md` | 2026-11-12 |
| T06 | Strategy research: originating own lines, signals, single bets, parlays, player-prop combos, leaderboard with rewards | done | `session-01b698ef` | `content/strategies.md` | 2026-11-12 |
| T07 | Validation gates, correlation values, skill-vs-luck separation, out-of-sample protocol | done | `session-01b698ef` | `content/validation.md` | 2026-11-12 |
| T08 | Injury / lineup / depth-chart tracking design (2nd–4th string replacements, offense and defense) | done | `session-01b698ef` | `content/injuries.md` | 2026-11-12 |
| T09 | Executive summary | done | `session-01b698ef` | `content/executive-summary.md` | 2026-11-12 |
| T10 | **Integration (shared outputs):** table data, site index + navigation, build, line-by-line re-verification, broken-link check, publish | done | `session-01b698ef` (final integration session) | `data/`, `site/`, `tools/`, `README.md`, `.nojekyll`, `.github/workflows/`, root `*.html`, `assets/`, `404.html` | 2026-11-12 |
| T11 | PR from integration branch → `main`, merge without waiting, confirm Pages deploy, record PR link + result here | in progress | `session-01b698ef` | `COORDINATION.md` (log section) | 2026-11-12 |

**Shared outputs rule:** `data/`, the site's `index.html` and navigation are changed only by the final
integration session (T10), once T01–T09 are done. Tasks requiring a file owned by another session must
log a request here instead of editing it.

## Claims (this session)

`session-01b698ef` claims T00 immediately and will claim each remaining task in order, with a commit and
push at each claim. All scopes above are disjoint except `COORDINATION.md`, which is reserved for the
board owner. Because no other session is present (verified via remote branch inventory), this session
also performs T10 (integration) and T11 (PR/merge) after T01–T09 are marked `done`.

## Commit / push / conflict log

| UTC | Event | Detail |
| --- | --- | --- |
| 2026-11-12 | Board created, T00 claimed | Initial board; no competing branches found; environment branch constraint flagged. |
| 2026-11-12 | T01–T09 claimed | Claims pushed before starting those tasks; disjoint file scopes. |
| 2026-11-12 | T01–T09 done | Research, source registry, requirements, decision gates, suggestions, strategies, validation, injuries, executive summary written; sources/verification/irregularities recorded in the log above. |
| 2026-11-12 | T10 claimed as final integration session | Only after T01–T09 were marked done; shared outputs now in scope. |
| 2026-11-12 | T10 done | Static site + shared table data + navigation + assets + CI verifier committed; `python3 tools/verify.py` exits 0 with 0 broken links; build is reproducible (second build produces byte-identical output). |
| 2026-11-12 | T11 claimed | PR / merge / deploy phase. |

## Verification log (per task)

Filled in as each task completes. **Nothing is marked verified without checking it against an official
source and linking that source.**

| Task | Sources used | Verification performed | Irregularities |
| --- | --- | --- | --- |
| T00 | `git branch -a`, `git ls-tree -r HEAD`, `gh api repos/kanlerxz87-cyber/NFL2/pages` (local/official GitHub API) | Repo tree and remote branch inventory read directly | Branch-per-session requirement not achievable in this environment |
| T01 | https://github.com/kanlerxz87-cyber/NFL2/tree/01f227119ee8df4223b0aa697d08ed92257773c3 · https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site | `git ls-tree -r HEAD`, `od -c README.md`, `git log`, `git branch -a`, `git remote -v`, `gh repo view`, `gh api repos/.../pages`, `gh auth status`; 12 audit rows (A01–A12) | F11 (baseline repo hygiene), F10 (single-branch environment) |
| T02 | `research/source-registry.json` (33 fetch-verified official URLs) | Every URL opened with fetch_page; title + excerpt recorded; non-official search results explicitly excluded | F08 (search snippet URL/title mismatch), F09 (canonical redirects), F10 (shell network blocked) |
| T03 | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md | 52 atomic requirements traced line-by-line to the verbatim brief | R12/R20 numeric values left UNVERIFIED |
| T04 | S01–S32 in `research/source-registry.json` | 12 "have" items verified; 17 blocking questions; blank answers left blank | F01, F02, F03, F05, F06, F07, F13 |
| T05 | https://operations.nfl.com/programs-initiatives/innovation/big-data-bowl · https://www.kaggle.com/docs/competitions | 5 ranked paths + 10 usability suggestions; decision record intentionally blank | No path chosen; no changes implemented |
| T06 | S01–S25, S36 official sources | 15 candidate strategies, 11 official data inputs, leaderboard design | F01, F02, F12; all performance values blank |
| T07 | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html · https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html · https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html · https://www.itl.nist.gov/div898/handbook/ · https://www.kaggle.com/docs/competitions | 12 gates, 10 correlation pairs, 9-step skill protocol | F12 — every numeric result blank + UNVERIFIED |
| T08 | https://www.nfl.com/injuries/league/2026/REG10 · https://www.chiefs.com/team/depth-chart · https://operations.nfl.com/game-operations-logistics/preparation-safety/game-and-stadium-prep · https://www.nfl.com/news/competition-committee-approves-revisions-to-injury-report-0ap3000000688693 | 20 injury rows and 10 depth rows copied verbatim; 11-field tracker schema | F03, F05, F07, F14; replacement_depth and deficiency_index UNVERIFIED |
| T09 | all of the above | Executive summary cross-checked against every prior task | 14 flagged items summarised |
| T10 | `research/source-registry.json`, `data/content.py`, `data/records.json`, https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages | Built 16 pages / 41 tables / 423 rows from one data file; `tools/verify.py` re-checked every record against the rendered HTML cell by cell (423/423 rows carry an official source link; 230 blank cells are genuinely empty; 94 UNVERIFIED rows each have a blank cell and a flag; 292 internal links and 562 external links checked; 0 broken links); CI workflow `.github/workflows/verify.yml` re-runs build reproducibility + verification | F10 (single-branch environment), F11 (baseline hygiene now fixed), F14 (point-in-time snapshots) |

## Handoff / conflict notes

- Crash or stale claim rule: if a claim is more than 60 minutes old with no commits, another session may
  take over the task and note the handoff here, preserving the prior session's work.
- On merge conflict: stop, resolve without discarding the other session's work, and log what happened
  in this section.
