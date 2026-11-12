# Verification Log

Every claim the site makes, with the source used and the check performed. "Official"
means the NFL itself (operations.nfl.com / nfl.com) or the licensed data provider.
Where an official page could not be loaded from this environment, that is stated.

**Verification date:** 2026-11-12. **Method:** each item was fetched, read, and the
stated value compared with the repository's data by code where possible.

---

## 1. Rules and scoring

| # | Claim verified | Official source | Result |
|---|----------------|-----------------|--------|
| 1.1 | The 2025 rulebook is the current playing-rules document | https://operations.nfl.com/the-rules/2025-nfl-rulebook/ | Confirmed (page 404s on the bare rulebook URL, resolves through operations.nfl.com/rules-officiating/featured-rules; the 2025 changes page loads cleanly) |
| 1.2 | 2025 rules changes: dynamic kickoff made permanent, both teams get a possession in regular-season OT, replay-assist expansion | https://operations.nfl.com/the-rules/rules-changes/2025-rules-changes/ | Confirmed verbatim on the page |
| 1.3 | Regular-season overtime is 10 minutes | same page ("subject to a 10-minute overtime period in the regular season") | Confirmed |
| 1.4 | A team cannot score exactly 1 point; scores are built from 2, 3, 6, 7, 8-point plays | https://operations.nfl.com/the-rules/2025-nfl-rulebook/ (Rule 11) | Confirmed; used as an audit check, and **no** game in the dataset contains a score of 1 |
| 1.5 | Ties are possible | Rule 16 (overtime) | Confirmed; the dataset contains tied games, consistent with the rule |

## 2. Schedule structure

| # | Claim verified | Official source | Result |
|---|----------------|-----------------|--------|
| 2.1 | 32 clubs play 17 regular-season games each = 272 per season since 2021 | https://operations.nfl.com/ (schedule section) and the league's own published figure of 272 | Confirmed. Data: 272 games in 2021, 2023, 2024, 2025 |
| 2.2 | 16 games per club = 256 per season from 2002-2020 | NFL historical schedule | Confirmed. Data: 256 for every season 2002-2020 |
| 2.3 | 31 clubs x 16 = 248 per season 1999-2001 (Houston Texans began play in 2002) | NFL historical record | Confirmed. Data: 248 in 1999, 2000, 2001 |
| 2.4 | 2022 regular season has **271** games, not 272 | NFL announcement that the Week 17 Bills-Bengals game would not be resumed, after Damar Hamlin's on-field cardiac arrest (2 Jan 2023); reported by ESPN and the AP | Confirmed as a genuine, explained irregularity — see Flagged for Review |

## 3. Data schema and provenance

| # | Claim verified | Source | Result |
|---|----------------|--------|--------|
| 3.1 | `spread_line` is the home-team handicap; positive means home favoured | https://github.com/leesharpe/nfldata/blob/master/DATASETS.md | Confirmed by documentation **and** by test: corr(spread_line, result)=+0.439, and a home fav of 27 won by 16 |
| 3.2 | `result` = home_score − away_score | same | Confirmed by code: max deviation 0 across all 7,412 played games |
| 3.3 | `total` = home_score + away_score | same | Confirmed by code: max deviation 0 |
| 3.4 | `rosters.csv` games/starts/AV come from Pro Football Reference | same, §Rosters | Confirmed in the documentation |
| 3.5 | `starts` is **not populated** after 2018 | our own audit of the shipped file | Confirmed: 0 total starts recorded for 2019-2026. Independent of upstream docs; flagged |
| 3.6 | Seven roster rows carry negative years-of-experience | our own audit | Confirmed in the shipped file; upstream artefact, flagged |

## 4. Injuries

| # | Claim verified | Official source | Result |
|---|----------------|-----------------|--------|
| 4.1 | The NFL publishes a weekly injury report with game statuses Out / Doubtful / Questionable and practice participation Limited / Full / Did Not Participate | https://www.nfl.com/injuries/ (live page, Week 10 of the 2026 season) | Confirmed directly: the official page was read and its tables use exactly these values |
| 4.2 | The official Week 10 2026 page lists a specific set of players (e.g. Washington: Lucas Patrick, concussion, Out) | same | Confirmed — the named example appears on the official page at verification time |
| 4.3 | Our injury CSVs use the same status vocabulary | nflverse `injuries` release, mirrored in-repo | Confirmed: values are Out / Doubtful / Questionable / Note |
| 4.4 | The 2026 injury mirror is one week behind the official page | comparison | **Confirmed irregularity** — mirror stops at Week 9 while the official page shows Week 10. Flagged; the site never claims the mirror is current |

## 5. Depth charts

| # | Claim verified | Source | Result |
|---|----------------|--------|--------|
| 5.1 | Depth charts carry a `depth_team` rank of 1, 2 or 3 per position | nflverse `depth_charts` release (mirror copy in-repo) | Confirmed in the file; 18,244 depth-1 / 14,056 depth-2 / 5,012 depth-3 rows |
| 5.2 | Coverage is 2024 only, all 32 clubs, weeks 1-22 including playoffs | same | Confirmed: `season` is 2024 throughout |
| 5.3 | A depth-1 player ruled Out implies a depth-2 starter | logical consequence of the chart; not directly stated by the NFL | Marked **inference, not a verified fact** on the availability page |

## 6. Betting mathematics

| # | Claim verified | Source | Result |
|---|----------------|--------|--------|
| 6.1 | −110 pricing implies a 52.38% break-even | arithmetic | Confirmed: 110/210 = 0.52381 |
| 6.2 | A 2-leg parlay at −110 has a book hold of 8.9% | arithmetic | Confirmed: 1−0.25/0.2744 = 8.9% |
| 6.3 | Spread and total outcomes are close to independent | our measurement over 3,289 paired games | Confirmed: φ = +0.019 |
| 6.4 | Spread and home moneyline are strongly dependent | our measurement over 3,320 paired games | Confirmed: φ = +0.669 |

## 7. Compliance

| # | Claim verified | Official source | Result |
|---|----------------|-----------------|--------|
| 7.1 | NFL personnel may not bet on NFL football | National Football League Gambling Policy for Players, restated 24 Oct 2025 | Confirmed through the league's own newsroom: https://www.nfl.com/news/nfl-reminds-players-of-league-gambling-policy-in-light-of-federal-indictments |
| 7.2 | The league treats prediction-market sports contracts as betting | NFL Chief Compliance Officer, public remarks; league memos September and October 2025 | Confirmed via multiple independent outlets; **no** primary NFL document with this text could be loaded, so it is quoted as reported, not as read |
| 7.3 | Using a statistical model to analyse games is not prohibited for members of the public | no statute prohibits analysis; books prohibit bot-placed wagers | Partially confirmed — the negative claim (nothing prohibits analysis) cannot be exhaustively proven; recorded as **best available understanding**, to be confirmed by counsel |

---

## What could not be verified from an official source

Listed so that nothing above is mistaken for a complete verification.

| Item | Why | Effect on the site |
|------|-----|--------------------|
| Prop-line history | no licensed archive reachable | prop correlations published as UNVERIFIED |
| Snap counts | release assets above the API size limit | "actually played" cannot be confirmed; "listed Out" is used instead |
| Opening lines for most seasons | only 2021 exists in the source (one book) | injury-price impact cannot be measured |
| Depth charts 2025-2026 | unreachable | vacancy index limited to 2024 |
| Primary NFL text on prediction markets | not published as a loadable document | quoted as reported by the press |
| Licence to redistribute the dataset | no LICENSE file upstream | flagged for legal review |
