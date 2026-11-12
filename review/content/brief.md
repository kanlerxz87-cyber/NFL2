# Primary source: the project brief (verbatim)

Recorded 2026-11-12 (UTC). This is the primary source for the requirements list. It is
reproduced verbatim so every requirement can be traced line-by-line. No edits, corrections
or interpretations have been applied here; interpretation lives in `requirements.md`.

---

NFL

The goal of this project is to collect, organize, and analyze utilizing a full list of requirements.

Make suggestions on how to improve the site to improve decision making and create a section dedicated for suggestions so someone can review suggestions and choose the best path before implementing any changes.

I want a clear list of questions, informations and answers that need to be addressed before any decision can be reasonably made bases upon the information that we already have and do not have.  Suggestions need to be made to discover missing information.

I want to originate my own NFL lines.  Research and develop strategies for generating useful signals.  Treat it as a leaderboard competition that provides rewards for top performing strategies.  Look at single bet, parlays, player prop bet combos.   Each strategy must pass validation gates.  Determine correlation values.  Remove luck from the equation and build strategies that are selectively skill based.

The system should be tracking injuries and know any deficiencies in defenses such as 2nd,3rd or 4th string backups having to replace starters due to lineups.  Also same can be said for offenses using starters or backups.

Create an executive summary outlining important details.

There should be no manual input on my part. Work on your own to finish all tasks in this session. Work line by line, verify everything from official verified trusted sources, no hallucinations.

REPO WORK

Review the repo. Work line by line verifying from official verified trusted sources, and provide links for manual review. Flag any irregularities for review. No hallucinations.

SITE CREATION

Create a github page live site for this repo with a clean landing page and subpages organized by category. The UI should be clean, user friendly, simple, and easy to use, like a simple dashboard. It should contain all entries and findings in a simple, easy to read table format, and include any analysis and findings. Work line by line, verify everything, no hallucinations.

VERIFICATION

Verify line by line. Every table row must have a source link to an official site. If a value can't be confirmed from an official source, leave it blank and flag it as unverified. Never infer or fill in values.

PARALLEL SESSIONS

Multiple agent sessions may work on this repo at the same time, so coordinate to avoid conflicts and duplicate work. Before starting, read COORDINATION.md in the repo root (create it if it doesn't exist). It is the shared task board, listing each task, its status (unclaimed, in progress, done, needs review), the owning session ID, and the files it touches. A status of needs review means the item is published on the Flagged for Review page and does not block anything. Claim a task by writing your session ID and file scope there, then commit and push that claim immediately, and never start a task another session has claimed. Keep scopes non-overlapping: each session works on its own branch (or git worktree) named session-<id>/<task> and edits only the files in its claimed scope. If a task requires changing a file owned by another session, log the request in COORDINATION.md instead of editing it. Make small, frequent commits, and run git pull --rebase before every push. If you hit a merge conflict, stop, resolve it without discarding the other session's work, and log what happened. When a task is finished, record its sources, the verification performed, and any irregularities in COORDINATION.md and mark it done. Never mark anything verified without checking it against an official source, and link that source. Shared outputs, such as the table data and the site's index and navigation, are changed only by a final integration session once all other tasks are done. That session merges the branches, re-verifies the combined data line by line, confirms the site builds with no broken links, and publishes to GitHub Pages. If a session crashes or its claim is more than 60 minutes old with no commits, any other session may take over the task and note the handoff in the log.

PULL REQUEST AND MERGE

Do not stop to wait for my review. Work fully on your own from start to finish. When all tasks are done and the final integration session has verified the combined data and confirmed the site builds with no broken links, create a pull request from the integration branch to main with a summary of the changes, the sources used, and any flagged irregularities. Then merge the pull request without waiting for approval, confirm GitHub Pages deploys successfully, and record the PR link and merge result in COORDINATION.md. Flagged irregularities and unverified items do not block the merge. Publish them on a clearly labeled "Flagged for Review" page on the site, with the source links, so I can review them after the site is live and request changes. If the build, a check, or the deploy fails, fix the problem and retry until the site is live. Do not merge a broken site.

---

## Constraints discovered while executing

* The execution environment pins work to the current branch `arena/01b698ef-nfl2` and forbids
  creating or pushing other branches, so the per-session branch/worktree requirement cannot be
  literally satisfied. Logged as irregularity F10 and in `COORDINATION.md`.
* Direct outbound shell network access is blocked; official pages were verified with the
  provided page-fetch/search tools. Logged as audit item A12.
