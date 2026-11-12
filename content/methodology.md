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

- **Point-in-time completeness.** The injury hub was fetched twice on 12 November, at 04:45Z and again at 22:35Z, and the two reads differ by 25 rows and 15 practice codes — which is the finding, not an error: the page is a rolling document and every published row is labelled with the moment it was true. There is still no stored history, so nothing on this site is an availability *time series* (FL-09, FL-22, Q-31).
- **Roster membership.** We spot-checked one club's roster page, one chunk deep (FL-14). We did not verify all 32 rosters, so "player X is on team Y" is only as good as the hub's own table.
- **Headline-only rows.** Three depth rows rest on an article headline without the body fetched (FL-13). They are marked and they feed no number.
- **No price data we can stand behind as a market statement.** The repository does hold market prices — `pipeline/data/raw/` carries 20,490 rows of archived lines and 163 priced 2026 rows in `games.csv` — which is why FL-10 as originally written ("no price data of any kind") is recorded as wrong-scope and corrected by FL-24. What is still true is the operative part: no *vintage-documented* closing price exists, so no page on this site may be read as a market statement and close-vs-open cannot be resolved from the upstream schema (FL-25, Q-30, [Price archive](price-archive.html)).
- **Egress limits.** The sandbox blocks outbound access to the league from CI, so refresh is a deliberate operation here, not a background service (FL-11).
- **Imported files we did not re-derive.** The parallel session's team-stat, player-leader and depth-chart JSON is in the repository and is *not* published as this site's data, because their column mapping (proved by conservation identities on their side) was not re-run here; only the game log survived that bar (FL-18, Q-29).

## Reproducing the audit

```
python3 tools/build_site.py && python3 tools/verify.py && python3 tools/check_site.py
```

The generator is deterministic: same inputs, same bytes out. If it fails, that is the intended behaviour — the site is not allowed to publish a table it cannot vouch for.

### How a table is produced, and how to break one

Every table on the site is generated, never hand-written: a page in `content/*.md` holds a directive naming the file, the columns and the row source, and the builder renders it.

```
{{csv data/<file>.csv;;cols=<key>:<Label>[:<value-map>],...;;source=<S-id>|source_col=<key>
        ;;filter=<key>=<substring>|<key>=!<substring>|<key>=*;;group=<key>;;show_source=0
        ;;link_player=1;;caption=<one sentence a reader needs>}}
```

Three rules worth knowing before editing a page, each of them learned from a defect that reached the published site:

| Rule | Why it exists |
| --- | --- |
| A filter clause is `key=value`, never `key:value`; `value` may be prefixed with `!` for "does not contain", or be `*` for "the cell is filled in" | A colon-spelled clause used to be dropped without complaint, which silently unfiltered three tables at once, including the injury-designations table and both suggestion tiers (FL-28). The builder now raises `BuildError`, and `verify.py` recomputes every filter clause and fails if it matches nothing or everything |
| Every row must resolve to a source | `source=S-id` (one source for the table) or `source_col=<key>` (a per-row source id or URL). A table that declares neither fails the build — there is no configuration that publishes an uncited row |
| A gap is an empty cell, never a word | The builder renders empty cells as `not published`; `0` means zero and `n/a` means "does not apply". Writing a filler into the CSV is the one edit that cannot be caught downstream, which is why `verify.py` treats it as fabrication |
