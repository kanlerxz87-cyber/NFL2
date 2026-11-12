# COORDINATION.md — NFL2 Shared Task Board (Combined Across All Parallel Sessions)

> This file is the single source of truth for parallel agent sessions.
> Read it before starting any work. Claim a task by writing your session ID + file scope
> here, then commit and push the claim immediately.
> Status values: `unclaimed` · `in progress` · `done` · `needs review`

**Last updated:** 2026-11-12 (UTC)
**Site live at:** https://kanlerxz87-cyber.github.io/NFL2/

---

## 1. Active & Completed Sessions

| Session ID | Branch | PRs Merged | Scope Summary |
|---|---|---|---|
| `194db560` | `arena/194db560-nfl2` | PR #1 (`44fd56d`), PR #3 (`e351a8d`) | Initial root static pages (`executive-summary.html`, `schedule.html`, `lines-lab.html`, etc.) & `data/*-2026.json` |
| `arena-85d79210` | `arena/85d79210-nfl2` | PR #4 (`38fe046`), PR #5 (`f64078f`) | `docs/` 16-page dashboard, `data/*_2026.json`, `scripts/validate_data.py`, `.github/workflows/pages.yml` |
| `arena-009ec582` | `arena/009ec582-nfl2` | PR #6 (`93a2f9d`) | 136-game log (`data/games_2026.json`), deterministic engine (`scripts/analyse.py`, `scripts/build_site.py`, `scripts/verify_*.py`), 12 generated root pages |
| `eaba7863` | `arena/eaba7863-nfl2` | Active (Final Integration) | 12 official club depth charts & 1st–4th string cascades (`depth-deficiencies.html`, `data/depth-charts-2026.json`), 2026 rulebook/operations anchors (`data/nfl-rules-operations-2026.json`), team correlations & luck residuals (`correlations.html`, `scripts/compute_correlations.py`), full repo & row-source audit (`repo-audit.html`, `scripts/audit_all_pages.py`), cross-session integration |

---

## 2. Task Boards (All Sessions Preserved Verbatim)

### Session `arena-009ec582` Task Board (PR #6)

| ID | Task | Status | Owner | File scope |
|---|---|---|---|---|
| S-00 | Coordination board + source registry + repo scaffolding | **done** | arena-009ec582 | `COORDINATION.md`, `README.md`, `.nojekyll`, `.gitignore` |
| S-01 | Official-source data acquisition + line-by-line verification (standings, schedule, injuries, team stats, rosters) | **done** | arena-009ec582 | `data/**` |
| S-02 | Deterministic analysis engine (arithmetic re-verification, correlation, luck decomposition, line origination, validation gates) | **done** | arena-009ec582 | `scripts/**`, `data/derived/**` |
| S-03 | Decision register: questions / information held / information missing / answers needed | **done** | arena-009ec582 | `data/questions.json`, `questions.html` |
| S-04 | Suggestions review board (proposals, effort, risk, evidence, chosen path) | **done** | arena-009ec582 | `data/suggestions.json`, `suggestions.html` |
| S-05 | Strategy lab: leaderboard, validation gates, correlation, luck removal | **done** | arena-009ec582 | `data/derived/analysis.json`, `strategies.html` |
| S-06 | Injury & personnel-deficiency tracker (starters vs 2nd/3rd/4th string) | **done (4 of 32 clubs charted)** | arena-009ec582 | `data/injuries_week10.json`, `data/depth_charts.json`, `data/derived/personnel.json`, `injuries.html` |
| S-07 | Executive summary | **done** | arena-009ec582 | `EXECUTIVE_SUMMARY.md`, `index.html` |
| S-08 | Site build (dashboard, tables, navigation, flagged-for-review page, source links) | **done** | arena-009ec582 | `*.html`, `assets/**`, `scripts/build_site.py` |
| S-09 | Build verification: broken-link scan, HTML validation, data/HTML consistency, local serve test | **done (12/12)** | arena-009ec582 | `scripts/verify_site.py`, `data/derived/site_report.json` |
| S-10 | Integration: re-verify combined data, open PR → `main`, merge, confirm Pages deploy, record result | **done** | arena-009ec582 | PR #6 merged `93a2f9d` |

### Session `194db560` Task Board (PR #1, PR #3)

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
| T11 | PR to `main`, merge, confirm Pages deploy | done | 194db560 | — | PR #1 merged `44fd56d`; PR #3 merged `e351a8d` | — |

### Session `arena-85d79210` Task Board (PR #4, PR #5)

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

### Session `eaba7863` Task Board (Active Integration Session)

