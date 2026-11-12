# COORDINATION.md — Shared Task Board (combined across parallel sessions)

> **How this file works (per project instructions):** This is the single shared task board for all parallel sessions. Each task lists its status (`unclaimed` / `in progress` / `done` / `needs review`), the owning session ID, and the files it touches. Claim a task by writing your session ID + file scope here, then commit + push the claim immediately. Never start a task another session has claimed. Keep scopes non-overlapping. If a task needs a file owned by another session, log the request here instead of editing it. Make small, frequent commits; run `git pull --rebase` before every push. On merge conflict: stop, resolve without discarding the other session's work, log it here. On finish: record sources, verification performed, and irregularities; mark `done`. Never mark anything verified without checking it against an official source and linking that source. Shared outputs (table data, site index/navigation) are changed only by the final integration session. If a session crashes or its claim is >60 minutes old with no commits, any other session may take over and note the handoff.

**Sessions on this board:**
- `194db560` — branch `arena/194db560-nfl2`, branched from `01f2271` on `main`. **PR #1 (`44fd56d`) + PR #3 (`e351a8d`) merged to `main`.** Scope: repo-root site (`index.html`, `*.html`, `assets/`, `data/standings-2026.json` etc.).
- `arena-85d79210` — branch `arena/85d79210-nfl2`, branched from `01f2271` on `main`. **PR #4 (`38fe046`) + PR #5 (`f64078f`) merged to `main`.** Scope: `docs/` site + `data/*_2026.json` + `scripts/validate_data.py` + `.github/workflows/pages.yml`.
- `eaba7863` — branch `arena/eaba7863-nfl2`, branched from `01f2271` on `main`. **Active.** Non-overlapping scope: `data/full-injuries-week10-2026.json`, `data/depth-charts-2026.json`, `data/team-stats-offense-defense-2026.json`, `data/correlations-2026.json`, `data/nfl-rules-operations-2026.json`, `data/repo-audit-2026.json`, `depth-deficiencies.html`, `correlations.html`, `repo-audit.html`, `scripts/compute_correlations.py`, `scripts/verify_site.py`, plus final integration pass across shared pages once module tasks complete.

**Last updated:** 2026-11-12 (UTC)
**Site live at:** https://kanlerxz87-cyber.github.io/NFL2/

---

## Task board — Session 194db560 (root build, preserved verbatim)

| # | Task | Status | Owner | Files touched | Sources / verification | Irregularities |
|---|---|---|---|---|---|---|
| T1 | Repo audit + COORDINATION.md setup | done | 194db560 | `COORDINATION.md`, `README.md` | Repo empty except `README.md` at `01f2271` | None |
| T2 | Verified data collection (standings, schedule, injuries, rules) | done | 194db560 | `data/*.json`, `standings.html`, `schedule.html`, `injuries.html` | NFL.com official pages | See Flagged page |
| T3 | Executive summary | done | 194db560 | `executive-summary.html` | Synthesizes T2 only | — |
| T4 | Suggestions review board | done | 194db560 | `suggestions.html` | N/A (proposals) | — |
| T5 | Questions / info gaps register | done | 194db560 | `questions.html` | N/A (open questions) | — |
| T6 | Originated-lines methodology (Lines Lab) | done | 194db560 | `lines-lab.html`, `assets/app.js` | NFL Official Playing Rules; MODEL ONLY | No sportsbook odds reproduced |
| T7 | Strategy leaderboard + gates + correlation | done | 194db560 | `strategies.html` | Framework only; no fabricated win rates | See Flagged page |
| T8 | Injury & depth-chart deficiency tracker | done | 194db560 | `injuries.html` | NFL.com Week 10 injury report | Depth charts not published by NFL — flagged |
| T9 | Site build (landing + subpages) | done | 194db560 | `index.html`, `*.html`, `assets/*` | — | — |
| T10 | Final integration: re-verify, link check, Pages deploy | done | 194db560 | All (merge only) | 32/32 standings, 19/19 schedule, 16/16 injury, 32/32 team rows sourced | — |
| T11 | PR to `main`, merge, confirm Pages deploy | done | 194db560 | — | PR #1 merged `44fd56d` | — |

## Task board — Session arena-85d79210 (docs/ build, preserved verbatim)

