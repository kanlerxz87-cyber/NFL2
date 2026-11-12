# NFL2 — NFL Intelligence Dashboard

Verified NFL data + originated-lines research system. Live site: **https://kanlerxz87-cyber.github.io/NFL2/**

> Every fact links to an official source (NFL.com / NFL Official Playing Rules). Anything unverified stays blank and flagged — never inferred. Models are labelled **Model only** and are not betting advice.

## Site map (GitHub Pages, served from repo root)

| Page | What it is |
|---|---|
| `index.html` | Dashboard — verified snapshot + navigation |
| `executive-summary.html` | Executive summary (verified facts, system, blockers, recommended path) |
| `standings.html` | 2026 division standings (32 rows, each sourced to NFL.com) |
| `schedule.html` | Week 11 schedule (13 games) + bye teams |
| `injuries.html` | Week 10 injury designations + depth-chart deficiency tracker |
| `teams.html` | All 32 teams by conference/division with official links |
| `lines-lab.html` | Originate your own fair lines (transparent v0 calculator + roadmap) |
| `strategies.html` | Strategy leaderboard framework (gates G1–G7, correlation, skill vs luck) |
| `suggestions.html` | Suggestions board — review and pick the best path before building |
| `questions.html` | Questions / info gaps / answers-needed register (Q-01…Q-12) |
| `flagged.html` | Flagged for Review (F-01…F-10) — unverified items, do not block merge |
| `sources.html` | Official sources + line-by-line verification method |

Data: `data/standings-2026.json`, `data/schedule-week11-2026.json`, `data/injuries-week10-2026.json` (each with source URL + as-of date). Coordination: `COORDINATION.md`.

## Verify it yourself

1. Open any table → click the row's source link (e.g. [NFL.com standings](https://www.nfl.com/standings/division/2026/reg)).
2. Compare each cell. Counts must reconcile: 32 standings rows; 13 Week 11 games + 6 byes = 32 teams.
3. Anything blank/flagged is listed on `flagged.html` — check the linked source there.

## Responsible gambling

Sports betting is legal only in some jurisdictions with age limits (commonly 21+ in the US). Never wager money you cannot afford to lose. US help: call/text **1-800-GAMBLER**. This project provides information and models, not betting advice.

## Repo / Pages

- Branch: `arena/194db560-nfl2` → PR to `main` → GitHub Pages (source `/` on `main`).
- See `COORDINATION.md` for the task board, claims, and PR/merge record.
