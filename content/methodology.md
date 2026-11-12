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
| Link and asset audit | `tools/check_site.py` | broken internal links, missing pages, pages not in navigation, non-official hosts used as system-of-record |
| CI | `.github/workflows/validate.yml` | the three above must pass on every push and pull request |

## What verification did *not* cover — read this before reusing the data

- **Point-in-time completeness.** The injury hub was fetched once. It is a page that changes three times in a week; this snapshot is a faithful copy of one moment, not the week's history (FL-09).
- **Roster membership.** We spot-checked one club's roster page, one chunk deep (FL-14). We did not verify all 32 rosters, so "player X is on team Y" is only as good as the hub's own table.
- **Headline-only rows.** Three depth rows rest on an article headline without the body fetched (FL-13). They are marked and they feed no number.
- **No price data.** Nothing on this site is a market statement of any kind (FL-10).
- **Egress limits.** The sandbox blocks outbound access to the league from CI, so refresh is a deliberate operation here, not a background service (FL-11).

## Reproducing the audit

```
python3 tools/build_site.py && python3 tools/verify.py && python3 tools/check_site.py
```

The generator is deterministic: same inputs, same bytes out. If it fails, that is the intended behaviour — the site is not allowed to publish a table it cannot vouch for.
