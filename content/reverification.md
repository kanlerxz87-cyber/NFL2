# Re-Verification Register — 16 November 2026

> A dated line-by-line re-read of every official page this repository's Week 10 numbers rest on, taken on **16 November 2026 between 14:35Z and 15:05Z**. Every row below was checked against the live official page in this session and carries the page it was checked against. Nothing on this page is inferred: where the league publishes nothing, the cell says so and the row is marked pending. Source pages: the [official injury hub](https://www.nfl.com/injuries/), the [Week 10 scores page](https://www.nfl.com/scores/2026/week-10), the [Week 10 schedule page](https://www.nfl.com/schedules/2026/by-week/week-10), the [Week 11 schedule page](https://www.nfl.com/schedules/2026/by-week/week-11) and the [official standings](https://www.nfl.com/standings/), registered as S-INJ-E632, S-SCORES-E632, S-SCHED-E632, S-WK11-E632 and S-STAND-E632.

## What this session found

- **The Week 10 injury hub has not moved since 15 November.** The full row-level re-read (347 rows, transcribed to `data/hub_read_e632af20_20261116.csv`) matches both 15 November reads cell for cell: zero additions, zero removals, zero changed designations, zero changed practice codes. The Friday report was frozen through Sunday's games and into Monday. One transcription error in this session's own first draft was caught by that same cell-for-cell comparison and corrected against the fetched page before anything was published.
- **Thirteen Week 10 games are final and the repository has ingested one of them.** The two official score pages agree line for line. The hold-up is structural, not clerical: the pre-registration hash gate treats any append to the results file as tampering. The twelve un-ingested results are published here with their official game pages (the parallel 16 November capture session publishes the same thirteen on the [Results feed](results-feed.html) page from its own read) so ingestion needs no second transcription once an owner approves an append protocol ([FL-112](flagged-for-review.html), [FL-113](flagged-for-review.html)).
- **The standings delta closes exactly.** For all 32 clubs, today's official read equals the repository's 13 November snapshot plus exactly that club's Sunday result — wins, losses, ties, points for and points against, recomputed by `tools/verify_e632af20.py`. There is no unexplained cell on either side.
- **The Henderson reserve-list conflict is still live** ([FL-96](flagged-for-review.html)). Two days on, the hub still lists TreVeyon Henderson with game status Out while its own news block carries the league's article placing him on injured reserve.
- **The whole Week 11 slate matches the published schedule file** — clubs, dates, kickoffs and broadcasters — including the two fixtures whose broadcasters moved between the league's 9 November schedule-change article and the live page (the repository already carries the current values). Two fixture rows fell in a gap between page chunks of the schedule fetch and were verified on their own official game pages instead, which also name their stadiums.

## The register — every check, with its official page

{{csv data/reverification_e632af20.csv;;cols=id:ID,check:Check,scope:Scope,published_value:What the repository publishes,official_value:What the official pages showed on 16 Nov,result:Result,note:Note;;source_col=source;;caption=One row per check, written only after the official page was read in this session. Results: MATCH means the repository and the official page agree; NOT INGESTED means the fact is verified and published here but not yet in the results file the models read (FL-112); PENDING means the league publishes no result yet and none is recorded; FLAGGED means the row is on the Flagged for Review page with its decision.}}

## Standings: the dated delta, club by club

The site's [standings table](league-data.html) deliberately still renders the 13 November snapshot: the refresh cadence is the open owner decision ([Q-40](questions.html)), and a self-refreshing cumulative table would silently re-baseline every grade built on the old one. What this session publishes instead is the **change**: below is the 16 November official read as an independent transcription, and the register row RV632-21 records that it equals the 13 November snapshot plus the twelve Sunday results for every club.

{{csv data/standings_recheck_e632af20_20261116.csv;;cols=abbr:Club,w:W,l:L,t:T,pct:PCT,pf:PF,pa:PA,net:Net,streak:Streak;;source_col=source;;caption=Independent row-by-row transcription of the official division standings page, read 2026-11-16T14:50Z. League-wide identities recomputed: wins equal losses at 148, ties at 2, points for equal points against at 6,880 — 298 club-games for 149 completed games (the 136-game weeks 1-9 corpus with its one tie, plus the thirteen settled Week 10 games).}}

## Week 10 results as the league publishes them

Thirteen final, one pending. Every score below was read on both the official scores page and the official schedule page; the game links are the league's own game centres. The Monday game carries no result here because at read time (14:55Z, kickoff 01:15Z on 17 November) the league published none.

