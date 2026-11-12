# COORDINATION — NFL2 (shared task board)

> This file is the single source of truth for parallel agent sessions.
> Read it before starting any work. Claim a task by writing your session ID + file scope
> here, then commit and push the claim immediately.
> Status values: `unclaimed` · `in progress` · `done` · `needs review`

**Last updated:** 2026-11-12T04:35Z
**Branch model in use:** single-branch session. The Arena platform pins this session to
`arena/009ec582-nfl2`; per-session branches (`session-<id>/<task>`) are not permitted for this
session (platform rule: one branch, no switching/creating branches). All work therefore happens on
`arena/009ec582-nfl2`, and that branch acts as the integration branch. File scopes below are still
enforced to keep concurrent work non-overlapping.

---

## 1. Active sessions

| Session ID | Branch | Started (UTC) | Notes |
|---|---|---|---|
| `arena-009ec582` | `arena/009ec582-nfl2` | 2026-11-12T04:30Z | Owner of all tasks below. No other session was present at claim time. |

---

## 2. Task board

| ID | Task | Status | Owner | File scope |
|---|---|---|---|---|
| S-00 | Coordination board + source registry + repo scaffolding | **done** | arena-009ec582 | `COORDINATION.md`, `README.md`, `.nojekyll`, `.gitignore` |
| S-01 | Official-source data acquisition + line-by-line verification (standings, schedule, injuries, team stats, rosters) | **in progress** | arena-009ec582 | `data/**` |
| S-02 | Deterministic analysis engine (arithmetic re-verification, correlation, luck decomposition, line origination, validation gates) | unclaimed | — | `scripts/**`, `data/derived/**` |
| S-03 | Decision register: questions / information held / information missing / answers needed | unclaimed | — | `pages/decisions.html`, `data/decisions.json` |
| S-04 | Suggestions review board (proposals, effort, risk, evidence, chosen path) | unclaimed | — | `pages/suggestions.html`, `data/suggestions.json` |
| S-05 | Strategy lab: leaderboard, validation gates, correlation, luck removal | unclaimed | — | `pages/strategy.html`, `data/strategy.json` |
| S-06 | Injury & personnel-deficiency tracker (starters vs 2nd/3rd/4th string) | unclaimed | — | `pages/injuries.html`, `data/injuries.json` |
| S-07 | Executive summary | unclaimed | — | `EXECUTIVE_SUMMARY.md`, `pages/executive-summary.html` |
| S-08 | Site build (dashboard, tables, navigation, flagged-for-review page, source links) | unclaimed | — | `index.html`, `pages/**`, `assets/**` |
| S-09 | Build verification: broken-link scan, HTML validation, data/HTML consistency, local serve test | unclaimed | — | `scripts/verify_site.py`, `data/derived/verification_report.json` |
| S-10 | Integration: re-verify combined data, open PR → `main`, merge, confirm Pages deploy, record result | unclaimed | — | `COORDINATION.md` (log section only) |

### Rules of engagement
1. Never edit a file outside your claimed scope. If you need a change in someone else's file,
   log a *request* in §5 instead of editing.
2. Never mark anything verified without an official source link **and** the check you performed.
3. Never infer, estimate, or back-fill a value. Blank + flagged is always preferred to a guess.
4. Small, frequent commits. `git pull --rebase` before every push.
5. A crashed session's claim may be taken over after 60 minutes with no commits — log the handoff.

---

## 3. Source registry (official / primary sources only)

| Key | Source | URL | Used for |
|---|---|---|---|
| `NFL-STANDINGS` | NFL.com official standings, 2026 REG | https://www.nfl.com/standings/ | W-L-T, PCT, PF, PA, net points, streak |
| `NFL-SCHEDULE` | NFL.com official 2026 schedule | https://www.nfl.com/schedules/2026/REG/ | Week 10 matchups, kickoff, broadcast |
| `NFL-INJURIES` | NFL.com official injury report, Week 10 2026 | https://www.nfl.com/injuries/ | Player, position, injury, practice status, game status |
| `NFL-TEAM-STATS-OFF` | NFL.com 2026 team offense stats | https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all | Pass/rush/score production |
| `NFL-TEAM-STATS-DEF` | NFL.com 2026 team defense stats | https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all | Pass/rush/score allowed |
| `NFL-ROSTER` | NFL.com official team rosters (per team) | https://www.nfl.com/teams/<club>/roster/ | Active roster, position, experience |
| `NFL-RULES` | NFL official playing rules & rulebook | https://www.nfl.com/rulebook/ | Scoring/OT/tie rules cited in methodology |
| `NFL-OPS` | NFL Football Operations (roster limits, injury policy) | https://operations.nfl.com/ | Roster sizes, game-day actives, injury-report policy |

**Not available to this environment (declared gaps, not filled):** licensed sportsbook odds
(DraftKings/FanDuel/BetMGM), player-prop market lines, official All-22/participation data,
Next Gen Stats API, official depth charts (NFL.com depth-chart route returns 404 — see §5 IR-01).
Anything requiring those is published as a **model-implied estimate**, labelled as such, never as a
market line.

---

## 4. Verification log

| Date (UTC) | Item | Check performed | Result |
|---|---|---|---|
| 2026-11-12 | `NFL-STANDINGS` | Arithmetic re-derivation of every row: `PCT = (W + T/2) / (W+L+T)` and `NET = PF − PA` | see `data/derived/verification_report.json` |
| 2026-11-12 | `NFL-TEAM-STATS-OFF` | Cross-check team scoring vs standings PF/PA | see verification report |

---

## 5. Irregularities & requests for review

| ID | Item | Finding | Action |
|---|---|---|---|
| IR-01 | NFL.com depth-chart route | `https://www.nfl.com/teams/<club>/depth-chart/` returns HTTP-equivalent 404 ("Flag on the Play") for the club tested | Depth charts declared **unavailable from an official source**; personnel-deficiency analysis is derived from official injury report + official roster positions instead. |
| IR-02 | NFL.com season-level team-stat URLs | `/stats/team-stats/offense/points/2026/reg/` returns 404; the working path is `/stats/team-stats/offense/scoring/2026/reg/all` | Use the verified path in the registry. |
| IR-03 | Standings column mapping | Source table has 17 columns; the page legend names only 12. The trailing record columns cannot be mapped with certainty | Only unambiguously labelled columns are transcribed. Unmapped columns are deliberately left blank and flagged. |

---

## 6. Merge record

| Item | Value |
|---|---|
| PR | _pending_ |
| Merge result | _pending_ |
| Pages deploy | _pending_ (GitHub Pages already enabled: source `main`, path `/`, legacy builder, https enforced) |
