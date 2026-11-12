# Line-by-Line Repository Audit (`S53-01` — Session `arena-53126614`)

**Audited repository:** `https://github.com/kanlerxz87-cyber/NFL2`  
**Audited commit on `main`:** `f64078fc` (incorporating Session `194db560` PR #1/#3 and Session `arena-85d79210` PR #4/#5)  
**Audit date (UTC):** `2026-11-12`  
**Machine-readable copy:** `data/s53126614_repo_audit.json`  
**Published dashboard page:** `repo-audit.html`

## 1. Scope & Verification Protocol

Every JSON file and HTML table on `main` was checked cell-by-cell against live fetches of official NFL sources:
- [NFL.com 2026 Division Standings](https://www.nfl.com/standings/division/2026/reg)
- [NFL.com Week 11 Schedule Change (Nov 9, 2026)](https://www.nfl.com/news/week-11-schedule-change)
- [NFL.com 2026 Schedule Release: Every Team's Bye Week](https://www.nfl.com/news/2026-nfl-schedule-release-every-team-bye-week)
- [NFL.com Official Week 10 Injury Report (`REG10`)](https://www.nfl.com/injuries/league/2026/REG10) & [Week 9 Injury Report (`REG9`)](https://www.nfl.com/injuries/league/2026/REG9)
- [NFL.com Week 10 Injury Summary Article](https://www.nfl.com/news/nfl-week-10-injury-report-2026-season) & [Wednesday Nov 11 News Roundup](https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11)
- [NFL.com 2026 Team Offense Passing](https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all), [Offense Rushing](https://www.nfl.com/stats/team-stats/offense/rushing/2026/reg/all), [Defense Passing](https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all), and [Defense Rushing](https://www.nfl.com/stats/team-stats/defense/rushing/2026/reg/all)
- [NFL.com 2026 Player Passing](https://www.nfl.com/stats/player-stats/category/passing/2026/reg/all/passingyards/desc), [Player Rushing](https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all/rushingyards/desc), [Player Receiving](https://www.nfl.com/stats/player-stats/category/receiving/2026/reg/all/receivingreceptions/desc), and [Player Tackles](https://www.nfl.com/stats/player-stats/category/tackles/2026/reg/all/defensivecombinetackles/desc)
- [NFL Official Playing Rules 2026 (PDF)](https://static.www.nfl.com/image/upload/fl_attachment/league/tqivdkzt9mu6wdgsh1ku.pdf)

## 2. File-by-File Verification Summary

| File(s) | Owner | Rows Checked | Verified | Mismatches | Result | Official Source |
|---|---|---:|---:|---:|---|---|
| `data/standings-2026.json`, `standings.html` | `194db560` | 32 | 32 | 0 | VERIFIED | [NFL.com Standings](https://www.nfl.com/standings/division/2026/reg) |
| `data/standings_2026.json`, `docs/standings.html` | `arena-85d79210` | 32 | 32 | 0 | VERIFIED | [NFL.com Standings](https://www.nfl.com/standings/division/2026/reg) |
| `data/schedule-week11-2026.json`, `schedule.html` | `194db560` | 19 | 19 | 0 | VERIFIED | [NFL.com Week 11](https://www.nfl.com/news/week-11-schedule-change) |
| `data/schedule_week11_2026.json`, `docs/schedule.html` | `arena-85d79210` | 19 | 19 | 0 | VERIFIED | [NFL.com Bye Weeks](https://www.nfl.com/news/2026-nfl-schedule-release-every-team-bye-week) |
| `data/injuries-week10-2026.json`, `injuries.html` | `194db560` | 6 | 6 | 1 URL | FLAGGED (`IR-01`, `IR-10`) | [NFL.com REG10](https://www.nfl.com/injuries/league/2026/REG10) |
| `data/injuries_2026-11-11.json`, `docs/injuries.html` | `arena-85d79210` | 35 | 35 | 0 | VERIFIED (Snapshot) | [NFL.com Nov 11 Roundup](https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11) |
| `data/team_stats_defense_2026.json`, `docs/defense.html` | `arena-85d79210` | 32 | 32 | 0 | VERIFIED | [NFL.com Defense Stats](https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all) |
| `data/player_leaders_2026.json` (Passing & Tackles) | `arena-85d79210` | 20 | 20 | 0 | VERIFIED (`IR-11` note) | [NFL.com Passing](https://www.nfl.com/stats/player-stats/category/passing/2026/reg/all/passingyards/desc) |
| `data/player_leaders_2026.json` (Rushing & Receiving) | `arena-85d79210` | 20 | 16 | 4 | FLAGGED (`IR-04`..`IR-08`) | [NFL.com Rushing](https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all/rushingyards/desc) |
| `lines-lab.html`, `assets/app.js` | `194db560` | 13 | 12 | 2 | FLAGGED (`IR-02`, `IR-03`) | [NFL.com Standings](https://www.nfl.com/standings/division/2026/reg) |
| `teams.html`, `data/teams.json` | Both | 32 | 32 | 0 | VERIFIED | [NFL.com Standings](https://www.nfl.com/standings/division/2026/reg) |

## 3. Irregularities Flagged for Review (`IR-01` – `IR-12`)

1. **`IR-01` (High — Wrong Week 10 Injury Report URL):** `data/injuries-week10-2026.json`, `injuries.html`, `flagged.html`, `questions.html`, and `sources.html` link `https://www.nfl.com/injuries/league/2026/REG9` as the "Official NFL Injury Report — Week 10". Live verification confirms `/REG9` renders `## Injuries - WEEK 9` (`THURSDAY, NOVEMBER 5TH — JAX at BAL`), whereas `/REG10` (`https://www.nfl.com/injuries/league/2026/REG10`) is the actual Week 10 report (`## Injuries - WEEK 10`, `THURSDAY, NOVEMBER 12TH — WAS at NYG`).
2. **`IR-02` (Low — Malformed HTML Row):** `lines-lab.html` row `NO at CHI` has 7 `<td>` cells instead of 8.
3. **`IR-03` (High — Equal-Games Assumption Bug in Lines Lab v0):** `lines-lab.html` / `assets/app.js` divides both teams' PF and PA by a single `Games played` input `g`. In official 2026 standings, 16 teams have played 8 games and 16 have played 9 games; 8 of 13 Week 11 games pair an 8-game team against a 9-game team.
4. **`IR-04` (High — Player Rushing TD Transcription Error):** `data/player_leaders_2026.json` (`docs/stats.html`) lists **Bijan Robinson** with `TD = 9`. Official [NFL.com Player Rushing](https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all/rushingyards/desc) shows `RushYds = 880, Att = 169, TD = 5, 20+ = 9, 40+ = 2, Lng = 59` (column `20+` misread as `TD`).
5. **`IR-05` (High — Player Rushing TD Transcription Error):** `data/player_leaders_2026.json` (`docs/stats.html`) lists **Jaylen Warren** with `TD = 7`. Official [NFL.com Player Rushing](https://www.nfl.com/stats/player-stats/category/rushing/2026/reg/all/rushingyards/desc) shows `RushYds = 704, Att = 119, TD = 2, 20+ = 7, 40+ = 2, Lng = 51` (and Pittsburgh's entire team rushing TD total on [Team Rushing](https://www.nfl.com/stats/team-stats/offense/rushing/2026/reg/all) is `4`).
6. **`IR-06` (High — Player Receiving Longest Play Transcription Error):** `data/player_leaders_2026.json` (`docs/stats.html`) lists **Trey McBride** with `Lng = 41`. Official [NFL.com Player Receiving](https://www.nfl.com/stats/player-stats/category/receiving/2026/reg/all/receivingreceptions/desc) shows `Rec = 73, Yds = 598, TD = 5, 20+ = 4, 40+ = 0, Lng = 27, Rec 1st = 30, Rec 1st% = 41.1` (`Rec 1st%` misread as `Lng`).
7. **`IR-07` (High — Player Receiving TD Transcription Error):** `data/player_leaders_2026.json` (`docs/stats.html`) lists **Ja'Marr Chase** with `TD = 8`. Official [NFL.com Player Receiving](https://www.nfl.com/stats/player-stats/category/receiving/2026/reg/all/receivingreceptions/desc) shows `Rec = 53, Yds = 647, TD = 7, 20+ = 8, 40+ = 2, Lng = 47` (`20+` misread as `TD`).
8. **`IR-08` (Low — Unlabelled Derived Ratios):** `Yds/Att` in Player Rushing and `Yds/Rec` in Player Receiving are derived ratios (`Yds / Att`, `Yds / Rec`), not raw columns on those two NFL.com pages.
9. **`IR-09` (Medium — Dual Root `/` vs `docs/` Pages Builds):** GitHub Pages serves `/` via `legacy` mode while `.github/workflows/pages.yml` uploads `docs/`. Cross-linking preserves both sessions' sites seamlessly.
10. **`IR-10` (Low — Cross-Source Position Granularity):** `Ben Brown` (NE) is `OL` in NFL.com's Week 10 summary, `C` on `REG10`, and 1st-string `LG` + 2nd-string `C` on [Patriots.com Depth Chart](https://www.patriots.com/team/depth-chart).
11. **`IR-11` (Low — Official NFL.com Tackles Upstream Accounting):** On [NFL.com Tackles](https://www.nfl.com/stats/player-stats/category/tackles/2026/reg/all/defensivecombinetackles/desc), `Comb` exceeds `Solo + Ast` for 7 of top 10 tacklers because special-teams tackles are included in `Comb`.
12. **`IR-12` (Low — Fixed Session Branch Name):** Execution environment pins each session to `arena/<id>-nfl2`; disjoint file scopes and rebase serialization in `COORDINATION.md` replace per-task sub-branches.
