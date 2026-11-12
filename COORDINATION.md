# COORDINATION — NFL2 Shared Task Board

> **How this file works:** Each task has a status (`unclaimed`, `in progress`, `done`, `needs review`), an owning session ID, and a file scope. Claim a task by writing your session ID + scope, then commit & push immediately. Never edit a file owned by another session — log a request here instead. `needs review` = published on the Flagged for Review page; it does not block anything. If a claim is >60 min old with no commits, another session may take over and note the handoff.

**Session ID for this board:** `194db560` (branch `arena/194db560-nfl2`, branched from `01f2271` on `main`)
**Last updated:** 2026-11-12 (UTC)
**Site live at:** https://kanlerxz87-cyber.github.io/NFL2/ (GitHub Pages, source: `/` on `main`)

---

## Task board

| # | Task | Status | Owner (session) | Files touched | Sources / verification | Irregularities |
|---|------|--------|-----------------|---------------|------------------------|----------------|
| T1 | Repo audit + COORDINATION.md setup | in progress | 194db560 | `COORDINATION.md`, `README.md` | Repo was empty except `README.md` (`# NFL2`) at `01f2271` — verified via `git log` | None |
| T2 | Verified data collection (standings, schedule, injuries, rules) | in progress | 194db560 | `data/*.json`, `standings.html`, `schedule.html`, `injuries.html` | NFL.com official standings/schedule/injury pages (see Sources index) | See Flagged page |
| T3 | Executive summary | unclaimed | — | `executive-summary.html` | Synthesizes T2 only; no new numbers | — |
| T4 | Suggestions review board | unclaimed | — | `suggestions.html` | N/A (proposals, not facts) | — |
| T5 | Questions / info gaps / answers-needed register | unclaimed | — | `questions.html` | N/A (open questions) | — |
| T6 | Originated-lines methodology (own lines lab) | unclaimed | — | `lines-lab.html`, `assets/app.js` | NFL Official Playing Rules (scoring values); methodology is original, labelled MODEL ONLY | No sportsbook odds reproduced |
| T7 | Strategy leaderboard + validation gates + correlation | unclaimed | — | `strategies.html` | Framework only; performance cells left blank until backtested — no fabricated win rates | See Flagged page |
| T8 | Injury & depth-chart deficiency tracker | unclaimed | — | `injuries.html` | NFL.com Week 10 injury report article + official injury report pages | Depth-chart (1st/2nd/3rd/4th string) not published by NFL — flagged |
| T9 | Site build (landing + subpages, clean dashboard UI) | unclaimed | — | `index.html`, `*.html`, `assets/style.css`, `assets/app.js` | — | — |
| T10 | Final integration: re-verify combined data, link check, Pages deploy | unclaimed | — | All (merge only) | Re-check every table row has a source link | — |
| T11 | PR to `main`, merge, confirm Pages deploy | unclaimed | — | — | Record PR link + merge result below | — |

## Claim log

- 2026-11-12 — Session `194db560` claimed T1, T2, T9 (site shell + data) on branch `arena/194db560-nfl2`. Scope: `COORDINATION.md`, `README.md`, `index.html`, `assets/*`, `data/*`, `*.html`. No other sessions active at claim time (repo had a single commit). Will claim T3–T8, T10–T11 in sequence to keep scopes non-overlapping within this session.

## Handoff / conflict log

- (none yet)

## PR & merge record

- PR: (pending)
- Merge result: (pending)
- Pages deploy: (pending — Pages currently built from `/` on `main`; will re-confirm after merge)

## Rules reminder (from task brief)

- Every table row must carry a source link to an official site. If a value can't be confirmed, leave it blank and flag it as unverified. Never infer or fill in values.
- Flagged irregularities and unverified items do not block the merge; they are published on the Flagged for Review page.
- Small, frequent commits; `git pull --rebase` before every push.