| ID | Task | Status | Owner | Files touched (scope) |
|---|---|---|---|---|
| T-01 | Repo review + source verification (standings, schedule, stats, injuries) | done | arena-85d79210 | `data/*_2026.json`, `docs/standings.html`, `docs/schedule.html`, `docs/stats.html`, `docs/injuries.html`, `docs/sources.html` |
| T-02 | Executive summary + QIA register | done | arena-85d79210 | `docs/executive-summary.html`, `docs/questions.html`, `data/questions.json` |
| T-03 | Suggestions review board | done | arena-85d79210 | `docs/suggestions.html`, `data/suggestions.json` |
| T-04 | Originate-own-lines methodology + calculator | done | arena-85d79210 | `docs/lines.html`, `docs/assets/app.js` |
| T-05 | Strategy leaderboard (single/parlay/props, gates, correlation, skill-vs-luck) | done | arena-85d79210 | `docs/strategies.html`, `data/strategies.json` |
| T-06 | Injury + depth-chart + defensive-deficiency tracking | done | arena-85d79210 | `docs/injuries.html`, `docs/depth-charts.html`, `docs/defense.html` |
| T-07 | GitHub Pages site (landing + subpages, dashboard UI) | done | arena-85d79210 | `docs/**`, `.github/workflows/pages.yml` |
| T-08 | Final integration: re-verify, link check, PR + merge + Pages deploy | done | arena-85d79210 | `COORDINATION.md`, `README.md`, PR #4 + PR #5 to `main` |

## Task board — Session eaba7863 (deep official-source verification, depth-chart strings, correlations & integration audit)

| ID | Task | Status | Owner | Files touched (non-overlapping scope) | Sources / verification | Irregularities |
|---|---|---|---|---|---|---|
| E-01 | Line-by-line repo audit (`01f2271`..`f64078f`) + automated HTML/table-row-source/link verifier | done | eaba7863 | `repo-audit.html`, `data/repo-audit-2026.json`, `scripts/verify_site.py`, `scripts/build_new_pages.py` | Git commit history + official `nfl.com` / `operations.nfl.com` cross-check | Found `REG9` vs `REG10` URL bug in root `injuries.html`/`flagged.html`/`sources.html`, missing `<td>` in `lines-lab.html`, and unlinked framework rows across root + `docs/` |
| E-02 | Full Official NFL Week 10 Injury Report ingestion (all 14 games, DNP/LP/FP + Out/Questionable) | done | eaba7863 | `data/full-injuries-week10-2026.json`, `scripts/build_verified_datasets.py` | `https://www.nfl.com/injuries/league/2026/REG10` (all 7 chunks verified line-by-line; 222 player rows across 28 teams) | 4 teams show "No Injuries Reported" on REG10 table despite IR/ruled-out QB news — flagged |
| E-03 | Official NFL club 1st/2nd/3rd/4th-string depth charts & offense/defense replacement deficiency tracker | done | eaba7863 | `depth-deficiencies.html`, `data/depth-charts-2026.json` | 12 official club depth charts (`commanders.com`, `giants.com`, `patriots.com`, `detroitlions.com`, `baltimoreravens.com`, `miamidolphins.com`, `49ers.com`, `azcardinals.com`, `seahawks.com`, `therams.com`, `packers.com`, `dallascowboys.com`) + `operations.nfl.com` roster rules | Club depth charts carry "unofficial" PR disclaimers & roster lag (e.g. `therams.com` lists Aaron Donald) — flagged |
| E-04 | Official 2026 NFL Team Offense/Defense Stats + Reproducible Empirical Correlations (`n=32`) + Luck-vs-Skill Residuals | done | eaba7863 | `correlations.html`, `data/team-stats-offense-defense-2026.json`, `data/correlations-2026.json`, `scripts/compute_correlations.py` | `nfl.com/stats/team-stats/offense/{passing,rushing}/2026/reg/all`, `nfl.com/stats/team-stats/defense/{passing,rushing}/2026/reg/all`, `nfl.com/standings/division/2026/reg` | Play-level SGP/prop leg correlations left blank & flagged (awaiting play-by-play feed) |
| E-05 | Official 2026 NFL Operations & Rulebook anchors (2026 rule changes, 48-active/8-OL, PS elevations, AT spotters) | done | eaba7863 | `data/nfl-rules-operations-2026.json` | `operations.nfl.com/rules-officiating/2026-nfl-rulebook`, `operations.nfl.com/calendar-events/nfl-free-agency/contract-language` | — |
| E-06 | Final integration: verify combined root + `docs/` builds line-by-line, fix missing row source links & `REG9`->`REG10` URL without discarding any session's files, PR + merge + confirm Pages live | in progress | eaba7863 | Shared navigation/tables (`*.html`, `docs/*.html`, `data/injuries-week10-2026.json`, `README.md`) | `python3 scripts/verify_site.py` + `python3 scripts/validate_data.py` + live Pages check | — |

## Claim log