| Game | Fixture | Official result at read time | Ingested in the results file |
| --- | --- | --- | --- |
| W10-01 | WAS at NYG | [WAS 24 – NYG 21](https://www.nfl.com/games/commanders-at-giants-2026-reg-10) FINAL | yes |
| W10-02 | NE at DET (Munich) | [NE 10 – DET 35](https://www.nfl.com/games/patriots-at-lions-2026-reg-10) FINAL | no (FL-112) |
| W10-03 | KC at ATL | [KC 35 – ATL 13](https://www.nfl.com/games/chiefs-at-falcons-2026-reg-10) FINAL | no (FL-112) |
| W10-04 | MIN at GB | [MIN 30 – GB 10](https://www.nfl.com/games/vikings-at-packers-2026-reg-10) FINAL | no (FL-112) |
| W10-05 | JAX at TEN | [JAX 40 – TEN 23](https://www.nfl.com/games/jaguars-at-titans-2026-reg-10) FINAL | no (FL-112) |
| W10-06 | MIA at IND | [MIA 22 – IND 24](https://www.nfl.com/games/dolphins-at-colts-2026-reg-10) FINAL | no (FL-112) |
| W10-07 | CAR at NO | [CAR 20 – NO 17](https://www.nfl.com/games/panthers-at-saints-2026-reg-10) FINAL | no (FL-112) |
| W10-08 | BUF at NYJ | [BUF 31 – NYJ 12](https://www.nfl.com/games/bills-at-jets-2026-reg-10) FINAL | no (FL-112) |
| W10-09 | HOU at CLE | [HOU 24 – CLE 27](https://www.nfl.com/games/texans-at-browns-2026-reg-10) FINAL | no (FL-112) |
| W10-10 | LAR at AZ | [LAR 34 – AZ 6](https://www.nfl.com/games/rams-at-cardinals-2026-reg-10) FINAL | no (FL-112) |
| W10-11 | SEA at LV | [SEA 21 – LV 13](https://www.nfl.com/games/seahawks-at-raiders-2026-reg-10) FINAL | no (FL-112) |
| W10-12 | SF at DAL | [SF 46 – DAL 40](https://www.nfl.com/games/49ers-at-cowboys-2026-reg-10) FINAL | no (FL-112) |
| W10-13 | PIT at CIN | [PIT 18 – CIN 38](https://www.nfl.com/games/steelers-at-bengals-2026-reg-10) FINAL | no (FL-112) |
| W10-14 | LAC at BAL | [no result published at read time](https://www.nfl.com/games/chargers-at-ravens-2026-reg-10) — kickoff 8:15 PM ET tonight | no (pending) |

## Method

1. Every official page was fetched and read in this session on 16 November 2026; the fetch window is 14:35–15:05Z. The hub read is transcribed row by row to `data/hub_read_e632af20_20261116.csv` with its capture clock on every row, the standings read to `data/standings_recheck_e632af20_20261116.csv`.
2. `tools/verify_e632af20.py` re-derives every arithmetic claim on this page from the checked-in files: the zero-change hub delta, the standings reconciliation club by club, the league-wide identities, the result scores against the fixture map and the results file, and the Week 11 fixture facts against the schedule file. It exits non-zero if any claim moves.
3. The verification suite that builds and audits the whole site (`tools/build_site.py`, `tools/verify.py`, `tools/check_site.py`, `scripts/audit_all_pages.py` and the other session suites) was re-run on the combined tree; the tally is recorded in [COORDINATION.md](https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md).

## What this page does not establish

- **It does not grade anything.** The settled table still grades one game; extending it is blocked on the append protocol in [FL-112](flagged-for-review.html), not on missing evidence — every result it needs is in the table above.
- **It does not refresh the site's cumulative tables.** The standings, ratings and fair-line tables keep their dated snapshots until [Q-40](questions.html) sets a cadence; this page publishes the delta beside them instead.
- **It is transcription, not byte capture.** The rows were transcribed from the rendered pages and then verified by the arithmetic above and by cross-reading two official pages per result. A raw capture with stored hashes is still the missing infrastructure ([FL-82](flagged-for-review.html)).

Flags for this page: [FL-96](flagged-for-review.html) (the Henderson conflict, re-verified here), [FL-112](flagged-for-review.html) (the results-feed growth gate), [FL-113](flagged-for-review.html) (the one-game settle sample). The hub's own history is on the [Injury Hub delta](hub-delta.html) and [Availability Watch](availability-watch.html) pages; the pre-registered lines that will be graded against these results are on [Settled Week 10](week10-settled.html) and [Week 11 Lines](week11-originated.html).
