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
| T00 | Create this board, define tasks and scopes, push claim | in progress | `session-01b698ef` | `COORDINATION.md` | 2026-11-12 |
| T01 | Repo audit, line-by-line review, flag irregularities, official links for manual review | in progress | `session-01b698ef` | `research/repo-audit.md`, `research/irregularities.md` | 2026-11-12 |
| T02 | Official-source registry: discover + fetch-verify every official URL used anywhere on the site | in progress | `session-01b698ef` | `research/sources.md`, `research/source-registry.json` | 2026-11-12 |
| T03 | Full requirements list (line-by-line), acceptance criteria, status | in progress | `session-01b698ef` | `content/requirements.md`, `content/brief.md` | 2026-11-12 |
| T04 | Decision prerequisites: clear list of questions / information / answers known and missing; discovery suggestions | in progress | `session-01b698ef` | `content/decision-gates.md` | 2026-11-12 |
| T05 | Improvement suggestions + decision path chooser (review picks before implementing) | in progress | `session-01b698ef` | `content/suggestions.md` | 2026-11-12 |
| T06 | Strategy research: originating own lines, signals, single bets, parlays, player-prop combos, leaderboard with rewards | in progress | `session-01b698ef` | `content/strategies.md` | 2026-11-12 |
| T07 | Validation gates, correlation values, skill-vs-luck separation, out-of-sample protocol | in progress | `session-01b698ef` | `content/validation.md` | 2026-11-12 |
| T08 | Injury / lineup / depth-chart tracking design (2nd–4th string replacements, offense and defense) | in progress | `session-01b698ef` | `content/injuries.md` | 2026-11-12 |
| T09 | Executive summary | in progress | `session-01b698ef` | `content/executive-summary.md` | 2026-11-12 |
| T10 | **Integration (shared outputs):** table data, site index + navigation, build, line-by-line re-verification, broken-link check, publish | unclaimed | — | `data/`, `site/`, `tools/`, `README.md`, `.nojekyll`, `.github/workflows/` | — |
| T11 | PR from integration branch → `main`, merge without waiting, confirm Pages deploy, record PR link + result here | unclaimed | — | `COORDINATION.md` (log section) | — |

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

## Verification log (per task)

Filled in as each task completes. **Nothing is marked verified without checking it against an official
source and linking that source.**

| Task | Sources used | Verification performed | Irregularities |
| --- | --- | --- | --- |
| T00 | `git branch -a`, `git ls-tree -r HEAD`, `gh api repos/kanlerxz87-cyber/NFL2/pages` (local/official GitHub API) | Repo tree and remote branch inventory read directly | Branch-per-session requirement not achievable in this environment |

## Handoff / conflict notes

- Crash or stale claim rule: if a claim is more than 60 minutes old with no commits, another session may
  take over the task and note the handoff here, preserving the prior session's work.
- On merge conflict: stop, resolve without discarding the other session's work, and log what happened
  in this section.
