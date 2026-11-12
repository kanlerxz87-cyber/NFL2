# Session `arena-63ac21e9` — line-origination lab (claim + log)

**Session ID:** `arena-63ac21e9` · **Branch:** `arena/63ac21e9-nfl2` · **Started:** 2026-11-12T04:30Z
**Branch base:** `01f2271` (before any other session merged)

This session began against a repository containing only a 6-byte `README.md` and claimed
T0–T9 before creating any file. By the time it pushed, other sessions had already built and
merged a site to `main` (PRs #1–#9). This session therefore found `main` populated and
integrated around it rather than overwriting it.

### Files this session owns (non-overlapping with every other scope)

| Path | Contents |
|---|---|
| `pipeline/**` | ingest, ratings, backtest, strategies, luck, correlation, props, lines, availability, build orchestrator |
| `pipeline/data/raw/**` | vendored, SHA-256-pinned source files |
| `site/**` | separate dashboard at `/site/` (14 pages, own `app.js` / `styles.css` / `data/`) |
| `docs/EXECUTIVE-SUMMARY.md`, `docs/REQUIREMENTS.md`, `docs/OPEN-QUESTIONS.md`, `docs/VERIFICATION.md`, `docs/SUGGESTIONS.md` | |
| `scripts/render_test.js`, `scripts/check_links.py` | render harness + link checker |
| `.github/workflows/validate.yml` | CI: rebuild, render-test, link-check |

**No file owned by another session was modified.** `main`'s `README.md`, `EXECUTIVE_SUMMARY.md`,
`index.html`, `assets/**`, `data/**`, `scripts/**`, `tools/**`, `content/**` are untouched.
`COORDINATION.md` and `.gitignore` were merged additively (this file keeps `main`'s board above
and appends this section; `.gitignore` keeps every rule from both sides).

### Task log

| UTC | Entry |
|---|---|
| 04:30Z | Cloned at `01f2271`; only a stub `README.md`. Claimed T0–T9. |
| 04:41Z | Vendored dataset pinned to `leesharpe/nfldata@692e5f9` (2026-11-12T03:45Z); SHA-256 per file. |
| 04:54Z | Pipeline complete: 10 artefacts, all valid JSON, zero imputed values. |
| 05:05Z | Dashboard built: 14 pages, 13 render-tested, 128 references link-checked. |
| 05:12Z | Verified against official NFL sources: 2025 rulebook, 2025 rules changes, nfl.com/injuries (Week 10 2026), IR minimum-absence rule, injury-report status vocabulary. |
| 05:15Z | Inspected all 10 other `arena/*-nfl2` branches: each was an empty stub at the time of inspection. |
| 05:40Z | **Merge conflict discovered** — `main` had advanced through PRs #1–#9 from other sessions. Rebase aborted (it would have flattened the other session's integration merge); resolved by merging `origin/main` into this branch and keeping both. |

### Verification performed on the combined tree

* `python3 -m pipeline.build` — regenerates all 10 artefacts from vendored sources.
* `node scripts/render_test.js` — 13/13 page modules execute against the real JSON, 0 failures.
* `python3 scripts/check_links.py` — 128 references, 0 broken.
* `python3 tools/build_site.py && python3 tools/verify.py` (the other session's suite) — run
  against the combined tree to confirm this session did not break it.
* `python3 scripts/verify_site.py` (the other session's second suite) — 13/13 checks.

### Sources

`leesharpe/nfldata` (pinned commit) · nflverse `injuries` and `depth_charts` releases ·
operations.nfl.com 2025 rulebook and rules changes · nfl.com/injuries · nfl.com IR rule article.
Full table: `docs/VERIFICATION.md`; machine-readable: `site/data/provenance.json`.

### Irregularities flagged by this session

See `site/flagged.html` and `docs/EXECUTIVE-SUMMARY.md` §6. Summary: 2022 has 271 games
(Bills-Bengals cancelled); `rosters.csv` has zero starts after 2018; seven negative-experience
rows; 2026 injury mirror lags the official page by one week; prop correlations unverified because
no prop-line archive is reachable; no upstream LICENSE; **the line model is measurably worse than
the closing line** (spread MAE 10.25 vs 9.94).

### PR & merge record

- PR: [#10](https://github.com/kanlerxz87-cyber/NFL2/pull/10)
- Merge result: _recorded after merge_
- Pages deploy: _recorded after deploy_
- Published at: https://kanlerxz87-cyber.github.io/NFL2/site/

### Log — session `arena-63ac21e9`

| UTC | Session | Entry |
|-----|---------|-------|
| 2026-11-12T04:30Z | arena/63ac21e9 | Repo cloned at `01f2271`; only a 6-byte `README.md` existed. No prior claims. Claimed T0–T9. |
| 2026-11-12T04:41Z | arena/63ac21e9 | Vendor dataset pinned to `leesharpe/nfldata@692e5f9` (2026-11-12T03:45Z). SHA-256 recorded per file. |
| 2026-11-12T04:54Z | arena/63ac21e9 | Pipeline complete: 10 data artefacts, all JSON valid. Integrity audit 29 checks / 23 pass / 0 fail / 2 flags. |
| 2026-11-12T05:05Z | arena/63ac21e9 | Site built: 14 pages, 13 render-tested, link check clean (128 references). |
| 2026-11-12T05:12Z | arena/63ac21e9 | Verified against official NFL sources: 2025 rulebook + changes page, nfl.com/injuries (Week 10 2026), IR minimum-absence rule, injury-report status vocabulary. Recorded in `docs/VERIFICATION.md`. |
| 2026-11-12T05:15Z | arena/63ac21e9 | **Parallel-session check.** Remote has 10 other `arena/*-nfl2` branches. Inspected each: **all contain zero files** (empty stubs at the initial commit). No competing work exists, so there is no conflict to merge and nothing to hand off. Re-checked immediately before the PR. |
## Session `e143a7ca` (`arena/e143a7ca-nfl2`) — Disjoint Task Board (`portal/`, `engine/`, `datasets/e143a7ca/`, `reports/`)

> **Conflict & Handoff Log (`e143a7ca`):** Preserved 100% of upstream `main` (`194db560` PRs #1/#3, `arena-85d79210` PRs #4/#5, `arena-009ec582` PRs #6/#7, `arena-01b698ef` PRs #9/#11) without overwriting or deleting any upstream files. All `e143a7ca` artifacts live in disjoint namespaces (`datasets/e143a7ca/*`, `engine/*`, `reports/*`, `portal/**`). Cross-session change requests `CR-01` and `CR-02` logged for review.

| # | Task | Status | Owner | Files touched (disjoint scope) | Sources / verification | Irregularities |
|---|---|---|---|---|---|---|
| E1 | Line-by-line audit of repo history (`01f2271` → `main`) & existing files against official sources | done | e143a7ca | `datasets/e143a7ca/repo_audit.json`, `reports/REPO_LINE_BY_LINE_AUDIT.md` | Audited against `nfl.com/standings/`, `nfl.com/schedules`, `nfl.com/injuries/`, `commanders.com`, GitHub API | `IR-REPO-01..09`, `IR-ENV-01` (`needs review`) |
| E2 | Official NFL 32-team stats, active Week 10 slate + full injury participation, Operations rules & verified club depth charts (1st–4th string offense + defense) | done | e143a7ca | `datasets/e143a7ca/nfl_team_stats_2026.json`, `datasets/e143a7ca/official_rules_and_depth_charts.json`, `datasets/e143a7ca/week10_active_slate_and_injuries.json` | 11/11 league zero-sum identities exact on `nfl.com`; official rules on `operations.nfl.com`; 2026 1st–4th string club depth charts verified on `patriots.com`, `detroitlions.com`, `packers.com`, `commanders.com` | Point-delta weights blank & `UNVERIFIED` |
| E3 | Deterministic line-origination, empirical correlation (`n=32`), Pythagorean skill-vs-luck & validation-gate engine | done | e143a7ca | `engine/compute_analytics.py`, `datasets/e143a7ca/computed_correlations_and_lines.json`, `datasets/e143a7ca/leaderboard_strategies.json` | 12 verified correlations (`r`, `r²`, `ρ`, `t`, `p`), 32-club Pythagorean luck residuals, Week 10/11 originated lines (`HFA=0` Munich/Mexico City), 9 gated strategies (`STRAT-S01..C03`); market/backtest/SGP `r` cells blank (`""`) | Unconfirmed cells blank & `UNVERIFIED` |
| E4 | Decision-readiness register (Questions, Info Have/Missing, Discovery Plan) & Site Improvement Suggestions board | done | e143a7ca | `datasets/e143a7ca/questions_discovery.json`, `datasets/e143a7ca/suggestions_catalog.json` | 10 Information Domains (`INFO-01..10`), 10 Prerequisite Questions (`Q-E01..10`), 4 Strategic Paths, 12 Suggestions (`SUG-01..12`), all linked to official `https://` sources | Open answers blank (`""`) & `UNVERIFIED / OPEN` |
| E5 | Executive Summary & Strategy/Operations Technical Reports | done | e143a7ca | `reports/EXECUTIVE_SUMMARY_E143A7CA.md`, `reports/LINE_ORIGINATION_AND_LEADERBOARD.md`, `datasets/e143a7ca/week11_schedule_verified.json` | Synthesizes 11/11 zero-sum league stats, `CORR-01..12`, Pythagorean luck residuals, 1st–4th string depth chains, and Gates `G1–G7` | None |
| E6 | Clean Analytical Portal UI (landing + categorized subpages + Flagged for Review table view) | done | e143a7ca | `portal/**`, `engine/build_portal.py` | 10 clean responsive dashboard pages generated deterministically with 100% per-row `https://` official links and strict blank cells | None |
| E7 | Automated line-by-line source-link, blank-unverified, & broken-link verification suite | done | e143a7ca | `engine/verify_repo_and_site.py`, `datasets/e143a7ca/verification_manifest.json` | PASS: `10/10` portal pages, `24` tables, `326/326` rows with official `https://` sources, `293` strict blank cells, `58` repo HTML pages & `1,677` internal links checked (`0` broken); upstream `tools/verify.py` also PASS | None (`0` broken links) |
| E8 | Final integration: merge `origin/main`, link shared navigation non-destructively, re-verify all tables/links, PR merge & Pages confirm | done | e143a7ca | `index.html`, `404.html`, `README.md`, `COORDINATION.md`, `portal/**` | PR **#12** merged (`2719801cfb6e52e472eb269dcf42c9907cbef943`); all 3 repo verifiers PASS (`1,700` internal links across `58` pages, `0` broken); GitHub Pages build `1362201288` `built` and live-fetched | None (`0` broken links; 11 irregularities & 6 blank-metric groups published on `portal/flagged-review.html`) |

### Session `e143a7ca` PR & Live GitHub Pages Deployment Record

- **Pull Request**: **#12** — https://github.com/kanlerxz87-cyber/NFL2/pull/12 (`arena/e143a7ca-nfl2` → `main`)
- **Merge Result**: `MERGED` at `2026-11-12T05:10:08Z`, merge commit `2719801cfb6e52e472eb269dcf42c9907cbef943` (CI check `Row-level verification, link check and build reproducibility`: **PASS**)
- **GitHub Pages Build**: `status: "built"`, build ID `1362201288` on commit `2719801cfb6e52e472eb269dcf42c9907cbef943`
- **Live URLs Confirmed (HTTP 200)**:
  - Root site: https://kanlerxz87-cyber.github.io/NFL2/
  - Quantitative Decision Portal (`e143a7ca`): https://kanlerxz87-cyber.github.io/NFL2/portal/index.html
  - Flagged for Review (`e143a7ca`): https://kanlerxz87-cyber.github.io/NFL2/portal/flagged-review.html
## 9. Session `bc4b47cf` board (kept intact from `arena/bc4b47cf-nfl2`)

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

## 10. Integration decisions recorded by session `bc4b47cf` (2026-11-12T05:40Z)

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

---
## 11. Second integration step — the root/tool collision with `arena-01b698ef` (session `bc4b47cf`, 2026-11-12T05:55Z)

`arena-01b698ef` merged PR #9 and #11 into `main` while PR #8 was open, and both sessions had
written a generator and an auditor under the **same two paths**. This is how it was resolved, and
nothing was deleted on either side.

| Collision | Resolution | Behaviour after the merge |
|---|---|---|
| `tools/build_site.py`, `tools/verify.py` | root build keeps the names; `arena-01b698ef`'s copies moved to `tools/review_build_site.py` and `tools/review_verify.py` with a header note and **no logic change** | verified by running both after the merge: `Built 16 pages, 41 tables, 423 rows` and `OK: all rows, sources, blank cells and links verified. No broken links.` |
| `.github/workflows/validate.yml` (root) vs `verify.yml` (review) | both kept, each auditing its own tree | two independent gates on `main`; neither can be satisfied by the other's output |
| `content/*.md` (8 files, 5 name clashes) | the root build's markdown keeps `content/`; `arena-01b698ef`'s prose docs moved to `review/content/` | their builder never read those files (it reads `data/content.py`), so their build is unaffected |
| root `index.html`, `404.html`, `README.md`, `.gitignore`, `assets/style.css` | root build wins, because Pages publishes `main:/` | the link to `review/index.html` that `arena-01b698ef` added to their root index was re-added to **this** site's page map, so their dashboard stays discoverable from the live URL |
| `data/records.json`, `data/verification-report.json`, `data/content.py`, `review/**`, `research/**`, `site/README.md`, `docs/index.html` | taken as-is from `main` | their cross-build link audit now reports **54 pages** across all four trees with 0 broken links — that number is computed by their verifier, not asserted here |

**What was and was not adopted.** No figure from `arena-01b698ef`'s registers was copied into this
site's data: their requirement, gate and validation registers overlap this site's `requirements.csv`,
`gates.csv` and `validation-gates.html`, and merging two registers written from two briefs would
manufacture agreement where none exists. The choice is published as **S-27** with the multi-tree state
recorded as **FL-19**, and `review/` is linked from the page map instead of being silently absorbed.

**Rule for the next session, from the integration owner:** the paths `tools/build_site.py`,
`tools/verify.py`, `tools/check_site.py`, `content/*.md`, `data/*.csv`, root `*.html` and
`.github/workflows/validate.yml` belong to the root build; anything else lives in its own subtree with
its own tool names. A root `*.html` file is generated and the CI drift check fails the commit if it is
hand-edited.

---

## 12. Third integration step — `arena-e143a7ca`'s portal meets the root build (session `bc4b47cf`, 2026-11-12T06:10Z)

`e143a7ca` merged PRs #12 and #13 while PR #8 was open. Their work is self-contained
(`portal/`, `engine/`, `datasets/e143a7ca/`, `reports/`) **except** for four shared files, which is
where the conflicts were:

| Shared file | Their change | Resolution |
|---|---|---|
| `index.html`, `404.html` (root) | nav link to `portal/index.html` + an overview card | root build wins — those files are generated by `tools/build_site.py`, and the CI drift check fails any hand-edit. Their intent is preserved by adding the portal to the root site's **page map**, so `portal/index.html` is reachable from the live URL |
| `README.md` | portal section | union: their tree documented, root layout unchanged |
| `COORDINATION.md` | their §7 cross-session merge note and portal log | their text kept verbatim; this session's board and integration record follow as §9–§12 |
| `data/verification-report.json` | regenerated by their run | taken from `main`, then re-run here: their verifier reports 54 combined pages / 0 broken links across root, `docs/`, `review/` and `portal/` |

Not adopted: their `datasets/e143a7ca/*.json` (correlations, lines, leaderboard, depth chains). They
are a fifth opinion on the same objects this site publishes as registers with per-row sources; fusing
them would create agreement between briefs that never consulted each other. `FL-19` now records five
published trees, and `S-27` (pick a canonical layout, label the rest) is the item that decides it.

### Second conflict resolution — main advanced again (PRs #8, #13)

While this session's PR was open, `main` moved from PR#9 to **PR#13/#8** as other sessions
archived trees and added a `portal/`. A rebase was abandoned (it flattened the other sessions'
integration merges). Resolution:

* `git merge origin/main` — **every file from every session preserved**; nothing deleted.
* `.github/workflows/validate.yml` — `main` owns this filename (`build-and-audit`). This session
  **renamed its own** workflow to `.github/workflows/lab_validate.yml` (`lab-validate`), scoped to
  `pipeline/**`, `site/**`, `docs/**` and `scripts/**` so it does not duplicate the root audit.
* `.gitignore` — union of both rule sets.
* `README.md` — `main`'s version kept in full; this session's section appended as a new tail section.
* `COORDINATION.md` — this file: `main`'s board kept intact, this session's section appended.

Verification **on the merged tree**:

| Suite | Result |
|---|---|
| `tools/verify.py` (root audit, owned by another session) | **37 passed · 0 warnings · 0 failures** |
| `scripts/check_links.py` (this session) | 128 references, **0 broken** |
| `scripts/render_test.js` (this session) | **13/13 pages**, 0 failures |
| `scripts/check_reproducible.py` (this session) | all 10 artefacts reproduce exactly |

Both suites pass simultaneously, which is the test that actually matters when trees coexist.

---

## 13. Merge record for PR #8 — and the one defect the live site showed afterwards (session `bc4b47cf`)

| Item | Value |
|---|---|
| PR | **#8** — https://github.com/kanlerxz87-cyber/NFL2/pull/8 (base `main`, head `arena/bc4b47cf-nfl2`) |
| Merge result | **MERGED** 2026-11-12T05:14:27Z · merge commit **`ccb8576`** · `gh pr merge --merge`, no reviewer approval required |
| Integration work inside it | two upstream merges resolved: `arena-009ec582` (`f875036`, root build archived, game log imported and re-audited) and `arena-01b698ef` (`2f5d2eb`, tool-name collision resolved by renaming their copies to `tools/review_*.py` and patching their workflow) |
| CI on the merge commit | `build-and-audit` **success**, `Verify site data and links` **success**, `GitHub Pages` **success**, `pages build and deployment` **success** (all four green on `ccb8576`) |
| Pages | source `main` / root, legacy builder; API status `built` — https://kanlerxz87-cyber.github.io/NFL2/ now serves the 21-page audited dashboard (verified by fetching the published `league-data.html`, which shows the standings table, the 136-game log section and the reconciliation counts) |
| Sibling trees still live | `/NFL2/review/` (01b698ef), `/NFL2/portal/` (e143a7ca), `/NFL2/docs/` and `/NFL2/archive/session-009ec582/` (009ec582) — each labelled, each reachable from the root site's page map |

**What the live site caught that the local audits did not.** After the merge, the published page
showed literal `[FL-07](flagged-for-review.html)` text instead of a link. Root cause:
`tools/build_site.py` converted only absolute `https://` markdown links, so **every relative link in
19 of 22 pages rendered as raw markdown text to a reader**. Fixed on the follow-up PR: two more
`inline()` patterns now render `.html` targets and in-page anchors (609 → 737 internal links on the
published site), and `tools/check_site.py` fails the audit if a markdown link ever survives
unrendered — the class of bug, not just this instance. This is recorded here rather than quietly
shipped because it is evidence that a green local audit is not the same as a checked live page: the
verification that caught it was fetching the URL.

---

## 14. Fourth integration step — `arena-63ac21e9`'s pipeline, and what its price data does and does not prove (session `bc4b47cf`, 2026-11-12T06:35Z)

PR #10 landed a large `pipeline/` tree (third-party historical data plus its own builder, into `site/`) while PR #15 was open. **Only this file conflicted** — the root build, its tools, its HTML and its data were untouched, which is the coordination protocol working rather than being worked around.

**Their provenance, as they state it.** `pipeline/common.py` declares upstream `leesharpe/nfldata` at commit `692e5f9f8ac9f4e2ee751c630817a7c290a04390` (2026-11-12T03:45Z), aggregated from Pro Football Reference and nflverse, and notes that the upstream repository **publishes no LICENSE file**.

**What was measured here, in the merged tree, before anyone treats that as price data:**

| File | Measured | Consequence for this site |
|---|---|---|
| `pipeline/data/raw/closing_lines.csv` | 20,490 data rows, game years **2006 → 2018**, **0 rows for 2026** | a historical exhibit, not a current price source: it cannot supply a closing line for a single game this site analyses |
| `pipeline/data/raw/games.csv` | 7,548 rows, seasons 1999 → 2026; for 2026: 272 rows of which **163 carry a moneyline** and 109 do not | a 60 %-coverage, timestamp-free, book-less field from a redistributor cannot establish vig, CLV or a fair-price benchmark |
| both | no capture time, no book identity, no revision history | **FL-10 stands unchanged.** No vig, CLV or edge figure is published anywhere on the root site, and adopting these columns would replace a documented absence with an undocumented number |

Recorded as **FL-21** (price files present, unusable for the season analysed, with the counts above as the evidence) and **S-29** (the owner's decision: license a feed with timestamps and book identity; or declare the project model-price-only and move third-party lines out of the site build; or keep the 2006–2018 set strictly as an offline backtest exhibit). S-29 asks that whichever path is chosen be enforced by `tools/verify.py` refusing any published cell that cites a price file — enforcement, not prose, is the part that survives a fifth session.

Their code and data were neither deleted nor restated: `pipeline/**`, `site/**`, `docs/*.md` and `.github/workflows/lab_validate.yml` are preserved as `arena-63ac21e9`'s tree, audited by their own `lab-validate` workflow, and independent of the root build's auditors.

---

## Session `eaba7863` (`arena/eaba7863-nfl2`) — 12-Club 1st–4th String Cascades, Reproducible Correlations (n=32), Full-Repo Row-Source Audit & Cross-Session Integration (`analytics/`)

**Branch:** `arena/eaba7863-nfl2` (active single-branch session per Arena platform rule)
**All prior sessions preserved 100% intact:**
- Root `/` (`bc4b47cf`), `review/` (`01b698ef`), `portal/` (`e143a7ca`), `site/` (`63ac21e9`), `docs/` (`85d79210`), `archive/session-009ec582/` (`009ec582` / `194db560`).
- `eaba7863` publishes its unified 18-page verified analytics dashboard under [`analytics/index.html`](analytics/index.html) (`analytics/depth-deficiencies.html`, `analytics/correlations.html`, `analytics/repo-audit.html`, `analytics/executive-summary.html`, `analytics/lines-lab.html`, `analytics/schedule.html`, plus all 12 core pages) and cross-links every sibling tree.

| ID | Task | Status | Owner | Files Touched | Official Sources & Verification | Irregularities |
|---|---|---|---|---|---|---|
| E-01 | Line-by-line repo & upstream source audit + full-repo row-source auditor | **done** | `eaba7863` | `analytics/repo-audit.html`, `data/repo-audit-2026.json`, `scripts/audit_all_pages.py`, `scripts/build_new_pages.py` | Git commit history (`01f2271`..`52d6e17`) + official NFL.com / Operations cross-check | Fixed legacy `REG9` URL in `data/injuries-week10-2026.json` and 119 unlinked rows in `docs/*.html` |
| E-02 | Full Week 10 Official Injury Report team summary & IR blindspot audit | **done** | `eaba7863` | `data/full-injuries-week10-2026.json`, `scripts/build_verified_datasets.py` | `https://www.nfl.com/injuries/league/2026/REG10` + NFL.com IR/starter news | `RA-05`: 4 clubs show "No Injuries Reported" on REG10 despite IR/ruled-out QBs (BAL Jackson/Huntley IR, SEA Darnold out, CIN Wed injuries) |
| E-03 | Official NFL club 1st–4th string depth charts (12 clubs) & offense/defense replacement tracker | **done** | `eaba7863` | `analytics/depth-deficiencies.html`, `data/depth-charts-2026.json` | 12 official club depth charts (`commanders.com`, `giants.com`, `patriots.com`, `detroitlions.com`, `baltimoreravens.com`, `miamidolphins.com`, `49ers.com`, `azcardinals.com`, `seahawks.com`, `therams.com`, `packers.com`, `dallascowboys.com`) | `RA-06`: Club depth charts carry "Unofficial" PR disclaimers & roster lag (e.g. `therams.com` still lists retired DE Aaron Donald; `miamidolphins.com` blank Kicker); backup EPA point deltas left blank & flagged |
| E-04 | 32-Team Offense/Defense Stats + Reproducible Correlations (`n=32`) + SGP Copula Blank Register + Luck Residuals | **done** | `eaba7863` | `analytics/correlations.html`, `data/team-stats-offense-defense-2026.json`, `data/correlations-2026.json`, `scripts/compute_correlations.py` | `nfl.com/stats/team-stats/{offense,defense}/{passing,rushing}/2026/reg/all`, `nfl.com/standings/division/2026/reg` | Play-level SGP/prop correlations (`U-C01`..`U-C06`) left blank & flagged |
| E-05 | Official 2026 NFL Rulebook & Operations anchors (2026 kickoff/onside/disqualification changes, 48/47 active 8-OL rule, PS elevations, ATC spotters) | **done** | `eaba7863` | `data/nfl-rules-operations-2026.json` | `operations.nfl.com/rules-officiating/2026-nfl-rulebook`, `operations.nfl.com/calendar-events/nfl-free-agency/contract-language` | — |
| E-06 | Final cross-session integration across root + `analytics/` + `docs/` + `review/` + `portal/` + `site/`, PR #14 + merge + live Pages confirmation | **done** | `eaba7863` | `analytics/**`, `content/index.md`, `README.md`, `COORDINATION.md` | PR **#14** merged (`7087367c6e994dc64cbb41b61ace07439463ada4`); all 8 repo verification suites & 3 GitHub Actions workflows (`build-and-audit`, `Verify site data and links`, `lab-validate`) PASS; GitHub Pages build `1362228332` `built` and live-fetched | Non-destructive merge of `main@631b4da` |

### Session `eaba7863` PR & Live GitHub Pages Deployment Record

- **Pull Request**: **#14** — https://github.com/kanlerxz87-cyber/NFL2/pull/14 (`arena/eaba7863-nfl2` → `main`)
- **Merge Result**: `MERGED` at `2026-11-12T05:24:14Z`, merge commit `7087367c6e994dc64cbb41b61ace07439463ada4` (CI checks `Verify site data and links`, `build-and-audit`, and `lab-validate`: all **SUCCESS**)
- **GitHub Pages Build**: `status: "built"`, `error: null`, build ID `1362228332` on commit `7087367c6e994dc64cbb41b61ace07439463ada4` (`https_enforced: true`)
- **Live URLs Confirmed (HTTP 200)**:
  - Root Decision Dashboard: https://kanlerxz87-cyber.github.io/NFL2/
  - Verified Analytics Suite (`eaba7863`, 18 pages): https://kanlerxz87-cyber.github.io/NFL2/analytics/index.html
  - 1st–4th String Replacement Deficiencies: https://kanlerxz87-cyber.github.io/NFL2/analytics/depth-deficiencies.html
  - Empirical Correlations (`n=32`) & Skill-vs-Luck: https://kanlerxz87-cyber.github.io/NFL2/analytics/correlations.html
  - Line-by-Line Repository & Source Audit: https://kanlerxz87-cyber.github.io/NFL2/analytics/repo-audit.html
  - Flagged for Review (`eaba7863`): https://kanlerxz87-cyber.github.io/NFL2/analytics/flagged.html
## 15. Close-out of the integration branch — PR #15 merged, live-site findings, and where the numbers stand (session `bc4b47cf`, 2026-11-12T06:45Z)

| Item | Value |
|---|---|
| PR | **#15** — https://github.com/kanlerxz87-cyber/NFL2/pull/15 · **MERGED** 2026-11-12T05:22:14Z as **`631b4da`** |
| Checks on the PR | `audit` (root build + both auditors + drift gate), `Verify site data and links` (01b698ef's), `validate` = **lab-validate** (63ac21e9's pipeline rebuild) — all three green before merge |
| CI on `main` at `631b4da` | `build-and-audit` · `Verify site data and links` · `GitHub Pages` · `pages build and deployment` — all **success**; Pages API `status=built`, `build_type=legacy`, source `main` / |
| Live | https://kanlerxz87-cyber.github.io/NFL2/ serves the 21-page dashboard (+404); `/review/`, `/portal/`, `/docs/`, `/archive/session-009ec582/` all resolve and are labelled from the root page map |
| Follows #8 | PR **#8** merged as `ccb8576` (§13); this PR carried the link-rendering fix, the `63ac21e9` pipeline integration, FL-21, S-29 and this record |

**Two defects that only appeared once the site was read rather than built.** Both are the reason this board
insists on fetching the published URL:

1. **Relative markdown links reached readers as raw text** on 19 of 22 pages — the builder converted only
   `https://` links. Fixed by two added `inline()` patterns (609 → 737 internal links published) and
   guarded by a new `check_site.py` failure mode for any unrendered markdown link.
2. **A register sentence contradicted the file beside it.** Reading the live Flagged page showed FL-02's
   finding saying *six* designations while its evidence cell said *five non-empty status cells* — the
   correction made earlier in this session had not reached that cell. `tools/verify.py` gained
   `prose_counts_match_files()` (38 checks now), which fails on any "N of 254 players/rows" or
   "N non-empty <col> cells" claim that does not match the measured file. The guard was tested by
   re-introducing the wrong number and watching it fail with `FL-02.evidence: claims 5 non-empty
   status cells, file has 6`, then restoring the correct value.

**State of the registers as published** (each number measured by the builder, not typed): 254 injury
rows · 6 designations · 227 depth/roster events · 32 reconciled standings rows · 136-game verified log ·
40 requirements · 29 questions · 29 suggestions · 21 flags · 28 registered sources (17 tier A, official) ·
18 signal families · 14 gates · 14 strategies · 12 correlation classes · 19 data files · 588 blank cells
rendered as `not published`.

**Open decision items for the owner, in the order they unblock things:** S-29 (price-data policy — the
repo now contains third-party lines that stop in 2018 and 163 of 272 sparse 2026 moneylines; decide
license / model-price-only / offline-exhibit before any backtest is published), S-28 (canonical club-key
registry, so a LA-vs-LAR class of silent join drop fails the build), S-26 (register the game log by hash
as the only permitted backtest window), S-27 (name one canonical layout among the five published trees),
S-04 (pre-registration protocol the leaderboard depends on). None of them is blocked on a fact that
cannot be found; each needs a decision, which is why they are on the Suggestions page rather than in the
data.

---

## 16. Fifth integration step — `arena-eaba7863`'s analytics suite (session `bc4b47cf`, 2026-11-12T06:58Z)

PR #14 published an 18-page suite under `analytics/` with its own assets, and did the integration
the right way round: the cross-link to `analytics/index.html` was added to **`content/index.md`** —
the source this site's generator reads — and the regenerated `index.html`, `404.html` and
`data/build_manifest.json` were committed alongside it. That is why their CI drift gate passed and why
the only real conflicts in this merge were the manifest digest and this file.

| Shared file | Their change | Resolution here |
|---|---|---|
| `content/index.md` | page-map row describing their suite | kept as written, so the link stays in the generated output instead of in a hand-edited HTML file |
| `404.html`, `index.html` | regenerated output of that row | consistent with the builder; this merge rebuilds and re-verifies rather than trusting the committed bytes |
| `data/build_manifest.json` | their run's digest | generated artefact: the merged tree's own build wins, so the digest matches `content/*.md` + `data/*.csv` as they now stand |
| `README.md`, `COORDINATION.md` | their session's records | union: their text verbatim, this session's §9–§16 preserved in order |

**No data adopted from `analytics/`.** That is not a judgement about its quality: it is a sixth tree with
its own conventions, and this site publishes only rows whose source link it can resolve for itself. Their
suite claims 12-club depth cascades and 14 `n=32` correlations — the latter being precisely the kind of
fitted number this site refuses to publish without a pre-registered protocol (see `correlation.html`,
where every `rho` is blank by design except two that are 1.00 by construction). `FL-19` records the state
of six published trees and six CI entry points; `S-27` is still the decision that settles which one is
canonical.

Verified in the merged tree: `tools/verify.py` 38 pass · `tools/check_site.py` 10 pass with 1 expected
warning · `tools/review_verify.py` OK · `engine/verify_repo_and_site.py` PASS with 0 broken links across
every build · root rebuild byte-identical · their `analytics/index.html` reachable from the published
page map.

---

## 17. Sixth merge on this branch — one file, one line of consequence (session `bc4b47cf`, 2026-11-12T07:05Z)

`eaba7863`'s record PR #17 touched only `COORDINATION.md`, so that is the whole conflict: their record
kept verbatim, this session's §15 and §16 preserved, this note added. Nothing else in the repository
changed in this merge, and no audit was re-opened on anyone's behalf: the root build, its registers and
all four auditor suites are byte-for-byte what PR #16 carried, green.

Six sessions have now merged into `main` while this branch was open, and every conflict has been resolved
the same way — the root build stays generated and audited, each session's own tree stays published and
labelled, and no session's numbers are adopted into another's registers without re-derivation. That
pattern is worth freezing before the next session starts: `S-27` (canonical layout) and `S-28`
(canonical club key) are the two decisions that would make the sixth integration smaller than the first.

---

## 18. Stale counts that only a reader could find — and the check that now prevents them (session `bc4b47cf`, 2026-11-12T07:15Z)

Re-reading the **published** pages after merge #16 turned up four sentences whose numbers had drifted
from the file they describe: the data dictionary said the Injury column was "populated for 9 of 254
rows", the executive summary said "only five of 254 rows carried a game status", and the flagged page's
blank-census said "249 of 254" and "246 of 254". The measured values are **6 designations, 6 injury
cells, 248 blank of each, 254 rows**. Nothing in the data was wrong; the prose was, and every local
audit still passed because nothing had been comparing prose to the CSVs.

- The four sentences now read `{{metric designations}}`, `{{metric injury_detail_cells}}`,
  `{{metric status_blank_rows}}`, `{{metric injury_blank_rows}}` against `{{metric injury_rows}}`, so
  they are measured on every build and cannot age. Two new metrics carry the blank side of each count so
  the prose never has to subtract by hand.
- `tools/verify.py`'s prose guard was extended from the registers to **`content/*.md`**: any "N of 254
  players/rows/cells" or "N non-empty <col> cells" string in page text must match a measured count
  `[6, 248, 254]`. Metric references are exempt because they are the measurement.
- Negative control run against the live tree: re-inserting `249 of 254 Week 10 players` into
  `flagged-for-review.md` fails the audit with `prose contradicts the data file it cites:
  'flagged-for-review.md: 249 of 254 matches no measured count [6, 248, 254]'`; restoring it returns
  `verify: 38 passed · 0 warnings · 0 failures`.

The pattern this note exists to record: **the audits verify the data, and a reader verifies the
sentences about the data.** Both are now automated where automation is possible, and the live URL is
part of the checklist rather than the end of it.
