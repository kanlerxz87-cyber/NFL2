# Re-Verification Register — 16 November 2026

> A dated line-by-line re-read of every official page this repository's Week 10 numbers rest on, taken on **16 November 2026 between 14:35Z and 15:05Z**. Every row below was checked against the live official page in this session and carries the page it was checked against. Nothing on this page is inferred: where the league publishes nothing, the cell says so and the row is marked pending. Source pages: the [official injury hub](https://www.nfl.com/injuries/), the [Week 10 scores page](https://www.nfl.com/scores/2026/week-10), the [Week 10 schedule page](https://www.nfl.com/schedules/2026/by-week/week-10), the [Week 11 schedule page](https://www.nfl.com/schedules/2026/by-week/week-11) and the [official standings](https://www.nfl.com/standings/), registered as S-INJ-E632, S-SCORES-E632, S-SCHED-E632, S-WK11-E632 and S-STAND-E632.

## What this session found

- **The Week 10 injury hub has not moved since 15 November.** The full row-level re-read (347 rows, transcribed to `data/hub_read_e632af20_20261116.csv`) matches both 15 November reads cell for cell: zero additions, zero removals, zero changed designations, zero changed practice codes. The Friday report was frozen through Sunday's games and into Monday. One transcription error in this session's own first draft was caught by that same cell-for-cell comparison and corrected against the fetched page before anything was published.
- **Thirteen Week 10 games were final at read time and one was ingested; by the time this page merged, all thirteen were.** The two official score pages agreed line for line, and this register published the twelve un-ingested finals with their game-centre links at 14:52Z. In parallel, the results-feed session appended those twelve to the append-only results file (captured 14:41Z) and re-pinned the pre-registration's settled-file hash under a **dated amendment that preserves the decision-time hash** — so the model-grade gate kept its word and the results feed grew ([FL-114](flagged-for-review.html) is the remaining ask: the owner's ratification of that adopted append protocol). The [Results feed](results-feed.html) page carries the same thirteen finals from its own read.
- **The standings delta closes exactly — twice over.** For all 32 clubs, this session's 14:50Z official read equals the repository's 13 November snapshot plus exactly that club's Sunday result on wins, losses, ties, points for and points against, recomputed by `tools/verify_e632af20.py`. And it agrees **cell for cell with the published table's own 14:57Z read** (S-STAND-F3EC), which a parallel session refreshed after this one — two independent reads seven minutes apart, identical on all 32 clubs × 8 fields (RV632-41). There is no unexplained cell on either side.
- **The Henderson reserve-list conflict is still live** ([FL-96](flagged-for-review.html)). Two days on, the hub still lists TreVeyon Henderson with game status Out while its own news block carries the league's article placing him on injured reserve.
- **The whole Week 11 slate matches the published schedule file** — clubs, dates, kickoffs and broadcasters — including the two fixtures whose broadcasters moved between the league's 9 November schedule-change article and the live page (the repository already carries the current values). Two fixture rows fell in a gap between page chunks of the schedule fetch and were verified on their own official game pages instead, which also name their stadiums.

## The register — every check, with its official page

{{csv data/reverification_e632af20.csv;;cols=id:ID,check:Check,scope:Scope,published_value:What the repository publishes,official_value:What the official pages showed on 16 Nov,result:Result,note:Note;;source_col=source;;caption=One row per check, written only after the official page was read in this session. Results: MATCH means the repository and the official page agree; NOT INGESTED means the fact was verified and published here but not yet in the results file the models read — a verdict dated at the read time, since the twelve finals were appended later the same day (RV632-26, FL-114); PENDING means the league publishes no result yet and none is recorded; FLAGGED means the row is on the Flagged for Review page with its decision; SUPERSEDED marks a finding of this read that a parallel session resolved before this page merged.}}

## Standings: the dated delta, club by club

What this session publishes is the **change**, dated twice over. The table below is the 14:50Z official read as an independent transcription; RV632-21 records that it equals the 13 November snapshot plus exactly the twelve Sunday results for every club, and RV632-41 records that it agrees cell for cell with the 14:57Z read the site's [standings table](league-data.html) now carries (a parallel session refreshed the table after this read, and this transcription is the independent cross-check that refresh needed). The refresh cadence question itself stays with the owner ([Q-40](questions.html)).

{{csv data/standings_recheck_e632af20_20261116.csv;;cols=abbr:Club,w:W,l:L,t:T,pct:PCT,pf:PF,pa:PA,net:Net,streak:Streak;;source_col=source;;caption=Independent row-by-row transcription of the official division standings page, read 2026-11-16T14:50Z. League-wide identities recomputed: wins equal losses at 148, ties at 2, points for equal points against at 6,880 — 298 club-games for 149 completed games (the 136-game weeks 1-9 corpus with its one tie, plus the thirteen settled Week 10 games).}}

