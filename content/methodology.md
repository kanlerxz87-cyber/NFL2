# Verification Method
> The rules this project will not bend, the checks that run automatically, and exactly what the words "verified", "corroborated" and "unverified" mean here.

## The rules

1. **Every row that asserts a fact about the world cites an official league page.** The generator refuses to build a table whose rows do not carry a resolvable source id, so this is not a convention that can be forgotten — it is a build failure.
2. **Tier A = official.** Only `nfl.com` (including `operations.nfl.com`) counts as a system-of-record source. Third-party sites — even accurate ones — are used for two things only: as a discrepancy exhibit, or as a pointer to a claim we then refuse to publish until the official text is found.
3. **A blank is a blank.** Unknown values are stored as an empty field and rendered as `not published`. Never `0`, never `N/A`, never "likely", never the value a third party reported.
4. **No inference across sources.** If the official table leaves an injury column empty and a prose article on the same site mentions an injury for a player with the same name, we do not merge them. Merging would be an assertion that the row and the sentence describe the same event, and we cannot verify that per row.
5. **Recompute, then trust.** Anything arithmetic in the published data is recomputed from the inputs — winning percentage, net points, league-wide balance — and a mismatch stops the build.
6. **Verbatim first.** Names, positions and status strings are stored as published, including two typos in the official source ("limted" twice), which are annotated rather than corrected.
7. **Timeliness is stated, not implied.** Every page shows the fetch time of the underlying pull, and no page claims to be live.
8. **Another session's file is an input, not a source.** Anything imported from a parallel session is re-audited here — per-row source links re-checked, totals recomputed, and reconciled against data we transcribed ourselves from a different official page — before it is published. Where it cannot be re-derived in the session that imports it, it stays that session's output and is labelled as such (see [S-PARALLEL](sources.html) and [Q-29](questions.html)).

## Verification vocabulary (frozen)

| Word | Means | Never means |
| --- | --- | --- |
| verified | transcribed from a tier-A official page **and** passed a recomputation or cross-page check | "I believe this is right" |
| corroborated | two independent official pages say the same thing | an official page plus a third-party page |
| computed | arithmetic performed in-repo on verified rows, with the formula published | a model output |
| design | a proposal written in this session, with no measurement behind it | a finding |
| unverified | anything else, always with a flag link | a value we should have filled in anyway |

## What actually runs

| Check | Where | What it catches |
| --- | --- | --- |
| Row-has-source enforcement | `tools/build_site.py` | a table row without a resolvable source id fails the build |
| URL-in-cell enforcement | `tools/build_site.py` | a flag row whose source cell has no link fails the build |
| Field-count enforcement | `tools/build_site.py` | a CSV row with a shifted column count fails the build — this caught six real defects in this dataset during this session |
| Standings reconciliation | `tools/verify.py` | pct formula, net points, ΣPF = ΣPA, Σnet = 0, W = L across 32 clubs |
| Injury-row integrity | `tools/verify.py` | valid practice codes, valid status codes, known game ids, unique player-per-game rows, blank census |
| Depth-log integrity | `tools/verify.py` | every change type in the controlled vocabulary, every src id resolving to an official row |
| Game-log cross-check | `tools/verify.py` | every imported row carries an official game-page URL, every week's slate is complete, and the recount of 136 games implies the same W-L-T, PF and PA as the standings table for all 32 clubs |
| Link and asset audit | `tools/check_site.py` | broken internal links, missing pages, pages not in navigation, non-official hosts used as system-of-record |
| Stale-output guard | `tools/check_site.py` | a page left on disk by an earlier build after the current build refused to render it fails the audit, and the manifest's SHA-256 over `data/*.csv` + `content/*.md` must match what is on disk |
| CI | `.github/workflows/validate.yml` | the three above must pass on every push and pull request |

## What verification did *not* cover — read this before reusing the data

- **Point-in-time completeness.** The injury hub was fetched once. It is a page that changes three times in a week; this snapshot is a faithful copy of one moment, not the week's history (FL-09).
- **Roster membership.** We spot-checked one club's roster page, one chunk deep (FL-14). We did not verify all 32 rosters, so "player X is on team Y" is only as good as the hub's own table.
- **Headline-only rows.** Three depth rows rest on an article headline without the body fetched (FL-13). They are marked and they feed no number.
- **No price data.** Nothing on this site is a market statement of any kind (FL-10).
- **Egress limits.** The sandbox blocks outbound access to the league from CI, so refresh is a deliberate operation here, not a background service (FL-11).
- **Imported files we did not re-derive.** The parallel session's team-stat, player-leader and depth-chart JSON is in the repository and is *not* published as this site's data, because their column mapping (proved by conservation identities on their side) was not re-run here; only the game log survived that bar (FL-18, Q-29).

## Reproducing the audit

```
python3 tools/build_site.py && python3 tools/verify.py && python3 tools/check_site.py
```

The generator is deterministic: same inputs, same bytes out. If it fails, that is the intended behaviour — the site is not allowed to publish a table it cannot vouch for.

## Independent live-source re-verification (session `8361cc7a`, 12 November 2026)

Every check above compares the published site to `data/`. None of them compares `data/` to the league.
That is a real gap: a snapshot can be internally consistent and months out of date. This session closed the
gap by hand, once, and recorded the result here so the claim is auditable rather than asserted.

**What was re-fetched and compared, row by row**

