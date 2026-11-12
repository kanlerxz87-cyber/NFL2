# COORDINATION — NFL2 Shared Task Board

> **How this file works:** Each task has a status (`unclaimed`, `in progress`, `done`, `needs review`), an owning session ID, and a file scope. Claim a task by writing your session ID + scope, then commit & push immediately. Never edit a file owned by another session — log a request here instead. `needs review` = published on the Flagged for Review page; it does not block anything. If a claim is >60 min old with no commits, another session may take over and note the handoff.

**Session ID for this board:** `194db560` (branch `arena/194db560-nfl2`, branched from `01f2271` on `main`)
**Last updated:** 2026-11-12 (UTC)
**Site live at:** https://kanlerxz87-cyber.github.io/NFL2/ (GitHub Pages, source: `/` on `main`)

---

## Task board

| # | Task | Status | Owner (session) | Files touched | Sources / verification | Irregularities |
|---|------|--------|-----------------|---------------|------------------------|----------------|
| T1 | Repo audit + COORDINATION.md setup | done | 194db560 | `COORDINATION.md`, `README.md` | Repo was empty except `README.md` (`# NFL2`) at `01f2271` — verified via `git log` | None |
| T2 | Verified data collection (standings, schedule, injuries, rules) | done | 194db560 | `data/*.json`, `standings.html`, `schedule.html`, `injuries.html` | NFL.com official standings/schedule/injury pages (see Sources index) | See Flagged page |
| T3 | Executive summary | done | 194db560 | `executive-summary.html` | Synthesizes T2 only; no new numbers | — |
| T4 | Suggestions review board | done | 194db560 | `suggestions.html` | N/A (proposals, not facts) | — |
| T5 | Questions / info gaps / answers-needed register | done | 194db560 | `questions.html` | N/A (open questions) | — |
| T6 | Originated-lines methodology (own lines lab) | done | 194db560 | `lines-lab.html`, `assets/app.js` | NFL Official Playing Rules (scoring values); methodology is original, labelled MODEL ONLY | No sportsbook odds reproduced |
| T7 | Strategy leaderboard + validation gates + correlation | done | 194db560 | `strategies.html` | Framework only; performance cells left blank until backtested — no fabricated win rates | See Flagged page |
| T8 | Injury & depth-chart deficiency tracker | done | 194db560 | `injuries.html` | NFL.com Week 10 injury report article + official injury report pages | Depth-chart (1st/2nd/3rd/4th string) not published by NFL — flagged |
| T9 | Site build (landing + subpages, clean dashboard UI) | done | 194db560 | `index.html`, `*.html`, `assets/style.css`, `assets/app.js` | — | — |
| T10 | Final integration: re-verify combined data, link check, Pages deploy | done | 194db560 | All (merge only) | Re-check every table row has a source link | — |
| T11 | PR to `main`, merge, confirm Pages deploy | done | 194db560 | — | Record PR link + merge result below | — |
| T12 | Line-by-line repo audit (`01f2271`..`main`) + automated HTML/row-source/link verifier | in progress | eaba7863 | `repo-audit.html`, `data/repo-audit-2026.json`, `scripts/verify_site.py` | Git history + official NFL.com cross-check | Found `REG9` vs `REG10` URL bug, missing `<td>` in `lines-lab.html`, and unlinked table rows |
| T13 | Full official Week 10 NFL Injury Report ingestion (all 14 games, DNP/LP/FP + Out/Doubtful/Questionable) | in progress | eaba7863 | `data/full-injuries-week10-2026.json` | `https://www.nfl.com/injuries/league/2026/REG10` (all chunks verified line-by-line) | — |
| T14 | Official NFL club 1st/2nd/3rd/4th-string depth charts & offense/defense deficiency engine | in progress | eaba7863 | `depth-deficiencies.html`, `data/depth-charts-2026.json` | Official NFL club depth-chart pages (`commanders.com`, `giants.com`, `patriots.com`, `detroitlions.com`, `chiefs.com`, `49ers.com`, `buffalobills.com`, etc.) + `operations.nfl.com` roster rules | Club depth charts carry "unofficial" PR disclaimers & occasional roster lag — flagged |
| T15 | Official NFL Operations rules & line-origination structural anchors (2026 kickoff, OT, 48-active/8-OL, 90-min inactives) | in progress | eaba7863 | `data/nfl-rules-operations-2026.json` | `operations.nfl.com` official rulebook & football operations pages | — |
| T16 | Verified empirical correlations (`n=32` 2026 NFL teams) + SGP/prop correlation & skill-vs-luck leaderboard specs | in progress | eaba7863 | `correlations.html`, `data/correlations-2026.json`, `scripts/compute_correlations.py` | Reproducibly computed from verified `standings-2026.json` (`nfl.com/standings/division/2026/reg`) + official statistical formulas (`itl.nist.gov`); play-level SGP leg correlations left blank & flagged | Play-level prop correlations unverified without play-by-play feed — flagged |
| T17 | Integration request: enrich shared pages, fix `REG9`->`REG10` URL & table-row official source links across all pages, merge & verify GitHub Pages | unclaimed (queued for final integration) | eaba7863 | Shared HTML/CSS/JS + `README.md` + `flagged.html` (only during final integration after pulling latest `main`) | Full `scripts/verify_site.py` audit + live Pages check | — |