| ID | Task | Status | Owner | Files touched (non-overlapping scope) | Sources / verification | Irregularities |
|---|---|---|---|---|---|---|
| E-01 | Line-by-line repo audit (`01f2271`..`93a2f9d`) + automated HTML/table-row-source/link verifier | done | eaba7863 | `repo-audit.html`, `data/repo-audit-2026.json`, `scripts/audit_all_pages.py`, `scripts/build_new_pages.py` | Git commit history + official `nfl.com` / `operations.nfl.com` cross-check | Found `REG9` vs `REG10` URL bug in legacy root files, missing `<td>` in `lines-lab.html`, and unlinked rows |
| E-02 | Full Official NFL Week 10 Injury Report ingestion (all 14 games, DNP/LP/FP + Out/Questionable) | done | eaba7863 | `data/full-injuries-week10-2026.json`, `scripts/build_verified_datasets.py` | `https://www.nfl.com/injuries/league/2026/REG10` (222 player rows across 28 teams) | 4 teams show "No Injuries Reported" on REG10 table despite IR/ruled-out QB news — flagged |
| E-03 | Official NFL club 1st/2nd/3rd/4th-string depth charts (12 clubs) & offense/defense replacement deficiency tracker | done | eaba7863 | `depth-deficiencies.html`, `data/depth-charts-2026.json` | 12 official club depth charts (`commanders.com`, `giants.com`, `patriots.com`, `detroitlions.com`, `baltimoreravens.com`, `miamidolphins.com`, `49ers.com`, `azcardinals.com`, `seahawks.com`, `therams.com`, `packers.com`, `dallascowboys.com`) + `operations.nfl.com` roster rules | Club depth charts carry "unofficial" PR disclaimers & roster lag (e.g. `therams.com` lists Aaron Donald) — flagged |
| E-04 | Official 2026 NFL Team Offense/Defense Stats + Reproducible Empirical Correlations (`n=32`) + Luck-vs-Skill Residuals | done | eaba7863 | `correlations.html`, `data/team-stats-offense-defense-2026.json`, `data/correlations-2026.json`, `scripts/compute_correlations.py` | `nfl.com/stats/team-stats/offense/{passing,rushing}/2026/reg/all`, `nfl.com/stats/team-stats/defense/{passing,rushing}/2026/reg/all`, `nfl.com/standings/division/2026/reg` | Play-level SGP/prop leg correlations left blank & flagged (awaiting play-by-play feed) |
| E-05 | Official 2026 NFL Operations & Rulebook anchors (2026 rule changes, 48-active/8-OL, PS elevations, AT spotters) | done | eaba7863 | `data/nfl-rules-operations-2026.json` | `operations.nfl.com/rules-officiating/2026-nfl-rulebook`, `operations.nfl.com/calendar-events/nfl-free-agency/contract-language` | — |
| E-06 | Final cross-session integration: unify styling/navigation, ensure 100% per-row official source links across all HTML pages, pass all sessions' verifiers, PR + merge + confirm Pages live | in progress | eaba7863 | Shared navigation/tables (`scripts/build_site.py`, `*.html`, `docs/*.html`, `README.md`, `COORDINATION.md`) | `verify_data.py` + `verify_personnel.py` + `verify_site.py` + `validate_data.py` + `audit_all_pages.py` | — |

---

## 3. Source Registry (Official / Primary Sources Only)

| Key | Source | URL | Used for |
|---|---|---|---|
| `NFL-STANDINGS` | NFL.com official standings, 2026 REG | https://www.nfl.com/standings/division/2026/reg | W-L-T, PCT, PF, PA, net points, streak |
| `NFL-SCHEDULE` | NFL.com official 2026 schedule | https://www.nfl.com/schedules/2026/REG11/ | Week 10/11 matchups, kickoff, broadcast |
| `NFL-INJURIES` | NFL.com official injury report, Week 10 2026 | https://www.nfl.com/injuries/league/2026/REG10 | Player, position, injury, practice status, game status |
| `NFL-TEAM-STATS-OFF` | NFL.com 2026 team offense stats | https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all | Pass/rush/score production |
| `NFL-TEAM-STATS-DEF` | NFL.com 2026 team defense stats | https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all | Pass/rush/score allowed |
| `NFL-CLUB-DEPTH` | Official NFL club `/team/depth-chart` pages (12 clubs) | e.g. https://www.patriots.com/team/depth-chart | 1st–4th string offense/defense depth cascades |
| `NFL-RULES` | 2026 NFL Official Playing Rules & Rulebook | https://operations.nfl.com/rules-officiating/2026-nfl-rulebook | Scoring, 2026 kickoff/onside/disqualification changes |
| `NFL-OPS` | NFL Football Operations (roster limits, elevations, AT spotters) | https://operations.nfl.com/calendar-events/nfl-free-agency/contract-language | 53-man roster, 48/47 active (8-OL), PS elevations, spotters |

---

## 4. Combined Verification Logs

