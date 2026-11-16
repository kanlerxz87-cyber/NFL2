# Official Capture (retained, hashed)
> Two official NFL injury-hub responses are retained with UTC times and SHA-256 hashes. This page publishes only capture metadata and aggregate checks—not player-level rows. The unredacted bytes and reconciliation CSV are currently present in this public repository without a recorded source-terms review; see **FL-99**. Hash integrity is not permission to republish.

## What was captured, and when

The captures ran on GitHub-hosted runners, because the analysis sandbox cannot reach nfl.com (FL-90). The manifest records HTTP 200 responses at **2026-11-16 14:39:21 UTC** and **14:44:29 UTC**, each 399,895 bytes; their SHA-256 values are `e2b4074a9837a93e0d38ae8a8aac7b7b668b96fdd41d7caf86269a650cd981a3` and `2877f2c8a1a28acb7024708cf103f2154d0d3f0231e9748b4b5d9480fec6c5fb`. The capture tool's schema checks reported 28 club tables, 347 player rows, 347 practice-status hits and 171 game-status hits on each response. The **14:44 UTC** retained capture was row-reconciled against the 15 Nov transcription (347/347 match after the disclosed Rams code alias); the two captures are only five minutes apart and do not establish a daily history.

Source: [https://www.nfl.com/injuries/](https://www.nfl.com/injuries/) · retained files: `data/captures/injuries_hub/20261116T143921Z_e2b4074a9837.bin` and `data/captures/injuries_hub/20261116T144429Z_2877f2c8a1a2.bin` · the append-only ledger is `data/capture_manifest.csv`.

{{csv data/capture_manifest.csv;;cols=fetch_utc:Fetched (UTC),source_url:Official URL,http_status:HTTP,bytes:Bytes,sha256:SHA-256,stored_path:Stored file,title:Page title,schema_ok:Structure check;;source_col=source_url;;caption=One row per fetch. A repeat fetch whose bytes are identical is logged but not stored again. A page that answers but fails the structure check is kept as evidence and marked no.}}

## Aggregate reconciliation with the 15 November file

The 347 rows of the 14:44 UTC retained bytes were compared with `data/injuries_wk10_5de1805b_20261115.csv` (the 15 November 12:55Z read, 347 rows). The comparison matches each player's club, position, injury, practice status and game status. The club key needed one alias, disclosed here: the repository writes the Los Angeles Rams as `LAR`, and the page's own logo code is `LA`. No other alias was used, and no value was changed.

| Check (aggregate only) | Rows | Official source |
| --- | ---: | --- |
| Captured player rows in the 14:44 UTC response | 347 | [NFL injury hub](https://www.nfl.com/injuries/) |
| Rows matched on all five compared fields | 347 | [NFL injury hub](https://www.nfl.com/injuries/) |
| Rows mismatched in both files | 0 | [NFL injury hub](https://www.nfl.com/injuries/) |
| Rows present only in the capture | 0 | [NFL injury hub](https://www.nfl.com/injuries/) |
| Rows present only in the 15 Nov repository transcription | 0 | [NFL injury hub](https://www.nfl.com/injuries/) |

What this shows: the 15 November read and the 16 November retained bytes agree on every row. What it does not show: whether the league changed anything between those two times, or whether the page will change before kickoff. A matching pair of reads is evidence of agreement, not of a stable designation.

The reconciliation used the league's practice vocabulary: **F** = Full Participation in Practice, **L** = Limited Participation, **D** = Did Not Participate In Practice. Game-status labels are Out, Questionable and Doubtful. Blank cells were preserved as blank. **No player-level rows are rendered here.** The row-by-row comparison is in `data/capture_reconciliation_7c23f22f.csv`, which remains accessible in the public repository pending the source-use decision in [FL-99](flagged-for-review.html).

## What is still open

- **FL-90** — stays open: the two captures are five minutes apart, not a multi-day series, and they cannot replay earlier reports (FL-88).
- **FL-94** — the canonical injury page still shows blank Detroit designations from its older read, although the retained capture contains them as Out.
- **FL-97** — the empty-store condition is resolved by two verified captures; future daily cadence remains to be demonstrated.
- **FL-98** — the Rams club key differs (`LAR` in the repository, `LA` in the official page); the reconciliation discloses the alias.
- **FL-99** — raw responses and the row-level reconciliation remain accessible in this public repository without a recorded terms review. The page suppresses player-row rendering, but this does not make the files private.

Flags: [Flagged for Review](flagged-for-review.html) (FL-90, FL-94, FL-97, FL-98, FL-99). Source: [NFL injury hub](https://www.nfl.com/injuries/) and [Source Registry](sources.html) (S-CAP-7C). Method: `tools/capture_official.py`, `tools/reconcile_capture_7c23f22f.py`, `tools/verify_capture_7c23f22f.py`.