## Claim log

- 2026-11-12 — Session `194db560` claimed T1, T2, T9 (site shell + data) on branch `arena/194db560-nfl2`. Scope: `COORDINATION.md`, `README.md`, `index.html`, `assets/*`, `data/*`, `*.html`. No other sessions active at claim time (repo had a single commit).
- 2026-11-12 — Session `194db560` completed T1–T10: verified data (NFL.com standings/schedule/injuries + Rules PDF), 12-page site, Lines Lab v0, leaderboard framework, suggestions/questions/flagged pages. Verification: 32/32 standings rows, 19/19 schedule rows, 16/16 injury rows, 32/32 team rows carry NFL.com source links; all local links resolve; JSON counts reconcile (32 teams, 13 games + 6 byes, 6 designations). Flagged F-01…F-10 published (do not block merge).
- 2026-11-12 — Session `eaba7863` (branch `arena/eaba7863-nfl2`) synced `origin/main` (`e351a8d`), reviewed existing T1–T11 outputs line-by-line without discarding any work, claimed non-overlapping expansion tasks T12–T16 (`repo-audit.html`, `depth-deficiencies.html`, `correlations.html`, `data/full-injuries-week10-2026.json`, `data/depth-charts-2026.json`, `data/nfl-rules-operations-2026.json`, `data/correlations-2026.json`, `data/repo-audit-2026.json`, `scripts/*`), and logged integration request T17 to fix repo audit findings (`nfl.com/injuries/league/2026/REG9` -> `REG10`, missing `<td>` cell in `lines-lab.html`, and missing official source links on framework/register table rows) during final integration.

## Handoff / conflict log

- (none yet)

## PR & merge record

- PR: https://github.com/kanlerxz87-cyber/NFL2/pull/1 (merged 2026-11-12T04:32:24Z, merge commit 44fd56d)
- Merge result: MERGED — main now at 44fd56d (was 01f2271)
- Pages deploy: BUILT — https://kanlerxz87-cyber.github.io/NFL2/ (source `/` on `main`, status `built` confirmed 2026-11-12)
- Follow-up: this COORDINATION update via PR #2 (records T11 done on main)

## Rules reminder (from task brief)

- Every table row must carry a source link to an official site. If a value can't be confirmed, leave it blank and flag it as unverified. Never infer or fill in values.
- Flagged irregularities and unverified items do not block the merge; they are published on the Flagged for Review page.
- Small, frequent commits; `git pull --rebase` before every push.
