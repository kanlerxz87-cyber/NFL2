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
| S-01 | Official-source data acquisition + line-by-line verification (standings, schedule, injuries, team stats, rosters) | **done** | arena-009ec582 | `data/**` |
| S-02 | Deterministic analysis engine (arithmetic re-verification, correlation, luck decomposition, line origination, validation gates) | **done** | arena-009ec582 | `scripts/**`, `data/derived/**` |
| S-03 | Decision register: questions / information held / information missing / answers needed | unclaimed | — | `pages/decisions.html`, `data/decisions.json` |
| S-04 | Suggestions review board (proposals, effort, risk, evidence, chosen path) | unclaimed | — | `pages/suggestions.html`, `data/suggestions.json` |
| S-05 | Strategy lab: leaderboard, validation gates, correlation, luck removal | unclaimed | — | `pages/strategy.html`, `data/strategy.json` |
| S-06 | Injury & personnel-deficiency tracker (starters vs 2nd/3rd/4th string) | **in progress** | arena-009ec582 | `pages/injuries.html`, `data/injuries_week10.json`, `data/depth_charts.json` |
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
| 2026-11-12 | 122-game log vs official standings | Recomputed PF, PA, W, L, T, PCT, net points and current streak for all 32 clubs from the game log and compared to the published standings | **all 32 clubs match on every field** (checks V3a, V3b, V4, V5, V6, V8, V10) |
| 2026-11-12 | Team-stat conservation | League-total offense equals league-total defense allowed for passing yards (63,556), rushing yards (30,580), sacks (641), pass TD (411), rush TD (257), INT (197), pass 1st downs (3,006), rush 1st downs (1,757) | **all 8 identities hold exactly** (checks V12a–V12h) |
| 2026-11-12 | Derived rates | AVG == YDS/CAR (32/32), CMP% == 100*CMP/ATT (31/32), YPA == YDS/ATT (28/32) | 3 disagreements recorded as source irregularities, not silently corrected |
| 2026-11-12 | Model sign convention | Asserted the power-rating line predicts the home side at 64.6% (>50%); an inverted sign would score <50% | **PASS** |

---

## 5. Irregularities & requests for review

| ID | Item | Finding | Action |
|---|---|---|---|
| IR-01 | NFL.com depth-chart route | `https://www.nfl.com/teams/<club>/depth-chart/` returns HTTP-equivalent 404 ("Flag on the Play") for the club tested | Depth charts declared **unavailable from an official source**; personnel-deficiency analysis is derived from official injury report + official roster positions instead. |
| IR-02 | NFL.com season-level team-stat URLs | `/stats/team-stats/offense/points/2026/reg/` returns 404; the working path is `/stats/team-stats/offense/scoring/2026/reg/all` | Use the verified path in the registry. |
| IR-03 | Standings column mapping | Source table has 16 data columns; the page legend names only 12. The trailing record columns cannot be mapped with certainty from the page alone. | Mapped empirically instead: columns 8–9 were shown to be home/road records and column 16 the last-5 record by re-deriving them from the 122-game log. Column 15 is confirmed as STRK. Only confirmed columns are published. |
| IR-04 | **Home-field advantage measures ≈ zero** | Home clubs are 60-61-1 in the 122-game log — a home win rate of **.4963**, and the mean home margin is **+0.00** points. The conventional NFL prior (~2.5–3 pts) is not present in this season's data. | HFA is applied at its measured value (+0.00) rather than the conventional prior. Sensitivity analysis published on the Methods page. This materially changes every model line. |
| IR-05 | Team scoring tables unusable | Both `offense/scoring` and `defense/scoring` team pages render 4 header-less columns; no arithmetic identity holds for columns 3–4 (SF 12+17≠31, TB 11+6≠19, ATL 9+11≠21, DEN 9+11≠21), and the defensive identity fails for CIN (1+1+0 vs published 0). | The four columns are **not published or used**. Flagged as FL-04. |
| IR-06 | 'TOTAL OFFENSIVE YARDS' on club pages ≠ team-stat page | KC club page prints 3069 total offensive yards; the official team-stat pages give 2037 passing + 1102 rushing = 3139. The 70-yard gap is unexplained. | Both published values are shown side by side with the discrepancy stated. Flagged as FL-05. Nothing is reconciled by assumption. |
| IR-07 | Derived-rate disagreements | CMP% for WAS computes to 61.7 from 164/266 but NFL.com prints 61.6. YPA disagrees for KC, JAX, SEA, PIT under every candidate denominator tested ((YDS+SACK_YDS)/(ATT+SACKS) fails 22/32; YDS/(ATT+SACKS) fails 32/32). | Published values are transcribed as published; the recomputation is shown next to them so the disagreement is visible. Flagged FL-06/FL-07. |
| IR-08 | Player leaderboard column order unestablishable | The rushing (9 cols) and receiving (11 cols) leaderboards render with no header row, and no consistent arithmetic identity identifies the columns — YDS/CAR and YDS/REC fail for all 25 sampled rows under every candidate ordering. | Those boards are **not published**. Only 8 passers whose 15-value line is arithmetically identical to their club's official team passing line are published. Flagged FL-08. |
| IR-09 | No official odds source | No NFL.com property publishes betting lines, spreads, totals or player-prop prices. | No market comparison, no ROI, no closing-line value. Profitability **cannot** be claimed anywhere on the site. Flagged FL-01. |

---

## 6. Merge record

| Item | Value |
|---|---|
| PR | _pending_ |
| Merge result | _pending_ |
| Pages deploy | _pending_ (GitHub Pages already enabled: source `main`, path `/`, legacy builder, https enforced) |