## Week 10 results as the league publishes them

Thirteen final, one pending. Every score below was read on both the official scores page and the official schedule page; the game links are the league's own game centres. The Monday game carries no result here because at read time (14:55Z, kickoff 01:15Z on 17 November) the league published none.

| Game | Fixture | Official result at read time | Ingestion state |
| --- | --- | --- | --- |
| W10-01 | WAS at NYG | [WAS 24 – NYG 21](https://www.nfl.com/games/commanders-at-giants-2026-reg-10) FINAL | ingested 2026-11-13 |
| W10-02 | NE at DET (Munich) | [NE 10 – DET 35](https://www.nfl.com/games/patriots-at-lions-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-03 | KC at ATL | [KC 35 – ATL 13](https://www.nfl.com/games/chiefs-at-falcons-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-04 | MIN at GB | [MIN 30 – GB 10](https://www.nfl.com/games/vikings-at-packers-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-05 | JAX at TEN | [JAX 40 – TEN 23](https://www.nfl.com/games/jaguars-at-titans-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-06 | MIA at IND | [MIA 22 – IND 24](https://www.nfl.com/games/dolphins-at-colts-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-07 | CAR at NO | [CAR 20 – NO 17](https://www.nfl.com/games/panthers-at-saints-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-08 | BUF at NYJ | [BUF 31 – NYJ 12](https://www.nfl.com/games/bills-at-jets-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-09 | HOU at CLE | [HOU 24 – CLE 27](https://www.nfl.com/games/texans-at-browns-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-10 | LAR at AZ | [LAR 34 – AZ 6](https://www.nfl.com/games/rams-at-cardinals-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-11 | SEA at LV | [SEA 21 – LV 13](https://www.nfl.com/games/seahawks-at-raiders-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-12 | SF at DAL | [SF 46 – DAL 40](https://www.nfl.com/games/49ers-at-cowboys-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-13 | PIT at CIN | [PIT 18 – CIN 38](https://www.nfl.com/games/steelers-at-bengals-2026-reg-10) FINAL | appended 2026-11-16, after this read |
| W10-14 | LAC at BAL | [no result published at read time](https://www.nfl.com/games/chargers-at-ravens-2026-reg-10) — kickoff 8:15 PM ET tonight | pending — not recorded (not final) |

## Method

1. Every official page was fetched and read in this session on 16 November 2026; the fetch window is 14:35–15:05Z. The hub read is transcribed row by row to `data/hub_read_e632af20_20261116.csv` with its capture clock on every row, the standings read to `data/standings_recheck_e632af20_20261116.csv`.
2. `tools/verify_e632af20.py` re-derives every arithmetic claim on this page from the checked-in files: the zero-change hub delta, the standings reconciliation club by club, the league-wide identities, the result scores against the fixture map and the results file, and the Week 11 fixture facts against the schedule file. It exits non-zero if any claim moves.
3. The verification suite that builds and audits the whole site (`tools/build_site.py`, `tools/verify.py`, `tools/check_site.py`, `scripts/audit_all_pages.py` and the other session suites) was re-run on the combined tree; the tally is recorded in [COORDINATION.md](https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md).

## What this page does not establish

- **It does not grade anything.** This page is the verification record; the grading lives on [Settled Week 10](week10-settled.html), which since the parallel append re-scores all thirteen finals. Nothing on this page forecasts.
- **It does not set the refresh cadence.** The cumulative tables are dated snapshots and this page publishes the deltas beside them; when they move and how grades re-baseline is [Q-40](questions.html), the owner's open decision.
- **It is transcription, not byte capture.** The rows were transcribed from the rendered pages and then verified by the arithmetic above and by cross-reading two official pages per result. Byte captures with stored hashes now exist for the injury hub (the [Official Capture](captures.html) store, session 7c23f22f); the schedule, scores and standings pages used here are still transcriptions only.

Flags for this page: [FL-96](flagged-for-review.html) (the Henderson conflict, re-verified here) and [FL-114](flagged-for-review.html) (the owner's ratification of the append protocol that cleared the results-feed gate this page's read found). Two findings this page published at read time — the blocked results feed and the one-game settle sample — were resolved in parallel before it merged; the register keeps them as dated rows (RV632-37/38, marked SUPERSEDED) because a verification record that erases what it found verifies nothing. The hub's own history is on the [Injury Hub delta](hub-delta.html) and [Availability Watch](availability-watch.html) pages; the pre-registered lines that will be graded against these results are on [Settled Week 10](week10-settled.html) and [Week 11 Lines](week11-originated.html).