| Official page | Rows compared | Result |
| --- | --- | --- |
| [nfl.com/standings](https://www.nfl.com/standings/) (division view, both chunks) | 32 clubs × W-L-T, PCT, PF, PA, net, streak | **32 / 32 exact.** No correction needed. |
| [nfl.com/schedules/2026/by-week/week-10](https://www.nfl.com/schedules/2026/by-week/week-10) | 14 fixtures × date, time ET, broadcaster, venue | **14 / 14 exact.** No correction needed. |
| [nfl.com/injuries](https://www.nfl.com/injuries/) (Week 10, all 7 chunks) | every club block, every player, position, practice status, game status | **25 of 28 clubs exact.** Three differed: SEA absent, CIN absent, IND 11 of 13 rows. Published as [FL-22](flagged-for-review.html) and [FL-01](flagged-for-review.html). |

**What that comparison found in our own prose** — all corrected in this session, all listed on
[Flagged for Review](flagged-for-review.html):

1. The Week 10 snapshot's coverage was overstated on the landing page, in the executive summary and in the
   source registry; the file holds **24 of the 28** clubs playing, and the page's own availability table already
   showed 24. Coverage is now a measured metric, not a sentence.
2. The four clubs with no injury rows were described as SEA, CIN, LAC and BAL. Only **LAC and BAL** read
   "No Injuries Reported"; SEA and CIN publish full blocks and are simply missing from our file.
3. Three register rows quoted stale sizes of other registers: 25 suggestions (29 exist), 28 questions
   (29 exist), 15 flags (22 exist, including the two added here).
4. The landing page described the repository as containing one tracked file created in one session. It
   tracks **384 files across seven merged sessions**, which is what the page now says.

**Club depth charts re-checked against the clubs' own sites.** The depth analysis rests on four transcribed
charts, so each was re-fetched from the club that publishes it and compared position group by position group:

| Club | Official page | Result |
| --- | --- | --- |
| GB | [packers.com/team/depth-chart](https://www.packers.com/team/depth-chart) (labelled "Unofficial, Nov. 10, 2026") | **22 of 22 groups exact**, including the three-deep LG (Banks / Glover / Jennings) and LB (Franklin / Hopper / Welch) rows that produce two of the three third-string cases |
| NE | [patriots.com/team/depth-chart](https://www.patriots.com/team/depth-chart) | **11 offensive groups exact**, including the four-deep RB (Stevenson / Henderson / Kiner / Larison) that produces the third-string case |
| DET | [detroitlions.com/team/depth-chart](https://www.detroitlions.com/team/depth-chart) | **21 of 21 groups exact** |
| KC | [chiefs.com/team/depth-chart](https://www.chiefs.com/team/depth-chart) | **19 of 22 groups exact.** Three gaps, all listed below |

Every chart is labelled **unofficial** by the club that publishes it — Green Bay stamps a date on it, New
England states it reflects the opinions of Patriots.com writers rather than the organisation. That caveat is
published next to the table rather than buried, because a chart can lag a coaching decision and nothing in
this dataset would reveal that.

**The three KC gaps, stated rather than smoothed over.** The Kansas City transcription is materially
complete but not perfect, and the differences are of two kinds:

1. **The LT starter is deliberately unasserted.** The club's chart names Kahlil Benson there; the dataset
   records only Diego Pounds (2nd string) and states why in its own correction note. That is a defensible
   conservative call about a name collision, but it has a side effect this session noticed: any code that
   treats the first name in a group as the starter will read **Pounds as the KC left-tackle starter**, which
   he is not. No published cascade is affected, because Pounds is not on the practice report and the group
   therefore produces no row — but it is a latent trap for the next consumer of `depth_charts.json`.
2. **Two third-string entries were not transcribed**: Josh Downs at WR and Marcus Harris at DT. Neither
   changes a published row, because no injury reaches that deep on those groups this week, but both would
   matter in a week that did.

The honest reading of all four charts: the transcription is reliable at the top of each group, which is
where the cascades come from, and slightly incomplete at the third and fourth string.

**A defect this re-check found in our own analysis.** The first version of the depth-reach table silently
dropped any position group where *no* player at any depth was available, because the loop only recorded a
row once it found someone available. New England's left guard — starter Ben Brown Out, 2nd-string Walter
Rouse also did not practise — was therefore missing from a table whose whole purpose is to surface exactly
that situation. It is now published as a **vacancy** with the next-man-up cell empty, and the verifier
re-derives every row including vacancies.

**The guard added so this cannot recur.** Two checks now fail the build rather than warn:

- `tools/verify.py` → `register_counts_match_files()` — any "N suggestions / questions / flags / gates /
  signals / strategies / sources" written inside a register row must equal the real file length.
- `tools/verify.py` → `injury_coverage_is_measured_not_named()` — the set of clubs with no injury rows must
  be derived from `schedule_2026_wk10.csv`, and the builder may not hand-name that set. It also fails if any
  page overstates the club coverage as a bare count.

Negative control run during this session: restoring the literal list to `tools/build_site.py` fails with
`build_site.py still hand-names the empty-club list`, and writing a bare coverage count into a page fails
with `claims 28 clubs as coverage; the file holds 24 of 28`. Both revert to `41 passed · 0 failures`.

**What this does *not* establish.** A one-off manual re-fetch is not a substitute for scheduled ingest
(FL-11) and it cannot establish point-in-time completeness (FL-09). It establishes that on 12 November 2026
the standings and fixtures matched the league exactly, and that the injury snapshot's coverage claim did not.
