# Repo audit — line-by-line (T01)

**Session:** `session-01b698ef` · **Audited:** 2026-11-12 (UTC)
**Base commit:** `01f227119ee8df4223b0aa697d08ed92257773c3` (`main`, "Initial commit")
**Working branch:** `arena/01b698ef-nfl2`

## Method

Each item below was checked with a local `git` / `gh` command against this checkout or the
official GitHub API. Nothing was assumed from memory. Links are provided for manual review.

| # | Object / line | Observed content | How verified | Official link for manual review | Status |
| --- | --- | --- | --- | --- | --- |
| A01 | `README.md`, line 1 | `# NFL2` (6 bytes total, no trailing newline) | `git ls-tree -r HEAD` + `cat README.md \| od -c` | https://github.com/kanlerxz87-cyber/NFL2/blob/main/README.md | verified |
| A02 | repository tree at base commit | Exactly one tracked file: `README.md` (blob `bea05f1ebccb7ec645e358f4ff3a3b14380e1ffd`) | `git ls-tree -r HEAD` | https://github.com/kanlerxz87-cyber/NFL2/tree/01f227119ee8df4223b0aa697d08ed92257773c3 | verified |
| A03 | commit history | One commit: `01f2271 Initial commit` | `git log --oneline -5` | https://github.com/kanlerxz87-cyber/NFL2/commits/main | verified |
| A04 | branches | `main` and `arena/01b698ef-nfl2`; remote has only `origin/main` and `origin/HEAD -> origin/main` at audit time | `git branch -a` | https://github.com/kanlerxz87-cyber/NFL2/branches | verified |
| A05 | remote | `origin https://github.com/kanlerxz87-cyber/NFL2.git` | `git remote -v` | https://github.com/kanlerxz87-cyber/NFL2 | verified |
| A06 | default branch | `main` | `gh repo view --json defaultBranchRef` | https://github.com/kanlerxz87-cyber/NFL2 | verified |
| A07 | GitHub Pages config | `status: built`, `build_type: legacy`, `source.branch: main`, `source.path: /`, `https_enforced: true`, `html_url: https://kanlerxz87-cyber.github.io/NFL2/` | `gh api repos/kanlerxz87-cyber/NFL2/pages` | https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site | verified |
| A08 | `COORDINATION.md` | Did not exist at base commit; created by this session | `cat COORDINATION.md` (404 before creation) | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md | verified |
| A09 | `.gitignore`, `LICENSE`, CI workflow, `.nojekyll`, `404.html`, site files, data files | Absent at base commit | `ls -la` + `git ls-tree -r HEAD` | https://github.com/kanlerxz87-cyber/NFL2/tree/01f227119ee8df4223b0aa697d08ed92257773c3 | verified |
| A10 | git identity | `kanlerxz87-cyber <312694378+kanlerxz87-cyber@users.noreply.github.com>` | `git config user.name`, `git config user.email` | https://github.com/kanlerxz87-cyber/NFL2 | verified |
| A11 | GitHub auth | Authenticated as `kanlerxz87-cyber` via `GH_TOKEN` | `gh auth status` | https://github.com/kanlerxz87-cyber/NFL2 | verified |
| A12 | outbound network from sandbox | Direct `curl` to `www.nfl.com` fails with `SSL_ERROR_SYSCALL`; all external verification therefore went through the fetch/search tools, not shell networking | `curl -sS -o /tmp/nfltest.html -w ... https://www.nfl.com/injuries/` | https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages | verified (environment fact) |

## Lines that could not be verified

There are no unverified *repository* lines: the entire tracked tree was one 6-byte file and
was read byte-by-byte. Unverified **data values** (odds, correlations, strategy scores) are
a different matter and are handled on the site: blank cells plus `UNVERIFIED` flags.
See [`irregularities.md`](../research/irregularities.md) and the site's
"Flagged for Review" page.

## What the audit means

The repository contained no dataset, no schema, no code, no tests and no prior analysis.
Therefore every finding on the site is either (a) a fact copied from a fetch-verified
official page, (b) a documented design proposal, or (c) an explicitly blank/unverified
value. No pre-existing project values were inherited, inferred or "filled in".
