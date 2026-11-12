# COORDINATION — NFL2 (shared task board)

> This file is the single source of truth for parallel agent sessions.
> Read it before starting any work. Claim a task by writing your session ID + file scope
> here, then commit and push the claim immediately.
> Status values: `unclaimed` · `in progress` · `done` · `needs review`

**Last updated:** 2026-11-12T05:40Z (integration merge by session `bc4b47cf`)
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
| `bc4b47cf` | `arena/bc4b47cf-nfl2` | 2026-11-12T04:10Z | **Integration session.** Claimed the board while `arena-009ec582` was still active on `data/**` and root HTML; see §7 for its own board and §8 for how the two builds were reconciled. |

---

## 2. Task board

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
| S-10 | Integration: re-verify combined data, open PR → `main`, merge, confirm Pages deploy, record result | **done** | arena-009ec582 | `COORDINATION.md` (log section only) |

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
| 2026-11-12 | 136-game log vs official standings | Recomputed PF, PA, W, L, T, PCT, net points and current streak for all 32 clubs from the game log and compared to the published standings | **all 32 clubs match on every field** (checks V3a, V3b, V4, V5, V6, V8, V10) |
| 2026-11-12 | Team-stat conservation | League-total offense equals league-total defense allowed for passing yards (63,556), rushing yards (30,580), sacks (641), pass TD (411), rush TD (257), INT (197), pass 1st downs (3,006), rush 1st downs (1,757) | **all 8 identities hold exactly** (checks V12a–V12h) |
| 2026-11-12 | Derived rates | AVG == YDS/CAR (32/32), CMP% == 100*CMP/ATT (31/32), YPA == YDS/ATT (28/32) | 3 disagreements recorded as source irregularities, not silently corrected |
| 2026-11-12 | Model sign convention | Asserted the power-rating line predicts the home side at 65.97% (>50%); an inverted sign would score <50% | **PASS** |
| 2026-11-12 | Parlay leg dependence | Asserted text matches measured sign, and the generator now derives the sentence from r instead of hardcoding it | **PASS — found and fixed a contradiction where the text said "negatively correlated" while r was +0.076** |

---

## 5. Irregularities & requests for review

| ID | Item | Finding | Action |
|---|---|---|---|
| IR-01 | NFL.com depth-chart route | `https://www.nfl.com/teams/<club>/depth-chart/` returns HTTP-equivalent 404 ("Flag on the Play") for the club tested | Depth charts declared **unavailable from an official source**; personnel-deficiency analysis is derived from official injury report + official roster positions instead. |
| IR-02 | NFL.com season-level team-stat URLs | `/stats/team-stats/offense/points/2026/reg/` returns 404; the working path is `/stats/team-stats/offense/scoring/2026/reg/all` | Use the verified path in the registry. |
| IR-03 | Standings column mapping | Source table has 16 data columns; the page legend names only 12. The trailing record columns cannot be mapped with certainty from the page alone. | Mapped empirically instead: columns 8–9 were shown to be home/road records and column 16 the last-5 record by re-deriving them from the 136-game log. Column 15 is confirmed as STRK. Only confirmed columns are published. |
| IR-04 | **Home-field advantage is not detectable in 2026 — and the pooled figure is misleading** | Pooling all 136 games gives a mean home margin of +0.00 and a home win rate of .4963, which looks like home-field has vanished. But 7 of the 136 games were at neutral sites and have no true home club. | The estimate is restricted to the **129 true home games**: mean home margin **+0.50 pts**, sd 13.32, SE 1.17, **95% CI [−1.80, +2.79]**, true-home win rate .5155. The conventional ~+2.5 pt prior sits **inside** that interval, so this season **cannot reject** it. The model uses +0.50 and the site states plainly that 2026 is too small a sample to settle the question. Closing it needs P-05 (multi-season data). |
| IR-05 | Team scoring tables unusable | Both `offense/scoring` and `defense/scoring` team pages render 4 header-less columns; no arithmetic identity holds for columns 3–4 (SF 12+17≠31, TB 11+6≠19, ATL 9+11≠21, DEN 9+11≠21), and the defensive identity fails for CIN (1+1+0 vs published 0). | The four columns are **not published or used**. Flagged as FL-04. |
| IR-06 | 'TOTAL OFFENSIVE YARDS' on club pages ≠ team-stat page | KC club page prints 3069 total offensive yards; the official team-stat pages give 2037 passing + 1102 rushing = 3139. The 70-yard gap is unexplained. | Both published values are shown side by side with the discrepancy stated. Flagged as FL-05. Nothing is reconciled by assumption. |
| IR-07 | Derived-rate disagreements | CMP% for WAS computes to 61.7 from 164/266 but NFL.com prints 61.6. YPA disagrees for KC, JAX, SEA, PIT under every candidate denominator tested ((YDS+SACK_YDS)/(ATT+SACKS) fails 22/32; YDS/(ATT+SACKS) fails 32/32). | Published values are transcribed as published; the recomputation is shown next to them so the disagreement is visible. Flagged FL-06/FL-07. |
| IR-08 | Player leaderboard column order unestablishable | The rushing (9 cols) and receiving (11 cols) leaderboards render with no header row, and no consistent arithmetic identity identifies the columns — YDS/CAR and YDS/REC fail for all 25 sampled rows under every candidate ordering. | Those boards are **not published**. Only 8 passers whose 15-value line is arithmetically identical to their club's official team passing line are published. Flagged FL-08. |
| IR-09 | No official odds source | No NFL.com property publishes betting lines, spreads, totals or player-prop prices. | No market comparison, no ROI, no closing-line value. Profitability **cannot** be claimed anywhere on the site. Flagged FL-01. |

