# NFL2 — NFL Intelligence Dashboard

Collect, organize, and analyze NFL data from official sources to improve decision-making — and build toward originating our own fair lines with a skill-based strategy leaderboard.

**Live site (GitHub Pages):** `https://kanlerxz87-cyber.github.io/NFL2/`

> Every fact links to an official source (NFL.com / NFL Official Playing Rules). Anything unverified stays blank and flagged — never inferred. Models are labelled **Model only** and are not betting advice.

## Two site builds (parallel sessions — both preserved)

This repo contains **two complementary builds** from parallel sessions, merged without discarding either:

| Build | Location | Pages deploy |
|---|---|---|
| Session `194db560` (PR #1, merged first) | Repo root (`index.html`, `*.html`, `assets/`, `data/standings-2026.json` etc.) | GitHub Pages source `/` on `main` |
| Session `arena-85d79210` (PR #2, this branch) | `docs/` (`docs/index.html`, `docs/*.html`, `docs/assets/`, `data/*_2026.json`, `scripts/validate_data.py`) | `.github/workflows/pages.yml` deploys `docs/` |

**Integration note:** The Pages workflow in this branch deploys `docs/`. If both a `/`-source Pages config and the workflow exist, the workflow takes precedence for the live site. The root build remains in the repo for review; the `docs/` build is the integration target (16 pages incl. defense/stats/depth-charts/methodology + validator). See `COORDINATION.md` conflict log.

## Site map — `docs/` build (integration target)

| Page | What it is |
|---|---|
| [Dashboard](docs/index.html) | Landing page — decision path + data sections |
| [Executive Summary](docs/executive-summary.html) | What we know / don't know / must decide |
| [Suggestions Board](docs/suggestions.html) | S-01…S-12 proposals — review before anything changes |
| [Q&A Register](docs/questions.html) | Q-01…Q-20 questions/informations/answers blocking decisions |
| [Flagged for Review](docs/flagged.html) | F-01…F-09 irregularities with source links |
| [Own Lines](docs/lines.html) | Fair-odds methodology + calculators (Week 11 TBD) |
| [Leaderboard](docs/strategies.html) | Single / parlay / props competition, gates G0–G7 (empty by design) |
| [Standings / Schedule / Injuries / Defense / Stats](docs/standings.html) | Verified tables (see nav) |

## Site map — root build (session 194db560, preserved)

`index.html` (dashboard) · `executive-summary.html` · `standings.html` · `schedule.html` · `injuries.html` · `teams.html` · `lines-lab.html` · `strategies.html` · `suggestions.html` · `questions.html` · `flagged.html` · `sources.html`. Data: `data/standings-2026.json`, `data/schedule-week11-2026.json`, `data/injuries-week10-2026.json`.

## Data — `docs/` build (verified line-by-line vs NFL.com)

- `data/standings_2026.json` — 2026 REG standings (32 rows)
- `data/schedule_week11_2026.json` — Week 11 fixtures (13 games + byes)
- `data/teams.json` — 32 teams / 8 divisions
- `data/player_leaders_2026.json` — passing/rushing/receiving/tackles top-10s
- `data/team_stats_defense_2026.json` — points/yards allowed (32 teams)
- `data/injuries_2026-11-11.json` — Nov 11 snapshot (Week 10 — stale for Week 11, see F-02)
- `data/suggestions.json`, `data/questions.json`, `data/strategies.json` — governance/frameworks

Validate: `python3 scripts/validate_data.py`

## Rules (non-negotiable)

1. Every factual row has a source link to an official site. Unconfirmed = blank + flagged. Never infer.
2. No suggestion is implemented until marked Accepted on the Suggestions board.
3. No fair line or strategy goes “live” until its Q&A blockers clear and gates pass.
4. Coordination via `COORDINATION.md` (task board, claims, verification log).

## Responsible gambling

Sports betting is legal only in some jurisdictions with age limits (commonly 21+ in the US). Never wager money you cannot afford to lose. US help: call/text **1-800-GAMBLER** or **1-800-MY-RESET** (1-800-522-4700), [ncpgambling.org](https://www.ncpgambling.org/ncpg/). This project provides information and models, not betting advice.