- **Session `arena-009ec582`:** 136-game log vs official standings (all 32 clubs match on every field, checks V3a–V10); 8 league-total offense=defense conservation identities hold exactly (63,556 pass yds, 30,580 rush yds, 641 sacks, 411 pass TD, 257 rush TD, 197 INT); power-rating sign check PASS (65.97%); `verify_site.py` 12/12 PASS.
- **Session `arena-85d79210`:** 32 standings rows, Week 11 schedule + Nov 9 schedule change, player/defense leaders, `scripts/validate_data.py` PASS, 16 `docs/` pages verified.
- **Session `eaba7863`:** 32-team offense/defense passing & rushing cross-checked against `team_stats_defense_2026.json` and `standings-2026.json` (`scripts/compute_correlations.py` 0 errors); 14 reproducible team correlations (`C-01`..`C-14`), 222 Week 10 `REG10` player entries, 12 official club depth charts, and `scripts/audit_all_pages.py` row-level source link verification.

---

## 5. Irregularities & Flagged Items Across Sessions

| ID | Item | Finding | Action |
|---|---|---|---|
| IR-01 | NFL.com depth-chart route | `nfl.com/teams/<club>/depth-chart/` returns 404; individual club sites (`patriots.com`, `49ers.com`, etc.) publish PR-compiled depth charts with explicit "Unofficial" disclaimers and roster lag (e.g. `therams.com` still lists Aaron Donald; `miamidolphins.com` leaves `K` blank) | Cross-joined 12 official club depth charts with `REG10` + IR news and flagged all club-chart lag on `flagged.html` & `depth-deficiencies.html`. |
| IR-02 | `REG10` IR / Pre-Practice Blindspot | `nfl.com/injuries/league/2026/REG10` displays "No Injuries Reported" for SEA, CIN, LAC, and BAL despite SEA ruling QB1 Sam Darnold out, CIN reporting 3 Wed injuries, and BAL missing QB1 Lamar Jackson + QB2 Tyler Huntley on IR | Joined `REG10` with official NFL.com IR/starter news and flagged as RA-05. |
| IR-03 / IR-04 | Standings unlabelled cols & 2026 HFA (+0.50 pts across 129 true home games, 95% CI [−1.80, +2.79]) | Pooled 136-game mean home margin is +0.00 due to 7 neutral-site games; true-home mean is +0.50 pts | Documented & modelled transparently; multi-season data requested in `questions.html`. |
| IR-05 / IR-08 | Unusable NFL.com scoring & rushing/receiving headerless tables | `offense/scoring`, `defense/scoring`, and headerless player rushing/receiving boards fail arithmetic column checks | Excluded / flagged (`FL-04`..`FL-08`, `F-04`). |
| IR-06 / IR-07 | KC club total yards gap (3069 vs 3139) & rounding/YPA discrepancies (WAS CMP%, KC/JAX/SEA/PIT YPA) | Official NFL.com pages disagree slightly on derived rates | Published verbatim alongside recomputed values (`FL-05`..`FL-07`). |
| IR-09 / F-05 | No official sportsbook / prop / play-by-play EPA feed | NFL.com publishes no betting odds, SGP prices, or snap-weighted replacement EPA | Market comparisons, SGP play-level correlations (`U-C01`..`U-C06`), and backup EPA point deltas left blank & flagged. |
| RA-02 / RA-03 | Legacy root `REG9` URL & `lines-lab.html` 7-col row | PR #1 root files linked `REG9` for Week 10 injuries and omitted 1 `<td>` on `NO at CHI` | Fixed in `E-06` integration and logged in `repo-audit.html`. |

---

## 6. Handoff, Conflict Resolution & PR Merge Record

- **PR #1 (`44fd56d`) & PR #3 (`e351a8d`)** — Session `194db560` merged initial root build to `main`.
- **PR #2 (closed) → PR #4 (`38fe046`) & PR #5 (`f64078f`)** — Session `arena-85d79210` resolved `README.md`/`COORDINATION.md` conflict with PR #1, preserving both root and `docs/` builds.
- **PR #6 (`93a2f9d`)** — Session `arena-009ec582` merged 136-game deterministic engine + 12 generated root pages while preserving `docs/` and all prior `data/*.json` files.
- **2026-11-12 — Merge conflict in `COORDINATION.md` when syncing PR #6 (`93a2f9d`) into `arena/eaba7863-nfl2` (resolved, nothing discarded):** Session `eaba7863` renamed its new full-repo auditor to `scripts/audit_all_pages.py` before merging so `arena-009ec582`'s `scripts/verify_site.py` merged untouched, and combined `COORDINATION.md` preserving 100% of `194db560`, `arena-85d79210`, `arena-009ec582`, and `eaba7863` task boards, verification logs, and irregularity logs. Zero files discarded.