- 2026-11-12 — Session `194db560` claimed T1, T2, T9 on branch `arena/194db560-nfl2`. Scope: `COORDINATION.md`, `README.md`, `index.html`, `assets/*`, `data/*`, `*.html`. Completed T1–T10; PR #1 merged to `main` (`44fd56d`).
- 2026-11-12 — Session `arena-85d79210` claimed T-01…T-08 on branch `arena/85d79210-nfl2` (repo appeared empty except `README.md` at claim time; PR #1 had not yet merged). Scope: `docs/**`, `data/*_2026.json`, `scripts/`, `.github/workflows/pages.yml`. No overlapping file scopes with 194db560 except `README.md` + `COORDINATION.md` (shared outputs — integration session only).
- 2026-11-12 — Session `eaba7863` claimed E-01…E-05 (and queued E-06 integration) on branch `arena/eaba7863-nfl2`. Non-overlapping scope: `depth-deficiencies.html`, `correlations.html`, `repo-audit.html`, `data/full-injuries-week10-2026.json`, `data/depth-charts-2026.json`, `data/team-stats-offense-defense-2026.json`, `data/correlations-2026.json`, `data/nfl-rules-operations-2026.json`, `data/repo-audit-2026.json`, `scripts/compute_correlations.py`, `scripts/verify_site.py`.

## Handoff / conflict log

- **2026-11-12 — Merge conflict on PR #2 (resolved, nothing discarded).** While `arena-85d79210` was building, session `194db560` merged PR #1 to `main` (`44fd56d`: root site + `data/standings-2026.json` etc.). PR #2 (`docs/` build) then showed `CONFLICTING`. Resolution: `git merge origin/main` into `arena/85d79210-nfl2`. Only `README.md` + `COORDINATION.md` conflicted (both sessions edited them); all other files auto-merged (root build files added alongside `docs/` build — different paths, no overlap). Both files were rewritten to preserve **both** sessions' boards/logs verbatim above. No files deleted. Root build preserved at repo root; `docs/` build preserved under `docs/`. Pages: workflow deploys `docs/`; root build remains for review. Logged here per instructions.
- **2026-11-12 — Merge conflict in `COORDINATION.md` when syncing `origin/main` (`f64078f`) into `arena/eaba7863-nfl2` (resolved, nothing discarded).** Session `arena-85d79210` merged PR #4 (`38fe046`) and PR #5 (`f64078f`) while `eaba7863` pushed its initial `COORDINATION.md` claim (`c6ae227`). Resolution: merged `origin/main` into `arena/eaba7863-nfl2` keeping 100% of `194db560` and `arena-85d79210` files, boards, verification logs, and PR records verbatim, and appended `eaba7863`'s non-overlapping task table (`E-01`…`E-06`). Zero files discarded.

## Verification log — arena-85d79210

- **Standings:** NFL.com League + Division Standings (2026 REG), 32 rows transcribed. `data/standings_2026.json`.
- **Schedule Week 11:** NFL.com Week 11 Schedule + Nov 9 NFL Media schedule-change release. `data/schedule_week11_2026.json`.
- **Stats:** NFL.com Passing/Rushing/Receiving/Tackles + Defense Passing/Rushing. `data/player_leaders_2026.json`, `data/team_stats_defense_2026.json`.
- **Injuries:** NFL.com News Roundup Nov 11 (Week 10 snapshot, F-02). `data/injuries_2026-11-11.json`.
- **Validation:** `python3 scripts/validate_data.py` PASSED. Internal link check: 16 docs pages, 0 broken internal links. Local preview HTTP 200.
- **Frameworks (T-02…T-06):** Original analysis on verified inputs only. No fair line / strategy performance / correlation coefficient presented as measured fact (TBD pending data).

## Irregularities flagged (arena-85d79210; also on `docs/flagged.html`)

| ID | Irregularity | Status |
|---|---|---|
| F-01 | Third-party standings disagree with NFL.com (NFL.com authoritative) | needs review |
| F-02 | Injury roundup is Week 10 snapshot, not Week 11 | needs review |
| F-03 | Backup-QB lists conflict across outlets (UNVERIFIED) | needs review |
| F-04 | NFL.com Defense Scoring placeholders (unused) | needs review |
| F-05 | No licensed market-odds feed | needs review |
| F-06 | No play-by-play/EPA/snaps/weather | needs review |
| F-07 | No backtests; leaderboard empty by design | needs review |
| F-08 | 6 bye teams as published (unusual) | needs review |
| F-09 | Week 11 injury URL 404 at fetch | needs review |

## PR & merge record

- Session 194db560: PR #1 merged to `main` (`44fd56d`). Pages source `/` on `main`.
- Session 194db560 follow-up: PR #3 merged to `main` (`e351a8d`, records PR #1 merge + Pages built). Pages: BUILT at https://kanlerxz87-cyber.github.io/NFL2/ (source `/` on `main`).
- Session arena-85d79210: PR #2 closed (superseded) → PR #4 `https://github.com/kanlerxz87-cyber/NFL2/pull/4` — **MERGED 2026-11-12T04:37:55Z, merge commit `38fe046`**; follow-up PR #5 merged (`f64078f`). Pages: workflow `GitHub Pages` success + `pages-build-deployment` success; Pages status `built`. Live: root build at https://kanlerxz87-cyber.github.io/NFL2/ (source `/`) and docs/ build at https://kanlerxz87-cyber.github.io/NFL2/docs/index.html (both verified live 2026-11-12). T-08 done.