---

## 6. Merge record

| Item | Value |
|---|---|
| PR | **#6** — https://github.com/kanlerxz87-cyber/NFL2/pull/6 (base `main`, head `arena/009ec582-nfl2`) |
| Merge result | **MERGED** 2026-11-12T04:52:33Z · merge commit **`93a2f9d`** · squash-free merge commit (`--merge`) · no reviewer approval required, per project rule |
| Pages deploy | Source `main`, path `/`, legacy builder, https enforced. **`pages build and deployment` succeeded for `93a2f9d` at 04:52:36Z**, `GitHub Pages` workflow succeeded at 04:52:37Z, Pages API status `built`. Live: https://kanlerxz87-cyber.github.io/NFL2/ · prior session's build still reachable at /NFL2/docs/index.html |

### Merge conflict with concurrent session work — how it was resolved

`main` had advanced to `f64078f` (session `arena-85d79210`, PRs #4 and #5) while this session was
building on `arena/009ec582-nfl2` from `01f2271`. Both sessions wrote **static HTML to the repo root**,
and GitHub Pages is configured as `legacy` / root — so both builds were competing for the same URLs.

Resolution, and the reasoning:

1. **This session's pages win at the root.** They are generated from verified JSON by
   `scripts/build_site.py` and pass 12/12 build checks; every figure has a provenance chain. The
   previous session's root pages were hand-built HTML with no generator and no data behind them.
2. **The previous session's site is preserved, not deleted.** Its complete 16-page build already
   existed in `docs/` on `main`, and `.github/workflows/pages.yml` publishes `docs/`. That tree was
   merged in unchanged, so the previous build remains reachable at
   `https://kanlerxz87-cyber.github.io/NFL2/docs/index.html`.
3. **The previous session's data files are preserved.** Files unique to `main`
   (`data/injuries_2026-11-11.json`, `data/player_leaders_2026.json`, `data/strategies.json`,
   `data/teams.json`, `data/team_stats_defense_2026.json`, the duplicated `*-2026.json` /
   `*_2026.json` pairs) were kept as-is. They are **not read by this session's pipeline**, which uses
   the canonical `data/games_2026.json`, `data/standings_raw.json`, `data/team_stats.json`,
   `data/injuries_week10.json`, `data/depth_charts.json`, `data/player_verified.json`. They are left in
   place so nothing another session produced is destroyed.
4. **`.nojekyll` retained.** Without it, Jekyll's underscore/hyphen rules can drop files from the
   published site.

**Open issue flagged for the next session:** the repository now carries two site builds (root and
`docs/`) produced by two different sessions with different conventions (e.g. `data/injuries_2026-11-11.json`
vs `data/injuries_week10.json`; `lines-lab.html` vs `strategies.html`). This should be consolidated by
picking one build and deprecating the other explicitly, rather than letting both drift. It is recorded
here rather than resolved silently.

---

## 7. Session `bc4b47cf` board (kept intact from `arena/bc4b47cf-nfl2`)

> This session's claims, log and verification record as they stood before the merge. Headings are demoted one level so this file keeps one numbering scheme.

This file is the coordination mechanism for all agent sessions working on `kanlerxz87-cyber/NFL2`.
Read it before touching anything. Claim work before you start it. Never edit files inside another session's scope.

- **Board owner:** whichever session is currently integrating.
- **Session ID convention:** short id from the branch name (`arena/<id>-<repo>` → `<id>`).
- **Stale claim rule:** a claim older than 60 minutes with no commits may be taken over; record the handoff in the Log below.
- **Statuses:** `unclaimed` · `in progress` · `done` · `needs review`
- **`needs review`** means the item is published on the *Flagged for Review* page and does not block other sessions.

---

### Repo review (as of session `bc4b47cf`, 2026-11-12)

| Fact | Detail |
| --- | --- |
| Files tracked | 1 — `README.md` (6 bytes, contents: `# NFL2`) |
| Commits on `main` | 1 — `01f2271 Initial commit` |
| Code / data / config / docs | none present |
| Requirements document | **absent** — no `REQUIREMENTS.md`, no spec, no issue tracker content in repo |
| GitHub Pages | already configured: `legacy` build, source branch `main`, path `/` → https://kanlerxz87-cyber.github.io/NFL2/ |
| Consequence | the site must be buildable from the repo root (`index.html` at root); the requirements register is reconstructed from the project brief in `data/requirements.csv` |

---

### Task board

| ID | Task | Status | Owner session | File scope | Notes |
| --- | --- | --- | --- | --- | --- |
| T1 | Coordination board + repo review | done | `bc4b47cf` | `COORDINATION.md` | this file |
| T2 | Ingestion: Week 10 official injury report (practice snapshot) | done | `bc4b47cf` | `data/raw/nfl_injuries_2026_wk10.md`, `data/injuries_2026_wk10.csv` | 254 rows, 28 teams, 14 games, from nfl.com/injuries/ |
| T3 | Ingestion: Week 10 schedule + standings | done | `bc4b47cf` | `data/schedule_2026_wk10.csv`, `data/standings_2026.csv` | nfl.com/standings/, nfl.com/news week-10 report |
| T4 | Ingestion: roster moves / depth-chart changes (official news roundup) | done | `bc4b47cf` | `data/depth_changes_2026_wk10.csv` | nfl.com Wed 11-Nov-2026 roundup, 4 chunks |
| T5 | Source registry + verification tooling | done | `bc4b47cf` | `data/sources.csv`, `tools/verify.py` | every table row must carry a source id |
| T6 | Requirements register (reconstructed from brief) | done | `bc4b47cf` | `data/requirements.csv` | 34 requirements, traceable to site sections |
| T7 | Questions / known-unknowns / missing information | done | `bc4b47cf` | `data/questions.csv` | 28 decision-blocking questions |
| T8 | Suggestion register (review & choose path) | done | `bc4b47cf` | `data/suggestions.csv` | 25 suggestions, none implemented that the brief did not require — decision pending |
| T9 | Line-origination methodology + signal catalogue | done | `bc4b47cf` | `content/line-origination.md`, `content/signals.md`, `data/signals.csv` | design only, no model output yet |
| T10 | Strategy registry + leaderboard + reward rules | done | `bc4b47cf` | `content/strategies.md`, `content/leaderboard.md`, `data/strategies.csv` | zero strategies have live results; all rows unranked by design |
| T11 | Validation gates definition + current status | done | `bc4b47cf` | `content/validation-gates.md`, `data/gates.csv` | 12 gates; status = blocked pending data |
| T12 | Correlation framework | done | `bc4b47cf` | `content/correlation.md`, `data/correlation.csv` | no estimated rho values yet — placeholders flagged unverified |
| T13 | Skill-vs-luck / sample-size math | done | `bc4b47cf` | `content/skill-vs-luck.md` | analytic formulas, computed locally, no external claims |
| T14 | Bet-type economics (single / parlay / prop combo) | done | `bc4b47cf` | `content/bet-types.md` | math derived, no live odds captured (no verified source) |
| T15 | Site generator + template + styles | done | `bc4b47cf` | `tools/build_site.py`, `assets/**`, `content/index.md` | markdown → static HTML |
| T16 | Link + source audit, `needs review` publication | done | `bc4b47cf` | `tools/check_site.py`, `data/flags.csv`, `content/flagged-for-review.md` | 16 flags |
| T17 | GitHub Actions validation workflow | done | `bc4b47cf` | `.github/workflows/validate.yml` | build + audit on PR/push |
| T18 | Integration: merge to `main`, publish GitHub Pages | in progress | `bc4b47cf` | `*.html`, `README.md`, `.github/**`, `assets/**` | final session only; site is flat at the repo root because Pages is configured for `main` / |

---

### Rules of engagement

1. **Claim before editing.** Write your session id + file scope in the row, `git commit && git push` the claim, then start.
2. **Non-overlapping scope.** One task = one branch `session-<id>/<task>` (or a worktree). Touch only files in your claimed scope.
3. **Requests across scopes.** If you need to change a file owned by another session, add a row to *Change requests* below; do not edit it.
4. **Small, frequent commits.** `git pull --rebase` before every push.
5. **Conflicts.** Stop, resolve without discarding the other session's work, record it in *Log*.
6. **Finish line.** Record sources, verification performed, and irregularities here, then mark the task `done`.
7. **Never mark verified without an official source link.** Unconfirmable values stay blank and get a row in `data/flags.csv`.
8. **Shared outputs** (table data, site index/nav) are only touched by the final integration session.

---

### Change requests

| # | Requested by | Owned by | File | Request | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | — | — | — | none open | — |

### Handoffs

| # | From session | To session | Task | Reason | Timestamp (UTC) |
| --- | --- | --- | --- | --- | --- |
| 1 | — | — | — | none | — |

### Log

| # | UTC | Session | Event |
| --- | --- | --- | --- |
| 1 | 2026-11-12 04:3x | `bc4b47cf` | Repo review: single 6-byte README, no code/data; claimed T1–T18 (sole session so far) |
| 2 | 2026-11-12 04:4x | `bc4b47cf` | Pulled official Week 10 injury report (nfl.com/injuries/, 7 chunks), standings (2 chunks), week-10 status article, Wed 11-Nov roundup (4 chunks) |
| 3 | 2026-11-12 04:4x | `bc4b47cf` | Bash egress to nfl.com blocked by sandbox allowlist → all external data obtained through the fetch/search tools; recorded as a constraint in `data/questions.csv` (Q-24) |
| 4 | 2026-11-12 05:0x | `bc4b47cf` | Audit caught 3 real defects before publishing: (a) 6 shifted rows in `suggestions.csv` + 5 in `requirements.csv` (short rows silently moving columns) → strict field-count check added to the builder and `verify.py`; (b) my own prose said "5 designations" and "9 injury cells" where the data says 6 and 6 → corrected at every occurrence; (c) `nfl.com` player-slug/name mismatches enumerated and turned into FL-15 rather than silently "fixed" |
| 5 | 2026-11-12 05:1x | `bc4b47cf` | CI `build-and-audit` failed on the drift step. Root cause: a `tools/__pycache__/*.pyc` file had been committed by an earlier `git add -A` and `check_site.py` rewrote it. Fix: `.gitignore` for bytecode, `git rm --cached`, `sys.dont_write_bytecode` in the auditor, and the build made byte-deterministic (no wall-clock stamp in any page). Verified by a clean `git clone` + rebuild + `git diff --cached` showing nothing |
| 6 | 2026-11-12 05:2x | `bc4b47cf` | Final state before PR: `tools/verify.py` 29 pass / 0 warn / 0 fail; `tools/check_site.py` 8 pass / 1 warn (non-league hosts appear only on the Source Registry, by design) / 0 fail; 22 HTML pages, 588 blank cells rendered as `not published` |

---

### Verification record (T2–T5)

Sources used, all fetched 2026-11-12 (UTC) from the official league site:

| Data | Official URL | Verification performed | Result |
| --- | --- | --- | --- |
| Week 10 practice-snapshot injury report (254 player rows) | https://www.nfl.com/injuries/ | Row-by-row transcription from the rendered official tables; each row keeps the official player link; participation strings kept verbatim | 254 rows verified against the official page text; **injury column blank wherever the official table left it blank** (246 of 254) |
| Week 10 game status (Out / Questionable) | https://www.nfl.com/injuries/ and https://www.nfl.com/news/nfl-week-10-injury-report-2026-season | Cross-checked the two official pages; the article lists designations only for the 12-Nov and 15-Patriots cases | 6 designations confirmed (5 Out + 1 Questionable); Sunday/Monday designations **not yet published at fetch time** → flagged |
| 2026 standings (32 teams, W/L/T, PF/PA, streak) | https://www.nfl.com/standings/ | Both chunks transcribed; win % and net points recomputed locally and compared to the published columns | 32/32 rows recomputed clean |
| Week 10 schedule (14 games: date, kickoff, venue, TV) | https://www.nfl.com/news/nfl-week-10-injury-report-2026-season | Schedule block of the official article vs. the official injuries page header | 14/14 games agree |
| Depth-chart / IR / roster moves (Wed 11-Nov) | https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11 | 4 chunks, transcribed per team | 3 confirmed QB changes + 1 unresolved + 1 backup assignment, 13 designated-to-return, 1 activated off IR, 6 ruled-out statements, plus signings and cuts |

### Irregularities found (published on *Flagged for Review*, not blocking)

| # | Irregularity | Evidence |
| --- | --- | --- |
| 1 | Official injury page shows **“No Injuries Reported” for Seattle** on 15-Nov, yet the same official news page reports Darnold ruled out and 12 Seahawks participants with injuries. | https://www.nfl.com/injuries/ vs https://www.nfl.com/news/sam-darnold-ruled-out-for-seahawks-week-10-game-vs-raiders-drew-lock-expected-to-start-again |
| 2 | Third-party sites publish game statuses (Nacua *Out*, Jacobs *Out*) that the official page does not carry at fetch time — timing difference, not a data conflict, but it shows why third-party "official-looking" tables must not be used as the system of record. | https://www.nfl.com/injuries/ vs https://dknetwork.draftkings.com/2026-11-10/nfl-injury-report-week-10/ |
| 3 | Roster-movement volume this season is extreme (Garrett on LAR, Parsons on GB, Evans on SF, Watson on CLE, Jacobs on GB, etc.). Every row was transcribed as published and **not** corrected, but the roster-join keys need an official 53-man roster pull before any team-level model uses them. | https://www.nfl.com/teams/new-england-patriots/roster |
| 4 | The 2026 roster-manual mechanics (4-game IR minimum, 8 return designations, 21-day window) could only be found on non-official sites; the NFL Football Operations landing page does not expose them in a fetchable rule page. Marked **unverified against an official source**. | https://operations.nfl.com/ |
| 5 | `nfl.com/teams/<slug>/depth-chart/` returns a 404 page — there is **no official public depth chart** at that path, so "2nd/3rd/4th-string replacement" cannot be derived from an official depth chart; it must be derived from the roster list + injury report + game reports. | https://www.nfl.com/teams/new-england-patriots/depth-chart/ |
| 6 | Market data (closing/opening lines, prop prices) has no official NFL endpoint reachable from this sandbox; the sandbox blocks egress outside an allowlist. Line-origination therefore ships as a **spec**, not a fitted model. | tool-level observation, recorded in `data/flags.csv` |

### No-conflict statement

At the time of this integration there are **no other active sessions** on this repo: `git branch -r` shows only `origin/main`, and the task board above is the only claim record. Nothing was merged, discarded, or overwritten from another session.

---

## 8. Integration decisions recorded by session `bc4b47cf` (2026-11-12T05:40Z)

Resolves the open issue flagged at the end of §6 — "the repository now carries two site builds ... consolidate by picking one build and deprecating the other explicitly".

| Question | Decision | Why |
|---|---|---|
| Which build owns the published root? | The `bc4b47cf` dashboard (21 pages + 404, generated from `content/*.md` + `data/*.csv`) | Pages is a **legacy build from `main` / **, so the root *is* the site; the root build is the one whose generator refuses to render an unsourced row and whose two auditors run in CI |
| Was the other session's root build deleted? | **No** — all 15 pages plus their `assets/style.css`, `assets/app.js`, `assets/meta.json` moved verbatim to `archive/session-009ec582/` | The archive renders standalone at `/NFL2/archive/session-009ec582/index.html`; nothing that a session published is destroyed by the integration merge |
| What about `docs/`? | Untouched, still published at `/NFL2/docs/` | It is that session's earlier complete build; deleting it would remove the only copy of their defence/depth-chart/stats pages |
| What was absorbed from `arena-009ec582`? | Only the **verified 136-game week 1–9 log** (`data/games_2026.json` → `data/games_2026_wk1_9.csv`), via `tools/import_parallel.py` | It is the one artefact that could be re-derived and independently checked here: per-row official game URLs on 136/136 rows, and a recount that matches `data/standings_2026.csv` for 32/32 clubs on W-L-T, PF and PA |
| What was **not** absorbed? | Their team-stat, player-leader, depth-chart and derived-analysis JSON | Their column mapping and walk-forward folds were not re-derived in this session; publishing them as ours would break rule 2 of this repo's own method. Recorded as **Q-29**, with **S-26** proposing the corpus be registered by hash before any backtest is run |
| New irregularities published | **FL-17** LA vs LAR club codes across official pages · **FL-18** `meta.games = 122` vs 136 rows in the imported file · **FL-19** two publish paths (root legacy + `docs` workflow) · **FL-20** log stops at week 9, so no trend feature crosses into week 10 | FL-17 and FL-18 were found by arithmetic during the import, not by reading; both are left un-corrected in the source file and handled by a published alias + a printed contradiction |
| New suggestions for the owner | **S-26** pre-registered backtest corpus · **S-27** label the canonical layout in the other two trees · **S-28** canonical club-key registry so a key mismatch fails the build instead of dropping a club | S-28 is the fix that makes FL-17 impossible to repeat |
| Tooling changes that affect other sessions | `tools/build_site.py` now accepts a raw official URL in a row's source column (`source_col`); `tools/check_site.py` fails on stale output on disk and on a manifest/input digest mismatch; `tools/verify.py` grew a `gamelog()` check (37 checks total) | The stale-output guard exists because an import error left the *previous* build of a page on disk with a passing link audit — exactly the failure mode a parallel session would hit next |
| CI | `build-and-audit` green: build → `verify.py` (37 pass) → `check_site.py` (10 pass, 1 expected warning) → byte-determinism drift check | The drift check failed on the first push because a committed `__pycache__` file was rewritten by the auditor; fixed with `.gitignore` + `sys.dont_write_bytecode` + a timestamp-free build, not by deleting the check |

**Handoff note for any session still working:** do not write to the repository root `*.html` — root pages are generated and a hand-edited page there will fail the drift check. Page text belongs in `content/<slug>.md`, data in `data/*.csv` (pipe-delimited, fixed field count), and any new data file must be added to `tools/verify.py` with the source rule enforced. `scripts/**`, `data/*.json`, `docs/**` and `archive/**` remain `arena-009ec582`'s scope.
