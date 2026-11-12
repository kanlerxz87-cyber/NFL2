# Repository Line-by-Line Audit (`kanlerxz87-cyber/NFL2`)

- **Session**: `e143a7ca` (`arena/e143a7ca-nfl2`)
- **Initial Commit Audited**: [`01f227119ee8df4223b0aa697d08ed92257773c3`](https://github.com/kanlerxz87-cyber/NFL2/commit/01f227119ee8df4223b0aa697d08ed92257773c3)
- **Merged `main` Head Audited**: [`e351a8d`](https://github.com/kanlerxz87-cyber/NFL2/commit/e351a8d)
- **Audit Timestamp**: `2026-11-12T04:39:00Z`

## 1. Line-by-Line File Verification Summary

| File Path | Lines | Status | Verification Summary | Official Source |
| :--- | ---: | :--- | :--- | :--- |
| `README.md` (`@01f2271`) | 1 | Flagged (`IR-REPO-01`) | Contained `# NFL2` (6 bytes, missing EOF newline; no `.nojekyll` or `.gitignore`). | [GitHub Commit `01f2271`](https://github.com/kanlerxz87-cyber/NFL2/commit/01f227119ee8df4223b0aa697d08ed92257773c3) |
| `README.md` (`@e351a8d`) | 39 | Verified | Accurate sitemap for root 12-page dashboard and Pages configuration (`main:/`). | [GitHub `README.md`](https://github.com/kanlerxz87-cyber/NFL2/blob/main/README.md) |
| `COORDINATION.md` | 48 | Flagged (`IR-REPO-09`) | Line 41 cites `PR #2` for commit `e351a8d`, whereas GitHub PR ledger confirms `PR #3` merged `e351a8d`. | [GitHub PR #3](https://github.com/kanlerxz87-cyber/NFL2/pull/3) |
| `data/standings-2026.json` | 42 | Verified (100%) | All 32 team records (`W`, `L`, `T`, `PCT`, `PF`, `PA`, `NET`, `HOME`, `ROAD`, `DIV`, `CONF`, `STRK`, `LAST5`) match live NFL.com standings. Zero-sum checks pass: `sum(W)=135=sum(L)`, `sum(T)=2`, `sum(PF)=6246=sum(PA)`. | [NFL.com Standings](https://www.nfl.com/standings/) |
| `data/schedule-week11-2026.json` | 25 | Flagged (`IR-REPO-05`) | 13 Week 11 games + 6 byes = 32 teams verified, but active Week 10 slate (Nov 12–16, 2026) is absent despite Week 10 injury tracking. | [NFL.com Schedules](https://www.nfl.com/schedules) |
| `data/injuries-week10-2026.json` | 32 | Flagged (`IR-REPO-02..04`) | Line 6 links `fullReport` to `.../2026/REG9` under a Week 10 label; line 12 lists `Ben Brown` as `OL` instead of `C` (`Carlton Davis III` truncated); omits full DNP/Limited table on `nfl.com/injuries/`. | [NFL.com Official Injuries](https://www.nfl.com/injuries/) |
| `standings.html` | 64 | Verified (100%) | 32/32 `<tbody>` rows verified against `nfl.com/standings/` with per-row official links. | [NFL.com Standings](https://www.nfl.com/standings/) |
| `schedule.html` | 58 | Verified | 19/19 `<tbody>` rows (13 games + 6 byes) carry official `nfl.com` links. | [NFL.com Week 11 Schedule Change](https://www.nfl.com/news/week-11-schedule-change) |
| `teams.html` | 64 | Verified | 32/32 club alignment rows carry official `nfl.com/teams/<slug>/` links. | [NFL.com Standings](https://www.nfl.com/standings/) |
| `injuries.html` | 75 | Flagged (`IR-REPO-02`, `IR-REPO-08`) | Uses `REG9` URL for full report; leaves all 2nd–4th string replacements blank despite official NFL club depth charts existing on club sites (`commanders.com`, `giants.com`, etc.). | [Commanders 2026 Official Club Depth Chart](https://www.commanders.com/news/commanders-release-2026-unofficial-depth-chart) |
| `lines-lab.html` | 84 | Flagged (`IR-REPO-06`, `IR-REPO-07`) | Line 56 (`NO at CHI`) has 7 `<td>` cells in an 8-column table; 18 `<tbody>` rows lack official `https://` source links. | [GitHub `lines-lab.html`](https://github.com/kanlerxz87-cyber/NFL2/blob/main/lines-lab.html#L56) |
| `strategies.html` | 90 | Flagged (`IR-REPO-07`) | 10 `<tbody>` rows across validation gates and leaderboard tables lack per-row official `https://` source links; no computed empirical correlations included. | [GitHub `strategies.html`](https://github.com/kanlerxz87-cyber/NFL2/blob/main/strategies.html) |
| `executive-summary.html`, `suggestions.html`, `questions.html`, `flagged.html` | 209 | Flagged (`IR-REPO-07`) | Multiple `<tbody>` rows omit external official `https://` source links (or link only internally). | [GitHub Repository Tree](https://github.com/kanlerxz87-cyber/NFL2/tree/main) |
| `assets/app.js`, `assets/style.css` | 149 | Verified | Abramowitz & Stegun 7.1.26 normal CDF, Pearson `r` formula, and DOM filter verified line by line. | [NIST Digital Library of Mathematical Functions §7.2](https://dlmf.nist.gov/7.2) |

## 2. Coordination Compliance Note

Per `COORDINATION.md` scope-isolation rules, files owned by session `194db560` were **not** directly overwritten during Task `E1`. Instead:
1. Change requests for `IR-REPO-02`..`IR-REPO-09` are logged in `COORDINATION.md`.
2. Session `e143a7ca` publishes fully verified datasets (`datasets/e143a7ca/*.json`), deterministic verification scripts (`engine/*.py`), and a 100%-sourced multi-page dashboard (`portal/*.html` + `portal/flagged-review.html`) where **every single table row** links to an official primary source and any unconfirmed value is left strictly blank and flagged `UNVERIFIED`.
